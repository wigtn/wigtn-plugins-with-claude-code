# Dev Handoff — {feature-name}

> **Generated from**: 01-IA.md + 02-USER-FLOW.md + 03-SCREEN-SPEC.md + 04-WIREFRAME.html
> **Target**: `/implement {feature-name}`
> **Created**: {YYYY-MM-DD}

## 1. FR ↔ Screen ↔ Component Mapping

| FR | Description | Screens | Components | Estimated Tasks |
|----|------------|---------|-----------|----------------|
| FR-001 | {요약} | {route-list} | {Component-list} | {sub-task-list} |
| FR-002 | {요약} | {route-list} | {Component-list} | {sub-task-list} |
| FR-003 | {요약} | {route-list} | {Component-list} | {sub-task-list} |

### Coverage Check

- 모든 FR 매핑 여부: {✓ / 누락 항목}
- 모든 화면이 1+ FR 연결 여부: {✓ / 고아 페이지}
- 매핑 누락 FR: {목록 또는 없음}

## 2. Component Inventory

### Reusable (다른 기능에서도 재사용 가능)

- {ComponentName-1} — {역할}
- {ComponentName-2} — {역할}
- {useBreakpoint 또는 공통 hook}

### Feature-specific

- {FeatureForm}
- {FeatureList}
- {FeatureModal}

## 3. State Management

| Scope | Library | Note |
|-------|---------|------|
| Auth | {프로젝트 표준 — Supabase / Auth.js / 자체} | session, user |
| Form | {react-hook-form + zod 등} | {대상 화면} |
| Server data | {TanStack Query / SWR / RTK Query} | {목록/페이지네이션 화면} |
| UI state | {jotai / zustand / Context} | modal, toast 등 |

## 4. Data Fetching Patterns

| Screen | API | Strategy |
|--------|-----|----------|
| {route-1} | {endpoint} | {query / mutation / optimistic} |
| {route-2} | {endpoint} | {query + filter} |
| {route-3} | {endpoint} | {query + pagination} |

## 5. Routing

```
app/
├── page.tsx                    # {route-1}
├── {slug-2}/page.tsx           # {route-2}
└── {slug-3}/page.tsx           # {route-3}
```

Auth middleware: `middleware.ts` — {보호 대상 라우트 패턴}.

> **모바일(`--platform=mobile`)인 경우**: 라우팅이 React Navigation Stack/Tab/Drawer 구조로 변환됨. 화면명을 라우트 키 대신 NavigatorScreenName으로 사용.

## 6. Suggested Implementation Order

Task Plan(`docs/todo_plan/PLAN_{feature-name}.md`)에 반영할 순서:

1. **Phase 1: Foundation**
   - 프로젝트 부트스트랩 (프레임워크 + 스타일)
   - 데이터 레이어 / 마이그레이션
   - 인증

2. **Phase 2: {Primary User} Path**
   - {핵심 화면 1}
   - {핵심 화면 2}
   - {보조 요소}

3. **Phase 3: {Secondary User} Path**
   - {관리/제한 화면}
   - {익스포트 또는 부가 기능}

4. **Phase 4: Polish**
   - 반응형 마무리
   - 에러 처리 / 빈 상태
   - 부가 기능 (P1/P2)

## 7. Open Questions Carried Over

01-IA / 02-USER-FLOW / 03-SCREEN-SPEC에서 결정되지 않은 항목 통합:

- [ ] {결정 보류 항목 1}
- [ ] {결정 보류 항목 2}

**규칙**: 이 질문들은 구현 전에 결정하거나, 결정 보류 시 명확한 미결정 사항으로 기록한다. 사용자 요청 없이 코드 TODO를 자동 생성하지 않는다.

## 8. Acceptance Mapping for /implement

`/implement`가 PRD Acceptance Criteria(§2.2)를 task로 분해할 때 참조:

| Scenario | Implementation Tasks |
|----------|---------------------|
| Scenario A | {FR-list} tasks |
| Scenario B | {FR-list} tasks |
| Scenario C | {FR-list} tasks |

## 9. Interview Decisions (선택, `--interview` 플래그 사용 시)

| 의사결정 | 선택 | 적용 화면 |
|---------|------|----------|
| 네비게이션 패턴 | {top/side/bottom/drawer} | 전체 |
| 정보 밀도 | {compact/spacious} | 목록/테이블 화면 |
| 에러 톤 | {공식/친근} | 모든 에러 메시지 |
| 빈 상태 철학 | {일러스트/최소} | empty state 화면 |
| 전환 방식 | {page/modal/drawer} | 폼/상세 |
| 모바일 우선순위 | {desktop-first/mobile-first/parity} | 반응형 분기 |
| 첫 화면 후크 | {value/action/story} | 랜딩 |
