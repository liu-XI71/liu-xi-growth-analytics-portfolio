import type { EChartsOption } from 'echarts'
import { BarChart, FunnelChart, LineChart, RadarChart } from 'echarts/charts'
import { GraphicComponent, GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import * as echarts from 'echarts/core'
import ReactEChartsCore from 'echarts-for-react/esm/core'
import { SVGRenderer } from 'echarts/renderers'

echarts.use([BarChart, FunnelChart, LineChart, RadarChart, GraphicComponent, GridComponent, LegendComponent, TooltipComponent, SVGRenderer])

export default function ChartCore({ option, height, ariaLabel }: { option: EChartsOption; height: number; ariaLabel: string }) {
  return <div role="img" aria-label={ariaLabel}><ReactEChartsCore echarts={echarts} option={{ animationDuration: 650, textStyle: { fontFamily: 'Inter, PingFang SC, Microsoft YaHei, sans-serif', color: '#172033' }, ...option }} notMerge style={{ height }} opts={{ renderer: 'svg' }} /></div>
}
