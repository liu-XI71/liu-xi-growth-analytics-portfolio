import { BarChart3, Bot, Database, FileText, FlaskConical, History, Menu, X } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import type { CopilotMeta, LoadedCopilot } from './types'

const navigation = [
  { to: '/', label: '决策总览', note: '核心判断与行动', icon: BarChart3, end: true },
  { to: '/analysis', label: '智能分析', note: '证据驱动诊断', icon: Bot },
  { to: '/weekly', label: '自动周报', note: '结论来源追溯', icon: FileText },
  { to: '/replay', label: '案例链路', note: '两类业务复盘', icon: History },
  { to: '/experiment', label: '实验决策', note: '设计与评估', icon: FlaskConical },
  { to: '/evidence', label: '指标治理', note: '口径与边界', icon: Database },
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
          <div><strong>刘希</strong><span>Growth Analytics</span></div>
          <button type="button" className="sidebar-close" onClick={() => setMobileOpen(false)} aria-label="关闭导航"><X /></button>
        </div>
        <div className="brand-promise"><span>业务问题</span><i /> <span>可信证据</span><i /> <span>可执行决策</span></div>
        <nav>
          {navigation.map(({ to, label, note, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} onClick={() => setMobileOpen(false)} className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <Icon size={19} aria-hidden="true" />
              <span><strong>{label}</strong><small>{note}</small></span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="boundary-label">数据边界</div>
          <p>{meta.data_boundary}</p>
          <div className="version-line"><span className={`source-dot ${source}`} />{source === 'api' ? '实时 API 数据' : '已发布数据快照'} · v{meta.version}</div>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div><span className="pulse" />增长分析作品集</div>
          <div className="topbar-right"><span>分析原则</span><strong>{meta.narrative_mode === 'evidence_bounded' ? '证据约束' : meta.narrative_mode === 'deterministic' ? '确定性计算' : '证据约束'}</strong></div>
        </header>
        <main id="main-content" className="main-content" tabIndex={-1}>{children}</main>
        <footer className="site-footer">以可复核证据连接业务异常、实验验证与增长决策。</footer>
      </div>
    </div>
  )
}
