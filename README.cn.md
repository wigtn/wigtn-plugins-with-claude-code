<div align="center">

[English](README.md) | [한국어](README.ko.md) | [中文](README.cn.md)

# WIGTN Plugins

**一个插件。11 个智能体。从创意到生产。**

![Version](https://img.shields.io/badge/v0.1.15-Unified_Plugin-FF6B6B?style=for-the-badge)
![Agents](https://img.shields.io/badge/13-Agents-5A67D8?style=for-the-badge)
![Commands](https://img.shields.io/badge/5-Commands-38B2AC?style=for-the-badge)
![Skills](https://img.shields.io/badge/6-Skills-00D4AA?style=for-the-badge)
![Styles](https://img.shields.io/badge/20-Design_Styles-F59E0B?style=for-the-badge)

[![GitHub Stars](https://img.shields.io/github/stars/wigtn/wigtn-plugins?style=flat-square)](https://github.com/wigtn/wigtn-plugins/stargazers)
[![License](https://img.shields.io/badge/license-Apache_2.0-blue?style=flat-square)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/wigtn/wigtn-plugins?style=flat-square)](https://github.com/wigtn/wigtn-plugins/graphs/contributors)
[![Last Commit](https://img.shields.io/github/last-commit/wigtn/wigtn-plugins?style=flat-square)](https://github.com/wigtn/wigtn-plugins/commits/main)

</div>

---

## 为什么选择 WIGTN-Coding？

**没有这个插件：**
打开 Claude Code → 写一个模糊的提示 → 得到通用代码 → 花 30 分钟修复 → 重复。

**使用 WIGTN-Coding：**
运行 `/prd` → 获得结构化规格 → 11 个智能体并行构建 → 一次就产出生产级代码。

---

## 它做什么

WIGTN Plugins 是一个 Claude Code 插件。你描述想要构建的东西，14 个专业智能体处理其余一切 — 需求、架构、代码、审查、提交 — 全部并行执行。

```
/prd "基于 OAuth 的 SaaS 仪表盘"  →  30 秒内生成 PRD + 任务计划
/screen-spec dashboard             →  (有 UI 时) IA + 流程 + 屏幕规格 + 可点击 HTML 线框图
/implement --parallel              →  后端 + 前端 + AI + 运维团队同时构建
/auto-commit                       →  3 智能体审查，质量门禁，80+ 分自动提交
```

---

## 快速开始

```bash
# 安装
/plugin marketplace add wigtn/wigtn-plugins
/install wigtn-plugins

# 体验 — 这就是完整的工作流
/prd 现代设计的 AI 创业公司落地页
/implement ai-landing
/auto-commit
```

就这样。插件会处理 PRD 生成、4 类质量分析、架构决策、设计风格选择、并行构建、代码审查和提交。

---

## 流水线

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  /prd "基于 OAuth 的 SaaS 仪表盘"                                           │
│                                                                             │
│  1. 上下文收集 ──── 扫描项目结构、技术栈、package.json                       │
│  2. AskUserQuestion ── 规模等级？(Hobby / Startup / Growth / Enterprise)    │
│  3. PRD 生成 ────────── PRD_{feature}.md（7 个章节，Gherkin 用户故事）       │
│  4. 任务规划 ────────── PLAN_{feature}.md（阶段 + 任务）                     │
│                                                                             │
│  ┌─── prd-reviewer — 4 个对抗性视角 ──────────────────────────────────┐    │
│  │  Phase 0: 上下文收割（CLAUDE.md、代码模式、依赖）                    │    │
│  │  Phase 1: PRD 结构解析                                             │    │
│  │  Phase 2: ════════════ 4 个智能体并行执行 ═══════════               │    │
│  │           │ 完整性       │ 可行性        │ 安全性      │ 一致性    │   │    │
│  │           │ FR/NFR/边界  │ 技术栈适配    │ OWASP       │ 命名规范 │   │    │
│  │           │ 用例、重复    │ 变更影响范围   │ 认证/授权    │ PRD↔代码 │   │    │
│  │  Phase 3: 跨类别综合分析（复合风险检测）                              │    │
│  │  Phase 4: 质量门禁 ─── PASS / WARN / BLOCKED                      │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                          BLOCKED → 中止
                                    │ PASS / WARN
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  /implement ai-landing                                                      │
│                                                                             │
│  ┌─── DESIGN 阶段 ───────────────────────────────────────────────────┐     │
│  │  ═══════════════ 3 个智能体并行执行 ═══════════════                │     │
│  │  │ Agent A          │ Agent B              │ Agent C          │   │     │
│  │  │ PRD 加载 +       │ architecture-decision│ 项目扫描 +       │   │     │
│  │  │ 质量门禁         │ Mono/Modular/MSA     │ 差距分析         │   │     │
│  │  ══════════════════════════════════════════════════════════════    │     │
│  │                          │                                        │     │
│  │  团队分配 ─────────────── 文件模式匹配 → 团队决定                  │     │
│  │    api/, services/   → 后端                                       │     │
│  │    components/, app/ → 前端                                       │     │
│  │    ai/, llm/         → AI 服务                                    │     │
│  │    Dockerfile, CI/   → 运维                                       │     │
│  │                                                                   │     │
│  │  设计发现（仅前端，无现有风格时）──────────────────────────────     │     │
│  │    VS 技法：4 个问题 → 每种风格适合度 % → 选择                    │     │
│  │                                                                   │     │
│  │  ✋ 检查点：AskUserQuestion ── 继续 / 详细检查 / 取消             │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  ┌─── BUILD 阶段 ─── team-build-coordinator ─────────────────────────┐     │
│  │                                                                   │     │
│  │  Phase 0: 初始化 ─── SHARED_CONTEXT_{feature}.md + TodoWrite     │     │
│  │           上下文收割：采样现有代码 → 学习模式                       │     │
│  │                                                                   │     │
│  │  Phase 1: 基础构建（后端 + 依赖团队存在时）                        │     │
│  │           后端编写：DB 模型、共享类型、API 契约                     │     │
│  │                    ↓ 解锁其他团队                                  │     │
│  │                                                                   │     │
│  │  Phase 2: ════════════ 最多 4 个团队并行执行 ════════════          │     │
│  │           │ 后端            │ 前端           │ AI 服务    │ 运维  │     │
│  │           │ backend-       │ frontend-      │ ai-agent   │ gen  │     │
│  │           │ architect      │ developer      │            │ pur  │     │
│  │           │                │ + 风格指南     │            │      │     │
│  │           │ API、服务      │ 页面、组件     │ LLM、STT   │ CI   │     │
│  │           │ DB、中间件     │ 状态、样式     │ 提示词     │ CD   │     │
│  │           ════════════════════════════════════════════════════     │     │
│  │           ▲ 读取                   │ 写入                         │     │
│  │           └──── SHARED_CONTEXT ────┘                              │     │
│  │                                                                   │     │
│  │  Phase 3: 集成验证 ─── API 契约匹配、类型一致性、                  │     │
│  │           Phase 0 学习模式对比验证                                  │     │
│  │                                                                   │     │
│  │  Phase 4: 构建 & 测试 ─── typecheck + test + build                │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  /auto-commit                                                               │
│                                                                             │
│  Step 1: 分支策略                                                           │
│          功能分支 → 复用 │ main + PLAN → feat/<name>                        │
│                                                                             │
│  Step 2: 质量门禁                                                           │
│  ┌─── ≤5 文件且 LOW 影响半径：code-reviewer（单个）──────────────┐         │
│  │     6+ 文件或 MEDIUM/HIGH 影响半径 → 按类别拆分                │         │
│  │                                                                 │        │
│  │  Phase 0: 上下文收割（lint 配置、相邻代码）                      │        │
│  │  Phase 1: 影响范围分析 ─── 调用者、导入者、影响评分              │        │
│  │  Phase 2: ═══════════ 3 个智能体并行执行 ════════════           │        │
│  │           │ 可读性 +          │ 性能 +         │ 最佳实践     │        │
│  │           │ 可维护性          │ 可测试性       │ + 安全性      │        │
│  │           │     (40 分)       │   (40 分)      │   (20 分)     │        │
│  │           ══════════════════════════════════════════════════     │        │
│  │  Phase 3: 契约验证（调用者兼容性、边界、测试）                    │        │
│  │                                                                 │        │
│  │  分数合并：求和 + 契约违规扣分 + 安全覆盖                        │        │
│  │  安全关键 → 上限 59 分 → FAIL                                   │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                             │
│  ┌────────────────────────────────────────┐                                 │
│  │ ≥ 80 (PASS)  → Step 4                 │                                 │
│  │ 60-79 (WARN) → code-formatter 自动修复 → 重新评估                       │
│  │ < 60 (FAIL)  → 阻止                   │                                 │
│  └────────────────────────────────────────┘                                 │
│                                                                             │
│  Step 4: 提交信息 ─── <type>(<scope>): <subject> + 质量分数                │
│  ✋ 检查点：AskUserQuestion ── PR / Draft PR / 仅提交 / 取消               │
│  Step 5: git commit → git push -u → gh pr create                           │
└─────────────────────────────────────────────────────────────────────────────┘

共享内存（3 层）：
  Layer 1 — MEMORY.md ─────────── 跨会话持久化的项目规范
  Layer 2 — SHARED_CONTEXT ────── 会话范围 API 契约、类型、模式
  Layer 3 — TodoWrite ─── 对话内按团队追踪任务
```

每个步骤尽可能并行运行。完整流水线：~6 分钟（串行 ~20 分钟）。

---

## 命令

| 命令 | 功能 |
|------|------|
| `/prd <功能>` | 根据功能创意生成 PRD + 分阶段任务计划（针对 UI 功能新增 User Roles、Page State Matrix、User Flow 章节） |
| `/screen-spec <功能>` | 可选 UI 阶段：IA + 用户流程 + 屏幕规格 + 可点击 HTML 线框图 + Dev Handoff。灰度 + 语义色 lo-fi 线框图（风格决策在 `/implement` 阶段） |
| `/implement <功能>` | 自动并行模式检测，进行设计 + 构建（如存在 screen-spec 产物则作为输入使用） |
| `/auto-commit` | 3 智能体并行审查 → 质量门禁 → 提交 + PR |
| `/review-pr <PR>` | 在终端审查 GitHub PR：diff 分析、质量评分、行内评论 |

---

<details>
<summary><b>智能体（11 个）</b> — 点击展开</summary>

### 协调器

| 智能体 | 角色 |
|--------|------|
| `team-build-coordinator` | 并行分配后端、前端、AI、运维团队 |
| `architecture-decision` | MSA vs 单体 vs 模块化单体 |

### 开发者

| 智能体 | 角色 |
|--------|------|
| `frontend-developer` | React 19、Next.js 16+、20 种设计风格 |
| `backend-architect` | API 设计、数据库架构、后端模式 |
| `mobile-developer` | React Native / Expo、原生模块 |
| `ai-agent` | WhisperX STT、OpenAI/Anthropic 集成 |

### 质量

| 智能体 | 角色 |
|--------|------|
| `code-reviewer` | 5 个类别 100 分制质量评分 |
| `pr-reviewer` | GitHub PR diff 审查、100 分制评分、行内审查评论（用于 `/review-pr`） |
| `prd-reviewer` | 在完整性、可行性、安全性、一致性中发现缺口 |
| `code-formatter` | 多语言自动格式化和 lint 修复 |
| `design-discovery` | 基于 VS 技法的 Web/Mobile 风格推荐 |

</details>

<details>
<summary><b>技能（6 个）</b> — 点击展开</summary>

| 技能 | 提供内容 |
|------|---------|
| `code-review-levels` | 深度审查（Level 3：调用链、边界情况、并发）和架构审查（Level 4：SOLID、层违规、可扩展性） |
| `design-system-reference` | 20 个风格指南 — 排版、色彩、组件、动效、反模式。与 design-discovery 协同进行上下文感知推荐 |
| `handdrawn-diagram` | 通过 Mermaid `look:handDrawn` 生成手绘（草图）风格的架构/流程图，输出可提交的 SVG + PNG。在 README、GitHub、Devpost、幻灯片上渲染一致 |
| `screen-spec` | 从 PRD 生成 5 种 UI 产物 — IA、用户流程、屏幕规格、可点击 Wireframe HTML、Dev Handoff。灰度 + 语义色 lo-fi 线框图（风格在 `/implement` 决定）。由 `/screen-spec` 调用 |
| `team-memory-protocol` | 并行构建中跨智能体共享上下文（SHARED_CONTEXT）管理 |
| `wigtn-ppt` | 基于品牌令牌生成 WIGTN 品牌 HTML 演示文稿（Light/Dark 主题，无需模板）。每张幻灯片带签名紫点，缺少 logo 资源时回退到 CSS/SVG 字标 |

</details>

<details>
<summary><b>设计风格（20 种）</b> — 点击展开</summary>

每个风格指南涵盖设计哲学、排版、布局、色彩、组件、动效和反模式检查清单。

| 风格 | 氛围 |
|------|------|
| Editorial | 杂志布局，强烈衬线字体 |
| Brutalist | 原始、大胆、非常规 |
| Glassmorphism | 模糊透明的磨砂玻璃效果 |
| Swiss Minimal | 网格设计，排版核心 |
| Neomorphism | Soft UI，内凹/外凸阴影 |
| Bento Grid | 卡片网格（Apple 风格） |
| Dark Mode First | 从零开始的暗色界面 |
| Minimal Corporate | 简洁商务美学 |
| Retro Pixel | CRT 效果，等宽字体，终端怀旧 |
| Organic Shapes | 气泡形状，自然曲线，大地色调 |
| Maximalist | 大胆排版，浓烈色彩，层叠 |
| 3D Immersive | CSS 3D 变换，视差，深度 |
| Liquid Glass | 流体半透明玻璃，动态反射 |
| Claymorphism | 柔和 3D 粘土，粉彩色调 |
| Minimalism | 极致简约，留白驱动 |
| Neobrutalism | 彩色强调，粗边框 |
| Skeuomorphism | 逼真质感，物理隐喻 |
| Aurora / Gradient Mesh | 网格渐变，环境光晕，空灵 |
| Terminal / Hacker | 等宽字体驱动，信息密集，语义色彩 |
| Kinetic Typography | 滚动驱动文字动画，拆分揭示 |

`design-discovery` 智能体使用 VS（Verbalized Sampling）技法为项目推荐最佳风格。

</details>

<details>
<summary><b>钩子（4 个）</b> — 点击展开</summary>

| 钩子 | 触发器 | 功能 |
|------|--------|------|
| 危险命令拦截 | `Bash` PreToolUse | 拦截 `rm -rf /`、`git push --force`、`DROP TABLE` |
| 流水线完成 | Stop | 推送前提醒审查 |
| 前端格式化 | `Write\|Edit` PostToolUse | 提醒对 `.tsx`、`.jsx`、`.css` 运行 prettier/eslint |
| 后端模式合规 | `Write\|Edit` PostToolUse | 检查 `.ts`、`.py`、`.go` 的错误处理、验证、日志 |

</details>

---

## 场景

<details>
<summary><b>从零开始的全栈 SaaS</b></summary>

```bash
/prd 带看板和团队协作的项目管理工具
# → 4 智能体分析："缺失：实时同步、角色权限"

/implement --parallel project-management
# 后端：API 端点、Prisma 模型、认证中间件
# 前端：看板、团队视图、仪表盘
# 运维：Dockerfile、GitHub Actions CI/CD

/auto-commit
# 3 审查者 → 87/100 → 自动提交
```

</details>

<details>
<summary><b>React Native 移动应用</b></summary>

```bash
/prd 带运动记录、进度图表、Apple Health 同步的健身追踪器

/implement fitness-tracker
# Expo Router + Zustand + MMKV + React Query
# 生物认证、触觉反馈、离线同步
```

</details>

<details>
<summary><b>设计驱动的落地页</b></summary>

```bash
/prd 现代设计的 AI 创业公司落地页

/implement ai-landing
# design-discovery 激活 → 推荐 Glassmorphism 或 Liquid Glass
# 前端团队构建 Hero、Features、Pricing、CTA — 应用选定风格
```

</details>

<details>
<summary><b>后端 API + AI 功能</b></summary>

```bash
/prd 带 WhisperX STT 和 LLM 摘要的转录服务

/implement --parallel transcription-service
# 后端 → API + DB + 认证
# AI → WhisperX + OpenAI/Anthropic 模式
# 前端 → 上传 UI + 转录查看器
```

</details>

---

## 技术栈

| 领域 | 技术 |
|------|------|
| 前端 | React 19、Next.js 16+、Tailwind CSS、Radix UI |
| 后端 | NestJS、Express、FastAPI、Prisma、Drizzle |
| 移动端 | React Native 0.73+、Expo SDK 52+ |
| AI | WhisperX、OpenAI GPT、Anthropic Claude |
| DevOps | Docker、Kubernetes、GitHub Actions |
| 设计 | 20 种风格体系、VS 基础发现、HIG、MD3 |

---

## 贡献

```bash
git checkout -b feature/amazing-skill
# 编写更改
git commit -m 'feat: Add amazing skill'
git push origin feature/amazing-skill
# 创建 PR
```

---

## 许可证

Apache License 2.0 — 参阅 [LICENSE](LICENSE)。

---

<div align="center">

**Built by [WIGTN Crew](https://github.com/wigtn)**

5 位 AI 工程师。我们不研究 AI — 我们直接发布。

</div>
