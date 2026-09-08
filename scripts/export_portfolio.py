from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from scripts.portfolio_data import portfolio_frames

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "web" / "public" / "data" / "portfolio.json"


def _value(value: Any) -> Any:
    if value is None or (isinstance(value, (float, np.floating)) and np.isnan(value)):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [{key: _value(value) for key, value in row.items()} for row in frame.to_dict("records")]


def build_bundle() -> dict[str, Any]:
    frames = portfolio_frames()
    experiments = _records(frames["portfolio_experiments"])
    cases = _records(frames["portfolio_case_registry"])
    decisions = _records(frames["portfolio_decisions"])
    return {
        "meta": {
            "projectName": "Liu Xi Growth & Experiments",
            "projectNameZh": "刘希｜增长与实验",
            "version": "1.2.0",
            "dataBoundary": (
                "关键变化来自去标识化实习复盘；本地数据库行级明细由固定规则生成，不包含雇主内部数据、代码或系统信息。"
            ),
        },
        "cases": cases,
        "businessKpis": _records(frames["portfolio_business_kpis"]),
        "decisionLoop": _records(frames["portfolio_decision_loop"]),
        "growthQualityBridge": _records(frames["portfolio_growth_quality_bridge"]),
        "referral": {
            "versions": _records(frames["portfolio_referral_versions"]),
            "funnel": _records(frames["portfolio_referral_funnel"]),
            "experiment": next(
                item for item in experiments if item["case_id"] == "referral_growth"
            ),
        },
        "retention": {
            "trend": _records(frames["portfolio_retention_trend"]),
            "segments": _records(frames["portfolio_retention_segments"]),
            "decomposition": _records(frames["portfolio_retention_decomposition"]),
            "path": _records(frames["portfolio_retention_path"]),
            "benchmark": _records(frames["portfolio_benchmark_features"]),
            "experiment": next(
                item for item in experiments if item["case_id"] == "new_user_retention"
            ),
        },
        "experiments": experiments,
        "metricContracts": _records(frames["portfolio_metric_contracts"]),
        "hypothesisLedger": _records(frames["portfolio_hypothesis_ledger"]),
        "decisions": decisions,
    }


def export_bundle(output: Path = DEFAULT_OUTPUT) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as target:
        target.write(
            json.dumps(build_bundle(), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the public portfolio data bundle")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(export_bundle(args.output))


if __name__ == "__main__":
    main()
