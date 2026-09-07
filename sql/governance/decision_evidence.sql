SELECT
  decision_id,
  decision_date,
  decision_stage,
  evidence_level,
  primary_metric,
  final_metric,
  guardrail_metric,
  decision,
  limitation
FROM decision_log
ORDER BY decision_date DESC;
