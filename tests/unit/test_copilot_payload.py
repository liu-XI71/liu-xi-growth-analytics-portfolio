from __future__ import annotations

import httpx
import pytest

from analytics.copilot import build_copilot_payload
from analytics.copilot.contracts import Claim, ClaimType, EvidenceItem, SourceType
from analytics.copilot.evidence import validate_claim
from analytics.copilot.narrative import generate_narrative
from scripts.generate_demo_data import _copilot_frames


def _index(items: list[dict], key: str = "id") -> dict[str, dict]:
    return {item[key]: item for item in items}


def test_public_payload_is_complete_and_governed() -> None:
    payload = build_copilot_payload()
    assert {
        "meta",
        "decisions",
        "questions",
        "analysis_threads",
        "weekly_reports",
        "cases",
        "experiment_defaults",
        "metric_contracts",
        "evidence",
        "claims",
    } <= payload.keys()
    assert payload["meta"]["version"] == "1.2.0"
    assert payload["meta"]["narrative_mode"] == "deterministic"
    assert "evals" not in payload
    for report in payload["weekly_reports"]:
        assert report["report_mode"] == "fixed_rule_demo"
        assert report["previous_period"]
        assert report["comparison"]["history_type"] == "case_replay_not_calendar_week"
        assert "不是公司真实自然周数据" in report["data_boundary"]


def test_copilot_contracts_evidence_claims_and_reports_are_database_ready() -> None:
    frames = _copilot_frames()
    assert set(frames) == {
        "copilot_metric_contracts",
        "copilot_evidence",
        "copilot_claims",
        "copilot_weekly_reports",
    }
    assert len(frames["copilot_metric_contracts"]) >= 6
    assert frames["copilot_claims"]["validation_passed"].all()
    assert set(frames["copilot_weekly_reports"]["previous_period"])


def test_referral_facts_and_economics_use_professional_scoped_names() -> None:
    payload = build_copilot_payload()
    evidence = _index(payload["evidence"])
    experiment = evidence["ev_referral_experiment"]["values"]
    assert experiment["control_rate"] == 0.17
    assert experiment["treatment_rate"] == 0.235
    assert experiment["absolute_lift_pp"] == pytest.approx(6.5)
    assert experiment["relative_lift_pct"] == pytest.approx(38.2)
    assert experiment["significance"] == "p < 0.05"
    assert experiment["actual_control_n"] is None
    assert experiment["actual_treatment_n"] is None
    assert experiment["aa_result"] is None
    assert experiment["srm_result"] is None
    assert experiment["stratified_balance_result"] is None
    assert experiment["duration_days"] == 14
    assert experiment["total_sample"] == 7_000_000
    assert experiment["actual_control_n"] is None
    assert experiment["actual_treatment_n"] is None
    value_cost = evidence["ev_referral_value_cost"]
    assert value_cost["metric_id"] == "first_month_value_cost_ratio"
    assert value_cost["values"]["released_ratio"] == 2.18
    assert value_cost["values"]["external_same_scope_ratio"] == 1.9
    assert "完整生命周期价值" in value_cost["claim_boundary"]
    incentive = evidence["ev_referral_incentive_reconstruction"]
    assert incentive["values"] == {"before_index": 100, "after_index": 160}
    assert "绝对金额" in incentive["claim_boundary"]


def test_retention_fact_boundary_refuses_missing_mix_and_lift_numbers() -> None:
    payload = build_copilot_payload()
    evidence = _index(payload["evidence"])
    structure = evidence["ev_retention_device_structure"]
    assert structure["synthetic"] is False
    assert structure["values"]["tablet_gap_pp"] == 10
    assert structure["values"]["tablet_share_before"] is None
    assert structure["values"]["tablet_share_after"] is None
    assert structure["values"]["tablet_share_change"] is None
    assert "无法精确计算真实结构贡献" in structure["statement"]
    retention_experiment = evidence["ev_retention_experiment"]
    assert retention_experiment["values"]["total_sample"] == 300_000
    assert retention_experiment["values"]["control_rate"] is None
    assert retention_experiment["values"]["treatment_rate"] is None
    assert retention_experiment["values"]["absolute_lift"] is None
    assert "不能计算绝对或相对提升" in retention_experiment["claim_boundary"]


def test_synthetic_mix_shift_is_explicitly_separated_from_case_facts() -> None:
    payload = build_copilot_payload()
    evidence = _index(payload["evidence"])
    demo = evidence["ev_synthetic_mix_shift"]
    assert demo["synthetic"] is True
    assert demo["source_type"] == "synthetic_demo"
    assert "不能作为实习项目的真实业务事实" in demo["claim_boundary"]
    retention_case = _index(payload["cases"])["new_user_retention"]
    device = retention_case["analysis_data"]["device_structure"]
    assert device["structure_contribution_pp"] is None
    assert device["unexplained_residual_pp"] is None
    assert device["status"] == "missing_segment_share_change"


def test_claim_validator_blocks_unsupported_numbers_causal_overreach_and_bad_terms() -> None:
    evidence = EvidenceItem(
        id="evidence",
        case_id="case",
        evidence_type="correlational_benchmark",
        source_type=SourceType.EXPERIENCE_FACT,
        title="证据",
        metric_id="first_month_value_cost_ratio",
        values={"ratio": 2.18, "window_start_day": 1, "window_end_day": 7},
        statement="首月价值成本比为2.18。",
        claim_boundary="不是完整生命周期口径。",
        source_ref="fixture",
    )
    index = {evidence.id: evidence}
    unsupported = Claim(
        id="unsupported",
        case_id="case",
        statement="提升42%。",
        claim_type=ClaimType.FACT,
        evidence_ids=[evidence.id],
        confidence="low",
        allowed_scope="test",
    )
    causal = unsupported.model_copy(
        update={"id": "causal", "statement": "证明策略导致增长。", "claim_type": ClaimType.FACT}
    )
    bad_economics = unsupported.model_copy(
        update={"id": "roi", "statement": "ROI为2.18。", "claim_type": ClaimType.FACT}
    )
    retention_evidence = evidence.model_copy(
        update={"id": "retention", "metric_id": "d1_7_window_retention"}
    )
    exact_d7 = unsupported.model_copy(
        update={
            "id": "d7",
            "statement": "这是精确第7日留存。",
            "claim_type": ClaimType.FACT,
            "evidence_ids": [retention_evidence.id],
        }
    )
    assert "unsupported number: 42" in validate_claim(unsupported, index)
    assert any("causal language" in error for error in validate_claim(causal, index))
    assert any("ROI/LTV/CAC" in error for error in validate_claim(bad_economics, index))
    assert any(
        "exact D7" in error
        for error in validate_claim(exact_d7, {**index, retention_evidence.id: retention_evidence})
    )


def test_ollama_failure_falls_back_to_validated_deterministic_narrative() -> None:
    evidence = EvidenceItem(
        id="e",
        case_id="case",
        evidence_type="descriptive_monitoring",
        source_type=SourceType.EXPERIENCE_FACT,
        title="证据",
        values={"rate": 0.17},
        statement="指标为17%。",
        claim_boundary="仅描述事实。",
        source_ref="fixture",
    )

    def fail_post(*_args, **_kwargs):
        raise httpx.ConnectError("offline")

    result = generate_narrative(
        mode="ollama",
        headline="指标为17%",
        summary="当前指标为17%。",
        evidence=[evidence],
        post=fail_post,
    )
    assert result["mode"] == "deterministic_fallback"
    assert result["status"] == "fallback"
    assert result["text"] == "当前指标为17%。"


def test_unknown_narrative_mode_is_rejected() -> None:
    with pytest.raises(ValueError, match="narrative_mode"):
        build_copilot_payload(narrative_mode="unknown")
