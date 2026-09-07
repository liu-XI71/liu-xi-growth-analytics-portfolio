-- Primary causal decision estimand: randomized intention-to-treat (ITT).
-- Non-acquired assignments contribute zero to quality and attributed-cost net-return outcomes.
WITH arm AS (
  SELECT
    experiment_id,
    group_name,
    COUNT(*) AS assigned_users,
    SUM(retained_d7::INTEGER) AS retained_d7_users,
    SUM(retained_d1_7_window::INTEGER) AS retained_d1_7_users,
    SUM(first_month_attributed_cost_net_return)
      AS first_month_attributed_cost_net_return
  FROM mart_experiment_user_value
  WHERE experiment_id = 'synthetic_referral_ui_scenario'
  GROUP BY 1, 2
)
SELECT
  10000.0 * (
    MAX(retained_d7_users / assigned_users::DOUBLE) FILTER (group_name='treatment')
    - MAX(retained_d7_users / assigned_users::DOUBLE) FILTER (group_name='control')
  ) AS incremental_d7_retained_per_10k_assigned,
  10000.0 * (
    MAX(retained_d1_7_users / assigned_users::DOUBLE) FILTER (group_name='treatment')
    - MAX(retained_d1_7_users / assigned_users::DOUBLE) FILTER (group_name='control')
  ) AS incremental_d1_7_retained_per_10k_assigned,
  10000.0 * (
    MAX(first_month_attributed_cost_net_return / assigned_users::DOUBLE)
      FILTER (group_name='treatment')
    - MAX(first_month_attributed_cost_net_return / assigned_users::DOUBLE)
      FILTER (group_name='control')
  ) AS incremental_first_month_attributed_cost_net_return_per_10k_assigned
FROM arm;
