**프로젝트 산출물 계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave`가 있음 |
| Empty/loading/error/success/recovery state matrix | Missing | 사용자 가시 상태가 있다고만 되어 있고, 화면별 empty/loading/error/success/recovery 상태 매트릭스는 없음 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid flowchart 있음 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~AC-108이 FR ID, Given/When/Then/Verification을 포함함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3이 FR ID와 검증 가능한 종료 조건을 포함함 |

**Findings**

**High - 접근 거부 응답이 리소스 존재와 상태를 누출할 수 있음**

- 근거: `FR-104`, `Authorization and data boundaries`, `AC-105`는 다른 팀장 또는 본인 신청 처리 시 `403`과 권한 거부 감사를 요구합니다. `/leave/:id`는 소유 직원과 현재 팀장만 허용되지만, 타인 신청 조회·처리에서 `403`을 언제 반환하고 `404`/동일 응답을 언제 반환할지 정의가 없습니다.
- 영향: ID를 아는 사용자가 휴가 신청 존재 여부, 현재 상태, 팀 소속 관계를 추론할 수 있습니다. 특히 감사 이벤트까지 남기는 경우 권한 거부 로깅 자체가 내부 식별자·상태 조회를 유도할 수 있습니다.
- 수정 방향: 조회·처리별 deny policy를 명시하세요. 예: 조직 밖 또는 가시 범위 밖 리소스는 indistinguishable `404`, 가시 범위 안이지만 금지된 상태 전이는 `403/409`. 권한 거부 감사 이벤트에 기록할 수 있는 필드도 “리소스 확인 전/후”로 구분해야 합니다.

**High - 멱등성 키 계약이 부족해 중복 생성·오용·교차 사용자 충돌을 검증하기 어려움**

- 근거: `FR-106`, `AC-108`은 idempotency key 사용과 같은 key 재시도 시 같은 신청 ID 반환을 요구하지만, key의 scope, TTL, 요청 본문 불일치 처리, 사용자·조직·operation 경계가 없습니다.
- 영향: 같은 key를 다른 직원/조직/엔드포인트에서 재사용했을 때 보안 경계가 흔들릴 수 있고, 같은 key에 다른 날짜·사유를 실어 보낸 재시도를 어떻게 처리할지 구현마다 달라집니다.
- 수정 방향: key scope를 `actor + organization + operation` 또는 더 엄격한 범위로 정의하고, 요청 fingerprint 불일치 시 `409` 또는 `422` 같은 고정 응답을 지정하세요. TTL과 재시도 응답의 감사 이벤트 생성 여부도 AC에 추가해야 합니다.

**Medium - 화면 상태 매트릭스가 없어 필수 UX·오류 복구 동작이 누락됨**

- 근거: Applicability에서 `State matrix`를 Required로 판정했지만 실제 섹션은 없습니다. `User flow`에는 입력 실패 시 “입력 유지와 오류”만 있고, `Authorization and data boundaries`에는 People Platform 실패 시 `503`과 상태 유지가 있으나 화면별 복구 상태가 없습니다.
- 영향: `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave`에서 빈 목록, 로딩, 권한 오류, HR 시스템 장애, 충돌, 성공 후 반영 상태가 제각각 구현될 수 있습니다.
- 수정 방향: 페이지별로 empty/loading/error/success/recovery 상태를 표로 추가하세요. 특히 `409`, `403/404`, `503`, 감사 이력 조회 실패, 팀 이동 후 접근 상실 케이스를 포함해야 합니다.

**Medium - 감사 이벤트 원자성 요구와 실패 이벤트 범위가 불명확함**

- 근거: `FR-105`는 생성·승인·반려·취소와 권한 거부를 기록한다고 하고, `FR-106`은 “상태와 감사 이벤트”의 원자성을 요구합니다. 그러나 권한 거부는 상태 변경이 없고, `AC-102`는 겹침 충돌 시 “성공 감사 이벤트 없음”만 말합니다.
- 영향: 실패 유형별 감사 정책이 불명확합니다. 권한 거부는 반드시 기록하지만 validation 실패, overlap `409`, concurrency `409`, People Platform `503`은 기록 대상인지 아닌지 해석이 갈립니다.
- 수정 방향: 감사 대상 이벤트를 성공 상태 변경, 권한 거부, 충돌, 외부 의존성 실패로 나누고 각 케이스의 기록 여부를 명시하세요. 원자성 요구도 “상태 변경 이벤트”와 “상태 변경 없는 보안 이벤트”로 분리하는 편이 검증 가능합니다.

**Medium - 동시성 AC의 이벤트 기대값이 모호함**

- 근거: `AC-106`은 승인과 취소 동시 요청에서 “한 건만 성공, 다른 건 409, 최종 이벤트 한 건”을 요구합니다. `FR-105`는 승인·취소를 감사 기록 대상으로 정의하지만, 실패한 `409` 시도에 대한 감사 여부는 정의하지 않습니다.
- 영향: “최종 이벤트 한 건”이 성공 상태 변경 이벤트만 의미하는지, 전체 감사 이벤트 총량을 의미하는지 불명확합니다. 보안/운영 감사 관점에서는 실패한 경쟁 요청을 남길 수도 있어 AC와 충돌할 수 있습니다.
- 수정 방향: AC-106의 Then을 “성공 상태 변경 감사 이벤트는 한 건”처럼 좁히거나, 실패한 `409` 이벤트 기록 여부를 별도로 명시하세요.

**Low - 반려 사유의 저장·가시성·감사 제외 범위가 부족함**

- 근거: `FR-103`은 반려 사유 1~500자를 요구하고, Risks는 휴가 사유를 직원 본인과 현재 팀장만 읽고 로그·감사 이벤트에 넣지 않는다고 합니다. 하지만 “반려 사유”는 누가 읽을 수 있는지, 감사자에게 노출되는지, 로그 제외 대상인지 명시되지 않았습니다.
- 영향: 휴가 사유와 달리 반려 사유가 민감 정보를 포함할 수 있는데 감사자 또는 로그에 노출될 가능성이 남습니다.
- 수정 방향: 반려 사유의 가시 주체, 감사 이벤트 포함 여부, 로그 redaction 정책을 휴가 사유와 별도로 정의하세요.

**Low - 출시 전 API 지연 목표가 acceptance나 delivery와 연결되지 않음**

- 근거: `Non-functional requirements`와 `Assumptions and open decisions`에 API 지연 목표를 내부 베타 후 결정한다고 되어 있지만, `Delivery`에는 해당 결정의 종료 조건이 없습니다.
- 영향: 정식 출시 전 결정해야 하는 비기능 요구가 누락된 채 Phase 완료로 간주될 수 있습니다.
- 수정 방향: 별도 phase gate 또는 release readiness 조건에 “API latency SLO 확정 및 측정 방식 합의”를 넣으세요.

검증은 제공된 PRD 본문만 기준으로 수행했습니다. 요청에 따라 파일 생성, 저장소 탐색, 원문 재작성은 하지 않았습니다.