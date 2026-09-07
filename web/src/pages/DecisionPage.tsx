import { ArrowRight, CircleAlert, Lightbulb, Minus, ShieldCheck, Target, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge, CaseBadge, EvidencePanel, PageHeader, SectionHeader } from '../components'
import { displayText } from '../copy'
import type { CopilotData, DecisionItem, LoadedCopilot } from '../types'

function detail(decision: DecisionItem, key: 'anomaly' | 'business_impact' | 'negative_evidence' | 'evidence_level' | 'residual' | 'action') {
  if (decision[key]) return decision[key]
  return key === 'action' ? decision.recommendation : '分析包未提供该字段'
}

function gateLabel(decision: DecisionItem) {
  if (typeof decision.gate_status === 'string') return decision.gate_status
  const gates = decision.gate_status
  if (gates.statistical && gates.business && gates.guardrail) return '统计、业务与护栏条件通过'
  if (gates.statistical) return '统计检验通过，部分决策条件未披露'
  return '证据待继续回收'
}

function decisionQueue(data: CopilotData) {
  return data.decisions.slice(0, 5)
}

export function DecisionPage({ data, source }: { data: CopilotData; source: LoadedCopilot['source'] }) {
  const decisions = decisionQueue(data)
  const linkedDecisions = decisions.filter((item) => item.evidence_ids.length).length
  return (
    <>
      <PageHeader
        eyebrow="LIU XI · GROWTH ANALYTICS PORTFOLIO"
        title="从增长异常到可执行决策"
        description="围绕老带新获客与新用户留存，呈现指标体系、结构化诊断、A/B 实验与价值评估的完整决策闭环。"
        aside={<div className="freshness-card"><span className={`source-dot ${source}`} /><div><strong>{source === 'api' ? '本地接口链路已连接' : '公开快照已同步'}</strong><small>{source === 'api' ? '来源：FastAPI / 事实合同' : '来源：发布时生成的分析包'}</small></div></div>}
      />

      <section className="kpi-ribbon" aria-label="工作台摘要">
        <div><span>业务案例</span><strong>{data.cases.length}</strong><small>增长 × 留存</small></div>
        <div><span>预设业务问题</span><strong>{data.questions.length}</strong><small>都有分析链路</small></div>
        <div><span>决策证据关联</span><strong>{linkedDecisions}/{decisions.length}</strong><small>每项均可追溯</small></div>
        <div><span>分析闭环</span><strong>6 环节</strong><small>异常至持续监测</small></div>
      </section>

      <section className="content-section">
        <SectionHeader label="DECISION PRIORITIES" title="增长决策优先级" description="每项决策统一呈现业务异常、影响范围、反向证据、证据等级、剩余不确定性与建议行动。" action={<Link className="text-link" to="/analysis">进入智能分析 <ArrowRight size={16} /></Link>} />
        <div className="decision-grid">
          {decisions.map((decision, index) => (
            <article className="decision-card" key={decision.id}>
              <div className="decision-card-top">
                <div className="decision-index">0{index + 1}</div>
                <div className="decision-tags"><CaseBadge caseId={decision.case_id} /><Badge tone={gateLabel(decision).includes('通过') || decision.status.includes('support') || decision.status.includes('ship') ? 'positive' : 'warning'}>{gateLabel(decision)}</Badge></div>
              </div>
              <h3>{displayText(decision.title)}</h3>
              <p className="decision-summary">{displayText(decision.summary)}</p>
              <dl className="decision-facts">
                <div><dt><CircleAlert size={15} />异常</dt><dd>{displayText(detail(decision, 'anomaly'))}</dd></div>
                <div><dt><TrendingUp size={15} />业务影响</dt><dd>{displayText(detail(decision, 'business_impact'))}</dd></div>
                <div><dt><Minus size={15} />负证据</dt><dd>{displayText(detail(decision, 'negative_evidence'))}</dd></div>
                <div><dt><ShieldCheck size={15} />证据等级</dt><dd>{displayText(detail(decision, 'evidence_level'))}</dd></div>
                <div className="residual"><dt><Lightbulb size={15} />未决问题</dt><dd>{displayText(detail(decision, 'residual'))}</dd></div>
              </dl>
              <div className="decision-action"><Target size={18} aria-hidden="true" /><div><span>建议行动</span><strong>{displayText(detail(decision, 'action'))}</strong></div></div>
              <EvidencePanel compact evidenceIds={decision.evidence_ids} evidence={data.evidence} />
              <Link className="card-link" to={`/analysis?question=${encodeURIComponent(decision.analysis_id)}`}>查看分析链路 <ArrowRight size={15} /></Link>
            </article>
          ))}
        </div>
      </section>

      <section className="method-strip content-section">
        <SectionHeader label="REUSABLE METHOD" title="两个增长场景，一套可复用决策框架" description="通过指标口径、诊断拆解、因果验证与价值约束，在证据范围内形成可执行结论。" />
        <ol className="method-flow">
          {['看板发现异常', '指标合同统一口径', '分层 / 漏斗定位', '反向证据收敛范围', '实验识别策略效果', '价值护栏与复盘'].map((item, index) => <li key={item}><span>{index + 1}</span><strong>{item}</strong></li>)}
        </ol>
        <div className="method-outcome"><strong>方法输出</strong><span>形成可复核的决策闭环：证据 → 边界 → 行动 → 持续监测。</span></div>
      </section>
    </>
  )
}
