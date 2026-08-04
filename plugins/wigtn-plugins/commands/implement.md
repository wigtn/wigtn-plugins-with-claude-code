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

PRD에 정의된 기능을 구현한다.

파이프라인: `/prd` → `prd-reviewer` → (FE 있으면 `/screen-spec`) → **`/implement`** → `/auto-commit`

**핵심 원칙 — 설계-구현 분리**: DESIGN → **사용자 확인(Y/n)** → BUILD. 확인 없이 구현을 시작하지 않는다. 이것은 오버헤드가 아니라 안전장치다.

## 진행 원장 (ledger)

`docs/todo_plan/PLAN_{feature}.md`의 `- [ ]` 체크박스가 진행 상태의 **정본**이다. task 완료마다 `[ ]` → `[x]`로 갱신하고, Phase 완료 시 Progress 표와 Execution Log(시각은 `YYYY-MM-DD HH:MM`)를 기록한다.

> 서브에이전트에는 작업 추적 도구가 **없다** (호출 시 `not enabled in this context`). 진행 추적은 반드시 파일 원장으로 한다 — `.github/probes/HARNESS_FACTS.md` P-1.

PLAN 파일이 없으면 PRD 기반으로 계획을 세우고, 구현 완료 후 PLAN 생성을 제안한다.

## 작업 규모 triage — 진입 시 최초 1회

작은 수정에 그린필드용 오케스트레이션(디깅·팀빌드·별도 verifier)을 태워 느려지고 비싸지는 것을 막는다.

| 분류 | 정의 | 신호 |
|------|------|------|
| **quick-fix** | 버그픽스·소규모 수정·문구/설정 변경. 단일 관심사, 새 아키텍처 결정 불요. | "버그", "고쳐", "오타", "~만 바꿔", "롤백"; 예상 변경 ≤2 파일; 기존 코드 국소 수정 |
| **feature** | 기존 코드베이스에 기능 추가. 기존 스택/패턴 위에서 구현. | 단일~소수 팀; 새 모듈 소수; 기존 아키텍처 재사용 |
| **greenfield** | 새 프로젝트 또는 대형 기능. 아키텍처를 새로 정해야 함. | 새 레포/앱; 다수 팀·도메인; 아키텍처 미정; PRD 필수 |

요청 문구 + PRD 존재 여부 + 예상 변경 범위 + 새 아키텍처 필요 여부를 함께 본다. 애매하면 **한 단계 무겁게** 잡는다. 판정은 한 줄로 알린다(예: `triage: quick-fix — 단일 파일 버그픽스로 판단, 경량 경로 진행`).

| 단계 | quick-fix | feature | greenfield |
|------|-----------|---------|-----------|
| PRD 품질 게이트 (Step 0) | PRD 있을 때만 | 예 | 예 |
| 아키텍처 결정 (Step 2) | 스킵 | 조건부(기존 스택 있으면 스킵) | 항상 |
| DESIGN Step 3~5 | 인라인 경량(영향 파일만) | 예 | 예 |
| 디깅 상세검토 (`prd-reviewer`) | 스킵 | 사용자 선택 시만 | 사용자 선택 시만 |
| 사용자 확인 (Step 6) | 예(요약 1줄 + Y/n) | 예 | 예 |
| BUILD | 단일 에이전트 인라인 | 단일~소수 팀 | team-build 병렬 |
| Fresh-context verifier (Step 4.5) | 인라인 self-check | 예 | 예 |

quick-fix가 스킵하는 것은 **오케스트레이션 오버헤드지 안전장치가 아니다** — Step 6 확인과 커밋 전 확인은 그대로 유지한다.

**수동 오버라이드**: `--full`(풀 파이프라인 강제) · `--quick`(경량 경로 강제, greenfield에 쓰면 경고 후 진행). `--parallel`/`--sequential`은 feature/greenfield의 BUILD 모드에만 적용된다.

## 병렬 모드

- **전제**: `feature`/`greenfield`만. `quick-fix`는 항상 단일 에이전트.
- **기본값**: sequential.
- **자동 활성화**: 활성 팀 2개 이상 **또는** BUILD Phase 2개 이상 (Step 5.5 결과). **파일 개수 단독으로는 켜지 않는다** — 병렬 이득은 파일 수가 아니라 독립 팀·Phase 수에서 나온다.
- **병렬 DESIGN**: `Step 0+0.5+1`(읽기 전용) / `Step 2` / `Step 3+4` 를 3개 레인으로 나눠 실행하고 Step 5에서 병합한다. 첫 레인이 **Quality Gate BLOCKED**를 내면 나머지 레인을 즉시 중단한다.
- 활성화 시 현재 모드와 활성 에이전트 수를 한 줄로 표시하고 `--sequential`로 끌 수 있음을 안내한다.

## Usage

```bash
/implement 사용자 인증
/implement FR-006              # PRD 기능 ID로 직접 지정
/implement --parallel 사용자 인증
/implement --quick 오타 수정
/implement --full 로그인 버그
/implement --no-tracker 사용자 인증
```

## Parameters

- `feature-name or FR-ID`: 기능명 또는 기능 ID (required)
- `--quick`: triage를 무시하고 경량 경로(quick-fix) 강제
- `--full`: triage를 무시하고 풀 파이프라인 강제
- `--parallel`: 병렬 모드 강제 활성화 (feature/greenfield BUILD)
- `--sequential`: 순차 모드 강제
- `--full-stack`: (deprecated) 모든 팀 강제 활성화로 매핑
- `--no-tracker`: 이슈 트래커(Linear) 연동을 무시하고 원큐 플로우로 진행
- `--resume`: 저장된 진행 상태에서 마지막 실패 지점부터 재개 (인자 없이 `/implement {feature}` 와 동일)
- `--restart`: 저장된 진행 상태를 버리고 처음부터 다시 실행

---

## DESIGN Phase

> `quick-fix`는 이 Phase를 **인라인 최소 수행**한다 — 영향 파일 Read → 계획 1~3줄 → Step 6 확인. Step 2·디깅·병렬 DESIGN은 건너뛴다.

### Step 0: PRD 품질 검증 (Quality Gate)

`/prd` 실행 시 저장된 prd-reviewer 결과 또는 PRD 메타데이터에서 검증 상태를 읽는다.

| Critical 이슈 | 상태 | 액션 |
|--------------|------|------|
| **0개** | PASS | Step 1로 진행 |
| **1개 이상** | BLOCKED | 구현 중단 |

BLOCKED이면 Critical 이슈(번호·위치·영향)를 나열하고 ① PRD 수정 후 재실행 ② 강제 진행("Critical 무시하고 진행" 입력, 보안 취약점·구현 실패 위험 경고) 중 선택하게 한다.

### Step 0.5: 이슈 트래커 감지 (읽기 전용)

`mcp__linear__*` 도구가 있으면 `issue_tracker = linear`, 없거나 `--no-tracker`면 `none`(원큐 플로우).

연동 감지 시 읽기 전용으로 수집한다:

- `mcp__linear__list_teams` → 팀 1개면 자동 선택, 여러 개면 Step 6에서 선택 요청.
- `mcp__linear__list_projects` → Epic을 어디에 둘지 판단 (Step 7에서 사용).
- `mcp__linear__list_issue_statuses` → **상태 이름은 팀마다 다르므로 글자가 아닌 `type`으로 매칭한다**:
  - `started_state` = `type: "started"` (예: "In Progress", "In Dev")
  - `done_state` = `type: "completed"` (예: "Done", "Shipped")
  - 같은 type이 여러 개면 워크플로우 순서상 첫 번째. 없으면 가장 가까운 상태로 폴백하고 경고.
  - BUILD의 상태 전환은 이 두 변수만 쓴다 — 이름을 하드코딩하지 않는다.

> **쓰기 금지**: 실제 에픽/이슈 생성은 Step 6 승인 이후(Step 7)에만 한다. 이 단계는 읽기 전용이라 병렬 DESIGN의 첫 레인에 포함한다.

결과는 한 줄 요약(예: `Linear 연결됨 · 팀: Engineering`). 미연동이면 "이슈 트래커 미연동 → 원큐 플로우로 진행".

### Step 1: PRD 검색

기능명 또는 `FR-XXX`로 `prd/`, `docs/prd/`, `requirements/`, `specs/` 등에서 PRD를 찾는다. 못 찾으면 ① `/prd [기능명]` 먼저 작성 ② 경로 직접 지정 ③ PRD 없이 진행(권장하지 않음) 중 선택하게 한다.

### Step 2: 아키텍처 결정

> `greenfield`만 항상 수행. `feature`는 기존 스택/아키텍처가 감지되면 그것을 존속하고 스킵. `quick-fix`는 스킵.

`architecture-decision` 에이전트를 호출한다. 입력은 PRD 경로·프로젝트 경로·감지된 기존 스택, 출력은 아키텍처 유형 + 근거 + 추천 스택/패턴 + 주의사항이다. 결과를 요약해 표시한다.

### Step 3~4: 프로젝트 상태 분석

기존 구현 여부, 관련 파일 위치, 사용 중인 패턴·컨벤션을 파악해 **이미 된 부분은 다시 만들지 않는다**. 새 코드는 발견한 컨벤션을 따른다.

**화면정의서가 있으면 읽는다.** `docs/prd/screens/{feature}/` 가 존재하면
`03-SCREEN-SPEC.md`(화면별 상태·컴포넌트)와 `05-DEV-HANDOFF.md`(FR ↔ 화면 ↔ 컴포넌트 매핑)를
Read해 Step 5 계획의 입력으로 쓴다. 없으면 PRD만으로 진행한다.
`/screen-spec` 이 산출물을 내놓아도 여기서 읽지 않으면 그 단계는 값을 하지 못한다.

### Step 5: 구현 계획 수립

생성/수정할 파일을 표로 정리하고 **각 파일에 담당 `FR`을 매핑한다**. 이 매핑이 Step 5.7 이슈 본문의 "구현 범위(파일)"과 BUILD 루프의 작업 범위를 결정하므로, 이슈 트래커 연동 시에는 필수다. 여러 FR이 한 파일을 건드리면 의존성 순서상 **나중 FR 이슈**가 그 파일을 마지막에 커밋한다(앞 FR은 자기 범위만 부분 작성).

### Step 5.5: 팀 할당

| 팀 | 활성화 조건 | Agent |
|-----|-----------|-------|
| Backend | api/, services/, models/, prisma/ 파일 존재 | `backend-architect` |
| Frontend | components/, pages/, app/, styles/ 파일 존재 | `frontend-developer` |
| AI Server | ai/, llm/, stt/, ml/ 파일 또는 PRD에 AI 키워드 | `ai-agent` |
| Ops | Dockerfile, .github/, k8s/ 파일 존재 | (전용 에이전트 없음) |

팀별 활성 여부·task 수·담당 에이전트를 Step 6 확인에 포함한다.

### Step 5.6: 디자인 결정 (Frontend 팀 활성 시)

위에서부터 평가해 해당하면 그 자리에서 결정하고 나머지는 스킵한다.

| 조건 | 액션 |
|------|------|
| PRD에 스타일 명시 (`"스타일: Glassmorphism"`) | design-system-reference에서 해당 스타일 로드 |
| PRD에 브랜드 참조 (`"Stripe처럼"`) | 가장 가까운 스타일 패러다임으로 매핑 |
| 기존 프로젝트에 Tailwind config·theme·디자인 토큰 존재 | 기존 시스템 존속, 스킵 |
| 디자인 정보 없음 | `design-discovery` 에이전트 호출 (질문 3~4개) → 사용자 선택 |

결정 결과(스타일, 스타일 가이드 경로, common 모듈, 테마, 애니메이션 수준, 밀도)를 `frontend-developer`에 전달한다. **스타일 가이드 파일을 읽기 전에 Frontend 코드를 작성하지 않는다.**

### Step 5.7: 이슈 구조 설계 (`issue_tracker = linear` 일 때만)

PRD 구조를 그대로 매핑해 **제안만** 만든다 (생성은 Step 7).

| Linear | 소스 |
|--------|------|
| Epic (부모 이슈) | 기능명 / PRD 제목 — 1개 |
| 하위 이슈 | PRD §FR 각 1개, `parentId` = Epic |
| 의존성 | FR 테이블 Dependencies 컬럼. `FR-002 → FR-001` 이면 FR-002가 FR-001에 `blockedBy` |
| 우선순위 (선택) | FR Priority (P0→Urgent, P1→High, P2→Medium…) |
| 라벨 (선택) | Implementation Phase (MVP/Enhancement 등) |

하위 이슈 본문: **기능**(FR 설명) / **구현 범위(파일)**(Step 5 매핑) / **완료 조건**(acceptance criteria) + `Generated from PRD §{FR-ID}`.

FR 의존성 그래프를 **위상 정렬**해 BUILD 실행 순서를 정한다. 순환이 있으면 경고하고 해당 의존성을 무시하고 진행할지 묻는다.

### Step 6: 사용자 확인 (CHECKPOINT)

기능명, PRD 경로, 생성/수정 파일 목록, 팀 할당, (Frontend 활성 시) 디자인 결정을 요약한 뒤 AskUserQuestion으로 묻는다: **진행(권장)** / **상세 검토** / **수정 필요** / **취소**.

"상세 검토"를 고르면 `prd-reviewer`를 호출해 파일별 예상 구현·의존성·질문·리스크를 받고, 질문에 대한 답변으로 계획을 보완한 뒤 다시 확인받는다.

**`issue_tracker = linear` 일 때 추가 확인** (같은 체크포인트에서 함께):

| 질문 | 선택 | 다음 |
|------|------|------|
| "이번 작업을 Linear 이슈로 관리할까요?" | 예 (권장) | Step 7 → Issue-driven 순차 BUILD |
| | 아니요, 원큐로 진행 | `issue_tracker = none` 전환 → Team/Sequential BUILD |
| "어느 팀에 이슈를 만들까요?" (팀 여러 개일 때만) | `list_teams` 결과로 동적 생성 | — |

### Step 7: 이슈 등록 (Step 6 승인 시에만)

여기서 **처음으로** Linear에 쓰기를 한다.

```
0. Project 결정 — Step 0.5의 list_projects 결과 사용
   기능/레포명과 일치하는 기존 프로젝트 재사용 → 없으면 save_project(name, addTeams=[팀])
   → 워크스페이스가 Project를 안 쓰면 생략하고 Epic만으로 진행
1. save_issue(team, project?, title=<기능명>, description=<PRD 요약 + PRD 경로>) → epic_id
2. for FR in topological_order(FRs):
     save_issue(team, project?, title="FR-XXX <설명>", description=<Step 5.7 템플릿>,
                parentId=epic_id, priority=<매핑>) → fr_issue_id[FR]
3. for FR with deps:
     save_issue(id=fr_issue_id[FR], blockedBy=[fr_issue_id[dep] …])
```

> Linear엔 Jira식 "Epic" 타입이 없다 — **Epic = 부모 이슈**로 표현하고, Project는 그 Epic을 담는 선택적 상위 컨테이너다.

> **Linear 특성**: ① description 마크다운은 Linear가 일부 문자(`~`, `[`, `]`)를 자동 이스케이프하므로 본문은 단순하게 쓴다. ② 하드삭제 API가 없어 롤백·정리는 상태 `Canceled`로 처리한다.

**멱등성(재실행 안전)**: 생성된 이슈 ID를 PLAN 파일 `## Issue Tracker` 섹션(Provider/Team/Project/Epic + `FR | Issue | Depends on | State` 표)에 즉시 기록하고, 재실행 시 이 매핑으로 reconcile 한다.

| 재실행 시 상황 | 동작 |
|---|---|
| 매핑된 이슈가 Linear에 존재 | 새로 만들지 않고 제목/본문/의존성만 업데이트 |
| PRD에 새 FR 추가됨 | 그 FR만 하위 이슈 신규 생성 후 매핑에 추가 |
| PRD에서 FR 사라짐 | 기존 이슈를 자동 삭제하지 않음 (정리는 사용자가 Cancel) |
| 매핑된 이슈가 Canceled/삭제됨 | 사용자에게 알리고 재생성 여부 확인 |

등록 완료 후 Epic + 하위 이슈 트리(식별자·FR·의존 관계)를 요약한다. 등록 실패 시 Error Recovery §7 — 원큐 플로우로 폴백한다.

---

## BUILD Phase

### Issue-driven 순차 BUILD (`issue_tracker = linear` + Step 7 완료 시)

의존성 위상 순서대로 이슈를 **하나씩** 처리한다:

```
for issue in topological_order(sub_issues):   # blockedBy 가 모두 완료된 이슈부터
  1. save_issue(id=issue, state=started_state)      # Step 0.5의 type=started
  2. 해당 FR의 구현 범위(파일) 작성 — Step 5의 FR↔파일 매핑이 범위
     적합한 팀 에이전트 1개에 위임 (Backend/Frontend/AI)
  3. 검증: typecheck / test / build (해당 시)
  4. 커밋 — 이 이슈 변경분만. 메시지에 Linear 식별자 포함(예: "feat: 로그인 API (WIG-101)")
     → Linear가 커밋/PR을 이슈에 자동 연결. 브랜치는 이슈의 gitBranchName 사용 시 연결이 확실
  5. save_issue(id=issue, state=done_state)         # Step 0.5의 type=completed
  6. PLAN 파일 Issue Tracker 표 State 갱신 + Execution Log 기록
```

**왜 순차인가**: 선행 이슈가 Done이 된 뒤 다음을 시작해야 의존성이 지켜진다. 독립 이슈끼리도 기본은 순차 — 이력 추적을 단순하게 유지한다.

**한 이슈 실패 시**: 그 이슈는 시작 상태로 유지 + Execution Log에 오류 기록. 그 이슈에 의존하는 후속은 보류하고, 독립 이슈를 계속 진행할지 사용자에게 확인한다.

**커밋/PR**: 이슈마다 커밋하되 PR은 만들지 않는다. 품질 게이트가 필요하면 마지막에 `/auto-commit` 1회로 Epic 전체 PR을 만든다 (PR 폭주 방지).

### Team BUILD (병렬 모드)

`team-build-coordinator`를 호출해 Step 5.5의 팀 할당대로 실행한다. Coordinator가 수행하는 Phase:

- **Phase 0 Setup**: `SHARED_CONTEXT_{feature}.md` 생성, MEMORY.md로 프로젝트 컨벤션 파악, PLAN 원장에 팀별 Task 등록.
- **Phase 1 Foundation (조건부)**: 다른 팀이 의존하면 Backend 스키마/타입 선행.
- **Phase 2 병렬 실행**: Backend · Frontend · AI Server · Ops 동시 실행.
- **Phase 3 통합 검증**: 빌드 컨텍스트와 독립된 서브에이전트가 API 계약·타입 일관성·파일 충돌 검증.
- **Phase 4 빌드/테스트 검증**: typecheck / test / build, Auto Memory 업데이트.

조율은 SHARED_CONTEXT + PLAN 원장 + Auto Memory로 한다. 오류 시 실패 팀만 순차 재시도하고 독립 팀은 계속 진행한다. `--sequential`이면 Backend → Frontend → AI → Ops 순으로, `--full-stack`(deprecated)이면 알림 후 모든 팀을 활성화한다.

### 순차 BUILD

PLAN 파일이 있으면 Phase 단위로 실행하고, 각 task 시작·완료마다 **원장을 갱신한다**(`[ ]`→`[x]`, Progress 표, Execution Log). PLAN이 없으면 Database/Schema → Backend → Frontend → Tests 순으로 진행한다. 진행률은 현재 Phase + task 상태로 간결히 표시한다.

### Step 4.5: Fresh-Context 검증

> `feature`/`greenfield`만 별도 서브에이전트를 띄운다. `quick-fix`는 인라인 self-check(변경 파일 재확인 + typecheck/test)로 대체한다.

빌드를 수행한 컨텍스트와 **독립된 새 서브에이전트**를 띄운다 (self-critique보다 정확). 구현 과정 로그가 아니라 **PRD 요구사항 + 변경 파일 목록만** 넘긴다.

- 확인: 각 FR이 실제 코드로 충족됐는가 · 계약(시그니처/타입/엔드포인트) 일치 · 명백한 누락/모순
- 출력: FR별 충족/미충족 + 근거(파일:라인). 미충족이 있으면 완료 전에 보완하거나 사용자에게 보고한다.
- **비차단**: 검증자 실행 자체가 실패하면 경고만 남기고 진행한다.

### 완료 및 `/auto-commit` 트리거

| 조건 | 액션 |
|------|------|
| `auto_commit: true` + 모든 Phase 완료 | `/auto-commit` 자동 실행 |
| `auto_commit: false` | 수동 커밋 안내 |
| `commit_per_phase: true` | Phase 완료 시마다 중간 커밋 |

PLAN 파일 Progress를 `completed`로 바꾸고 Execution Log에 트리거·Quality Gate·Commit 결과를 기록한다. `/auto-commit`에는 생성/수정 파일 목록, 구현된 기능, 검증 결과, 실행 모드를 넘긴다.

---

## Error Recovery

자동 복구 가능한 오류는 고쳐서 재검증하고, 불가능하면 오류·원인·해결책을 안내한다. 진행 상태는 PLAN 파일(+ `.claude/session/implement_{feature}.json`)에 저장되어 실패 지점부터 재개된다(`/implement {feature}` 또는 `--resume`, 처음부터는 `--restart`).

1. **아키텍처 결정 실패**: 3회 재시도 → 실패 시 가장 안전한 기본값 제안 또는 수동 선택.
2. **Phase 중간 실패**: 자동 복구 시도(의존성 누락 → 설치, 단순 타입 오류 → 수정 후 재컴파일, 린트 → `code-formatter`, 포트 충돌 → 대체 포트). 불가능하면 수동 개입 안내.
3. **PLAN 파일 동기화 오류**: 파일 시스템 스캔으로 실제 상태 확인 → 불일치 표시 → PLAN 자동 업데이트(권장) / 덮어쓰기 / 수동 확인.
4. **빌드/테스트 실패**: 자동 수정 불가 시 파일·라인·권장 조치를 안내하고 사용자 수정 후 재검증.
5. **롤백**: 부분 롤백(권장, 문제 변경만) / Phase 롤백 / 전체 롤백 / 수동 수정.
6. **이슈 트래커 오류**: 재시도(권장) / `--no-tracker`로 원큐 진행 / 중단. 부분 생성된 이슈는 PLAN `## Issue Tracker`에 기록되어 재실행 시 중복 생성하지 않는다.

**Graceful Degradation**: 이슈 트래커는 보조 기능이다. 연동이 실패해도 구현 자체는 원큐 플로우로 계속 진행한다.

---

## Rules

1. **설계-구현 분리** — Step 6 확인 없이 구현하지 않는다. triage와 무관하게 항상.
2. **기존 코드 수정 시** — 먼저 Read로 현재 구현을 확인하고, 기존 패턴을 따르고, 불필요한 변경을 최소화한다.
3. **진행 추적은 파일 원장으로만** — PLAN 파일이 정본이다.
4. **에러 발생 시** — 즉시 수정하고, 롤백이 필요하면 사용자에게 알린다.
