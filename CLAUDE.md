# WIGTN Claude Code Plugin Tools

## Project Overview

A unified Claude Code plugin enabling AI-powered Vibe Coding: idea to production with minimal friction.

**Version**: 0.1.15
**License**: Apache-2.0
**Repository**: https://github.com/wigtn/wigtn-plugins

## Architecture

```
wigtn-plugins/
├── .claude-plugin/           # Marketplace metadata
├── plugins/
│   └── wigtn-plugins/         # Unified plugin: 12 agents, 5 commands, 6 skills, 20 design styles
│       ├── .claude-plugin/   # Plugin metadata
│       ├── agents/           # 12 agent definitions
│       ├── commands/         # 5 commands (/prd, /screen-spec, /implement, /auto-commit, /review-pr)
│       ├── skills/           # 6 skills (code-review-levels, design-system-reference, handdrawn-diagram, screen-spec, team-memory-protocol, wigtn-ppt)
│       └── hooks/            # Hooks configuration
├── CLAUDE.md                 # This file
├── README.md                 # English docs
└── README.ko.md              # Korean docs
```

### Plugin Structure

```
plugins/wigtn-plugins/
├── .claude-plugin/plugin.json  # Plugin metadata
├── agents/                     # Agent definitions (.md)
├── commands/                   # User-invocable commands (.md)
├── skills/                     # Skills with SKILL.md + reference files
└── hooks/hooks.json            # Hooks configuration
```

## Pipeline Flow

```
/prd <feature>
  → PRD.md + PLAN_{feature}.md  (§2.3 User Roles, §5.4 Pages, §5.4.1 State Matrix, §5.5 User Flow 포함)
    → digging (`prd-reviewer`: 4-lens 적대적 분석 + completeness-critic; 조건부 external-grounding)
      → /screen-spec <feature>  (FE 페이지가 있을 때만; IA / Flow / Spec / Wireframe / Handoff 5종 생성)
        → /implement (triage → quick-fix: 경량 단일 에이전트 | feature/greenfield: DESIGN → BUILD
                       → [Frontend? → design-discovery → style select]
                       → [Linear 연동? → Epic/하위 이슈 등록 → 이슈 단위 순차 BUILD | 미연동? → BUILD team parallel])
          → /auto-commit (변경 규모에 비례한 리뷰 → findings 롤업 게이트 → commit)
```

`/implement`는 진입 시 **작업 규모 triage**로 라우팅한다: `quick-fix`(버그픽스·소규모 수정)는 디깅·팀빌드·별도 verifier를 스킵하고 단일 에이전트가 인라인 구현(설계-구현 분리·커밋 확인은 유지). `feature`/`greenfield`만 풀 DESIGN→BUILD 파이프라인. `--quick`/`--full`로 강제 가능.

`/screen-spec`은 PRD §5.4에 `Has FE Components: Yes` 행이 1개+ 있을 때만 실행. 백엔드/API 전용 PRD에서는 스킵하고 바로 `/implement`로 진행.

PRD 리뷰(digging)는 4렌즈 전부 **코드베이스 grounding**만 하던 것에 더해, 조건부 **external-grounding**을 수행한다(deep-research 패턴 축소 이식). PRD가 외부 세계에 의존하는 주장(3rd-party API 동작·가격·한도, 라이브러리 능력, 규제, 경쟁사)을 담고 Scale Grade ≥ Startup 또는 3rd-party 연동 ≥1일 때만 발화 — 그 주장만 골라 WebSearch로 `confirmed/contradicted/unverifiable` 태깅하고, **모순 주장만 3표 적대 재검증**해 Feasibility/Security의 Critical 씨앗으로 넣는다. Hobby·refactor·외부주장 0·WebSearch 불가 시 무마찰 스킵(웹 호출 0). 정의는 `prd-reviewer`에 **자립적으로** 들어 있다(위임 없음).

`/implement`는 Step 0.5에서 이슈 트래커(Linear MCP, `mcp__linear__*`)를 감지한다. 연동 시 Step 6에서 1회 확인 후 PRD의 FR을 하위 이슈로(의존성은 FR 테이블 기준) 등록하고 의존성 순서대로 이슈 단위 순차 개발한다. 미연동/`--no-tracker`이면 기존 원큐 플로우. 이슈 트래커는 보조 기능이라 연동 실패 시 원큐로 graceful degradation.

### Quality Gate (findings 롤업 — 결정론적)

게이트는 합산 점수가 아니라 **findings 롤업**으로 정한다(같은 코드가 78/85로 튀는 노이즈 제거). 100점 점수는 참고 표시값.

- **FAIL** (커밋 차단): critical ≥1 (high/med confidence)
- **WARN** (auto-fix 후 재평가): critical 0 AND (major ≥1 OR minor ≥5)
- **PASS** (커밋): critical 0 AND major 0 AND minor <5
- **Security Critical**: critical의 부분집합 → 항상 FAIL (zero-tolerance, no score-cap hack)
- **정밀도**: major+ finding은 게이트 반영 전 adversarial refute 1회로 오탐 강등
- **하드 게이트 (hook 강제)**: 게이트가 프롬프트라 컨텍스트가 차면 스킵될 수 있으므로, `hooks.json`의 PreToolUse가 `git commit`을 가로채 강제한다. 롤업 PASS 시 `/auto-commit`이 repo 루트(`git rev-parse --show-toplevel`)의 `.wigtn/gate-pass`(mtime = PASS 시각)를 기록하고, 커밋 메시지에 `Quality Score:` 신호가 있는데 30분 내 아티팩트가 없으면 hook이 커밋을 **차단(exit 2)**한다. 수동 커밋(신호 없음)·`--no-review`(신호 제거)는 무마찰. hook·auto-commit 모두 toplevel 기준이라 하위 디렉토리 cwd에서도 일치한다.
- **객관 체크 게이트 (기본-on, PASS 날조 방어)**: gate-pass는 모델이 쓰는 아티팩트라 리뷰 날조 시 함께 써질 수 있다. Step 3.5가 빠른 검증 명령(`package.json`의 `typecheck`/`lint`, 또는 `tsconfig.json`)을 감지하면 `.wigtn/checks.sh`를 **자동 생성**하고, hook이 커밋 직전 **직접 실행**해 non-zero면 차단 — 모델이 못 꾸미는 exit code에 게이트를 바인딩("리뷰가 좋았음" → "객관 검증 통과"). 감지 실패 시 무마찰. `.wigtn/checks.sh` 편집(전체 테스트 추가)·삭제로 커스터마이즈/opt-out.

## Conventions

### Skill Frontmatter

```yaml
---
name: skill-name
description: Brief description of the skill
disable-model-invocation: true    # Optional: for heavy skills (600+ lines)
allowed-tools: Read, Write, Edit  # Optional: restrict available tools
context: fork                     # Optional: run in isolated subagent
agent: general-purpose            # Optional: agent type for fork
---
```

### Command Frontmatter

```yaml
---
argument-hint: "<feature name>"   # Optional: autocomplete hint for $ARGUMENTS
---
```

### Hooks

Hooks are defined in `plugins/wigtn-plugins/hooks/hooks.json` and follow the Claude Code hooks schema.

## Key Paths

| Path | Purpose |
|------|---------|
| `plugins/wigtn-plugins/skills/code-review-levels/` | Deep review (Level 3) + architecture review (Level 4) |
| `plugins/wigtn-plugins/skills/design-system-reference/` | 20 design style guides + common patterns |
| `plugins/wigtn-plugins/skills/design-system-reference/styles/` | Individual style guide files |
| `plugins/wigtn-plugins/skills/screen-spec/` | Screen specs (IA / User Flow / Screen Spec / Wireframe HTML / Dev Handoff) generator |
| `plugins/wigtn-plugins/skills/screen-spec/templates/` | 5 boilerplate artifacts |
| `plugins/wigtn-plugins/skills/screen-spec/references/` | state-checklist, microcopy-patterns, handoff-checklist |
| `plugins/wigtn-plugins/skills/team-memory-protocol/` | Cross-agent shared context management |
| `plugins/wigtn-plugins/skills/wigtn-ppt/` | WIGTN-brand HTML presentation generator (Light/Dark themes, principles-based, no template) |
| `plugins/wigtn-plugins/skills/wigtn-ppt/references/` | `brand.md` (palette, logo, purple-dot signature), `design-guide.md` (layouts) |
| `plugins/wigtn-plugins/agents/prd-reviewer.md` | PRD digging — 4 adversarial lenses + conditional external grounding (self-contained) |
| `plugins/wigtn-plugins/agents/team-build-coordinator.md` | Team-based parallel build orchestration |

## Important Notes

- All skills and commands use Korean (한국어) for user-facing content
- Design style files follow a consistent pattern: philosophy, typography, layout, color, components, anti-patterns
- Fan-out is proportional to change size — a single reviewer is the default; splitting by category is the exception, not the rule
- Hooks run asynchronously to avoid blocking the main workflow
- Commands can be used without plugin prefix (e.g., `/prd` instead of `wigtn-plugins:prd`)

## Repository Hygiene — team-private artifacts (NEVER commit)

This is a **public** plugin repo (Apache-2.0). The following are **team-private** and must never be staged or committed. They are `.gitignore`d, but ignore rules don't catch already-tracked files — so this rule is the backstop:

| Path | What | Why private |
|------|------|-------------|
| `docs/` | Brand logos, PPT templates & data, internal PRD / PLAN / migration notes | Internal working artifacts, not part of the published plugin |
| `docs/images/*.png` | WIGTN brand logo binaries | Brand assets, team-only |
| `plugins/wigtn-plugins/skills/wigtn-ppt/assets/logo/*.png` | Bundled WIGTN logos for the skill | Brand assets, team-only (only `README.md` is committed) |

**Rules for any agent/contributor:**
- Before committing, run `git status` and confirm nothing under `docs/` or any brand `*.png` is staged. Never `git add docs/` or `git add -A` without checking.
- If you find such files already **tracked** (a teammate added them by accident), untrack with `git rm -r --cached <path>` (keeps the file on disk) — do **not** commit them.
- WIGTN logos are obtained out-of-band by team members (see `skills/wigtn-ppt/assets/logo/README.md`); `wigtn-ppt` falls back to a CSS/SVG wordmark when binaries are absent, so the public plugin stays fully functional without them.
