# 刘希｜增长与实验

**用户增长与新用户留存：从业务问题，到指标诊断、策略验证和价值评估。**

[在线查看](https://liu-xi71.github.io/liu-xi-growth-analytics-portfolio/) · [全部作品](https://liu-xi71.github.io/liu-xi-growth-analytics-portfolio/collection.html) · [中文使用指南](README_zh.md)

[![CI](https://github.com/liu-XI71/liu-xi-growth-analytics-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/liu-XI71/liu-xi-growth-analytics-portfolio/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-0f766e.svg)](LICENSE)

![业务总览](docs/assets/overview.png)

## 先看什么

本作品聚焦两段实习中的业务判断，强调分析方法与个人参与，不以技术组件数量作为展示重点。

| 浏览顺序 | 页面 | 重点 |
|---|---|---|
| 1 | [业务总览](https://liu-xi71.github.io/liu-xi-growth-analytics-portfolio/) | 两个场景如何共用一套判断标准 |
| 2 | [老带新案例](https://liu-xi71.github.io/liu-xi-growth-analytics-portfolio/#/cases/referral) | 邀请链路断点、产品反馈、页面实验与首月价值 |
| 3 | [新用户留存案例](https://liu-xi71.github.io/liu-xi-growth-analytics-portfolio/#/cases/retention) | 用户结构、路径排查、标杆行为与引导实验 |
| 4 | [指标与实验方法](https://liu-xi71.github.io/liu-xi-growth-analytics-portfolio/#/methods) | 六项指标定义与七步实验流程 |

每个案例均按“业务目标 → 指标体系 → 诊断与策略 → 实验评估 → 决策与沉淀”展开，支持下载 Markdown 案例摘要。

## 两个业务案例

| 场景 | 业务问题 | 分析与策略 | 已公开结果 |
|---|---|---|---|
| 字节跳动 · 红果 · 老带新 | 外部拉新供给承压；激励升级后邀请点击率约 21% → 17% | 看板定位邀请动作，结合产品与用研反馈简化界面、前置入口，再进行随机实验 | 实验对照 17% 与 23.5%，提升 6.5 个百分点；两周、总样本约 700 万，p < 0.05；首月价值/激励成本 2.18，同口径外投 1.90 |
| 小红书 · 新用户留存 | 投放新增用户次 7 日内留存 48% → 41% | 用户分层识别设备结构压力；路径未同步恶化；高频高时标杆的关注渗透约为非标杆 2.5 倍；实验评估退出页主页与关注引导 | 两周、总样本约 30 万，次 7 日内留存显著提升，p < 0.05；组间绝对留存率未公开，不报告效果量 |

个人在 mentor 带领下参与指标梳理、看板监测、诊断分析、策略反馈与实验评估。本仓库为个人方法与工具沉淀，不是实习期间上线的企业生产系统。

## 业务判断与可复用方法

- **区分结构与表现**：总体率是分层占比与组内表现的加权结果；缺少分期占比时，不将整体变化全部归因于某个分层。
- **区分线索与因果**：标杆行为用于生成策略假设；随机实验评估完整产品改动。
- **区分局部与最终指标**：邀请点击支持机制判断，最终仍需观察有效新增与新用户质量。
- **区分显著与价值**：p 值、效果量、业务目标、观察窗口和价值护栏共同支持决策。
- **区分监控与实验**：页面将版本前后变化与随机实验组间差异分别绘图，避免混用对比口径。

## 支持工具

侧栏“分析工具与案例资料”保留可操作的辅助页面，原有网址继续可用：

| 页面 | 功能 |
|---|---|
| 分析链路 `#/analysis` | 选择问题，按口径、计算、证据、假设与行动逐步展开 |
| 案例周报 `#/weekly` | 查看不同案例阶段，导出 Markdown 周报示例 |
| 分步回放 `#/replay` | 依次回放完整分析过程 |
| 实验试算 `#/experiment` | 样本量、周期、Hash、SRM、两比例检验与价值条件 |
| 指标口径与证据 `#/evidence` | 筛选指标定义、计算依据及适用范围 |

试算采用可编辑演示输入；A/A、实际组内人数、SRM 和人群均衡的真实结果未披露，不默认作为历史通过记录。

## 与另外两项工具的分工

- 本项目 **增长与实验**：只负责两段实习的完整业务判断链路。
- [CSV分析工作台](https://liu-xi71.github.io/liu-xi-csv-analyst/)：导入兼容 CSV、保存口径、新数据复算与报告导出。
- [复购运营台](https://liu-xi71.github.io/liu-xi-evidence-analytics/)：订单接入、客户分群、候选名单与复购策略验证。

## 运行方式

在线页面无需安装、登录或模型密钥。压缩包内提供完整源码；源码中的 `web/index.html` 不能直接双击运行。

本地完整前后端与数据库链路使用 Docker Desktop：

```bash
docker compose up --build
```

启动后打开前端 `http://localhost:8501`，API 文档位于 `http://localhost:8000/docs`。停止时运行 `docker compose down`。

开发与验证：

```bash
python -m pip install -e ".[dev]"
python -m scripts.export_copilot
python -m pytest
cd web
npm ci
npm test
npm run lint
npm run build
```

## 数据与文档

案例关键变化来自去标识化经历复盘。行级明细、结构分解示例和实验试算用于演示计算，不是雇主生产数据。项目保留必要的数据说明，不包含内部表名、内部代码、用户信息或系统凭证。

- [老带新案例说明](docs/case-study-referral.md)
- [新用户留存案例说明](docs/case-study-retention.md)
- [实验设计与统计说明](docs/experimentation-guide.md)
- [指标口径字典](docs/metric-dictionary.md)
- [数据说明](docs/data-card.md)
- [三分钟浏览指南](docs/portfolio-review-guide_zh.md)
- [架构与运行链路](docs/architecture.md)

v1.2.0 · 代码采用 [MIT License](LICENSE)。项目为刘希个人作品，不代表字节跳动、小红书或其他公司的官方系统，详见 [DISCLAIMER.md](DISCLAIMER.md)。
