**산출물 계약 감사**

| Contract | Applicability | Status | Evidence |
|---|---:|---:|---|
| Applicability ledger | Applicable | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 표시함 |
| Pages and routes | Applicable | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Applicable | Missing | 원문은 “State matrix Required”라고 했지만 실제 상태 매트릭스는 없음 |
| Mermaid user or system flow | Applicable | Present | `User flow`에 Mermaid flowchart 있음 |
| Acceptance precondition/action/result mapped to requirement IDs | Applicable | Present | AC-101~AC-108이 FR ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Applicable | Present | `Delivery`가 Phase별 Requirement IDs와 exit condition을 포함 |

**Findings**

`high` 상태 매트릭스가 필수인데 누락되어 화면 동작 검증이 불가능합니다.  
근거: `Applicability`는 State matrix를 Required로 선언하지만, 목록·폼·상세·승인함·감사 이력의 empty/loading/error/success/recovery 상태가 정의되어 있지 않습니다.  
영향: 구현자가 “입력 유지와 오류”, HR 장애 503, 권한 거부, 빈 목록, 중복 신청 409, 감사 조회 제한 등을 화면별로 다르게 해석할 수 있고 QA가 누락 상태를 판정하기 어렵습니다.  
수정 방향: 각 route별로 최소 `initial/loading/empty/validating/success/validation error/authorization denied/conflict/server dependency failure/retry or recovery` 상태와 사용자에게 보이는 결과를 표로 추가하세요.

`high` 팀장의 조회 권한 범위가 모순 또는 과소정의되어 있습니다.  
근거: Role 표는 팀장에게 “현재 팀 직원 신청 조회·승인·반려”를 허용하고, `/leave/:id`도 “현재 팀장” 조회를 허용합니다. 반면 FR-103은 “현재 팀 직원 PENDING 신청만 처리”라고 하며, `/team/leave`는 “대기 신청 조회”입니다.  
영향: 팀장이 `APPROVED`, `REJECTED`, `CANCELLED` 상세를 계속 볼 수 있는지, PENDING만 볼 수 있는지, 직원 이동 후 과거 결정 건을 누가 볼 수 있는지 구현마다 달라집니다. 휴가 사유 노출 범위와도 연결되는 보안 문제입니다.  
수정 방향: 팀장 조회 권한을 상태별로 분리하세요. 예: “현재 팀장은 현재 팀 직원의 PENDING 상세만 조회 가능” 또는 “결정 당시 팀장/현재 팀장/감사자별 조회 범위”를 명시해야 합니다.

`medium` 감사자 요구사항은 있지만 acceptance criteria가 없습니다.  
근거: Role 표와 `/audit/leave`는 감사자 기능을 정의하고, FR-105는 감사 이벤트 필드를 정의합니다. 그러나 AC-101~AC-108에는 감사자가 이벤트를 조회할 수 있는지, 휴가 사유 전문을 볼 수 없는지, 상태 변경을 못 하는지 검증하는 항목이 없습니다.  
영향: 가장 민감한 개인정보 경계인 “사유 전문 미노출”이 구현·테스트 계약에서 빠집니다.  
수정 방향: 감사자 조회 AC를 추가해 이벤트 필드, 조직 범위, 사유 전문 비포함, 상태 변경 403을 검증하세요.

`medium` 권한 거부 감사 이벤트의 데이터 모델이 모호합니다.  
근거: FR-105는 권한 거부도 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 하지만, 존재하지 않는 request ID, 타 조직 request ID, 또는 enumeration 방지를 위해 request 존재 여부를 숨겨야 하는 경우의 이전/이후 상태가 정의되어 있지 않습니다.  
영향: 403/404 전략과 감사 이벤트가 충돌할 수 있고, 감사 로그가 타 조직 신청 ID 존재를 누설할 수 있습니다.  
수정 방향: 권한 거부 이벤트에는 `target_request_id` 기록 가능 여부, `previous_state/next_state = null` 허용 여부, cross-org 접근 시 응답 코드와 감사 기록 정책을 명시하세요.

`medium` 겹침 검사의 기준 범위가 불명확합니다.  
근거: FR-101은 PENDING·APPROVED 신청과 겹칠 수 없다고 하지만 “본인 신청” 기준인지, 조직/팀 기준인지 문장상 명확하지 않습니다.  
영향: 잘못 구현하면 같은 팀의 다른 직원 휴가와 충돌 처리하거나, 반대로 본인 기존 휴가만 막아야 하는 요구를 놓칠 수 있습니다.  
수정 방향: “동일 조직 내 동일 직원의 PENDING 또는 APPROVED 신청 기간과 겹칠 수 없다”처럼 충돌 도메인을 명시하세요.

`medium` 멱등성 키 범위와 보존 정책이 검증 불가능합니다.  
근거: FR-106과 AC-108은 idempotency key를 요구하지만 키가 actor별인지, operation별인지, request payload와 불일치하면 409인지 422인지, 보존 기간이 얼마인지 없습니다.  
영향: 재시도 안정성, 중복 이벤트 방지, 키 재사용 공격 방지 정책이 구현자 재량이 됩니다.  
수정 방향: 키 scope를 `actor + operation + idempotency key` 등으로 정의하고, 동일 키·동일 payload와 동일 키·다른 payload의 결과를 각각 명시하세요.

`low` API 지연 목표가 정식 출시 전 결정으로 남아 있어 출시 판정에는 약합니다.  
근거: NFR와 Open decisions에 “내부 베타 종료일까지/정식 출시 전에 결정”이라고 되어 있습니다.  
영향: PRD 자체로는 성능 acceptance를 검증할 수 없습니다. 다만 현재 범위가 내부 베타라면 즉시 blocker는 아닙니다.  
수정 방향: 베타 exit condition과 GA exit condition을 분리하고, GA 전에는 측정 기준과 승인자를 AC 또는 Delivery에 연결하세요.

**종합**

PRD는 상태 전이, 서버 권한 검사, HR fail-closed, 감사 원자성, 동시성 제어 같은 핵심 백엔드 계약은 비교적 탄탄합니다. 가장 큰 결함은 선언된 화면 상태 매트릭스가 실제로 없다는 점과, 팀장 조회 범위·감사자 검증·권한 거부 감사 정책처럼 개인정보와 권한 경계에 닿는 부분이 아직 판정 가능하게 닫히지 않았다는 점입니다.