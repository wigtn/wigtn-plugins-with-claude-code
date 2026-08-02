---
description: |
  Implement features based on PRD specifications.

  Trigger keywords:
  - Commands: "/implement", "구현해줘", "만들어줘", "바로 구현"

  - Natural language (바이브 코더 친화):
    - "코드 작성해줘", "개발해줘", "빌드해줘"
    - "이제 만들어", "시작해줘", "진행해줘"
    - "코딩해줘", "개발 시작", "구현 시작"
    - "바로 만들어줘", "빨리 만들어줘"
    - "작업해줘", "개발 진행해줘"

  Best used AFTER /prd and prd-reviewer.
---

# Implement

PRD에 정의된 기능을 구현합니다.

**핵심 원칙**: 설계와 구현을 분리하여, 설계 확인 후 구현을 진행합니다.

## Pipeline Position

`[/prd] → [prd-reviewer] → [/implement] (현재 단계) → [/auto-commit]`

| 이전 단계 | 현재 | 다음 단계 |
|----------|------|----------|
| `prd-reviewer` - PRD 분석 완료 | `/implement` - 구현 | `/auto-commit` - 품질 검사 & 커밋 |

## Two-Phase Approach

DESIGN(설계) → **사용자 확인(Y/n) 필수** → BUILD(구현)의 2단계로 진행합니다. 상세 동작은 아래 DESIGN Phase / BUILD Phase Step 정의를 따릅니다. `auto_commit: true` 이면 BUILD 완료 후 자동으로 `/auto-commit`을 트리거합니다.

## 작업 규모 triage (Triage) — 진입 시 최초 1회

`/implement` 진입 시, 파이프라인 전체를 태우기 전에 **작업 규모를 먼저 판정**한다. 목적: 작은 수정에 그린필드용 오케스트레이션(디깅·팀빌드·별도 검증 서브에이전트)을 태워 느려지고 비싸지는 것을 막는다. 큰 작업엔 풀 파이프라인을 그대로 유지한다.

### 분류 (셋 중 하나)

| 분류 | 정의 | 신호 |
|------|------|------|
| **quick-fix** (경량) | 버그픽스·소규모 수정·문구/설정 변경. 단일 관심사, 새 아키텍처 결정 불요. | "버그", "고쳐", "오타", "~만 바꿔", "롤백"; 예상 변경 ≤2 파일; PRD 불요; 기존 코드 국소 수정 |
| **feature** (표준) | 기존 코드베이스에 기능 추가. 기존 스택/패턴 위에서 구현. | PRD 있음(선택); 단일~소수 팀; 새 모듈 소수; 기존 아키텍처 재사용 |
| **greenfield** (풀) | 새 프로젝트 또는 대형 기능. 아키텍처를 새로 정해야 함. | 새 레포/앱; 다수 팀·다수 도메인; 아키텍처 미정; PRD 필수 |

판정은 **사용자 요청 문구 + PRD 존재 여부 + 예상 변경 범위 + 새 아키텍처 필요 여부**를 함께 본다. 애매하면 한 단계 무겁게 잡는다(quick-fix ↔ feature 애매 → feature). 사용자가 규모를 명시하면 그것을 따른다. 판정 결과는 한 줄로 알린다(예: `triage: quick-fix — 단일 파일 버그픽스로 판단, 경량 경로 진행`).

### 분류별 라우팅

| 단계 | quick-fix | feature | greenfield |
|------|-----------|---------|-----------|
| PRD 품질 게이트 (Step 0) | PRD 있을 때만 | 예 | 예 |
| 아키텍처 결정 (Step 2, subagent) | 스킵 | 조건부(기존 스택 있으면 스킵) | 항상 |
| DESIGN Step 3~5 | 인라인 경량(영향 파일만 파악) | 예 | 예 |
| 디깅 상세검토 (parallel-digging) | 스킵 | 사용자 선택 시만 | 사용자 선택 시만 |
| 사용자 확인 (Step 6) | 예(요약 1줄 + Y/n) | 예 | 예 |
| BUILD | 단일 에이전트 인라인 구현 | 단일~소수 팀 | team-build 병렬 |
| Fresh-context verifier (Step 4.5) | 인라인 self-check | 예 | 예 |

- **quick-fix**: DESIGN을 인라인으로 최소 수행(영향 파일 Read → 계획 1~3줄 → Step 6 확인) 후 단일 에이전트가 바로 구현한다. 디깅·팀빌드·별도 verifier 서브에이전트를 띄우지 않는다. **설계-구현 분리 원칙(Step 6 확인)과 커밋 전 확인은 그대로 유지**한다 — 스킵하는 것은 오케스트레이션 오버헤드지 안전장치가 아니다.
- **feature / greenfield**: 아래 DESIGN Phase를 정상 수행한다. 병렬 여부는 "모드 결정"을 따른다.

### 수동 오버라이드

- `--full`: quick-fix로 판정돼도 풀 파이프라인 강제(아키텍처 결정 + 디깅 옵션 + 별도 verifier 포함).
- `--quick`: 강제로 경량 경로. (greenfield에 쓰면 경고 후 진행)
- 기존 `--parallel` / `--sequential`은 feature/greenfield의 BUILD 모드에만 적용된다(quick-fix는 항상 단일 에이전트).

## 이슈 트래커 분기 (Issue Tracker Branch)

DESIGN 완료 후, **이슈 트래커(Linear) 연동 여부**에 따라 BUILD 방식이 갈립니다:

- **연동 O** → Epic + 하위 이슈(FR 단위) + 의존성을 Linear에 등록한 뒤, **의존성 순서대로 이슈 단위 순차 개발** (이슈마다 In Progress → 커밋 → Done)
- **연동 X** (또는 `--no-tracker`) → 기존 원큐(one-shot) BUILD

자세한 동작: Step 0.5(감지) · Step 5.7(이슈 구조 설계) · Step 6(이슈 관리 확인) · Step 7(이슈 등록) · "Issue-driven 순차 BUILD".

## Parallel Mode Detection

병렬 모드는 독립적인 작업을 동시에 실행합니다. 트레이드오프: 토큰 사용량이 늘고 속도 향상이 보장되지는 않습니다. 의존성이 없는 작업이 많을 때 유리합니다.

### 모드 결정

- **전제**: 병렬은 triage가 `feature` 또는 `greenfield`일 때만 고려한다. `quick-fix`는 항상 단일 에이전트(병렬 아님).
- **기본값**: sequential (안전).
- **자동 활성화** (feature/greenfield에서 하나라도 충족 시): 활성 팀 2개 이상 · BUILD Phase 2개 이상 (Step 5.5 결과).
  - **파일 개수 단독으로는 병렬을 켜지 않는다** — 3파일짜리 국소 수정이 팬아웃으로 붐비는 것을 막는다(병렬 이득은 파일 수가 아니라 독립 팀·Phase 수에서 나온다).
- **수동 제어**: `--parallel`(병렬 강제) · `--sequential`(순차 강제).
- 활성화 시 현재 모드와 활성 에이전트 수를 사용자에게 한 줄로 표시하고, `--sequential` 로 끌 수 있음을 안내합니다.

---

## Task Plan Integration

### Task Plan 파일 검색

`/prd` 명령으로 생성된 Task Plan 파일을 자동으로 검색합니다.

검색 경로: `docs/todo_plan/PLAN_{feature-name}.md`, `docs/todo_plan/PLAN_*.md`

**Task Plan 발견 시**: 파일 경로·상태, Execution Config(`auto_commit`, `quality_gate`), Phase 목록(각 task 수)을 요약해 표시하고, Phase별 실행으로 진행합니다.

**Task Plan 없을 경우**:
- 기존 방식대로 PRD 기반 구현 계획 수립
- 구현 완료 후 Task Plan 생성 제안

## Usage

```bash
/implement 사용자 인증
/implement 플러그인 등록
/implement FR-006              # PRD 기능 ID로 직접 지정
/implement --parallel 사용자 인증   # 병렬 모드 강제 활성화
/implement --sequential 사용자 인증 # 순차 모드 강제
/implement --quick 오타 수정         # 경량 경로 강제 (디깅·팀빌드·별도 verifier 스킵)
/implement --full 로그인 버그        # quick-fix여도 풀 파이프라인 강제
/implement --full-stack 사용자 인증 # 모든 팀 강제 활성화 (deprecated)
/implement --no-tracker 사용자 인증 # Linear 연동 무시, 원큐(one-shot) 진행
```

## Parameters

- `feature-name or FR-ID`: 기능명 또는 기능 ID (required)
- `--quick`: triage를 무시하고 경량 경로(quick-fix) 강제
- `--full`: triage를 무시하고 풀 파이프라인 강제
- `--parallel`: 병렬 모드 강제 활성화 (feature/greenfield BUILD)
- `--sequential`: 순차 모드 강제 (기존 방식)
- `--full-stack`: (deprecated) 모든 팀 강제 활성화로 매핑
- `--no-tracker`: 이슈 트래커(Linear) 연동을 무시하고 원큐 플로우로 진행
- `--resume`: 저장된 진행 상태에서 마지막 실패 지점부터 재개 (인자 없이 `/implement {feature}` 와 동일)
- `--restart`: 저장된 진행 상태를 버리고 처음부터 다시 실행

---

## DESIGN Phase (설계 단계)

> **triage 게이팅**: `quick-fix`는 이 Phase를 **인라인 최소 수행**한다 — 영향 파일 Read → 계획 1~3줄 → Step 6 확인. Step 2(아키텍처 결정 subagent)·디깅·Parallel DESIGN은 건너뛴다. `feature`/`greenfield`만 아래 Step 0~7을 정상 수행한다.

### Parallel DESIGN (병렬 모드 시)

병렬 모드에서는 Steps 0-4를 3개 에이전트로 나눠 동시 실행 후 Step 5에서 병합합니다: **A** = Step 0+0.5+1(PRD 검색·QG·트래커 감지, 모두 읽기 전용), **B** = Step 2(아키텍처 결정), **C** = Step 3+4(프로젝트 분석·Gap Analysis). Agent A가 **Quality Gate BLOCKED** 판정 시 즉시 B·C를 중단하고 Critical 이슈를 표시한 뒤 수정 후 재시도를 안내합니다.

순차 모드에서는 아래 Step 0~7을 순서대로 실행합니다.

---

### Step 0: PRD 품질 검증 (Quality Gate)

구현 시작 전 PRD 품질 상태를 확인합니다. (PRD 경로, 검증일, Critical/Major/Minor 건수를 요약 표시)

**품질 게이트 판단 기준:**

| Critical 이슈 | 상태 | 액션 |
|--------------|------|------|
| **0개** | PASS | Step 1로 진행 |
| **1개 이상** | BLOCKED | 구현 중단, 수정 가이드 제공 |

**Critical 이슈가 있는 경우 (BLOCKED):** 구현을 진행할 수 없음을 알리고, 발견된 Critical 이슈(번호, 위치, 영향)를 나열한 뒤 다음 중 하나를 선택하게 합니다.
1. PRD 수정 후 다시 시도 — PRD 파일을 수정하고 `/implement` 재실행
2. 강제 진행 (권장하지 않음) — "Critical 무시하고 진행" 입력. 보안 취약점/구현 실패 위험 경고.

**검증 데이터 소스:**
- `/prd` 실행 시 자동 저장된 prd-reviewer 분석 결과
- PRD 파일의 메타데이터 (검증 상태, 검증일)
- 수동 prd-reviewer 실행 결과

### Step 0.5: 이슈 트래커 감지 (Issue Tracker Detection)

구현 작업을 이슈 단위로 추적할지 결정하기 위해, 연결된 이슈 트래커를 감지합니다. 현재는 **Linear**를 지원합니다. `mcp__linear__*` 도구가 사용 가능하면 연동된 것으로 판단합니다.

| 감지 결과 | `issue_tracker` | 동작 |
|----------|-----------------|------|
| `mcp__linear__*` 도구 있음 | `linear` | Step 6에서 "이슈로 관리할지" 1회 확인 |
| 도구 없음 | `none` | 기존 원큐(one-shot) 플로우로 진행 |
| `--no-tracker` 플래그 | `none` (강제) | 감지를 무시하고 원큐 플로우 |

**연동 감지 시 추가 수집 (읽기 전용):**
- `mcp__linear__list_teams` → 워크스페이스 팀 목록 조회. 팀 1개면 자동 선택, 여러 개면 Step 6에서 사용자에게 선택 요청.
- `mcp__linear__list_projects` → 기존 프로젝트 목록 조회 (Epic을 어디에 둘지 판단, Step 7에서 사용).
- `mcp__linear__list_issue_statuses` → 대상 팀의 상태 목록 조회. **상태 이름은 팀마다 다르므로 글자가 아닌 `type`으로 매칭**한다:
  - `started_state` = `type: "started"` 인 상태 (예: "In Progress", "In Dev")
  - `done_state` = `type: "completed"` 인 상태 (예: "Done", "Shipped")
  - 해당 type이 여러 개면 워크플로우 순서상 첫 번째 사용. 없으면 가장 가까운 상태로 폴백하고 경고.
  - 이 `started_state` / `done_state`를 BUILD 상태 전환에 사용 (이름을 하드코딩하지 않음)

> **IMPORTANT**: 이 단계는 **읽기 전용**입니다. 실제 에픽/이슈 생성은 Step 6 승인 이후(Step 7)에만 수행합니다. 병렬 모드에서는 읽기 전용이므로 Agent A(Step 0+1) 레인에 포함해 함께 실행합니다.

감지 결과는 한 줄로 요약합니다 (예: `Linear 연결됨 · 팀: Engineering · 상태: Backlog→In Progress→In Review→Done`). 미연동이면 "이슈 트래커 미연동 → 원큐 플로우로 진행"으로 안내합니다.

### Step 1: PRD 검색

인자로 전달된 기능명 또는 기능 ID로 PRD를 검색합니다.

검색 경로(자동 탐지): `prd/`, `docs/prd/`, `requirements/`, `specs/`, `*.prd.md`, `*-requirements.md`, `*-spec.md`

검색 패턴: 기능명이 포함된 PRD 파일 · `FR-XXX` 형식의 기능 ID · 관련 키워드가 포함된 섹션

**PRD를 찾지 못한 경우**, 다음 중 하나를 선택하게 안내합니다.
1. `/prd [기능명]`으로 PRD 먼저 작성
2. PRD 파일 경로 직접 지정
3. PRD 없이 바로 구현 (권장하지 않음)

### Step 2: 아키텍처 결정 (Subagent)

> **triage 게이팅**: `greenfield`에서만 항상 수행. `feature`는 기존 스택/아키텍처가 감지되면 그것을 존속하고 이 단계를 스킵한다(새 아키텍처 결정이 필요할 때만 호출). `quick-fix`는 스킵.

PRD 분석을 바탕으로 `architecture-decision` agent를 호출해 최적 아키텍처를 결정합니다.

```yaml
Input:
  prd_path: "docs/prd/user-authentication.md"
  project_path: "./"
  existing_stack: ["typescript", "prisma"]

Output:
  architecture: { type: "modular-monolith", confidence: 85 }  # monolithic | modular-monolith | msa
  recommendations:
    tech_stack: ["NestJS", "Prisma", "PostgreSQL"]
    folder_structure: "src/modules/..."
    key_patterns: ["Repository pattern", "Event-driven"]
  warnings: ["향후 MSA 전환 고려"]
```

**아키텍처 결정 기준:**

| 평가 항목 | 모놀리식 | 모듈러 모놀리식 | MSA |
|----------|---------|---------------|-----|
| 도메인 수 | 1-2개 | 3-4개 | 5개+ |
| 팀 규모 | 1-3명 | 3-10명 | 10명+ |
| 프로젝트 단계 | MVP | 성장기 | 엔터프라이즈 |
| 독립 배포 필요 | X | △ | O |

결정 결과는 추천 아키텍처 + 신뢰도, 식별된 도메인, 추천 폴더 구조, 주의사항을 요약해 표시합니다.

### Step 3: 프로젝트 상태 분석

**프로젝트 구조 자동 탐지:**

| 프로젝트 유형 | 소스 경로 | API 경로 | 컴포넌트 경로 |
|--------------|---------|---------|-------------|
| 일반 | `src/`, `lib/` | `src/api/` | `src/components/` |
| Next.js | `app/`, `src/app/` | `app/api/` | `components/` |
| Monorepo | `apps/*/src/` | `apps/api/` | `apps/web/src/` |
| NestJS | `src/` | `src/modules/` | - |
| Python | `src/`, `app/` | `app/api/` | - |

확인 사항: 기존 구현 여부 · 관련 파일 위치 · 사용 중인 패턴/컨벤션

### Step 4: Gap Analysis

| Status | Description | Action |
|--------|-------------|--------|
| Complete | 이미 구현됨 | 스킵 또는 업데이트 확인 |
| Partial | 부분 구현 | 남은 부분만 구현 |
| Not done | 미구현 | 전체 구현 |

### Step 5: 구현 계획 수립

PRD와 프로젝트 분석을 바탕으로 구현 계획을 수립합니다. 생성/수정할 파일을 표로 정리하고 각 파일에 담당 `FR`을 매핑합니다.

```markdown
## 구현 계획

### 생성할 파일
| 경로 | 설명 | 타입 | FR |
|------|------|------|-----|
| src/api/auth/login.ts | 로그인 API | Backend | FR-001 |
| src/services/AuthService.ts | 인증 서비스 | Backend | FR-001, FR-002 |
| src/components/LoginForm.tsx | 로그인 폼 | Frontend | FR-004 |

### 수정할 파일
| 경로 | 변경 내용 | FR |
|------|----------|-----|
| prisma/schema.prisma | User 모델 추가 | FR-001 |

### 구현 순서
1. Database/Schema 변경  2. Backend API  3. Frontend 컴포넌트  4. 테스트
```

> **이슈 트래커 연동 시 필수**: 각 파일에 담당 `FR`을 매핑한다. 이 매핑이 Step 5.7 이슈 본문의 "구현 범위(파일)"과 BUILD 루프에서 각 이슈의 작업 범위를 결정한다. 여러 FR이 한 파일을 건드리면 의존성 순서상 **나중 FR 이슈**가 그 파일을 마지막에 커밋한다 (앞 FR은 자기 범위만 부분 작성).

### Step 5.5: 팀 할당 (Team Allocation)

구현 계획의 파일 목록과 PRD를 분석하여 활성화할 팀을 결정합니다.

| 팀 | 활성화 조건 | Agent | Plugin |
|-----|-----------|-------|--------|
| Backend | api/, services/, models/, prisma/ 파일 존재 | backend-architect | wigtn-plugins |
| Frontend | components/, pages/, app/, styles/ 파일 존재 | frontend-developer | wigtn-plugins |
| AI Server | ai/, llm/, stt/, ml/ 파일 또는 PRD에 AI 키워드 | ai-agent | wigtn-plugins |
| Ops | Dockerfile, .github/, k8s/ 파일 존재 | (없음) | wigtn-plugins |

팀별 활성/비활성 여부와 task 수, 담당 에이전트, 활성 팀 개수를 요약해 표시하고, 이 결과를 사용자 확인(Step 6)에 포함합니다.

### Step 5.6: 디자인 결정 (Frontend 팀 활성 시 자동)

Frontend 팀이 활성화된 경우, BUILD 전에 디자인 방향을 결정합니다. 판단 로직은 위에서부터 차례로 평가하고, 해당하면 그 단계에서 결정 후 스킵합니다.

| 조건 | 액션 | 소요 |
|------|------|------|
| PRD에 `"스타일: Glassmorphism"` 등 명시 | design-system-reference에서 해당 스타일 로드 → BUILD | 즉시 |
| PRD에 `"Stripe처럼"`, `"Linear 느낌"` 등 브랜드 참조 | 가장 가까운 스타일 패러다임 매핑 → BUILD | 즉시 |
| 기존 프로젝트에 Tailwind config, theme, 디자인 토큰 존재 | 기존 시스템 존속, 스킵 | 즉시 |
| 디자인 정보 없음 (새 프로젝트) | `design-discovery` agent 호출 → 사용자 선택 → 스타일 결정 | 질문 3-4개 |

**design-discovery agent 호출:**
```yaml
trigger: Frontend 팀 활성 AND 디자인 스타일 미정
agent: design-discovery
input:
  platform: "web" | "mobile"   # PRD에서 자동 판별
  context: PRD 요약 (타겟 유저, 프로젝트 유형)
output:
  style: "aurora-gradient"     # 선택된 스타일
  theme: "dark"                # 라이트/다크
  animation_level: "moderate"  # none/minimal/moderate/rich
  density: "balanced"          # compact/balanced/spacious
```

**결정된 디자인을 BUILD에 전달:**
```yaml
frontend_design:
  style: "aurora-gradient"
  style_guide_path: "styles/aurora-gradient.md"
  common_modules: ["common/colors.md", "common/animations.md", "common/spacing.md"]
  theme: "dark"
  animation_level: "moderate"
```

> `frontend-developer` agent는 BUILD 시작 전에 결정된 스타일 가이드 파일과 관련 common 모듈을 읽습니다. 스타일 가이드 없이 Frontend 코드를 작성하지 않습니다.

결정된 디자인(스타일, 테마, 애니메이션, 밀도)을 요약 표시하고 frontend-developer agent에 전달합니다.

### Step 5.7: 이슈 구조 설계 (이슈 트래커 연동 시)

> `issue_tracker = linear` 일 때만 수행. 미연동이면 건너뛰고 Step 6로 진행.

**PRD 구조를 그대로 활용**하여 에픽/하위 이슈/의존성을 설계합니다. (아직 생성하지 않고 **제안만** 만듭니다 — 실제 생성은 Step 7.)

**매핑 규칙:**

| Linear | 소스 | 비고 |
|--------|------|------|
| Epic (부모 이슈) | 기능명 / PRD 제목 | 1개 |
| 하위 이슈 (sub-issue) | PRD §FR (Functional Requirements) 각 1개 | `parentId` = Epic |
| 의존성 (`blocks`/`blockedBy`) | FR 테이블의 Dependencies 컬럼 | `FR-002 → FR-001` 이면 FR-002 가 FR-001 에 `blockedBy` |
| 우선순위 (선택) | FR Priority (P0→Urgent, P1→High, P2→Medium...) | `priority` |
| 라벨 (선택) | Implementation Phase (MVP/Enhancement 등) | `labels` |

**하위 이슈 본문 템플릿:**

```markdown
**기능:** {FR 설명}

**구현 범위(파일):**
- {Step 5 구현 계획에서 이 FR에 해당하는 생성/수정 파일}

**완료 조건:**
- {PRD acceptance criteria 또는 FR 검증 기준}

> Generated from PRD §{FR-ID}
```

**의존성 순서(topological order) 산출:**
- FR 의존성 그래프를 위상 정렬하여 BUILD 실행 순서를 결정
- 순환 의존성 발견 시 경고 후 사용자에게 표시 (해당 의존성은 무시하고 진행 제안)

제안은 Epic + 하위 이슈를 의존성 순서로 나열하고(각 FR의 의존 대상 표기), 총 Epic/sub-issue/의존성 건수를 요약해 표시한 뒤, 다음 단계(Step 6)에서 등록 여부를 확인한다고 안내합니다.

### Step 6: 사용자 확인 (CHECKPOINT)

설계 완료 후 반드시 사용자 확인을 받습니다. 기능명, PRD 경로, 생성/수정할 파일 목록, 팀 할당(활성 팀별 task 수·에이전트), (Frontend 활성 시) 디자인 결정을 요약해 보여준 뒤 진행 여부를 묻습니다.

**AskUserQuestion 사용:**
```yaml
question: "이 계획대로 구현을 진행할까요?"
options:
  - label: "진행 (Recommended)"
    description: "바로 구현 시작"
  - label: "상세 검토"
    description: "prd-reviewer 에이전트로 파일별 상세 분석 후 진행"
  - label: "수정 필요"
    description: "계획 수정 후 재확인"
  - label: "취소"
    description: "구현 취소"
```

**이슈 트래커 연동 시 추가 확인 (issue_tracker = linear):** 위 계획 확인과 함께 이슈 관리 여부와 (필요 시) 팀을 확인합니다.

```yaml
# 1) 이슈 관리 여부
question: "이번 작업을 Linear 이슈로 관리할까요?"
options:
  - label: "예, 이슈로 관리 (Recommended)"
    description: "Step 5.7 제안대로 Epic + 하위 이슈 + 의존성을 Linear에 생성하고, 이슈 단위로 순차 개발"
  - label: "아니요, 원큐로 진행"
    description: "이슈 생성 없이 기존 플로우로 바로 구현 (이번 실행만 --no-tracker 와 동일)"

# 2) 팀 선택 (Step 0.5에서 팀이 여러 개로 확인된 경우에만)
question: "어느 팀에 이슈를 만들까요?"
options: [list_teams 결과로 동적 생성]
```

| 응답 | 다음 단계 |
|------|----------|
| "이슈로 관리" 선택 | Step 7 (이슈 등록) → Issue-driven 순차 BUILD |
| "원큐로 진행" 선택 | `issue_tracker = none` 으로 전환 → 기존 Team/Sequential BUILD |

### "상세 검토" 선택 시 (Optional Deep Dive)

사용자가 "상세 검토"를 선택하면 `prd-reviewer` 에이전트를 호출하여 파일별 상세 분석(예상 구현, 의존성, 질문/리스크)을 진행합니다.

```yaml
input:
  context: "implementation_review"
  files:
    - { path: "src/api/auth/login.ts", purpose: "로그인 API", type: "Backend" }
    - { path: "src/api/auth/register.ts", purpose: "회원가입 API", type: "Backend" }
  prd_path: "docs/prd/user-authentication.md"

output:
  - file: "src/api/auth/login.ts"
    questions: ["Rate limiting 적용 필요?", "로그인 실패 횟수 제한?"]
    risks: []
  - file: "src/api/auth/register.ts"
    questions: ["이메일 인증 필수?"]
    risks: ["이메일 중복 체크 로직 필요"]
```

**상세 검토 완료 후:** 식별된 질문에 대한 답변 수집 → 답변 기반으로 구현 계획 보완 → 다시 사용자 확인 → BUILD Phase 진행.

---

### Step 7: 이슈 등록 (이슈 트래커 연동 시)

> Step 6에서 "이슈로 관리"를 승인한 경우에만 수행. 여기서 **처음으로** Linear에 쓰기 작업을 합니다.

**등록 순서:**

```
0. Project 결정 (Epic 컨테이너) — Step 0.5의 list_projects 결과 사용
   - 기능/레포명과 일치하는 기존 프로젝트가 있으면 재사용
   - 없으면 mcp__linear__save_project(name=<레포/기능명>, addTeams=[팀]) 로 생성
   - 워크스페이스가 Project를 안 쓰면 생략 가능 → 부모 이슈(Epic)만으로 진행

1. Epic 생성 (부모 이슈)
   mcp__linear__save_issue(team=<팀>, project=<있으면>, title="<기능명>", description="<PRD 요약 + PRD 파일 경로>")
   → epic_id 획득

2. 하위 이슈 생성 (FR마다, 의존성 위상 순서로)
   for FR in topological_order(FRs):
     mcp__linear__save_issue(team=<팀>, project=<있으면>, title="FR-XXX <설명>",
       description=<Step 5.7 본문 템플릿>, parentId=epic_id, priority=<FR priority 매핑>)
     → fr_issue_id[FR] 저장

3. 의존성 연결
   for FR with deps:
     mcp__linear__save_issue(id=fr_issue_id[FR],
       blockedBy=[ fr_issue_id[dep] for dep in FR.dependencies ])
```

**Project 결정 규칙:**

| 상황 | 동작 |
|------|------|
| 기능/레포명과 일치하는 Project 존재 | 재사용 (epic·하위 이슈를 그 project에 배치) |
| 일치하는 Project 없음 | 신규 Project 생성 후 배치 |
| 워크스페이스가 Project 미사용 | `project` 생략, 부모 이슈(Epic)만으로 운영 |

> Linear엔 Jira식 "Epic" 타입이 없어 **Epic = 부모 이슈**로 표현하고, Project는 그 Epic을 담는 상위 컨테이너로 (선택적으로) 사용한다.

> **멱등성(재실행 안전):** 생성된 이슈 ID를 PLAN 파일의 `## Issue Tracker` 섹션에 즉시 기록합니다. 재실행 시 이 매핑을 기준으로 reconcile 합니다:
> - 매핑된 이슈가 Linear에 존재 → **새로 만들지 않고** 제목/본문/의존성만 업데이트
> - PRD에 **새 FR 추가됨** (매핑에 없음) → 그 FR만 하위 이슈 신규 생성 후 매핑에 추가
> - PRD에서 **FR 사라짐** → 기존 이슈는 자동 삭제하지 않고 그대로 둠 (정리는 사용자가 Cancel)
> - 매핑된 이슈가 Linear에서 **Canceled/삭제됨** → 사용자에게 알리고 재생성 여부 확인

> **Linear 특성 주의:** ① description 마크다운은 Linear가 일부 문자(`~`, `[`, `]` 등)를 자동 이스케이프하므로 본문은 단순하게 작성. ② 하드삭제 API가 없으므로 롤백/정리는 상태 `Canceled`로 처리 (영구삭제는 Linear UI 휴지통).

**PLAN 파일에 추가하는 매핑 섹션:**

```markdown
## Issue Tracker

| Field | Value |
|-------|-------|
| Provider | linear |
| Team | <팀명> |
| Project | <프로젝트명 또는 - (미사용)> |
| Epic | <이슈 식별자> (<기능명>) |

| FR | Issue | Depends on | State |
|----|-------|-----------|-------|
| FR-001 | <id> | - | Backlog |
| FR-002 | <id> | <FR-001 id> | Backlog |
```

등록 완료 시 Epic과 하위 이슈 트리(각 이슈의 식별자, FR, 의존 관계)를 요약해 표시하고 의존성 순서대로 개발을 시작한다고 안내합니다.

**등록 실패 시 (Graceful Degradation):** Error Recovery §7 참조 — 사용자에게 알리고 원큐 플로우로 폴백 옵션 제공.

---

## BUILD Phase (구현 단계)

사용자 확인 후 실제 코드 작성을 진행합니다.

### Issue-driven 순차 BUILD (이슈 트래커 연동 시)

> `issue_tracker = linear` 이고 Step 7에서 이슈를 등록한 경우, 아래 **이슈 단위 순차 개발**을 수행합니다. (미연동이면 이 섹션을 건너뛰고 아래 Team BUILD / Step 1~5로 진행)

의존성 위상 순서(topological order)대로 이슈를 하나씩 처리합니다:

```
for issue in topological_order(sub_issues):   # blockedBy 가 모두 완료된 이슈부터
  1. Linear 상태 전환 → 시작 상태 (Step 0.5의 started_state, type=started)
     mcp__linear__save_issue(id=issue, state=started_state)   # 예: "In Progress"
  2. 해당 FR의 구현 범위(파일)를 작성  (범위 = Step 5의 FR↔파일 매핑)
     - 적합한 팀 에이전트에 위임 (Backend→backend-architect, Frontend→frontend-developer, AI→ai-agent)
     - 단일 이슈 범위이므로 1개 에이전트가 담당
  3. 검증: typecheck / test / build (해당 시)
  4. 커밋 (commit_per_issue): 이 이슈 변경분만 커밋
     - 커밋 메시지에 Linear 식별자 포함 (예: "feat: 로그인 API (WIG-101)")
       → Linear 가 커밋/PR을 이슈에 자동 연결
     - 브랜치명은 이슈 생성 응답의 gitBranchName 사용 시 연결이 더 확실
  5. Linear 상태 전환 → 완료 상태 (Step 0.5의 done_state, type=completed)
     mcp__linear__save_issue(id=issue, state=done_state)       # 예: "Done"
  6. PLAN 파일 Issue Tracker 표의 State 갱신 + Execution Log 기록
```

**왜 순차인가:** 이슈 간 의존성(예: 회원가입은 로그인 인증 흐름에 의존)을 존중하기 위해, 선행 이슈가 Done 이 된 뒤 다음 이슈를 시작합니다. (의존성이 없는 이슈끼리도 기본은 순차 — 이력 추적을 단순하게 유지)

진행 상황은 이슈별 상태(Done/In Progress/Blocked/Backlog)와 완료 건수, Epic 링크를 한 블록으로 표시합니다.

**한 이슈 실패 시:** 해당 이슈는 "In Progress" 유지 + Execution Log 에 오류 기록 → Error Recovery 프로토콜 적용. 그 이슈에 의존하는 후속 이슈는 보류하고, 독립 이슈는 계속 진행할지 사용자에게 확인.

**커밋/PR 정책:**
- `commit_per_issue: true` (이슈 단위 연동의 기본값): 이슈마다 커밋
- 품질 게이트가 필요하면 마지막에 `/auto-commit` 1회로 Epic 전체 PR 생성 (기존 `auto_commit` 설정 따름) — 이슈마다 별도 PR은 만들지 않음 (PR 폭주 방지)

---

### Team BUILD (팀 기반 병렬)

> 병렬 모드에서는 `team-build-coordinator`를 호출하여 팀별 병렬 빌드를 수행합니다. DESIGN Phase의 Step 5.5에서 결정된 팀 할당을 기반으로 실행합니다.
>
> 독립적이고 병렬 이득이 큰 작업은 팀·서브에이전트에 적극 위임합니다(방어적 blocking 대기 없이). 의존성이 강하거나 순차가 더 단순하면 원큐로 진행합니다.

`team-build-coordinator`가 다음 Phase를 순서대로 수행합니다:

- **Phase 0 — Setup**: `SHARED_CONTEXT_{feature}.md` 생성, MEMORY.md 읽기(프로젝트 컨벤션 파악), TodoWrite 등록(팀별 Task).
- **Phase 1 — Foundation (조건부)**: 다른 팀이 의존할 경우 Backend 스키마/타입 선행.
- **Phase 2 — 병렬 팀 실행**: Backend(backend-architect) · Frontend(frontend-developer) · AI Server(ai-agent, 해당 시) · Ops(general-purpose, 해당 시) 동시 실행.
- **Phase 3 — 통합 검증 (fresh-context verifier)**: 빌드 컨텍스트와 독립된 서브에이전트가 PRD/계약을 대조해 API 계약 준수·타입 일관성·파일 충돌을 검증.
- **Phase 4 — 빌드/테스트 검증**: typecheck / test / build, Auto Memory 업데이트.

조율은 SHARED_CONTEXT + TodoWrite + Auto Memory로 수행하며, 오류 발생 시 실패 팀만 순차 재시도하고 독립 팀은 계속 진행합니다. 진행 상황은 팀별 task 완료 현황과 전체 진행률, Shared Context 경로를 함께 표시합니다.

**팀 할당 모드:**

| 플래그 | 동작 |
|--------|------|
| `--parallel` | 팀 기반 병렬 강제 (기존과 동일 UX) |
| `--sequential` | 팀 순차 실행 (Backend → Frontend → AI → Ops) |
| `--full-stack` | deprecated 알림 + 모든 팀 강제 활성화로 매핑 |

순차 모드에서는 아래 Step 1~5를 순서대로 실행합니다.

---

### Step 1: Phase별 실행 (Task Plan 기반)

**Task Plan이 있는 경우**, Phase 단위로 순차 실행합니다. 각 Phase 시작 시 TodoWrite에 task를 등록하고 진행에 따라 상태를 갱신합니다.

```
For each Phase in Task Plan:
  1. TodoWrite에 Phase tasks 등록 (status: pending)
  2. 첫 번째 task를 in_progress로 변경
  3. Task 실행
  4. Task 완료 시: TodoWrite completed + PLAN 파일 [ ] → [x]
  5. 다음 task로 이동
  6. Phase 완료 시: PLAN 파일 Phase status + Progress 섹션 업데이트
  7. 다음 Phase로 이동
```

**PLAN 파일 실시간 업데이트** (체크박스 + Progress 표 + Execution Log):

```markdown
### Phase 1: 환경 설정
- [x] 프로젝트 구조 생성
- [x] 의존성 설치
- [ ] 설정 파일 작성              ← 진행 중

## Progress
| Metric | Value |
|--------|-------|
| Total Tasks | 3/13 |
| Current Phase | Phase 1: 환경 설정 |
| Status | in_progress |

## Execution Log
| Timestamp | Phase | Task | Status |
|-----------|-------|------|--------|
| YYYY-MM-DD HH:MM | Phase 1 | 프로젝트 구조 생성 | completed |
```

> Execution Log의 Timestamp는 `YYYY-MM-DD HH:MM` 형식으로 실제 실행 시각을 기록합니다.

### Step 2: 코드 작성 (Task Plan 없는 경우)

기존 방식의 구현 순서:
1. **Database/Schema** (필요 시) — 스키마 변경/추가, 마이그레이션 생성
2. **Backend/API** — 엔드포인트 구현, 서비스 로직, DTO/Validation
3. **Frontend/UI** — 페이지/컴포넌트, 상태 관리, API 연동
4. **Tests** (해당 시) — 유닛 테스트, 통합 테스트

### Step 3: 구현 진행 상황 표시

현재 Phase, task별 상태(완료/진행 중/대기), 전체 진행률을 간결한 목록으로 표시합니다.

### Step 4: 검증

```bash
npm run typecheck   # TypeScript 타입 체크 (해당 시)
npm test            # 테스트 실행 (해당 시)
npm run build       # 빌드 확인
```

### Step 4.5: Fresh-Context 검증 (verifier)

> **triage 게이팅**: `feature`/`greenfield`만 별도 서브에이전트를 띄운다. `quick-fix`는 인라인 self-check로 대체(변경 파일 재확인 + typecheck/test)한다 — 3줄 수정에 검증 서브에이전트를 띄우는 오버헤드를 피한다.

빌드를 수행한 컨텍스트와 **독립된 새 서브에이전트**를 띄워, 구현 산출물이 PRD/계약을 충족하는지 검증합니다 (self-critique보다 정확). 검증자에게는 구현 과정 로그가 아니라 **PRD 요구사항 + 변경 파일 목록만** 전달합니다.

- 입력: PRD의 FR/acceptance criteria, §5.4 계약(있으면), 생성·수정된 파일 목록
- 확인: 각 FR이 실제 코드로 충족됐는가 · 계약(시그니처/타입/엔드포인트) 일치 · 명백한 누락/모순
- 출력: FR별 충족/미충족 + 근거(파일:라인). 미충족이 있으면 Step 5 진행 전 보완하거나 사용자에게 보고합니다.
- 비차단: 검증자 실행이 실패하면 경고만 남기고 진행합니다 (graceful degradation).

### Step 5: 구현 완료 및 자동 커밋 트리거

모든 Phase 완료 시, Phase별 task 완료 현황과 검증 결과(타입체크/테스트/빌드)를 요약 표시합니다.

**auto_commit 트리거 조건:**

| 조건 | 액션 |
|------|------|
| `auto_commit: true` + 모든 Phase 완료 | `/auto-commit` 자동 실행 |
| `auto_commit: false` | 수동 커밋 안내 |
| `commit_per_phase: true` | Phase 완료 시마다 중간 커밋 |

완료 후 PLAN 파일의 Progress를 `completed`로, Execution Log에 `/auto-commit` 트리거·Quality Gate·Git Commit 결과를 (`YYYY-MM-DD HH:MM` 형식 시각으로) 기록합니다.

---

## Code Pattern Discovery

기존 패턴을 Glob/Grep으로 파악해 컨벤션을 따른다: API 엔드포인트(`**/api/**`, 라우터/컨트롤러 데코레이터), 컴포넌트(`**/components/**`, export 패턴), DB 스키마(Prisma `schema.prisma` / SQLAlchemy `models/` / TypeORM `entities/`).

---

## Validation Checklist

구현 완료 후 확인:
- [ ] 타입 에러 없음
- [ ] 빌드 성공
- [ ] 기존 테스트 통과
- [ ] 기존 기능에 영향 없음
- [ ] PRD 요구사항 충족

---

## Integration Points

### 호출하는 에이전트

| 에이전트 | 역할 | 호출 조건 |
|----------|------|----------|
| `architecture-decision` | 아키텍처 결정 | greenfield 항상 · feature 조건부 · **quick-fix 스킵** |
| `team-build-coordinator` | 팀 기반 병렬 빌드 조율 | BUILD Phase 병렬 모드 (feature/greenfield) · **quick-fix 스킵** |
| `backend-architect` | Backend 코드 생성 | Team BUILD (Backend 팀) |
| `frontend-developer` | Frontend 코드 생성 | Team BUILD (Frontend 팀) |
| `ai-agent` | AI/ML 코드 생성 | Team BUILD (AI Server 팀) |

> `quick-fix`는 위 조율 에이전트를 띄우지 않고, 단일 에이전트가 인라인으로 구현·자가검증한다. `--full`로 풀 파이프라인을 강제할 수 있다.

### 이슈 트래커 (MCP, 선택)

| 도구 | 역할 | 호출 시점 |
|------|------|----------|
| `mcp__linear__list_teams` | 팀 목록 조회 / 팀 선택 | Step 0.5 감지 |
| `mcp__linear__list_issue_statuses` | 상태 워크플로우 확인 | Step 0.5 감지 |
| `mcp__linear__save_issue` | Epic·하위 이슈 생성, 의존성 연결, 상태 전환 | Step 7 등록 / BUILD 중 |

> `mcp__linear__*` 도구가 없으면 모든 호출을 건너뛰고 원큐 플로우로 동작합니다 (Graceful Degradation).

### 이전 단계에서 받는 입력

`/prd` + prd-reviewer 결과물: 검증된 PRD 문서, 기능 요구사항(FR-XXX), 비기능 요구사항(NFR-XXX), API 명세(상세), 식별된 리스크 및 대응 방안.

### 다음 단계로 전달하는 출력

`/auto-commit`에 전달: 새로 생성된 파일 목록, 수정된 파일 목록, 구현된 기능 목록, 검증 결과(타입체크/테스트/빌드), 실행 모드(parallel/sequential).

---

## Auto-Trigger

구현 완료 시 자동으로 auto-commit 사용을 제안합니다.
- 다음 단계: `/auto-commit`으로 품질 검사 후 커밋 → 코드 리뷰로 품질 게이트 통과 확인
- 또는 추가 작업: 다른 기능 구현(`/implement [기능명]`), 테스트 추가 작성

---

## Rules

1. **설계-구현 분리** — 설계 완료 후 반드시 사용자 확인. 확인 없이 구현 진행 금지.
2. **기존 코드 수정 시** — 먼저 Read로 현재 구현 확인, 기존 패턴/컨벤션 준수, 불필요한 변경 최소화.
3. **새 파일 생성 시** — 기존 파일 구조 참고, 적절한 경로에 생성, 네이밍 컨벤션 준수.
4. **에러 발생 시** — 즉시 수정, 롤백이 필요하면 사용자에게 알림.

---

## Error Recovery Protocol (에러 복구 프로토콜)

공통 원칙: 자동 복구 가능한 오류는 고쳐서 재검증하고, 불가능하면 오류·원인·해결책을 안내한다. 진행 상태는 PLAN 파일(+ `.claude/session/implement_{feature}.json`)에 저장되어 실패 지점부터 재개(`/implement {feature}` 또는 `--resume`)한다.

1. **아키텍처 결정 실패**: 3회 재시도 → 실패 시 기본값(Modular Monolith, 가장 안전) 제안, 또는 수동 선택(Monolithic/Modular Monolith/MSA).
2. **Phase 중간 실패**: 자동 복구(의존성 누락→`npm/pip install`, 단순 타입 오류→수정 후 재컴파일, 린트→`code-formatter`, 포트 충돌→대체 포트). 불가능하면 수동 개입 안내.
3. **PLAN 파일 동기화 오류**: 파일 시스템 스캔으로 실제 상태 확인 → PLAN과 비교 → 불일치 항목 표시 및 옵션(PLAN 자동 업데이트(권장) / 덮어쓰기 / 수동 확인).
4. **빌드/테스트 실패**: 자동 수정 가능하면 수정 후 재검증, 아니면 파일/라인·권장 조치를 안내하고 사용자 수정 후 "검증 재실행" 또는 `/auto-commit`.
5. **작업 중단 및 재개**: 진행 상태 저장 → 다음 세션 `/implement {feature}`로 마지막 지점부터 재개, `--restart`로 처음부터.
6. **롤백**: 부분 롤백(권장, 문제 변경만) / Phase 롤백 / 전체 롤백(`git reset --hard HEAD~N`) / 수동 수정.
7. **이슈 트래커 연동 오류**: 재시도(권장) / 이슈 없이 원큐 진행(`--no-tracker`) / 중단. 부분 생성된 이슈는 PLAN `## Issue Tracker`에 기록되어 재실행 시 중복 생성 안 함. 취소·정리는 상태 `Canceled`로 전환(Linear는 하드삭제 미지원).

**원칙 (Graceful Degradation)**: 이슈 트래커는 보조 기능이므로 연동이 실패해도 구현 자체는 원큐 플로우로 계속 진행한다.

---

## Examples

### PRD 기반 구현

```
입력: /implement 사용자 인증

DESIGN: PRD 발견(docs/prd/user-authentication.md) + prd-reviewer 완료 + Critical 없음
        → 구현 계획 수립(생성 5 / 수정 2, 구현 순서 정의)
        → 사용자 확인: "이 계획대로 진행할까요?"
BUILD (승인 후): 파일 생성 → 검증(타입체크/테스트/빌드) → "다음 단계: /auto-commit"
```

### 자연어 입력 처리

```
입력: "이제 만들어줘"
인식: 패턴 매칭 + 이전 대화에서 기능 확인("사용자 인증")
진행: /implement 사용자 인증 → DESIGN → 사용자 확인 → BUILD
```

### 경량 경로 (quick-fix triage)

```
입력: /implement 로그인 버튼 클릭 시 콘솔 에러 고쳐줘
triage: quick-fix — 단일 관심사 버그픽스로 판단, 경량 경로 진행
DESIGN(인라인): 영향 파일 Read(LoginForm.tsx) → 원인 파악 → 수정 계획 1줄
사용자 확인: "이 수정대로 진행할까요?" → 진행
BUILD: 단일 에이전트가 바로 수정 → 인라인 self-check(typecheck/test)
        (디깅·team-build·별도 verifier 스킵)
다음 단계: /auto-commit
```

### 이슈 트래커 연동 구현 (Linear)

```
입력: /implement 사용자 인증

DESIGN: PRD 발견 + 품질 게이트 통과
        + 이슈 트래커 감지: Linear (팀 1개 → 자동 선택)
        + 구현 계획(생성 5 / 수정 2)
        + 이슈 구조 제안: Epic + FR 4개 + 의존성 3건
사용자 확인: "계획대로 진행?" → 진행 / "Linear 이슈로 관리?" → 예
이슈 등록(Step 7): Epic 생성 → FR 하위 이슈 생성 + blockedBy 연결 → PLAN 파일에 매핑 기록
Issue-driven 순차 BUILD: 의존성 순서대로 이슈마다 In Progress → 구현 → 검증 → 커밋 → Done
다음 단계: /auto-commit (Epic 전체 PR + 품질 게이트)
```

### PRD 없이 구현 시도

```
입력: /implement 알림 기능
PRD 확인: PRD 문서 없음
안내: PRD 없이 구현하면 요구사항 누락 위험. 권장: "/prd 알림 기능" 먼저 작성.
      계속하려면 "PRD 없이 진행"이라고 말씀해주세요.
```
