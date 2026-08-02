**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판단함 |
| Pages and routes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 Empty/Loading/Error/Success/Recovery 열 존재 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid lifecycle flow 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `Acceptance criteria`가 AC별 FR ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery`가 Phase별 Requirement IDs와 exit condition을 포함 |

**Findings**

| Impact | Finding | 근거 | 수정 방향 |
|---|---|---|---|
| High | 직원 취소 동작이 P0 상태 전이에 포함되지만 권한·검증·수용 기준이 불완전함 | 역할 표는 직원에게 `대기 취소`를 허용하고, FR-102는 `PENDING -> CANCELLED`를 허용하며, flow도 직원 취소를 포함함. 그러나 FR에는 “소유 직원만 본인 PENDING 신청을 취소 가능” 같은 명시 요건이 없고, AC에는 정상 취소·취소 감사 이벤트·취소 후 재취소/승인 시도 검증이 없음. AC-106은 동시성 케이스일 뿐 취소 기능 자체의 acceptance가 아님 | FR-102 또는 별도 FR에 취소 권한과 상태 조건을 명시하고, 정상 취소/비소유자 취소 거부/이미 최종 상태 취소 실패/감사 이벤트를 AC로 추가 |
| High | 기간 겹침 방지가 동시 신청에서 원자적으로 보장되는지 검증 불가능함 | FR-101은 `PENDING·APPROVED 신청과 겹칠 수 없다`고 하지만, FR-106의 조건부 갱신은 “생성·상태 명령”에 대한 일반 문장이고 겹침 검사와 삽입이 어떤 단위로 원자화되는지 불명확함. AC-102는 기존 겹침만 다루며, 같은 직원이 동시에 겹치는 두 신청을 생성하는 경쟁 조건을 검증하지 않음 | FR-101/FR-106에 “동일 소유자 기준 겹침 검사와 생성은 직렬화 가능 트랜잭션, exclusion constraint, 잠금 등으로 원자 보장”을 명시하고 동시 생성 AC 추가 |
| Medium | 감사 이벤트 스키마가 권한 거부와 감사 조회 요구를 충족하기에 부족함 | FR-105는 `actor, request ID, 이전/이후 상태, timestamp`만 요구함. 권한 거부 이벤트에는 상태 변경이 없으므로 이전/이후 상태 의미가 모호하고, 어떤 action이었는지, denied reason category, target/request owner, org/team scope가 없으면 AC-105의 “권한 거부 감사”와 `/audit/leave` 조회가 실무적으로 검증하기 어려움 | 감사 이벤트 필드에 `action`, `outcome`, `reason_code`, `target_leave_id`, `target_owner_id`, `org_id`, `actor_role` 등 최소 검색·감사 필드를 정의. 거부 이벤트의 before/after는 동일 상태 또는 null 정책을 명시 |
| Medium | 감사자 권한과 휴가 상세 접근 경계가 서로 어긋날 여지가 있음 | 역할 표에서 감사자는 `조직 내 감사 이벤트 읽기`만 가능하고 `휴가 사유 전문 읽기`는 금지됨. 그러나 `/audit/leave`의 이벤트 조회 결과 필드, request ID 노출 후 상세 API 접근 가능 여부, 감사자가 `/leave/:id` 접근 불가인지가 명시되지 않음 | 감사자는 `/leave/:id` 접근 불가 또는 redacted detail만 가능하다고 명시하고, 감사 이벤트 응답에서 휴가 사유·민감 필드 제외 및 request ID를 통한 우회 조회 금지를 acceptance에 추가 |
| Medium | People Platform 장애 정책이 조회와 처리에 불균등하게 정의되어 사용자 상태 검증이 흐림 | `Authorization and data boundaries`는 인사 시스템 실패 시 “처리 요청은 fail-closed 503”이라고만 함. 그런데 FR-103/104와 AC-107은 현재 팀장 조회·처리 모두 People Platform의 현재 팀 관계에 의존함. `/team/leave` 목록과 `/leave/:id` 팀장 조회에서 People Platform 장애 시 빈 목록, 캐시 사용, 503 중 무엇인지 불명확함 | People Platform 의존 작업을 조회/처리/감사로 나누어 fail-closed 정책, 캐시 허용 여부, UI recovery 상태를 명시. AC에 팀장 목록·상세 조회 시 인사 시스템 장애 케이스 추가 |

**Open Decisions**

- 휴가 기간이 주말·공휴일을 포함한 단순 KST 달력일인지, 근무일 기준 계산인지 결정이 필요합니다.
- 휴가 잔여일수 검증은 non-goal에 없지만 실제 승인 도메인에서는 핵심일 수 있습니다. 이번 PRD 범위에서 제외라면 명시적으로 non-goal에 넣는 편이 구현 해석을 줄입니다.