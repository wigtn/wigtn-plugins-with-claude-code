**계약 감사**

| Contract | 적용성 | Status | Evidence |
|---|---:|---|---|
| Applicability ledger | 적용 | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정 |
| Pages and routes | 적용 | Present | `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | 적용 | Missing | Applicability에서 Required라고 했지만 실제 상태 매트릭스는 없음 |
| Mermaid user or system flow | 적용 | Present | 신청 → 검증 → PENDING → CANCELLED/APPROVED/REJECTED Mermaid flow 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | 적용 | Present | AC-101~AC-108이 FR ID, Given/When/Then/Verification 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | 적용 | Present | Phase 1~3이 FR ID와 exit condition 포함 |

**Findings**

**High — 상태 매트릭스 계약이 누락됨**

영향도: 사용자 가시 상태가 있는 기능인데 empty/loading/error/success/recovery 상태가 정의되지 않아 프론트엔드 구현과 QA 기준이 갈라질 수 있습니다. 특히 인사 시스템 503, 409 충돌, 403 권한 거부, 신청 성공 후 목록 반영, 감사 이력 조회 실패 상태가 검증 불가능합니다.

근거: `Applicability`에서 `State matrix`를 Required로 선언했지만 별도 상태 매트릭스가 없습니다. `Authorization and data boundaries`와 NFR에는 실패 조건이 일부 있으나 화면별 상태 계약은 아닙니다.

수정 방향: 페이지별로 최소 `empty / loading / success / validation error / authorization error / conflict / dependency failure / retry or recovery` 상태를 표로 추가하세요.

**High — 직원 취소 흐름의 AC가 없음**

영향도: `CANCELLED` 전이가 핵심 상태 생명주기에 포함되어 있지만, 취소 권한·감사 이벤트·동시성·멱등성 검증이 빠져 실제 구현에서 누락되어도 PRD상 통과할 수 있습니다.

근거: `FR-102`는 PENDING에서 CANCELLED 전이를 허용하고, `FR-105`는 취소 감사 기록을 요구합니다. 역할 표도 직원의 `대기 취소`를 허용합니다. 하지만 `AC-101~AC-108`에는 직원 취소 성공, 비소유자 취소 거부, PENDING이 아닌 신청 취소 거부가 없습니다.

수정 방향: 직원 본인 PENDING 취소 성공 AC, APPROVED/REJECTED/CANCELLED 취소 시 409 또는 422 AC, 타인 취소 403 및 권한 거부 감사 AC를 추가하세요.

**High — 권한 거부 감사 이벤트가 테넌트/정보 노출 측면에서 불명확함**

영향도: 권한 거부 이벤트에 `request ID`, `이전/이후 상태`를 기록하라고 되어 있어, 다른 조직 또는 접근 불가 신청에 대한 존재 여부와 상태가 감사 로그를 통해 노출될 수 있습니다. 거부 이벤트를 어느 조직 감사 로그에 귀속할지도 불명확합니다.

근거: `FR-105`는 권한 거부를 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 합니다. `Authorization and data boundaries`는 조직 ID를 세션에서 결정한다고 하지만, 권한 거부 이벤트의 조직 귀속과 민감 필드 마스킹 규칙은 없습니다.

수정 방향: 거부 이벤트는 세션 조직에 귀속할지, 대상 리소스 조직에 귀속할지 명시하세요. 접근 불가 리소스의 상태·소유자·사유·팀 정보는 기록하지 않거나 `unknown/redacted`로 기록하는 규칙을 분리하는 편이 안전합니다.

**Medium — 팀 이동 후 최종 상태 신청의 조회 권한이 모호함**

영향도: 직원 이동 후 이전 팀장이 접근을 잃는다는 규칙은 PENDING 처리에는 명확하지만, 이미 APPROVED/REJECTED/CANCELLED된 상세 조회나 감사/이력 조회 권한까지 동일하게 적용되는지 불분명합니다. 구현에 따라 이전 팀장이 과거 신청 사유를 계속 볼 수도, 새 팀장이 과거 사유까지 볼 수도 있습니다.

근거: `FR-104`는 “직원 이동 후에는 새 팀장이 PENDING 신청을 처리하고 이전 팀장은 접근을 잃는다”고 합니다. `Pages and routes`의 `/leave/:id`는 “소유 직원, 현재 팀장” 접근입니다. `Risks`는 휴가 사유를 “직원 본인과 현재 팀장만 읽음”이라고 합니다.

수정 방향: 팀장 상세 조회 권한을 `현재 팀의 모든 상태`인지, `현재 팀의 PENDING만`인지, `처리 당시 팀장에게 제한된 과거 결정 조회`인지 명시하세요. 휴가 사유 전문 접근도 같은 기준으로 고정해야 합니다.

**Medium — 멱등성 키 범위와 응답 재현 규칙이 검증 불가능함**

영향도: 같은 idempotency key가 사용자/조직/엔드포인트/요청 본문 중 어디에 묶이는지 없어서 중복 생성 방지, 재시도, 악의적 키 재사용 처리 방식이 달라질 수 있습니다.

근거: `FR-106`은 모든 생성·상태 명령이 idempotency key를 사용한다고만 합니다. `AC-108`은 신청 재시도만 다루며 승인·반려·취소의 멱등성은 검증하지 않습니다.

수정 방향: 키 범위를 `actor + organization + command type + key` 등으로 정의하고, 같은 키에 다른 payload가 오면 409를 반환하는지 명시하세요. 승인·반려·취소 재시도 AC도 추가하세요.

**Medium — 반려 사유와 신청 사유의 읽기/저장 경계가 비대칭임**

영향도: 휴가 사유 전문은 감사 로그에 넣지 않는다고 명시되어 있지만, 반려 사유의 감사 로그 포함 여부와 감사자 열람 가능 여부가 없습니다. 반려 사유도 개인정보나 민감한 평가 문구를 포함할 수 있습니다.

근거: `FR-101`은 신청 사유, `FR-103`은 반려 사유를 요구합니다. `FR-105`는 “휴가 사유 전문은 기록하지 않는다”고만 하며 반려 사유는 언급하지 않습니다. 감사자는 “휴가 사유 전문” 읽기가 금지되어 있습니다.

수정 방향: 감사 이벤트에서 신청 사유와 반려 사유 모두 제외 또는 요약/코드화할지 명시하세요. 감사자에게 반려 사유 전문 열람을 허용할지도 별도 규칙으로 두세요.

**Low — API 지연 목표가 출시 전 결정으로 남아 있어 NFR로는 약함**

영향도: 현재는 성능 요구사항이 측정·검증 가능한 계약이 아니라 출시 전 미결정 항목입니다.

근거: `Non-functional requirements`와 `Assumptions and open decisions`에 “내부 베타 종료일까지 제품 책임자가 결정”이라고 되어 있습니다.

수정 방향: 지금은 open decision으로 두는 것은 가능하지만, 출시 승인 기준에는 `p95`, 대상 API, 측정 환경, 기간을 포함한 구체 값이 필요합니다.