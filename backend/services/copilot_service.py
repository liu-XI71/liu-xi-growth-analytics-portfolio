from __future__ import annotations

from functools import lru_cache
from typing import Any

from analytics.copilot import build_copilot_payload, calculate_experiment_readout
from analytics.copilot.contracts import ExperimentCalculationInput
from backend.config import settings


@lru_cache(maxsize=4)
def _build_payload(
    narrative_mode: str,
    ollama_base_url: str,
    ollama_model: str,
    ollama_timeout_seconds: float,
) -> dict[str, Any]:
    result = build_copilot_payload(
        narrative_mode=narrative_mode,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
        ollama_timeout_seconds=ollama_timeout_seconds,
    )
    return result


def payload() -> dict[str, Any]:
    return _build_payload(
        settings.copilot_narrative_mode,
        settings.ollama_base_url,
        settings.ollama_model,
        settings.ollama_timeout_seconds,
    )


def bundle() -> dict[str, Any]:
    """Return the complete, evidence-bound payload consumed by the web app."""
    return payload()


def overview() -> dict[str, Any]:
    result = payload()
    return {
        key: result[key]
        for key in (
            "meta",
            "decisions",
            "questions",
            "analysis_threads",
            "weekly_reports",
            "cases",
        )
    }


def questions(case_id: str | None = None) -> dict[str, Any]:
    items = payload()["questions"]
    if case_id:
        items = [item for item in items if item["case_id"] == case_id]
    return {"items": items, "count": len(items), "case_id": case_id}


def analysis(analysis_id: str) -> dict[str, Any]:
    result = payload()
    for item in result["analysis_threads"]:
        if item["id"] == analysis_id:
            case = next(case for case in result["cases"] if case["id"] == item["case_id"])
            return {
                "analysis": item,
                "case": case,
                "evidence": [
                    evidence
                    for evidence in result["evidence"]
                    if evidence["case_id"] in {item["case_id"], "cross_case"}
                ],
                "claims": [
                    claim for claim in result["claims"] if claim["case_id"] == item["case_id"]
                ],
            }
    raise LookupError(f"Unknown copilot analysis: {analysis_id}")


def weekly_reports(case_id: str | None = None) -> dict[str, Any]:
    items = payload()["weekly_reports"]
    if case_id:
        items = [item for item in items if item["case_id"] == case_id]
    return {"items": items, "count": len(items), "case_id": case_id}


def metrics() -> dict[str, Any]:
    items = payload()["metric_contracts"]
    return {"items": items, "count": len(items)}


def evidence(case_id: str | None = None, evidence_id: str | None = None) -> dict[str, Any]:
    items = payload()["evidence"]
    if case_id:
        items = [item for item in items if item["case_id"] in {case_id, "cross_case"}]
    if evidence_id:
        items = [item for item in items if item["id"] == evidence_id]
    if evidence_id and not items:
        raise LookupError(f"Unknown copilot evidence: {evidence_id}")
    return {"items": items, "count": len(items), "case_id": case_id}


def calculate_experiment(request: ExperimentCalculationInput) -> dict[str, Any]:
    return calculate_experiment_readout(request)
