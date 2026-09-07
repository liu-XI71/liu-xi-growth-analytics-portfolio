from __future__ import annotations

import pytest

from analytics.economics import calculate_first_month_economics, sensitivity_analysis


def test_first_month_economics_uses_bounded_value_and_cost_formulas() -> None:
    result = calculate_first_month_economics(
        active_days_30=10,
        daily_active_hours=0.5,
        value_per_hour=4,
        attributed_incentive_cost=8,
        retention_discount=0.8,
        external_benchmark_ratio=1.9,
    )

    assert result["undiscounted_first_month_value"] == pytest.approx(20.0)
    assert result["first_month_value"] == pytest.approx(16.0)
    assert result["attributed_incentive_cost"] == pytest.approx(8.0)
    assert result["first_month_value_cost_ratio"] == pytest.approx(2.0)
    assert result["first_month_attributed_cost_net_return"] == pytest.approx(8.0)
    assert result["break_even_attributed_incentive_cost"] == pytest.approx(16.0)
    assert result["above_external_benchmark"] is True
    assert "not full lifetime value" in result["claim_boundary"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"active_days_30": -1},
        {"daily_active_hours": -0.1},
        {"value_per_hour": -1},
        {"attributed_incentive_cost": 0},
        {"retention_discount": -0.1},
        {"retention_discount": 1.1},
    ],
)
def test_first_month_economics_rejects_invalid_inputs(
    overrides: dict[str, float],
) -> None:
    inputs = {
        "active_days_30": 10.0,
        "daily_active_hours": 0.5,
        "value_per_hour": 4.0,
        "attributed_incentive_cost": 8.0,
        "retention_discount": 0.8,
    }
    inputs.update(overrides)
    with pytest.raises(ValueError):
        calculate_first_month_economics(**inputs)


def test_sensitivity_preserves_base_and_moves_cost_ratio_in_expected_direction() -> None:
    base = {
        "active_days_30": 10.0,
        "daily_active_hours": 0.5,
        "value_per_hour": 4.0,
        "attributed_incentive_cost": 8.0,
        "retention_discount": 0.8,
    }
    output = sensitivity_analysis(base, {"attributed_incentive_cost": [0.8, 1.2]})
    assert output["base"]["first_month_value_cost_ratio"] == pytest.approx(2.0)
    low_cost, high_cost = output["items"]
    assert low_cost["first_month_value_cost_ratio"] > output["base"]["first_month_value_cost_ratio"]
    assert (
        high_cost["first_month_value_cost_ratio"] < output["base"]["first_month_value_cost_ratio"]
    )
