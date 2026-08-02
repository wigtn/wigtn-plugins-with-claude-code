**계약 감사**

| Contract | 적용성 | Status | Evidence / Gap |
|---|---:|---|---|
| Applicability ledger | Required | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Required | Present | `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Required | Present, partial | State matrix는 있으나 `/team/leave`, `/audit/leave`, 직원 상세 조회 상태가 빠져 있음 |
| Mermaid user or system flow | Required | Present | 신청 → 검증 → PENDING → 취소/승인/반려 flow 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | Required | Present, partial | AC-101~108이 FR에 매핑됨. 다만 취소 성공/실패, 감사자 조회, 상태 명령 멱등성은 미검증 |
| Delivery phases mapped to requirement IDs and exit conditions | Required | Present | Phase 1~3이 FR ID와 exit condition에 연결됨 |

**Findings**

**High — 직원 이동 후 휴가 사유 접근 권한이 과도하게 열릴 수 있음**

근거: FR-104는 “직원 이동 후에는 새 팀장이 PENDING 신청을 처리하고 이전 팀장은 접근을 잃는다”고 하고, Risks는 “휴가 사유는 직원 본인과 현재 팀장만 읽는다”고 합니다. 그런데 승인/반려/취소된 과거 신청의 사유를 새 팀장이 계속 읽을 수 있는지, 처리 당시 팀장만 읽을 수 있는지, 이전 팀장이 이력 목적상 읽을 수 있는지가 불명확합니다.

영향: 팀 이동 이후 새 팀장에게 과거 민감 사유가 노출될 수 있고, 반대로 과거 처리 책임자가 감사나 분쟁 대응에 필요한 상세를 잃을 수 있습니다.

수정 방향: `PENDING 처리 권한`, `상세 사유 열람 권한`, `감사 이벤트 열람 권한`을 분리하세요. 예: PENDING은 현재 팀장만 처리, 최종 상태의 사유 열람은 직원 본인과 처리 당시 권한자 또는 명시된 HR 역할로 제한.

**High — 취소 흐름이 핵심 상태 전이인데 acceptance coverage가 없음**

근거: FR-102는 PENDING에서 CANCELLED 전이를 허용하고, FR-105는 취소 감사 이벤트를 요구합니다. User flow에도 직원 취소가 있습니다. 하지만 AC에는 취소 성공, 비소유자 취소, APPROVED/REJECTED 이후 취소 거부, 취소 감사 이벤트 검증이 없습니다.

영향: 구현자가 취소 API, 감사 이벤트, 권한 검사를 빠뜨려도 현재 AC로는 PRD 충족처럼 보일 수 있습니다.

수정 방향: 취소 성공 AC와 취소 거부 AC를 추가하세요. 최소한 “소유 직원이 PENDING 취소 → CANCELLED + 감사 이벤트”, “최종 상태 취소 시도 → 409 + 상태 불변”, “타인 취소 시도 → 403 + 권한 거부 감사”가 필요합니다.

**High — 권한 거부 감사가 리소스 존재 여부를 누출할 수 있음**

근거: FR-105는 권한 거부도 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 합니다. 그러나 권한이 없는 요청에서 이전 상태를 기록하거나 응답/감사 조회에 노출하면 해당 신청의 존재와 상태가 새어 나갈 수 있습니다.

영향: 타 팀 신청 ID를 추측해 403 감사 이벤트나 상태 정보를 통해 신청 존재 여부, 상태, 조직 내 활동을 유추할 수 있습니다.

수정 방향: 권한 거부 감사의 필드를 별도 정의하세요. 권한 없는 actor에게는 동일한 오류 표면을 유지하고, 감사 이벤트에는 `target_request_id`, `denial_reason_code`, `state_known_to_server` 같은 내부 필드를 둘 수 있되 감사자 조회 시 민감 필드 노출 정책을 명확히 해야 합니다.

**Medium — State matrix가 실제 화면 전체를 커버하지 않음**

근거: Pages/routes에는 `팀 승인함`, `감사 이력`, `휴가 상세`가 있지만 State matrix는 `내 휴가`, `신청 폼`, `승인 상세`만 다룹니다.

영향: 팀 승인함의 빈 목록/권한 상실/직원 이동 후 stale item 처리, 감사 이력의 권한 오류/필터 없음/이벤트 없음 상태가 구현자 재량으로 남습니다.

수정 방향: `/team/leave`, `/audit/leave`, `/leave/:id`의 소유 직원 상세 상태를 matrix에 추가하세요. 특히 403, 404/존재 은닉, 409, People Platform 503, stale PENDING 항목 회복 동작을 구분해야 합니다.

**Medium — 상태 명령의 멱등성 요구는 있으나 검증은 신청 생성에만 있음**

근거: FR-106은 “모든 생성·상태 명령은 idempotency key”를 요구하지만 AC-108은 신청 재시도만 검증합니다. 승인/반려/취소 재시도, payload mismatch, actor mismatch, key TTL, 조직 범위가 정의되지 않았습니다.

영향: 승인 버튼 재시도나 네트워크 재전송에서 중복 감사 이벤트, 잘못된 응답 재사용, 다른 사용자의 key 충돌 같은 문제가 생길 수 있습니다.

수정 방향: 멱등성 key scope를 `org + actor + operation + target + key` 수준으로 정의하고, 동일 key 다른 payload 처리 방식과 TTL을 명시하세요. 승인/반려/취소 각각의 재시도 AC도 추가해야 합니다.

**Medium — 겹침 방지의 동시 생성 케이스가 검증되지 않음**

근거: FR-101은 PENDING·APPROVED와 겹칠 수 없다고 하고 FR-106은 조건부 갱신을 요구하지만, AC는 기존 신청과의 충돌만 다룹니다. 동시에 두 개의 겹치는 신청을 생성하는 race condition은 별도 검증이 없습니다.

영향: 같은 직원이 거의 동시에 겹치는 휴가 두 건을 만들 수 있으면 핵심 불변식이 깨집니다.

수정 방향: 동시 생성 AC를 추가하고, 구현 방향에는 DB exclusion constraint, serializable transaction, per-employee date-range lock 등 불변식을 보장하는 수단을 요구하세요.

**Medium — 휴가 일수 산정 기준이 검증 불가능함**

근거: FR-101은 “KST 달력일”, “양끝 포함”만 정의합니다. 주말, 공휴일, 회사 휴무일, 입사 전/퇴사 후 날짜, 과거 날짜, 최대 기간, 휴가 잔여일 차감 여부는 없습니다.

영향: “일 단위 휴가”의 실제 승인 가능 여부와 신청 일수가 조직 정책과 다르게 구현될 수 있습니다.

수정 방향: 이 PRD가 단순 상태 관리 범위라면 명시적으로 “잔여일/근무일/공휴일 검증은 제외”라고 Non-goal에 넣으세요. 범위에 포함한다면 People Platform 또는 휴가 정책 서비스의 진실 공급원과 검증 AC가 필요합니다.

**Low — API 지연 목표가 정식 출시 전 결정으로 남아 현재 exit condition이 약함**

근거: NFR와 Open decisions에서 지연 목표를 베타 후 결정한다고 합니다.

영향: Phase exit에는 영향이 작지만, 정식 출시 readiness에서 성능 기준이 늦게 확정되어 회귀 판단이 어려울 수 있습니다.

수정 방향: 지금 수치를 만들 필요는 없지만, “베타 종료일”, 측정 지표, 측정 구간, 책임자를 acceptance 가능한 형태로 두는 것이 좋습니다.

검증기는 실행하지 않았습니다. 요청대로 저장소 탐색이나 파일 생성 없이 제공된 PRD 원문만 검토했습니다.