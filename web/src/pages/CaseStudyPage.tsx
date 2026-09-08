import { ArrowRight, CheckCircle2, Download, Target } from 'lucide-react'
import { Link } from 'react-router-dom'
import { caseReadout, numberLabel, rateLabel, sampleLabel, type CaseKey } from '../case-model'
import { EvidencePanel, PageHeader, SectionHeader } from '../components'
import type { CopilotData } from '../types'

function Comparison({ title, rows, note }: { title: string; rows: { label: string; value: number | null; color?: string }[]; note: string }) {
  return <figure className="case-comparison"><figcaption>{title}</figcaption><div className="comparison-scale"><span>0%</span><span>50%</span><span>100%</span></div>{rows.map((row) => <div className="comparison-row" key={row.label}><div><span>{row.label}</span><strong>{rateLabel(row.value)}</strong></div><div className="comparison-track">{row.value !== null && <span style={{ width: `${Math.max(0, Math.min(100, row.value * 100))}%`, background: row.color ?? 'var(--blue)' }} />}</div></div>)}<p>{note}</p></figure>
}

function CaseSection({ id, number, title, description, children }: { id: string; number: string; title: string; description: string; children: React.ReactNode }) {
  return <section id={id} className="case-section content-section"><SectionHeader label={`STEP ${number}`} title={title} description={description} />{children}</section>
}

export function CaseStudyPage({ data, caseKey }: { data: CopilotData; caseKey: CaseKey }) {
  const growth = caseKey === 'referral'
  const facts = caseReadout(data, caseKey)
  const experimentId = growth ? 'ev_referral_experiment' : 'ev_retention_experiment'
  const prefix = `case-${caseKey}`
  const lift = facts.control !== null && facts.treatment !== null ? (facts.treatment - facts.control) * 100 : null
  const sections = ['业务目标', '指标体系', '诊断与策略', '实验评估', '决策与沉淀']
  const downloadBrief = () => {
    const title = growth ? '老带新增长案例' : '新用户留存案例'
    const metrics = growth
      ? `邀请点击率：对照组 ${rateLabel(facts.control)}，实验组 ${rateLabel(facts.treatment)}，差异 ${numberLabel(lift, 1)} 个百分点。首月价值/激励成本倍数 ${numberLabel(facts.valueRatio)}，同口径外投 ${numberLabel(facts.externalRatio)}。`
      : `次7日内留存监控变化：${rateLabel(facts.before)} → ${rateLabel(facts.after)}。标杆/非标杆关注渗透率比 ${numberLabel(facts.benchmarkRatio)}。实验支持留存提升，p < 0.05；组间绝对留存率未公开，不报告绝对效果量。`
    const summary = growth
      ? '外部拉新供给承压 → 监控邀请点击下降 → 产品与用研反馈页面信息复杂、邀请入口后置 → 简化界面并前置按钮 → 随机实验评估 → 首月价值约束下持续迭代。'
      : '投放新增留存下滑 → 按渠道、设备与用户维度分层 → 识别设备结构压力 → 核心路径转化未同步下降 → 高频高时标杆用户关注渗透更高 → 退出页主页与关注引导实验 → 推广策略并持续优化。'
    const content = `# 刘希｜增长与实验 · ${title}\n\n## 个人参与\n\n在 mentor 带领下参与指标梳理、看板监测、诊断分析、策略反馈与实验评估。\n\n## 分析链路\n\n${summary}\n\n## 核心信息\n\n${metrics}\n\n实验周期 ${numberLabel(facts.days)} 天，总样本约 ${sampleLabel(facts.sample)}。\n\n## 方法沉淀\n\n业务目标 → 指标口径 → 诊断证据 → 策略验证 → 价值约束。\n\n## 数据说明\n\n${data.meta.data_boundary}\n${growth ? '实际组内人数、A/A、SRM、分层均衡及精确统计量未公开。首月比较不等同于完整生命周期或增量利润。' : '缺少分期设备占比，不量化真实结构贡献；标杆差异是相关性，实验评估的是完整引导策略。'}\n`
    const url = URL.createObjectURL(new Blob([content], { type: 'text/markdown;charset=utf-8' }))
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `Liu-Xi-${caseKey}-case-brief.md`
    anchor.click()
    window.setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  return <>
    <PageHeader eyebrow={growth ? 'CASE 01 · 字节跳动 · 红果业务线 · 用户增长' : 'CASE 02 · 小红书 · 新用户留存'} title={growth ? '老带新：定位断点，验证增长策略' : '新用户留存：从结构诊断到产品引导'} description={growth ? '在扩大拉新规模的目标下，将邀请链路诊断、页面简化实验与首月价值评估串成完整决策过程。' : '围绕次 7 日内留存下滑，依次拆解用户结构、产品路径和关键行为，再以实验评估引导策略。'} aside={<button className="secondary-button" type="button" onClick={downloadBrief}><Download size={16} />下载案例摘要</button>} />
    <nav className="case-section-nav" aria-label="案例章节">{sections.map((label, index) => <button key={label} type="button" onClick={() => document.getElementById(`${prefix}-${index}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })}><span>0{index + 1}</span>{label}</button>)}</nav>

    <CaseSection id={`${prefix}-0`} number="01" title="业务目标与个人参与" description="先确认业务要解决的问题，再选择分析路径。">
      <div className="case-two-columns"><article className="case-panel"><span className="section-label">BUSINESS CONTEXT</span><h3>{growth ? '外部拉新流量下滑，寻找内部增长来源' : '投放获得新用户，必须进一步形成回访'}</h3><p>{growth ? '部门通过老用户邀请新用户的活动扩大拉新。分析不能只追求单次投入回报倍数，还要判断激励与产品设计是否支持新增规模增长。' : '看板监测到新增用户的次 7 日内留存下滑。新增用户来自渠道投放，如果用户进入产品后不能持续回访，获客投入难以形成稳定用户价值。'}</p><div className="case-action"><Target size={18} /><strong>{growth ? '目标：提升拉新用户数，兼顾新增价值与激励成本。' : '目标：提升新用户的次 7 日内留存率。'}</strong></div></article><article className="case-panel"><span className="section-label">MY CONTRIBUTION</span><h3>在 mentor 带领下参与分析与评估</h3><ul className="professional-list">{(growth ? ['梳理拉新指标链路，搭建和监控活动看板。', '发现邀请点击下滑，定位关键环节并反馈产品与用研。', '参与页面改版实验设计、结果评估与首月价值测算。'] : ['按渠道、设备及用户维度拆解新增留存变化。', '梳理主要产品路径，比较各环节转化表现。', '进行高频高时标杆用户分析，参与引导策略实验评估。']).map((item) => <li key={item}>{item}</li>)}</ul><p className="case-caption">作品中的前后端与交互工具为个人方法沉淀，不代表实习期间交付的企业生产系统。</p></article></div>
    </CaseSection>

    <CaseSection id={`${prefix}-1`} number="02" title="指标体系：结果、机制与约束" description="同一业务链路中，不同指标承担不同决策职责。">
      <div className="metric-levels"><article><span>最终业务指标</span><h3>{growth ? '拉新用户数' : '次 7 日内留存率'}</h3><p>{growth ? '观察活动带来的新增用户规模，不能用邀请点击人数代替。' : '新增用户在 D1–D7 内至少回访一次的用户数 / 已完成观察窗口的新增用户数。'}</p></article><article><span>策略作用指标</span><h3>{growth ? '邀请点击率' : '主页浏览与关注渗透'}</h3><p>{growth ? '活动页访问老用户中，点击邀请的去重用户占比；页面改版首先影响这一动作。' : '比较使用相应功能的用户占比，判断引导策略是否改变关键行为。'}</p></article><article><span>{growth ? '价值护栏' : '观察窗口'}</span><h3>{growth ? '首月价值 / 激励成本' : '新增后 D1–D7'}</h3><p>{growth ? '以相同观察期、成本范围和归因规则，与外部获客方式比较。' : '跨完整一周观察回访，减少只看次日时受入组星期影响的局限；不等于精确 D7 留存。'}</p></article></div>
      <div className="case-panel content-section"><h3>{growth ? '活动链路与关联指标' : '用户路径与留存口径'}</h3><ol className="business-path">{(growth ? ['活动页曝光 / 访问', '点击邀请', '成功分享', '新用户访问与转化', '新用户留存与价值'] : ['下载', '注册登录', '首页', '内容浏览', '互动 / 博主主页 / 关注', 'D1–D7 回访']).map((item) => <li key={item}>{item}</li>)}</ol><p>{growth ? '配合监控裂变率、人均邀请用户数、新用户访问频次与留存。不同转化率必须使用对应上游人群作分母，不能将不同阶段的率直接相乘外推真实拉新。' : '产品路径用来识别使用环节的变化；留存以新增用户 cohort 为分母，回访按用户去重。浏览、互动与主页访问存在分支，不能把所有动作强行当作人人必经的单向漏斗。'}</p><Link className="text-link" to="/evidence">展开指标定义与统计粒度 <ArrowRight size={15} /></Link></div>
    </CaseSection>

    <CaseSection id={`${prefix}-2`} number="03" title="诊断与策略：每一步分析服务一个判断" description={growth ? '将异常定位到邀请动作，再结合产品反馈形成页面改版策略。' : '先诊断人群变化，再排查路径问题，最后寻找可干预的产品行为。'}>
      <div className="case-two-columns"><Comparison title={growth ? '邀请点击率：策略升级前后' : '次 7 日内留存：异常前后'} rows={[{ label: growth ? '升级前' : '异常前', value: facts.before }, { label: growth ? '复杂升级后' : '异常后', value: facts.after, color: '#d08b3d' }]} note="图中为监控阶段对比，不是随机实验组间效果。" /><article className="case-panel"><span className="section-label">DIAGNOSTIC QUESTION</span><h3>{growth ? '为什么增加激励，点击反而下降？' : '是用户结构变了，还是使用体验变了？'}</h3><p>{growth ? '最初激励较保守。为支持新增规模，团队提升激励并增加留存成功玩法；策略升级后邀请点击由约 21% 降到 17%。分享成功率约 95%，分析优先集中在邀请入口及页面表达。' : `整体留存从 ${rateLabel(facts.before)} 降到 ${rateLabel(facts.after)}。分层发现平板留存约比手机低 ${numberLabel(facts.deviceGap)} 个百分点，且平板新增占比上升，提示人群结构对整体留存形成压力。`}</p><EvidencePanel evidenceIds={growth ? ['ev_referral_version_trend', 'ev_referral_share_negative', 'ev_referral_incentive_reconstruction'] : ['ev_retention_trend', 'ev_retention_device_structure']} evidence={data.evidence} /></article></div>
      <div className="diagnosis-cards content-section">{(growth ? [
        ['01 · 看板定位', '关键动作发生变化', '邀请点击率下滑，分享成功率保持高位。先降低分享完成环节作为主要断点的调查优先级，继续关注动作发现成本。'],
        ['02 · 产品反馈', '信息复杂与入口后置', '反馈产品与用研后，发现改版介绍内容增多、重点不集中，邀请按钮位于第二页，老用户难以快速找到核心动作。'],
        ['03 · 策略形成', '简化页面，邀请按钮前置', '对页面信息层级做简化，将邀请入口放到首页清晰位置；用随机实验评估完整改版策略，而非仅凭上线前后对比定论。'],
      ] : [
        ['01 · 用户分层', '结构压力与投放建议', '按渠道、设备类型、品牌、系统、城市等级、地域及用户画像分层。在投入产出要求不变的前提下，建议提高手机投放占比；该建议短期内未落地。'],
        ['02 · 路径排查', '主要转化环节未同步恶化', '梳理下载、注册登录、首页、内容浏览、互动、主页访问与关注等环节。转化未见明显下滑，降低普遍上手障碍作为主要原因的优先级。'],
        ['03 · 标杆分析', '从高频高时用户发现线索', `依据首月活跃天数和日活跃时长分层，将高频高时用户作为标杆；比较直播、视频、点赞、评论、收藏、主页浏览与关注等功能渗透率，关注差异最明显，约为 ${numberLabel(facts.benchmarkRatio)} 倍。`],
      ]).map(([label, title, text]) => <article className="case-panel" key={label}><span className="section-label">{label}</span><h3>{title}</h3><p>{text}</p></article>)}</div>
      {!growth && <div className="hypothesis-bridge"><div><span>观察性关联</span><strong>高频高时用户更常关注</strong></div><ArrowRight size={22} /><div><span>可检验策略</span><strong>退出页引导主页浏览与关注</strong></div><ArrowRight size={22} /><div><span>随机实验</span><strong>比较新用户 D1–D7 回访</strong></div></div>}
      <details className="case-disclosure content-section"><summary>诊断解释与适用范围</summary><p>{growth ? '分享成功率高，不等于已证明所有分享问题不存在。邀请入口改版同时调整页面信息与按钮位置，实验结论对应完整策略，不能分别归因给某个单一元素。激励使用指数化表达，不公开活动绝对定价。' : '设备差距与占比上升支持结构压力方向；缺少分期占比，不能将整体 7 个百分点降幅全部归因于设备结构。标杆分层是回顾性分析，先验意愿与使用机会均可造成行为差异，不直接证明关注行为带来留存提升。'}</p></details>
    </CaseSection>

    <CaseSection id={`${prefix}-3`} number="04" title="实验评估：将产品策略转化为可验证结果" description="以随机分流控制组间差异，分别判断统计结果和业务价值。">
      <div className="experiment-case-plan"><article><span>对照组</span><h3>{growth ? '原活动界面' : '不增加退出页引导'}</h3><p>{growth ? '保留原有页面信息与邀请入口。' : '沿用原有浏览内容后的退出体验。'}</p></article><article><span>实验组</span><h3>{growth ? '简化信息，邀请按钮前置' : '增加主页浏览与关注引导'}</h3><p>{growth ? '首页突出邀请动作，降低入口发现成本。' : '浏览内容后退出时，引导访问博主主页并关注。'}</p></article><article><span>评估设计</span><h3>{numberLabel(facts.days)} 天 · 约 {sampleLabel(facts.sample)}</h3><p>{growth ? '核心指标为邀请点击率；最终业务结果仍是拉新用户数。' : '核心指标为次 7 日内留存率，同时观察相关功能使用。'}</p></article></div>
      <div className="case-two-columns content-section">{growth ? <Comparison title="邀请点击率：随机实验组间对比" rows={[{ label: '对照组', value: facts.control }, { label: '实验组', value: facts.treatment, color: '#6858dc' }]} note={`组间绝对提升 ${numberLabel(lift, 1)} 个百分点；p < 0.05。此图与上方监控变化分开表达。`} /> : <article className="case-result-panel"><span>实验结果</span><CheckCircle2 size={38} /><h3>次 7 日内留存显著提升</h3><strong>p &lt; 0.05</strong><p>项目评估支持退出页主页与关注引导策略。组间绝对留存率未公开，因此不展示效果量柱状图，也不使用监控前后值替代实验结果。</p></article>}<article className="case-panel"><span className="section-label">DECISION READOUT</span><h3>{growth ? '从点击改善，继续观察最终新增' : '从相关线索，推进到策略效果评估'}</h3><p>{growth ? '设计基于历史点击率 17%，MDE 为提升 3 个百分点，α = 0.05、Power = 80%；使用用户 ID 稳定 Hash 分桶，按 1:1 分流。实验运行两周后统一评估，避免因反复查看 p 值而提前停止。' : '标杆分析用于提出假设；随机实验评估的是“增加退出页引导”的整体效果，不等同于孤立估计“关注行为本身”的因果效应。'} </p><Link className="text-link" to="/experiment">使用实验设计与结果试算 <ArrowRight size={15} /></Link><EvidencePanel evidenceIds={[experimentId]} evidence={data.evidence} /></article></div>
      <details className="case-disclosure content-section"><summary>实验口径与完整观察</summary><p>{growth ? '总样本与 1:1 分流为已公开设计，实际组内人数、A/A、SRM、分层均衡结果和精确统计量未公开；交互试算不作为原始实验记录。' : '留存比较须使用已完成 D1–D7 观察的入组用户；招募周期与观察成熟时间需分开管理。本案例只展示已公开的两周周期、总样本和显著性结论，不补写原始分组计数。'} 网络干扰、新奇效应与分层分析的处理原则见“指标与实验方法”。</p></details>
    </CaseSection>

    <CaseSection id={`${prefix}-4`} number="05" title="决策与沉淀：让结果进入下一轮业务行动" description={growth ? '同时判断是否改善关键动作，以及新增价值是否支持继续投入。' : '将可落地产品策略与中期投放建议分开推进。'}>
      {growth && <div className="value-comparison"><div><span>当前策略 · 首月倍数</span><strong>{numberLabel(facts.valueRatio)}</strong></div><div><span>同口径外投 · 首月倍数</span><strong>{numberLabel(facts.externalRatio)}</strong></div><p>首月价值估算 = 活跃天数 × 日活跃时长 × 单位时长商业化价值；再除以归因范围内激励成本。首月窗口支持快速迭代，不代表完整生命周期价值或增量利润。</p></div>}
      <div className="case-action result"><CheckCircle2 size={23} /><div><strong>{growth ? '支持在首屏简化版本上持续迭代' : '推进主页与关注引导策略，并持续优化'}</strong><p>{growth ? '邀请点击实验支持关键动作改善；首月价值/激励成本高于同口径外投基准。后续仍监控有效拉新规模、新增留存与成本变化。' : '产品引导实验支持留存改善；设备投放优化作为独立方向继续推进。后续持续关注人群结构、核心行为与成熟 cohort 留存。'}</p></div></div>
      <div className="case-panel content-section"><h3>可复用经验</h3><p>{growth ? '以最终业务目标选择机制指标；通过漏斗定位动作断点；将产品反馈组织成可实验的改版策略；以同口径价值比较支持投入决策。' : '将“留存为什么下滑”和“产品如何提升留存”分开分析；先拆结构与路径，再用标杆形成假设，最后通过随机实验验证可干预策略。'}</p><div className="case-bottom-links"><Link className="text-link" to="/methods">查看完整方法 <ArrowRight size={15} /></Link><Link className="text-link" to={growth ? '/cases/retention' : '/cases/referral'}>查看另一业务案例 <ArrowRight size={15} /></Link><Link className="text-link" to="/weekly">查看案例周报 <ArrowRight size={15} /></Link></div></div>
    </CaseSection>
  </>
}
