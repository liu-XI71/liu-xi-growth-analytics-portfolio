import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import published from '../public/data/growth-analytics.json'
import { caseReadout, evidenceNumber, numberLabel, rateLabel } from './case-model'
import { DecisionPage } from './pages/DecisionPage'
import { CaseStudyPage } from './pages/CaseStudyPage'
import { MethodPage } from './pages/MethodPage'
import type { CopilotData } from './types'

const data = published as unknown as CopilotData

describe('case summaries use the published evidence source', () => {
  it('keeps monitoring and experiment comparisons distinct', () => {
    const referral = caseReadout(data, 'referral')
    expect([referral.before, referral.after, referral.control, referral.treatment]).toEqual([0.21, 0.17, 0.17, 0.235])
    expect(referral.sample).toBe(7000000)
    const retention = caseReadout(data, 'retention')
    expect([retention.before, retention.after]).toEqual([0.48, 0.41])
    expect(retention.sample).toBe(300000)
    expect([retention.control, retention.treatment]).toEqual([null, null])
  })
  it('does not fill absent values with zero or synthetic data', () => {
    expect(evidenceNumber(data, 'missing', 'value')).toBeNull()
    expect(evidenceNumber(data, 'ev_synthetic_mix_shift', 'baseline_rate')).toBeNull()
    expect(rateLabel(null)).toBe('—')
    expect(numberLabel(null)).toBe('—')
    expect(rateLabel(0)).toBe('0%')
  })
  it('home links to both distinct case routes and companion tools', () => {
    const html = renderToStaticMarkup(<MemoryRouter><DecisionPage data={data} source="snapshot" /></MemoryRouter>)
    expect(html).toContain('/cases/referral')
    expect(html).toContain('/cases/retention')
    expect(html).toContain('collection.html')
    expect(html).toContain('liu-xi-csv-analyst')
    expect(html).toContain('mentor')
    expect(html).not.toContain('决策证据关联')
  })
  it('retention case never substitutes monitoring rates for experiment rates', () => {
    const html = renderToStaticMarkup(<MemoryRouter><CaseStudyPage data={data} caseKey="retention" /></MemoryRouter>)
    expect(html).toContain('组间绝对留存率未公开')
    expect(html).toContain('不展示效果量柱状图')
    expect(html).not.toContain('44.9%')
    expect(html).not.toContain('47.9%')
    expect(html).toContain('短期内未落地')
    expect(html).toContain('先验意愿')
  })
  it('growth case preserves strategy-level interpretation and cost scope', () => {
    const html = renderToStaticMarkup(<MemoryRouter><CaseStudyPage data={data} caseKey="referral" /></MemoryRouter>)
    expect(html).toContain('不是随机实验组间效果')
    expect(html).toContain('不能分别归因给某个单一元素')
    expect(html).toContain('首月价值')
    expect(html).toContain('A/A、SRM')
  })
  it('methods separate reusable checks from historical performed claims', () => {
    const html = renderToStaticMarkup(<MemoryRouter><MethodPage /></MemoryRouter>)
    expect(html).toContain('不保证实际人数绝对相等')
    expect(html).toContain('A/A 不能自动解决辛普森悖论')
    expect(html).toContain('|Z|')
    expect(html).toContain('簇级设计')
  })
})
