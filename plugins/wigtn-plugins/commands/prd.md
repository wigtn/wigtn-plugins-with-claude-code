---
description: |
  Generate structured PRD documents from vague feature requests.

  Trigger keywords:
  - Commands: "/prd", "PRD 작성해줘", "기능 정의서", "요구사항 문서"

  - Natural language (바이브 코더 친화):
    - "~하는거 만들고 싶어", "~하는 기능 필요해"
    - "~할 수 있게 해줘", "~하는 앱 만들어줘"
    - "~하는 서비스 기획해줘", "이런 거 가능해?"
    - "아이디어가 있는데", "기능 추가하고 싶어"
    - "~하는 사이트 만들어줘", "~하는 시스템 구축해줘"
---

# PRD Generation

모호한 기능 요청을 구조화된 PRD 문서로 변환한다.

파이프라인: `/prd` → `prd-reviewer` → (FE 페이지 있으면) `/screen-spec` → `/implement` → `/auto-commit`

## Step 1 — 계약을 먼저 읽는다 (건너뛰지 않는다)

**`${CLAUDE_PLUGIN_ROOT}/contracts/PRD-CONTRACT.md`를 Read한다.**
PRD 골격·섹션 조건·Critical 항목은 전부 그 파일에 있다. 이 커맨드는 그것을 재진술하지 않는다.

## Step 2 — 문서 유형과 규모

- **문서 유형** 판정: `product-feature` | `internal-backend` | `refactor` (섹션 활성 규칙은 계약 §문서 유형).
  모호하면 AskUserQuestion. 판정 결과를 PRD 헤더 `> **Type**:` 에 쓴다.
- **Scale Grade**: AskUserQuestion으로 `Hobby | Startup | Growth | Enterprise` 중 선택받는다
  (`refactor`는 생략). 등급 경계는 계약 §4.0.

## Step 3 — 프로젝트 컨텍스트

기존 PRD(`prd/`, `docs/prd/`), 기술 스택(`package.json` 등), API·컴포넌트·스키마 구조를 확인해
PRD가 실제 코드베이스와 어긋나지 않게 한다.

## Step 4 — 작성

계약의 골격대로 PRD를 쓴다. 문장 규칙:

1. **구체적으로** — "카테고리별 필터링" (O) / "검색 가능" (X)
2. **측정 가능하게** — "p95 < 200ms" (O) / "빠른 응답" (X)
3. **검증 가능하게** — 모든 스토리에 수용 기준
4. API 명세는 Request / Response / Error를 모두 정의한다.
   REST 외(GraphQL / gRPC / WebSocket / OpenAPI) 템플릿이 필요하면
   `${CLAUDE_PLUGIN_ROOT}/commands/references/prd-api-templates.md`를 읽는다.

## Step 5 — 저장

AskUserQuestion으로 위치 확인: `docs/prd/` (권장) | `prd/` | 루트.

이어서 실행 계획을 `docs/todo_plan/PLAN_{feature-name}.md`로 생성한다.
PRD의 §6 Implementation Phases를 Phase로, §3 FR을 Task로 매핑하고 **의존성 순서대로** 배치한다.
각 Task는 `- [ ]` 체크박스로 쓴다 — 이 파일이 `/implement`의 진행 원장(ledger)이다.

## Step 6 — 검증 (Quality Gate)

`prd-reviewer` 에이전트를 실행한다. 판정은 **findings 롤업**이다:

| 결과 | 조건 | 다음 |
|---|---|---|
| ❌ BLOCKED | Critical ≥1 | 수정 후 재검증 |
| ✅ PASS | Critical 0 | `/implement` 진행 가능 |

Critical은 위치 / 문제 / 영향 / 개선안 4줄로 제시한다. Major·Minor는 건수만 요약한다.

## Step 7 — 다음 단계

§5.4 Pages에 `Has FE Components: Yes` 행이 **1개 이상이면** `/screen-spec {feature}` 권장,
아니면 곧바로 `/implement {feature}`. PRD 경로·PLAN 경로·게이트 결과·감지된 FE 페이지 수를 함께 보고한다.
