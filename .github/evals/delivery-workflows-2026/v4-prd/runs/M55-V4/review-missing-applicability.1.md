**산출물 계약 감사**

| Contract | Status | 적용성 | Evidence |
|---|---|---:|---|
| Applicability ledger | Present | Applicable | `Context`, `Goals`, `Non-goals`, `Users, roles, and permissions`, `Assumptions and open decisions`, `Risks and mitigations`가 존재 |
| Pages and routes | Present | Applicable | user-visible 기능이며 `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | Applicable | `State matrix` 존재 |
| Mermaid user or system flow | Present | Applicable | 신청부터 취소·승인·반려까지 Mermaid flow 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | Applicable | `Acceptance criteria`가 `FR-*`와 Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Applicable | `Delivery`가 Phase별 Requirement IDs와 exit condition 포함 |

**Findings**

1. **High — 중복 휴가 생성의 동시성 보장이 검증되지 않음**
   - 근거: `FR-101`은 `PENDING·APPROVED 신청과 겹칠 수 없다`고 하지만, `FR-106`의 조건부 갱신은 “모든 생성·상태 명령”이라고만 되어 있고 실제 충돌 방지 방식은 불명확합니다. `AC-106`은 승인과 취소 동시 요청만 다루며, 같은 직원이 겹치는 기간을 동시에 신청하는 케이스가 없습니다.
   - 영향: 두 요청이 동시에 통과하면 겹치는 `PENDING` 휴가가 생성될 수 있습니다. 이는 핵심 도메인 불변식 위반입니다.
   - 수정 방향: 생성 경로에 대해 DB 레벨 exclusion/unique constraint, serializable transaction, advisory lock 등 하나를 명시하고, “동시 겹침 신청 중 하나만 성공, 다른 하나는 409, 성공 감사 이벤트만 1건” AC를 추가하세요.

2. **High — idempotency key의 보안·재사용 범위가 정의되지 않음**
   - 근거: `FR-106`, `AC-108`은 같은 idempotency key 재시도 시 같은 신청 ID를 반환한다고만 합니다. key가 actor, organization, operation, request body hash, TTL에 어떻게 묶이는지 없습니다.
   - 영향: 전역 key 충돌, 다른 본문으로 같은 key 재사용, 사용자 간 key 추측·재사용 시 잘못된 신청 ID 노출 또는 명령 오작동이 생길 수 있습니다.
   - 수정 방향: idempotency key를 `organization + actor + operation + key` 단위로 스코프하고, 최초 요청 본문 해시와 불일치하면 409/422를 반환하도록 정의하세요. TTL, 저장 실패 시 동작, 성공/실패 응답 재현 범위도 AC로 검증 가능하게 두는 편이 안전합니다.

3. **Medium — 취소 권한과 검증 기준이 불완전함**
   - 근거: 역할 표는 직원이 `본인 ... 대기 취소` 가능하다고 하지만 `FR-102`는 상태 전이만 말하고, `FR-104`는 작업별 권한 검사를 일반적으로만 언급합니다. `Pages and routes`의 `/leave/:id`는 “소유 직원, 현재 팀장”에게 `조회·취소·처리`를 묶어 보여 팀장이 취소할 수 있는지 애매합니다. `AC`에는 직원 취소 성공, 타인 취소 거부, 취소 감사 이벤트 검증이 없습니다.
   - 영향: 구현자가 팀장 취소를 허용하거나, 취소 감사/권한 검사를 누락해도 현재 AC로는 잡히지 않습니다.
   - 수정 방향: “취소는 소유 직원만, PENDING에서만 가능”처럼 actor별 전이를 명시하고, 직원 취소 성공 및 비소유자/팀장 취소 거부 AC를 추가하세요.

4. **Medium — People Platform 장애 시 조회·목록 권한 동작이 불명확함**
   - 근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고 합니다. 하지만 `FR-104`와 routes는 현재 팀장 관계로 조회·상세·승인함 접근을 제어해야 하며, 장애 시 읽기 요청이 fail-closed인지 캐시 허용인지 정의가 없습니다.
   - 영향: 장애 중 이전 팀장이 계속 접근하거나, 반대로 승인함 전체가 예측 불가능하게 동작할 수 있습니다. 보안 경계가 People Platform의 가용성에 걸려 있는데 읽기 정책이 빠져 있습니다.
   - 수정 방향: 팀장 권한이 필요한 모든 읽기·쓰기 요청에 대해 People Platform 실패 시 정책을 명시하세요. 캐시를 허용한다면 freshness, stale 허용 범위, 이동 직후 접근 차단 조건을 함께 정의해야 합니다.

5. **Medium — 감사자 범위와 권한 거부 감사 이벤트의 정보 노출 경계가 부족함**
   - 근거: 감사자는 `조직 내 감사 이벤트 읽기` 가능하고 `휴가 사유 전문`은 금지됩니다. `FR-105`는 권한 거부도 `actor, request ID, 이전/이후 상태`로 기록한다고 합니다. 그러나 권한 거부 상황에서 존재하지 않거나 접근 불가한 request의 현재 상태를 감사 이벤트에 기록해도 되는지, 감사자가 어떤 조직/범위의 actor·request ID를 볼 수 있는지 세부 기준이 없습니다.
   - 영향: IDOR 시도나 타 팀 접근 거부 이벤트가 request 존재 여부, 상태, 소유 관계를 간접 노출할 수 있습니다. 감사 화면이 조직 전체라면 최소권한 원칙도 애매합니다.
   - 수정 방향: 권한 거부 이벤트는 접근 불가 대상의 민감 상태를 기록하지 않거나 별도 redaction 규칙을 두세요. 감사자 조회 범위, 필드 마스킹, 이벤트 타입/결과/거부 사유 코드, request ID 노출 정책을 AC로 검증 가능하게 정의하는 것이 좋습니다.

**검증 불가능 항목**

`Non-functional requirements`의 “API 지연 목표는 내부 베타 측정 후 제품 책임자가 정식 출시 전에 결정”은 현재 PRD 기준으로는 합격/불합격을 판정할 수 없습니다. 출시 전 결정이 요구사항이라면 “베타 종료일까지 p95/p99 목표가 문서화되어야 한다”처럼 산출물 기준으로 두거나, 지금은 open decision으로만 유지하는 편이 맞습니다.