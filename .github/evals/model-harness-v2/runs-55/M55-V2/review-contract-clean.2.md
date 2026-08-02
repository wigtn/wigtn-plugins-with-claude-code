**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 Pages/routes, State matrix, User flow의 Required 여부와 근거를 명시 |
| Pages and routes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 주요 surface별 Empty/Loading/Error/Success/Recovery 정의 |
| Mermaid user or system flow | Present | `User flow` Mermaid로 신청→검증→PENDING→취소/승인/반려 흐름 정의 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `Acceptance criteria`가 AC별 FR 매핑, Given/When/Then/Verification 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery`가 Phase별 Requirement IDs와 exit condition 포함 |

**Findings**

**High — 멱등성 키의 보안 경계가 불명확함**

근거: `FR-106`, `AC-108`

`같은 idempotency key 재시도`가 같은 신청 ID를 반환한다고만 되어 있고, 키가 어떤 범위로 고립되는지 정의되지 않았습니다. 조직, actor, operation type, request fingerprint에 바인딩되지 않으면 다른 사용자의 키 재사용, 요청 본문 변경 재시도, 처리/생성 명령 간 충돌 같은 보안·정합성 문제가 생길 수 있습니다.

수정 방향: idempotency key는 최소한 `organization + actor + operation + request fingerprint` 단위로 유일해야 하며, 같은 키에 다른 payload가 오면 기존 결과 반환이 아니라 `409` 또는 `422`로 거부하도록 명시하세요. 응답 재생 시 권한 재검사 여부도 정해야 합니다.

**Medium — 취소 기능의 정상·권한·불가 상태 검증이 부족함**

근거: `Users, roles, and permissions`, `FR-102`, `FR-105`, `Pages and routes`, `AC-106`

직원은 `대기 취소`가 가능하고 상태 전이에도 `CANCELLED`가 포함되지만, acceptance criteria에는 취소 단독 성공 케이스가 없습니다. `AC-106`은 승인과 취소 동시성만 검증하므로, 본인 PENDING 취소, 타인 취소 금지, APPROVED/REJECTED/CANCELLED 이후 취소 금지, 취소 감사 이벤트를 직접 검증하지 못합니다.

수정 방향: 취소 전용 AC를 추가하세요. 예: 본인 PENDING 취소 시 `CANCELLED + 감사 이벤트`, 타인 또는 최종 상태 취소 시 `403/409 + 상태 불변 + 필요한 감사 정책`.

**Medium — 권한 거부 감사 범위가 모호함**

근거: `FR-105`, `AC-105`, `Authorization and data boundaries`

`권한 거부`를 감사 이벤트로 남긴다고 되어 있지만, 어떤 권한 거부가 대상인지 불분명합니다. 조회 거부, 처리 거부, 감사 이력 접근 거부, 조직 경계 위반, People Platform 조회 실패로 인한 fail-closed 503이 모두 같은 정책인지 알 수 없습니다. 현재 AC는 `다른 팀장 또는 팀장 본인 신청 처리`만 검증합니다.

수정 방향: 감사 대상 권한 거부를 명령별로 나누세요. 특히 `read denied`와 `mutation denied`를 구분하고, 403은 감사 대상인지, 404-style concealment를 쓸 경우에도 감사하는지, 503 fail-closed는 권한 거부가 아닌 dependency failure로 감사하는지 정해야 합니다.

**Medium — 감사자의 데이터 접근 모델이 구현 가능할 만큼 구체적이지 않음**

근거: `Users, roles, and permissions`, `FR-105`, `Pages and routes`

감사자는 조직 내 감사 이벤트를 읽을 수 있지만 휴가 사유 전문은 읽을 수 없다고 되어 있습니다. 그러나 감사 이벤트 스키마에 신청자 ID, 팀 ID, actor, request ID, 상태, timestamp 외 어떤 식별자와 필터가 포함되는지 정의가 없습니다. 감사자가 `/audit/leave`에서 어떤 범위로 검색하고, request ID로 상세를 따라갈 수 있는지에 따라 사유 노출 우회 가능성이 달라집니다.

수정 방향: 감사 이벤트의 허용 필드와 금지 필드를 명시하세요. 감사 화면에서 request 상세 링크가 있다면 감사자에게 사유가 노출되지 않도록 별도 redacted view 또는 이벤트 전용 상세를 요구해야 합니다.

**Low — KST 달력일 입력의 API 표현이 모호함**

근거: `FR-101`

`KST 달력일`과 inclusive date는 정의되어 있지만, API가 date-only 문자열을 받는지, timestamp를 받는지, 서버가 어떤 기준으로 정규화하는지 불명확합니다. 클라이언트 timezone, DST는 KST에 없더라도 해외 접속자의 로컬 날짜 변환에서 하루 밀림 버그가 날 수 있습니다.

수정 방향: `YYYY-MM-DD` date-only를 KST calendar date로 받고 저장·비교도 date-only 또는 명시적 KST 기준으로 한다고 적으세요. timestamp 입력은 거부하거나 변환 규칙을 명확히 두는 편이 좋습니다.

**Low — 팀장 상세 조회 권한과 팀 승인함 목록 범위가 약간 다르게 읽힘**

근거: `Pages and routes`, `FR-103`, `FR-104`

`팀 승인함`은 대기 신청 조회이고, `휴가 상세`는 현재 팀장이 조회 가능하다고 되어 있습니다. 최종 상태가 된 신청을 현재 팀장이 계속 상세 조회할 수 있는지, 아니면 PENDING 처리 목적일 때만 가능한지 불명확합니다. 이 차이는 개인정보 노출 기간에 영향을 줍니다.

수정 방향: 팀장의 상세 조회 범위를 `현재 팀 직원의 PENDING만`, 또는 `현재 팀 직원의 과거 처리 건 포함`처럼 명시하고, 퇴사·팀 이동 후 기존 상세 접근이 어떻게 되는지도 `FR-104`와 맞춰 정리하세요.

검토 기준상 필수 산출물 계약은 모두 존재합니다. 주요 보완점은 계약 부재보다는 멱등성 보안 경계, 취소 검증, 감사 범위의 명확성입니다.