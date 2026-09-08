export function displayText(value: unknown) {
  return String(value ?? '')
    .replaceAll('指标合同', '指标口径')
    .replaceAll('智能分析', '分析链路')
    .replaceAll('次1至7日窗口留存率', '次7日内留存率')
    .replaceAll('次1至7日窗口留存', '次7日内留存')
    .replaceAll('首月价值成本比', '首月价值/激励成本倍数')
    .replaceAll('首月价值/激励成本比', '首月价值/激励成本倍数')
    .replaceAll('device_retention_gap', '平板与手机留存差距')
}

export function statusLabel(value: unknown) {
  const status = String(value ?? '')
  const labels: Record<string, string> = {
    ship_with_monitoring: '持续迭代并监控',
    continue_with_monitoring: '继续推进并监控',
    diagnosis_ready: '诊断完成',
    data_gap_visible: '数据缺口已标记',
    supported: '证据支持',
    completed: '已完成',
    complete: '已完成',
    correlational: '相关性线索',
    causal_supported: '因果证据支持',
    causal_supported_lift_unknown: '因果支持 · 幅度未公开',
    direction_supported_quantification_blocked: '方向支持 · 量化受阻',
    not_primary_explanation: '降低优先级',
    hypothesis: '待验证假设',
  }
  return labels[status] ?? displayText(status)
}

export function roleLabel(value: string) {
  const labels: Record<string, string> = {
    result: '结果指标', final_business: '结果指标', mechanism: '机制指标', diagnostic: '诊断指标', exploratory: '探索指标', guardrail: '护栏指标', decision_guardrail: '决策护栏', primary: '核心指标',
  }
  return labels[value] ?? displayText(value)
}
