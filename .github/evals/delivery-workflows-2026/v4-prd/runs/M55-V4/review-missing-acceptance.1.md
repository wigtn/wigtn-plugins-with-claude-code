**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판단함 |
| Pages and routes | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix` 표가 있음 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid 생명주기 흐름이 있음 |
| Acceptance precondition/action/result mapped to requirement IDs | Missing | 요구사항 ID와 Delivery exit condition은 있으나, 각 FR별 precondition/action/result 형태의 검증 가능한 acceptance criteria가 없음 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery` 표가 Phase별 FR ID와 exit condition을 매핑함 |

**Findings**

| Impact | Finding | Evidence | 수정 방향 |
|---|---|---|---|
| high | 멱등성 요구가 구현·검증 가능한 수준으로 정의되지 않아 중복 처리, 재시도 오동작, 키 재사용 공격을 막는 기준이 불명확함 | `FR-106`은 “idempotency key와 조건부 갱신”만 요구하고, 키 스코프, TTL, 동일 키의 payload mismatch 처리, 성공/실패 재응답 규칙, actor/request 바인딩을 정의하지 않음 | 멱등성 키를 `actor + command type + target/request scope`에 묶고, 보관 기간, 동일 키 재시도 응답, 다른 payload 재사용 시 `409` 같은 결과, 권한 변경 후 재시도 처리 기준을 acceptance criteria로 추가 |
| high | 감사 이벤트 스키마가 권한 거부 케이스와 충돌해 검증 불가능하거나 과다 노출 위험이 있음 | `FR-105`는 생성·승인·반려·취소와 권한 거부를 모두 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 함. 하지만 권한 거부는 request 존재 여부를 확인할 수 없거나, 확인하면 타인/타조직 request ID 존재를 감사·응답 경로로 누출할 수 있음 | 거부 이벤트 전용 필드를 분리해 `target_request_id nullable`, `decision=DENIED`, `reason_code`, `resolved_org_id`, `previous/next_state nullable` 등을 정의. 감사자 조회에서도 존재 여부와 휴가 사유가 새지 않는 마스킹 규칙을 명시 |
| medium | 현재 팀장 권한과 휴가 사유 열람 범위가 과거·최종 상태 신청에 대해 모호해 개인정보 경계가 흔들림 | `Pages/routes`는 `/leave/:id`를 “소유 직원, 현재 팀장”에게 조회 허용. `FR-103`은 팀장이 현재 팀 직원의 `PENDING` 신청만 처리한다고 제한. `Risks`는 휴가 사유를 “직원 본인과 현재 팀장만” 읽는다고 해, 이동 후 새 팀장이 과거 신청 사유까지 읽는지 불명확함 | 팀장 조회 권한을 상태별로 분리. 예: 현재 팀장은 `PENDING` 처리 대상만 전문 사유 조회 가능, terminal 상태는 요약만 가능 또는 당시 처리 팀장/감사 정책에 따름. 직원 이동 후 기존/신규 팀장의 terminal 상세 접근 규칙을 명시 |
| medium | 겹침 검증 범위가 불명확해 핵심 도메인 제약을 잘못 구현할 수 있음 | `FR-101`의 “PENDING·APPROVED 신청과 겹칠 수 없다”가 본인 신청 기준인지, 같은 조직 전체인지, 팀 단위인지 명시하지 않음 | “같은 조직 내 동일 직원의 PENDING 또는 APPROVED 신청과 KST 날짜 구간이 겹치면 거부”처럼 주체와 범위를 명시. 경계값 예시도 acceptance criteria에 포함 |
| medium | PRD의 검증 계약이 Delivery 수준에 머물러 FR별 합격 조건을 재현하기 어려움 | 계약 감사상 `Acceptance precondition/action/result mapped to requirement IDs`가 없음. 예: `FR-104`의 직원 이동 후 접근 상실, People Platform 실패, `FR-106`의 outbox 원자성 장애 주입은 개별 precondition/action/result가 없음 | 각 FR마다 최소 1개 이상의 Given/When/Then 또는 precondition/action/result 기준을 추가. 특히 권한, 동시성, 멱등성, People Platform 장애, 감사 원자성은 성공·실패 양쪽 케이스로 분리 |

요약하면 구조 산출물은 대부분 존재하지만, acceptance criteria 계약이 비어 있고 멱등성·감사·팀 이동 후 개인정보 경계가 구현자 해석에 맡겨져 있습니다. 이 세 영역은 출시 전 반드시 더 구체화해야 합니다.