**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Missing | Applicability에서는 Required라고 했지만 실제 빈 목록·로딩·오류·성공·복구 상태 매트릭스가 없음 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid flowchart 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~AC-108이 FR ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3이 FR ID와 exit condition을 포함 |

**Findings**

1. **medium — 필수 상태 매트릭스가 누락되어 화면 구현·검증 기준이 비어 있음**  
   영향: `/leave`, `/team/leave`, `/audit/leave`, 상세 화면에서 빈 목록, 로딩, 403/503, 충돌 409, 성공 후 복구 동작을 구현자가 임의 해석하게 됩니다. 특히 PRD가 People Platform 장애 시 fail-closed 503과 입력 유지까지 요구하므로 복구 상태는 검증 가능해야 합니다.  
   근거: `Applicability`는 State matrix를 Required로 표시하지만, 실제 `Empty/loading/error/success/recovery state matrix`가 없습니다.  
   수정 방향: 화면별로 최소 `empty`, `loading`, `error`, `success`, `recovery/retry` 상태와 사용자에게 유지되어야 하는 입력값, 재시도 가능 여부, 권한 오류 표시 범위를 표로 추가하세요.

2. **high — 조회/list 작업의 People Platform 장애·권한 실패 동작이 불명확함**  
   영향: 팀장 상세 조회와 팀 승인함 목록은 “현재 팀장 관계” 확인에 People Platform이 필요하지만, 장애 시 처리 요청만 503이라고 되어 있습니다. 조회가 fail-open 되면 타 팀/이전 팀장 접근 위험이 있고, fail-closed 여부가 검증되지 않으면 구현마다 보안 경계가 달라집니다.  
   근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고만 합니다. 반면 FR-104는 “서버는 조직·현재 팀·신청 소유자·현재 상태를 작업별로 검사”한다고 하며, Pages에는 팀장 조회 화면이 있습니다.  
   수정 방향: 생성, 직원 본인 조회, 팀장 목록, 팀장 상세, 승인/반려 각각에 대해 People Platform 장애 시 응답과 상태 유지, 감사 기록 여부를 명시하세요. 현재 팀장 판정이 필요한 모든 작업은 fail-closed로 통일하는 편이 안전합니다.

3. **medium — 취소 기능의 acceptance coverage가 부족함**  
   영향: 직원의 `PENDING` 취소는 권한표와 상태 흐름에 있는 핵심 상태 전이지만, 성공/실패/동시성/감사 이벤트 검증 기준이 없습니다. 구현이 빠져도 현재 AC만으로는 잡기 어렵습니다.  
   근거: 권한표는 “직원: 대기 취소”, Mermaid는 `PENDING -> CANCELLED`, FR-102는 PENDING에서 CANCELLED 전이를 허용합니다. 그러나 AC-101~AC-108에는 직원 취소 성공, 비소유자 취소 거부, 이미 처리된 신청 취소 409에 대한 기준이 없습니다.  
   수정 방향: 취소 성공 AC, 승인/반려 후 취소 409 AC, 타인 취소 403 AC를 추가하고 각각 상태 불변 및 감사 이벤트 기대값을 명시하세요.

4. **medium — 멱등성 요구가 생성에만 검증되어 상태 명령의 재시도 안전성이 검증 불가능함**  
   영향: 승인/반려/취소 요청에서 네트워크 재시도나 중복 제출이 발생하면 중복 감사 이벤트, 잘못된 409, 또는 서로 다른 결과 재생이 생길 수 있습니다. FR-106은 모든 생성·상태 명령을 요구하지만 AC는 신청 재시도만 확인합니다.  
   근거: FR-106 “모든 생성·상태 명령은 idempotency key…” vs AC-108 “같은 idempotency key 재시도 | 신청”. AC-103/104/106은 상태 명령의 동일 키 재시도를 다루지 않습니다.  
   수정 방향: 승인, 반려, 취소 각각에 대해 같은 actor·same key·same payload 재시도는 같은 결과를 반환하고 중복 이벤트가 없어야 한다는 AC를 추가하세요. key scope도 조직, actor, operation, payload hash 기준으로 고정하세요.

5. **medium — 감사 이벤트 스키마가 권한 거부·실패 케이스에 과도하거나 모호함**  
   영향: “권한 거부”에도 request ID, 이전/이후 상태를 기록하라고 되어 있어, 접근 권한이 없는 요청의 존재·상태를 감사 로그나 로그 파이프라인에 불필요하게 노출할 수 있습니다. 반대로 존재하지 않는 ID나 조직 밖 ID의 거부 이벤트에서는 이전/이후 상태를 채울 수 없어 요구가 구현 불가능해집니다.  
   근거: FR-105는 “생성·승인·반려·취소와 권한 거부를 actor, request ID, 이전/이후 상태, timestamp로 기록”한다고 합니다. 권한표는 직원의 타인 신청 조회·처리를 금지하고, 감사자는 휴가 사유 전문을 읽을 수 없다고만 되어 있습니다.  
   수정 방향: 감사 이벤트 타입별 필드를 분리하세요. 권한 거부는 `attempted_request_id` 또는 redacted ID, action, actor, timestamp, denial reason category 정도로 제한하고, 리소스가 안전하게 확인된 경우에만 previous/next state를 허용하는 식으로 명시하는 게 안전합니다.

검토는 제공된 PRD 원문만 대상으로 했고, 요청대로 저장소 탐색·파일 생성·검증 스크립트 실행은 하지 않았습니다.