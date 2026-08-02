**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow 적용성을 표시함 |
| Pages and routes | Missing | 적용성은 Required로 선언했지만 실제 페이지/route 목록, 소유 화면, 진입 조건, 권한별 접근 경계가 없음 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 내 휴가, 신청 폼, 승인 상세 상태가 있음 |
| Mermaid user or system flow | Present | `User flow` Mermaid가 신청부터 최종 상태까지 표시함 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~AC-108이 FR ID, Given/When/Then/Verification을 포함함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3이 Requirement IDs와 exit condition을 포함함 |

**Findings**

**blocker**

- Pages/routes 계약이 적용 대상인데 산출물이 누락됨.
  - 영향도: 구현자가 직원 목록/상세/신청, 팀장 목록/상세/처리, 감사 조회가 각각 별도 화면인지, 어떤 route와 접근 제어가 필요한지 확정할 수 없음. 특히 팀장 조회 권한과 감사자 조회 권한은 UI/서버 경계가 필요한데 현재는 요구사항과 state matrix에 흩어져 있음.
  - 근거: `Applicability`에서 `Pages/routes Required`라고 했지만 별도 Pages/routes 섹션이 없음.
  - 수정 방향: 최소한 화면/route, 접근 role, 표시 데이터, 주요 액션을 표로 추가. 예: 내 휴가 목록, 신청 생성, 신청 상세, 팀장 승인 대기 목록, 승인 상세, 감사 이벤트 목록.

**high**

- 직원 취소 기능이 flow/role/audit에는 있지만 독립 FR과 AC가 부족함.
  - 영향도: 취소 가능 주체, 취소 가능 상태, 멱등성, 감사 이벤트, 승인과의 경쟁 조건을 일관되게 구현하기 어렵다. AC-106에 동시 승인/취소가 있지만 취소 자체의 정상/실패 기준이 없다.
  - 근거: `Users, roles`는 직원의 `대기 취소`를 허용하고, `User flow`는 `PENDING -> CANCELLED`를 표시함. 그러나 FR-101~106에는 직원 취소 명령의 세부 요건이 없고 AC도 정상 취소, 타인 취소, 최종 상태 취소 실패를 직접 검증하지 않음.
  - 수정 방향: “직원은 본인 PENDING 신청만 취소할 수 있고 CANCELLED 감사 이벤트를 원자적으로 기록한다” 같은 FR과 AC를 추가.

- 멱등성 키의 보안·정합성 범위가 정의되지 않음.
  - 영향도: 같은 idempotency key가 조직/actor/operation/body와 묶이지 않으면 다른 사용자의 결과 재사용, 잘못된 중복 억제, 요청 본문이 다른 재시도 처리 오류가 생길 수 있음.
  - 근거: FR-106은 “모든 생성·상태 명령은 idempotency key”라고만 하고, AC-108도 “같은 idempotency key 재시도”만 검증함.
  - 수정 방향: 키는 `organization + actor + command type + request/body fingerprint` 범위로 유일해야 하며, 같은 키에 다른 payload가 오면 409 또는 422로 거부한다고 명시. 보관 기간도 결정 필요.

- 겹침 검사의 대상 범위가 모호함.
  - 영향도: PENDING·APPROVED 기간과 겹칠 수 없다는 규칙이 “같은 직원의 휴가”인지 “같은 조직 전체”인지 명시되지 않아 구현 차이가 날 수 있음.
  - 근거: FR-101의 “PENDING·APPROVED 신청과 겹칠 수 없다”에 owner/org 범위가 없음.
  - 수정 방향: “동일 조직 내 동일 신청 소유자의 PENDING 또는 APPROVED 휴가와 겹칠 수 없다”처럼 범위를 고정.

**medium**

- People Platform 장애 처리 범위가 처리 요청에만 명확함.
  - 영향도: 팀장 목록/상세 조회, 직원 이동 후 접근 검증, 감사 조회에서 People Platform 장애 시 fail-open/fail-closed/캐시 사용 여부가 달라질 수 있음.
  - 근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고만 함. FR-104는 작업별 현재 팀 검사를 요구하지만 조회 실패 시 동작은 없음.
  - 수정 방향: 팀장 조회·상세·승인·반려 모두 현재 팀 관계 확인 실패 시 503 fail-closed로 통일할지 명시. 캐시 허용 여부도 결정.

- 권한 거부 감사 이벤트의 테넌시와 필드 정책이 부족함.
  - 영향도: 타 조직 리소스 접근 시 어느 조직의 감사 로그에 남길지 불명확하다. 잘못 설계하면 대상 조직에 외부 actor 정보가 남거나, actor 조직 감사자가 타 조직 request ID 존재를 추론할 수 있다.
  - 근거: FR-105는 “권한 거부를 actor, request ID, 이전/이후 상태, timestamp로 기록”한다고 하지만 cross-org deny, nonexistent request, inaccessible request의 `request ID`·상태 기록 기준이 없음.
  - 수정 방향: denied audit은 actor 조직 기준으로 기록할지, 리소스 조직 기준으로 기록할지, 리소스 존재/상태를 모를 때 어떤 값을 기록할지 명시. 휴가 사유 전문 금지는 유지.

- 감사 이벤트 검증 범위가 FR보다 좁음.
  - 영향도: FR-105는 생성·승인·반려·취소·권한 거부를 요구하지만 NFR은 “성공 상태 변경”만 장애 주입 통합 테스트로 검증한다. 거부 감사와 취소 감사의 원자성 검증이 누락될 수 있음.
  - 근거: `Non-functional requirements`와 FR-105/AC-105.
  - 수정 방향: 장애 주입 검증 대상을 성공 상태 변경뿐 아니라 취소와 권한 거부 감사 이벤트까지 포함할지 명시.

**low**

- API 지연 목표가 출시 전 결정으로 남아 있어 현재 PRD 기준으로는 검증 불가함.
  - 영향도: Phase exit나 acceptance에서 성능 완료 여부를 판단할 수 없음. 다만 내부 베타 이후 결정이라는 제품 의사결정으로는 허용 가능하다.
  - 근거: `Non-functional requirements`, `Assumptions and open decisions`.
  - 수정 방향: 정식 출시 전 gate로 “latency SLO 확정 및 측정 리포트 승인” 같은 검증 가능한 조건을 Delivery에 추가.

- 반려 사유와 휴가 사유의 보존/노출 범위가 비대칭임.
  - 영향도: 휴가 사유 전문은 로그·감사 이벤트 금지가 명확하지만 반려 사유의 읽기 권한, 감사 포함 여부, 로그 금지 여부는 덜 명확하다.
  - 근거: FR-103은 반려 사유 1~500자만 정의하고, FR-105는 “휴가 사유 전문”만 감사 제외한다고 함.
  - 수정 방향: 반려 사유도 전문/요약/감사 포함 여부와 열람 가능 role을 명시.

검토는 제공된 PRD 텍스트만 기준으로 했고, 요청대로 저장소 탐색이나 파일 생성은 하지 않았습니다.