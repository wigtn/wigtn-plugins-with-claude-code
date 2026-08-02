## 산출물 계약 감사

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 존재하며 Pages/routes, State matrix, User flow를 Required로 분류했다. 다만 Acceptance criteria와 Delivery phases의 적용성은 빠져 있다. |
| Pages and routes | Present | `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave`와 허용 역할·주요 동작이 정의되어 있다. |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`가 존재한다. 다만 팀 승인함·감사 이력 등 일부 화면의 상태 계약은 누락됐다. |
| Mermaid user or system flow | Present | 신청 검증부터 PENDING 및 세 가지 최종 상태 전이가 Mermaid로 표현되어 있다. |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~108이 Given/When/Then/Verification 및 FR ID와 연결되어 있다. |
| Delivery phases mapped to requirement IDs and exit conditions | Missing | 단계별 출시 범위, 연결된 FR ID, 진입·종료 조건이 없고 N/A 근거도 없다. |

## 주요 Findings

### 1. High — 동시 생성 시 기간 중복 금지가 깨질 수 있다

- 근거: `FR-101`, `FR-106`, `AC-102`, `AC-106`
- 영향: 동일 직원이 서로 다른 idempotency key로 겹치는 두 신청을 동시에 생성하면, 양쪽 모두 기존 중복이 없다고 판단한 뒤 PENDING으로 저장될 수 있다. `FR-106`의 조건부 갱신은 기존 신청의 상태 경쟁은 막을 수 있지만, 아직 존재하지 않는 두 신규 레코드 사이의 기간 불변식까지 보장한다고 검증할 수 없다.
- 수정 방향:
  - “동일 조직·직원에 대해 PENDING/APPROVED 날짜 범위 중복 검사가 원자적으로 직렬화된다”는 관찰 가능한 서버 불변식을 명시한다.
  - 서로 다른 키로 겹치는 신청을 동시에 보냈을 때 정확히 하나만 성공하고 나머지는 409이며, 신청·감사 이벤트도 하나만 생성되는 AC를 추가한다.
  - 구현 수단은 DB 제약, 잠금, 직렬화 트랜잭션 등으로 열어두되 요구 결과는 고정한다.

### 2. High — 직원 이동과 승인 경쟁에서 “승인 시점의 현재 팀장”을 판정할 기준이 없다

- 근거: `FR-103`, `FR-104`, `AC-107`, Authorization and data boundaries
- 영향: People Platform 조회 직후 직원이 이동하고 그 사이 승인 트랜잭션이 커밋되면 이전 팀장의 승인이 성립할 수 있다. 현재 AC-107은 이동이 끝난 뒤의 순차 상황만 검증하므로 이 경쟁 조건을 판정하지 못한다.
- 수정 방향:
  - 권한 판정의 기준 시점을 명시한다. 예: 커밋 직전 재검증, 멤버십 버전 일치, 또는 People Platform이 제공하는 권한 스냅숏 기준.
  - 이동과 승인 요청이 동시에 발생한 경우 허용되는 단 하나의 결과를 정의한다.
  - 캐시 사용 여부, People Platform 응답의 유효성 판정, 중간 실패 시 상태·감사 이벤트 결과를 AC로 고정한다.

### 3. High — 권한 실패 응답과 감사 이벤트가 리소스 존재·민감 상태를 노출할 수 있다

- 근거: 역할 표, `FR-104`, `FR-105`, `AC-105`, `/leave/:id`
- 영향:
  - AC-105는 다른 팀장의 접근에 403을 요구하지만 존재하지 않는 ID나 타 조직 ID의 응답 정책은 없다. 응답이 다르면 신청 ID 존재 여부를 열거할 수 있다.
  - 권한 거부 이벤트에도 이전/이후 상태를 요구하는 것으로 읽히지만, 접근 권한이 없는 신청의 상태를 감사 이벤트에 복제하면 감사자에게 불필요한 휴가 메타데이터가 노출될 수 있다.
  - 조직 밖 접근 시 어느 조직의 감사 경계에 기록되는지도 불명확하다.
- 수정 방향:
  - 소유권·팀·조직 불일치와 미존재 리소스에 대한 비열거 응답 정책을 정의한다.
  - 권한 거부 이벤트의 최소 스키마를 별도로 정의하고, 휴가 상태·사유 등 대상 정보는 권한 판정에 필요한 범위 이상 기록하지 않도록 한다.
  - 감사 조회의 조직 경계와 거부 이벤트 귀속 규칙을 명시하고 보안 테스트를 추가한다.

### 4. High — P0 멱등성·감사 요구가 생성 외 명령에서는 검증 불가능하다

- 근거: `FR-105`, `FR-106`, `AC-101`~`AC-108`, Non-functional requirements
- 영향:
  - `FR-106`은 생성·승인·반려·취소 모두를 대상으로 하지만 AC-108은 생성 재시도만 다룬다.
  - 키의 범위, 같은 키에 다른 payload를 사용했을 때의 결과, 동시 재시도, 키 유효기간이 정의되지 않았다.
  - transactional outbox를 허용하면서 AC는 “이벤트 한 건”을 요구한다. 논리적 이벤트의 유일성과 전달 중복 제거 기준이 없어 구현별로 합격 결과가 달라질 수 있다.
  - 정상 취소, 취소 권한 실패, 승인·반려 재시도에 대한 직접 AC도 없다.
- 수정 방향:
  - 각 명령별로 동일 키·동일 payload, 동일 키·다른 payload, 동시 중복 요청의 결과를 정의한다.
  - 키의 격리 범위와 재사용 정책을 명시한다.
  - “이벤트 한 건”이 저장된 논리 이벤트 한 건인지 소비자가 관찰하는 전달 한 건인지 구분하고, event ID 또는 동등한 중복 판정 기준을 둔다.
  - 취소와 권한 거부 감사의 성공·실패·원자성 AC를 추가한다.

### 5. Medium — 출시 계약과 화면 상태 계약이 불완전하며 지연 목표 결정 시점도 일치하지 않는다

- 근거: `Applicability`, Pages and routes, State matrix, Non-functional requirements, Assumptions and open decisions
- 영향:
  - Required인 화면 중 `/team/leave`와 `/audit/leave`의 empty/loading/error/success/recovery가 없다. 직원 상세의 최종 상태와 접근 상실 상황도 명확하지 않다.
  - Delivery phases가 없어 P0 요구사항의 출시 단위와 종료 조건을 확인할 수 없다.
  - API 지연 목표 결정 시점이 한 곳에서는 “정식 출시 전”, 다른 곳에서는 “내부 베타 종료일까지”로 달라 책임자가 준수해야 할 마감이 불명확하다.
- 수정 방향:
  - 네 개 페이지 각각에 필요한 사용자 가시 상태와 복구 동작을 보완한다.
  - 최소한 베타와 정식 출시 단계별 포함 FR/AC 및 종료 조건을 정의하거나, 단계 구분이 불필요하다면 Applicability ledger에 N/A 근거를 명시한다.
  - 지연 목표의 단일 결정 마감과 승인 책임자를 하나의 표현으로 통일한다.

검토는 제공된 PRD 본문만 대상으로 했으며, 저장소 탐색·파일 생성·실행 검증은 수행하지 않았다.