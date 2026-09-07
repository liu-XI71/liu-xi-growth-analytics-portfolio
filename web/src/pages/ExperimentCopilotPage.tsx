import { AlertTriangle, Calculator, Check, CircleHelp, FlaskConical, GitBranch, ShieldCheck, UserRoundCheck, X } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Badge, PageHeader, SectionHeader } from '../components'
import { recommendedDuration, srmCheck, stableBucket, twoProportionTest } from '../experiment'
import type { CopilotData } from '../types'

function rateValue(value: number | null | undefined, fallback: number) {
  if (typeof value !== 'number') return fallback
  return value > 1 ? value : value * 100
}

function NumberField({ label, value, onChange, suffix, min, max, step = 0.1, help }: { label: string; value: number; onChange: (value: number) => void; suffix?: string; min?: number; max?: number; step?: number; help?: string }) {
  return <label className="number-field"><span>{label}</span><div><input type="number" value={value} min={min} max={max} step={step} onChange={(event) => onChange(Number(event.target.value))} />{suffix && <em>{suffix}</em>}</div>{help && <small>{help}</small>}</label>
}

export function ExperimentCopilotPage({ data }: { data: CopilotData }) {
  const defaults = data.experiment_defaults.referral ?? {}
  const [baseline, setBaseline] = useState(rateValue(defaults.baseline_rate ?? defaults.baseline, 17))
  const [mde, setMde] = useState(rateValue((defaults.mde_absolute as number | null | undefined) ?? defaults.mde, 3))
  const [alpha, setAlpha] = useState(typeof defaults.alpha === 'number' ? defaults.alpha : 0.05)
  const [power, setPower] = useState(rateValue(defaults.power, 80))
  const [dailyTraffic, setDailyTraffic] = useState(typeof defaults.daily_traffic === 'number' ? defaults.daily_traffic : typeof defaults.total_sample === 'number' && typeof defaults.duration_days === 'number' ? Math.round(defaults.total_sample / defaults.duration_days) : 500000)
  const [userId, setUserId] = useState('lx-demo-user-001')
  const [controlN, setControlN] = useState(100000)
  const [treatmentN, setTreatmentN] = useState(100000)
  const [controlRate, setControlRate] = useState(rateValue(defaults.control_rate, 17))
  const [treatmentRate, setTreatmentRate] = useState(rateValue(defaults.treatment_rate, 23.5))
  const [checks, setChecks] = useState({ aa: false, tracking: false, balance: false })
  const [guardrail, setGuardrail] = useState<'pass' | 'pending' | 'fail'>('pass')
  const [bucketResult, setBucketResult] = useState<{ unitId: string; value: number } | null>(null)

  const design = useMemo(() => recommendedDuration({ baseline: baseline / 100, mde: mde / 100, alpha, power: power / 100, dailyTraffic }), [baseline, mde, alpha, power, dailyTraffic])
  useEffect(() => {
    let active = true
    stableBucket(userId).then((value) => { if (active) setBucketResult({ unitId: userId, value }) }).catch(() => { if (active) setBucketResult(null) })
    return () => { active = false }
  }, [userId])

  const bucket = bucketResult?.unitId === userId ? bucketResult.value : null
  const srm = srmCheck(controlN, treatmentN)
  const test = twoProportionTest(Math.round(controlN * controlRate / 100), controlN, Math.round(treatmentN * treatmentRate / 100), treatmentN)
  const integrityPassed = checks.aa && checks.tracking && checks.balance && Boolean(srm?.passed)
  const statsPassed = Boolean(test && test.pValue < alpha)
  const businessPassed = Boolean(test && test.lift * 100 >= mde)
  const releasePassed = integrityPassed && statsPassed && businessPassed && guardrail === 'pass'
  const verdict = !integrityPassed ? '先修复实验可信度，再判断策略' : guardrail === 'fail' ? '护栏受损，暂不进入后续迭代' : guardrail === 'pending' ? '护栏待回收，保持观察' : statsPassed && businessPassed ? '支持进入后续迭代，并持续监控最终业务指标' : statsPassed ? '统计显著但未达到业务MDE，不建议仅凭p值推进' : '尚未通过统计检验，继续按预设周期观察'

  const gates = [
    { label: 'AA与埋点', pass: checks.aa && checks.tracking, unknown: !(checks.aa && checks.tracking), detail: checks.aa && checks.tracking ? '已在本次试算中标记通过' : '项目复盘未披露，当前未录入' },
    { label: 'SRM（试算）', pass: Boolean(srm?.passed), detail: srm ? `基于演示计数 p=${srm.pValue.toFixed(3)}` : '样本不足' },
    { label: '分层平衡', pass: checks.balance, unknown: !checks.balance, detail: checks.balance ? '已在本次试算中标记通过' : '项目复盘未披露，当前未录入' },
    { label: '统计显著（试算）', pass: statsPassed, detail: test ? `基于演示计数 z=${test.z.toFixed(2)} · p${test.pValue < 0.001 ? '<0.001' : `=${test.pValue.toFixed(3)}`}` : '无法计算' },
    { label: '业务显著', pass: businessPassed, detail: test ? `当前试算 +${(test.lift * 100).toFixed(1)}pp · MDE ${mde.toFixed(1)}pp` : '无法计算' },
    { label: '价值护栏', pass: guardrail === 'pass', pending: guardrail === 'pending', detail: guardrail === 'pass' ? '首月价值/激励成本倍数未受损' : guardrail === 'pending' ? '数据尚未回收完整' : '护栏指标出现损失' },
  ]

  return (
    <>
      <PageHeader eyebrow="EXPERIMENT DESIGN · 从方案到决策" title="A/B 实验设计与决策治理" description="覆盖基线、MDE、显著性水平、统计功效、最小样本量、固定分流、A/A、SRM、人群均衡、业务显著性与价值护栏。" />
      <section className="content-section experiment-fact-banner">
        <Badge tone="purple">项目已确认事实</Badge>
        <p>两周、总样本约700万、1:1随机分流设计，邀请点击率17%→23.5%，p&lt;0.05；首月价值/激励成本倍数2.18，高于同口径外投1.90。</p>
        <small>未披露：实际组内人数、AA结果、SRM结果、分层均衡结果、精确Z值与精确p值。下方读数区是可编辑试算，不是原始实验记录。</small>
      </section>
      <section className="experiment-layout content-section">
        <div className="experiment-main">
          <article className="experiment-panel">
            <SectionHeader label="01 · DESIGN" title="样本量与周期" description="双样本比例检验，双侧检验；周期至少覆盖完整业务周。" />
            <div className="input-grid">
              <NumberField label="历史基线" value={baseline} onChange={setBaseline} suffix="%" min={0.1} max={99} />
              <NumberField label="最小可检测提升 MDE" value={mde} onChange={setMde} suffix="pp" min={0.1} max={30} />
              <NumberField label="显著性水平 α" value={alpha} onChange={setAlpha} min={0.001} max={0.2} step={0.01} />
              <NumberField label="统计功效 Power" value={power} onChange={setPower} suffix="%" min={50} max={99} />
              <NumberField label="每日可用总流量" value={dailyTraffic} onChange={setDailyTraffic} suffix="人" min={1} step={1000} help="默认按约700万÷14天试算；可编辑，非逐日真实流量" />
            </div>
            <div className="calculation-result">
              <Calculator size={22} />
              {design ? <><div><span>每组最小样本</span><strong>{design.perArm.toLocaleString()}</strong></div><div><span>合计样本</span><strong>{design.total.toLocaleString()}</strong></div><div><span>统计所需</span><strong>{design.statisticalDays} 天</strong></div><div><span>完整周期建议</span><strong>{design.fullCycleDays} 天起</strong></div></> : <p>请检查输入：基线 + MDE 必须小于100%，所有参数应为正数。</p>}
            </div>
            <div className="novelty-note"><AlertTriangle size={17} /><p><strong>周期不是由样本量单独决定。</strong>即使一天达到最小样本，也应覆盖完整周，并预先考虑新奇效应。真实项目按两周回收结果。</p></div>
          </article>

          <article className="experiment-panel">
            <SectionHeader label="02 · RANDOMIZATION" title="固定 Hash 分流预览" description="同一用户在实验周期内始终进入同一桶；0–49为实验组，50–99为对照组。" />
            <div className="hash-tool">
              <label><span>输入用户ID</span><input value={userId} onChange={(event) => setUserId(event.target.value)} /></label>
              <div className="bucket-result"><GitBranch size={21} /><span>Bucket</span><strong>{bucket === null ? '—' : String(bucket).padStart(2, '0')}</strong><Badge tone={bucket !== null && bucket < 50 ? 'purple' : 'info'}>{bucket === null ? '计算中' : bucket < 50 ? '实验组' : '对照组'}</Badge></div>
            </div>
            <div className="bucket-bar" aria-label={bucket === null ? '正在计算稳定分桶' : `用户进入第${bucket}桶`}><span className="experiment-half">实验组 00–49</span><span className="control-half">对照组 50–99</span>{bucket !== null && <i style={{ left: `calc(${bucket}% - 6px)` }} />}</div>
            <small className="field-disclosure">与后端统一采用 SHA-256：固定盐值 + 用户ID，读取前8字节后对100取模。</small>
          </article>

          <article className="experiment-panel">
            <SectionHeader label="03 · TRUST CHECK" title="AA、埋点与人群平衡" description="先验证实验是否可信，再讨论策略是否有效。" />
            <div className="trust-checks">
              {([
                ['aa', 'AA核心指标无显著差异', '检查分流与历史基线'],
                ['tracking', '埋点与指标口径一致', '分子、分母、去重与窗口已核对'],
                ['balance', '关键人群分布均衡', '渠道、城市、设备分层检查'],
              ] as const).map(([key, title, note]) => <button type="button" key={key} className={checks[key] ? 'checked' : ''} aria-pressed={checks[key]} onClick={() => setChecks((value) => ({ ...value, [key]: !value[key] }))}><span>{checks[key] ? <Check size={17} /> : <CircleHelp size={17} />}</span><div><strong>{title}</strong><small>{note}</small></div></button>)}
            </div>
          </article>

          <article className="experiment-panel">
            <SectionHeader label="04 · READOUT" title="可编辑结果试算与护栏" description="默认带入已确认的17%与23.5%；组内样本计数为演示输入，不代表项目实际分组人数。修改输入后，试算决策会同步变化。" />
            <div className="readout-grid">
              <div className="readout-arm"><Badge tone="neutral">对照组 · 旧版</Badge><NumberField label="样本量" value={controlN} onChange={setControlN} min={1} step={1000} /><NumberField label="邀请点击率" value={controlRate} onChange={setControlRate} suffix="%" min={0} max={100} /></div>
              <div className="readout-arm treatment"><Badge tone="purple">实验组 · 简化版</Badge><NumberField label="样本量" value={treatmentN} onChange={setTreatmentN} min={1} step={1000} /><NumberField label="邀请点击率" value={treatmentRate} onChange={setTreatmentRate} suffix="%" min={0} max={100} /></div>
            </div>
            <label className="guardrail-select"><span>护栏状态：首月价值/激励成本倍数</span><select value={guardrail} onChange={(event) => setGuardrail(event.target.value as typeof guardrail)}><option value="pass">未受损 / 通过</option><option value="pending">数据未回收完整</option><option value="fail">出现损失</option></select></label>
          </article>
        </div>

        <aside className="decision-gates">
          <div className="gate-title"><FlaskConical size={20} /><div><span>实验决策条件</span><strong>六项准入检查</strong></div></div>
          <div className="gate-list">
            {gates.map((gate) => <div key={gate.label} className={`${gate.pass ? 'pass' : gate.pending ? 'pending' : gate.unknown ? 'unknown' : 'fail'}`}><span>{gate.pass ? <Check size={15} /> : gate.pending ? '…' : gate.unknown ? '?' : <X size={15} />}</span><div><strong>{gate.label}</strong><small>{gate.detail}</small></div></div>)}
          </div>
          <div className={`final-verdict ${releasePassed ? 'pass' : 'hold'}`}><ShieldCheck size={22} /><span>综合决策</span><strong>{verdict}</strong></div>
          <div className="peeking-warning"><UserRoundCheck size={18} /><p><strong>避免未经校正的中期窥探与提前停止。</strong>运行期仅监控数据质量与护栏；达到预设样本量和周期后统一评估主指标。</p></div>
        </aside>
      </section>

      <section className="content-section retention-boundary-card">
        <div><Badge tone="purple">留存实验边界</Badge><h2>主页与关注引导：方向与显著性已知，绝对提升未公开</h2><p>可确认：实验两周、约30万样本、次7日内留存率提升且 p&lt;0.05。不可展示：实验组和对照组的具体留存率、绝对提升百分点。</p></div>
        <div className="boundary-lock"><strong>公开展示</strong><span>提升方向</span><span>统计结论</span><span>样本与周期</span><em>锁定未披露绝对值</em></div>
      </section>
    </>
  )
}
