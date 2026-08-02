**산출물 계약 감사**

| Contract | 적용성 | Status | Evidence |
|---|---:|---|---|
| Applicability ledger | 적용 | Missing | 별도 적용성/비적용성 원장 없음. Non-goals는 있으나 계약별 적용 판단은 없음 |
| Pages and routes | 적용 | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | 적용 | Present | `State matrix` 정의 |
| Mermaid user or system flow | 적용 | Present | 신청부터 취소/승인/반려까지 Mermaid flow 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | 적용 | Present | AC-101~108이 FR ID, Given/When/Then/Verification 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | 적용 | Present | Phase 1~3이 FR ID와 exit condition 포함 |

**Findings**

**High — 취소 기능의 검증 계약이 누락됨**  
근거: 직원 권한에 “대기 취소”, FR-102에 `PENDING -> CANCELLED`, FR-105에 취소 감사 기록이 있지만 AC에는 취소 성공/실패/권한/감사 이벤트 기준이 없습니다. AC-106은 승인과 취소 동시 요청만 다룹니다.  
영향: 핵심 사용자 권한이 구현되어도 승인 조건, 감사 원자성, 이미 처리된 신청 취소 실패, 타인 취소 금지 여부를 검증할 수 없습니다.  
수정 방향: `소유 직원 + PENDING -> CANCELLED + 감사 이벤트 1건`, `타인/비소유 취소 -> 403`, `APPROVED/REJECTED/CANCELLED 취소 -> 409`를 AC와 Delivery exit condition에 추가하세요.

**High — 중복 휴가 생성의 동시성 검증이 부족함**  
근거: FR-101은 `PENDING·APPROVED 신청과 겹칠 수 없다`, FR-106은 생성 명령도 멱등성/조건부 갱신을 사용한다고 하지만 AC-102는 단일 충돌 신청만 검증합니다. AC-106은 상태 변경 동시성만 다룹니다.  
영향: 같은 직원이 동시에 겹치는 기간을 두 번 신청하는 race condition이 통과될 수 있습니다. 이 경우 PRD의 가장 중요한 무결성 규칙이 깨집니다.  
수정 방향: 동시 생성 AC를 추가하고, 검증 방식에 DB exclusion constraint, serializable transaction, per-user date-range lock 등 구현 가능한 원자적 충돌 방지 수단을 요구하세요.

**Medium — 감사 이벤트 스키마가 권한 거부 케이스에 모순적임**  
근거: FR-105는 권한 거부도 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 합니다. 하지만 권한 거부는 존재하지 않는 신청 ID, 타 조직 ID, 목록 조회 거부, HR 장애 등 “이전/이후 상태” 또는 유효한 `request ID`가 없을 수 있습니다.  
영향: 보안상 404/403 구분을 숨겨야 하는 경우에도 감사 이벤트가 리소스 존재를 전제로 하게 되어 구현이 애매하거나 정보 노출 위험이 생깁니다.  
수정 방향: 감사 이벤트 필드를 `action`, `outcome`, `target request ID nullable`, `previous/next state nullable`, `denial reason code`처럼 거부 이벤트에 맞게 분리하세요. 외부 응답은 리소스 존재 여부를 노출하지 않는 정책도 명시하는 편이 좋습니다.

**Medium — 조회 권한과 사유 노출 범위가 화면별로 충분히 검증되지 않음**  
근거: 감사자는 “휴가 사유 전문 읽기 금지”, Risks에는 “휴가 사유는 직원 본인과 현재 팀장만 읽음”이 있습니다. 그러나 `/team/leave` 목록, `/leave/:id` 상세, `/audit/leave` 이벤트에서 어떤 필드가 반환되는지와 레드액션 AC가 없습니다.  
영향: 목록 API나 감사 API에서 사유 전문, 날짜, 직원 식별자 등 민감 정보가 과다 노출될 수 있습니다. 특히 감사자는 조직 내 이벤트를 읽을 수 있어 최소 필드 계약이 필요합니다.  
수정 방향: 화면/API별 반환 필드를 정의하고, 감사자 응답에 사유 전문이 없음을 검증하는 AC를 추가하세요. 팀장 목록에서 사유를 보여줄지 상세에서만 보여줄지도 결정해야 합니다.

**Medium — 직원 이동 외의 People Platform 실패/불일치 상태가 검증 불가능함**  
근거: Authorization에는 HR 실패 시 처리 요청은 `fail-closed 503`이라고 되어 있지만, 조회 요청이나 취소 요청에는 적용 범위가 명확하지 않습니다. 직원이 퇴사, 팀 없음, 팀장 없음, 조직 이동한 경우의 PENDING 처리 정책도 없습니다.  
영향: 오래된 PENDING 신청이 처리 불가 상태로 남거나, 이전 조직/팀에 대한 접근 경계가 구현마다 달라질 수 있습니다.  
수정 방향: HR 조회 실패가 적용되는 작업 범위를 “조회/목록/처리/취소”별로 정하고, 소속 없음·팀장 없음·조직 이동 시 접근 및 처리 결과를 AC로 고정하세요.

**Low — API 지연 목표가 출시 전 결정으로만 남아 NFR 검증이 약함**  
근거: NFR에 “내부 베타 측정 후 제품 책임자가 정식 출시 전에 결정”이라고만 되어 있습니다.  
영향: 현재 PRD 기준으로는 성능 acceptance를 통과/실패 판정할 수 없습니다.  
수정 방향: 지금 수치를 정하지 않더라도 “GA 전 성능 목표가 AC로 갱신되어야 출시 가능” 같은 release gate를 Delivery나 open decision에 명시하세요.

**Open Decisions**

- 감사 이벤트의 최소 필드와 거부 이벤트의 nullable 정책.
- `/team/leave`, `/leave/:id`, `/audit/leave`별 휴가 사유 및 개인정보 반환 필드.
- People Platform 장애/소속 없음/조직 이동 시 조회와 처리의 정확한 응답 정책.
- 겹침 방지를 위한 동시 생성 원자성 보장 방식.