**프로젝트 산출물 계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix` 표 존재. 다만 일부 적용 화면 누락은 finding 참고 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid lifecycle flow 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | Missing | `Delivery`에는 exit condition이 있으나 각 FR별 precondition/action/result 형태의 검증 가능한 인수 기준은 없음 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery` 표가 Phase별 Requirement IDs와 exit condition을 매핑함 |

**Findings**

**high - 동시 휴가 생성 시 겹침 방지 보장이 불완전함**  
근거: `FR-101`은 `PENDING·APPROVED` 신청과 겹칠 수 없다고 하고, `FR-106`은 생성·상태 명령에 idempotency key와 조건부 갱신을 사용한다고 합니다. 하지만 신규 생성 간 레이스에서는 “조건부 갱신”만으로 동일 직원의 중복 기간 삽입을 막는지 검증할 수 없습니다.  
영향: 동시에 두 신청이 들어오면 둘 다 overlap check를 통과한 뒤 삽입될 수 있어 핵심 불변식이 깨집니다.  
수정 방향: 직원+조직+KST 날짜 범위+활성 상태(`PENDING`, `APPROVED`)에 대해 DB exclusion constraint, serializable transaction, range lock, 또는 동등한 원자적 충돌 방지 메커니즘을 명시하고 테스트 exit condition에 동시 생성 충돌 케이스를 추가하세요.

**high - 인수 기준 계약이 빠져 구현 완료 여부를 객관적으로 판정하기 어려움**  
근거: 계약 감사상 `Acceptance precondition/action/result mapped to requirement IDs`가 Missing입니다. `Delivery`의 “테스트 통과”는 범주만 있고, 각 요구사항별 Given/When/Then 또는 precondition/action/result가 없습니다.  
영향: `FR-101`의 날짜 경계, `FR-103`의 본인 처리 금지, `FR-105`의 권한 거부 감사 기록 등 핵심 동작이 구현자마다 다르게 해석될 수 있습니다.  
수정 방향: 각 P0 요구사항에 최소 1개 이상의 관찰 가능한 인수 기준을 추가하세요. 예: “소속 이동 후 이전 팀장이 상세 조회/승인 시도 → 403 및 권한 거부 감사 이벤트 기록”.

**medium - idempotency key의 범위·보존·payload 일치 규칙이 정의되지 않음**  
근거: `FR-106`은 idempotency key 사용만 요구합니다. actor, organization, endpoint/action, request body hash, TTL, 재시도 응답 규칙이 없습니다.  
영향: 키 충돌, 다른 payload로 같은 키 재사용, 사용자/조직 간 키 재사용 같은 보안·정합성 문제가 생길 수 있습니다.  
수정 방향: idempotency key는 최소 `organization + actor + operation + key` 범위로 격리하고, 같은 키에 다른 payload가 오면 `409` 또는 명시 오류를 반환하도록 정의하세요. 보존 기간과 재응답 semantics도 정해야 합니다.

**medium - State matrix가 정의된 화면 전체를 덮지 않음**  
근거: `Pages and routes`는 내 휴가, 휴가 상세, 팀 승인함, 감사 이력을 정의하지만 `State matrix`는 내 휴가, 신청 폼, 승인 상세만 다룹니다. 팀 승인함 목록, 감사 이력, 일반 상세 조회의 empty/loading/error/success/recovery 상태가 없습니다.  
영향: 감사자 화면의 권한·비식별 데이터 표시, 팀장 목록의 HR 장애/빈 상태, 상세 조회의 403/404/이동 후 접근 상실 UX가 검증 대상에서 빠집니다.  
수정 방향: route별 주요 surface를 모두 state matrix에 추가하거나, 의도적으로 제외한 화면은 `N/A` 근거를 남기세요.

**medium - 권한 거부 감사 이벤트가 정보 노출과 기록 기준을 애매하게 만듦**  
근거: `FR-105`는 권한 거부를 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 합니다. 동시에 감사자는 휴가 사유 전문을 읽을 수 없고, 조직 경계는 세션에서 결정한다고 되어 있습니다.  
영향: 존재하지 않거나 타 조직의 `request ID` 접근 시도를 어떻게 기록할지 불명확합니다. 잘못 설계하면 감사 로그가 타 조직 request ID 존재 여부를 노출하거나, 반대로 보안상 중요한 거부 이벤트가 누락될 수 있습니다.  
수정 방향: 권한 거부 이벤트의 target 식별자를 “검증된 동일 조직 request ID”와 “미검증/타조직/존재불명 target”으로 분리하세요. 감사자에게 노출되는 필드와 redaction 규칙도 명시해야 합니다.

**low - API 지연 목표가 출시 전 결정 사항으로 남아 Delivery 검증과 연결되지 않음**  
근거: `Non-functional requirements`와 `Assumptions and open decisions`에 API 지연 목표를 내부 베타 이후 제품 책임자가 결정한다고 되어 있으나, `Delivery`에는 이를 확인하는 exit condition이 없습니다.  
영향: 정식 출시 직전까지 성능 기준이 비어 있어 릴리스 판단이 주관화될 수 있습니다.  
수정 방향: 목표 수치 자체가 TBD인 것은 괜찮지만, “출시 전 latency SLO 확정 및 측정 대시보드/부하 기준 승인” 같은 Phase gate를 Delivery에 추가하세요.

검토는 제공된 PRD 본문만 기준으로 했고, 저장소 탐색이나 파일 생성은 하지 않았습니다.