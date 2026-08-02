**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 Empty/Loading/Error/Success/Recovery 열 정의 |
| Mermaid user or system flow | Present | 신청 → 검증 → PENDING → 취소/승인/반려 Mermaid flow 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | Missing | Delivery exit condition은 있으나 각 FR별 precondition/action/result 형태의 수용 기준은 없음 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3이 Requirement IDs와 exit condition에 매핑됨 |

**Findings**

**High — 중복 휴가 생성의 동시성 보장이 검증 불가능함**  
근거: `FR-101`은 `PENDING·APPROVED 신청과 겹칠 수 없다`고 하고, `FR-106`은 생성 명령도 idempotency key와 조건부 갱신을 사용한다고 하지만, 신규 생성에서 겹침 방지는 단순 조건부 갱신만으로 충분하지 않을 수 있습니다. 같은 직원이 같은 기간을 거의 동시에 제출하면 둘 다 “기존 겹침 없음”을 읽고 insert할 수 있습니다.  
영향: 핵심 불변식인 휴가 기간 중복 금지가 깨질 수 있고, 이후 승인/감사 이력도 모순됩니다.  
수정 방향: 생성 트랜잭션의 격리 수준, 직원+날짜 범위 잠금, exclusion constraint, 날짜별 점유 테이블, serializable retry 중 하나를 제품 요구로 명시하고, 동시 생성 테스트를 `FR-101/FR-106` 수용 기준에 넣어야 합니다.

**High — People Platform 실패/캐시 정책이 처리 요청에만 한정되어 권한 경계가 불완전함**  
근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고 하지만, `FR-103/FR-104`는 현재 팀장 관계가 조회·상세·처리 모두에 영향을 줍니다. 팀 승인함 조회와 상세 조회의 People Platform 실패 시 동작이 빠져 있습니다.  
영향: stale manager cache나 장애 시 fallback 정책에 따라 이전 팀장이 PENDING 신청을 계속 조회하거나 사유 전문을 볼 수 있습니다. 이는 권한 및 개인정보 문제입니다.  
수정 방향: 현재 팀장 관계가 필요한 모든 manager-scoped read/write에 대해 fail-closed 여부, 허용 캐시 TTL, 재검증 시점, 장애 응답을 명시하세요. 특히 `/team/leave`와 `/leave/:id` 팀장 조회에도 적용되어야 합니다.

**Medium — 권한 거부 감사 이벤트의 원자성·필드 규칙이 모호함**  
근거: `FR-105`는 권한 거부도 actor, request ID, 이전/이후 상태, timestamp로 기록한다고 합니다. 그러나 권한 거부는 요청 대상이 존재하지 않거나, 존재하더라도 actor에게 노출되면 안 되는 경우가 있습니다. `FR-106`의 원자성도 “상태와 감사 이벤트”에 초점이 있어 상태 변경이 없는 거부 이벤트에는 적용이 불명확합니다.  
영향: 감사 누락 또는 audit log를 통한 리소스 존재 여부 노출이 생길 수 있습니다.  
수정 방향: 거부 이벤트의 subject 식별자, 이전/이후 상태 값 처리 방식, 존재하지 않는/접근 불가 리소스의 redaction 규칙, 거부 감사 저장 실패 시 API 응답 정책을 별도 요구로 정의하세요.

**Medium — 감사자 권한의 범위와 개인정보 비식별 기준이 부족함**  
근거: 감사자는 “조직 내 감사 이벤트 읽기”가 가능하고 “휴가 사유 전문 읽기”는 금지됩니다. 하지만 감사 이벤트에 직원명, 팀, 날짜 범위, request ID, actor 정보가 포함되는지 여부는 정의되어 있지 않습니다.  
영향: 사유 전문이 없어도 날짜와 actor/대상 정보만으로 민감한 휴가 패턴이 노출될 수 있습니다.  
수정 방향: 감사자에게 필요한 최소 필드 목록, 마스킹/필터링 기준, 검색 조건, 보존 기간, 내보내기 가능 여부를 명시하세요.

**Medium — API 지연 목표가 출시 전 결정으로 남아 수용 검증이 불완전함**  
근거: `Non-functional requirements`와 `Assumptions and open decisions` 모두 API 지연 목표를 베타 후 결정한다고 둡니다.  
영향: 정식 출시 전까지 성능 수용 기준이 없어 Phase exit 또는 release readiness에서 합격/불합격을 판단하기 어렵습니다.  
수정 방향: 현재 PRD에서는 “베타 진입 기준”과 “정식 출시 차단 기준”을 분리하세요. 예: 베타에서는 측정 계측 필수, GA 전에는 p95/p99 목표 확정 및 테스트 통과 필수.

**Low — 상태 매트릭스가 일부 실제 화면을 덮지 않음**  
근거: Pages/routes에는 `팀 승인함`, `휴가 상세`, `감사 이력`이 있지만 State matrix는 `내 휴가`, `신청 폼`, `승인 상세`만 있습니다.  
영향: 팀 승인함의 빈 목록/403/People Platform 503, 감사 이력의 권한 오류/빈 결과/필터 오류 같은 화면 상태가 구현자별로 달라질 수 있습니다.  
수정 방향: 모든 route 또는 주요 surface별로 Empty/Loading/Error/Success/Recovery를 맞추거나, 의도적으로 공통 상태 정책을 적용한다고 명시하세요.

**Low — 반려 사유와 신청 사유의 표시·저장 권한이 비대칭으로 정의됨**  
근거: `FR-103`은 반려 사유 1~500자를 요구하지만, 누가 반려 사유를 읽을 수 있는지 `Risks and mitigations`에는 휴가 사유만 언급됩니다.  
영향: 반려 사유가 직원/팀장/감사자에게 어떻게 보이는지 불명확하고, 감사 이벤트에 포함 가능한지도 애매합니다.  
수정 방향: 반려 사유의 reader, audit 포함 여부, 로그 금지 여부를 신청 사유와 별도로 정의하세요.

**요약**

PRD는 권한, 상태 전이, 감사, 전달 단계의 큰 구조는 잘 잡혀 있습니다. 가장 먼저 보완할 부분은 `FR-101/FR-106`의 동시 생성 중복 방지 방식, People Platform 장애 시 모든 조회·처리 권한의 fail-closed 정책, 그리고 FR별 수용 기준의 precondition/action/result 매핑입니다.