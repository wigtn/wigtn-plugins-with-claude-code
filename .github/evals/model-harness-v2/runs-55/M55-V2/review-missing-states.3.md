**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Missing | Required로 선언했지만 실제 상태 매트릭스가 없음. 오류는 일부 flow/NFR에만 산재 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid flowchart 있음 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~108이 FR ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery` 표가 Phase별 FR ID와 exit condition 포함 |

**Findings**

**High: UI 상태 매트릭스가 Required인데 누락되어 화면 구현·검증 계약이 불완전함**  
영향도: 목록/상세/신청/처리/감사 화면의 empty, loading, error, permission-denied, conflict, retry, success 상태가 구현자마다 달라질 수 있습니다. 특히 409, 403, 503, 입력 유지가 일부 요구에만 흩어져 있어 QA가 일관되게 검증하기 어렵습니다.  
근거: `Applicability`는 State matrix를 Required로 선언하지만 별도 상태 매트릭스가 없습니다. `User flow`에는 “입력 유지와 오류”만 있고, `Authorization`에는 처리 요청 503만 있습니다.  
수정 방향: 페이지별로 `empty/loading/error/success/recovery/permission denied/conflict` 상태를 표로 추가하고, 각 상태의 사용자 액션과 보존 데이터, 재시도 가능 여부를 명시하세요.

**High: 취소 기능의 권한·성공 기준·검증이 부족함**  
영향도: 직원의 PENDING 취소가 핵심 상태 전이인데, 기능 요구와 AC가 승인/반려보다 약합니다. 구현 시 소유자만 취소 가능한지, 팀장이 취소할 수 없는지, 취소 감사 이벤트와 멱등성이 어떻게 검증되는지 빠질 수 있습니다.  
근거: 역할 표와 flow에는 “대기 취소/직원 취소”가 있지만 FR에는 취소 전용 요구가 없습니다. AC도 승인/반려/동시성은 있으나 “직원 본인 PENDING 취소 성공”, “타인 취소 거부”, “CANCELLED 감사 이벤트”를 직접 검증하지 않습니다.  
수정 방향: 취소 FR 또는 FR-102/104 하위 조건으로 `소유 직원만 PENDING 취소 가능`을 명시하고, 성공/권한거부/멱등성 AC를 추가하세요.

**High: 멱등성 키 범위와 재사용 정책이 보안·정합성 관점에서 불명확함**  
영향도: 키가 actor/org/operation/body hash에 묶이지 않으면 다른 요청의 결과 재사용, 중복 이벤트, 교차 사용자 충돌, 승인/반려 재시도 오동작이 생길 수 있습니다.  
근거: FR-106은 “모든 생성·상태 명령은 idempotency key”를 요구하지만 키 scope, TTL, 요청 본문 불일치 처리, 성공/실패 캐싱 범위가 없습니다. AC-108은 신청 재시도만 검증합니다.  
수정 방향: 키를 `organization + actor + command type + target/request body hash` 단위로 제한하고, 동일 키·다른 payload는 409 또는 422로 정의하세요. 승인/반려/취소 재시도 AC도 추가하세요.

**Medium: People Platform 장애 시 fail-closed 범위가 처리 요청에만 한정되어 보임**  
영향도: 팀장 조회, 상세 접근, 감사 범위, 직원 이동 직후 접근권 박탈 같은 권한 판단도 People Platform에 의존한다면 장애 시 보안상 허용/거부 정책이 달라질 수 있습니다.  
근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고만 합니다. 반면 FR-104는 서버가 현재 팀을 작업별로 검사한다고 합니다.  
수정 방향: 생성, 목록, 상세, 승인, 반려, 취소, 감사 조회 각각 People Platform 의존성과 장애 응답을 명시하세요. 권한 확인이 필요한 읽기 작업도 fail-closed인지 정의가 필요합니다.

**Medium: 조회 권한의 최종 상태·직원 이동 후 범위가 모호함**  
영향도: 직원이 팀 이동한 뒤 이전 팀장이 APPROVED/REJECTED 이력 상세를 계속 볼 수 있는지, 새 팀장이 과거 최종 결정 건까지 볼 수 있는지 불분명합니다. 휴가 사유 전문 접근과도 연결되어 개인정보 노출 범위가 달라집니다.  
근거: FR-104는 “직원 이동 후에는 새 팀장이 PENDING 신청을 처리하고 이전 팀장은 접근을 잃는다”고 하지만, 최종 상태 신청의 상세 조회 권한은 정의하지 않습니다. `Pages/routes`는 `/leave/:id`를 “소유 직원, 현재 팀장”으로 둡니다.  
수정 방향: 팀장 상세 조회 범위를 `현재 팀 + PENDING만`, `현재 팀 + 모든 상태`, `결정 당시 팀장 포함` 중 하나로 고정하고 사유 전문 노출 정책을 함께 맞추세요.

**Medium: 권한 거부 감사와 존재 여부 노출 정책이 충돌할 수 있음**  
영향도: 모든 권한 거부를 감사하면서 클라이언트에는 403을 반환하면, 타인의 신청 ID 존재 여부를 추측할 수 있습니다. 반대로 404로 숨기면 감사 이벤트에 어떤 target 정보를 남길지 별도 정책이 필요합니다.  
근거: FR-105는 권한 거부를 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 하고, AC-105는 다른 팀장 또는 본인 신청 처리에 403을 기대합니다. 직원의 타인 조회/처리 시 응답 정책은 없습니다.  
수정 방향: unauthorized 대상 조회/처리의 응답을 403과 404 중 의도적으로 분리하고, 감사 이벤트에는 민감하지 않은 target 식별자만 남기도록 정의하세요.

**Medium: 감사 이벤트 스키마가 추적에 필요한 필드를 충분히 고정하지 않음**  
영향도: “request ID”가 휴가 신청 ID인지 API correlation ID인지 모호하면 감사자가 특정 신청의 생명주기를 재구성하기 어렵습니다. 조직 격리, action type, denial reason code도 빠질 수 있습니다.  
근거: FR-105는 `actor, request ID, 이전/이후 상태, timestamp`만 요구합니다. 감사자는 조직 내 이벤트를 읽지만 이벤트의 `organization_id`, `action`, `target leave id`, `decision reason presence`, `denial code`가 명시되지 않았습니다.  
수정 방향: 감사 이벤트 필드를 `event_id, organization_id, actor_id, action, leave_request_id, previous_status, next_status, timestamp, result, reason_code, correlation_id`처럼 구분하세요. 휴가 사유 전문 제외 원칙은 유지하면 됩니다.

**Medium: 겹침 검사의 대상 범위가 명시되지 않음**  
영향도: PENDING·APPROVED와 겹칠 수 없다는 조건이 같은 직원 기준인지, 같은 조직 전체인지, 같은 팀 기준인지 구현 해석이 갈릴 수 있습니다.  
근거: FR-101은 “PENDING·APPROVED 신청과 겹칠 수 없다”고만 합니다.  
수정 방향: “동일 조직 내 동일 직원의 PENDING 또는 APPROVED 휴가 기간과 겹칠 수 없다”처럼 범위를 명시하세요.

**Low: API 지연 목표는 출시 전 결정 예정이라 현재 PRD만으로는 검증 불가능함**  
영향도: 베타 이후 성능 기준이 정해지기 전까지는 출시 준비 검증에서 통과/실패를 판단할 수 없습니다.  
근거: NFR과 `Assumptions and open decisions`가 API 지연 목표를 추후 결정으로 둡니다.  
수정 방향: 현재는 open decision으로 유지 가능하지만, 정식 출시 exit condition에는 구체 수치와 측정 방식이 필요합니다.

**Low: 날짜 입력의 정규화 규칙이 부족함**  
영향도: 클라이언트가 timestamp를 보내거나 사용자가 해외 시간대에서 접근할 때 KST 달력일 해석이 흔들릴 수 있습니다.  
근거: FR-101은 “KST 달력일”과 inclusive만 정의합니다.  
수정 방향: API는 date-only `YYYY-MM-DD`를 받는지, 서버에서 KST 기준으로 정규화하는지, 저장 타입을 date로 제한하는지 명시하세요.

검증기는 실행하지 않았습니다. 사용자가 파일 생성·저장소 탐색을 금지했고, PRD가 파일 경로가 아닌 본문으로만 제공되었기 때문입니다.