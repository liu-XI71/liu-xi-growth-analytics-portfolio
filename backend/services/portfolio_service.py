from __future__ import annotations

from typing import Any

from backend.database.connection import query_records


def _rows(table: str, order_by: str | None = None) -> list[dict[str, Any]]:
    allowed = {
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
    if table not in allowed:
        raise ValueError(f"Unsupported portfolio table: {table}")
    clause = f" ORDER BY {order_by}" if order_by else ""
    return query_records(f'SELECT * FROM "{table}"{clause}')


def portfolio_bundle() -> dict[str, Any]:
    return {
        "meta": {
            "projectName": "Liu Xi Growth & Experiments",
            "projectNameZh": "刘希｜增长与实验",
            "version": "1.2.0",
            "dataBoundary": (
                "关键变化来自去标识化实习复盘；本地数据库行级明细由固定规则生成，不包含雇主内部数据、代码或系统信息。"
            ),
        },
        "cases": _rows("portfolio_case_registry", "case_order"),
        "businessKpis": _rows("portfolio_business_kpis", "display_order"),
        "decisionLoop": _rows("portfolio_decision_loop", "step_order"),
        "growthQualityBridge": _rows("portfolio_growth_quality_bridge", "step_order"),
        "referral": {
            "versions": _rows("portfolio_referral_versions", "version_order"),
            "funnel": _rows("portfolio_referral_funnel", "step_order"),
            "experiment": _experiment("referral_growth"),
        },
        "retention": {
            "trend": _rows("portfolio_retention_trend", "period_order"),
            "segments": _rows("portfolio_retention_segments", "segment_order"),
            "decomposition": _rows("portfolio_retention_decomposition"),
            "path": _rows("portfolio_retention_path", "step_order"),
            "benchmark": _rows("portfolio_benchmark_features"),
            "experiment": _experiment("new_user_retention"),
        },
        "experiments": _rows("portfolio_experiments", "experiment_id"),
        "metricContracts": _rows("portfolio_metric_contracts", "metric_key"),
        "hypothesisLedger": _rows("portfolio_hypothesis_ledger"),
        "decisions": _rows("portfolio_decisions", "decision_id"),
    }


def _experiment(case_id: str) -> dict[str, Any]:
    records = query_records("SELECT * FROM portfolio_experiments WHERE case_id = ?", [case_id])
    if not records:
        raise LookupError(f"Experiment not found for case: {case_id}")
    return records[0]


def overview() -> dict[str, Any]:
    bundle = portfolio_bundle()
    return {
        "meta": bundle["meta"],
        "cases": bundle["cases"],
        "businessKpis": bundle["businessKpis"],
        "decisionLoop": bundle["decisionLoop"],
        "growthQualityBridge": bundle["growthQualityBridge"],
    }


def referral_case() -> dict[str, Any]:
    bundle = portfolio_bundle()
    return {
        "case": next(item for item in bundle["cases"] if item["case_id"] == "referral_growth"),
        **bundle["referral"],
        "decision": next(
            item for item in bundle["decisions"] if item["case_id"] == "referral_growth"
        ),
    }


def retention_case() -> dict[str, Any]:
    bundle = portfolio_bundle()
    return {
        "case": next(item for item in bundle["cases"] if item["case_id"] == "new_user_retention"),
        **bundle["retention"],
        "decision": next(
            item for item in bundle["decisions"] if item["case_id"] == "new_user_retention"
        ),
    }


def experiments_center() -> dict[str, Any]:
    return {"items": _rows("portfolio_experiments", "experiment_id")}


def metrics_governance() -> dict[str, Any]:
    return {"items": _rows("portfolio_metric_contracts", "metric_key")}


def decision_records() -> dict[str, Any]:
    return {"items": _rows("portfolio_decisions", "decision_id")}
