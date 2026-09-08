import { ArrowUpRight, BarChart3, BookOpen, FileText, FlaskConical, History, Menu, Route, Users, X } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import type { CopilotMeta, LoadedCopilot } from './types'

const navigation = [
  { to: '/', label: '业务总览', note: '目标、方法与结果', icon: BarChart3, end: true },
  { to: '/cases/referral', label: '老带新案例', note: '从邀请断点到策略验证', icon: Route },
  { to: '/cases/retention', label: '新用户留存案例', note: '从结构诊断到产品引导', icon: Users },
  { to: '/methods', label: '指标与实验方法', note: '可复用的分析标准', icon: BookOpen },
]
const supportNavigation = [
  { to: '/analysis', label: '分析链路', icon: Route },
  { to: '/weekly', label: '案例周报', icon: FileText },
  { to: '/replay', label: '分步回放', icon: History },
  { to: '/experiment', label: '实验试算', icon: FlaskConical },
  { to: '/evidence', label: '指标口径与证据', icon: BookOpen },
]

export function Layout({ meta, source, children }: { meta: CopilotMeta; source: LoadedCopilot['source']; children: ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">跳到主要内容</a>
      <button type="button" className="mobile-menu-button" onClick={() => setMobileOpen(true)} aria-label="打开导航"><Menu /></button>
      {mobileOpen && <button type="button" className="nav-backdrop" onClick={() => setMobileOpen(false)} aria-label="关闭导航遮罩" />}
      <aside className={`sidebar ${mobileOpen ? 'open' : ''}`} aria-label="主导航">
        <div className="brand-row">
          <div className="brand-mark" aria-hidden="true">LX</div>
          <div><strong>刘希｜增长与实验</strong><span>Growth & Experiments</span></div>
          <button type="button" className="sidebar-close" onClick={() => setMobileOpen(false)} aria-label="关闭导航"><X /></button>
        </div>
        <div className="brand-promise"><span>业务问题</span><i /> <span>可信证据</span><i /> <span>可执行决策</span></div>
        <nav aria-label="业务案例">
          {navigation.map(({ to, label, note, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} onClick={() => setMobileOpen(false)} className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <Icon size={19} aria-hidden="true" />
              <span><strong>{label}</strong><small>{note}</small></span>
            </NavLink>
          ))}
        </nav>
        <details className="support-navigation">
          <summary>分析工具与案例资料</summary>
          <nav aria-label="分析工具">{supportNavigation.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} onClick={() => setMobileOpen(false)}><Icon size={14} />{label}</NavLink>)}</nav>
        </details>
        <a className="collection-link" href={`${import.meta.env.BASE_URL}collection.html`}>数据分析作品集 <ArrowUpRight size={15} /></a>
        <div className="sidebar-footer">
          <details><summary className="boundary-label">数据与项目说明</summary><p>{meta.data_boundary}</p></details>
          <div className="version-line"><span className={`source-dot ${source}`} />{source === 'api' ? '实时 API 数据' : '已发布数据快照'} · v{meta.version}</div>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div><span className="pulse" />用户增长 · 新用户留存</div>
          <div className="topbar-right"><span>个人作品</span><strong>业务分析与方法沉淀</strong></div>
        </header>
        <main id="main-content" className="main-content" tabIndex={-1}>{children}</main>
        <footer className="site-footer">以可复核证据连接业务异常、实验验证与增长决策。</footer>
      </div>
    </div>
  )
}
