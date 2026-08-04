---
name: team-memory-protocol
description: 팀 빌드 간 공유 컨텍스트 관리 프로토콜. SHARED_CONTEXT 파일 생성/관리, PLAN 원장 연동, Auto Memory 업데이트 규칙을 정의합니다.
allowed-tools: Read, Write, Edit, Glob
---

# Shared Memory Protocol

팀 기반 병렬 빌드에서 팀 간 데이터 공유를 위한 3계층 메모리 관리 프로토콜입니다.

## 3-Layer Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  3계층 공유 메모리 구조                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Auto Memory (MEMORY.md)                           │
│  ├── 지속성: 세션 간 영구 지속                               │
│  ├── 용도: 프로젝트 컨벤션, 패턴, 아키텍처 결정              │
│  ├── 읽기: 빌드 시작 시 (모든 팀)                            │
│  └── 쓰기: 빌드 완료 후 (Coordinator만)                      │
│                                                             │
│  Layer 2: SHARED_CONTEXT (파일 기반)                         │
│  ├── 지속성: 빌드 세션 동안 (완료 후 참조용 유지)            │
│  ├── 용도: API 계약, 공유 타입, 환경변수, 진행 상태          │
│  ├── 읽기: 빌드 중 (모든 팀)                                 │
│  └── 쓰기: Coordinator + Backend 팀만                        │
│                                                             │
│  Layer 3: PLAN 원장 (docs/todo_plan/PLAN_{feature}.md)       │
│  ├── 지속성: 파일 — 세션이 끝나도 남는다                     │
│  ├── 용도: 팀별 진행 추적, 의존성 관리                       │
│  ├── 읽기: 모든 팀 / 쓰기: Coordinator                       │
│  └── 형식: `- [ ]` 체크박스 + blocked-by 주석                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## SHARED_CONTEXT 파일 관리

### 파일 경로

```
docs/shared/SHARED_CONTEXT_{feature_name}.md
```

### 생성 템플릿

```markdown
# SHARED_CONTEXT: {feature_name}
> team-build-coordinator 자동 생성. 팀 간 조율용.
> 생성일: {timestamp}
> 기능: {feature_name}

## API Contract
| Method | Path | Request Type | Response Type | Owner |
|--------|------|-------------|--------------|-------|

## Shared Types
<!-- TypeScript interfaces/types 공유 -->
<!-- Backend 팀이 정의, 다른 팀이 import하여 사용 -->

## Environment Variables
| Variable | Required By | Description |
|----------|------------|-------------|

## Integration Points
| From | To | Type | Description |
|------|-----|------|-------------|

## Team Progress
| Team | Status | Tasks | Completion | Last Update |
|------|--------|-------|------------|-------------|
```

### 쓰기 권한 규칙

```yaml
write_permissions:
  coordinator:
    sections: ["Team Progress", "Integration Points"]
    timing: "Phase 0 생성, Phase 2 중 업데이트, Phase 3 최종 확인"

  backend_team:
    sections: ["API Contract", "Shared Types", "Environment Variables"]
    timing: "Phase 1 (Foundation) + Phase 2 (Parallel)"
    rules:
      - "API 엔드포인트 추가/변경 시 API Contract 업데이트"
      - "공유 타입 생성 시 Shared Types에 기록"
      - "환경 변수 추가 시 Environment Variables에 기록"

  other_teams:
    sections: []
    access: "읽기 전용"
    rules:
      - "API Contract을 참조하여 API 호출 구현"
      - "Shared Types를 import하여 타입 일관성 유지"
      - "Environment Variables를 참조하여 설정 파일 작성"
```

### 충돌 방지

```yaml
conflict_prevention:
  strategy: "섹션별 소유권"
  rules:
    - "각 섹션은 하나의 소유자만 수정 가능"
    - "API Contract: Backend 팀 소유"
    - "Shared Types: Backend 팀 소유"
    - "Team Progress: Coordinator 소유"
    - "Integration Points: Coordinator 소유"
  fallback:
    - "충돌 감지 시 Coordinator가 수동 병합"
    - "Backend 팀의 API 정의가 우선"
```

## PLAN 원장 연동 프로토콜

> **왜 도구가 아니라 파일인가**: 서브에이전트 컨텍스트에는 `TodoWrite`도 `Task*`도 없다
> (프로브 확정 — `.github/probes/HARNESS_FACTS.md` P-1). 없는 도구에 진행 추적을 걸면
> 조용히 아무것도 기록되지 않는다. 원장은 파일이므로 어느 컨텍스트에서도 동작한다.

### 팀별 Task 등록

```yaml
task_naming:
  format: "[{TEAM_PREFIX}-{NNN}] {description}"
  prefixes:
    BACKEND: "BE"
    FRONTEND: "FE"
    AI_SERVER: "AI"
    OPS: "OP"

  examples:
    - "[BE-001] prisma/schema.prisma - User 모델 추가"
    - "[FE-001] src/components/LoginForm.tsx - 로그인 폼"
    - "[AI-001] src/ai/transcribe.ts - STT 엔드포인트"
    - "[OP-001] Dockerfile - 멀티스테이지 빌드"
```

### Task metadata

```yaml
metadata_schema:
  team: "BACKEND | FRONTEND | AI_SERVER | OPS"
  files:
    - "file1.ts"
    - "file2.ts"
  phase: "foundation | parallel | integration | verification"
  depends_on: ["BE-001"]        # 다른 팀 Task 의존성
```

### 의존성 관리

```yaml
dependency_rules:
  - description: "Frontend → Backend 스키마 의존"
    from: "FE-*"
    to: "BE-001 (스키마)"
    type: "blockedBy"
    resolution: "Phase 1에서 Backend 스키마 선행"

  - description: "AI Server → Backend API 계약 참조"
    from: "AI-*"
    to: "BE-* (API 계약)"
    type: "soft_dependency"
    resolution: "SHARED_CONTEXT의 API Contract 참조"

  - description: "Ops → 모든 팀 완료 후 최종 설정"
    from: "OP-* (CI/CD)"
    to: "BE-*, FE-*"
    type: "soft_dependency"
    resolution: "환경 변수 목록만 참조, 코드 독립"
```

## Auto Memory 업데이트 프로토콜

### 업데이트 시점

```yaml
timing:
  read: "Phase 0 (빌드 시작)"
  write: "Phase 4 검증 통과 후"
  skip: "검증 실패 시 업데이트하지 않음"
```

### 업데이트 규칙

```yaml
update_rules:
  add_items:
    - "새로 확립된 아키텍처 패턴 (예: Repository pattern)"
    - "성공한 팀 간 API 계약 구조"
    - "기술 스택 결정사항 (새 라이브러리 도입 등)"
    - "발견된 프로젝트 컨벤션 (네이밍, 폴더 구조)"

  skip_items:
    - "세션별 임시 데이터 (진행률, 타임스탬프)"
    - "SHARED_CONTEXT의 실시간 상태"
    - "빌드 로그, 에러 트레이스"
    - "이미 MEMORY.md에 있는 정보"

  format:
    - "기존 MEMORY.md 구조를 유지"
    - "200줄 제한 준수"
    - "중복 항목 추가하지 않음 (같은 교훈 반복 금지)"
    - "구체적이고 재사용 가능한 정보만 기록"
    - "교훈은 항목당 1개로 분리 (한 항목에 여러 교훈을 섞지 않음)"
    - "각 항목은 요약을 앞에 두고, 왜 중요했는지(맥락)를 한 줄 덧붙임"
    - "틀린 것으로 판명된 과거 기록은 삭제하거나 정정"
```

### 과거 세션 Reflect (Phase 0 부트스트랩)

빌드 시작(Phase 0)에 MEMORY.md를 읽을 때, 과거 세션에서 기록된 교훈(패턴·함정·아키텍처 결정)을 먼저 reflect하여 이번 빌드에 반영합니다. 이번 기능과 관련된 교훈이 있으면 요약해 `SHARED_CONTEXT`의 Project Patterns에 전달하여 모든 팀이 참조하게 합니다.

### 업데이트 예시

```markdown
## 빌드 전 MEMORY.md:
- Project uses Next.js 14 + Prisma

## 빌드 후 추가:
- Auth: JWT + bcrypt, Repository pattern
- API: RESTful, /api/v1/ prefix convention
- Shared types: src/types/shared.ts for cross-module types
- [교훈] Prisma는 `$transaction` 인터랙티브 형태 사용 — 배열형에서 중첩 write 부분 커밋 이슈 있었음 (왜: 롤백 누락 위험)
```
