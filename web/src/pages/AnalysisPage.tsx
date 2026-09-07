import { ArrowRight, Check, ChevronRight, Play, RotateCcw } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { AnalysisChart } from '../analysis-chart'
import { Badge, CaseBadge, EvidencePanel, PageHeader, SectionHeader } from '../components'
import { displayText } from '../copy'
import type { AnalysisStep, CopilotData } from '../types'

const typeNames: Record<string, string> = {
  question: '问题', contract: '指标合同', analysis: '确定性分析', chart: '图表', negative_evidence: '负证据', hypothesis: '假设', experiment: '实验 / 价值', boundary: '结论边界',
  metric_definition: '指标合同', trend: '趋势定位', mix_shift: '结构分解', benchmark: '标杆分析', decision: '价值与决策',
}

function toneFor(type: string) {
  if (type === 'negative_evidence' || type === 'boundary') return 'warning' as const
  if (type === 'experiment') return 'positive' as const
  if (type === 'hypothesis') return 'purple' as const
  return 'info' as const
}

function StageCard({ step, active, index, onSelect }: { step: AnalysisStep; active: boolean; index: number; onSelect: () => void }) {
  return (
    <button type="button" className={`analysis-stage ${active ? 'active' : ''}`} onClick={onSelect} aria-current={active ? 'step' : undefined}>
      <span className="stage-number">{String(index + 1).padStart(2, '0')}</span>
      <span><small>{typeNames[step.type] ?? step.type}</small><strong>{displayText(step.title)}</strong></span>
      <ChevronRight size={17} aria-hidden="true" />
    </button>
  )
}

export function AnalysisPage({ data }: { data: CopilotData }) {
  const [params] = useSearchParams()
  const requested = params.get('question')
  const firstQuestion = data.questions.find((item) => item.analysis_id === requested) ?? data.questions[0]
  const [questionId, setQuestionId] = useState(firstQuestion?.id ?? '')
  const [revealed, setRevealed] = useState(1)
  const [activeStep, setActiveStep] = useState(0)
  const question = data.questions.find((item) => item.id === questionId) ?? data.questions[0]
  const thread = useMemo(() => data.analysis_threads.find((item) => item.id === question?.analysis_id), [data.analysis_threads, question])
  const steps = useMemo(() => {
    if (!thread || !question) return []
    const source = thread.steps.slice().sort((a, b) => a.order - b.order)
    const root: AnalysisStep = { id: `${thread.id}-root`, order: 0, type: 'question', title: '问题界定', summary: question.question, status: 'confirmed', evidence_ids: [], chart: null }
    return [root, ...source]
  }, [question, thread])

  const current = steps[activeStep]
  const advance = () => {
    if (revealed < steps.length) {
      setRevealed((value) => value + 1)
      setActiveStep(revealed)
    }
  }

  if (!question || !thread || !current) return null
  return (
    <>
      <PageHeader eyebrow="EVIDENCE-BASED ANALYSIS · 结构化诊断" title="基于证据约束的智能分析" description="围绕业务问题依次呈现指标定义、确定性计算、反向证据、可检验假设与结论边界；智能解释仅组织已验证证据，不生成业务数值。" />
      <section className="analysis-workbench content-section">
        <aside className="question-rail" aria-label="预设业务问题">
          <div className="rail-title"><span>选择业务问题</span><small>{data.questions.length} 个已配置问题</small></div>
          {data.questions.map((item, index) => (
            <button type="button" key={item.id} className={`question-button ${item.id === question.id ? 'active' : ''}`} onClick={() => { setQuestionId(item.id); setRevealed(1); setActiveStep(0) }} aria-pressed={item.id === question.id}>
              <span className="question-seq">Q{index + 1}</span>
              <strong>{displayText(item.question)}</strong>
              <div><CaseBadge caseId={item.case_id} />{item.tags.slice(0, 2).map((tag) => <span key={tag}>{tag}</span>)}</div>
            </button>
          ))}
          <div className="rail-boundary"><strong>结构化分析机制</strong><p>业务问题、指标口径与证据来源预先约束，确保分析结论可复核。</p></div>
        </aside>

        <div className="analysis-canvas">
          <div className="analysis-question-head">
            <div><span className="section-label">ROOT QUESTION</span><h2>{displayText(question.question)}</h2><p>{displayText(question.answer_summary)}</p></div>
            <Badge tone="positive"><Check size={13} /> 已有证据链</Badge>
          </div>
          <div className="analysis-progress" aria-label={`已展开 ${revealed} / ${steps.length} 步`}><span style={{ width: `${(revealed / steps.length) * 100}%` }} /></div>
          <div className="analysis-grid">
            <div className="analysis-stages">
              {steps.slice(0, revealed).map((step, index) => <StageCard key={step.id} step={step} index={index} active={index === activeStep} onSelect={() => setActiveStep(index)} />)}
              {revealed < steps.length && <div className="locked-stage">下一步尚未展开</div>}
            </div>
            <article className="analysis-detail" aria-live="polite">
              <div className="detail-kicker"><Badge tone={toneFor(current.type)}>{typeNames[current.type] ?? current.type}</Badge></div>
              <h3>{displayText(current.title)}</h3>
              <p className="detail-summary">{displayText(current.summary)}</p>
              {current.chart?.data_key && <AnalysisChart data={data} dataKey={current.chart.data_key} caseId={thread.case_id} />}
              <EvidencePanel evidenceIds={current.evidence_ids} evidence={data.evidence} />
              <div className="analysis-controls">
                <button type="button" className="secondary-button" onClick={() => { setRevealed(1); setActiveStep(0) }}><RotateCcw size={16} />重新播放</button>
                {revealed < steps.length ? <button type="button" className="primary-button" onClick={advance}><Play size={16} />展开下一步<ArrowRight size={16} /></button> : <span className="complete-note"><Check size={16} />分析链已完整展开</span>}
              </div>
            </article>
          </div>
        </div>
      </section>
      <section className="content-section compact-section"><SectionHeader label="ANALYSIS BOUNDARY" title="智能辅助分析边界" /><div className="boundary-grid"><div><strong>支持范围</strong><p>将已计算结果组织为假设、追问与决策摘要。</p></div><div><strong>使用限制</strong><p>不生成未披露实验数值，不改变指标口径，不忽略反向证据。</p></div><div><strong>必要留痕</strong><p>保留证据编号、计算来源、人工确认状态与后续验证计划。</p></div></div></section>
    </>
  )
}
