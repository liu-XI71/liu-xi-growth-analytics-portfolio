import { ArrowDownRight, ArrowRight, CheckCircle2, Download, Sparkles } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Badge, PageHeader, SectionHeader, SourceBadge } from '../components'
import { displayText } from '../copy'
import type { CopilotData, ReportEntry, ReportKpi, SourceType, WeeklyReport } from '../types'

function asEntry(value: ReportEntry | string, defaultSource: SourceType = 'system'): Required<Pick<ReportEntry, 'text'>> & ReportEntry {
  if (typeof value === 'string') return { text: displayText(value), source_type: defaultSource }
  return { ...value, text: displayText(value.text ?? value.statement ?? value.title ?? '—') }
}

function asEntries(value: WeeklyReport['experiment_status'], defaultSource: SourceType = 'system') {
  if (Array.isArray(value)) return value.map((item) => asEntry(item, defaultSource))
  return [asEntry(value, defaultSource)]
}

function asKpi(value: ReportKpi | string): ReportKpi {
  if (typeof value === 'string') return { name: displayText(value), value: '—', source_type: 'system' }
  return value
}

function kpiName(kpi: ReportKpi, data: CopilotData) {
  const metricId = kpi.metric_id ?? kpi.metric
  return displayText(kpi.name ?? kpi.label ?? (metricId ? data.metric_contracts.find((item) => item.metric_id === metricId)?.name : '') ?? metricId ?? '指标')
}

function kpiValue(kpi: ReportKpi) {
  return displayText(kpi.value ?? kpi.display ?? '—')
}

function sourceLabel(source?: SourceType) {
  const value = String(source ?? 'human').toLowerCase()
  if (value.includes('ai')) return '智能解释'
  if (value.includes('system') || value.includes('系统') || value.includes('calculation') || value.includes('derived') || value.includes('method')) return '系统计算'
  return '人工确认'
}

function previousReport(report: WeeklyReport): WeeklyReport | null {
  if (!report.previous_snapshot) return null
  return { ...report, ...report.previous_snapshot, id: `${report.id}-previous` }
}

function reportMarkdown(report: WeeklyReport, data: CopilotData) {
  const section = (title: string, rows: Array<ReportEntry | string>, source: SourceType) => `## ${title}\n\n${rows.map((row) => { const item = asEntry(row, source); return `- [${sourceLabel(item.source_type)}] ${item.text}` }).join('\n') || '- 暂无'}\n`
  const kpis = report.kpis.map((row) => { const item = asKpi(row); return `| ${kpiName(item, data)} | ${kpiValue(item)} | ${displayText(item.change ?? '—')} | ${displayText(item.status ?? '—')} | ${sourceLabel(item.source_type)} |` }).join('\n')
  return `# ${displayText(report.title)} · ${report.period}\n\n> ${displayText(report.headline)}\n\n> 说明：${displayText(report.data_boundary ?? '固定规则的案例阶段回放，不是公司实时周报。')}\n\n## 核心指标\n\n| 指标 | 当前值 | 变化 | 状态 | 来源 |\n|---|---:|---:|---|---|\n${kpis}\n\n${section('异常', report.anomalies, 'system')}\n${section('负证据', report.negative_evidence, 'system')}\n${section('候选假设', report.hypotheses, 'human')}\n${section('实验状态', asEntries(report.experiment_status), 'system')}\n${section('行动建议', report.recommendations, 'human')}\n${section('结论边界', report.limitations, 'human')}\n## 证据索引\n\n${report.evidence_ids.map((id) => `- ${id}`).join('\n')}\n`
}

export function WeeklyReportPage({ data }: { data: CopilotData }) {
  const caseOptions = useMemo(() => Array.from(new Map(data.weekly_reports.map((item) => [item.case_id, item])).values()), [data.weekly_reports])
  const [caseId, setCaseId] = useState(caseOptions[0]?.case_id ?? '')
  const [week, setWeek] = useState<'current' | 'prior'>('current')
  const current = data.weekly_reports.find((item) => item.case_id === caseId) ?? data.weekly_reports[0]
  const prior = current ? previousReport(current) : null
  const report = week === 'current' ? current : prior
  if (!report || !current || !prior) return null
  const download = () => {
    const blob = new Blob([reportMarkdown(report, data)], { type: 'text/markdown;charset=utf-8' })
    const href = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = href
    anchor.download = `增长决策周报-${report.case_id}-${report.period}.md`
    anchor.click()
    URL.revokeObjectURL(href)
  }
  const sections = [
    { key: 'anomaly', title: '本周异常', rows: report.anomalies.map((row) => asEntry(row, 'system')), tone: 'danger' as const },
    { key: 'negative', title: '负证据 / 降低优先级', rows: report.negative_evidence.map((row) => asEntry(row, 'system')), tone: 'info' as const },
    { key: 'hypothesis', title: '待验证假设', rows: report.hypotheses.map((row) => asEntry(row, 'human')), tone: 'purple' as const },
    { key: 'experiment', title: '实验进度', rows: asEntries(report.experiment_status, 'system'), tone: 'positive' as const },
    { key: 'action', title: '下周行动', rows: report.recommendations.map((row) => asEntry(row, 'human')), tone: 'warning' as const },
    { key: 'boundary', title: '结论边界', rows: report.limitations.map((row) => asEntry(row, 'human')), tone: 'neutral' as const },
  ]
  return (
    <>
      <PageHeader eyebrow="AUTOMATED WEEKLY REVIEW · 可追溯周报" title="结论来源可追溯，决策依据可复核" description="系统生成指标与统计结果，智能解释组织既有证据，分析者确认业务判断；阶段对比呈现结论随证据演进的过程。" aside={<button type="button" className="primary-button" onClick={download}><Download size={17} />下载 Markdown</button>} />
      <section className="report-toolbar content-section">
        <div className="weekly-selector">
          <div className="segmented-control" role="group" aria-label="周报案例">{caseOptions.map((item) => <button type="button" key={item.case_id} className={caseId === item.case_id ? 'active' : ''} aria-pressed={caseId === item.case_id} onClick={() => setCaseId(item.case_id)}>{item.case_id.includes('referral') ? '老带新' : '新用户留存'}</button>)}</div>
          <div className="segmented-control" role="group" aria-label="周报周期"><button type="button" className={week === 'current' ? 'active' : ''} aria-pressed={week === 'current'} onClick={() => setWeek('current')}>W02 决策阶段</button><button type="button" className={week === 'prior' ? 'active' : ''} aria-pressed={week === 'prior'} onClick={() => setWeek('prior')}>W01 诊断阶段</button></div>
        </div>
        <div className="provenance-legend"><span>内容来源</span><SourceBadge source="system" /><SourceBadge source="ai" /><SourceBadge source="human" /></div>
      </section>
      <div className="demo-disclosure"><Badge tone="warning">演示边界</Badge><span>页面按案例阶段生成周报示例，不代表公司真实自然周数据。</span></div>

      <section className="report-paper content-section">
        <div className="report-cover">
          <div><span>WEEKLY GROWTH REVIEW</span><h2>{displayText(report.title)}</h2><p>{report.period}</p></div>
          <div className="report-headline"><Sparkles size={20} /><strong>{displayText(report.headline)}</strong><p>{displayText(report.narrative?.text)}</p></div>
        </div>
        <div className="report-kpis">
          {report.kpis.map((row, index) => { const kpi = asKpi(row); return <article key={`${kpiName(kpi, data)}-${index}`}><div><span>{kpiName(kpi, data)}</span><SourceBadge source={kpi.source_type ?? 'system'} /></div><strong>{kpiValue(kpi)}</strong><p>{displayText(kpi.change ?? '固定口径')} · {displayText(kpi.status ?? '已收录')}</p></article> })}
        </div>
        <div className="report-sections">
          {sections.map((section) => <article key={section.key} className={`report-section report-${section.tone}`}><div className="report-section-title"><Badge tone={section.tone}>{section.title}</Badge><span>{section.rows.length} 条</span></div><div className="report-section-body">{section.rows.map((row, index) => { const item = asEntry(row); return <div key={`${section.key}-${index}`}><CheckCircle2 size={16} /><p>{item.text}</p><SourceBadge source={item.source_type} /></div> })}</div></article>)}
        </div>
      </section>

      <section className="content-section">
        <SectionHeader label="WEEK OVER WEEK" title="从异常定位到决策推进" />
        <div className="report-diff">
          <div><span>{prior.period} · 诊断阶段</span><strong>{displayText(prior.headline)}</strong><p>重点是明确异常、负证据和数据缺口。</p></div>
          <ArrowRight size={24} aria-hidden="true" />
          <div className="diff-current"><span>{current.period} · 决策阶段</span><strong>{displayText(current.headline)}</strong><p><ArrowDownRight size={15} />在结论边界内形成实验或后续迭代动作。</p></div>
        </div>
      </section>
    </>
  )
}
