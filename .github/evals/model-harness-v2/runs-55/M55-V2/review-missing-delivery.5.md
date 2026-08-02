**산출물 계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow 적용성을 선언함 |
| Pages and routes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`가 있으나 일부 표면 누락은 아래 finding 처리 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid 생명주기 제공 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~AC-108이 FR ID와 Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Missing | 단계, 범위 분할, 릴리스별 exit condition 없음 |

**Findings**

| Severity | Finding | Impact | 근거 | 수정 방향 |
|---|---|---|---|---|
| High | Delivery phases 계약이 누락됨 | P0 권한·감사·동시성 요구가 한 번에 묶여 있어 베타/정식 출시 전 필수 검증 범위와 차단 조건이 불명확함 | 산출물 계약상 `Delivery phases mapped to requirement IDs and exit conditions` 없음. NFR의 “내부 베타 측정 후”도 phase exit로 연결되지 않음 | 예: Phase 1 신청/조회, Phase 2 처리/권한, Phase 3 감사/장애 주입처럼 FR/AC별 출고 단위와 exit condition을 명시 |
| High | 날짜 겹침 범위가 불명확함 | 구현에 따라 전사 전체 휴가와 충돌시키거나, 같은 직원·같은 조직 기준을 빠뜨릴 수 있음 | FR-101: “PENDING·APPROVED 신청과 겹칠 수 없다”가 누구의 신청인지 명시하지 않음 | “동일 조직 내 동일 직원의 PENDING 또는 APPROVED 신청”처럼 충돌 스코프를 명확히 지정 |
| High | 직원 취소 성공 경로가 검증되지 않음 | `CANCELLED` 전이가 핵심 상태인데 실제 구현이 누락돼도 AC를 통과할 수 있음 | FR-102, 역할 표, User flow에는 취소가 있으나 AC에는 직원 단독 취소 성공 기준이 없음. AC-106은 승인/취소 동시성만 검증 | `PENDING` 소유 직원이 취소하면 `CANCELLED`와 감사 이벤트 1건이 생기는 AC 추가 |
| Medium | 상태 명령 멱등성 검증이 신청에만 있음 | 승인/반려/취소 재시도 시 중복 이벤트, 잘못된 409, 다른 응답 재생 등의 구현 차이가 발생할 수 있음 | FR-106: “모든 생성·상태 명령은 idempotency key”라고 하나 AC-108은 “신청”만 다룸 | 승인·반려·취소 각각 동일 key 재시도, 동일 key 다른 payload, 처리 완료 후 재시도 응답을 AC로 분리 |
| Medium | 감사 이벤트 필드가 감사 목적에 부족하거나 용어가 모호함 | 권한 거부나 상태 변경 추적 시 어떤 이벤트가 어떤 대상에 발생했는지 검증하기 어려움 | FR-105 필드는 `actor, request ID, 이전/이후 상태, timestamp`뿐임. `request ID`가 휴가 신청 ID인지 API 요청 ID인지 모호하고, event type/action/outcome도 명시되지 않음 | `leave_request_id`, `operation_id/idempotency_key`, `event_type`, `outcome`, `actor_role`, `org_id` 등 필요한 최소 필드를 명확히 구분 |
| Medium | State matrix 적용 범위가 일부 화면에 빠짐 | 팀 승인함, 감사 이력, 소유자 상세의 빈/오류/복구 상태가 누락되어 UI 구현·검증 기준이 비게 됨 | Pages에는 4개 화면이 있으나 State matrix는 `내 휴가`, `신청 폼`, `승인 상세`만 있음 | `/team/leave`, `/audit/leave`, 직원용 상세의 empty/loading/error/success/recovery 상태를 추가 |
| Medium | `/leave/:id`의 primary action이 역할별로 모호함 | 팀장이 취소할 수 있는지, 직원이 처리 버튼을 볼 수 있는지 같은 권한/UI 불일치가 생길 수 있음 | Pages: “소유 직원, 현재 팀장 | 조회·취소·처리”. 역할 표는 직원 취소, 팀장 승인·반려로 구분 | route별 action을 role/state 기준으로 분리: 소유 직원은 `PENDING 취소`, 현재 팀장은 `PENDING 승인/반려`, 감사자는 접근 불가 등 |
| Medium | People Platform 장애 처리 범위가 처리 요청에만 명확함 | 조회·목록에서 팀장 권한 판정 실패 시 fail-open/캐시 사용 여부가 갈릴 수 있음 | Authorization: “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고만 함. FR-104는 조회와 처리 모두 현재 팀 관계 검사 | 팀 승인함 조회, 상세 조회, 처리 각각 People Platform 실패 시 정책을 명시. 보안 우선이면 모두 fail-closed 또는 검증된 캐시 조건 정의 |
| Low | API 지연 목표가 출시 전 결정으로만 남아 검증 불가능함 | 정식 출시 gate에서 “충분히 빠른지” 판단 기준이 없음 | NFR: “내부 베타 측정 후 제품 책임자가 정식 출시 전에 결정” | delivery phase exit condition에 지연 목표 결정 책임자, 결정 시점, 측정 방식, 미결 시 출시 차단 여부를 연결 |
| Low | 감사자의 개인정보 접근 제한은 방향은 있으나 검증 기준이 약함 | 감사 API가 휴가 사유 전문을 포함해도 AC에서 잡지 못할 수 있음 | 역할 표와 Risks에는 “휴가 사유 전문 읽기 금지”가 있으나 AC에 감사자 조회 응답 검증 없음 | 감사 이력 조회 AC에 `reason` 원문 미포함, 필요한 경우 redaction/hash/metadata만 포함을 명시 |

**Open Questions**

- 과거 날짜 휴가 신청을 허용하는지, 미래 신청만 허용하는지는 의도적으로 열린 정책인지 확인이 필요합니다.
- 팀장 본인의 신청은 누가 처리하는지 대체 승인자 규칙이 없습니다. “본인 신청 처리 금지”가 있으면 운영상 위임/상위 승인 흐름도 필요할 수 있습니다.

Validator는 실행하지 않았습니다. 사용자가 파일 생성·저장소 탐색을 금지했고, PRD가 파일 경로로 제공되지 않았기 때문입니다.