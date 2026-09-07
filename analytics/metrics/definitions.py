from __future__ import annotations

from typing import Any

METRIC_DEFINITIONS: list[dict[str, str | None]] = [
    {
        "metric_name": "referral_new_users",
        "display_name_zh": "老带新激活用户数",
        "display_name_en": "Referral activated users",
        "description": "通过邀请链路完成激活的新用户去重数。",
        "formula": "COUNT(DISTINCT new_user_id WHERE activated)",
        "numerator": None,
        "denominator": None,
        "unit": "users",
        "grain": "day × campaign_version",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "invite_click_rate",
        "display_name_zh": "邀请点击率",
        "display_name_en": "Invite click-through rate",
        "description": "访问活动页面的老用户中点击邀请按钮的比例。",
        "formula": "invite_click_uv / campaign_page_visit_uv",
        "numerator": "invite_click_uv",
        "denominator": "campaign_page_visit_uv",
        "unit": "ratio",
        "grain": "day × campaign_version",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "share_success_rate",
        "display_name_zh": "分享成功率",
        "display_name_en": "Share success rate",
        "description": "点击邀请的用户中完成分享的比例。",
        "formula": "share_success_uv / invite_click_uv",
        "numerator": "share_success_uv",
        "denominator": "invite_click_uv",
        "unit": "ratio",
        "grain": "day × campaign_version",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "activation_per_exposure",
        "display_name_zh": "曝光到新用户激活率",
        "display_name_en": "Activation per exposure",
        "description": "激活新用户数除以活动曝光老用户数。",
        "formula": "new_user_activate_uv / campaign_exposure_uv",
        "numerator": "new_user_activate_uv",
        "denominator": "campaign_exposure_uv",
        "unit": "ratio",
        "grain": "day × campaign_version",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "activation_per_invite_click",
        "display_name_zh": "邀请点击到新用户激活率",
        "display_name_en": "Activation per invite click",
        "description": "激活新用户数除以邀请点击用户数。",
        "formula": "new_user_activate_uv / invite_click_uv",
        "numerator": "new_user_activate_uv",
        "denominator": "invite_click_uv",
        "unit": "ratio",
        "grain": "day × campaign_version",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "invites_per_inviter",
        "display_name_zh": "邀请者人均拉新",
        "display_name_en": "Activated users per inviter",
        "description": "完成激活的新用户数除以有效邀请者数。",
        "formula": "new_user_activate_uv / effective_inviter_uv",
        "numerator": "new_user_activate_uv",
        "denominator": "effective_inviter_uv",
        "unit": "users_per_inviter",
        "grain": "day × campaign_version",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "first_month_value",
        "display_name_zh": "新用户首月价值",
        "display_name_en": "First-month modelled value",
        "description": (
            "用前30日活跃天数、日均时长和单位时长价值估算的首月价值，不代表完整生命周期价值。"
        ),
        "formula": "active_days_30 × daily_hours × value_per_hour",
        "numerator": None,
        "denominator": None,
        "unit": "normalized_value",
        "grain": "acquisition_version",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "attributed_incentive_cost",
        "display_name_zh": "归因激励成本",
        "display_name_en": "Attributed incentive cost",
        "description": ("归因到成功激活新用户的平均邀请激励成本，不含全部渠道、运营与固定成本。"),
        "formula": "total_attributed_incentive_cost / activated_new_users",
        "numerator": "total_attributed_incentive_cost",
        "denominator": "activated_new_users",
        "unit": "normalized_cost",
        "grain": "acquisition_version",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "first_month_value_cost_ratio",
        "display_name_zh": "首月价值/激励成本倍数",
        "display_name_en": "First-month value-to-cost ratio",
        "description": (
            "首月估算用户价值与归因激励成本的比值，不代表完整生命周期收益、全部获客成本或净回报率。"
        ),
        "formula": "first_month_value / attributed_incentive_cost",
        "numerator": "first_month_value",
        "denominator": "attributed_incentive_cost",
        "unit": "ratio",
        "grain": "acquisition_version",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "first_month_attributed_cost_net_return",
        "display_name_zh": "首月归因成本后净回报",
        "display_name_en": "First-month attributed-cost net return",
        "description": (
            "首月估算价值扣除可归因的可变服务成本与可变获客成本后的标准化金额，不代表完整利润。"
        ),
        "formula": (
            "first_month_value - first_month_variable_service_cost - variable_acquisition_cost"
        ),
        "numerator": None,
        "denominator": None,
        "unit": "normalized_value",
        "grain": "acquisition_version",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "d1_7_window_retention",
        "display_name_zh": "次1至7日窗口留存",
        "display_name_en": "Day 1-7 window retention",
        "description": "新增后第1至7天内至少活跃一次的用户占比，不等同于精确D7留存。",
        "formula": "users active on any day 1..7 / new users",
        "numerator": "retained_d1_7_window_users",
        "denominator": "new_users",
        "unit": "ratio",
        "grain": "signup_cohort",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "incremental_d7_retained_per_10k_assigned",
        "display_name_zh": "每万分流增量D7留存新用户",
        "display_name_en": "Incremental D7 retained users per 10k assigned",
        "description": "随机实验ITT口径：每万名被分流老用户带来的增量精确D7留存新用户。未拉新用户贡献为0。",
        "formula": "10000 × (retained_D7_T / assigned_T - retained_D7_C / assigned_C)",
        "numerator": "difference in D7-retained referred users",
        "denominator": "experiment assignment",
        "unit": "users_per_10k_assigned",
        "grain": "experiment × arm",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "incremental_d1_7_retained_per_10k_assigned",
        "display_name_zh": "每万分流增量D1-7窗口留存新用户",
        "display_name_en": "Incremental D1-7 retained users per 10k assigned",
        "description": "随机实验ITT口径：每万名被分流老用户带来的增量D1-7窗口留存新用户。未拉新用户贡献为0。",
        "formula": "10000 × (retained_D1_7_T / assigned_T - retained_D1_7_C / assigned_C)",
        "numerator": "difference in D1-7 retained referred users",
        "denominator": "experiment assignment",
        "unit": "users_per_10k_assigned",
        "grain": "experiment × arm",
        "owner_role": "growth_analytics",
    },
    {
        "metric_name": "incremental_first_month_attributed_cost_net_return_per_10k_assigned",
        "display_name_zh": "每万分流首月增量贡献价值",
        "display_name_en": "Incremental first-month attributed-cost net return per 10k assigned",
        "description": (
            "随机实验ITT口径：未获客用户净回报记0，比较每万分流用户带来的"
            "首月估算价值减可归因的可变服务与获客成本。"
        ),
        "formula": ("10000 × [Σ(first_month_attributed_cost_net_return)_T / assigned_T - same_C]"),
        "numerator": "difference in first-month attributed-cost net return",
        "denominator": "experiment assignment",
        "unit": "normalized_value_per_10k_assigned",
        "grain": "experiment × arm",
        "owner_role": "growth_analytics",
    },
]


# A metric is a governed decision contract, not merely a display label.  Defaults
# complete every definition with a consistent set of decision and lineage fields.
for _metric in METRIC_DEFINITIONS:
    _metric.setdefault("metric_type", "diagnostic")
    _metric.setdefault("decision_use", "Diagnose a governed stage of the growth lifecycle.")
    _metric.setdefault("eligibility", "Rows satisfying the documented source-table contract.")
    _metric.setdefault(
        "inclusion_exclusion", "Deduplicate by governed user and window; exclude test traffic."
    )
    _metric.setdefault("attribution_window", "As defined in formula and grain.")
    _metric.setdefault("observation_window", "As defined in formula and grain.")
    _metric.setdefault("timezone", "UTC")
    _metric.setdefault("freshness_sla", "Regenerated as one deterministic portfolio snapshot.")
    _metric.setdefault("source_table", "See metric lineage endpoint.")
    _metric.setdefault("sql_model", "See metric lineage endpoint.")
    _metric.setdefault(
        "claim_boundary", "Descriptive unless an explicit randomized estimand is named."
    )

for _metric_name in {
    "incremental_d7_retained_per_10k_assigned",
    "incremental_d1_7_retained_per_10k_assigned",
    "incremental_first_month_attributed_cost_net_return_per_10k_assigned",
}:
    _item = next(item for item in METRIC_DEFINITIONS if item["metric_name"] == _metric_name)
    _item["metric_type"] = "final_business"
    _item["decision_use"] = "Primary causal rollout and resource-allocation decision evidence."
    _item["eligibility"] = "All users assigned to the pre-registered referral UI experiment."
    _item["inclusion_exclusion"] = (
        "ITT: retain every assignment; non-acquired users contribute zero."
    )
    _item["attribution_window"] = "Assignment through referred-user activation."
    _item["observation_window"] = "Exact D7, D1-7 window, or 30 days as named."
    _item["source_table"] = "mart_experiment_user_value"
    _item["sql_model"] = "sql/experiments/quality_adjusted_effects.sql"
    _item["claim_boundary"] = "Causal only for the randomized ITT population and fixed horizon."

for _metric_name in {"referral_new_users", "d1_7_window_retention"}:
    _item = next(item for item in METRIC_DEFINITIONS if item["metric_name"] == _metric_name)
    _item["metric_type"] = "final_business"
    _item["decision_use"] = "Evaluate whether the business outcome improved."

for _metric_name in {"invite_click_rate", "activation_per_exposure"}:
    _item = next(item for item in METRIC_DEFINITIONS if item["metric_name"] == _metric_name)
    _item["metric_type"] = "mechanism"
    _item["decision_use"] = "Localize the mechanism; never substitute for the final value outcome."

_share_success = next(
    item for item in METRIC_DEFINITIONS if item["metric_name"] == "share_success_rate"
)
_share_success["metric_type"] = "diagnostic"
_share_success["decision_use"] = "Test whether loss occurs after the invitation click."

for _metric_name in {
    "first_month_value_cost_ratio",
    "first_month_attributed_cost_net_return",
}:
    _item = next(item for item in METRIC_DEFINITIONS if item["metric_name"] == _metric_name)
    _item["metric_type"] = "guardrail"
    _item["decision_use"] = "Evaluate whether an effective strategy remains economically viable."


def metric_tree() -> dict[str, Any]:
    """Return the governed business tree shown by the application."""
    return {
        "name": "Active user growth index",
        "display_name": "活跃用户增长指数",
        "unit": "index",
        "children": [
            {"name": "paid_acquisition", "display_name": "外部获客新增"},
            {"name": "organic_acquisition", "display_name": "自然新增"},
            {
                "name": "referral_new_users",
                "display_name": "老带新新增",
                "children": [
                    {"name": "campaign_exposure_uv", "display_name": "活动曝光UV"},
                    {"name": "campaign_page_visit_uv", "display_name": "活动访问UV"},
                    {"name": "invite_click_uv", "display_name": "邀请点击UV"},
                    {"name": "share_success_uv", "display_name": "分享成功UV"},
                    {"name": "new_user_landing_uv", "display_name": "新用户到达UV"},
                    {"name": "new_user_activate_uv", "display_name": "新用户激活UV"},
                ],
            },
        ],
        "disclaimer": (
            "Operational records are synthetic and normalized; de-identified case facts "
            "are served separately by the portfolio endpoints."
        ),
    }
