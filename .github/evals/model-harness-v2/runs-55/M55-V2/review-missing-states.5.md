**산출물 계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 표시함 |
| Pages and routes | Present | `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Missing | 적용성은 Required인데 실제 목록·상세·폼·처리·감사 화면의 empty/loading/error/success/recovery 상태 행렬이 없음 |
| Mermaid user or system flow | Present | 신청 → 검증 → PENDING → CANCELLED/APPROVED/REJECTED Mermaid flow 있음 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~AC-108이 FR ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3이 FR ID와 검증 가능한 exit condition을 포함 |

**Findings**

**High: 상태 매트릭스가 적용 대상으로 선언됐지만 누락됨**

영향도: UI와 API 오류 처리의 구현 계약이 비어 있어, 실패 시 입력 유지, 403/409/503, 빈 목록, 로딩, 재시도 가능 여부가 화면별로 다르게 구현될 수 있습니다.

근거: `Applicability`에서 `State matrix`가 Required로 표시되어 있지만, 별도의 empty/loading/error/success/recovery state matrix가 없습니다. `User flow`에는 “입력 유지와 오류”만 있고, `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave`별 상태는 정의되지 않았습니다.

수정 방향: 각 route별로 empty/loading/success/error/recovery 상태를 행으로 정의하고, 특히 403, 409, 503, validation error, stale state conflict에서 사용자에게 보이는 상태와 재시도 가능성을 명시해야 합니다.

**High: 멱등성 키의 범위·보관·payload 불일치 정책이 없어 보안 및 정합성 검증이 불완전함**

영향도: 같은 idempotency key가 사용자, 조직, 명령 종류, payload를 넘어 재사용될 때 잘못된 신청 ID 반환, 중복 차단 실패, 또는 다른 사용자의 요청 결과 노출 위험이 생깁니다.

근거: FR-106은 “모든 생성·상태 명령은 idempotency key”를 요구하고 AC-108은 “같은 신청 ID, 중복 이벤트 없음”만 검증합니다. 하지만 key scope, TTL, actor/org binding, operation binding, 동일 key와 다른 payload 재시도 처리 규칙이 없습니다.

수정 방향: idempotency key를 `org + actor + command type + key` 범위로 제한하고, 동일 key 다른 payload는 409 또는 422로 거부하며, 응답 재생 범위와 보관 기간을 AC에 추가해야 합니다.

**Medium: 목록/상세 조회 권한과 사유 전문 노출 정책이 감사자·팀장·팀 이동 케이스에서 충분히 검증되지 않음**

영향도: 휴가 사유는 민감 정보인데, 감사자에게 노출 금지한다는 정책이 실제 API 응답 수준의 acceptance criteria로 고정되어 있지 않습니다. 팀 이동 후 이전 팀장이 상세 캐시나 목록에서 사유를 계속 볼 위험도 남습니다.

근거: `Users, roles, and permissions`와 `Risks and mitigations`는 “감사자는 휴가 사유 전문 읽기 금지”, “직원 본인과 현재 팀장만 읽음”을 말합니다. 그러나 AC는 감사자 조회에서 redaction을 검증하지 않고, AC-107도 “접근·처리”만 말할 뿐 상세 사유 비노출과 캐시/목록 제거를 명시하지 않습니다.

수정 방향: 감사 이력 응답에는 request ID, 상태 변화, actor, timestamp만 포함하고 reason 전문은 제외한다는 AC를 추가하세요. 팀 이동 후 이전 팀장의 목록·상세·처리·사유 조회가 모두 403/미노출인지 분리 검증하는 것이 좋습니다.

**Medium: People Platform 장애 정책이 처리 요청에만 명확하고 조회/목록/상세에는 불명확함**

영향도: 인사 시스템 장애 시 팀 승인함과 상세 접근에서 fail-open, 오래된 권한 캐시 사용, 과도한 500 처리 등 구현 편차가 생길 수 있습니다.

근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고만 합니다. FR-104는 작업별로 현재 팀을 검사한다고 하지만, 조회 작업에서 People Platform 장애 시의 응답과 상태 유지, 사용자 메시지, 감사 기록 여부가 없습니다.

수정 방향: 조회·목록·처리 각각에서 People Platform 실패 시 fail-closed 여부, 503 반환 여부, 입력/상태 유지, 권한 거부 감사와 장애 감사의 차이를 명시해야 합니다.

**Medium: 감사 이벤트 요구사항과 AC 커버리지 사이에 빈칸이 있음**

영향도: “권한 거부”와 “취소” 감사가 핵심 P0인데, acceptance criteria가 일부 성공/거부 경로만 덮어 구현 누락을 잡지 못할 수 있습니다.

근거: FR-105는 생성·승인·반려·취소와 권한 거부를 모두 기록한다고 합니다. AC-101, AC-103, AC-104, AC-105는 일부를 검증하지만 직원 취소 성공 감사 AC가 없고, 감사 이벤트 필드 `actor, request ID, 이전/이후 상태, timestamp` 전체를 검증하는 AC도 없습니다.

수정 방향: 취소 성공 AC를 추가하고, 모든 감사 이벤트 검증에서 필수 필드와 reason 전문 미포함을 명시하세요.

**Low: API 지연 목표가 출시 전 결정으로 남아 있어 성능 acceptance는 현재 검증 불가능함**

영향도: 베타까지는 허용 가능하지만, 정식 출시 readiness 판단에는 성능 기준이 없습니다.

근거: Non-functional requirements와 Assumptions에서 “내부 베타 종료일까지 제품 책임자가 결정”이라고 되어 있습니다.

수정 방향: 현재 PRD에서는 open decision으로 유지하되, 정식 출시 전 gate로 “P95/P99 또는 내부 운영 기준 결정 및 측정 통과” 같은 검증 조건을 Delivery나 Acceptance에 연결하세요.

검토는 제공된 PRD 원문만 기준으로 했고, 저장소 탐색이나 파일 생성은 하지 않았습니다. PRD 파일 경로가 없으므로 validator도 실행하지 않았습니다.