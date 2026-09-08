import { lazy, Suspense, useEffect, useLayoutEffect, useState } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { Skeleton } from './components'
import { loadCopilot } from './data'
import { Layout } from './layout'
import type { LoadedCopilot } from './types'

const DecisionPage = lazy(async () => ({ default: (await import('./pages/DecisionPage')).DecisionPage }))
const AnalysisPage = lazy(async () => ({ default: (await import('./pages/AnalysisPage')).AnalysisPage }))
const WeeklyReportPage = lazy(async () => ({ default: (await import('./pages/WeeklyReportPage')).WeeklyReportPage }))
const ReplayPage = lazy(async () => ({ default: (await import('./pages/ReplayPage')).ReplayPage }))
const ExperimentCopilotPage = lazy(async () => ({ default: (await import('./pages/ExperimentCopilotPage')).ExperimentCopilotPage }))
const EvidencePage = lazy(async () => ({ default: (await import('./pages/EvidencePage')).EvidencePage }))
const CaseStudyPage = lazy(async () => ({ default: (await import('./pages/CaseStudyPage')).CaseStudyPage }))
const MethodPage = lazy(async () => ({ default: (await import('./pages/MethodPage')).MethodPage }))

function ScrollToTop() {
  const { key, pathname } = useLocation()
  useLayoutEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
    const frame = window.requestAnimationFrame(() => window.scrollTo(0, 0))
    return () => window.cancelAnimationFrame(frame)
  }, [key, pathname])
  return null
}

export default function App() {
  const [loaded, setLoaded] = useState<LoadedCopilot | null>(null)
  const [loadFailed, setLoadFailed] = useState(false)

  useEffect(() => {
    loadCopilot().then(setLoaded).catch(() => setLoadFailed(true))
  }, [])

  if (loadFailed) return (
    <main className="data-load-error">
      <span>加载提示</span>
      <h1>案例数据加载失败</h1>
      <p>请检查网络连接后重试。本地部署请确认服务已启动、data/growth-analytics.json 文件可访问；不要直接双击源码中的 index.html。</p>
      <button type="button" onClick={() => window.location.reload()}>重新加载</button>
    </main>
  )
  if (!loaded) return <Skeleton />
  const { data, source } = loaded
  return (
    <Layout meta={data.meta} source={source}>
      <ScrollToTop />
      <Suspense fallback={<div className="route-loading"><div className="loader" /><span>正在展开业务工作区…</span></div>}>
        <Routes>
          <Route path="/" element={<DecisionPage data={data} source={source} />} />
          <Route path="/cases/referral" element={<CaseStudyPage data={data} caseKey="referral" />} />
          <Route path="/cases/retention" element={<CaseStudyPage data={data} caseKey="retention" />} />
          <Route path="/methods" element={<MethodPage />} />
          <Route path="/analysis" element={<AnalysisPage data={data} />} />
          <Route path="/weekly" element={<WeeklyReportPage data={data} />} />
          <Route path="/replay" element={<ReplayPage data={data} />} />
          <Route path="/experiment" element={<ExperimentCopilotPage data={data} />} />
          <Route path="/evidence" element={<EvidencePage data={data} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </Layout>
  )
}
