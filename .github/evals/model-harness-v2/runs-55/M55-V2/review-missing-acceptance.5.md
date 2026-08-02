**산출물 계약 감사**
| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 주요 surface별 상태 정의 |
| Mermaid user or system flow | Present | 신청 → 검증 → PENDING → CANCELLED/APPROVED/REJECTED 흐름 |
| Acceptance precondition/action/result mapped to requirement IDs | Missing | Delivery exit condition은 있으나 FR별 precondition/action/result 형태의 검증 가능한 수락 기준은 없음 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3이 FR ID와 exit condition에 매핑됨 |

**Findings**

**high — FR별 수락 기준이 없어 핵심 요구사항 일부가 검증 불가능함**  
근거: `FR-101`~`FR-106`은 기능 요구를 설명하지만, 계약상 필요한 “precondition / action / result mapped to requirement IDs”가 없다. `Delivery`의 “테스트 통과”는 너무 포괄적이라 어떤 입력, 권한, 실패 조건을 통과해야 하는지 구현자와 QA가 다르게 해석할 수 있다.  
수정 방향: 각 FR에 대해 최소 1개 이상의 Given/When/Then 또는 precondition/action/result 기준을 추가한다. 특히 중복 날짜, 직원 이동, 403/409/503, 멱등 재시도, 감사 이벤트 원자성은 별도 기준이 필요하다.

**high — 멱등성 키의 보안·재시도 의미가 부족함**  
근거: `FR-106`은 “모든 생성·상태 명령은 idempotency key”를 요구하지만 키의 범위, TTL, 동일 키 재사용 시 요청 본문 불일치 처리, actor/session 바인딩, 응답 재현 여부가 없다.  
영향: 다른 사용자나 다른 명령 간 키 충돌, 재시도 시 중복 승인/반려 오인, 본문이 다른 재요청을 정상 재시도로 처리하는 문제가 생길 수 있다.  
수정 방향: idempotency key를 `actor + organization + command type + target/request body hash`에 바인딩하고, 동일 키·동일 본문은 기존 결과 반환, 동일 키·다른 본문은 409, 보관 TTL과 상태 명령별 동작을 명시한다.

**high — 권한 거부 감사 이벤트의 필드 요구가 모순적이거나 정보 노출 위험이 있음**  
근거: `FR-105`는 “권한 거부”도 `request ID, 이전/이후 상태`로 기록한다고 한다. 그러나 권한 거부는 리소스가 없거나, 사용자가 볼 수 없는 요청이거나, 조직 경계 밖일 수 있어 실제 `request ID`와 상태를 기록하거나 노출하는 것이 부적절할 수 있다. `감사자`는 조직 내 이벤트를 읽을 수 있으므로 휴가 요청 존재 여부와 상태가 감사 이벤트를 통해 과도하게 노출될 수 있다.  
수정 방향: 권한 거부 이벤트를 별도 스키마로 분리한다. 예: `target_request_id`는 접근 허용 범위 내에서만 기록하거나 해시/nullable 처리, `previous/next state`는 미해결 또는 미인가 대상에서는 null, denial reason은 coarse-grained로 제한한다.

**medium — 팀 이동 후 상세 조회·사유 열람 권한이 불명확함**  
근거: `FR-104`는 직원 이동 후 “새 팀장이 PENDING 신청을 처리하고 이전 팀장은 접근을 잃는다”고 한다. `Pages and routes`는 상세를 “소유 직원, 현재 팀장”에게 허용하고, `Risks`는 휴가 사유를 “직원 본인과 현재 팀장만” 읽는다고 한다. 하지만 최종 처리된 `APPROVED/REJECTED/CANCELLED` 신청을 직원 이동 후 새 팀장이 볼 수 있는지, 처리 당시 팀장이 이후에도 볼 수 없는지 명확하지 않다.  
영향: 개인정보 노출 범위와 관리 책임 이력이 구현마다 달라질 수 있다.  
수정 방향: 상태별·시점별 조회 권한을 분리해 명시한다. 예: `PENDING`은 현재 팀장, 최종 상태는 소유 직원만 또는 처리 당시 팀장/현재 팀장 중 어느 쪽인지 결정한다.

**medium — 날짜 검증의 기준이 일부 빠져 경계 조건이 흔들림**  
근거: `FR-101`은 KST 달력일, inclusive range, 시작일 ≤ 종료일, `PENDING·APPROVED` 중복 금지를 정의한다. 하지만 과거 날짜 허용 여부, 최대 신청 기간, 조직 휴무일/주말 포함 여부, 날짜 저장 형식이 없다. Non-goal에 급여 연동이 있어 휴일 계산을 제외할 수는 있지만, “일 단위 휴가”의 카운트 기준은 여전히 구현 판단에 남는다.  
수정 방향: 과거일 허용 여부, 최대 연속 일수 또는 제한 없음, 주말/공휴일 포함 여부, 서버 저장 기준을 `KST LocalDate` 같은 형태로 명시한다.

**medium — 인사 시스템 장애 정책이 처리에는 있지만 조회·생성에는 충분히 적용되지 않음**  
근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고 한다. 하지만 `FR-104`는 작업별로 현재 팀을 검사한다고 하므로 팀장 목록 조회(`/team/leave`), 상세 조회(`/leave/:id`의 팀장 접근), 생성 시 신청자의 현재 조직/팀 확인에도 People Platform 의존이 있을 수 있다.  
영향: 일부 API는 장애 시 열려 있거나 캐시된 권한으로 동작할 수 있다.  
수정 방향: People Platform 의존 작업별 장애 동작을 표로 정의한다. 처리, 팀 승인함 조회, 상세 조회, 생성 각각에 대해 fail-closed 여부와 캐시 허용 여부를 명시한다.

**low — 상태 전이 정의는 간결하지만 API별 충돌 응답이 덜 명확함**  
근거: `FR-102`, `State matrix`는 403·409·일시 오류를 언급하지만 어떤 경우가 409인지 구체화되어 있지 않다. 예를 들어 이미 승인된 요청을 취소, 이미 반려된 요청을 승인, 중복 날짜 신청, 동일 멱등 키 본문 불일치가 모두 409인지 구분되지 않는다.  
수정 방향: 상태 명령별 실패 코드를 명시한다. 권한 실패는 403, 상태 불일치는 409, 날짜 충돌은 409, HR 장애는 503처럼 고정하면 테스트 가능성이 높아진다.

검토는 제공된 PRD 본문만 기준으로 했고, 저장소 탐색이나 파일 생성은 하지 않았다.