**계약 감사**

| Contract | Status | Applicability / Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 선언함 |
| Pages and routes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`가 있음. 다만 감사 이력 화면 상태는 빠져 있음 |
| Mermaid user or system flow | Missing | 다단계 생명주기라 적용 대상이며 Applicability에서도 User flow Required라고 했지만 Mermaid flow 산출물은 없음 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~AC-108이 FR ID와 Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3이 Requirement IDs와 exit condition을 포함 |

**Findings**

**blocker - 필수 User Flow 계약이 적용 대상인데 산출물이 없음**  
영향도: 구현팀이 상태 생명주기, 권한 주체 전환, 감사 기록 타이밍을 동일하게 이해했는지 검증하기 어렵습니다. 특히 직원 신청, 팀장 승인/반려, 직원 취소, 팀 이동 후 새 팀장 처리, 감사 이벤트 생성이 여러 actor와 시스템에 걸쳐 있습니다.  
근거: `Applicability`에서 `User flow`를 Required로 선언했지만, PRD Review Contract상 요구되는 `Mermaid user or system flow`가 없습니다.  
수정 방향: 신청 생성부터 `PENDING -> APPROVED/REJECTED/CANCELLED`까지의 actor별 Mermaid flow를 추가하고, People Platform 조회 실패, 팀 이동, 권한 거부 감사 기록 지점을 포함하세요.

**high - 취소 기능이 역할 표와 상태 정의에는 있으나 기능 요구사항·AC가 불완전함**  
영향도: 직원의 `PENDING` 취소가 실제 제품 요구인지, 어떤 API/권한/검증/감사 조건을 가져야 하는지 구현자가 추론해야 합니다. `AC-106`의 승인과 취소 동시 요청도 독립 취소 요구가 없어 검증 기반이 약합니다.  
근거: `Users, roles, and permissions`는 직원에게 `대기 취소`를 허용하고, `FR-102`는 `PENDING`에서 `CANCELLED` 전이를 허용합니다. 하지만 `Functional requirements`에는 취소 actor, 취소 가능 조건, 취소 사유 여부, 취소 권한 검사에 대한 별도 FR이 없습니다. `Acceptance criteria`에도 단독 취소 성공/실패 케이스가 없습니다.  
수정 방향: 직원 본인만 `PENDING` 신청을 `CANCELLED`로 전이할 수 있다는 FR과 AC를 추가하세요. `APPROVED/REJECTED/CANCELLED` 취소 시 409, 타인 취소 시 403, 감사 이벤트 생성 여부를 명시하세요.

**high - 감사 이벤트의 권한 거부 기록 요구가 보안·정보노출과 충돌할 수 있음**  
영향도: 접근 권한이 없는 요청에 대해 `이전/이후 상태`를 기록하려면 대상 신청의 존재나 상태를 조회해야 할 수 있습니다. 이 과정이 응답, 로그, 감사 조회를 통해 ID 존재 여부나 상태를 노출할 위험이 있습니다.  
근거: `FR-105`는 `권한 거부`도 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 합니다. 반면 직원은 타인 신청 조회 금지, 팀장은 타 팀 처리 금지이며 감사자는 휴가 사유 전문 읽기가 금지됩니다.  
수정 방향: 권한 거부 감사 이벤트는 대상 리소스를 확인할 수 없는 경우 `previous_state`/`next_state`를 `UNKNOWN` 또는 `null`로 기록하도록 분리하세요. 감사자에게 보이는 필드와 내부 보안 로그 필드도 구분하는 것이 좋습니다.

**high - 겹침 방지의 동시성 검증 방식이 구현 가능 수준으로 충분하지 않음**  
영향도: 동시에 두 개의 신청이 생성되면 둘 다 기존 PENDING/APPROVED와 겹치지 않는다고 판단하고 삽입될 수 있습니다. 이 경우 `FR-101`의 중복 금지가 깨집니다.  
근거: `FR-101`은 PENDING·APPROVED 신청과 겹칠 수 없다고 하고, `FR-106`은 모든 생성·상태 명령에 idempotency key와 조건부 갱신을 요구합니다. 하지만 신규 신청 간 날짜 범위 충돌을 막는 DB 제약, 직렬화 트랜잭션, advisory lock, exclusion constraint 같은 검증 가능한 전략은 없습니다.  
수정 방향: “같은 조직·직원 기준 날짜 구간 겹침은 트랜잭션 안에서 직렬화되며, 경쟁 생성 중 하나는 409가 된다”처럼 관찰 가능한 요구를 추가하세요. 구현 방식은 DB 제약 또는 명시적 잠금 중 하나로 열어둘 수 있습니다.

**medium - 멱등성 키의 범위와 payload 불일치 처리가 정의되지 않음**  
영향도: 같은 idempotency key가 다른 사용자, 조직, 요청 본문, 다른 명령에서 재사용될 때 잘못된 신청 ID 반환, 중복 이벤트, 또는 보안 경계 혼동이 생길 수 있습니다.  
근거: `FR-106`과 `AC-108`은 idempotency key 사용과 같은 신청 ID 반환만 말합니다. 키 scope, 보존 기간, 요청 fingerprint mismatch 시 응답, actor/org/request type별 분리 규칙은 없습니다.  
수정 방향: idempotency key는 `organization + actor + command type + key` 범위로 고유해야 하며, 동일 키에 다른 payload가 오면 409 또는 422로 실패한다고 명시하세요. 보존 기간도 운영 요구로 결정해야 합니다.

**medium - 감사 이력 화면은 route가 있으나 상태·권한·검색 요구가 부족함**  
영향도: 감사자가 무엇을 조회할 수 있는지, 조직 범위가 어떻게 제한되는지, 거부 이벤트와 상태 이벤트가 어떤 필드로 노출되는지 구현마다 달라질 수 있습니다.  
근거: `/audit/leave` route는 있지만 `State matrix`에는 감사 이력 surface가 없습니다. `Users, roles, and permissions`는 감사자에게 조직 내 감사 이벤트 읽기를 허용하지만 `Authorization and data boundaries`는 주로 신청 작업 기준이고 감사 조회의 필터, 페이지네이션, reason redaction 검증은 없습니다.  
수정 방향: 감사 이력 목록의 empty/loading/error/success/recovery 상태와, 감사 조회의 조직 경계·필드 redaction·필터 조건·페이지네이션 요구를 추가하세요.

**medium - People Platform 실패 처리 범위가 모호함**  
영향도: 팀장 처리 요청은 fail-closed 503으로 명확하지만, 목록/상세 조회에서 People Platform 장애가 나면 이전 팀장 접근을 허용할지, 새 팀장 접근을 막을지, 직원 본인 조회는 허용할지 판단이 갈립니다.  
근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고만 합니다. `FR-104`는 직원 이동 후 새 팀장이 처리하고 이전 팀장은 접근을 잃는다고 하므로 조회 권한도 People Platform 의존성이 있습니다.  
수정 방향: 팀장 목록·상세·처리 각각에서 People Platform 실패 시 응답을 정의하세요. 직원 본인 조회처럼 People Platform이 필요 없는 경로와 팀장 권한 경로를 분리하면 검증 가능합니다.

**low - API 지연 목표가 출시 전 결정으로 남아 있어 NFR로는 검증 불가능함**  
영향도: 현재 PRD만으로는 성능 합격/불합격을 판단할 수 없습니다. 다만 내부 베타 후 결정이라는 일정은 명시되어 있어 출시 전 open decision으로 관리하면 됩니다.  
근거: `Non-functional requirements`와 `Assumptions and open decisions`에 API 지연 목표는 내부 베타 종료/정식 출시 전 결정이라고 되어 있습니다.  
수정 방향: 지금은 “출시 차단 open decision”으로 표시하고, 베타 종료 시점에 측정 기준, percentile, 대상 API, 데이터 규모를 확정하는 AC 또는 release gate를 추가하세요.