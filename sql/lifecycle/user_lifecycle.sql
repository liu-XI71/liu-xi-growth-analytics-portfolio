-- One row per activated referral edge.  Retention comes from exact user-day activity,
-- not from multiplying a campaign conversion rate by an unrelated cohort average.
SELECT
  e.edge_id,
  e.source_kind,
  e.experiment_id,
  e.group_name,
  e.inviter_user_id,
  e.new_user_id,
  e.activated_date,
  r.mature_d7,
  r.mature_d30,
  r.retained_d1,
  r.retained_d7,
  r.retained_d1_7_window,
  r.retained_d30,
  a.first_month_value,
  a.variable_acquisition_cost,
  a.first_month_attributed_cost_net_return
FROM referral_edges e
JOIN new_user_retention r ON r.user_id = e.new_user_id
LEFT JOIN acquired_users a ON a.new_user_id = e.new_user_id;
