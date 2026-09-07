CREATE TABLE IF NOT EXISTS copilot_metric_contracts (
    metric_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    numerator VARCHAR,
    denominator VARCHAR,
    window_definition VARCHAR NOT NULL,
    grain VARCHAR NOT NULL,
    decision_use VARCHAR NOT NULL,
    allowed_claims_json JSON NOT NULL,
    forbidden_claims_json JSON NOT NULL,
    source_type VARCHAR NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS copilot_evidence (
    evidence_id VARCHAR PRIMARY KEY,
    case_id VARCHAR NOT NULL,
    evidence_type VARCHAR NOT NULL,
    source_type VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    metric_id VARCHAR,
    values_json JSON NOT NULL,
    statement VARCHAR NOT NULL,
    calculation VARCHAR,
    claim_boundary VARCHAR NOT NULL,
    is_synthetic BOOLEAN NOT NULL,
    source_ref VARCHAR NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS copilot_claims (
    claim_id VARCHAR PRIMARY KEY,
    case_id VARCHAR NOT NULL,
    statement VARCHAR NOT NULL,
    claim_type VARCHAR NOT NULL,
    evidence_ids_json JSON NOT NULL,
    confidence VARCHAR NOT NULL,
    allowed_scope VARCHAR NOT NULL,
    validation_passed BOOLEAN NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS copilot_weekly_reports (
    report_id VARCHAR PRIMARY KEY,
    case_id VARCHAR NOT NULL,
    period VARCHAR NOT NULL,
    previous_period VARCHAR NOT NULL,
    report_json JSON NOT NULL,
    narrative_mode VARCHAR NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
