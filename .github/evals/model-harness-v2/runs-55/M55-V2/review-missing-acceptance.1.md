## 산출물 계약 감사

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판단함 |
| Pages and routes | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix` 표가 Empty/Loading/Error/Success/Recovery 열을 포함 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid flowchart 포함 |
| Acceptance precondition/action/result mapped to requirement IDs | Missing | Delivery exit condition은 있으나 각 FR별 precondition/action/result 형태의 검증 조건은 없음 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery` 표가 Phase별 Requirement IDs와 exit condition을 포함 |

## Findings

**blocker - FR별 acceptance criteria가 없어 핵심 요구사항 일부가 검증 불가능함**  
근거: `Functional requirements`는 행위와 제약을 설명하지만, 계약상 필요한 “precondition/action/result mapped to requirement IDs”가 없다. 특히 FR-103, FR-104, FR-106은 조직, 팀 이동, 현재 팀장, 동시성, 멱등성 조건이 복합적이라 단순 “테스트 통과”만으로 구현 합의를 만들기 어렵다.  
영향: 구현팀과 QA가 같은 요구를 다르게 해석할 수 있고, 권한·동시성 같은 P0 동작이 누락되어도 PRD상 실패 판정이 모호하다.  
수정 방향: 각 FR에 최소 1개 이상의 Given/When/Then 또는 precondition/action/result 기준을 추가하고, 성공·실패·경계 조건을 requirement ID에 직접 연결한다.

**high - 권한 거부 감사 이벤트 요구가 상태 필드 요구와 충돌함**  
근거: FR-105는 “생성·승인·반려·취소와 권한 거부를 actor, request ID, 이전/이후 상태, timestamp로 기록”한다고 한다. 하지만 권한 거부는 대상 신청을 조회하면 안 되는 경우, 존재하지 않는 ID, 타 조직 ID 추측, People Platform 장애 등에서 이전/이후 상태를 알 수 없거나 알아서는 안 될 수 있다.  
영향: 감사 요건을 만족하려다 권한 없는 객체를 조회하거나, 반대로 보안적으로 안전하게 처리하면 FR-105를 만족하지 못하는 모순이 생긴다.  
수정 방향: 권한 거부 이벤트의 스키마를 별도 정의한다. 예: `target_request_id`는 입력 ID 또는 해시, `previous_state/next_state`는 nullable, `denial_reason_category`, `resource_resolved=false` 등을 허용한다.

**high - 감사자 데이터 경계가 부족해 민감 정보 노출 가능성이 남아 있음**  
근거: `Users, roles, and permissions`는 감사자가 “조직 내 감사 이벤트 읽기” 가능, “휴가 사유 전문 읽기” 금지라고만 한다. FR-105는 actor, request ID, 이전/이후 상태, timestamp를 기록한다고 하지만 감사자에게 보이는 필드, 필터 범위, 직원 식별자 노출 수준, 권한 거부 이벤트 노출 여부는 정의하지 않는다.  
영향: 감사 화면에서 휴가 신청 존재, 직원 활동 패턴, 권한 거부 대상 ID 등이 과도하게 노출될 수 있다.  
수정 방향: 감사자용 응답 필드와 마스킹 정책을 명시한다. 휴가 사유뿐 아니라 직원명/ID, request ID, actor 식별자, denial target의 표시 방식을 정의해야 한다.

**high - 멱등성 키의 범위와 재사용 규칙이 불명확함**  
근거: FR-106은 “모든 생성·상태 명령은 idempotency key와 조건부 갱신을 사용”한다고만 한다. 키가 조직, actor, endpoint, payload, 대상 request ID 중 무엇에 묶이는지, 같은 키로 다른 payload가 오면 409인지, 성공 응답을 재생하는지, TTL이 있는지 정의가 없다.  
영향: 같은 키가 사용자 간 또는 작업 간 충돌하거나, 반려 요청 재시도에서 다른 반려 사유가 덮이는 등 상태 변경 안정성이 흔들릴 수 있다.  
수정 방향: idempotency key scope를 `org + actor + command type + target/request payload hash` 수준으로 정의하고, 동일 키·동일 payload는 기존 결과 반환, 동일 키·상이 payload는 충돌로 처리하도록 명시한다.

**medium - 팀장 조회 권한과 상세 조회 권한의 상태 기준이 다르게 읽힘**  
근거: FR-103은 팀장이 “현재 팀 직원 PENDING 신청만 처리”한다고 하고, Pages/routes의 `휴가 상세`는 “소유 직원, 현재 팀장”에게 허용된다. `팀 승인함`은 “대기 신청 조회”로 제한되어 있지만 상세 페이지는 현재 팀장이 최종 상태의 과거 신청도 조회할 수 있는지 모호하다.  
영향: 승인/반려 후 팀장이 상세를 계속 볼 수 있는지, 직원 이동 후 새 팀장이 과거 APPROVED/REJECTED 신청을 볼 수 있는지 구현이 갈릴 수 있다.  
수정 방향: 팀장 상세 조회를 `현재 팀 직원의 PENDING만`, `처리했던 신청은 최종 후에도 조회 가능`, `현재 팀 소속 전체 이력 조회 가능` 중 하나로 명확히 분리한다.

**medium - People Platform 장애 시 읽기와 쓰기 정책이 완전히 분리되어 있지 않음**  
근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고 한다. 그러나 목록/상세 조회, 직원 신청 생성 시 현재 조직·팀 검증 실패, 감사 조회에는 어떤 실패 정책을 적용하는지 불명확하다.  
영향: HR 시스템 장애 시 어떤 API가 503이고 어떤 화면이 캐시/기존 데이터로 동작하는지 검증하기 어렵다. 특히 팀장 권한 판정이 필요한 상세 조회는 보안상 fail-closed가 필요할 가능성이 높다.  
수정 방향: 작업별 People Platform 의존성을 표로 나누고, 생성/조회/처리/감사 각각의 장애 응답과 UI recovery를 정의한다.

**low - API 지연 목표가 출시 전 결정으로 남아 현재 PRD에서는 비기능 검증 기준이 없음**  
근거: `Non-functional requirements`와 `Assumptions and open decisions`가 API 지연 목표를 내부 베타 후 결정한다고 반복한다.  
영향: Phase exit 조건에서 성능 회귀나 베타 완료 기준을 검증할 수 없다.  
수정 방향: 지금 수치를 확정하지 않더라도 베타에서 측정할 엔드포인트, percentile, 표본 조건, 결정 책임자, 결정 마감일을 acceptance 형태로 둔다.