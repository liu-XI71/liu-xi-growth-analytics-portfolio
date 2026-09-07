import type { EChartsOption } from 'echarts'
import ChartCore from './chart-core'
import type { CopilotData } from './types'

function baseGrid(): EChartsOption {
  return {
    animationDuration: 500,
    grid: { left: 18, right: 18, top: 24, bottom: 12, containLabel: true },
    tooltip: { trigger: 'axis', backgroundColor: '#132138', borderWidth: 0, textStyle: { color: '#fff' } },
    xAxis: { axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#64748b' } },
    yAxis: { axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: '#e8edf4' } }, axisLabel: { color: '#64748b' } },
  }
}

function record(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {}
}

function numberValue(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : 0
}

function evidenceValues(data: CopilotData, id: string): Record<string, unknown> {
  return record(data.evidence.find((item) => item.id === id)?.values)
}

function percent(value: unknown): number {
  return numberValue(value) * 100
}

function analysisData(data: CopilotData, caseId: string): Record<string, unknown> {
  const item = data.cases.find((candidate) => candidate.id.includes(caseId))
  return record(item?.analysis_data)
}

function statusGraphic(): EChartsOption {
  return {
    graphic: [
      { type: 'rect', left: '9%', top: '31%', shape: { width: 150, height: 78, r: 12 }, style: { fill: '#eef1f6', stroke: '#d4dae5', lineWidth: 1 } },
      { type: 'text', left: '12%', top: '39%', style: { text: '对照组\n绝对值未公开', fill: '#526074', font: '600 14px sans-serif', lineHeight: 23, align: 'center' } },
      { type: 'text', left: '47%', top: '43%', style: { text: '→', fill: '#78879b', font: '700 28px sans-serif' } },
      { type: 'rect', right: '9%', top: '31%', shape: { width: 150, height: 78, r: 12 }, style: { fill: '#edf0ff', stroke: '#8a91ed', lineWidth: 1 } },
      { type: 'text', right: '12%', top: '39%', style: { text: '实验组\n方向提升 · p < 0.05', fill: '#4e51b7', font: '700 14px sans-serif', lineHeight: 23, align: 'center' } },
      { type: 'text', left: 'center', bottom: '10%', style: { text: '状态图不编码提升幅度', fill: '#7b8798', font: '12px sans-serif', align: 'center' } },
    ],
  }
}

function chartOption(data: CopilotData, dataKey: string, caseId = ''): { option: EChartsOption; label: string } {
  const referral = caseId.includes('referral')
  const referralTrend = evidenceValues(data, 'ev_referral_version_trend')
  const referralExperiment = evidenceValues(data, 'ev_referral_experiment')
  const referralFunnel = evidenceValues(data, 'ev_referral_partial_funnel')
  const retentionTrend = evidenceValues(data, 'ev_retention_trend')
  const retentionStructure = evidenceValues(data, 'ev_retention_device_structure')
  const benchmark = evidenceValues(data, 'ev_retention_benchmark')
  const economics = evidenceValues(data, 'ev_referral_value_cost')

  if (dataKey.includes('referral_experiment') || (dataKey === 'experiment' && referral)) {
    const control = percent(referralExperiment.control_rate)
    const treatment = percent(referralExperiment.treatment_rate)
    return {
      label: `邀请点击率实验结果，对照组${control}%，实验组${treatment}%`,
      option: { ...baseGrid(), xAxis: { type: 'category', data: ['对照组\n旧版', '实验组\n简化版'], axisLine: { show: false }, axisTick: { show: false } }, yAxis: { type: 'value', max: Math.ceil(Math.max(control, treatment) + 5), axisLabel: { formatter: '{value}%' }, splitLine: { lineStyle: { color: '#e8edf4' } } }, series: [{ type: 'bar', data: [{ value: control, itemStyle: { color: '#a8b4c7', borderRadius: [8, 8, 0, 0] } }, { value: treatment, itemStyle: { color: '#2e6cf6', borderRadius: [8, 8, 0, 0] } }], barWidth: '42%', label: { show: true, position: 'top', formatter: '{c}%', fontWeight: 700 } }] },
    }
  }
  if (dataKey.includes('referral') || dataKey === 'version_trend') {
    const before = percent(referralTrend.before_upgrade_rate)
    const complex = percent(referralTrend.after_complex_upgrade_rate)
    const treatment = percent(referralExperiment.treatment_rate)
    return {
      label: `邀请点击率版本变化，${before}%降至${complex}%，简化实验组为${treatment}%`,
      option: { ...baseGrid(), xAxis: { type: 'category', data: ['升级前', '复杂升级后', '简化实验组'], axisLine: { show: false }, axisTick: { show: false } }, yAxis: { type: 'value', max: Math.ceil(Math.max(before, complex, treatment) + 5), axisLabel: { formatter: '{value}%' }, splitLine: { lineStyle: { color: '#e8edf4' } } }, series: [{ type: 'bar', data: [{ value: before, itemStyle: { color: '#6f8cf7', borderRadius: [8, 8, 0, 0] } }, { value: complex, itemStyle: { color: '#e36b5d', borderRadius: [8, 8, 0, 0] } }, { value: treatment, itemStyle: { color: '#2e9f79', borderRadius: [8, 8, 0, 0] } }], barWidth: '38%', label: { show: true, position: 'top', formatter: '{c}%', fontWeight: 700 } }] },
    }
  }
  if (dataKey.includes('retention_residual') || dataKey === 'retention_trend') {
    const before = percent(retentionTrend.before_rate)
    const after = percent(retentionTrend.after_rate)
    return {
      label: `次7日内留存率由${before}%下降到${after}%`,
      option: { ...baseGrid(), xAxis: { type: 'category', data: ['下滑前', '下滑后'], axisLine: { show: false }, axisTick: { show: false } }, yAxis: { type: 'value', min: Math.floor(Math.min(before, after) - 5), max: Math.ceil(Math.max(before, after) + 5), axisLabel: { formatter: '{value}%' }, splitLine: { lineStyle: { color: '#e8edf4' } } }, series: [{ type: 'bar', data: [{ value: before, itemStyle: { color: '#536eec', borderRadius: [8, 8, 0, 0] } }, { value: after, itemStyle: { color: '#e36b5d', borderRadius: [8, 8, 0, 0] } }], barWidth: '42%', label: { show: true, position: 'top', formatter: '{c}%', fontWeight: 700 } }] },
    }
  }
  if (dataKey.includes('funnel') && referral) {
    const visits = numberValue(referralFunnel.normalized_visits)
    const stage = record(referralFunnel.diagnostic_stage)
    const clicks = numberValue(stage.invite_clicks)
    const shares = numberValue(stage.share_successes)
    return {
      label: `复杂升级后诊断折算：标准化${visits}名活动页访问用户中，${clicks}人点击邀请，${shares}人成功分享`,
      option: { tooltip: { trigger: 'item', formatter: '{b}: {c}' }, series: [{ type: 'funnel', top: 12, bottom: 8, left: '8%', width: '84%', minSize: '20%', maxSize: '100%', gap: 3, label: { show: true, position: 'inside', color: '#fff', formatter: '{b}  {c}' }, itemStyle: { borderWidth: 0 }, data: [{ value: visits, name: '活动页访问' }, { value: clicks, name: '点击邀请' }, { value: shares, name: '成功分享' }] }] },
    }
  }
  if (dataKey.includes('funnel') || dataKey === 'path') {
    const path = record(analysisData(data, 'retention').path)
    const steps = Array.isArray(path.steps) ? path.steps.map(String) : []
    return {
      label: '新用户主要路径趋势状态；不编码未披露的绝对转化率',
      option: { ...baseGrid(), grid: { left: 24, right: 24, top: 16, bottom: 44, containLabel: true }, xAxis: { type: 'category', data: steps, axisLine: { lineStyle: { color: '#dbe3ee' } }, axisTick: { show: false }, axisLabel: { color: '#59687e', interval: 0 } }, yAxis: { type: 'value', show: false, min: 0, max: 2 }, series: [{ name: '趋势状态', type: 'line', data: steps.map(() => 1), symbol: 'circle', symbolSize: 13, lineStyle: { color: '#9aabc2', type: 'dashed', width: 2 }, itemStyle: { color: '#5472d3' }, label: { show: true, position: 'top', formatter: '无明显下滑', color: '#52647d', fontSize: 10 } }] },
    }
  }
  if (dataKey.includes('benchmark')) {
    const ratio = numberValue(benchmark.benchmark_to_non_benchmark_ratio)
    return {
      label: `博主主页与关注渗透率，标杆用户约为非标杆用户的${ratio}倍`,
      option: { ...baseGrid(), grid: { left: 20, right: 48, top: 14, bottom: 10, containLabel: true }, xAxis: { type: 'value', max: Math.ceil(ratio + 0.5), axisLabel: { formatter: '{value}x' }, splitLine: { lineStyle: { color: '#e8edf4' } } }, yAxis: { type: 'category', data: ['非标杆用户', '高频高时标杆用户'], axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#475569' } }, series: [{ type: 'bar', data: [1, { value: ratio, itemStyle: { color: '#6a5bea' } }], barWidth: 20, itemStyle: { color: '#a7b3c9', borderRadius: [0, 8, 8, 0] }, label: { show: true, position: 'right', formatter: '{c}x', fontWeight: 700 } }] },
    }
  }
  if (dataKey === 'economics') {
    const released = numberValue(economics.released_ratio)
    const external = numberValue(economics.external_same_scope_ratio)
    return {
      label: `首月价值/激励成本倍数${released}，对照同口径外投参考${external}`,
      option: { ...baseGrid(), xAxis: { type: 'category', data: ['策略版本', '同口径外投参考'], axisLine: { show: false }, axisTick: { show: false } }, yAxis: { type: 'value', max: Math.ceil((Math.max(released, external) + 0.25) * 2) / 2, splitLine: { lineStyle: { color: '#e8edf4' } } }, series: [{ type: 'bar', data: [{ value: released, itemStyle: { color: '#2e6cf6', borderRadius: [8, 8, 0, 0] } }, { value: external, itemStyle: { color: '#a8b4c7', borderRadius: [8, 8, 0, 0] } }], barWidth: '40%', label: { show: true, position: 'top', formatter: '{c}', fontWeight: 700 } }] },
    }
  }
  if (dataKey === 'device_structure') {
    const gap = numberValue(retentionStructure.tablet_gap_pp)
    return {
      label: `平板留存比手机低约${gap}个百分点；分期占比缺失，结构贡献不可计算`,
      option: { ...baseGrid(), grid: { left: 20, right: 80, top: 22, bottom: 18, containLabel: true }, xAxis: { type: 'value', max: Math.ceil(gap + 2), axisLabel: { formatter: '{value}pp' }, splitLine: { lineStyle: { color: '#e8edf4' } } }, yAxis: { type: 'category', data: ['平板相对手机留存差距'], axisLine: { show: false }, axisTick: { show: false } }, series: [{ type: 'bar', data: [gap], barWidth: 24, itemStyle: { color: '#e79b51', borderRadius: [0, 8, 8, 0] }, label: { show: true, position: 'right', formatter: `约低${gap}pp\n结构贡献不可计算`, fontWeight: 700 } }] },
    }
  }
  if (dataKey === 'metric_contracts' || dataKey === 'claims') {
    return {
      label: '结果指标、机制指标和护栏指标共同组成决策口径',
      option: { ...baseGrid(), xAxis: { type: 'category', data: ['结果指标', '机制指标', '护栏指标'], axisLine: { show: false }, axisTick: { show: false } }, yAxis: { type: 'value', show: false, max: 1.25 }, series: [{ type: 'bar', data: [{ value: 1, itemStyle: { color: '#2e6cf6', borderRadius: [8, 8, 0, 0] } }, { value: 1, itemStyle: { color: '#6958e8', borderRadius: [8, 8, 0, 0] } }, { value: 1, itemStyle: { color: '#178764', borderRadius: [8, 8, 0, 0] } }], barWidth: '38%', label: { show: true, position: 'top', formatter: '口径已定义', fontWeight: 600 } }] },
    }
  }
  return { label: '留存引导实验仅公开方向与统计结论，绝对数值未披露', option: statusGraphic() }
}

export function AnalysisChart({ data, dataKey, caseId, height = 250 }: { data: CopilotData; dataKey: string; caseId?: string; height?: number }) {
  const { option, label } = chartOption(data, dataKey, caseId)
  return <div className="chart-shell"><ChartCore option={option} height={height} ariaLabel={label} /><div className="chart-note">公开演示视图 · 以证据卡中的口径与边界为准</div></div>
}
