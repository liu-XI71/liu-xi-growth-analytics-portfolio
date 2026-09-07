from __future__ import annotations

import json
from collections.abc import Callable

import httpx
import pytest

from analytics.copilot.contracts import EvidenceItem, SourceType
from analytics.copilot.narrative import generate_narrative


def _evidence() -> list[EvidenceItem]:
    return [
        EvidenceItem(
            id="retention-trend",
            case_id="retention",
            evidence_type="descriptive_monitoring",
            source_type=SourceType.EXPERIENCE_FACT,
            title="次7日内留存变化",
            metric_id="d1_7_window_retention",
            values={
                "before_rate": 0.48,
                "after_rate": 0.41,
                "absolute_change_pp": -7,
                "window_start_day": 1,
                "window_end_day": 7,
            },
            statement="次7日内留存率从48%降至41%。",
            claim_boundary="第1至7天至少回访一次，不等于精确D7留存。",
            source_ref="fixture",
        ),
        EvidenceItem(
            id="device-structure",
            case_id="retention",
            evidence_type="descriptive_segmentation",
            source_type=SourceType.EXPERIENCE_FACT,
            title="设备结构压力",
            metric_id="d1_7_window_retention",
            values={
                "tablet_gap_pp": 10,
                "tablet_share_before": None,
                "tablet_share_after": None,
                "tablet_share_change": None,
            },
            statement="平板留存比手机低约10pp，设备结构形成压力。",
            claim_boundary="缺少分期占比，不能量化结构贡献和残差。",
            source_ref="fixture",
        ),
        EvidenceItem(
            id="path-negative",
            case_id="retention",
            evidence_type="negative_evidence",
            source_type=SourceType.EXPERIENCE_FACT,
            title="路径负证据",
            values={},
            statement="已检查路径未见明显恶化。",
            claim_boundary="只能降低排查优先级，不证明产品没有卡点。",
            source_ref="fixture",
        ),
        EvidenceItem(
            id="benchmark",
            case_id="retention",
            evidence_type="correlational_benchmark",
            source_type=SourceType.EXPERIENCE_FACT,
            title="标杆用户差异",
            metric_id="follow_penetration",
            values={"benchmark_to_non_benchmark_ratio": 2.5},
            statement="标杆用户关注渗透率约为非标杆用户的2.5倍。",
            claim_boundary="只是相关性线索，不能证明因果。",
            source_ref="fixture",
        ),
        EvidenceItem(
            id="retention-experiment",
            case_id="retention",
            evidence_type="randomized_experiment",
            source_type=SourceType.EXPERIENCE_FACT,
            title="退出页引导实验",
            metric_id="d1_7_window_retention",
            values={"duration_days": 14, "total_sample": 300_000, "alpha": 0.05},
            statement="随机实验显示次7日内留存率显著提升。",
            claim_boundary="只识别完整退出页引导策略，绝对提升未提供。",
            source_ref="fixture",
        ),
        EvidenceItem(
            id="value-cost",
            case_id="referral",
            evidence_type="economics_guardrail",
            source_type=SourceType.EXPERIENCE_FACT,
            title="首月价值成本比",
            metric_id="first_month_value_cost_ratio",
            values={"released_ratio": 2.18, "external_same_scope_ratio": 1.9},
            statement="首月价值/激励成本比为2.18。",
            claim_boundary="不是完整ROI、LTV、CAC或利润口径。",
            source_ref="fixture",
        ),
    ]


def _post_with_text(text: str, headline: str = "自动周报") -> Callable[..., httpx.Response]:
    def post(*_args, **_kwargs) -> httpx.Response:
        request = httpx.Request("POST", "http://127.0.0.1:11434/api/generate")
        return httpx.Response(
            200,
            request=request,
            json={"response": json.dumps({"headline": headline, "text": text})},
        )

    return post


@pytest.mark.parametrize(
    "malicious_text,expected_error",
    [
        (
            "标杆用户关注渗透率为非标杆的2.5倍，证明关注行为导致留存提升。",
            "correlational evidence",
        ),
        ("D7留存率从48%降至41%。", "exact D7 retention"),
        ("该策略ROI为2.18，已实现净利润。", "ROI/LTV/CAC/profit"),
        (
            "设备结构完全解释了7pp下滑，结构贡献为7pp、残差为10pp。",
            "device-structure evidence",
        ),
        ("未解释残差为7pp。", "device-structure evidence"),
        ("路径稳定证明产品没有任何使用卡点。", "negative evidence"),
        ("不是使用卡点导致留存下滑。", "negative evidence"),
    ],
)
def test_ollama_semantic_overreach_falls_back(malicious_text: str, expected_error: str) -> None:
    result = generate_narrative(
        mode="ollama",
        headline="证据边界内结论",
        summary="现有证据仅支持方向判断。",
        evidence=_evidence(),
        post=_post_with_text(malicious_text),
    )

    assert result["mode"] == "deterministic_fallback"
    assert result["status"] == "fallback"
    assert result["fallback_reason"] == "semantic_guardrail"
    assert any(expected_error in item for item in result["rejected_generation_errors"])
    assert result["text"] == "现有证据仅支持方向判断。"


def test_ollama_accepts_scoped_experimental_and_negative_evidence_language() -> None:
    text = (
        "随机实验支持完整退出页引导策略改善次7日内留存率；"
        "标杆用户差异只是相关性线索；"
        "路径稳定仅降低基础使用卡点的排查优先级；"
        "设备结构仅形成方向性压力，缺少分期占比，无法计算真实贡献和残差。"
    )
    result = generate_narrative(
        mode="ollama",
        headline="实验与证据边界",
        summary="现有证据仅支持方向判断。",
        evidence=_evidence(),
        post=_post_with_text(text, headline="实验与证据边界"),
    )

    assert result["mode"] == "ollama"
    assert result["status"] == "ready"
    assert result["text"] == text
    assert result["validation_errors"] == []


def test_ollama_accepts_explicit_economic_scope_disclaimer() -> None:
    text = "首月价值/激励成本比为2.18，不是完整ROI、LTV、CAC或利润口径。"
    result = generate_narrative(
        mode="ollama",
        headline="首月同口径比较",
        summary="首月价值/激励成本比为2.18。",
        evidence=_evidence(),
        post=_post_with_text(text, headline="首月同口径比较"),
    )

    assert result["mode"] == "ollama"
    assert result["text"] == text


def test_ollama_number_guardrail_still_rejects_an_allowed_semantic_shape() -> None:
    result = generate_narrative(
        mode="ollama",
        headline="证据边界内结论",
        summary="现有证据仅支持方向判断。",
        evidence=_evidence(),
        post=_post_with_text("次7日内留存率为52%。"),
    )

    assert result["mode"] == "deterministic_fallback"
    assert result["fallback_reason"] == "unsupported_numbers"
    assert result["rejected_generation_errors"] == ["unsupported number: 52"]
