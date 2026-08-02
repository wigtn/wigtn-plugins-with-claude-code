<div align="center">

[English](README.md) | [한국어](README.ko.md) | [中文](README.cn.md)

# WIGTN Plugins

**One plugin. 12 agents. From idea to production.**

![Version](https://img.shields.io/badge/v0.1.14-Unified_Plugin-FF6B6B?style=for-the-badge)
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

## Why WIGTN-Coding?

**Without this plugin:**
You open Claude Code → write a vague prompt → get generic code → spend 30 min fixing → repeat.

**With WIGTN-Coding:**
You run `/prd` → get a structured spec → 12 agents build it in parallel → ship production-ready code on the first try.

---

## What it does

WIGTN Plugins is a Claude Code plugin. You describe what you want to build, and 14 specialized agents handle the rest — requirements, architecture, code, review, commit — all in parallel.

```
/prd "SaaS dashboard with OAuth"  →  PRD + task plan in 30 seconds
/screen-spec dashboard            →  (if UI) IA + flow + screen spec + clickable wireframe HTML
/implement --parallel             →  Backend + Frontend + AI + Ops teams build simultaneously
/auto-commit                      →  3-agent review, quality gate, auto-commit if 80+
```

---

## Quick Start

```bash
# Install
/plugin marketplace add wigtn/wigtn-plugins
/install wigtn-plugins

# Try it — this is the full workflow
/prd landing page for an AI startup with modern design
/implement ai-landing
/auto-commit
```

That's it. The plugin handles PRD generation, 4-category quality analysis, architecture decisions, design style selection, parallel build, code review, and commit.

---

## The Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  /prd "SaaS dashboard with OAuth"                                          │
│                                                                             │
│  1. Context Gathering ─── scan project structure, tech stack, package.json  │
│  2. AskUserQuestion ───── Scale Grade? (Hobby / Startup / Growth / Enterprise) │
│  3. PRD Generation ────── PRD_{feature}.md  (7 sections, Gherkin stories)  │
│  4. Task Planning ─────── PLAN_{feature}.md (phases + tasks)               │
│                                                                             │
│  ┌─── prd-reviewer — 4 adversarial lenses ────────────────────────────┐    │
│  │  Phase 0: Context Harvest (CLAUDE.md, code patterns, deps)         │    │
│  │  Phase 1: PRD Structure Parsing                                    │    │
│  │  Phase 2: ════════════ 4 AGENTS IN PARALLEL ═══════════            │    │
│  │           │ Completeness │ Feasibility │ Security │ Consistency │   │    │
│  │           │ FR/NFR/edge  │ stack fit   │ OWASP    │ naming/arch │   │    │
│  │           │ cases, dups  │ blast radius│ auth/z   │ PRD↔code    │   │    │
│  │  Phase 3: Cross-Category Synthesis (compound risks)                │    │
│  │  Phase 4: Quality Gate ─── PASS / WARN / BLOCKED                   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                          BLOCKED → stop
                                    │ PASS / WARN
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  /implement ai-landing                                                      │
│                                                                             │
│  ┌─── DESIGN PHASE ──────────────────────────────────────────────────┐     │
│  │  ═══════════════ 3 AGENTS IN PARALLEL ═══════════════             │     │
│  │  │ Agent A          │ Agent B              │ Agent C          │   │     │
│  │  │ PRD load +       │ architecture-decision│ Project scan +   │   │     │
│  │  │ quality gate     │ Mono/Modular/MSA     │ gap analysis     │   │     │
│  │  ══════════════════════════════════════════════════════════════    │     │
│  │                          │                                        │     │
│  │  Team Allocation ─────── pattern match files → teams              │     │
│  │    api/, services/   → Backend                                    │     │
│  │    components/, app/ → Frontend                                   │     │
│  │    ai/, llm/         → AI Server                                  │     │
│  │    Dockerfile, CI/   → Ops                                        │     │
│  │                                                                   │     │
│  │  Design Discovery (Frontend only, if no existing style) ────────  │     │
│  │    VS technique: 4 questions → suitability % per style → select   │     │
│  │                                                                   │     │
│  │  ✋ CHECKPOINT: AskUserQuestion ── proceed / review / cancel      │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  ┌─── BUILD PHASE ─── team-build-coordinator ────────────────────────┐     │
│  │                                                                   │     │
│  │  Phase 0: Setup ─── SHARED_CONTEXT_{feature}.md + TodoWrite      │     │
│  │           Context Harvest: sample existing code → learn patterns   │     │
│  │                                                                   │     │
│  │  Phase 1: Foundation (if Backend + dependents exist)              │     │
│  │           Backend writes: DB schema, shared types, API contracts   │     │
│  │                    ↓ unblocks other teams                         │     │
│  │                                                                   │     │
│  │  Phase 2: ════════════ UP TO 4 TEAMS IN PARALLEL ════════════     │     │
│  │           │ BACKEND        │ FRONTEND       │ AI SERVER    │ OPS │     │
│  │           │ backend-       │ frontend-      │ ai-agent     │ gen │     │
│  │           │ architect      │ developer      │              │ pur │     │
│  │           │                │ + style guide  │              │     │     │
│  │           │ API, services  │ pages, comps   │ LLM, STT    │ CI  │     │
│  │           │ DB, middleware │ state, styling │ prompts      │ CD  │     │
│  │           ════════════════════════════════════════════════════     │     │
│  │           ▲ reads                  │ writes                       │     │
│  │           └──── SHARED_CONTEXT ────┘                              │     │
│  │                                                                   │     │
│  │  Phase 3: Integration ─── API contract match, type consistency,   │     │
│  │           pattern verification vs Phase 0 learned patterns        │     │
│  │                                                                   │     │
│  │  Phase 4: Build & Test ─── typecheck + test + build               │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  /auto-commit                                                               │
│                                                                             │
│  Step 1: Branch Strategy                                                    │
│          on feature branch → reuse │ on main + PLAN → feat/<name>          │
│                                                                             │
│  Step 2: Quality Gate                                                       │
│  ┌─── ≤5 files & LOW blast radius: code-reviewer (single) ────────┐        │
│  │     6+ files or MEDIUM/HIGH blast radius → split by category    │        │
│  │                                                                 │        │
│  │  Phase 0: Context Harvest (lint configs, adjacent code)         │        │
│  │  Phase 1: Blast Radius ─── callers, importers, impact score     │        │
│  │  Phase 2: ═══════════ 3 AGENTS IN PARALLEL ════════════         │        │
│  │           │ Readability +     │ Performance +  │ Best Practices │        │
│  │           │ Maintainability   │ Testability    │ + Security     │        │
│  │           │     (40 pts)      │   (40 pts)     │   (20 pts)     │        │
│  │           ══════════════════════════════════════════════════     │        │
│  │  Phase 3: Contract Verification (callers, boundaries, tests)    │        │
│  │                                                                 │        │
│  │  Score Merge: sum + contract penalty + security override        │        │
│  │  Security Critical → cap at 59 → FAIL                          │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                             │
│  ┌────────────────────────────────────────┐                                 │
│  │ ≥ 80 (PASS)  → Step 4                 │                                 │
│  │ 60-79 (WARN) → code-formatter auto-fix → re-evaluate                   │
│  │ < 60 (FAIL)  → blocked                │                                 │
│  └────────────────────────────────────────┘                                 │
│                                                                             │
│  Step 4: Commit Message ─── <type>(<scope>): <subject> + quality score     │
│  ✋ CHECKPOINT: AskUserQuestion ── PR / Draft PR / Commit only / Cancel    │
│  Step 5: git commit → git push -u → gh pr create                           │
└─────────────────────────────────────────────────────────────────────────────┘

Shared Memory (3 layers):
  Layer 1 — MEMORY.md ─────────── persistent cross-session conventions
  Layer 2 — SHARED_CONTEXT ────── session-scoped API contracts, types, patterns
  Layer 3 — TodoWrite ─── in-conversation task tracking per team
```

Each step runs in parallel where possible. Full pipeline: ~6 min (vs ~20 min sequential).

---

## Commands

| Command | What it does |
|---------|-------------|
| `/prd <feature>` | Generate PRD + phased task plan from a feature idea (now includes User Roles, Page State Matrix, User Flow sections for UI features) |
| `/screen-spec <feature>` | Optional UI gate: IA + User Flow + Screen Spec + clickable HTML wireframe + Dev Handoff. Lo-fi wireframe (grayscale + semantic colors); style is decided later at `/implement` |
| `/implement <feature>` | Design + build with automatic parallel team dispatch (consumes screen-spec output if present) |
| `/auto-commit` | 3-agent parallel review → quality gate → commit + PR |
| `/review-pr <PR>` | Review a GitHub PR from terminal: diff analysis, quality score, inline comments |

---

<details>
<summary><b>Agents (13)</b> — click to expand</summary>

### Coordinators

| Agent | Role |
|-------|------|
| `team-build-coordinator` | Dispatches Backend, Frontend, AI, Ops teams in parallel |
| `architecture-decision` | MSA vs Monolithic vs Modular Monolith |

### Developers

| Agent | Role |
|-------|------|
| `frontend-developer` | React 19, Next.js 16+, 20 design styles |
| `backend-architect` | API design, database schema, backend patterns |
| `mobile-developer` | React Native / Expo, native modules |
| `ai-agent` | WhisperX STT, OpenAI/Anthropic integration |

### Quality

| Agent | Role |
|-------|------|
| `code-reviewer` | 100-point scoring across 5 categories |
| `pr-reviewer` | GitHub PR diff review, 100-point scoring, inline review comments (used by `/review-pr`) |
| `prd-reviewer` | Finds gaps across completeness, feasibility, security, consistency |
| `code-formatter` | Multi-language auto-formatting and lint fixes |
| `design-discovery` | VS-based style recommendation for Web and Mobile |

</details>

<details>
<summary><b>Skills (6)</b> — click to expand</summary>

| Skill | What it provides |
|-------|-----------------|
| `code-review-levels` | Deep review (Level 3: call chains, edge cases, concurrency) and architecture review (Level 4: SOLID, layer violations, scalability) |
| `design-system-reference` | 20 style guides with typography, color, components, motion, and anti-patterns. Works with design-discovery for context-aware recommendations |
| `handdrawn-diagram` | Generates a hand-drawn (sketch-style) architecture or flow diagram as committable SVG + PNG via Mermaid `look:handDrawn`. Renders identically on README, GitHub, Devpost, and slides |
| `screen-spec` | Generates 5 UI artifacts from PRD — IA, User Flow, Screen Spec, clickable Wireframe HTML, Dev Handoff. Lo-fi wireframe (grayscale + semantic colors); style decisions deferred to `/implement`. Invoked by `/screen-spec` |
| `team-memory-protocol` | SHARED_CONTEXT management for cross-agent coordination during parallel builds |
| `wigtn-ppt` | Generates a WIGTN-brand HTML presentation (Light/Dark themes) from brand tokens — no template needed. Signature purple dot on every slide, with a CSS/SVG wordmark fallback when logo assets are absent |

</details>

<details>
<summary><b>Design Styles (20)</b> — click to expand</summary>

Each style guide covers philosophy, typography, layout, color, components, motion, and an anti-pattern checklist.

| Style | Vibe |
|-------|------|
| Editorial | Magazine layouts, strong serif typography |
| Brutalist | Raw, bold, unconventional |
| Glassmorphism | Frosted glass, blur, transparency |
| Swiss Minimal | Grid-based, typography-focused |
| Neomorphism | Soft UI, inset/outset shadows |
| Bento Grid | Card-based grid (Apple-inspired) |
| Dark Mode First | Dark interfaces from the ground up |
| Minimal Corporate | Clean professional aesthetic |
| Retro Pixel | CRT effects, monospace, terminal nostalgia |
| Organic Shapes | Blobs, natural curves, earthy tones |
| Maximalist | Bold type, intense colors, layered |
| 3D Immersive | CSS 3D transforms, parallax, depth |
| Liquid Glass | Fluid translucent glass, dynamic reflections |
| Claymorphism | Soft 3D clay elements, pastel tones |
| Minimalism | Extreme simplicity, whitespace-driven |
| Neobrutalism | Colorful accents, bold borders |
| Skeuomorphism | Realistic textures, physical metaphors |
| Aurora / Gradient Mesh | Mesh gradients, ambient glow, ethereal |
| Terminal / Hacker | Monospace-driven, information-dense, semantic color |
| Kinetic Typography | Scroll-driven text animation, split reveals |

The `design-discovery` agent recommends the best style for your project context using VS (Verbalized Sampling).

</details>

<details>
<summary><b>Hooks (4)</b> — click to expand</summary>

| Hook | Trigger | What it does |
|------|---------|-------------|
| Dangerous Command Blocker | `Bash` PreToolUse | Blocks `rm -rf /`, `git push --force`, `DROP TABLE` |
| Pipeline Completion | Stop | Reminds to review before pushing |
| Frontend Formatting | `Write\|Edit` PostToolUse | Reminds prettier/eslint for `.tsx`, `.jsx`, `.css` |
| Backend Pattern Compliance | `Write\|Edit` PostToolUse | Checks error handling, validation, logging for `.ts`, `.py`, `.go` |

</details>

---

## Scenarios

<details>
<summary><b>Full-Stack SaaS from scratch</b></summary>

```bash
/prd project management tool with kanban boards and team collaboration
# → 4-agent analysis catches: "Missing: real-time sync, role permissions"

/implement --parallel project-management
# Backend: API endpoints, Prisma schema, auth middleware
# Frontend: Kanban board, team views, dashboard
# Ops: Dockerfile, GitHub Actions CI/CD

/auto-commit
# 3 reviewers → 87/100 → auto-commit
```

</details>

<details>
<summary><b>Mobile app with React Native</b></summary>

```bash
/prd fitness tracker with workout logging, progress charts, Apple Health sync

/implement fitness-tracker
# Expo Router + Zustand + MMKV + React Query
# Biometric auth, haptic feedback, offline sync
```

</details>

<details>
<summary><b>Design-driven landing page</b></summary>

```bash
/prd AI startup landing page with modern design

/implement ai-landing
# design-discovery activates → recommends Glassmorphism or Liquid Glass
# Frontend team builds Hero, Features, Pricing, CTA with chosen style
```

</details>

<details>
<summary><b>Backend API + AI features</b></summary>

```bash
/prd transcription service with WhisperX STT and LLM summarization

/implement --parallel transcription-service
# Backend → API + DB + auth
# AI → WhisperX + OpenAI/Anthropic patterns
# Frontend → Upload UI + transcription viewer
```

</details>

---

## Tech Stack

| Domain | Technologies |
|--------|-------------|
| Frontend | React 19, Next.js 16+, Tailwind CSS, Radix UI |
| Backend | NestJS, Express, FastAPI, Prisma, Drizzle |
| Mobile | React Native 0.73+, Expo SDK 52+ |
| AI | WhisperX, OpenAI GPT, Anthropic Claude |
| DevOps | Docker, Kubernetes, GitHub Actions |
| Design | 20 style systems, VS-based discovery, HIG, MD3 |

---

## Contributing

```bash
git checkout -b feature/amazing-skill
# make changes
git commit -m 'feat: Add amazing skill'
git push origin feature/amazing-skill
# open PR
```

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).

---

<div align="center">

**Built by [WIGTN Crew](https://github.com/wigtn)**

5 AI engineers. We don't study AI — we ship it.

</div>
