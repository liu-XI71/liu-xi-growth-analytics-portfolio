from __future__ import annotations

from typing import Any

from analytics.copilot.contracts import ExperimentCalculationInput
from analytics.copilot.numbers import normalize_public_numbers
from analytics.experimentation import (
    assign_hash_group,
    calculate_sample_size,
    check_srm,
    proportion_effect,
)


def stable_hash_assignment(
    unit_id: str | int,
    *,
    salt: str = "liu_xi_growth_analytics_demo_v1",
    buckets: int = 100,
    treatment_buckets: int = 50,
) -> dict[str, int | str]:
    return assign_hash_group(
        unit_id,
        salt=salt,
        buckets=buckets,
        treatment_buckets=treatment_buckets,
    )


def calculate_experiment_readout(
    request: ExperimentCalculationInput | dict[str, Any],
) -> dict[str, Any]:
    item = (
        request
        if isinstance(request, ExperimentCalculationInput)
        else ExperimentCalculationInput.model_validate(request)
    )
    effect = proportion_effect(
        item.control_successes,
        item.control_n,
        item.treatment_successes,
        item.treatment_n,
        alpha=item.alpha,
    )
    if effect["p_value"] == 0:
        effect["p_value"] = 1e-300
        effect["p_value_is_upper_bound"] = True
        effect["p_value_display"] = "<1e-300"
    else:
        effect["p_value_is_upper_bound"] = False
        effect["p_value_display"] = f"{effect['p_value']:.6g}"
    sample_plan = calculate_sample_size(
        baseline_rate=item.baseline_rate,
        mde_absolute=item.mde_absolute,
        alpha=item.alpha,
        power=item.power,
    )
    srm = check_srm(
        [item.control_n, item.treatment_n],
        expected_proportions=[1 - item.expected_treatment_share, item.expected_treatment_share],
        alpha=item.alpha,
    )
    business_threshold = item.business_mde_absolute or item.mde_absolute
    statistical_gate = bool(effect["p_value"] < item.alpha)
    business_gate = bool(effect["absolute_uplift"] >= business_threshold)
    guardrail_gate = item.guardrail_pass
    if not srm.get("pass"):
        recommendation = "DO_NOT_DECIDE_ASSIGNMENT_QUALITY"
    elif statistical_gate and business_gate and guardrail_gate is True:
        recommendation = "SHIP_WITH_MONITORING"
    elif guardrail_gate is None:
        recommendation = "CONTINUE_GUARDRAIL_REQUIRED"
    else:
        recommendation = "DO_NOT_SHIP"
    hash_preview = [stable_hash_assignment(unit_id) for unit_id in range(1001, 1009)]
    result = {
        "input": item.model_dump(),
        "sample_plan": sample_plan,
        "assignment": {
            "unit": "user_id",
            "method": "SHA-256 stable hash modulo 100",
            "ratio": "1:1",
            "preview": hash_preview,
            "stability_check": stable_hash_assignment(1001) == stable_hash_assignment(1001),
        },
        "srm": srm,
        "effect": {
            **effect,
            "relative_uplift": (
                effect["absolute_uplift"] / effect["control_rate"]
                if effect["control_rate"]
                else None
            ),
            "relative_uplift_pct": (
                100 * effect["absolute_uplift"] / effect["control_rate"]
                if effect["control_rate"]
                else None
            ),
            "confidence_interval_absolute": {
                "lower": effect["ci_lower"],
                "upper": effect["ci_upper"],
            },
        },
        "gates": {
            "statistical": {
                "passed": statistical_gate,
                "rule": f"p_value < {item.alpha}",
            },
            "business": {
                "passed": business_gate,
                "threshold_absolute": business_threshold,
            },
            "guardrail": {
                "passed": guardrail_gate,
                "status": "evaluated" if guardrail_gate is not None else "not_evaluated",
            },
        },
        "recommendation": recommendation,
        "warnings": [
            "Do not stop an experiment because of repeated unadjusted interim p-value checks.",
            "Inspect novelty and network-interference risks before broad rollout.",
            "Statistical significance, business significance and guardrails are separate gates.",
        ],
    }
    return normalize_public_numbers(result)
