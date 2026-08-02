**프로젝트 산출물 계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 표시함 |
| Pages and routes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`가 Empty/Loading/Error/Success/Recovery를 포함 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid flowchart 포함 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~AC-108이 FR ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Missing | 단계별 delivery phase, 각 phase의 포함 FR, exit condition이 없음 |

**Findings**

**High — 관리자 상세 조회 권한이 최종 상태·직원 이동 후 개인정보 경계를 모호하게 만든다**  
영향: 휴가 사유는 민감정보일 수 있는데, “현재 팀장” 기준만으로 상세 조회를 허용하면 직원 이동 후 새 팀장이 과거 신청 사유를 읽거나, 반대로 당시 승인 책임자가 처리 이력을 확인하지 못하는 상황이 생긴다. 특히 `Pages and routes`의 `/leave/:id`는 “소유 직원, 현재 팀장”에게 조회를 허용하고, `Risks and mitigations`는 “휴가 사유는 직원 본인과 현재 팀장만 읽음”이라고 한다. 반면 FR-104는 직원 이동 후 이전 팀장이 접근을 잃고 새 팀장이 PENDING 신청을 처리한다고만 하며, 최종 상태 신청의 조회 권한은 정의하지 않는다.  
근거: `Pages and routes`, FR-104, `Risks and mitigations`.  
수정 방향: PENDING 처리 목적의 상세 조회와 최종 상태 이력 조회를 분리해야 한다. 예: PENDING은 현재 팀장만 사유 열람·처리, APPROVED/REJECTED/CANCELLED는 직원 본인과 “처리 당시 승인권자” 또는 별도 감사 권한만 제한 조회. 직원 이동 후 과거 사유 열람 정책을 명시한다.

**High — 겹침 방지의 동시성 보장이 검증 가능하지 않다**  
영향: FR-101은 PENDING·APPROVED 신청과 겹칠 수 없다고 하지만, FR-106의 “조건부 갱신”은 주로 상태 변경에는 충분해도 신규 신청 간 겹침 경쟁을 막는 방식으로는 불명확하다. 동시에 두 개의 겹치는 신청이 생성되면 둘 다 PENDING이 될 수 있는지 검증 기준이 없다.  
근거: FR-101, FR-106, AC-101, AC-102.  
수정 방향: 생성 시 겹침 검사를 원자적으로 보장하는 요구를 추가한다. 예: 조직+직원+기간 기준 exclusion constraint, serializable transaction, advisory lock, 또는 동등한 DB 제약. AC에 “동시 겹침 신청 중 하나만 성공, 다른 하나는 409, 성공 이벤트는 1건”을 추가한다.

**Medium — 권한 거부 감사 이벤트의 필수 필드가 상태 변경 이벤트와 맞지 않는다**  
영향: FR-105는 권한 거부도 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 하지만, 권한 거부는 조회 대상이 없거나 접근 자체가 금지될 수 있어 이전/이후 상태를 기록할 수 없거나 기록하면 정보 노출이 될 수 있다. AC-105는 권한 거부 감사를 요구하지만 이벤트 스키마가 모호하다.  
근거: FR-105, AC-105, `Authorization and data boundaries`.  
수정 방향: 감사 이벤트 타입별 필드를 분리한다. 권한 거부는 `actor`, `operation`, `target_type`, `target_id` 가능 여부, `denial_reason_code`, `timestamp`, `correlation_id`를 기록하고, 상태는 “대상이 존재하고 열람 권한이 있는 경우에만” 또는 “redacted”로 정의한다.

**Medium — 감사 이벤트의 `request ID` 의미가 모호해 추적성과 테스트가 흔들린다**  
영향: `request ID`가 HTTP 요청 correlation ID인지 휴가 신청 ID인지 불명확하다. 전자라면 감사 이벤트가 어떤 휴가 신청에 대한 것인지 추적이 부족하고, 후자라면 재시도·멱등성·운영 추적을 위한 correlation ID가 부족하다.  
근거: FR-105, AC-101, AC-103, AC-108.  
수정 방향: `leave_request_id`, `idempotency_key_hash`, `correlation_id` 또는 `command_id`처럼 목적별 식별자를 분리한다. 감사 조회 AC에도 신청 ID 기준 필터링 또는 이벤트 연계 검증을 넣는다.

**Medium — 감사자 권한은 “조직 내 감사 이벤트 읽기”인데 조직 경계와 사유 비노출 검증이 부족하다**  
영향: 감사자는 상태 변경 이력은 봐야 하지만 휴가 사유 전문은 금지되어 있다. 그러나 `/audit/leave`의 필터, 조직 범위, 이벤트 redaction, actor/target 개인정보 노출 수준이 acceptance criteria로 검증되지 않는다.  
근거: `Users, roles, and permissions`, `Pages and routes`, FR-105.  
수정 방향: 감사자 조회 AC를 추가한다. 예: 감사자는 같은 조직 이벤트만 조회 가능, 타 조직 이벤트는 403/404, 휴가 사유 필드는 응답·로그·이벤트 payload에 없음.

**Medium — Delivery phases 계약이 누락되어 구현 범위 절단과 출시 판정이 어렵다**  
영향: 적용 가능한 산출물 계약인데 phase별 요구사항·exit condition이 없다. P0가 많고 감사 원자성, 인사 시스템 연동, 동시성, 감사자 화면까지 포함되어 있어 한 번에 구현할 경우 베타 출시 기준이 불명확하다.  
근거: 산출물 계약 감사표, 전체 FR/AC.  
수정 방향: 예: Phase 1 신청·직원 조회·취소, Phase 2 팀장 처리·인사 권한, Phase 3 감사 이력·장애 주입·운영 검증처럼 FR/AC를 매핑하고 각 phase별 테스트 통과 조건을 둔다.

**Low — API 지연 목표가 출시 전 결정으로 남아 있어 현재 PRD 단계에서는 검증 불가능하다**  
영향: 정식 출시 전 결정한다고 되어 있으나, 현재 acceptance criteria에는 성능 측정 방식이나 책임 시점이 없다. 기능 구현 자체를 막지는 않지만 출시 readiness에서 공백이 된다.  
근거: `Non-functional requirements`, `Assumptions and open decisions`.  
수정 방향: 수치가 아직 없다면 “베타에서 p50/p95 측정 대시보드 존재”, “출시 승인 전 목표값 기록”처럼 수치 결정 전의 검증 가능한 exit condition을 둔다.

**Open Questions**

- 최종 상태의 휴가 상세와 사유는 현재 팀장, 당시 팀장, 감사자 중 누가 어떤 수준으로 볼 수 있어야 하는가?
- `request ID`는 휴가 신청 ID인가, HTTP correlation ID인가?
- People Platform 장애 시 조회도 fail-closed인지, 처리 명령만 fail-closed인지 구분할 필요가 있다.

검토는 제공된 PRD 원문만 대상으로 했고, 저장소 탐색이나 파일 생성은 하지 않았습니다.