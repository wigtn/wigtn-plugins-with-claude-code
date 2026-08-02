**프로젝트 산출물 계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow의 Required 여부와 근거를 명시함 |
| Pages and routes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 Empty/Loading/Error/Success/Recovery 정의 |
| Mermaid user or system flow | Missing | `Applicability`에서 User flow가 Required이나 Mermaid 또는 동등한 명시적 흐름 다이어그램 없음 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~AC-108이 FR ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3이 FR ID와 exit condition을 포함 |

**Findings**

`High` Mermaid user/system flow 계약 누락  
영향: 신청 생성, 팀 이동, 승인/반려/취소, 감사 이벤트, 동시성 실패 경로가 다단계 생명주기인데 흐름 산출물이 없어 구현자가 상태 전이와 권한 재평가 시점을 다르게 해석할 수 있습니다.  
근거: `Applicability`에서 User flow를 Required로 선언했지만, 실제 문서에는 Mermaid flow가 없습니다.  
수정 방향: Mermaid flow로 최소한 `직원 신청 -> PENDING -> 팀장 승인/반려 또는 직원 취소 -> 최종 상태`, `팀 이동 후 현재 팀장 재평가`, `권한 거부 감사`, `동시 요청 409` 경로를 표시해야 합니다.

`High` 직원 취소 기능은 요구사항에 있지만 검증 기준이 없음  
영향: `CANCELLED` 상태와 “대기 취소” 권한이 구현 누락되어도 AC 통과가 가능합니다. 특히 취소는 승인과 경쟁하는 상태 명령이라 FR-106의 조건부 갱신·감사 원자성 검증 대상이어야 합니다.  
근거: 역할 표는 직원에게 `대기 취소`를 허용하고, FR-102는 `PENDING -> CANCELLED`를 허용하며, Pages는 상세에서 `취소`를 언급합니다. 그러나 AC-101~AC-108 중 직원 단독 취소 성공/실패 기준이 없습니다.  
수정 방향: 소유 직원이 본인 `PENDING` 신청을 취소하면 `CANCELLED`와 감사 이벤트 1건이 생기는 AC, 이미 `APPROVED/REJECTED/CANCELLED`인 신청 취소 시 409가 나는 AC를 추가해야 합니다.

`High` idempotency key의 보안 스코프와 재사용 규칙이 불명확함  
영향: 같은 key가 actor, 조직, endpoint, request payload, target request ID에 바인딩되지 않으면 다른 사용자의 요청 결과를 재사용하거나, 다른 명령이 같은 결과를 돌려받는 보안·정합성 문제가 생길 수 있습니다.  
근거: FR-106은 “모든 생성·상태 명령은 idempotency key”를 요구하지만, AC-108은 신청 재시도만 검증합니다. 상태 명령 승인/반려/취소의 key 재시도, payload mismatch, actor mismatch 규칙은 없습니다.  
수정 방향: key는 최소 `organization + actor + command type + target/request payload hash`에 스코프된다고 명시하고, 같은 key 다른 payload는 409 또는 422, 다른 actor 재사용은 403/404 계열로 검증해야 합니다.

`Medium` 권한 거부 감사 이벤트 스키마가 개인정보·정보노출 측면에서 애매함  
영향: 권한 거부 이벤트에 `request ID`, 이전/이후 상태를 항상 기록하면, 접근 권한이 없는 사용자가 존재하는 신청 ID나 상태를 추론하게 만들 수 있습니다. 반대로 이를 기록하지 않으면 FR-105와 충돌합니다.  
근거: FR-105는 “생성·승인·반려·취소와 권한 거부를 actor, request ID, 이전/이후 상태, timestamp로 기록”한다고 합니다. 하지만 감사자는 사유 전문을 읽을 수 없고, 서버는 조직·소유자·팀장 관계를 검사해야 합니다. 권한 거부 시 노출 가능한 필드가 별도 정의되지 않았습니다.  
수정 방향: 거부 감사 이벤트는 `target_request_id` 기록 가능 조건, 상태 필드가 `unknown/null/redacted`가 되는 조건, 감사자 조회 시 마스킹 규칙을 분리해 명시해야 합니다.

`Medium` 감사 이력 조회 자체의 수용 기준이 없음  
영향: 감사자 권한, 조직 경계, 사유 전문 미노출, 권한 거부 이벤트 조회 가능 여부가 구현되어야 하는 핵심 보안 기능인데 AC로 검증되지 않습니다.  
근거: 역할 표에 감사자 권한이 있고 `/audit/leave` 경로도 있으나, AC-101~AC-108은 상태 변경 감사 생성만 다룹니다. 감사자 조회, 직원/팀장의 감사 조회 금지, 사유 redaction 검증이 없습니다.  
수정 방향: 감사자가 조직 내 이벤트를 조회할 수 있고 사유 전문은 보이지 않는 AC, 타 역할의 감사 조회가 거부되는 AC, 조직 간 감사 이벤트 격리 AC를 추가해야 합니다.

`Medium` People Platform 실패 처리 범위가 처리 요청에만 한정됨  
영향: 직원 이동 후 접근권한을 현재 팀 기준으로 판단하려면 상세 조회와 팀 승인함 조회도 People Platform 의존성이 있습니다. 처리 요청만 503 fail-closed로 정의하면 조회에서 stale 권한을 허용하거나 모호한 에러가 날 수 있습니다.  
근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고만 합니다. FR-104는 작업별로 현재 팀을 검사하고, Pages는 상세·팀 승인함 조회를 포함합니다.  
수정 방향: 생성, 상세 조회, 팀 승인함 조회, 승인/반려 각각에서 People Platform 장애 시 동작을 정의해야 합니다. 권한 판단이 필요한 조회도 fail-closed인지, 캐시 허용 여부가 있는지 명시가 필요합니다.

`Low` 반려 사유와 휴가 사유의 저장·노출 경계가 다르게 정의되지 않음  
영향: 휴가 사유는 민감정보로 로그·감사 제외가 명시되어 있지만, 반려 사유는 1~500자만 있고 누가 읽을 수 있는지, 감사 이벤트에 포함되는지 불명확합니다.  
근거: FR-101은 휴가 사유, FR-103은 반려 사유를 정의합니다. FR-105와 Risks는 “휴가 사유 전문”만 제외한다고 되어 있습니다.  
수정 방향: 반려 사유도 감사 이벤트 전문 제외 대상인지, 직원/팀장/감사자별 조회 가능 범위를 명시해야 합니다.

**요약**

PRD는 권한·상태·감사·동시성의 핵심 방향은 꽤 잘 잡혀 있습니다. 다만 계약상 Mermaid flow가 누락되어 있고, 실제 구현 리스크는 `취소 AC 누락`, `idempotency 스코프 불명확`, `감사 조회·redaction 검증 부재`, `People Platform 장애 범위 모호함`에 집중됩니다.