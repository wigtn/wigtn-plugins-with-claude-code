**산출물 계약 감사**

| Contract | 적용성 | Status | Evidence |
|---|---:|---|---|
| Applicability ledger | 적용 | Present | `Assumptions and open decisions`, `Non-goals`, `Risks and mitigations`가 범위와 미결정을 분리함 |
| Pages and routes | 적용 | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | 적용 | Present | `State matrix` 표 존재 |
| Mermaid user or system flow | 적용 | Present | `User flow` Mermaid 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | 적용 | Present | AC-101~AC-108이 FR ID, Given/When/Then/Verification 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | 적용 | Present | `Delivery` 표가 Phase, Requirement IDs, exit condition 포함 |

**Findings**

**High — 상세 화면 권한/행동이 요구사항과 충돌합니다.**  
근거: `Users, roles, and permissions`는 직원만 “본인 … 대기 취소” 가능하고 팀장은 “승인·반려”만 가능하다고 합니다. 그런데 `Pages and routes`의 `/leave/:id`는 “소유 직원, 현재 팀장”에게 `조회·취소·처리`를 primary action으로 둡니다. 이 문구대로면 현재 팀장이 취소할 수 있는 것처럼 해석됩니다.  
영향: 구현자가 팀장 취소 API/UI를 열 수 있고, 감사·상태 전이 정책도 달라집니다.  
수정 방향: `/leave/:id`의 action을 역할별로 분리하세요. 예: 소유 직원은 `조회·PENDING 취소`, 현재 팀장은 `조회·승인·반려`, 팀장은 `취소 불가`.

**High — 상태 명령의 멱등성 검증이 생성에만 닫혀 있습니다.**  
근거: FR-106은 “모든 생성·상태 명령은 idempotency key”를 요구하지만 AC-108은 “같은 idempotency key 재시도 | 신청”만 검증합니다. 승인, 반려, 취소의 같은 키 재시도, 같은 키 다른 payload, 같은 키 다른 actor/resource 케이스가 없습니다.  
영향: 승인/반려/취소에서 중복 감사 이벤트, 잘못된 재처리, 키 재사용 취약점이 생겨도 AC로 잡히지 않습니다.  
수정 방향: 상태 명령별 멱등성 AC를 추가하고, idempotency key scope를 명시하세요. 최소한 `actor + organization + operation + target request` 단위인지, 같은 키에 다른 payload가 오면 `409` 또는 `422`인지 정해야 합니다.

**High — 감사자의 “조직 내 감사 이벤트” 범위가 다중 조직/관리 권한 모델에 비해 과합니다.**  
근거: `Users, roles, and permissions`는 감사자가 “조직 내 감사 이벤트 읽기” 가능하다고만 하고, `Authorization and data boundaries`도 세션 조직만 언급합니다. 감사자가 전체 조직 감사 로그를 읽어도 되는지, 팀/부서/권한 범위가 있는지, actor 식별자·request ID가 개인정보로 취급되는지 불명확합니다.  
영향: 조직 규모가 크거나 감사 권한이 세분화되어야 하는 환경에서 과다 노출이 됩니다. 휴가 사유 전문은 제외해도 휴가 신청 존재, 기간, 행위자, 거부 이벤트 자체가 민감 정보일 수 있습니다.  
수정 방향: 감사자 scope를 명시하세요. 예: `organization-wide auditor`인지, 특정 조직 단위 auditor인지. 감사 이벤트 조회 필드와 필터 가능 범위도 AC에 포함해야 합니다.

**Medium — 권한 거부 감사 이벤트의 원자성/장애 처리 기준이 불명확합니다.**  
근거: FR-105는 “권한 거부”를 감사 기록한다고 하고, FR-106은 “상태와 감사 이벤트” 원자성을 말합니다. 하지만 권한 거부는 상태 변경이 없으므로 어떤 트랜잭션 경계와 실패 정책을 적용하는지 빠져 있습니다. AC-105는 403과 권한 거부 감사를 기대하지만, 감사 기록 실패 시 요청을 403으로 반환할지 503으로 실패시킬지 불명확합니다.  
영향: 보안 감사 누락 또는 사용자 응답과 감사 기록 간 불일치가 생길 수 있습니다.  
수정 방향: 권한 거부 이벤트도 감사 저장 실패 시 fail-closed인지, 별도 outbox로 보장하는지 명시하세요.

**Medium — People Platform 장애 정책이 조회와 처리에 다르게 필요한데 처리 요청만 정의되어 있습니다.**  
근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고 합니다. 그러나 FR-104는 조회도 현재 팀/소유자/조직을 작업별로 검사한다고 하며, `/team/leave`, `/leave/:id` 조회 역시 현재 팀장 관계에 의존합니다.  
영향: People Platform 장애 중 팀 승인함 또는 상세 조회가 stale 권한으로 열릴지, 503으로 닫힐지 구현마다 달라집니다.  
수정 방향: 조회, 목록, 처리 각각의 People Platform 장애 정책을 명시하세요. 권한 판단이 필요한 조회도 fail-closed인지 결정해야 합니다.

**Medium — 휴가 기간 충돌 검증의 동시 생성 케이스가 AC에 없습니다.**  
근거: FR-101은 PENDING·APPROVED와 겹칠 수 없다고 하고 FR-106은 조건부 갱신을 요구하지만, AC-106은 “승인과 취소 동시 요청”만 다룹니다. 같은 직원이 겹치는 두 신청을 동시에 생성하는 경우가 없습니다.  
영향: 가장 중요한 데이터 무결성인 중복 휴가 신청 방지가 레이스에서 깨질 수 있습니다.  
수정 방향: 동시 생성 충돌 AC를 추가하세요. 예: 두 요청 중 하나만 PENDING 생성, 다른 하나는 409, 성공 감사 이벤트는 하나만 존재.

**Medium — 반려 사유의 저장·노출·감사 정책이 불완전합니다.**  
근거: FR-103은 반려 사유 1~500자만 요구하고, Risks는 “휴가 사유”를 로그·감사 이벤트에 넣지 않는다고만 합니다. 반려 사유가 직원에게 노출되는지, 감사 이벤트에 전문 또는 요약이 들어가는지, 로그 제외 대상인지 불명확합니다.  
영향: 반려 사유에 민감정보가 들어갈 수 있고, 감사자 금지 범위가 “휴가 사유 전문”에만 한정되어 반려 사유가 과다 노출될 수 있습니다.  
수정 방향: 반려 사유의 reader, audit/log 포함 여부, 마스킹 여부를 휴가 사유와 별도로 정의하세요.

**Low — API 지연 목표가 출시 전 결정으로 남아 있어 현재 PRD만으로 성능 acceptance가 불가능합니다.**  
근거: NFR과 Open decisions 모두 “내부 베타 후/종료일까지 결정”이라고 합니다.  
영향: 베타 전 구현 검증에는 문제 없지만, 정식 출시 readiness 기준으로는 측정 가능한 통과 조건이 없습니다.  
수정 방향: 현재 단계에서는 “N/A for Phase 1~3”로 두거나, 출시 게이트 AC로 별도 ID를 부여해 결정 책임자와 결정 시점을 명확히 하세요.

검토는 제공된 PRD 원문만 대상으로 했고, 요청대로 저장소 탐색·파일 생성·원문 재작성은 하지 않았습니다.