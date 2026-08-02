**산출물 계약 감사**

| Contract | Status | Evidence | 적용성 판단 |
|---|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정 | 적용 가능 |
| Pages and routes | Present | `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 | 적용 가능 |
| Empty/loading/error/success/recovery state matrix | Present | `내 휴가`, `신청 폼`, `승인 상세` 상태 정의 | 적용 가능하지만 일부 화면 누락 |
| Mermaid user or system flow | Present | 신청 → 검증 → PENDING → 취소/승인/반려 flowchart | 적용 가능 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~108이 FR ID와 Given/When/Then/Verification 포함 | 적용 가능 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3이 FR ID와 exit condition 포함 | 적용 가능 |

**Findings**

**High — 상태 전이 계약과 취소 요구사항이 검증 가능하게 닫혀 있지 않음**  
근거: FR-102는 `PENDING`에서 `CANCELLED` 전이를 허용하고, 권한 표는 직원의 `대기 취소`를 허용하지만, AC에는 직원 취소 단독 기준이 없습니다. AC-106은 승인과 취소 동시 요청만 다룹니다.  
영향: 직원 취소 API의 권한, 감사 이벤트, 멱등성, 409 처리, 이미 승인된 신청 취소 불가 여부가 구현마다 달라질 수 있습니다.  
수정 방향: `직원 본인 + PENDING 신청` 취소 성공 AC와 `타인/최종상태 취소 실패` AC를 추가하고, FR-103 또는 별도 FR에서 취소 명령의 권한·상태 조건을 명시하세요.

**High — idempotency key 범위와 충돌 의미가 불명확함**  
근거: FR-106은 “모든 생성·상태 명령은 idempotency key”를 사용한다고만 하고, AC-108은 “같은 key 재시도 → 같은 신청 ID”만 검증합니다.  
영향: 같은 key로 다른 payload를 보내는 경우, 사용자/조직/operation 간 key 충돌, 승인과 반려에 같은 key를 쓰는 경우, key 보관 기간이 구현자 판단으로 남습니다. 이는 중복 생성, 잘못된 재사용, 감사 이벤트 누락으로 이어질 수 있습니다.  
수정 방향: key scope를 `organization + actor + operation + request body hash` 등으로 정의하고, 같은 key·다른 payload는 `409` 또는 `422`로 고정하세요. 상태 명령에도 동일하게 “동일 결과 반환, 중복 이벤트 없음” 기준을 추가하세요.

**High — 감사 이벤트의 실패/거부 범위가 모호하고 일부는 보안상 누출 위험이 있음**  
근거: FR-105는 “권한 거부”를 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 합니다. 하지만 권한 거부가 조회·목록·처리·취소 중 어디까지인지, 존재하지 않거나 접근 불가한 신청의 `request ID`와 상태를 감사 이벤트에 남겨도 되는지 불명확합니다.  
영향: 감사 로그가 타인의 신청 존재 여부나 상태를 간접적으로 노출할 수 있습니다. 반대로 구현자가 일부 권한 거부를 기록하지 않아 요구사항을 만족했다고 착각할 수도 있습니다.  
수정 방향: 권한 거부 이벤트 스키마를 성공 이벤트와 분리하세요. 접근 불가 객체의 상태/소유자/사유는 기록하지 않는 원칙, `target_request_id` 기록 가능 조건, 조회 거부와 처리 거부의 감사 범위를 명시하세요.

**Medium — State matrix가 정의된 라우트 전체를 커버하지 않음**  
근거: Pages/routes에는 `휴가 상세`, `팀 승인함`, `감사 이력`이 있는데 State matrix는 `내 휴가`, `신청 폼`, `승인 상세`만 있습니다.  
영향: 감사 이력의 권한 오류/빈 상태, 팀 승인함의 빈 목록/HR 장애, 직원 상세의 최종 상태 표시 같은 사용자 가시 상태가 검증되지 않습니다.  
수정 방향: 라우트 단위로 `내 휴가`, `신청 폼`, `휴가 상세`, `팀 승인함`, `승인/반려 처리`, `감사 이력`을 모두 매핑하거나, 통합된 surface라면 어떤 route를 대표하는지 Evidence에 명시하세요.

**Medium — 감사자의 데이터 경계는 의도는 좋지만 조회 필드 계약이 부족함**  
근거: 권한 표는 감사자가 “휴가 사유 전문 읽기” 금지이고, FR-105는 감사 이벤트에 사유 전문을 기록하지 않는다고 합니다. 그러나 감사 이력 화면/API가 어떤 필드를 반환하는지는 없습니다.  
영향: 감사자가 이벤트 외에 상세 API를 통해 사유를 읽거나, 감사 이벤트 metadata에 사유 일부가 들어가는 구현이 생길 수 있습니다.  
수정 방향: 감사자 응답 필드를 allowlist로 정의하세요. 예: actor, action, request ID, 이전/이후 상태, timestamp, denial reason category 등. 사유 원문, 사유 preview, free-text error detail 제외를 명시하면 좋습니다.

**Medium — People Platform 장애 처리 범위가 처리 요청에만 명확함**  
근거: Authorization and data boundaries는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고 합니다. 하지만 팀 승인함 조회, 상세 조회에서 현재 팀장 관계를 확인해야 하는 경우의 동작은 명확하지 않습니다.  
영향: 목록/상세에서는 캐시를 쓰고 처리에서는 live check를 쓰는 등 일관성이 깨질 수 있습니다. 이전 팀장이 장애 중 접근하는 보안 결함도 가능해집니다.  
수정 방향: People Platform 의존 작업을 조회·목록·처리별로 나누고, 각 작업의 fail-closed/캐시 허용 여부와 캐시 TTL/사용 조건을 정하세요.

**Low — API 지연 목표가 출시 전 결정으로 남아 있어 현재 PRD 기준으로는 NFR 검증이 불가능함**  
근거: Non-functional requirements와 Open decisions 모두 API 지연 목표가 내부 베타 후 결정된다고 합니다.  
영향: 현재 구현 범위에서는 성능 acceptance가 없습니다. 정식 출시 전 게이트가 별도 문서나 추적 항목 없이 빠질 수 있습니다.  
수정 방향: 지금 수치를 정하지 않더라도 “출시 전 latency SLO가 정의되어야 GA 불가” 같은 delivery gate를 추가하거나, 베타에서는 측정 instrumentation만 exit condition으로 두세요.

**Low — Delivery Phase 3가 FR-105만 묶어 원자성 검증과 어긋남**  
근거: FR-106은 상태와 감사 이벤트의 원자성을 요구하지만 Delivery에서는 Phase 2에 FR-106, Phase 3에 FR-105가 배치되어 있습니다.  
영향: Phase 2에서 상태 전이는 완성됐지만 감사 원자성은 나중으로 밀려, 중간 산출물이 핵심 P0 불변식을 만족하지 못할 수 있습니다.  
수정 방향: 감사 이벤트 원자성 검증은 FR-105/FR-106 교차 요구로 묶어 Phase 2 또는 Phase 3 exit condition에 함께 반영하세요.

검토는 제공된 PRD 원문만 기준으로 했고, 저장소 탐색이나 파일 생성은 하지 않았습니다.