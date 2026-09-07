from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def calculate_first_month_economics(
    *,
    active_days_30: float,
    daily_active_hours: float,
    value_per_hour: float,
    attributed_incentive_cost: float,
    retention_discount: float = 1.0,
    external_benchmark_ratio: float = 1.6,
) -> dict[str, float | bool | str]:
    """Estimate a bounded first-month value-to-attributed-cost comparison.

    The denominator covers only the incentive cost attributed to an activated
    referral. It is neither a fully loaded acquisition cost nor a company-wide
    customer acquisition cost. The numerator is a 30-day modelled value, not a
    complete customer lifetime value.
    """
    values = [active_days_30, daily_active_hours, value_per_hour, attributed_incentive_cost]
    if any(value < 0 for value in values) or not 0 <= retention_discount <= 1:
        raise ValueError(
            "Economics inputs must be non-negative and retention_discount must be in [0, 1]"
        )
    if attributed_incentive_cost == 0:
        raise ValueError("attributed_incentive_cost must be greater than zero")
    undiscounted_first_month_value = active_days_30 * daily_active_hours * value_per_hour
    first_month_value = undiscounted_first_month_value * retention_discount
    ratio = first_month_value / attributed_incentive_cost
    return {
        "undiscounted_first_month_value": undiscounted_first_month_value,
        "first_month_value": first_month_value,
        "attributed_incentive_cost": attributed_incentive_cost,
        "first_month_value_cost_ratio": ratio,
        "first_month_attributed_cost_net_return": (first_month_value - attributed_incentive_cost),
        "break_even_attributed_incentive_cost": first_month_value,
        "external_benchmark_ratio": external_benchmark_ratio,
        "above_external_benchmark": ratio >= external_benchmark_ratio,
        "claim_boundary": (
            "First-month modelled value divided by attributed referral incentive cost; "
            "not full lifetime value, fully loaded acquisition cost, or a net return ratio."
        ),
    }


def sensitivity_analysis(
    base: Mapping[str, float],
    variations: Mapping[str, Sequence[float]],
) -> dict[str, Any]:
    required = {
        "active_days_30",
        "daily_active_hours",
        "value_per_hour",
        "attributed_incentive_cost",
        "retention_discount",
    }
    missing = required - set(base)
    if missing:
        raise ValueError(f"Missing base inputs: {sorted(missing)}")
    base_result = calculate_first_month_economics(**base)
    items = []
    for parameter, multipliers in variations.items():
        if parameter not in required:
            raise ValueError(f"Unsupported sensitivity parameter: {parameter}")
        for multiplier in multipliers:
            scenario = dict(base)
            scenario[parameter] = base[parameter] * float(multiplier)
            if parameter == "retention_discount":
                scenario[parameter] = min(1.0, max(0.0, scenario[parameter]))
            result = calculate_first_month_economics(**scenario)
            items.append(
                {
                    "parameter": parameter,
                    "multiplier": float(multiplier),
                    "input_value": scenario[parameter],
                    "first_month_value_cost_ratio": result["first_month_value_cost_ratio"],
                    "first_month_attributed_cost_net_return": result[
                        "first_month_attributed_cost_net_return"
                    ],
                    "change_from_base": result["first_month_value_cost_ratio"]
                    - base_result["first_month_value_cost_ratio"],
                }
            )
    return {"base": base_result, "items": items}
