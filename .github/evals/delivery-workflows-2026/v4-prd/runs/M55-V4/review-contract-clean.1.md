**산출물 계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix` 표에 Empty/Loading/Error/Success/Recovery 정의 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid lifecycle flow 포함 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `Acceptance criteria`가 AC별 Requirement, Given, When, Then, Verification을 가짐 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery` 표가 Phase별 Requirement IDs와 exit condition을 가짐 |

**Findings**

**High — 겹침 방지의 동시성 계약이 부족해 중복 승인 가능한 신청이 생길 수 있음**  
근거: `FR-101`은 `PENDING·APPROVED 신청과 겹칠 수 없다`고 하지만, `FR-106`의 조건부 갱신은 주로 상태 명령에 적용되는 표현이고, 생성 시 겹치는 기간을 동시에 제출하는 race를 어떻게 원자적으로 막는지 불명확합니다. `AC-102`도 기존 충돌만 검증하고 동시 생성 충돌은 검증하지 않습니다.  
영향: 두 요청이 동시에 유효성 검사를 통과하면 같은 직원의 겹치는 `PENDING` 신청이 생성될 수 있어 핵심 도메인 불변식이 깨집니다.  
수정 방향: 생성도 같은 트랜잭션 안에서 직원·조직·KST 날짜 범위 기준의 충돌 검사를 잠금/제약/serializable transaction 등으로 보장한다고 명시하고, “동시 겹침 신청 중 하나만 성공, 다른 하나는 409, 감사 이벤트 중복 없음” AC를 추가하세요.

**High — 상태 명령 멱등성 검증이 신청 생성에만 치우쳐 있음**  
근거: `FR-106`은 “모든 생성·상태 명령”에 idempotency key를 요구하지만, `AC-108`은 신청 생성 재시도만 다룹니다. 승인, 반려, 취소의 동일 key 재시도, 같은 key로 다른 payload 재사용, 이미 완료된 상태 명령 재전송 결과가 검증되지 않습니다.  
영향: 네트워크 재시도나 중복 클릭에서 승인/반려/취소 이벤트가 중복 기록되거나, 같은 key가 다른 작업에 재사용되어 상태·감사 이력이 오염될 수 있습니다.  
수정 방향: 상태 명령별 멱등성 AC를 추가하세요. 동일 actor+command+key+payload는 동일 결과를 반환하고 감사 이벤트를 중복 생성하지 않으며, 같은 key의 다른 payload 또는 다른 command 재사용은 409/422 등으로 거부한다고 정해야 합니다.

**Medium — 취소 기능의 권한·감사·검증 계약이 불완전함**  
근거: `Users, roles`에는 직원의 `대기 취소`가 있고 `FR-102`에도 `CANCELLED`가 있지만, 기능 요구사항에는 취소 명령의 서버 검사 조건이 명시적으로 분리되어 있지 않습니다. `FR-105`는 취소 감사 기록을 요구하지만 Acceptance criteria에는 취소 성공, 타인 취소 금지, 취소 감사 이벤트, 취소 멱등성 검증이 없습니다.  
영향: 구현자가 취소를 목록 UI 동작 정도로 해석하거나, 승인/반려와 다른 권한·감사 경로로 구현할 수 있습니다. 특히 직원 본인만 `PENDING`을 취소할 수 있다는 서버 보장이 테스트로 잠기지 않습니다.  
수정 방향: `직원 본인 + 같은 조직 + PENDING`일 때만 취소 가능하다는 요구사항과 AC를 추가하고, 성공 시 `CANCELLED` 및 감사 이벤트 1건, 타인/최종 상태 취소 시 403 또는 409와 상태 불변을 검증하세요.

**Medium — 감사자 데이터 경계가 조회 결과 수준에서 충분히 검증 가능하지 않음**  
근거: `감사자`는 “휴가 사유 전문 읽기”가 금지되고 `FR-105`는 감사 이벤트에 휴가 사유 전문을 기록하지 않는다고 합니다. 하지만 `/audit/leave`의 응답 필드, 사유 요약/부분 마스킹 허용 여부, request ID를 통한 상세 API 접근 차단 여부는 acceptance에서 검증되지 않습니다.  
영향: 감사 이력 화면이나 API가 원문 사유, 과도한 사유 파생 정보, 또는 상세 링크를 통해 사유를 노출해도 현재 AC로는 실패를 잡기 어렵습니다.  
수정 방향: 감사 이벤트 조회 AC에 “reason 원문 및 파생 전문 없음, 감사자는 `/leave/:id` 사유 본문 접근 불가, 필요한 최소 식별자만 노출”을 검증 항목으로 추가하세요.

**Medium — 인사 시스템 장애의 사용자 흐름과 API 결과가 처리 명령에만 정의되어 있음**  
근거: `Authorization and data boundaries`는 People Platform 실패 시 “처리 요청은 fail-closed 503”이라고 하지만, 팀 승인함 조회, 상세 조회, 직원 이동 후 접근 판단, 생성 시 현재 조직/팀 확인이 필요한 경우의 실패 처리는 명확하지 않습니다. `State matrix`에도 승인 상세의 일시 오류는 있으나 팀 승인함/감사 이력/내 휴가의 외부 의존 실패 복구는 구체적이지 않습니다.  
영향: People Platform 장애 시 일부 경로는 stale 권한으로 열리거나, 어떤 경로는 500/빈 목록으로 처리되는 등 보안·UX가 불일치할 수 있습니다.  
수정 방향: People Platform 의존 작업을 조회/처리/생성별로 나누고, 권한 판단에 실패한 경우 fail-closed 상태 코드와 UI recovery를 명시하세요. 특히 팀장 조회와 상세 접근은 503 또는 접근 불가로 통일하는지 정해야 합니다.

**검증 메모**

저장소 탐색, 파일 생성, 원문 재작성은 하지 않았고 제공된 PRD 텍스트만 기준으로 검토했습니다. Validator는 실행하지 않았습니다.