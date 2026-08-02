**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 표시함 |
| Pages and routes | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix` 표 존재 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid 상태 흐름 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~AC-108이 FR ID와 Given/When/Then/Verification을 매핑 |
| Delivery phases mapped to requirement IDs and exit conditions | Missing | 단계별 출시/구현 phase, 각 phase의 요구사항 ID, exit condition이 없음 |

**Findings**

1. **Medium - Delivery phase 계약이 누락되어 구현·릴리스 검증 경계가 불명확함**  
   근거: 계약 감사상 `Delivery phases mapped to requirement IDs and exit conditions`가 없음. 이 PRD는 권한, 감사, 동시성, 외부 People Platform 의존성이 모두 P0라서 한 번에 출시 가능한지, 어떤 통합 검증을 통과해야 다음 단계로 갈 수 있는지 결정 기준이 필요함.  
   수정 방향: 예를 들어 `Phase 1: 신청/목록/상세`, `Phase 2: 팀장 처리/팀 이동 권한`, `Phase 3: 감사·동시성·장애 주입`처럼 FR ID와 exit condition을 연결하라. 단, 실제 일정이나 SLA 숫자는 근거 없이 만들지 않는 편이 맞음.

2. **High - 상태 명령 멱등성 요구가 생성만 검증되어 승인·반려·취소 중복 처리 결함을 놓칠 수 있음**  
   근거: FR-106은 “모든 생성·상태 명령은 idempotency key와 조건부 갱신을 사용”한다고 하지만 AC-108은 “같은 idempotency key 재시도 | 신청”만 다룸. 승인, 반려, 취소의 같은 키 재시도, 다른 키 중복 요청, 응답 재생 규칙이 검증되지 않음.  
   영향: 팀장이 승인 요청을 재시도하거나 직원 취소 요청이 네트워크 타임아웃 후 재전송될 때 중복 감사 이벤트, 잘못된 409, 또는 클라이언트가 최종 상태를 확정하지 못하는 문제가 생길 수 있음.  
   수정 방향: 승인·반려·취소 각각에 대해 같은 idempotency key 재시도 시 동일 결과를 반환하고 중복 이벤트가 없어야 한다는 AC를 추가하라. 다른 key의 경쟁 요청은 조건부 갱신으로 한 건만 성공한다는 AC와 분리하는 것이 좋음.

3. **High - People Platform 장애 시 조회 권한 판단이 불명확해 fail-open 또는 과도한 차단 위험이 있음**  
   근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고만 함. 하지만 FR-104와 routes는 상세 조회, 팀 승인함 조회, 현재 팀장 접근 상실까지 요구함. 조회 요청에서 People Platform 장애가 발생했을 때의 동작이 정의되지 않음.  
   영향: 이전 팀장이 캐시나 stale 관계로 계속 상세를 볼 수 있거나, 반대로 정상 팀장이 전체 기능을 예측 불가능하게 사용할 수 없게 됨. 휴가 사유 전문 접근까지 걸려 있어 보안 영향도 있음.  
   수정 방향: 조회·목록·처리 모두에 대해 People Platform 실패 시 정책을 명시하라. 보안 기준상 현재 팀장 관계를 확인해야 하는 팀장 조회/처리는 fail-closed가 자연스럽고, 직원 본인 조회는 세션 소유자 기준으로 허용할지 별도 정의해야 함.

4. **Medium - 감사 이벤트 스키마가 권한 거부와 조직 경계를 검증하기에 부족함**  
   근거: FR-105는 actor, request ID, 이전/이후 상태, timestamp를 기록한다고 하나, 권한 거부 이벤트에는 상태 전이가 없고, 조직 내 감사 조회를 보장할 조직 ID/tenant ID, action, outcome, denial reason 같은 필드가 명시되지 않음. 감사자는 “조직 내 감사 이벤트 읽기”만 허용되므로 감사 이벤트 자체의 조직 경계가 제품 요구로 필요함.  
   영향: 권한 거부 감사가 어떤 작업의 거부인지 검증하기 어렵고, 다중 조직 환경에서 감사 이벤트 조회가 교차 노출될 위험이 있음.  
   수정 방향: 감사 이벤트 필드에 최소한 `organization_id`, `action`, `outcome`, `target_request_id nullable`, `actor_id`, `previous_state nullable`, `next_state nullable`, `timestamp`, `denial_code`를 정의하라. 휴가 사유 전문 제외 요구는 유지해야 함.

5. **Medium - 겹침 검증의 범위가 덜 명시되어 잘못된 충돌 판정 가능성이 있음**  
   근거: FR-101은 “PENDING·APPROVED 신청과 겹칠 수 없다”고 하지만 “같은 직원의 신청”인지, 같은 조직 기준인지, CANCELLED/REJECTED 제외가 명시적 정책인지, KST 달력일 경계 저장 방식이 무엇인지가 부족함. 문맥상 본인 휴가로 추론되지만 AC-102도 범위를 확정하지 않음.  
   영향: 다른 직원의 휴가와 충돌 처리하거나, 조직/타임존 경계에서 같은 날짜를 다르게 계산하는 구현이 나올 수 있음.  
   수정 방향: “동일 조직의 동일 직원 기준으로 KST 달력일 inclusive range가 기존 PENDING 또는 APPROVED와 겹치면 409”처럼 충돌 범위를 명시하고, 저장/비교 기준도 KST date-only인지 UTC timestamp 변환인지 정하라.

검증기는 실행하지 않았습니다. 사용자 요청대로 원문 재작성, 파일 생성, 저장소 탐색 없이 제공된 PRD 텍스트만 검토했습니다.