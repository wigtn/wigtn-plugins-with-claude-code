**산출물 계약 감사**

| Contract | 존재 여부 | 적용성 판단 | 근거 | 판정 |
|---|---:|---:|---|---|
| Pages/routes | 있음 | 적용 가능 | `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave`가 역할·주요 액션과 연결됨 | 충족, 단 상태별 UI 권한은 부족 |
| State matrix | 없음 | 적용 필요 | Applicability에서 Required라고 했지만 실제 상태 매트릭스 표가 없음. PENDING/APPROVED/REJECTED/CANCELLED의 화면별 표시·액션·오류·빈 상태가 정의되지 않음 | 누락 |
| User flow | 있음 | 적용 가능 | 신청 → 검증 → PENDING → 취소/승인/반려 흐름 제공 | 부분 충족, 조회·권한거부·HR 장애 흐름은 빠짐 |

**Findings**

**High: 동시 신청 시 기간 중복 방지 검증이 불완전합니다.**  
근거: FR-101은 `PENDING·APPROVED`와 겹칠 수 없다고 하고, FR-106은 “모든 생성·상태 명령은 idempotency key와 조건부 갱신”을 요구합니다. 하지만 생성은 기존 row의 조건부 갱신이 아니라 새 row 삽입이라, 두 요청이 동시에 같은 기간을 신청하면 둘 다 사전 검증을 통과할 수 있습니다. AC도 승인/취소 동시성만 검증하고 생성 간 overlap race는 없습니다.  
수정 방향: DB exclusion constraint, serializable transaction, 사용자별 날짜 범위 잠금, 또는 canonical leave-day allocation 같은 원자적 충돌 방지 방식을 명시하고, 동시 신청 AC를 추가해야 합니다.

**High: 취소 기능의 요구사항과 검증이 빠져 있습니다.**  
근거: 역할 표와 User flow에는 직원의 `PENDING` 취소가 있지만 Functional requirements에는 “누가 어떤 조건에서 취소 가능한지”가 독립 FR로 정의되지 않았고 AC에도 취소 성공, 취소 권한거부, 이미 승인된 신청 취소 실패가 없습니다. FR-102는 상태 전이만 말할 뿐 작업 권한과 감사 요건을 충분히 검증하지 못합니다.  
수정 방향: “소유 직원만 본인 PENDING 신청을 CANCELLED로 전이 가능” 같은 FR과 AC를 추가하고, 성공 감사 이벤트 및 실패 시 상태 불변을 검증해야 합니다.

**High: State matrix 계약이 Required인데 실제 산출물이 없습니다.**  
근거: Applicability에서 State matrix를 Required로 선언했지만, 화면별 사용자 가시 상태가 표로 정의되어 있지 않습니다. 특히 목록 empty/loading/error, 403, 409, 503, 처리 중 중복 클릭, 승인 후 버튼 비활성화, 반려 사유 validation 상태가 불명확합니다.  
수정 방향: route × role × request status × HR availability × allowed action 매트릭스를 추가해야 구현·QA가 같은 기준으로 검증할 수 있습니다.

**Medium: 감사 로그의 “권한 거부” 기록은 보안 경계가 모호합니다.**  
근거: FR-105는 권한 거부도 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 합니다. 그런데 타 조직 또는 접근 불가 신청에 대해 실제 request ID와 상태를 감사 이벤트에 남기거나 감사자에게 노출하면 신청 존재 여부나 상태가 간접 유출될 수 있습니다. 감사자는 조직 내 이벤트만 읽는다고 되어 있지만, 거부 이벤트의 조직 귀속을 어떤 기준으로 결정하는지 불명확합니다.  
수정 방향: 권한 거부 감사 이벤트는 세션 조직 기준으로 기록하고, 접근 불가 리소스의 실제 상태·소유자·사유·타 조직 식별자를 포함하지 않는다고 명시해야 합니다.

**Medium: 감사자 권한과 휴가 사유 비노출 요구가 상세 화면·감사 화면 수준에서 검증되지 않습니다.**  
근거: 역할 표는 감사자가 휴가 사유 전문을 읽을 수 없다고 하고 FR-105도 감사 이벤트에 사유 전문을 넣지 않는다고 합니다. 하지만 `/audit/leave`에서 어떤 필드가 허용되는지, request 상세로 drill-down 가능한지, 반려 사유도 민감정보로 취급되는지 정의가 없습니다.  
수정 방향: 감사 이벤트 필드 allowlist를 명시하고, 휴가 사유와 반려 사유의 노출 주체를 분리해야 합니다. AC에 감사자가 사유 전문을 볼 수 없다는 검증을 추가하는 것이 좋습니다.

**Medium: 팀장 조회 권한과 처리 권한의 HR 장애 동작이 섞여 있습니다.**  
근거: Authorization에는 “인사 시스템 실패 시 처리 요청은 fail-closed 503”이라고 되어 있지만 조회 요청, 팀 승인함 목록, 상세 접근에서 People Platform 장애가 발생했을 때의 응답과 UI 상태는 없습니다. FR-104는 직원 이동 후 이전 팀장이 접근을 잃는다고 하므로 조회도 HR 의존성이 있습니다.  
수정 방향: 조회·목록·처리 각각의 HR 장애 정책을 분리해 503, 캐시 사용 금지 여부, 입력 유지, 재시도 UX를 정의해야 합니다.

**Medium: idempotency key 범위와 응답 재현 규칙이 검증 불가능합니다.**  
근거: FR-106과 AC-108은 같은 key 재시도 시 같은 신청 ID와 중복 이벤트 없음만 말합니다. 하지만 key가 actor별인지 조직별인지, endpoint별인지, payload가 달라진 같은 key를 409/422로 볼지, 보관 기간은 얼마인지가 없습니다.  
수정 방향: idempotency key scope, payload hash mismatch 처리, retention window, 상태 명령 재시도 응답 규칙을 명시해야 합니다.

**Low: API 지연 목표가 출시 전 결정으로 남아 있어 NFR로는 검증 불가능합니다.**  
근거: Non-functional requirements와 Open decisions에 “내부 베타 측정 후 제품 책임자가 결정”이라고만 되어 있습니다. 지금 PRD 기준으로는 구현 완료 여부를 판정할 수 없습니다.  
수정 방향: 현재는 open decision으로 유지하되, Delivery exit condition에는 포함하지 않거나 “GA 전 별도 release gate”로 분리하는 편이 명확합니다.