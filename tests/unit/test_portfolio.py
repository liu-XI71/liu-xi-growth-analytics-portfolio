from __future__ import annotations

import json

import pandas as pd
import pytest

from scripts.export_portfolio import build_bundle, export_bundle
from scripts.portfolio_data import portfolio_frames


def test_portfolio_frames_freeze_two_case_business_contract() -> None:
    frames = portfolio_frames()
    cases = frames["portfolio_case_registry"]
    assert cases["case_id"].tolist() == ["referral_growth", "new_user_retention"]
    assert set(frames) == {
        "portfolio_case_registry",
        "portfolio_business_kpis",
        "portfolio_decision_loop",
        "portfolio_growth_quality_bridge",
        "portfolio_referral_versions",
        "portfolio_referral_funnel",
        "portfolio_retention_trend",
        "portfolio_retention_segments",
        "portfolio_retention_decomposition",
        "portfolio_retention_path",
        "portfolio_benchmark_features",
        "portfolio_experiments",
        "portfolio_metric_contracts",
        "portfolio_hypothesis_ledger",
        "portfolio_decisions",
    }


def test_portfolio_key_claims_match_disclosed_narrative() -> None:
    frames = portfolio_frames()
    experiments = frames["portfolio_experiments"].set_index("case_id")
    referral = experiments.loc["referral_growth"]
    assert referral["baseline_rate"] == pytest.approx(0.17)
    assert referral["treatment_rate"] == pytest.approx(0.235)
    assert referral["absolute_lift_pp"] == pytest.approx(6.5)
    assert referral["sample_size"] == 7_000_000
    assert referral["sample_display"] == "总样本约700万"
    assert referral["duration_days"] == 14
    assert referral["approx_min_per_arm"] == 2629
    assert "演示复算" in referral["minimum_sample_source"]
    assert "不是公司内部" in referral["minimum_sample_source"]
    retention = experiments.loc["new_user_retention"]
    assert retention["sample_size"] == 300_000
    assert retention["sample_display"] == "总样本约30万"
    assert retention["duration_days"] == 14
    assert retention["significance"] == "p < 0.05"
    assert retention["baseline_rate"] != retention["baseline_rate"]
    assert retention["absolute_lift_pp"] != retention["absolute_lift_pp"]


def test_retention_metric_is_window_not_exact_d7() -> None:
    metrics = portfolio_frames()["portfolio_metric_contracts"].set_index("metric_key")
    definition = metrics.loc["d1_7_window_retention"]
    assert "第1至7天" in definition["numerator"]
    assert "不等于精确第7日" in definition["boundary"]


def test_referral_economics_uses_first_month_value_cost_ratio() -> None:
    frames = portfolio_frames()
    initial = frames["portfolio_referral_versions"].query("version_id == 'baseline'").iloc[0]
    latest = frames["portfolio_referral_versions"].query("version_id == 'simplified_ui'").iloc[0]
    assert pd.isna(initial["m1_value_cost"])
    assert initial["reported_efficiency_metric"] == pytest.approx(2.9)
    assert "不与后续" in initial["efficiency_scope"]
    assert latest["m1_value_cost"] == pytest.approx(2.18)
    contract = frames["portfolio_metric_contracts"].query("metric_key == 'm1_value_cost'").iloc[0]
    assert "完整生命周期" in contract["boundary"]


def test_static_bundle_is_strict_json_without_nan(tmp_path) -> None:
    output = export_bundle(tmp_path / "portfolio.json")
    raw = output.read_text(encoding="utf-8")
    assert "NaN" not in raw
    parsed = json.loads(raw)
    assert parsed == build_bundle()
    retention = parsed["retention"]["experiment"]
    assert retention["absolute_lift_pp"] is None


def test_every_decision_has_full_reasoning_chain() -> None:
    decisions = portfolio_frames()["portfolio_decisions"]
    required = ["fact", "interpretation", "hypothesis", "action", "decision", "limitation"]
    assert decisions[required].notna().all().all()
    assert (decisions[required].map(len) > 8).all().all()


def test_retention_structure_is_bounded_and_not_a_complete_explanation() -> None:
    frames = portfolio_frames()
    segments = frames["portfolio_retention_segments"]
    tablet = segments.query("segment == '平板'").iloc[0]
    assert tablet["retention_comparison"] == "观察期内比手机低约10pp"
    assert tablet["share_finding"] == "新增占比方向上升；缺少分期占比，无法准确量化结构贡献"
    decomposition = frames["portfolio_retention_decomposition"].set_index("component")
    assert decomposition.loc["整体留存变化", "observed_value_pp"] == pytest.approx(-7.0)
    assert decomposition.loc["设备结构定量贡献", "kind"] == "missing_input"
    assert pd.isna(decomposition.loc["设备结构定量贡献", "bound_value_pp"])
    assert pd.isna(decomposition.loc["仍需解释的变化", "bound_value_pp"])
    assert "无法准确量化" in decomposition.loc["设备结构定量贡献", "display"]


def test_public_detail_tables_do_not_invent_unconfirmed_precision() -> None:
    frames = portfolio_frames()
    funnel = frames["portfolio_referral_funnel"]
    assert "users" not in funnel.columns
    assert "conversion_from_previous" not in funnel.columns
    assert funnel.loc[funnel["step_key"] == "invite_click", "confirmed_value_display"].item() == (
        "约21%→17%→23.5%"
    )

    trend = frames["portfolio_retention_trend"]
    assert trend["retention_d1_7_window"].tolist() == [0.48, 0.41]
    path = frames["portfolio_retention_path"]
    assert "baseline_rate" not in path.columns
    assert "current_rate" not in path.columns


def test_public_metric_contract_has_no_unfrozen_viral_rate() -> None:
    contracts = portfolio_frames()["portfolio_metric_contracts"]
    assert "viral_rate" not in contracts["metric_key"].tolist()
    assert contracts[["role", "window", "decision_use"]].notna().all().all()


def test_retention_decision_preserves_undisclosed_effect_size_boundary() -> None:
    decisions = portfolio_frames()["portfolio_decisions"].set_index("case_id")
    retention = decisions.loc["new_user_retention"]
    assert "实验组、对照组绝对留存率未披露" in retention["decision"]
    assert "建议继续推进" in retention["decision"]
    assert "策略推广" not in retention["decision"]
