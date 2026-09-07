from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import httpx

from analytics.copilot.contracts import EvidenceItem
from analytics.copilot.evidence import validate_narrative_numbers, validate_narrative_semantics


class NarrativeGuardrailError(ValueError):
    def __init__(self, *, reason: str, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.reason = reason
        self.errors = errors


def _validate_narrative(text: str, evidence: list[EvidenceItem]) -> tuple[list[str], list[str]]:
    number_errors = validate_narrative_numbers(text, evidence)
    semantic_errors = validate_narrative_semantics(text, evidence)
    return number_errors, semantic_errors


def deterministic_narrative(
    *,
    headline: str,
    summary: str,
    evidence: list[EvidenceItem],
) -> dict[str, Any]:
    number_errors, semantic_errors = _validate_narrative(f"{headline} {summary}", evidence)
    if number_errors or semantic_errors:
        raise ValueError(
            "Deterministic narrative violates its evidence contract: "
            f"{number_errors + semantic_errors}"
        )
    return {
        "mode": "deterministic",
        "status": "ready",
        "headline": headline,
        "text": summary,
        "evidence_ids": [item.id for item in evidence],
        "validation_errors": [],
    }


def _ollama_prompt(evidence: list[EvidenceItem]) -> str:
    evidence_payload = [item.model_dump(mode="json") for item in evidence]
    return (
        "你是用户增长分析周报编辑器。只能使用下面JSON证据，不得添加数字、公司内部事实或"
        "未提供的实验结果。区分事实、负证据、相关性、假设和随机实验结论；不得把相关性写成"
        "因果，不得把次7日内留存率写成精确D7，不得把首月价值/激励成本倍数写成完整ROI、LTV或CAC。"
        '输出严格JSON：{"headline":"...","text":"..."}。证据：'
        + json.dumps(evidence_payload, ensure_ascii=False, separators=(",", ":"))
    )


def ollama_narrative(
    *,
    fallback: dict[str, Any],
    evidence: list[EvidenceItem],
    base_url: str,
    model: str,
    timeout_seconds: float = 8.0,
    post: Callable[..., httpx.Response] | None = None,
) -> dict[str, Any]:
    sender = post or httpx.post
    try:
        response = sender(
            f"{base_url.rstrip('/')}/api/generate",
            json={
                "model": model,
                "prompt": _ollama_prompt(evidence),
                "stream": False,
                "format": "json",
                "options": {"temperature": 0},
            },
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        generated = json.loads(str(body["response"]))
        headline = str(generated["headline"]).strip()
        text = str(generated["text"]).strip()
        number_errors, semantic_errors = _validate_narrative(f"{headline} {text}", evidence)
        if number_errors:
            raise NarrativeGuardrailError(reason="unsupported_numbers", errors=number_errors)
        if semantic_errors:
            raise NarrativeGuardrailError(reason="semantic_guardrail", errors=semantic_errors)
        return {
            "mode": "ollama",
            "status": "ready",
            "headline": headline,
            "text": text,
            "evidence_ids": [item.id for item in evidence],
            "validation_errors": [],
        }
    except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        result = {
            **fallback,
            "mode": "deterministic_fallback",
            "status": "fallback",
            "fallback_reason": (
                error.reason if isinstance(error, NarrativeGuardrailError) else type(error).__name__
            ),
        }
        if isinstance(error, NarrativeGuardrailError):
            result["rejected_generation_errors"] = error.errors
        return result


def generate_narrative(
    *,
    mode: str,
    headline: str,
    summary: str,
    evidence: list[EvidenceItem],
    ollama_base_url: str = "http://127.0.0.1:11434",
    ollama_model: str = "qwen2.5:7b",
    timeout_seconds: float = 8.0,
    post: Callable[..., httpx.Response] | None = None,
) -> dict[str, Any]:
    fallback = deterministic_narrative(headline=headline, summary=summary, evidence=evidence)
    if mode != "ollama":
        return fallback
    return ollama_narrative(
        fallback=fallback,
        evidence=evidence,
        base_url=ollama_base_url,
        model=ollama_model,
        timeout_seconds=timeout_seconds,
        post=post,
    )
