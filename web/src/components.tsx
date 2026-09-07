import { ChevronDown, ShieldCheck } from 'lucide-react'
import { useMemo, useState, type ReactNode } from 'react'
import { displayText } from './copy'
import type { CaseId, EvidenceItem, SourceType } from './types'

export function PageHeader({ eyebrow, title, description, aside }: { eyebrow: string; title: string; description: string; aside?: ReactNode }) {
  return <header className="page-header"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>{aside && <div className="page-header-aside">{aside}</div>}</header>
}

export function SectionHeader({ label, title, description, action }: { label?: string; title: string; description?: string; action?: ReactNode }) {
  return <div className="section-header"><div>{label && <span className="section-label">{label}</span>}<h2>{title}</h2>{description && <p>{description}</p>}</div>{action && <div className="section-action">{action}</div>}</div>
}

export function Badge({ children, tone = 'neutral' }: { children: ReactNode; tone?: 'neutral' | 'positive' | 'warning' | 'danger' | 'info' | 'purple' }) {
  return <span className={`badge badge-${tone}`}>{children}</span>
}

export function SourceBadge({ source }: { source?: SourceType }) {
  const normalized = String(source ?? 'human').toLowerCase()
  if (normalized.includes('ai') || normalized.includes('ollama')) return <Badge tone="purple">智能解释</Badge>
  if (normalized.includes('system') || normalized.includes('系统') || normalized.includes('calculation') || normalized.includes('derived') || normalized.includes('method')) return <Badge tone="info">系统计算</Badge>
  return <Badge tone="positive">人工确认</Badge>
}

export function CaseBadge({ caseId }: { caseId: CaseId }) {
  const referral = caseId.includes('referral')
  const retention = caseId.includes('retention')
  return <Badge tone={referral ? 'info' : 'purple'}>{referral ? '老带新增长' : retention ? '新用户留存' : '跨案例'}</Badge>
}

export function EvidencePanel({ evidenceIds, evidence, compact = false }: { evidenceIds: string[]; evidence: EvidenceItem[]; compact?: boolean }) {
  const [open, setOpen] = useState(false)
  const matched = useMemo(() => evidenceIds.map((id) => evidence.find((item) => item.id === id)).filter((item): item is EvidenceItem => Boolean(item)), [evidenceIds, evidence])
  if (!matched.length) return null
  return <div className={`evidence-panel ${compact ? 'compact' : ''}`}>
    <button type="button" className="evidence-toggle" onClick={() => setOpen((value) => !value)} aria-expanded={open}><ShieldCheck size={16} aria-hidden="true" /><span>{matched.length} 条证据可核验</span><ChevronDown size={16} className={open ? 'rotate' : ''} aria-hidden="true" /></button>
    {open && <div className="evidence-list">{matched.map((item) => <article key={item.id} className="evidence-mini-card"><div className="evidence-mini-head"><code>{item.id}</code><SourceBadge source={item.source_type} />{item.synthetic && <Badge tone="warning">模拟演示</Badge>}</div><strong>{displayText(item.title)}</strong><p>{displayText(item.statement)}</p><small>结论边界：{displayText(item.claim_boundary)}</small></article>)}</div>}
  </div>
}

export function Skeleton() {
  return <main className="load-state"><div className="loader" /><strong>正在加载决策工作台…</strong><span>读取指标、证据与案例链路</span></main>
}
