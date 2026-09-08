import type { CopilotData } from './types'

export type CaseKey = 'referral' | 'retention'

export function evidenceNumber(data: CopilotData, evidenceId: string, field: string): number | null {
  const evidence = data.evidence.find((item) => item.id === evidenceId && !item.synthetic)
  const value = evidence?.values[field]
  return typeof value === 'number' && Number.isFinite(value) ? value : null
}

export function caseReadout(data: CopilotData, key: CaseKey) {
  const growth = key === 'referral'
  const experimentId = growth ? 'ev_referral_experiment' : 'ev_retention_experiment'
  return {
    before: evidenceNumber(data, growth ? 'ev_referral_version_trend' : 'ev_retention_trend', growth ? 'before_upgrade_rate' : 'before_rate'),
    after: evidenceNumber(data, growth ? 'ev_referral_version_trend' : 'ev_retention_trend', growth ? 'after_complex_upgrade_rate' : 'after_rate'),
    control: evidenceNumber(data, experimentId, 'control_rate'),
    treatment: evidenceNumber(data, experimentId, 'treatment_rate'),
    days: evidenceNumber(data, experimentId, 'duration_days'),
    sample: evidenceNumber(data, experimentId, 'total_sample'),
    valueRatio: evidenceNumber(data, 'ev_referral_value_cost', 'released_ratio'),
    externalRatio: evidenceNumber(data, 'ev_referral_value_cost', 'external_same_scope_ratio'),
    benchmarkRatio: evidenceNumber(data, 'ev_retention_benchmark', 'benchmark_to_non_benchmark_ratio'),
    deviceGap: evidenceNumber(data, 'ev_retention_device_structure', 'tablet_gap_pp'),
  }
}

export const rateLabel = (value: number | null) => value === null ? '—' : `${Number((value * 100).toFixed(2))}%`
export const numberLabel = (value: number | null, digits = 2) => value === null ? '—' : Number(value.toFixed(digits)).toLocaleString('zh-CN')
export const sampleLabel = (value: number | null) => value === null ? '—' : `${numberLabel(value / 10000)} 万`

export const commonMethod = [
  { title: '业务问题', description: '先明确规模、留存与成本约束，避免只优化局部指标。' },
  { title: '指标口径', description: '统一分子、分母、用户粒度与观察窗口。' },
  { title: '诊断证据', description: '分层识别结构变化，漏斗定位动作，标杆分析形成假设。' },
  { title: '策略验证', description: '将产品改动变成可检验策略，区分相关与因果。' },
  { title: '价值约束', description: '结合效果量、观察周期与投入产出形成行动。' },
]
