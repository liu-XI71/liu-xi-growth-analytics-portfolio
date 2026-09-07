-- Descriptive campaign quality.  This model must not be labelled causal because
-- campaign versions were launched in different time periods.
SELECT
  acquisition_source,
  acquisition_campaign,
  acquisition_treatment,
  acquired_users,
  d7_retention,
  d1_7_window_retention,
  total_first_month_value,
  total_variable_acquisition_cost,
  first_month_value_cost_ratio,
  total_first_month_attributed_cost_net_return
FROM mart_acquisition_quality;
