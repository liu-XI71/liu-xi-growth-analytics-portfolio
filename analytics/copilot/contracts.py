from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class ClaimType(str, Enum):
    FACT = "fact"
    NEGATIVE_EVIDENCE = "negative_evidence"
    INTERPRETATION = "interpretation"
    HYPOTHESIS = "hypothesis"
    CAUSAL_RESULT = "causal_result"
    RECOMMENDATION = "recommendation"
    LIMITATION = "limitation"


class SourceType(str, Enum):
    EXPERIENCE_FACT = "experience_fact"
    EXPERIENCE_RECONSTRUCTION = "experience_reconstruction"
    DERIVED_CALCULATION = "derived_calculation"
    SYNTHETIC_DEMO = "synthetic_demo"
    METHOD_CONTRACT = "method_contract"


class MetricContract(BaseModel):
    metric_id: str
    name: str
    role: str
    numerator: str | None = None
    denominator: str | None = None
    window: str
    grain: str
    decision_use: str
    allowed_claims: list[str]
    forbidden_claims: list[str]
    source_type: SourceType


class EvidenceItem(BaseModel):
    id: str
    case_id: str
    evidence_type: str
    source_type: SourceType
    title: str
    metric_id: str | None = None
    values: dict[str, Any] = Field(default_factory=dict)
    unit: str | None = None
    statement: str
    calculation: str | None = None
    claim_boundary: str
    synthetic: bool = False
    source_ref: str

    @model_validator(mode="after")
    def validate_source_boundary(self) -> EvidenceItem:
        if self.synthetic != (self.source_type == SourceType.SYNTHETIC_DEMO):
            raise ValueError("synthetic flag must match source_type")
        return self


class Claim(BaseModel):
    id: str
    case_id: str
    statement: str
    claim_type: ClaimType
    evidence_ids: list[str] = Field(min_length=1)
    confidence: str
    allowed_scope: str


class ExperimentCalculationInput(BaseModel):
    control_successes: int = Field(ge=0)
    control_n: int = Field(gt=0)
    treatment_successes: int = Field(ge=0)
    treatment_n: int = Field(gt=0)
    baseline_rate: float = Field(gt=0, lt=1)
    mde_absolute: float = Field(gt=0, lt=1)
    alpha: float = Field(default=0.05, gt=0, lt=1)
    power: float = Field(default=0.8, gt=0, lt=1)
    business_mde_absolute: float | None = Field(default=None, gt=0, lt=1)
    expected_treatment_share: float = Field(default=0.5, gt=0, lt=1)
    guardrail_pass: bool | None = None

    @model_validator(mode="after")
    def validate_counts(self) -> ExperimentCalculationInput:
        if self.control_successes > self.control_n:
            raise ValueError("control_successes cannot exceed control_n")
        if self.treatment_successes > self.treatment_n:
            raise ValueError("treatment_successes cannot exceed treatment_n")
        return self
