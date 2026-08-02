**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow 적용성을 표시함 |
| Pages and routes | Missing | 직원 신청/팀장 처리 화면 존재는 언급하지만 실제 페이지, route, 주요 화면 책임이 정의되지 않음 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix` 표 존재 |
| Mermaid user or system flow | Present | `User flow` Mermaid 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~AC-108이 FR ID와 Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery` 표가 Phase별 FR ID와 exit condition 포함 |

**Findings**

`high` 팀장 본인 신청은 승인 경로가 없다.  
근거: FR-103과 AC-105는 팀장이 본인 신청을 처리하지 못한다고만 하고, 대체 승인자나 위임 승인 경로가 없다. 팀장도 직원이라면 본인 휴가가 `PENDING`에서 영구 정체될 수 있다.  
수정 방향: 본인 신청의 처리 주체를 상위 관리자, 위임 팀장, HR 관리자 등으로 명시하고 권한·감사·AC를 추가해야 한다.

`high` 동시 생성의 날짜 중복 방지가 검증 가능하게 정의되지 않았다.  
근거: FR-101은 `PENDING·APPROVED`와 겹칠 수 없다고 하고 FR-106은 조건부 갱신을 요구하지만, 신규 신청 간 동시 생성에서 같은 기간 중복을 막는 구체 조건이 없다. AC-106은 승인/취소 동시성만 검증한다.  
수정 방향: 생성 시 동일 사용자·조직·기간에 대한 트랜잭션 격리, range/exclusion constraint, 잠금 전략 중 하나를 제품 계약으로 지정하고 동시 생성 AC를 추가해야 한다.

`high` idempotency 범위와 재사용 규칙이 불명확하다.  
근거: FR-106은 모든 생성·상태 명령에 idempotency key를 요구하지만 AC-108은 신청만 검증한다. key가 actor별인지, operation별인지, payload mismatch 재사용 시 409인지 422인지, TTL이 있는지 정의되지 않았다.  
수정 방향: key scope, 저장 기간, 동일 key+다른 payload 처리, 승인/반려/취소 재시도 결과를 명시하고 각 상태 명령 AC를 추가해야 한다.

`medium` 직원 이동 후 과거/최종 신청 조회 권한이 모순적으로 해석될 수 있다.  
근거: FR-104는 직원 이동 후 새 팀장이 `PENDING` 신청을 처리하고 이전 팀장은 접근을 잃는다고 한다. AC-107은 “새 팀장만 접근·처리”라고 더 넓게 말한다. 이미 `APPROVED/REJECTED/CANCELLED` 된 신청과 휴가 사유를 누가 계속 볼 수 있는지 불명확하다.  
수정 방향: 조회 권한을 `현재 팀 기준`인지 `결정 당시 팀 기준`인지 상태별로 분리하고, 휴가 사유 노출 정책까지 AC에 반영해야 한다.

`medium` 취소 기능의 독립 수용 기준이 빠졌다.  
근거: 역할 표와 FR-102는 직원의 `PENDING` 취소를 허용하고 FR-105는 취소 감사 이벤트를 요구하지만, AC에는 정상 취소, 취소 권한 거부, 비-PENDING 취소 검증이 없다. AC-106은 승인과 취소 경합만 다룬다.  
수정 방향: 직원 본인의 `PENDING -> CANCELLED`, 타인 취소 403, 최종 상태 취소 409, 감사 이벤트 검증 AC를 추가해야 한다.

`medium` People Platform 장애의 fail-closed 범위가 처리 요청에 치우쳐 있다.  
근거: Authorization 섹션은 “처리 요청은 fail-closed 503”이라고만 한다. 하지만 팀장 조회, 상세 접근, 직원 이동 후 접근 회수도 현재 팀 관계에 의존한다.  
수정 방향: People Platform 의존 작업 전체를 생성/목록/상세/처리별로 나누고 장애 시 503, 캐시 사용 여부, stale 데이터 허용 여부를 명시해야 한다.

`medium` 감사 이벤트의 `request ID` 의미가 모호하다.  
근거: FR-105는 `request ID` 기록을 요구하지만 이것이 휴가 신청 ID인지 HTTP correlation/request ID인지 불분명하다. 권한 거부 이벤트에서는 대상 휴가 ID가 없거나 노출하면 안 되는 경우도 있다.  
수정 방향: `leaveRequestId`, `correlationId`, `idempotencyKey hash` 등 필드를 분리하고, 대상 리소스가 존재하지 않거나 숨겨야 하는 403/404 케이스의 감사 필드를 정의해야 한다.

`medium` Pages/routes 계약이 적용 가능하지만 누락됐다.  
근거: Applicability에서 직원 신청과 팀장 처리 화면이 있다고 했고 state matrix도 화면 단위로 존재하지만, 실제 routes, 화면별 권한, 주요 액션, 진입 조건이 없다.  
수정 방향: 최소한 내 휴가 목록/상세/신청, 팀장 승인 목록/상세, 감사 이벤트 조회 화면 또는 API-only 여부를 명시해야 한다.

`low` API 지연 목표가 출시 전 검증 계약으로 닫히지 않았다.  
근거: NFR과 Open decisions는 내부 베타 후 결정한다고만 하며, 정식 출시 전 어떤 문서/AC/게이트로 확정되는지 없다.  
수정 방향: “베타 종료일까지 latency SLO를 별도 릴리스 체크리스트에 확정하고 미확정 시 GA 불가”처럼 검증 가능한 exit condition을 추가하면 된다.

검토는 제공된 PRD 원문만 기준으로 했고, 요청대로 저장소 탐색·파일 생성·검증 스크립트 실행은 하지 않았습니다.