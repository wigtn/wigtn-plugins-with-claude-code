**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 Empty/Loading/Error/Success/Recovery 정의 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid lifecycle 정의 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~108이 FR ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Missing | 릴리스 단계, 각 단계별 FR 범위, exit condition 없음 |

**Findings**

**High: 팀장 권한 확인 실패 시 조회 경로의 fail-closed 동작이 불완전합니다.**  
영향도: 팀장 목록·상세 조회에서 People Platform 장애 또는 지연 시 이전 소속/캐시 권한으로 타 팀 직원 신청을 볼 위험이 있습니다. 휴가 사유는 민감정보라 조회 권한의 실패 모드가 처리 권한만큼 중요합니다.  
근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고 처리 요청만 명시합니다. 반면 FR-104는 “작업별로” 현재 팀을 검사한다고 하며, `/team/leave`, `/leave/:id` 조회도 현재 팀장 권한에 의존합니다.  
수정 방향: People Platform 의존 권한이 필요한 모든 팀장 범위 작업, 즉 팀 승인함 조회·상세 조회·승인·반려에 대해 실패 시 `503 fail-closed`, 상태 불변, 감사 이벤트 정책을 명시하세요. 캐시 허용 여부와 최대 staleness도 정해야 합니다.

**High: 겹침 방지의 동시성 보장이 검증 가능하지 않습니다.**  
영향도: 두 개의 생성 요청이 동시에 들어오면 각각 검증 시점에는 겹치지 않는 것으로 보이고 둘 다 `PENDING`으로 생성될 수 있습니다. 휴가 기간 중복 금지라는 핵심 불변식이 깨집니다.  
근거: FR-101은 `PENDING·APPROVED`와 겹칠 수 없다고 하지만, FR-106의 “조건부 갱신”은 상태 명령에는 자연스럽게 적용되나 신규 생성의 기간 겹침에는 어떤 조건/락/제약을 쓰는지 불명확합니다. AC-108은 같은 idempotency key 재시도만 검증하고, 서로 다른 key의 동시 생성 충돌은 없습니다.  
수정 방향: 생성 시 조직+사용자+기간 기준의 직렬화, exclusion constraint, advisory lock, 또는 겹침 재검사 포함 트랜잭션 중 하나를 제품 요구로 고정하고, 동시 생성 AC를 추가하세요.

**Medium: 감사 요구사항과 AC-102가 충돌합니다.**  
영향도: 구현자가 실패/거부/충돌 이벤트를 어디까지 남겨야 하는지 다르게 해석할 수 있습니다. 감사 범위가 흔들리면 보안 사고 조사와 테스트 기준이 불안정해집니다.  
근거: FR-105는 “생성·승인·반려·취소와 권한 거부”를 기록한다고 합니다. AC-102는 기간 겹침 신청 시 “신청·성공 감사 이벤트 없음”이라고만 말해 충돌 실패 이벤트가 필요한지 불명확합니다. 권한 거부는 감사하지만 검증 실패·충돌은 감사하지 않는 정책인지 설명이 없습니다.  
수정 방향: 감사 대상 이벤트를 성공 상태 변경, 권한 거부, 검증 실패, 충돌 실패로 분리하고 각 이벤트의 기록 여부를 명시하세요. AC-102의 “성공 감사 이벤트 없음”도 실패 이벤트 허용/금지로 바꾸는 편이 검증 가능합니다.

**Medium: `request ID`와 `idempotency key`의 의미가 섞여 있습니다.**  
영향도: 멱등 재시도에서 감사 이벤트 중복 제거 기준이 불명확합니다. 같은 idempotency key지만 다른 HTTP request ID일 때 “중복 이벤트 없음”과 “request ID 기록”을 동시에 어떻게 만족할지 구현 차이가 생깁니다.  
근거: FR-105는 감사 이벤트에 `request ID`를 기록한다고 하고, FR-106/AC-108은 같은 idempotency key 재시도 시 같은 신청 ID와 중복 이벤트 없음을 요구합니다. 재시도 request ID를 별도 저장해야 하는지, 최초 request ID만 남기는지 정의가 없습니다.  
수정 방향: command id, idempotency key, HTTP request/correlation ID를 구분하세요. 감사 이벤트는 최초 성공 command 기준 1건인지, 재시도 접근 로그는 별도인지 정하면 됩니다.

**Medium: 배송 단계 산출물 계약이 빠져 있습니다.**  
영향도: 모든 요구사항이 P0로만 묶여 있어 베타, GA, 마이그레이션/운영 준비, 감사 검증의 완료 기준을 추적하기 어렵습니다.  
근거: 계약 감사에서 `Delivery phases mapped to requirement IDs and exit conditions`가 Missing입니다.  
수정 방향: 예를 들어 내부 베타와 정식 출시 단계를 나누고, 각 단계에 포함되는 FR/AC, 장애 주입 테스트 통과, latency 목표 확정 같은 exit condition을 연결하세요.

**Low: 감사자 조회 범위와 마스킹 기준이 충분히 구체적이지 않습니다.**  
영향도: 감사 화면에서 휴가 사유 전문은 금지되어 있지만, 이벤트 메타데이터만으로도 특정 직원의 휴가 패턴이나 권한 거부 대상이 과도하게 노출될 수 있습니다.  
근거: `Users, roles, and permissions`는 감사자가 “조직 내 감사 이벤트 읽기” 가능, “휴가 사유 전문 읽기” 금지라고만 합니다. `/audit/leave`의 필터, 필드, 보존기간, export 가능 여부는 없습니다.  
수정 방향: 감사자에게 노출되는 필드 allowlist, 사유 redaction, actor/subject 표시 수준, 필터 권한, 보존기간 또는 삭제 정책을 최소한으로 정의하세요.

검토는 제공된 PRD 원문만 기준으로 했고, 저장소 탐색·파일 생성·validator 실행은 하지 않았습니다.