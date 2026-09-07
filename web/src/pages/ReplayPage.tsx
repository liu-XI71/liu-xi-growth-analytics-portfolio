import { ArrowRight, Check, Play, RotateCcw } from 'lucide-react'
import { useMemo, useState } from 'react'
import { AnalysisChart } from '../analysis-chart'
import { CaseBadge, EvidencePanel, PageHeader, SectionHeader } from '../components'
import { displayText } from '../copy'
import type { CopilotData } from '../types'

export function ReplayPage({ data }: { data: CopilotData }) {
  const [caseId, setCaseId] = useState(data.cases[0]?.id ?? '')
  const [cursor, setCursor] = useState(0)
  const growthCase = data.cases.find((item) => item.id === caseId) ?? data.cases[0]
  const steps = useMemo(() => {
    if (!growthCase) return []
    return growthCase.analysis_ids.flatMap((id) => (data.analysis_threads.find((thread) => thread.id === id)?.steps ?? []).slice().sort((a, b) => a.order - b.order))
  }, [data.analysis_threads, growthCase])
  const current = steps[cursor]
  if (!growthCase || !current) return null
  const metricName = (metricId: string) => displayText(data.metric_contracts.find((item) => item.metric_id === metricId)?.name ?? metricId)
  const changeCase = (next: string) => { setCaseId(next); setCursor(0) }
  return (
    <>
      <PageHeader eyebrow="CASE ANALYSIS · 从异常到决策" title="从业务异常到决策闭环" description="按业务目标、诊断拆解、候选假设、实验验证与价值评估逐步推进，形成可复核的完整分析链路。" />
      <section className="content-section">
        <div className="case-tabs" role="tablist" aria-label="选择案例">
          {data.cases.map((item) => <button type="button" role="tab" key={item.id} aria-selected={item.id === growthCase.id} className={item.id === growthCase.id ? 'active' : ''} onClick={() => changeCase(item.id)}><CaseBadge caseId={item.id} /><span><strong>{displayText(item.name)}</strong><small>{displayText(item.business_question)}</small></span></button>)}
        </div>
      </section>

      <section className="replay-stage content-section">
        <div className="replay-overview">
          <span className="section-label">BUSINESS CONTRACT</span>
          <h2>{displayText(growthCase.business_question)}</h2>
          <div className="contract-triad">
            <div><span>最终业务指标</span><strong>{metricName(growthCase.primary_metric)}</strong></div>
            <div><span>机制指标</span><strong>{metricName(growthCase.mechanism_metric)}</strong></div>
            <div><span>决策指标</span><strong>{metricName(growthCase.decision_metric)}</strong></div>
          </div>
          <p className="case-boundary">公开边界：{displayText(growthCase.data_boundary)}</p>
        </div>

        <div className="replay-timeline" aria-label={`案例链路进度 ${cursor + 1} / ${steps.length}`}>
          {steps.map((step, index) => (
            <button type="button" key={`${step.id}-${index}`} className={`${index === cursor ? 'active' : ''} ${index < cursor ? 'done' : ''}`} onClick={() => index <= cursor && setCursor(index)} disabled={index > cursor} aria-current={index === cursor ? 'step' : undefined}>
              <span>{index < cursor ? <Check size={14} /> : index + 1}</span><strong>{displayText(step.title)}</strong>
            </button>
          ))}
        </div>

        <article className="replay-card" aria-live="polite">
          <div className="replay-card-number">STEP {String(cursor + 1).padStart(2, '0')} / {String(steps.length).padStart(2, '0')}</div>
          <h3>{displayText(current.title)}</h3>
          <p>{displayText(current.summary)}</p>
          {current.chart?.data_key && <AnalysisChart data={data} dataKey={current.chart.data_key} caseId={growthCase.id} height={270} />}
          <EvidencePanel evidenceIds={current.evidence_ids} evidence={data.evidence} />
          <div className="replay-controls">
            <button type="button" className="secondary-button" onClick={() => setCursor(0)} disabled={cursor === 0}><RotateCcw size={16} />回到起点</button>
            {cursor < steps.length - 1 ? <button type="button" className="primary-button" onClick={() => setCursor((value) => value + 1)}><Play size={16} />推进下一步<ArrowRight size={16} /></button> : <div className="replay-finish"><Check size={17} />完整业务链已回放</div>}
          </div>
        </article>
      </section>

      <section className="content-section compact-section">
        <SectionHeader label="COMMON CAPABILITY" title="两个案例的共通分析能力" />
        <div className="common-capability"><div><strong>01</strong><h3>建立业务目标与指标层级</h3><p>区分最终指标、机制指标与护栏指标，避免以单一过程指标替代业务结果。</p></div><div><strong>02</strong><h3>使用反向证据收敛问题空间</h3><p>分享成功率保持高位、核心路径转化率未同步下降，可降低对应环节作为主要问题来源的优先级。</p></div><div><strong>03</strong><h3>由观察性关联形成可检验假设</h3><p>相关性用于形成候选假设，策略决策进一步结合随机实验、业务显著性与价值护栏。</p></div></div>
      </section>
    </>
  )
}
