from __future__ import annotations

import numpy as np
import pandas as pd

PROJECT_NAME = "Liu Xi Growth Analytics Portfolio"
PROJECT_NAME_ZH = "刘希｜增长分析与实验决策作品集"


def _case_registry() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "case_id": "referral_growth",
                "case_order": 1,
                "experience": "字节跳动｜用户增长",
                "title": "老带新获客增长",
                "business_question": "外部拉新供给承压时，如何提升老带新新增规模并维持首月投入效率？",
                "primary_metric": "拉新用户数",
                "mechanism_metric": "邀请点击率",
                "decision_metric": "首月价值/激励成本",
                "evidence_boundary": "漏斗与版本变化用于定位，A/B实验验证页面策略效果。",
            },
            {
                "case_id": "new_user_retention",
                "case_order": 2,
                "experience": "小红书｜新用户留存",
                "title": "新用户留存提升",
                "business_question": "投放带来的新用户为什么留不住，什么产品引导能够提升次7日内留存？",
                "primary_metric": "次7日内留存率",
                "mechanism_metric": "关注行为渗透率",
                "decision_metric": "次7日内留存实验结果",
                "evidence_boundary": "分层、路径和标杆分析生成线索，A/B实验验证引导策略效果。",
            },
        ]
    )


def _business_kpis() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "case_id": "overview",
                "metric_key": "dau_gap_index",
                "label": "DAU目标完成度",
                "value": 81.25,
                "unit": "%",
                "display_value": "81.25%",
                "status": "attention",
                "evidence_type": "normalized business target",
                "note": "规模指数化后，当前81.25、目标100。",
                "display_order": 1,
            },
            {
                "case_id": "referral_growth",
                "metric_key": "invite_click_lift",
                "label": "邀请点击率实验提升",
                "value": 6.5,
                "unit": "pp",
                "display_value": "+6.5 pp",
                "status": "positive",
                "evidence_type": "de-identified experiment result",
                "note": "简化页面并将邀请按钮放回首屏：17.0%→23.5%。",
                "display_order": 2,
            },
            {
                "case_id": "new_user_retention",
                "metric_key": "retention_decline",
                "label": "次7日内留存异常",
                "value": -7.0,
                "unit": "pp",
                "display_value": "48% → 41%",
                "status": "negative",
                "evidence_type": "de-identified monitoring result",
                "note": "新增后第1至7天内至少再次访问一次。",
                "display_order": 3,
            },
            {
                "case_id": "referral_growth",
                "metric_key": "m1_value_cost_guardrail",
                "label": "首月价值/激励成本倍数",
                "value": 2.18,
                "unit": "x",
                "display_value": "2.18× vs 1.90×",
                "status": "positive",
                "evidence_type": "de-identified economic result",
                "note": "老带新版本高于外部投放基准。",
                "display_order": 4,
            },
        ]
    )


def _decision_loop() -> pd.DataFrame:
    rows = [
        (
            1,
            "monitor",
            "监测异常",
            "发生了什么？",
            "外部拉新供给下降，DAU存在目标差距。",
            "次7日内留存率从48%下滑到41%。",
        ),
        (
            2,
            "define",
            "定义指标",
            "什么指标代表业务结果？",
            "拉新用户数为结果，邀请点击率为机制，首月价值/激励成本倍数约束投入。",
            "次7日内窗口留存为核心，同时观察分层、路径与功能行为。",
        ),
        (
            3,
            "diagnose",
            "拆解定位",
            "损失发生在哪个环节或人群？",
            "玩法升级后邀请点击率从约21%降到17%，断点位于邀请动作。",
            "设备结构形成方向性压力；缺少分期设备占比，无法准确量化贡献。",
        ),
        (
            4,
            "exclude",
            "保留负证据",
            "哪些解释不被数据支持？",
            "分享成功率约95%，现有证据不支持分享完成环节是主要断点。",
            "下载到关注的主要路径转化率未同步下降，现有证据不支持普遍路径阻塞是主要解释。",
        ),
        (
            5,
            "hypothesize",
            "提出机制",
            "什么机制能够被验证？",
            "页面信息过多且CTA位于第二页，可能提高邀请发现成本。",
            "主页与关注引导可能帮助新用户建立持续内容关系。",
        ),
        (
            6,
            "experiment",
            "实验验证",
            "策略是否产生增量效果？",
            "首屏简化版运行两周、总样本约700万，邀请点击率17%→23.5%，p<0.05。",
            "退出页关注引导运行两周、总样本约30万，次7日内留存显著提升，p<0.05。",
        ),
        (
            7,
            "decide",
            "价值决策",
            "结果是否支持继续迭代？",
            "首月价值/激励成本倍数为2.18，高于同口径外部投放的1.90，支持继续迭代。",
            "建议继续推进并持续优化，同时监控新用户体验与长期留存。",
        ),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "step_order",
            "step_key",
            "label",
            "question",
            "referral_application",
            "retention_application",
        ],
    )


def _growth_quality_bridge() -> pd.DataFrame:
    return pd.DataFrame(
        [
            (1, "目标差距", "DAU目标完成度81.25%", "决定增长问题优先级"),
            (2, "有效新增", "老带新拉新用户数", "把外部流量压力转成可控链路"),
            (3, "早期回访", "次7日内留存", "判断投放用户是否真正留下"),
            (4, "内容关系", "主页浏览与关注引导", "形成可验证的产品机制"),
            (5, "首月价值", "价值/激励成本2.18×", "比较渠道并约束持续投入"),
        ],
        columns=["step_order", "stage", "metric", "decision_use"],
    )


def _referral_versions() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "version_id": "baseline",
                "version_order": 1,
                "label": "初始活动版本",
                "invite_click_rate": 0.21,
                "share_success_rate": np.nan,
                "incentive_index": 100.0,
                "m1_value_cost": np.nan,
                "reported_efficiency_metric": 2.90,
                "efficiency_scope": (
                    "初期复盘未完整披露价值窗口和成本范围，"
                    "不与后续首月价值/激励成本倍数作同口径比较。"
                ),
                "decision": "使用投入空间扩大拉新",
                "diagnosis": (
                    "初期记录的投入效率指标约2.9；由于公开复盘未完整披露其口径，"
                    "这里不将它标记为首月价值/激励成本倍数。"
                ),
            },
            {
                "version_id": "complex_growth",
                "version_order": 2,
                "label": "激励与玩法升级",
                "invite_click_rate": 0.17,
                "share_success_rate": 0.95,
                "incentive_index": 160.0,
                "m1_value_cost": np.nan,
                "decision": "定位异常并二次改版",
                "diagnosis": "信息增多、重点分散、邀请按钮位于第二页，可能增加动作发现成本。",
            },
            {
                "version_id": "simplified_ui",
                "version_order": 3,
                "label": "首屏CTA简化版",
                "invite_click_rate": 0.235,
                "share_success_rate": np.nan,
                "incentive_index": 160.0,
                "m1_value_cost": 2.18,
                "decision": "在该版本上继续迭代与优化",
                "diagnosis": "简化信息层级并将邀请按钮放回首页。",
            },
        ]
    )


def _referral_funnel() -> pd.DataFrame:
    return pd.DataFrame(
        [
            (1, "exposure", "活动页面曝光", "触达规模", "未公开"),
            (2, "visit", "活动页访问", "邀请点击率分母", "未公开"),
            (3, "invite_click", "老用户点击邀请", "关键机制", "约21%→17%→23.5%"),
            (4, "share", "微信分享成功", "诊断环节", "约95%"),
            (5, "new_user_success", "新用户成功", "最终拉新结果", "未公开"),
        ],
        columns=[
            "step_order",
            "step_key",
            "step_label",
            "metric_role",
            "confirmed_value_display",
        ],
    ).assign(data_status="去标识化链路口径；仅展示已确认节点")


def _retention_trend() -> pd.DataFrame:
    return pd.DataFrame(
        [
            (1, "异常前", 0.48),
            (2, "异常后", 0.41),
        ],
        columns=["period_order", "period", "retention_d1_7_window"],
    ).assign(data_status="去标识化看板监测结果")


def _retention_segments() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "segment_order": 1,
                "segment": "手机",
                "retention_comparison": "对照基准",
                "share_finding": "建议在经济性稳定时提高投放占比",
            },
            {
                "segment_order": 2,
                "segment": "平板",
                "retention_comparison": "观察期内比手机低约10pp",
                "share_finding": "新增占比方向上升；缺少分期占比，无法准确量化结构贡献",
            },
        ]
    ).assign(dimension="设备类型", data_status="去标识化分层结论")


def _retention_decomposition() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "component": "整体留存变化",
                "observed_value_pp": -7.0,
                "bound_operator": "=",
                "bound_value_pp": 7.0,
                "display": "-7.0pp",
                "kind": "observed",
            },
            {
                "component": "设备结构定量贡献",
                "observed_value_pp": np.nan,
                "bound_operator": None,
                "bound_value_pp": np.nan,
                "display": "缺少分期设备占比，无法准确量化",
                "kind": "missing_input",
            },
            {
                "component": "仍需解释的变化",
                "observed_value_pp": np.nan,
                "bound_operator": None,
                "bound_value_pp": np.nan,
                "display": "需在补齐结构贡献后再计算",
                "kind": "missing_input",
            },
        ]
    ).assign(
        formula="结构贡献 = 各设备分层留存率 × 对应新增占比变化；当前缺少分期设备占比",
        scope="只确认方向性结构压力，不把缺失输入替换为估计值",
    )


def _retention_path() -> pd.DataFrame:
    rows = [
        (1, "download", "下载", "观察起点"),
        (2, "register", "注册登录", "无明显下滑"),
        (3, "home", "进入首页", "无明显下滑"),
        (4, "browse", "浏览点击", "无明显下滑"),
        (5, "consume", "浏览内容", "无明显下滑"),
        (6, "interact", "点赞/收藏/评论", "无明显下滑"),
        (7, "profile", "浏览博主主页", "无明显下滑"),
        (8, "follow", "关注博主", "无明显下滑"),
    ]
    return pd.DataFrame(
        rows, columns=["step_order", "step_key", "step_label", "comparison_result"]
    ).assign(data_status="去标识化路径诊断结论")


def _benchmark_features() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("关注博主", 2.5, "最大差异"),
            ("浏览博主主页", np.nan, "已纳入比较"),
            ("点赞/收藏/评论", np.nan, "已纳入比较"),
            ("直播", np.nan, "已纳入比较"),
            ("内容浏览", np.nan, "已纳入比较"),
        ],
        columns=["feature", "benchmark_ratio", "finding"],
    ).assign(evidence_type="behavioral_hypothesis_discovery")


def _experiments() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "experiment_id": "referral_ui_simplification",
                "case_id": "referral_growth",
                "title": "邀请页面简化实验",
                "strategy": "简化信息层级并将邀请CTA放回首屏",
                "control": "复杂活动页，邀请按钮位于第二页",
                "treatment": "简化活动页，邀请按钮位于首页",
                "primary_metric": "邀请点击率",
                "final_metric": "拉新用户数",
                "guardrail": "新用户首月价值/激励成本",
                "baseline_rate": 0.17,
                "treatment_rate": 0.235,
                "absolute_lift_pp": 6.5,
                "relative_lift_pct": 38.24,
                "sample_size": 7_000_000,
                "sample_display": "总样本约700万",
                "duration_days": 14,
                "mde_pp": 3.0,
                "alpha": 0.05,
                "power": 0.80,
                "approx_min_per_arm": 2629,
                "minimum_sample_source": (
                    "根据17%基线、+3pp MDE、α=0.05、Power=80%和1:1分流的演示复算；"
                    "不是公司内部样本量工具的导出结果。"
                ),
                "significance": "p < 0.05",
                "decision": "支持在该版本上继续迭代与优化",
            },
            {
                "experiment_id": "creator_follow_guidance",
                "case_id": "new_user_retention",
                "title": "博主主页与关注引导实验",
                "strategy": "内容退出页弹窗引导浏览博主主页并关注",
                "control": "不展示额外引导",
                "treatment": "展示主页浏览与关注引导",
                "primary_metric": "次7日内留存率",
                "final_metric": "次7日内留存率",
                "guardrail": np.nan,
                "baseline_rate": np.nan,
                "treatment_rate": np.nan,
                "absolute_lift_pp": np.nan,
                "relative_lift_pct": np.nan,
                "sample_size": 300_000,
                "sample_display": "总样本约30万",
                "duration_days": 14,
                "mde_pp": np.nan,
                "alpha": 0.05,
                "power": np.nan,
                "approx_min_per_arm": np.nan,
                "significance": "p < 0.05",
                "decision": "建议继续推进并持续优化",
            },
        ]
    )


def _metric_contracts() -> pd.DataFrame:
    rows = [
        (
            "acquired_user_count",
            "拉新用户数",
            "结果指标",
            "活动归因的新用户UV",
            "—",
            "活动归因窗口",
            "日×活动",
            "衡量增长结果",
            "不与净DAU增长直接等同",
        ),
        (
            "invite_click_rate",
            "邀请点击率",
            "机制指标",
            "点击邀请UV",
            "活动页访问UV",
            "当日",
            "日×版本",
            "定位并评价页面改版",
            "同一用户按日去重",
        ),
        (
            "share_success_rate",
            "分享成功率",
            "诊断指标",
            "微信分享成功UV",
            "点击邀请UV",
            "当日",
            "日×版本",
            "判断分享链路是否异常",
            "只解释邀请后的分享环节",
        ),
        (
            "d1_7_window_retention",
            "次7日内留存率",
            "结果指标",
            "新增后第1至7天至少回访一次的用户UV",
            "完整经历7天观察窗的新增用户UV",
            "D1—D7",
            "新增Cohort",
            "衡量新用户早期质量",
            "窗口留存，不等于精确第7日留存",
        ),
        (
            "follow_penetration",
            "关注行为渗透率",
            "探索指标",
            "发生关注行为的用户UV",
            "对应分析人群UV",
            "固定行为观察窗",
            "人群×功能",
            "筛选可干预的产品行为",
            "标杆差异用于提出假设，不直接证明因果",
        ),
        (
            "m1_value_cost",
            "首月价值/激励成本倍数",
            "决策护栏",
            "新用户首月活跃天数×日均时长×单位时长商业化价值",
            "归因范围内的激励成本",
            "首月",
            "活动版本",
            "与外投同窗口比较投入效率",
            "首月回收口径，不代表完整生命周期价值或净利润率",
        ),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "metric_key",
            "metric_name",
            "role",
            "numerator",
            "denominator",
            "window",
            "grain",
            "decision_use",
            "boundary",
        ],
    )


def _hypothesis_ledger() -> pd.DataFrame:
    return pd.DataFrame(
        [
            (
                "referral_growth",
                "邀请点击下降",
                "页面复杂且CTA后置提高行动成本",
                "邀请点击21%→17%；按钮位于第二页",
                "分享成功率约95%",
                "首屏简化版A/B",
                "17%→23.5%，p<0.05",
            ),
            (
                "new_user_retention",
                "整体留存下降",
                "设备构成变化形成结构压力",
                "平板占比上升；平板留存低约10pp",
                "缺少分期设备占比，无法准确量化结构贡献",
                "继续排查路径与产品行为",
                "保留为方向性解释",
            ),
            (
                "new_user_retention",
                "基础使用路径阻塞",
                "核心路径转化恶化导致用户流失",
                "—",
                "下载至关注主要环节无明显下滑",
                "降低该方向排查优先级",
                "现有证据不支持作为主要解释",
            ),
            (
                "new_user_retention",
                "缺少持续内容关系",
                "主页与关注引导可能促进再次访问",
                "标杆用户关注渗透率约2.5×",
                "标杆比较仅为相关性",
                "退出页引导A/B",
                "次7日内留存显著提升，p<0.05",
            ),
        ],
        columns=[
            "case_id",
            "problem",
            "hypothesis",
            "supporting_evidence",
            "counter_evidence",
            "validation",
            "decision",
        ],
    )


def _decision_records() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "decision_id": "referral_ui_release",
                "case_id": "referral_growth",
                "fact": "玩法升级后邀请点击率从约21%下降到17%，分享成功率约95%。",
                "interpretation": "邀请动作需优先排查；分享成功率约95%，降低分享完成环节作为主要断点的排查优先级。",
                "hypothesis": "信息层级复杂且CTA位于第二页，可能提高行动发现成本。",
                "action": "简化页面并将CTA放回首页，运行两周A/B实验。",
                "decision": (
                    "邀请点击率提升至23.5%，首月价值/激励成本倍数2.18"
                    "高于同口径外投1.90；支持在该版本上继续迭代与优化。"
                ),
                "limitation": "页面实验识别的是首屏简化组合策略；首月口径用于同期渠道比较。",
                "monitoring": "持续观察拉新用户数、邀请点击率、分享成功率、首月价值/激励成本倍数与新用户留存。",
            },
            {
                "decision_id": "retention_follow_v1",
                "case_id": "new_user_retention",
                "fact": "整体留存下降7pp；平板留存低约10pp且占比上升；主要路径转化率未见明显同步下降；标杆关注渗透率约2.5倍。",
                "interpretation": "设备结构形成方向性压力；现有证据不支持基础路径为主要解释，关注行为提供可干预线索。",
                "hypothesis": "主动引导浏览主页和关注可能帮助新用户形成持续内容关系。",
                "action": "内容退出页增加主页与关注引导，运行两周A/B实验。",
                "decision": (
                    "总样本约30万，随机实验支持次7日内留存率提升，p<0.05；"
                    "实验组、对照组绝对留存率未披露，建议继续推进并持续优化。"
                ),
                "limitation": "实验识别的是退出页引导组合策略，不把标杆相关性解释为单一行为因果。",
                "monitoring": "持续观察次7日内留存、引导曝光与使用、主页访问、关注及分层异质性。",
            },
        ]
    )


def portfolio_frames() -> dict[str, pd.DataFrame]:
    return {
        "portfolio_case_registry": _case_registry(),
        "portfolio_business_kpis": _business_kpis(),
        "portfolio_decision_loop": _decision_loop(),
        "portfolio_growth_quality_bridge": _growth_quality_bridge(),
        "portfolio_referral_versions": _referral_versions(),
        "portfolio_referral_funnel": _referral_funnel(),
        "portfolio_retention_trend": _retention_trend(),
        "portfolio_retention_segments": _retention_segments(),
        "portfolio_retention_decomposition": _retention_decomposition(),
        "portfolio_retention_path": _retention_path(),
        "portfolio_benchmark_features": _benchmark_features(),
        "portfolio_experiments": _experiments(),
        "portfolio_metric_contracts": _metric_contracts(),
        "portfolio_hypothesis_ledger": _hypothesis_ledger(),
        "portfolio_decisions": _decision_records(),
    }
