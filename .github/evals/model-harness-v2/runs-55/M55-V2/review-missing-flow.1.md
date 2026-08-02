**계약 감사**

| Contract | Status | Applicability | Evidence |
|---|---:|---:|---|
| Applicability ledger | Present | Required | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 표시함 |
| Pages and routes | Present | Required | `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | Required | 내 휴가, 신청 폼, 승인 상세의 상태 매트릭스 정의 |
| Mermaid user or system flow | Missing | Required | PRD가 User flow를 Required로 표시했고 신청→처리→최종결정 생명주기가 있으나 Mermaid flow 없음 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | Required | AC-101~108이 FR ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Required | Phase 1~3이 FR ID와 검증 가능한 종료조건을 포함 |

**Findings**

**High — CANCELLED 전이에 대한 요구사항·검증이 부족함**

영향: 직원의 대기 취소가 권한, 상태, 감사, 멱등성, 동시성 측면에서 실제로 안전하게 구현됐는지 검증할 수 없습니다. 특히 `CANCELLED`가 상태로 존재하고 직원 권한에도 “대기 취소”가 있지만, 성공 취소 AC가 없습니다.

근거: `FR-102`는 `PENDING`에서 `CANCELLED` 전이를 허용하고, 역할 표는 직원의 “대기 취소”를 허용합니다. 그러나 AC는 승인, 반려, 동시 승인/취소 충돌만 다루며 “소유 직원이 본인 PENDING 신청을 취소하면 CANCELLED와 감사 이벤트가 남는다”를 직접 검증하지 않습니다. Delivery도 취소 성공 조건을 명시하지 않습니다.

수정 방향: 취소 성공 AC를 추가하세요. 예: 본인 직원 + PENDING 신청 + 유효 idempotency key → `CANCELLED`, 상태 불변성 보장, 감사 이벤트 1건. 타인 취소, 이미 최종 상태 취소 재시도, 승인과 취소 경합도 별도 기대 결과를 명확히 분리하는 편이 좋습니다.

**High — 거부 감사 이벤트가 보안 경계와 충돌할 수 있음**

영향: 권한 거부를 감사해야 한다는 요구는 좋지만, 타 조직 또는 접근 불가 신청에 대해 “request ID, 이전/이후 상태”를 기록하도록 하면 존재 여부나 상태를 감사 로그 또는 운영 경로로 노출할 수 있습니다. 또한 접근 불가 리소스의 이전 상태를 서버가 감사자에게 보여도 되는지 불명확합니다.

근거: `FR-105`는 “권한 거부를 actor, request ID, 이전/이후 상태, timestamp로 기록”한다고 합니다. `FR-104`와 Authorization은 조직·소유자·팀장 관계를 작업별로 검사한다고 하지만, 접근 불가 대상의 상태를 감사 이벤트에 어느 수준까지 남길지 제한하지 않습니다.

수정 방향: 거부 감사 이벤트 스키마를 성공 이벤트와 분리하세요. 예: `actor`, `attempted_action`, `tenant/org from session`, `resource_reference_hash or nullable request_id`, `decision=DENIED`, `reason_code`, `timestamp` 정도로 제한하고, 접근 권한 없는 리소스의 기존 상태·사유·소유자 정보는 기록/노출하지 않는다고 명시하세요.

**Medium — Mermaid user/system flow 계약 누락**

영향: 상태 전이, 팀 이동 후 처리자 변경, 승인/취소 경합, 감사 이벤트 원자성 같은 핵심 흐름이 산출물 수준에서 한눈에 검증되지 않습니다. 구현자는 개별 FR/AC를 조합해야 해서 누락 가능성이 커집니다.

근거: Applicability에서 User flow를 Required로 표시했지만 PRD 본문에는 Mermaid flow가 없습니다. review contract상 다단계 생명주기에는 Mermaid user or system flow가 적용됩니다.

수정 방향: 최소한 신청 생성→PENDING→직원 취소 또는 팀장 승인/반려→최종 상태, 그리고 팀 이동 시 “현재 팀장 재평가” 분기를 Mermaid flow로 추가하세요.

**Medium — 인사 시스템 실패 처리가 조회와 처리에 일관되게 검증되지 않음**

영향: People Platform 장애 시 접근 판단이 필요한 조회, 팀 승인함 목록, 상세, 처리 요청이 서로 다르게 동작할 수 있습니다. 특히 “처리 요청은 fail-closed 503”만 명시되어 조회 계열의 보안 동작이 불분명합니다.

근거: Authorization에는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고 되어 있습니다. 하지만 `FR-103`, `FR-104`, Pages/routes는 현재 팀장 관계에 따라 조회와 처리 모두를 제한합니다. AC에는 People Platform 장애 시 조회/목록/처리의 기대 결과가 없습니다.

수정 방향: People Platform 의존 작업을 구분해 실패 정책을 명시하세요. 예: 팀 승인함 목록과 팀장 상세 조회도 팀 관계 검증 실패 시 fail-closed 503인지, 직원 본인 조회는 People Platform 없이 가능한지. 해당 AC를 추가하세요.

**Medium — 반려 사유의 열람·보존·감사 범위가 불명확함**

영향: 반려 사유가 휴가 사유와 같은 민감정보 정책을 따르는지, 직원에게 표시되는지, 감사자에게 보이는지, 로그에서 제외되는지 구현마다 달라질 수 있습니다.

근거: `FR-103`은 반려 사유 1~500자를 요구합니다. `FR-105`와 Risks는 “휴가 사유 전문”을 감사 이벤트/로그에 넣지 않는다고 하지만 반려 사유는 언급하지 않습니다. 감사자 권한도 “휴가 사유 전문 읽기 금지”만 금지합니다.

수정 방향: 반려 사유의 데이터 분류를 명시하세요. 예: 직원 본인과 현재/처리 당시 팀장에게 표시, 감사 이벤트에는 전문 미포함, 감사자에게는 reason presence 또는 code만 제공 등.

**Low — API 지연 목표가 출시 전 결정으로 남아 있어 현재 PRD 기준 검증 불가**

영향: 성능 요구가 베타 이후로 유예되어 현재 산출물만으로는 출시 준비 여부를 판단할 수 없습니다. 다만 의도적으로 open decision으로 둔 항목이라 제품 리스크에 가깝습니다.

근거: Non-functional requirements와 Assumptions/Open decisions가 “내부 베타 종료일까지 제품 책임자가 결정”한다고 합니다.

수정 방향: 정식 출시 게이트에 “지연 목표 수치 확정 및 측정 기준 추가”를 exit condition으로 넣으세요. 지금 단계에서는 P0 구현 범위가 아니라면 Open decision으로 유지해도 됩니다.

검토는 사용자가 제공한 PRD 원문만 기준으로 했고, 요청대로 저장소 탐색·파일 생성은 하지 않았습니다.