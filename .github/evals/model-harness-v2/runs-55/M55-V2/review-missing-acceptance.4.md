**프로젝트 산출물 계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix` 표 존재. 다만 감사 이력 화면 상태는 빠져 있음 |
| Mermaid user or system flow | Present | `User flow` Mermaid 다이어그램 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | Missing | FR은 요구사항 문장이고, Delivery exit condition은 포괄적 테스트명이라 각 FR별 precondition/action/result가 없음 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery` 표가 Phase별 FR ID와 exit condition을 매핑함 |

**Findings**

**High - FR별 검증 조건이 부족해 구현 완료 여부가 판정 불가능함**

- 영향도: `FR-101~FR-106`이 P0인데, 무엇을 준비하고 어떤 액션을 수행했을 때 어떤 결과가 나와야 하는지 요구사항별로 관찰 가능하게 고정되어 있지 않습니다. 예를 들어 `FR-104`의 “직원 이동 후 이전 팀장은 접근을 잃는다”는 목록, 상세, 처리 API 각각에서 어떤 응답이어야 하는지 검증할 수 없습니다.
- 근거: `Acceptance precondition/action/result mapped to requirement IDs` 계약이 없음. `Delivery`의 “상태·권한·동시성·멱등성 테스트 통과”는 너무 넓습니다.
- 수정 방향: 각 FR 또는 주요 시나리오별로 `Given / When / Then`을 추가하세요. 특히 생성 중복, 승인/반려, 취소, 직원 이동, 권한 거부, 인사 시스템 장애, 멱등성 재시도, 감사 원자성은 별도 케이스가 필요합니다.

**High - 멱등성 키 보안·충돌 의미가 정의되지 않음**

- 영향도: `FR-106`은 모든 생성·상태 명령에 idempotency key를 요구하지만 키의 범위와 재사용 정책이 없습니다. 키가 조직·actor·operation·request body에 바인딩되지 않으면 다른 사용자나 다른 페이로드의 재사용, 의도치 않은 응답 재생, 상태 변경 혼동이 생길 수 있습니다.
- 근거: `FR-106`은 “idempotency key와 조건부 갱신”만 언급합니다.
- 수정 방향: 키 스코프를 `organization + actor + endpoint/command + normalized payload`로 정의하고, 같은 키/같은 payload는 원 응답 재생, 같은 키/다른 payload는 `409` 또는 `422`, TTL, 저장 데이터, 감사 이벤트 중복 방지 규칙을 명시하세요.

**High - 겹침 방지의 동시 생성 불변식이 충분히 검증 가능하지 않음**

- 영향도: 두 요청이 동시에 같은 날짜 범위로 들어오면 둘 다 “기존 PENDING·APPROVED와 겹치지 않음” 검사를 통과한 뒤 중복 신청이 생성될 수 있습니다. 휴가 중복 금지는 핵심 도메인 불변식이라 DB/트랜잭션 수준 보장이 필요합니다.
- 근거: `FR-101`은 겹칠 수 없다고 하고, `FR-106`은 조건부 갱신을 말하지만 생성 시 날짜 범위 충돌을 어떤 원자적 제약으로 막는지 불명확합니다.
- 수정 방향: 조직+직원+KST 날짜 범위 기준의 배타 제약, 직렬화 트랜잭션, 잠금 전략 중 하나를 제품 계약에 명시하고, 동시 생성 테스트의 기대 결과를 “한 건 성공, 나머지 409”처럼 고정하세요.

**Medium - 감사 이력 화면의 상태 매트릭스가 누락됨**

- 영향도: 감사자는 별도 사용자 역할과 `/audit/leave` 화면이 있는데 Empty/Loading/Error/Success/Recovery 정의가 없습니다. 감사 로그 조회 실패, 빈 이벤트, 권한 거부, 필터 결과 없음 같은 상태가 구현자별로 달라질 수 있습니다.
- 근거: `Pages and routes`에는 `감사 이력`이 있으나 `State matrix`에는 `내 휴가`, `신청 폼`, `승인 상세`만 있습니다.
- 수정 방향: 감사 이력 surface를 추가하고 빈 상태, 로딩, 오류, 성공 목록, 재시도 또는 필터 초기화 동작을 정의하세요.

**Medium - 직원 이동 후 최종 상태 신청의 조회 권한이 모호함**

- 영향도: `FR-104`는 직원 이동 후 새 팀장이 PENDING 신청을 처리하고 이전 팀장은 접근을 잃는다고 합니다. 그러나 이미 APPROVED/REJECTED/CANCELLED인 신청을 누가 조회할 수 있는지는 불명확합니다. 과거 결재자인 이전 팀장이 상세를 계속 볼 수 있는지, 새 팀장이 과거 최종 상태까지 볼 수 있는지에 따라 개인정보 노출 범위가 크게 달라집니다.
- 근거: `/leave/:id` Allowed roles는 “소유 직원, 현재 팀장”이고, `FR-103/FR-104`는 PENDING 처리 중심입니다.
- 수정 방향: 상세 조회 권한을 상태별로 분리하세요. 예: PENDING은 현재 팀장만, 최종 상태는 소유 직원과 감사 이벤트를 통한 제한 조회만, 또는 결재 당시 팀장에게 메타데이터만 허용 등으로 정해야 합니다.

**Medium - 권한 거부 감사 이벤트가 정보 노출과 충돌할 수 있음**

- 영향도: 권한 거부를 `request ID, 이전/이후 상태`와 함께 기록하면, 접근 권한이 없는 actor가 특정 신청 ID의 존재나 상태를 유추하게 만들 수 있습니다. 감사 로그 자체는 감사자만 보더라도, 거부 처리 과정에서 동일한 정보를 응답이나 로그 상관관계로 노출할 위험이 있습니다.
- 근거: `FR-105`는 “권한 거부를 actor, request ID, 이전/이후 상태, timestamp로 기록”한다고 합니다.
- 수정 방향: 권한 거부 이벤트의 `request ID`는 내부 대상 ID인지 HTTP 요청 상관 ID인지 분리하세요. 대상 신청을 조회할 권한이 없는 경우에는 previous/next state를 `unknown` 또는 null로 기록하고, 감사자에게만 필요한 최소 메타데이터를 제공하도록 정의하세요.

**Low - API 지연 목표가 출시 전 결정으로 남아 있어 현재 PRD 기준으로는 NFR 검증 불가**

- 영향도: 성능 요구가 없으면 베타 중 병목이나 회귀를 출시 판단에 반영하기 어렵습니다.
- 근거: `Non-functional requirements`와 `Assumptions and open decisions` 모두 API 지연 목표를 추후 결정으로 둡니다.
- 수정 방향: 정식 목표가 미정이면 최소한 베타 계측 항목과 임시 게이트를 정의하세요. 예: 주요 API별 p50/p95 수집, 타임아웃, 알림 기준, 출시 전 목표 확정 책임자와 날짜.

**Low - 날짜 입력 계약이 KST 달력일 외에는 부족함**

- 영향도: 클라이언트가 timestamp를 보내는지 `YYYY-MM-DD` date-only 값을 보내는지에 따라 UTC 변환, DST는 없더라도 경계일 처리, 포함 범위 계산이 달라질 수 있습니다.
- 근거: `FR-101`은 “KST 달력일”과 “양끝 포함”만 정의합니다.
- 수정 방향: API 입력을 date-only `YYYY-MM-DD`로 고정하고 서버가 KST 기준으로 해석한다고 명시하세요. 오류 코드와 필드별 메시지 기준도 acceptance에 포함하면 검증 가능해집니다.