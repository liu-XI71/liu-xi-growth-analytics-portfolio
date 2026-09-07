from __future__ import annotations

import math
import re
from collections.abc import Iterable, Mapping
from typing import Any

from analytics.copilot.contracts import Claim, ClaimType, EvidenceItem

# Python's ``\w`` includes CJK characters, so a generic word-boundary pattern
# would miss ordinary Chinese text such as "提升6.5pp". Only exclude ASCII
# identifier characters here; claims are prose, while this keeps version-like
# fragments from being split into misleading partial numbers.
NUMBER_PATTERN = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?")

CLAUSE_SPLIT_PATTERN = re.compile(r"[。！？!?\uff1b;\n]+")
CAUSAL_ASSERTION_PATTERN = re.compile(
    r"(?:导致|造成|驱动|促使|引起|归因于|证明|证实|因果关系|"
    r"(?:策略|页面|引导|功能|关注(?:行为)?|设备结构|平板占比)"
    r".{0,12}(?:带来|使得|使|提升|改善|增加|降低)|"
    r"(?<![a-z0-9_])(?:causes?|caused|drives?|led\s+to|leads\s+to|"
    r"results?\s+in|proves?)(?![a-z0-9_]))",
    re.IGNORECASE,
)
CORRELATION_PATTERN = re.compile(
    r"(?:相关性|相关线索|标杆用户|非标杆|观察性|自选择|渗透率.{0,8}(?:差异|倍))",
    re.IGNORECASE,
)
EXPERIMENT_ANCHOR_PATTERN = re.compile(
    r"(?:随机(?:对照)?实验|A\s*/\s*B\s*实验|AB实验|实验组|对照组|"
    r"实验(?:结果|显示|支持|证明|证实)?)",
    re.IGNORECASE,
)
EXACT_D7_PATTERN = re.compile(
    r"(?:(?<![a-z0-9_])d\s*7(?![a-z0-9_])\s*(?:留存|回访)?|"
    r"第\s*(?:7|七)\s*日(?:留存|回访)|(?<!次)7\s*日留存率?)",
    re.IGNORECASE,
)
ECONOMIC_RELABEL_PATTERN = re.compile(
    r"(?:(?<![a-z0-9_])(?:roi|ltv|cac)(?![a-z0-9_])|"
    r"投资回报率|净利润|利润率|净收益|完整利润|利润)",
    re.IGNORECASE,
)
STRUCTURE_PATTERN = re.compile(
    r"(?:设备结构|结构变化|结构贡献|平板占比|mix[-_ ]?shift)", re.IGNORECASE
)
STRUCTURE_QUANTIFICATION_PATTERN = re.compile(r"(?:贡献|残差|剩余变化|未解释变化|解释量)")
STRUCTURE_OVERREACH_PATTERN = re.compile(
    r"(?:"
    r"(?:设备结构|结构变化|平板占比).{0,16}"
    r"(?:完全|全部|唯一|主要原因|主因|解释(?:了|全部|部分|下滑)|"
    r"(?:是|为).{0,4}(?:原因|根因|主因)|导致了|造成了|贡献了)|"
    r"(?:完全|全部|唯一).{0,12}(?:由|是)?(?:设备结构|结构变化|平板占比)|"
    r"(?:贡献|残差|剩余变化|未解释变化).{0,8}(?:为|是|=|达到)"
    r")",
    re.IGNORECASE,
)
NEGATIVE_EVIDENCE_OVERREACH_PATTERN = re.compile(
    r"(?:"
    r"(?:彻底|完全|已经|已|可以|可)?排除|"
    r"证明.{0,18}(?:没有|不存在|无任何|毫无).{0,8}(?:问题|卡点|异常)|"
    r"(?:产品|链路|路径|环节).{0,12}(?:没有任何?|不存在|毫无)(?:问题|卡点|异常)|"
    r"(?:一定不是|绝非|不是|并非).{0,18}(?:问题|卡点).{0,8}(?:导致|原因|主因)|"
    r"(?:一定不是|绝非).{0,12}(?:原因|主因)|"
    r"(?:无需|不用|不必).{0,8}(?:排查|关注|监控)"
    r")",
    re.IGNORECASE,
)
NEGATION_PATTERN = re.compile(
    r"(?:不(?:能|可|应|代表|等于|是|足以|支持|成立|证明)?|"
    r"无法|并非|未能|未提供|没有证据|缺乏证据|缺少|拒绝)",
    re.IGNORECASE,
)
CONTRAST_OR_BOUNDARY_PATTERN = re.compile(r"(?:但是|然而|不过|但|却|[。！？!?\uff1b;\n])")


def _numeric_values(value: Any) -> list[float]:
    if isinstance(value, bool) or value is None:
        return []
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        number = float(value)
        candidates = [number]
        if abs(number) <= 1:
            candidates.append(number * 100)
        return candidates
    if isinstance(value, Mapping):
        return [item for nested in value.values() for item in _numeric_values(nested)]
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return [item for nested in value for item in _numeric_values(nested)]
    return []


def _numbers_in_statement(statement: str) -> list[float]:
    return [float(item) for item in NUMBER_PATTERN.findall(statement)]


def _clauses(text: str) -> list[str]:
    return [item.strip() for item in CLAUSE_SPLIT_PATTERN.split(text) if item.strip()]


def _is_locally_negated(text: str, start: int, end: int) -> bool:
    """Return whether a matched assertion is explicitly scoped as a limitation."""

    left = text[max(0, start - 36) : start]
    boundaries = list(CONTRAST_OR_BOUNDARY_PATTERN.finditer(left))
    if boundaries:
        left = left[boundaries[-1].end() :]
    if NEGATION_PATTERN.search(left):
        return True
    right = text[end : end + 20]
    return bool(
        re.match(
            r".{0,8}(?:不成立|不能成立|无法成立|无法计算|不能计算|"
            r"不可计算|未提供|不可量化|无法量化)",
            right,
            re.IGNORECASE,
        )
    )


def _unnegated_causal_clauses(text: str) -> list[str]:
    clauses: list[str] = []
    for clause in _clauses(text):
        if any(
            not _is_locally_negated(clause, match.start(), match.end())
            for match in CAUSAL_ASSERTION_PATTERN.finditer(clause)
        ):
            clauses.append(clause)
    return clauses


def _has_unquantified_device_structure(evidence: list[EvidenceItem]) -> bool:
    for item in evidence:
        boundary = f"{item.statement} {item.claim_boundary}".lower()
        has_structure_scope = bool(STRUCTURE_PATTERN.search(boundary))
        missing_mix_value = any(
            key in item.values and item.values[key] is None
            for key in ("tablet_share_before", "tablet_share_after", "tablet_share_change")
        )
        boundary_refuses_quantification = any(
            phrase in boundary for phrase in ("不能量化", "无法精确计算", "不计算", "不可量化")
        )
        if has_structure_scope and (missing_mix_value or boundary_refuses_quantification):
            return True
    return False


def _deduplicate(items: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(items))


def validate_narrative_semantics(text: str, evidence: Iterable[EvidenceItem]) -> list[str]:
    """Block high-risk meaning upgrades defined by the evidence contract.

    This deterministic checker intentionally covers a narrow risk set. It does
    not claim to verify every sentence or every possible paraphrase.
    """

    evidence_items = list(evidence)
    errors: list[str] = []

    causal_clauses = _unnegated_causal_clauses(text)
    randomized_evidence = any(
        item.evidence_type == "randomized_experiment" for item in evidence_items
    )
    for clause in causal_clauses:
        if CORRELATION_PATTERN.search(clause):
            errors.append("correlational evidence cannot be narrated as a causal result")
        elif not randomized_evidence or not EXPERIMENT_ANCHOR_PATTERN.search(clause):
            errors.append(
                "causal language requires an explicit randomized-experiment basis in the clause"
            )

    has_window_retention = any(item.metric_id == "d1_7_window_retention" for item in evidence_items)
    if has_window_retention:
        for match in EXACT_D7_PATTERN.finditer(text):
            if not _is_locally_negated(text, match.start(), match.end()):
                errors.append("D1-D7 window retention cannot be relabelled as exact D7 retention")

    has_first_month_value_cost = any(
        item.metric_id == "first_month_value_cost_ratio" for item in evidence_items
    )
    if has_first_month_value_cost:
        for match in ECONOMIC_RELABEL_PATTERN.finditer(text):
            if not _is_locally_negated(text, match.start(), match.end()):
                errors.append(
                    "first-month value-to-cost evidence cannot be relabelled as ROI/LTV/CAC/profit"
                )

    if _has_unquantified_device_structure(evidence_items):
        for clause in _clauses(text):
            if not STRUCTURE_PATTERN.search(clause) and not re.search(
                r"(?:残差|剩余变化|未解释变化)", clause
            ):
                continue
            for match in STRUCTURE_OVERREACH_PATTERN.finditer(clause):
                if not _is_locally_negated(clause, match.start(), match.end()):
                    errors.append(
                        "device-structure evidence lacks the mix inputs needed for contribution or residual claims"
                    )
            for match in STRUCTURE_QUANTIFICATION_PATTERN.finditer(clause):
                window = clause[max(0, match.start() - 16) : match.end() + 16]
                if NUMBER_PATTERN.search(window) and not _is_locally_negated(
                    clause, match.start(), match.end()
                ):
                    errors.append(
                        "device-structure evidence lacks the mix inputs needed for contribution or residual claims"
                    )

    if any(item.evidence_type == "negative_evidence" for item in evidence_items):
        for match in NEGATIVE_EVIDENCE_OVERREACH_PATTERN.finditer(text):
            if not _is_locally_negated(text, match.start(), match.end()):
                errors.append(
                    "negative evidence may lower investigation priority but cannot prove no problem exists"
                )

    return _deduplicate(errors)


def validate_claim(claim: Claim, evidence_index: Mapping[str, EvidenceItem]) -> list[str]:
    errors: list[str] = []
    missing = [
        evidence_id for evidence_id in claim.evidence_ids if evidence_id not in evidence_index
    ]
    if missing:
        errors.append(f"missing evidence: {', '.join(missing)}")
        return errors
    evidence = [evidence_index[evidence_id] for evidence_id in claim.evidence_ids]
    allowed_numbers = [number for item in evidence for number in _numeric_values(item.values)]
    for number in _numbers_in_statement(claim.statement):
        if not any(
            math.isclose(number, allowed, rel_tol=1e-6, abs_tol=0.011)
            for allowed in allowed_numbers
        ):
            errors.append(f"unsupported number: {number:g}")
    statement_lower = claim.statement.lower()
    contains_causal_language = bool(_unnegated_causal_clauses(claim.statement))
    randomized_evidence = any(item.evidence_type == "randomized_experiment" for item in evidence)
    if contains_causal_language and (
        claim.claim_type != ClaimType.CAUSAL_RESULT or not randomized_evidence
    ):
        errors.append("causal language requires a causal_result backed by randomized evidence")
    if claim.claim_type == ClaimType.CAUSAL_RESULT and not randomized_evidence:
        errors.append("causal_result requires randomized experiment evidence")
    if any(item.synthetic for item in evidence) and claim.claim_type == ClaimType.FACT:
        if "模拟" not in claim.statement and "synthetic" not in statement_lower:
            errors.append("synthetic evidence must be disclosed in a fact statement")
    errors.extend(validate_narrative_semantics(claim.statement, evidence))
    return _deduplicate(errors)


def validate_claims(claims: Iterable[Claim], evidence: Iterable[EvidenceItem]) -> dict[str, Any]:
    evidence_index = {item.id: item for item in evidence}
    items = []
    for claim in claims:
        errors = validate_claim(claim, evidence_index)
        items.append({"claim_id": claim.id, "passed": not errors, "errors": errors})
    failed = sum(not item["passed"] for item in items)
    return {
        "passed": failed == 0,
        "total": len(items),
        "failed": failed,
        "items": items,
    }


def validate_narrative_numbers(text: str, evidence: Iterable[EvidenceItem]) -> list[str]:
    allowed = [number for item in evidence for number in _numeric_values(item.values)]
    errors = []
    for number in _numbers_in_statement(text):
        if not any(math.isclose(number, item, rel_tol=1e-6, abs_tol=0.011) for item in allowed):
            errors.append(f"unsupported number: {number:g}")
    return errors
