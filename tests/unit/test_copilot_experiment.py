from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from analytics.copilot import calculate_experiment_readout, stable_hash_assignment
from analytics.copilot.contracts import ExperimentCalculationInput


def _request(**overrides):
    values = {
        "control_successes": 1700,
        "control_n": 10_000,
        "treatment_successes": 2350,
        "treatment_n": 10_000,
        "baseline_rate": 0.17,
        "mde_absolute": 0.03,
        "alpha": 0.05,
        "power": 0.80,
        "business_mde_absolute": 0.03,
        "expected_treatment_share": 0.5,
        "guardrail_pass": True,
    }
    values.update(overrides)
    return values


def test_experiment_readout_computes_effect_ci_srm_hash_and_three_gates() -> None:
    result = calculate_experiment_readout(_request())
    effect = result["effect"]
    assert effect["control_rate"] == pytest.approx(0.17)
    assert effect["treatment_rate"] == pytest.approx(0.235)
    assert effect["absolute_uplift_pp"] == pytest.approx(6.5)
    assert effect["relative_uplift_pct"] == pytest.approx(38.2)
    assert effect["confidence_interval_absolute"]["lower"] > 0
    assert effect["z_stat"] > 1.96
    assert effect["p_value"] < 0.05
    assert result["sample_plan"]["sample_total"] > 0
    assert result["srm"]["pass"] is True
    assert result["assignment"]["stability_check"] is True
    assert result["gates"]["statistical"]["passed"] is True
    assert result["gates"]["business"]["passed"] is True
    assert result["gates"]["guardrail"]["passed"] is True
    assert result["recommendation"] == "SHIP_WITH_MONITORING"


def test_hash_assignment_is_stable_and_salt_sensitive() -> None:
    first = stable_hash_assignment("user-42")
    second = stable_hash_assignment("user-42")
    other_salt = stable_hash_assignment("user-42", salt="other-experiment")
    assert first == second
    assert first["unit_id"] == "user-42"
    assert 0 <= first["bucket"] < 100
    assert first != other_salt


def test_backend_matches_shared_frontend_hash_vectors() -> None:
    contract_path = Path(__file__).resolve().parents[2] / "data" / "contracts" / "hash_vectors.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    for vector in contract["vectors"]:
        result = stable_hash_assignment(
            vector["unit_id"],
            salt=contract["salt"],
            buckets=contract["buckets"],
            treatment_buckets=contract["treatment_buckets"],
        )
        assert result == vector


def test_guardrail_missing_and_srm_failure_do_not_ship() -> None:
    missing_guardrail = calculate_experiment_readout(_request(guardrail_pass=None))
    assert missing_guardrail["recommendation"] == "CONTINUE_GUARDRAIL_REQUIRED"
    srm_failure = calculate_experiment_readout(
        _request(
            control_n=10_000, control_successes=1700, treatment_n=20_000, treatment_successes=4700
        )
    )
    assert srm_failure["srm"]["pass"] is False
    assert srm_failure["recommendation"] == "DO_NOT_DECIDE_ASSIGNMENT_QUALITY"


@pytest.mark.parametrize(
    "field,value",
    [
        ("control_successes", 10_001),
        ("treatment_successes", 10_001),
        ("baseline_rate", 0),
        ("mde_absolute", 1),
        ("expected_treatment_share", 1),
    ],
)
def test_invalid_experiment_inputs_are_rejected(field: str, value: float) -> None:
    with pytest.raises(ValidationError):
        ExperimentCalculationInput.model_validate(_request(**{field: value}))
