**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 Empty/Loading/Error/Success/Recovery 정의 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid flowchart 포함 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `Acceptance criteria`가 AC별 Requirement, Given, When, Then, Verification 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery`가 Phase별 Requirement IDs와 exit condition 포함 |

**Findings**

**High - 상태 명령 멱등성 검증이 불완전함**

- 영향도: `FR-106`은 “모든 생성·상태 명령”에 idempotency key를 요구하지만, `AC-108`은 신청 재시도만 검증합니다. 승인, 반려, 취소 재시도에서 중복 감사 이벤트, 중복 응답, 409 오판정이 발생해도 AC로 잡히지 않습니다.
- 근거: `FR-106`, `AC-108`
- 수정 방향: 승인·반려·취소 각각에 대해 동일 idempotency key 재시도 시 동일 결과를 반환하고 감사 이벤트가 중복되지 않는 AC를 추가하세요. 실패 후 재시도, payload 불일치 재사용도 정의해야 합니다.

**High - idempotency key의 보안·격리 스코프가 정의되지 않음**

- 영향도: 같은 key가 조직, actor, route, command type, request body에 바인딩되지 않으면 다른 사용자의 요청 재사용, 교차 조직 충돌, 승인 key로 반려 요청을 덮는 문제가 생길 수 있습니다.
- 근거: `FR-106`은 idempotency key 사용만 명시하고 scope, uniqueness, payload hash, retention을 정의하지 않음
- 수정 방향: key 저장 단위를 `organization + actor + command type + target/resource + idempotency key`로 제한하고, 동일 key에 다른 payload가 오면 409 또는 422로 거부하도록 명시하세요. 보관 기간도 필요합니다.

**Medium - 취소 기능의 acceptance coverage가 없음**

- 영향도: 직원의 `PENDING` 취소는 권한·상태 전이의 핵심 동작인데 성공/실패 AC가 없습니다. 본인만 취소 가능한지, 승인 후 취소가 409인지, 취소 감사 이벤트가 남는지 검증이 비어 있습니다.
- 근거: 직원 권한 표, `FR-102`, `FR-105`, user flow에는 취소가 있으나 AC에는 취소 단독 케이스가 없음
- 수정 방향: “소유 직원이 PENDING 신청 취소”, “타인 취소 시 403”, “APPROVED/REJECTED/CANCELLED 취소 시 409” AC를 추가하세요.

**Medium - 감사 이벤트 실패/거부 범위가 모호함**

- 영향도: `FR-105`는 “권한 거부”를 감사한다고 하지만, 409 충돌, 유효성 실패, People Platform 503, stale-state 실패는 감사 대상인지 불명확합니다. `AC-102`는 충돌 시 성공 감사 이벤트 없음만 말해 감사 이벤트 자체의 유무가 애매합니다.
- 근거: `FR-105`, `AC-102`, Authorization fail-closed 503 문장
- 수정 방향: 감사 대상 실패 유형을 명확히 나누세요. 예: 권한 거부 403은 감사, 상태 충돌 409는 선택, 입력 검증 400/422은 미기록, 외부 의존성 503은 보안 이벤트만 기록 여부 등.

**Medium - 현재 팀장 조회 권한과 과거 결정 이력의 경계가 불명확함**

- 영향도: 직원 이동 후 “새 팀장이 PENDING 신청을 처리”한다는 규칙은 명확하지만, 최종 처리된 과거 신청의 상세 조회 권한이 현재 팀장에게 계속 있는지, 처리 당시 팀장에게 남는지 불명확합니다. 휴가 사유는 민감 정보라 조회 경계가 제품·보안 요구사항입니다.
- 근거: `/leave/:id` allowed roles는 “소유 직원, 현재 팀장”, `FR-104`는 PENDING 처리와 이전 팀장 접근 상실을 언급, Risks는 “휴가 사유는 직원 본인과 현재 팀장만 읽음”
- 수정 방향: PENDING과 final 상태별 상세 조회자를 분리하세요. 특히 사유 전문을 현재 팀장에게 항상 노출할지, 처리 당시 팀장에게 감사 목적 조회를 허용할지 결정해야 합니다.

**Medium - 외부 인사 시스템 조회의 일관성 기준이 부족함**

- 영향도: 승인 시점의 현재 팀을 People Platform에서 확인한다고 되어 있으나, 조회 결과의 freshness, 캐시 허용 여부, 타임아웃, 재시도, 동일 요청 내 TOCTOU 방지가 정의되지 않았습니다. 팀 이동 직후 승인 경쟁에서 구현별 결과가 달라질 수 있습니다.
- 근거: `FR-103`, `FR-104`, Authorization and data boundaries, Assumptions
- 수정 방향: 처리 명령마다 authoritative read를 수행할지, 캐시 TTL을 금지/허용할지, 확인한 membership version 또는 timestamp를 감사 이벤트에 남길지 정의하세요.

**Low - API 지연 목표가 검증 가능한 NFR이 아님**

- 영향도: “출시 전에 결정”은 open decision으로는 괜찮지만 현재 PRD의 NFR로는 테스트하거나 릴리스 게이트로 사용할 수 없습니다.
- 근거: Non-functional requirements, Assumptions and open decisions
- 수정 방향: 지금은 open decision으로만 유지하고, Delivery exit condition에는 포함하지 않는다고 명시하거나 베타 종료 전 결정 기준과 측정 위치를 추가하세요.

**Low - 날짜 경계 조건이 일부 빠져 있음**

- 영향도: KST 달력일, inclusive range는 정의됐지만 과거일 신청 가능 여부, 최소/최대 기간, 공휴일·주말 포함 여부, 종료일 장기 미래 제한이 없습니다. “일 단위 휴가” 정책 해석이 구현마다 달라질 수 있습니다.
- 근거: `FR-101`, Non-goals
- 수정 방향: 과거일 허용 여부와 주말/공휴일 포함 계산 여부만이라도 명시하세요. 반차·시간차는 non-goal로 이미 잘 제외되어 있습니다.

**종합**

구조 계약은 모두 존재하고 적용성 판단도 타당합니다. 핵심 제품 모델도 비교적 잘 닫혀 있지만, 구현 리스크는 `FR-106`의 상태 명령 멱등성, idempotency key 격리, 취소 AC 누락, 민감 사유 조회 경계에서 큽니다. 이 네 가지를 보강하면 구현·테스트 가능한 PRD로 훨씬 단단해집니다.