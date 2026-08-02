**산출물 계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 모두 Required로 표시 |
| Pages and routes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`가 Empty/Loading/Error/Success/Recovery를 정의 |
| Mermaid user or system flow | Missing | User flow가 Required이고 신청부터 최종 결정까지 다단계 생명주기이나 Mermaid flow 산출물이 없음 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~AC-108이 FR ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Delivery Phase 1~3이 Requirement IDs와 exit condition을 포함 |

**Findings**

**Blocker - Required user flow 산출물 누락**

- 영향도: 상태 전이, 역할 전환, 팀 이동 후 접근권 변경, 감사 이벤트 발생 시점이 구현자마다 다르게 해석될 수 있습니다.
- 근거: `Applicability`에서 User flow를 Required로 선언했고, 리뷰 계약상 다단계 lifecycle은 Mermaid flow가 필요합니다. 그러나 Mermaid user/system flow가 없습니다.
- 수정 방향: 직원 신청 → PENDING → 취소/승인/반려, 팀 이동 시 현재 팀장 재평가, 권한 거부 감사 이벤트, HR 장애 fail-closed를 포함한 Mermaid flow를 추가하세요.

**High - 감사자 데이터 경계와 감사 이력 조회 범위가 서로 불명확함**

- 영향도: 감사자가 휴가 사유 전문을 읽지 못해야 한다는 보안 요구가 UI/API 응답 설계에서 누락될 수 있습니다.
- 근거: `Users, roles, and permissions`는 감사자에게 “휴가 사유 전문 읽기”를 금지하지만, `/audit/leave`의 이벤트 조회 필드와 마스킹 규칙은 없습니다. FR-105는 감사 이벤트에 사유 전문을 기록하지 않는다고만 합니다.
- 수정 방향: 감사 API 응답 필드를 명시하세요. 예: actor, action, request ID, target application ID, 이전/이후 상태, timestamp, denial reason category 정도만 허용하고 leave reason, rejection reason 전문 포함 여부를 명확히 분리해야 합니다.

**High - 생성 시 중복 기간 검사가 동시성 조건으로 충분히 검증되지 않음**

- 영향도: 동시에 두 신청이 들어오면 `PENDING·APPROVED 신청과 겹칠 수 없다`가 깨질 수 있습니다.
- 근거: FR-101은 겹침 금지, FR-106은 idempotency key와 조건부 갱신을 말하지만 AC에는 “동시 생성으로 겹치는 휴가 신청” 검증이 없습니다. AC-106은 승인과 취소 동시 요청만 다룹니다.
- 수정 방향: 동일 직원의 겹치는 기간에 대한 동시 생성 AC를 추가하고, DB exclusion constraint, serializable transaction, 잠금 전략 등 구현 가능한 원자적 충돌 방지 조건을 요구사항 수준에서 지정하세요.

**Medium - 취소 권한과 취소 감사 기준이 AC로 충분히 닫히지 않음**

- 영향도: 직원이 본인 PENDING 신청만 취소할 수 있다는 정책이 구현·검증에서 빠질 수 있습니다.
- 근거: 권한 표에는 직원의 “대기 취소”가 있고 FR-102는 PENDING에서 CANCELLED 전이를 허용합니다. 그러나 AC에는 취소 성공, 타인 취소 거부, APPROVED/REJECTED 취소 실패가 없습니다.
- 수정 방향: 본인 PENDING 취소 성공, 타인 취소 403, 최종 상태 취소 409, 각각의 감사 이벤트 기대값을 AC로 추가하세요.

**Medium - 반려 사유의 개인정보/가시성 정책이 없음**

- 영향도: 반려 사유가 감사 로그, 목록, 팀장 화면, 직원 상세에 과노출될 수 있습니다.
- 근거: FR-103은 반려 사유 1~500자를 요구하지만, `Risks and mitigations`의 “휴가 사유” 보호는 직원 신청 사유에만 초점이 있습니다. 반려 사유의 저장, 조회, 감사 포함 여부가 불명확합니다.
- 수정 방향: 반려 사유를 누가 볼 수 있는지, 감사 이벤트에 전문을 넣는지 여부, 로그 마스킹 규칙을 명시하세요.

**Medium - HR/People Platform 조회 시점과 캐싱 정책이 검증 불가능함**

- 영향도: “현재 팀장” 판정이 캐시, 지연 동기화, 장애 상황에 따라 달라질 수 있습니다.
- 근거: FR-103은 “승인 시점 인사 시스템의 현재 팀”을 기준으로 하고, Authorization은 HR 실패 시 503 fail-closed를 말합니다. 하지만 조회 freshness, 캐시 허용 여부, People Platform timeout/retry 기준은 없습니다.
- 수정 방향: 처리·조회별 People Platform 판정 시점, 허용 캐시 TTL 또는 캐시 금지, 장애 판정 기준을 제품 요구로 정리하세요.

**Low - API 지연 목표가 출시 전 결정으로 열려 있어 NFR 검증성이 약함**

- 영향도: 정식 출시 준비 시 성능 합격 기준이 늦게 정해져 테스트와 운영 준비가 밀릴 수 있습니다.
- 근거: Non-functional requirements와 Open decisions에 “내부 베타 후 제품 책임자가 결정”이라고만 되어 있습니다.
- 수정 방향: 베타 exit 전에 최소 측정 지표를 정의하세요. 예: p95 latency를 측정한다, endpoint별 baseline을 수집한다, 정식 출시 gate에 수치 기준을 연결한다.

**Low - 목록 화면의 노출 필드와 필터 기준이 부족함**

- 영향도: 직원 목록과 팀 승인함에서 어떤 상태와 범위를 보여줄지 구현 편차가 생길 수 있습니다.
- 근거: Pages/routes는 목록·대기 신청 조회를 말하지만, `/leave`가 CANCELLED/REJECTED 포함 전체인지, `/team/leave`가 PENDING만인지, 정렬·페이지네이션·기간 필터가 없습니다.
- 수정 방향: 각 목록의 포함 상태, 기본 정렬, 최소 필터, 페이지네이션 여부를 명시하세요.

검토는 제공된 PRD 원문만 기준으로 했고, 저장소 탐색이나 파일 생성은 하지 않았습니다.