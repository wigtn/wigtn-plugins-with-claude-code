**프로젝트 산출물 계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표에서 Pages/routes, State matrix, User flow를 Required로 선언 |
| Pages and routes | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 Empty/Loading/Error/Success/Recovery 열 정의 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid 신청-검증-결정 흐름 포함 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `Acceptance criteria`가 ID, Requirement, Given/When/Then/Verification 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery` 표가 Phase별 Requirement IDs와 exit condition 포함 |

**Findings**

**High: 팀장 본인 신청의 처리 주체가 정의되지 않아 핵심 플로우가 막힙니다.**  
영향도: 팀장도 직원이라면 본인 휴가를 신청할 수 있지만, 현재 PRD는 “본인 신청 처리 금지”만 있고 대체 승인자를 정의하지 않습니다. 이 경우 팀장의 PENDING 신청은 승인·반려될 수 없는 상태로 남을 수 있습니다.  
근거: `Users, roles, and permissions`의 팀장 Forbidden, `FR-103`, `AC-105`.  
수정 방향: 팀장 본인 신청은 상위 관리자, 위임 승인자, HR 관리자 등 누가 처리하는지 명시하고 해당 역할·권한·라우트·AC를 추가해야 합니다. 또는 팀장은 본인 신청 생성 불가라고 명시해야 하나, 일반 휴가 도메인에서는 부자연스럽습니다.

**High: idempotency key의 보안·정합성 범위가 불명확합니다.**  
영향도: 키가 조직, actor, 명령 종류, payload hash에 묶이지 않으면 다른 사용자/요청 간 충돌, 재사용, payload 변경 재시도에서 잘못된 기존 결과 반환이 발생할 수 있습니다.  
근거: `FR-106`, `AC-108`은 idempotency key 사용과 중복 이벤트 방지만 말하고 scope, TTL, payload mismatch 동작을 정의하지 않습니다.  
수정 방향: idempotency key는 최소 `org + actor + operation + key` 단위로 유일해야 하며, 최초 payload hash와 다르면 409 또는 422를 반환하도록 정의하세요. 보관 기간과 성공/실패 재시도 재현 정책도 AC에 포함하는 편이 좋습니다.

**Medium: 권한 거부 감사 이벤트가 정보 노출과 충돌할 수 있습니다.**  
영향도: 권한 없는 사용자가 존재하지 않는 신청 ID와 존재하지만 접근 불가한 신청 ID를 반복 조회·처리할 때, 감사 이벤트의 `request ID` 기록 방식이 신청 존재 여부를 내부 감사 로그에 과도하게 남기거나 운영자에게 사유 전문 외 민감 맥락을 노출할 수 있습니다.  
근거: `FR-105`는 권한 거부를 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 하나, 존재하지 않거나 타 조직 리소스인 경우의 request ID/상태 기록 정책이 없습니다. `Authorization and data boundaries`는 조직 ID를 세션에서 결정한다고만 합니다.  
수정 방향: 거부 감사 이벤트의 필드를 별도 정의하세요. 예: resolved request가 없거나 타 조직이면 내부 상관 ID와 denial reason category만 기록하고, 이전/이후 상태는 null 처리. 클라이언트 응답도 403/404 구분 정책을 정해야 합니다.

**Medium: 조회 권한의 시간 기준이 모호합니다.**  
영향도: 직원 이동 후 최종 처리된 과거 신청을 누가 볼 수 있는지 구현마다 달라질 수 있습니다. “현재 팀장” 기준을 모든 상세 조회에 적용하면 이전 팀장은 과거 자신이 승인한 건을 볼 수 없고, 새 팀장은 이전 팀에서 발생한 과거 사유를 볼 수 있습니다. 둘 중 어느 쪽이 제품 의도인지 불명확합니다.  
근거: `/leave/:id` Allowed roles는 “소유 직원, 현재 팀장”, `FR-104`는 직원 이동 후 새 팀장이 PENDING 신청을 처리하고 이전 팀장은 접근을 잃는다고 합니다. 하지만 APPROVED/REJECTED/CANCELLED 상세 조회의 권한 기준은 별도 정의가 없습니다.  
수정 방향: PENDING 처리 권한과 과거 상세 조회 권한을 분리하세요. 예: PENDING은 현재 팀장, 최종 상태는 처리 당시 팀장 또는 현재 팀장 중 어느 기준인지 명시해야 합니다.

**Medium: 감사자 화면의 상태 매트릭스가 누락되어 UI 계약이 부분적입니다.**  
영향도: `/audit/leave`가 페이지로 정의되어 있지만 Empty/Loading/Error/Success/Recovery 상태가 없어 감사 이력 조회의 실패, 빈 결과, 권한 오류, 필터 오류 처리가 검증 불가능합니다.  
근거: `Pages and routes`에는 `감사 이력`이 있지만 `State matrix`에는 `내 휴가`, `신청 폼`, `승인 상세`만 있습니다.  
수정 방향: 감사 이력 surface를 state matrix에 추가하고, 감사자가 사유 전문을 볼 수 없는 상태/표시 정책도 포함하세요.

**Low: 휴가 일수 계산에서 공휴일·주말·타임존 경계가 의도적으로 빠졌는지 불명확합니다.**  
영향도: “KST 달력일”과 “일 단위”는 좋지만, 주말·공휴일 포함 여부가 없으면 승인함과 중복 검사는 구현 가능해도 사용자 기대와 운영 정책이 어긋날 수 있습니다.  
근거: `FR-101`, `Non-goals`에는 반차·시간차만 제외되어 있고 휴일/근무일 정책은 없습니다.  
수정 방향: MVP에서 모든 KST 날짜를 휴가일로 취급하는지, 근무일 캘린더 기준인지 명시하세요. 급여 연동이 non-goal이어도 신청 가능일 검증 정책은 제품 동작입니다.

**검증 불가능성 요약**

대부분의 핵심 FR은 AC와 잘 연결되어 있습니다. 다만 위 항목 중 `idempotency payload mismatch`, `팀장 본인 신청 처리 주체`, `최종 상태 상세 조회 권한`, `감사 이력 화면 상태`는 현재 AC로는 합격/불합격 판정이 어렵습니다.

Validator는 실행하지 않았습니다. 사용자가 원문만 제공했고 “파일을 만들거나 저장소를 탐색하지 말라”고 했기 때문에 저장된 PRD 경로 기준 검증은 적용하지 않았습니다.