**프로젝트 산출물 계약 감사**

| Contract | Status | Evidence |
|---|---:|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Missing | 적용성은 Required로 선언했지만 실제 페이지/라우트 목록, 진입점, 권한별 접근 화면 정의가 없음 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 내 휴가, 신청 폼, 승인 상세 상태가 있음 |
| Mermaid user or system flow | Present | `User flow`에 신청, 검증, 대기, 취소, 승인, 반려 흐름이 있음 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `Acceptance criteria`가 AC별 Given/When/Then/Verification과 FR 매핑을 포함함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery`가 Phase별 FR ID와 검증 가능한 종료 조건을 포함함 |

**Findings**

`high` Pages/routes 계약이 적용되지만 누락되어 구현 경계가 불명확합니다.  
근거: `Applicability`는 Pages/routes를 Required로 선언하지만, PRD에는 “직원 신청과 팀장 처리 화면이 있다” 수준만 있고 실제 route, 화면 소유 역할, 상세/목록/폼/처리 화면 간 이동, 감사자 화면 또는 API-only 여부가 정의되지 않았습니다.  
영향: 프론트엔드, API 권한, QA 시나리오가 서로 다른 화면 범위를 가정할 수 있습니다. 특히 감사자는 “조직 내 감사 이벤트 읽기” 권한이 있는데 감사자용 화면/라우트가 필요한지 불명확합니다.  
수정 방향: 직원 목록/상세/신청, 팀장 처리 목록/상세, 감사 이벤트 조회의 화면 또는 API-only 여부를 명시하고 각 surface의 접근 역할을 연결하세요.

`high` idempotency key의 범위와 충돌 규칙이 없어 보안·정합성 검증이 불완전합니다.  
근거: `FR-106`, `AC-108`은 “idempotency key”와 “같은 신청 ID, 중복 이벤트 없음”만 말합니다. key가 조직, actor, command type, endpoint, request body hash에 묶이는지, 같은 key로 다른 payload가 오면 409인지 422인지, TTL이 있는지 정의가 없습니다.  
영향: 전역 key 또는 느슨한 key 저장소로 구현되면 다른 사용자/조직의 응답 재사용, 잘못된 명령 재실행, payload mismatch 은폐가 발생할 수 있습니다.  
수정 방향: key scope를 `organization + actor + operation + request fingerprint`로 제한하고, 같은 key/다른 payload는 명시적 오류, 같은 key/같은 payload는 원 응답 재반환으로 정의하세요.

`high` 감사 로그의 권한 거부 기록 요구가 존재·상태 정보 노출과 충돌할 수 있습니다.  
근거: `FR-105`는 권한 거부도 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 합니다. 그런데 `Users, roles, and permissions`와 `FR-104`는 타인/타팀 접근 금지 및 조직 격리를 요구합니다. 권한 거부 대상의 이전/이후 상태를 항상 기록하거나 반환 흐름과 결합하면, 존재 여부나 상태가 노출될 수 있습니다.  
영향: 타 팀 신청 ID를 추측한 요청이 내부 감사 데이터 또는 에러 처리 경로를 통해 신청 존재와 상태를 유추하게 만들 수 있습니다.  
수정 방향: 거부 감사 이벤트는 대상 상태를 nullable/redacted로 둘 수 있는지, 존재하지 않음과 접근 거부를 어떻게 구분하지 않을지, 감사자에게 표시 가능한 필드를 별도로 정의하세요.

`medium` 감사자 권한과 감사 이벤트 조회 범위가 검증 가능하지 않습니다.  
근거: `Users, roles, and permissions`는 감사자가 “조직 내 감사 이벤트 읽기” 가능, “휴가 사유 전문 읽기” 금지라고 하지만, 기능 요구사항과 AC에는 감사 이벤트 조회, 필터링, 마스킹, 권한 테스트가 없습니다.  
영향: 감사자 기능이 실제 제품 범위인지, 백오피스/API만인지, 사유가 어디까지 마스킹되는지 구현·QA가 확인할 수 없습니다.  
수정 방향: 감사자 조회가 범위라면 FR/AC를 추가하고 이벤트 필드 allowlist, reason redaction, 조직 격리, 권한 거부 이벤트 노출 방식을 검증 항목으로 넣으세요. 범위가 아니라면 역할에서 제외하거나 non-goal로 명확히 하세요.

`medium` 팀장 조회 권한과 처리 권한의 기준 시점이 일부만 정의되어 목록/상세에서 모순이 생길 수 있습니다.  
근거: `FR-103`은 “승인 시점” 현재 팀 직원 PENDING만 처리한다고 하고, `FR-104`는 직원 이동 후 새 팀장이 PENDING 신청을 처리하고 이전 팀장은 접근을 잃는다고 합니다. 하지만 APPROVED/REJECTED/CANCELLED 과거 신청을 현재 팀장이 볼 수 있는지, 이전 팀장이 이동 전 처리한 과거 기록을 계속 볼 수 있는지는 불명확합니다.  
영향: 팀장 목록·상세 화면에서 과거 신청 조회 정책이 구현마다 갈릴 수 있고, 개인정보 접근 범위가 과도해질 수 있습니다.  
수정 방향: 팀장 조회 범위를 PENDING만으로 제한할지, 현재 팀 직원의 과거 신청까지 허용할지, 과거 소속 기준 접근을 금지할지 명시하세요.

`medium` 실패 감사 범위가 불완전합니다.  
근거: `FR-105`는 생성·승인·반려·취소와 권한 거부를 기록한다고 하지만, `AC-102`의 겹침 충돌은 “성공 감사 이벤트 없음”만 말하고 충돌/검증 실패 감사 여부는 정의하지 않습니다. `FR-106`의 원자성도 상태와 감사 이벤트에만 걸려 있어 권한 거부나 실패 이벤트의 내구성은 별도입니다.  
영향: 보안 관점에서 중요한 반복 충돌/권한 시도 추적이 빠질 수 있고, 반대로 구현팀이 모든 validation failure를 기록해 개인정보·로그량 문제가 생길 수 있습니다.  
수정 방향: 감사 대상 실패 유형을 권한 거부, 상태 충돌, 검증 오류, HR 503 등으로 나누고 기록/비기록 기준과 필드를 정의하세요.

`low` API 지연 목표가 출시 전 결정으로 남아 있어 현재 PRD 기준으로는 성능 acceptance가 검증 불가능합니다.  
근거: `Non-functional requirements`와 `Assumptions and open decisions`가 API 지연 목표를 내부 베타 후 결정한다고 합니다.  
영향: 정식 출시 전까지는 허용 가능한 응답 지연, HR 시스템 의존 호출 타임아웃, 재시도 UX를 테스트 기준으로 삼기 어렵습니다.  
수정 방향: 지금 수치를 확정하지 않더라도 베타 종료 시점의 의사결정자, 측정 방식, p95/p99 여부, 대상 API 범위를 결정 항목으로 고정하세요.

검토는 제공된 PRD 원문만 기준으로 했고, 요청대로 파일 생성·저장소 탐색·원문 재작성은 하지 않았습니다.