import { ArrowRight, BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'
import { commonMethod } from '../case-model'
import { PageHeader, SectionHeader } from '../components'

const experimentSteps = [
  ['确定目标策略与目的', '将策略定义为“简化邀请界面并前置入口”，目的是改善老用户点击邀请，最终支持拉新规模。策略描述与指标作用路径一致。'],
  ['确定核心、护栏及相关指标', '核心是邀请点击率，价值护栏是新用户首月价值/激励成本；裂变率、人均邀请、新用户频次和留存用于理解后续链路。'],
  ['预设样本量与周期', '基线 17%、MDE +3 个百分点、双侧 α = 0.05、Power = 80%。按每日可分流样本估算周期，并覆盖完整业务周与新奇效应观察；项目实际运行两周。'],
  ['按实验单位稳定分流', '用户 ID 加固定实验盐值后 Hash 分桶，0–49 为实验组、50–99 为对照组；1:1 是预设比例，不保证实际人数绝对相等。'],
  ['A/A 与数据质量检查', '检查埋点、指标口径、SRM 与关键人群分布。A/A 偶发 p < 0.05 并不自动证明分流错误，应先定位原因，避免不断重分流直到显著性消失。'],
  ['按计划执行 A/B', '在预设周期与样本量达到后统一评价，过程中监控数据质量与护栏，不因反复查看 p 值而提前停止。对干扰、新奇效应和观察窗口作预案。'],
  ['统计结果与业务决策', '分别报告效果量与统计显著性，再结合业务目标、价值护栏和最终新增质量判断。双侧检验条件是 |Z| > 临界值；显著不等于值得扩大投入。'],
]

export function MethodPage() {
  return <>
    <PageHeader eyebrow="REUSABLE METHODOLOGY" title="业务问题 → 指标口径 → 实验决策" description="将两个案例中重复使用的判断方式沉淀为分析标准。以下是可复用方法，不将检查项或处理预案表述为实习项目已经全部完成的记录。" />
    <section className="method-strip content-section"><SectionHeader label="FRAMEWORK" title="先回答业务问题，再选择分析方法" /><ol className="case-method-flow">{commonMethod.map((item, index) => <li key={item.title}><span>0{index + 1}</span><strong>{item.title}</strong><p>{item.description}</p></li>)}</ol></section>
    <section className="content-section"><SectionHeader label="METRIC SYSTEM" title="一项指标，需要同时明确六件事" description="指标名称相同，并不保证计算与解释相同。" /><div className="method-contract-grid">{[['业务角色', '结果、机制、诊断或护栏；不能用点击替代最终新增。'], ['分子与分母', '同一人群范围内统计，明确去重与资格条件。'], ['统计粒度', '按用户、事件或订单统计，不混用 PV 与 UV。'], ['观察窗口', 'D1–D7 窗口留存区别于精确 D7；首月价值区别于生命周期。'], ['对比基准', '监控前后、实验组间、外部投放属于不同类型的比较。'], ['决策用途', '该指标能支持什么行动，是否仍需实验或价值验证。']].map(([title, text]) => <article className="case-panel" key={title}><h3>{title}</h3><p>{text}</p></article>)}</div><Link className="text-link content-section" to="/evidence">查看两个案例的指标口径 <ArrowRight size={16} /></Link></section>
    <section className="content-section"><SectionHeader label="DIAGNOSIS" title="三种分析方法，各自回答一个问题" /><div className="diagnosis-cards">{[['分层分析', '是谁发生了变化？', '整体率 = 各层占比 × 各层表现的加权和。分开观察结构与组内变化；设备差距存在时，还需要分期占比才能量化结构贡献。'], ['路径漏斗', '用户在哪一步受阻？', '比较同口径、同资格人群的转化；稳定环节降低调查优先级，不等于绝对排除所有体验问题。存在分支时保留真实产品路径。'], ['标杆分析', '哪些行为值得干预验证？', '高频高时用户提供行为线索，但其先验意愿与机会可能不同。回顾性分层用于探索，不能把结果期特征当作实验前特征。']].map(([title, question, text]) => <article className="case-panel" key={title}><span className="section-label">{title}</span><h3>{question}</h3><p>{text}</p></article>)}</div></section>
    <section className="content-section"><SectionHeader label="EXPERIMENT SOP" title="七步实验流程" description="设计、分流、检查、执行与决策分开记录。" action={<Link className="text-link" to="/experiment">打开样本量与结果试算 <ArrowRight size={16} /></Link>} /><ol className="experiment-sop">{experimentSteps.map(([title, text], index) => <li key={title}><span>0{index + 1}</span><div><h3>{title}</h3><p>{text}</p></div></li>)}</ol></section>
    <section className="content-section"><SectionHeader label="PRACTICAL CONDITIONS" title="四项容易影响结论的条件" /><div className="method-contract-grid conditions">{[['留存成熟窗口', '实验招募期与观察期分开管理。新用户必须走完 D1–D7 才进入该口径分母；首月价值另需完整首月观察。'], ['人群组成与辛普森现象', 'A/A 不能自动解决辛普森悖论。检查渠道、设备、城市分布，按预设维度分层，并区分总体效果与人群异质性。'], ['网络干扰', '老带新可能存在用户间影响。若采用城市或社群簇随机，样本量与标准误需对应簇级设计；不能只换分组方式而沿用独立用户计算。'], ['非随机数据', '无法随机分流时，可在满足假设的前提下考虑 DID 或 PSM；它们不是 A/A 异常的自动修复，也不能保证消除未观测混杂。']].map(([title, text]) => <article className="case-panel" key={title}><h3>{title}</h3><p>{text}</p></article>)}</div></section>
    <section className="content-section"><SectionHeader label="OUTPUT" title="把一次分析，沉淀为下一次工作的输入" /><div className="tool-links"><Link to="/analysis"><BookOpen size={22} /><div><strong>分析链路</strong><p>按问题、口径、证据、假设和行动逐步展开。</p></div><ArrowRight size={18} /></Link><Link to="/weekly"><BookOpen size={22} /><div><strong>案例周报</strong><p>将阶段指标与建议整理为可下载摘要。</p></div><ArrowRight size={18} /></Link></div></section>
  </>
}
