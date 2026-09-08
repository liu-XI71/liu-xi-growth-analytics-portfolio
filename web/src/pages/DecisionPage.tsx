import { ArrowRight, ArrowUpRight, BookOpen, CheckCircle2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { caseReadout, commonMethod, numberLabel, rateLabel } from '../case-model'
import { PageHeader, SectionHeader } from '../components'
import type { CopilotData, LoadedCopilot } from '../types'

export function DecisionPage({ data }: { data: CopilotData; source: LoadedCopilot['source'] }) {
  const referral = caseReadout(data, 'referral')
  const retention = caseReadout(data, 'retention')
  const lift = referral.control !== null && referral.treatment !== null ? (referral.treatment - referral.control) * 100 : null
  return <>
    <PageHeader eyebrow="LIU XI · GROWTH & EXPERIMENTS" title="从业务问题到增长决策" description="两段用户增长与留存实习，一套从指标拆解、诊断定位到实验评估的方法。重点呈现分析目的、判断依据与策略推进过程。" aside={<Link className="primary-button" to="/cases/referral">开始浏览案例 <ArrowRight size={16} /></Link>} />
    <div className="participation-note"><CheckCircle2 size={18} /><p><strong>个人参与</strong> 在 mentor 带领下参与指标梳理与看板监测、分层与漏斗分析、策略反馈、实验设计与结果评估；本作品将项目分析方法沉淀为可交互案例。</p></div>
    <section className="case-showcase content-section" aria-label="两段实习案例">
      <article className="showcase-card growth">
        <div className="showcase-kicker"><span>CASE 01</span><span>字节跳动 · 红果业务线 · 用户增长</span></div>
        <h2>老带新：从邀请断点<br />到页面简化实验</h2>
        <p>外部拉新供给承压，激励升级后邀请点击反而下降。先定位用户动作断点，再验证页面改版，最后检查新增价值能否覆盖激励投入。</p>
        <div className="showcase-metrics"><div><span>邀请点击率 · 实验对照</span><strong>{rateLabel(referral.control)} <i>→</i> {rateLabel(referral.treatment)}</strong><small>组间提升 {numberLabel(lift, 1)} 个百分点</small></div><div><span>首月价值 / 激励成本</span><strong>{numberLabel(referral.valueRatio)}</strong><small>同口径外投基准 {numberLabel(referral.externalRatio)}</small></div></div>
        <ol className="case-mini-chain"><li>漏斗定位</li><li>产品反馈</li><li>随机实验</li><li>价值评估</li></ol>
        <Link className="primary-button" to="/cases/referral">查看老带新案例 <ArrowRight size={16} /></Link>
      </article>
      <article className="showcase-card retention">
        <div className="showcase-kicker"><span>CASE 02</span><span>小红书 · 新用户留存</span></div>
        <h2>留存：从人群结构<br />到关注引导实验</h2>
        <p>投放新增用户回访不足。先区分人群结构与路径体验，再从标杆用户行为中提出产品假设，以实验评估主页与关注引导策略。</p>
        <div className="showcase-metrics"><div><span>次 7 日内留存 · 监控变化</span><strong>{rateLabel(retention.before)} <i>→</i> {rateLabel(retention.after)}</strong><small>异常识别，不是实验组间对比</small></div><div><span>标杆 / 非标杆关注渗透</span><strong>{numberLabel(retention.benchmarkRatio)} 倍</strong><small>形成假设，后续实验评估策略</small></div></div>
        <ol className="case-mini-chain"><li>用户分层</li><li>路径排查</li><li>标杆分析</li><li>因果验证</li></ol>
        <Link className="primary-button" to="/cases/retention">查看新用户留存案例 <ArrowRight size={16} /></Link>
      </article>
    </section>
    <section className="method-strip content-section">
      <SectionHeader label="ONE REUSABLE FRAMEWORK" title="两个业务场景，共用一套判断标准" description="从业务目标出发，把描述现象、解释原因和验证策略分开处理。" />
      <ol className="case-method-flow">{commonMethod.map((item, index) => <li key={item.title}><span>0{index + 1}</span><strong>{item.title}</strong><p>{item.description}</p></li>)}</ol>
      <Link className="method-more" to="/methods">查看指标与实验方法 <ArrowRight size={16} /></Link>
    </section>
    <section className="content-section">
      <SectionHeader label="ANALYTICAL JUDGEMENT" title="三项关键业务判断" />
      <div className="common-capability"><div><strong>01</strong><h3>区分人群结构与组内表现</h3><p>整体留存是各类用户留存的加权结果。先观察人群占比和组内表现，再判断结构与产品因素。</p></div><div><strong>02</strong><h3>区分行为相关性与策略因果</h3><p>高频高时用户更常关注博主，仍需排查先验意愿和行为暴露差异，再验证引导策略。</p></div><div><strong>03</strong><h3>结合统计效果与业务约束</h3><p>邀请点击提升后仍要观察最终拉新与新用户质量，并使用同窗口、同成本范围的价值比较。</p></div></div>
    </section>
    <section className="content-section">
      <SectionHeader label="REUSABLE TOOLS" title="从案例方法，到可复用工具" description="此处聚焦实习业务分析。重复数据分析与客户运营，分别由两项独立工具承接。" action={<a className="text-link" href={`${import.meta.env.BASE_URL}collection.html`}>查看全部作品 <ArrowUpRight size={15} /></a>} />
      <div className="tool-links"><a href="https://liu-xi71.github.io/liu-xi-csv-analyst/"><BookOpen size={22} /><div><strong>CSV分析工作台</strong><p>导入新数据、确认口径、复算分析、导出报告。</p></div><ArrowUpRight size={18} /></a><a href="https://liu-xi71.github.io/liu-xi-evidence-analytics/"><BookOpen size={22} /><div><strong>复购运营台</strong><p>订单接入、客户分层、名单选择与策略验证。</p></div><ArrowUpRight size={18} /></a></div>
    </section>
    <details className="case-disclosure content-section"><summary>数据来源与展示范围</summary><p>{data.meta.data_boundary} 图中明确区分监控前后变化与实验组间比较。行级演示、结构分解示例与可编辑试算不代表企业生产记录。</p><Link className="text-link" to="/evidence">查看指标口径与证据 <ArrowRight size={15} /></Link></details>
  </>
}
