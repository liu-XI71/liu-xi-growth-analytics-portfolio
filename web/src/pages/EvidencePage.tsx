import { Check, ChevronDown, Database, Search, ShieldCheck } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Badge, CaseBadge, PageHeader, SectionHeader, SourceBadge } from '../components'
import { displayText, roleLabel } from '../copy'
import type { CopilotData, EvidenceItem, MetricContract } from '../types'

function list(value: string[] | string) {
  return Array.isArray(value) ? value : [value]
}

function valueLabel(value: unknown) {
  if (value === null) return '未公开'
  if (typeof value === 'boolean') return value ? '是' : '否'
  if (typeof value === 'object') return JSON.stringify(value)
  return displayText(value)
}

function evidenceTypeLabel(value: string) {
  const labels: Record<string, string> = {
    descriptive_monitoring: '监控事实', derived_funnel: '确定性折算', negative_evidence: '负证据', randomized_experiment: '随机实验', economics_guardrail: '价值护栏',
    experience_reconstruction: '去标识化复盘', descriptive_segmentation: '用户分层', correlational_benchmark: '相关性标杆', method_demonstration: '方法演示', method_contract: '方法合同', governance_boundary: '治理边界',
  }
  return labels[value] ?? displayText(value)
}

function ContractCard({ contract }: { contract: MetricContract }) {
  const [open, setOpen] = useState(false)
  return (
    <article className="contract-card">
      <button type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open}>
        <span className="metric-id">{contract.metric_id}</span>
        <div><strong>{displayText(contract.name)}</strong><small>{roleLabel(contract.role)} · {displayText(contract.window)}</small></div>
        <Badge tone={contract.role.includes('guardrail') || contract.role.includes('护栏') ? 'warning' : contract.role.includes('result') || contract.role.includes('最终') || contract.role.includes('结果') ? 'positive' : 'info'}>{roleLabel(contract.role)}</Badge>
        <ChevronDown size={18} className={open ? 'rotate' : ''} />
      </button>
      {open && <div className="contract-details">
        <dl><div><dt>分子</dt><dd>{displayText(contract.numerator ?? '计数指标，不适用')}</dd></div><div><dt>分母</dt><dd>{displayText(contract.denominator ?? '不适用')}</dd></div><div><dt>时间窗口</dt><dd>{displayText(contract.window)}</dd></div><div><dt>统计粒度</dt><dd>{displayText(contract.grain)}</dd></div></dl>
        <div className="contract-use"><strong>决策用途</strong><p>{displayText(contract.decision_use)}</p></div>
        <div className="claim-columns"><div><strong><Check size={15} />适用结论</strong>{list(contract.allowed_claims).map((item) => <p key={item}>{displayText(item)}</p>)}</div><div><strong>× 使用限制</strong>{list(contract.forbidden_claims).map((item) => <p key={item}>{displayText(item)}</p>)}</div></div>
      </div>}
    </article>
  )
}

function EvidenceCard({ item }: { item: EvidenceItem }) {
  const [open, setOpen] = useState(false)
  return (
    <article className="evidence-card-full">
      <button type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open}>
        <div className="evidence-icon"><Database size={18} /></div>
        <div className="evidence-card-title"><div><code>{item.id}</code><CaseBadge caseId={item.case_id} /><SourceBadge source={item.source_type} /><Badge tone="neutral">{evidenceTypeLabel(item.evidence_type)}</Badge>{item.synthetic && <Badge tone="warning">模拟演示</Badge>}</div><strong>{displayText(item.title)}</strong><p>{displayText(item.statement)}</p></div>
        <ChevronDown size={19} className={open ? 'rotate' : ''} />
      </button>
      {open && <div className="evidence-card-details">
        {Object.keys(item.values ?? {}).length > 0 && <div className="evidence-values">{Object.entries(item.values).map(([key, value]) => <div key={key}><span>{key}</span><strong>{valueLabel(value)}</strong></div>)}</div>}
        <dl><div><dt>计算 / 判定</dt><dd>{displayText(item.calculation || '人工确认的项目事实')}</dd></div><div><dt>结论边界</dt><dd>{displayText(item.claim_boundary)}</dd></div><div><dt>来源引用</dt><dd>{item.source_ref}</dd></div><div><dt>关联指标</dt><dd>{item.metric_id ? displayText(item.metric_id) : '跨指标证据'}</dd></div></dl>
      </div>}
    </article>
  )
}

export function EvidencePage({ data }: { data: CopilotData }) {
  const [tab, setTab] = useState<'contracts' | 'evidence'>('contracts')
  const [query, setQuery] = useState('')
  const [caseFilter, setCaseFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const evidenceTypes = useMemo(() => Array.from(new Set(data.evidence.map((item) => item.evidence_type))), [data.evidence])
  const filteredEvidence = useMemo(() => data.evidence.filter((item) => {
    const text = `${item.id} ${item.title} ${item.statement} ${item.claim_boundary} ${item.metric_id}`.toLowerCase()
    return (caseFilter === 'all' || item.case_id === caseFilter) && (typeFilter === 'all' || item.evidence_type === typeFilter) && text.includes(query.toLowerCase())
  }), [data.evidence, query, caseFilter, typeFilter])
  const filteredContracts = useMemo(() => data.metric_contracts.filter((item) => `${item.metric_id} ${item.name} ${item.role} ${item.decision_use}`.toLowerCase().includes(query.toLowerCase())), [data.metric_contracts, query])
  return (
    <>
      <PageHeader eyebrow="METRIC & EVIDENCE REGISTRY · 口径治理" title="指标口径统一，分析结论可追溯" description="集中管理分子、分母、观察窗口、统计粒度、证据来源与适用边界，降低口径漂移和过度归因风险。" />
      <section className="evidence-summary content-section">
        <div><span>指标合同</span><strong>{data.metric_contracts.length}</strong><small>核心 / 机制 / 护栏</small></div>
        <div><span>证据记录</span><strong>{data.evidence.length}</strong><small>每条都有独立ID</small></div>
        <div><span>证据层级</span><strong>4 类</strong><small>事实 / 推断 / 实验 / 决策</small></div>
        <div className="safety-promise"><ShieldCheck size={22} /><p><strong>结论治理原则</strong><span>相关性与因果性分层表达；缺失数据不进行无依据量化。</span></p></div>
      </section>

      <section className="evidence-toolbar content-section">
        <div className="registry-tabs" role="tablist"><button type="button" role="tab" aria-selected={tab === 'contracts'} className={tab === 'contracts' ? 'active' : ''} onClick={() => setTab('contracts')}>指标合同</button><button type="button" role="tab" aria-selected={tab === 'evidence'} className={tab === 'evidence' ? 'active' : ''} onClick={() => setTab('evidence')}>证据账本</button></div>
        <label className="search-box"><Search size={18} /><span className="sr-only">搜索</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索指标、证据ID或业务结论" /></label>
        {tab === 'evidence' && <div className="filter-row"><label><span className="sr-only">案例</span><select value={caseFilter} onChange={(event) => setCaseFilter(event.target.value)}><option value="all">全部案例</option>{data.cases.map((item) => <option key={item.id} value={item.id}>{item.id.includes('referral') ? '老带新增长' : '新用户留存'}</option>)}</select></label><label><span className="sr-only">证据类型</span><select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}><option value="all">全部证据类型</option>{evidenceTypes.map((type) => <option key={type} value={type}>{evidenceTypeLabel(type)}</option>)}</select></label></div>}
      </section>

      <section className="registry-content content-section">
        <SectionHeader label={tab === 'contracts' ? 'METRIC CONTRACTS' : 'EVIDENCE LEDGER'} title={tab === 'contracts' ? `${filteredContracts.length} 个指标口径` : `${filteredEvidence.length} 条可核验证据`} description={tab === 'contracts' ? '展开指标可查看决策用途、适用结论与使用限制。' : '证据值、来源、计算方法与结论边界同步保存。'} />
        <div className={tab === 'contracts' ? 'contract-list' : 'evidence-full-list'}>
          {tab === 'contracts' ? filteredContracts.map((item) => <ContractCard key={item.metric_id} contract={item} />) : filteredEvidence.map((item) => <EvidenceCard key={item.id} item={item} />)}
        </div>
      </section>

      <section className="content-section compact-section">
        <SectionHeader label="CONCLUSION GOVERNANCE" title="业务结论治理规则" description="在指标计算、证据解释与决策输出之间建立统一约束。" />
        <div className="boundary-grid"><div><strong>证据分层</strong><p>监控事实、描述性分析、观察性关联与随机实验采用不同结论强度。</p></div><div><strong>输入完整性</strong><p>结构贡献、实验效果与价值评估仅在必要输入完整时进行量化。</p></div><div><strong>口径一致性</strong><p>观察窗口、成本范围、归因规则与对比基准保持一致。</p></div></div>
      </section>
    </>
  )
}
