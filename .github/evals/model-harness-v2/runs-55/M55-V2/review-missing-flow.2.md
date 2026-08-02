**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow의 Required 여부와 근거를 적음 |
| Pages and routes | Present | `Pages and routes` 표 존재 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix` 표 존재 |
| Mermaid user or system flow | Missing | `User flow`가 Required로 선언됐지만 Mermaid 흐름도는 없음 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~108이 Requirement ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3이 Requirement IDs와 Verifiable exit condition을 포함 |

**Findings**

**High - 필수 사용자 흐름 계약이 누락됨**  
근거: `Applicability`에서 User flow가 Required이고, 신청부터 최종 결정까지 다단계 생명주기라고 적었지만 Mermaid user/system flow가 없음.  
영향: 상태 전이, 팀 이동, 취소·승인 경쟁, 권한 거부·감사 기록의 순서를 구현자가 서로 다르게 해석할 수 있음. 특히 “승인과 취소 동시 요청” 및 “직원 팀 이동 후 처리자 변경”은 순서가 제품 동작이다.  
수정 방향: 신청 생성 → 중복 검사 → PENDING → 직원 취소/팀장 승인/팀장 반려 → 감사 기록 원자화 → 팀 이동 시 접근 주체 재평가를 Mermaid로 명시.

**High - 취소 기능의 권한·검증 계약이 불완전함**  
근거: 역할 표에는 직원이 “대기 취소” 가능하다고 되어 있고 FR-102는 `PENDING → CANCELLED` 전이를 허용하지만, Functional requirements에는 취소 주체·조건·응답·감사 요구가 별도 요구사항으로 정리되어 있지 않음. AC도 취소 단독 성공/실패 기준이 없고 AC-106에서 승인과 취소 동시 요청만 다룸.  
영향: 팀장이 취소할 수 있는지, 직원이 팀 이동 후에도 본인 PENDING을 취소할 수 있는지, APPROVED/REJECTED/CANCELLED 재취소가 409인지 403인지 구현이 갈릴 수 있음.  
수정 방향: “소유 직원은 본인 PENDING 신청만 취소 가능하며, 최종 상태에서는 409, 타인 신청은 403”처럼 취소 요구사항과 AC를 독립적으로 추가.

**High - 감사 이벤트 스키마가 감사 목적을 충족하기에 모호함**  
근거: FR-105는 `actor, request ID, 이전/이후 상태, timestamp`만 요구함. 여기서 `request ID`가 휴가 신청 ID인지 HTTP/request correlation ID인지 불명확하고, 이벤트 타입, 대상 휴가 ID, 조직 ID, 권한 거부 사유 코드, actor role이 명시되지 않음.  
영향: 감사자가 “누가 어떤 조직의 어떤 신청에 어떤 명령을 시도했고 왜 거부됐는지”를 검증하기 어렵다. 멀티 조직 격리와 권한 거부 감사를 제품 목표로 삼은 PRD에서는 실제 감사 가능성이 떨어짐.  
수정 방향: 감사 이벤트 필드에 `event_type`, `leave_request_id`, `organization_id`, `actor_id`, `actor_role`, `decision`, `denial_reason_code`, `correlation_id`를 구분해서 정의. 휴가 사유 전문 제외 원칙은 유지.

**Medium - 권한 거부 감사의 적용 범위가 검증 불가능함**  
근거: FR-105는 “권한 거부”를 기록한다고 하지만 어떤 작업의 거부인지 범위가 없음. AC-105는 다른 팀장 또는 본인 신청 “처리” 거부만 검증한다. 직원의 타인 상세 조회, 이전 팀장의 팀 이동 후 조회, 감사자의 사유 전문 접근, 조직 간 접근 거부 감사는 AC에 없음.  
영향: 보안상 중요한 read-denial과 cross-tenant denial이 구현·테스트에서 빠질 수 있음.  
수정 방향: 권한 거부 감사를 `create/read/update/process/audit-read` 중 어디까지 적용할지 정하고, 최소한 타인 상세 조회·타 조직 접근·이전 팀장 접근 거부 AC를 추가.

**Medium - 감사자 데이터 경계가 화면/검증 수준에서 부족함**  
근거: 역할 표는 감사자가 “휴가 사유 전문 읽기” 금지라고 하고 Risks에도 로그·감사 이벤트 제외를 적었지만, `감사 이력` 페이지의 표시 필드와 AC에서 사유 비노출 검증이 없음.  
영향: 감사 UI/API가 원본 신청 테이블을 조인하면서 사유를 노출하거나, 로그/응답 페이로드에 사유가 섞여도 PRD 기준으로 잡아내기 어렵다.  
수정 방향: 감사 이력 응답/화면 필드를 명시하고, “감사자 조회 결과에 reason 원문이 포함되지 않는다”는 AC를 추가.

**Medium - People Platform 장애와 캐시/시점 기준이 일부 모순적으로 열려 있음**  
근거: FR-103은 “승인 시점 인사 시스템의 현재 팀 직원”이라고 하고, Authorization은 인사 시스템 실패 시 처리 요청을 fail-closed 503으로 둔다. 반면 목록·상세 조회에서 People Platform 실패 시 동작은 정의되지 않음.  
영향: `/team/leave`와 `/leave/:id` 조회에서 HR 장애 시 이전 팀장에게 계속 보일지, 503으로 닫을지, 캐시를 쓸지 불명확하다. 이는 직원 이동 후 “이전 팀장은 접근을 잃는다”는 FR-104와 충돌 가능성이 있음.  
수정 방향: 처리뿐 아니라 팀장 목록/상세 조회도 현재 팀 관계 확인 실패 시 fail-closed인지 명시. 캐시 허용 여부와 최대 허용 지연을 정하지 않으면 실시간 People Platform 기준으로 고정.

**Low - NFR의 API 지연 목표가 출시 전 결정이라 현재는 검증 불가능함**  
근거: Non-functional requirements에 “API 지연 목표는 내부 베타 측정 후 제품 책임자가 정식 출시 전에 결정”이라고 되어 있음.  
영향: PRD 자체는 결정 유보를 명시했지만, 정식 출시 게이트에서 성능 합격 기준이 아직 없음.  
수정 방향: 현재 PRD에서는 open decision으로 유지하되, Delivery 또는 release gate에 “latency SLO 확정 전 정식 출시 불가”를 명시.

**Low - 날짜 정책의 경계 조건이 부족함**  
근거: FR-101은 KST 달력일, 양끝 포함, 시작일≤종료일, PENDING/APPROVED와 겹침 금지만 정의한다. 과거 날짜, 최대 연속 일수, 주말/공휴일 포함 여부, 동일 날짜 1일 신청 여부는 명시되지 않음.  
영향: 구현자가 과거 휴가 신청이나 장기 신청을 허용/차단하는 기준을 다르게 잡을 수 있음.  
수정 방향: 일 단위 MVP에서 허용할 날짜 범위를 명시. 정책 결정이 없다면 “과거/미래 제한 없음, 주말 포함 달력일 기준”처럼 의도적으로 열어둔 상태를 기록.

**요약**

PRD는 권한, 상태 전이, 멱등성, 감사 원자성의 핵심 방향은 좋지만, 계약상 Mermaid flow가 빠져 있고 취소·감사·조회 권한 실패 케이스가 구현 가능한 수준까지 닫히지 않았습니다. 가장 먼저 흐름도와 취소 AC, 감사 이벤트 스키마/비노출 검증을 보강하는 것이 좋습니다.