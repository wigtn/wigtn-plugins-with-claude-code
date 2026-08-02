**산출물 계약 감사**

| Contract | Status | Applicability | Evidence |
|---|---|---:|---|
| Applicability ledger | Missing | Applicable | 사용자 화면, 상태, 플로우, 인수조건, Delivery가 모두 적용되지만 각 산출물의 Required/N/A 판정 근거를 별도 ledger로 기록하지 않음 |
| Pages and routes | Present | Applicable | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | Applicable | `State matrix`에 내 휴가, 신청 폼, 승인 상세 상태 정의 |
| Mermaid user or system flow | Present | Applicable | `User flow` Mermaid로 신청부터 취소·승인·반려 전이 정의 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | Applicable | `Acceptance criteria`가 AC별 FR ID, Given/When/Then/Verification 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Applicable | `Delivery`가 Phase별 Requirement IDs와 exit condition 포함 |

**Findings**

**High - 취소 성공 경로가 핵심 상태인데 검증 계약에서 빠져 있음**  
근거: FR-102는 `PENDING -> CANCELLED` 전이를 핵심 상태 전이로 정의하고, 역할 표도 직원의 `대기 취소`를 허용합니다. FR-105는 `취소` 감사 이벤트를 요구합니다. 하지만 AC에는 취소 성공, 취소 감사 이벤트, 취소 후 재처리 불가를 직접 검증하는 항목이 없습니다. AC-106은 승인과 취소 동시 요청만 다룹니다.  
영향: 구현이 취소 기능, 취소 감사, 취소 권한 검사를 누락해도 PRD상 인수 테스트를 통과할 수 있습니다.  
수정 방향: `소유 직원 + PENDING` 취소 성공, `CANCELLED + 감사 이벤트 1건`, 취소 후 승인/반려/재취소 409를 별도 AC로 추가하세요.

**High - 상태 명령 멱등성 검증이 신청에만 한정됨**  
근거: FR-106은 “모든 생성·상태 명령”에 idempotency key를 요구하지만 AC-108은 `신청` 재시도만 검증합니다. 승인, 반려, 취소의 동일 key 재시도 결과와 중복 감사 이벤트 방지가 없습니다.  
영향: 승인/반려/취소에서 네트워크 재시도 시 중복 이벤트, 잘못된 409, 클라이언트 재시도 불능이 발생할 수 있습니다.  
수정 방향: 승인·반려·취소 각각에 대해 같은 idempotency key 재시도 시 동일 결과 반환, 중복 상태 변경 없음, 중복 감사 이벤트 없음 기준을 추가하세요.

**High - 권한 거부 감사 이벤트 필드가 보안상 애매함**  
근거: FR-105는 권한 거부도 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 합니다. 그런데 다른 팀장 또는 무권한 사용자가 임의 ID로 접근한 경우, 감사 이벤트에 실제 `request ID`와 이전/이후 상태를 남기는 정책이 존재하면 권한 없는 행위자가 존재 여부나 상태를 추론할 수 있습니다. AC-105도 `403, 상태 불변, 권한 거부 감사`만 요구하고, 응답·감사 이벤트의 redaction 기준은 없습니다.  
영향: 타인의 신청 존재 여부, 현재 상태, 조직 경계 정보가 권한 실패 경로에서 새어 나갈 수 있습니다.  
수정 방향: 권한 거부 감사는 내부 감사용 원본 ID 기록 가능 여부와 클라이언트 응답의 존재 은닉 정책을 분리하세요. 예: 클라이언트에는 일관된 403/404 정책, 감사 이벤트에는 `attempted_request_id`, `resolved_request_id nullable`, `status_snapshot nullable/redacted`처럼 명확히 정의합니다.

**Medium - Delivery Phase 1의 FR-104 종료 조건이 요구사항 전체를 검증하지 못함**  
근거: Delivery Phase 1은 FR-104를 포함하지만 exit condition은 `신청·중복·조직 격리 테스트 통과`입니다. FR-104에는 작업별 현재 팀, 신청 소유자, 현재 상태 검사와 “직원 이동 후 새 팀장 처리, 이전 팀장 접근 상실”이 포함됩니다. 이는 Phase 1 종료 조건에 없습니다.  
영향: Phase 1 완료 판정이 FR-104의 핵심 권한 동작을 검증하지 않은 채 내려질 수 있습니다.  
수정 방향: FR-104를 Phase 2/3으로 재배치하거나 Phase 1 exit condition에 소유자, 현재 팀장, 현재 상태, 팀 이동 접근 상실 테스트를 포함하세요.

**Medium - People Platform 장애 처리 범위가 처리 요청에만 명시됨**  
근거: `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고만 합니다. 하지만 FR-103/104와 `/team/leave`, `/leave/:id`의 현재 팀장 조회도 People Platform의 현재 팀 관계에 의존합니다.  
영향: 조회/list에서는 장애 시 fail-open, stale team cache 사용, 이전 팀장 노출 같은 구현 차이가 생길 수 있습니다.  
수정 방향: People Platform 장애 시 생성, 상세 조회, 팀 승인함 조회, 승인/반려/취소 각각의 동작을 명시하세요. 특히 현재 팀장 권한이 필요한 조회와 처리는 fail-closed 기준을 맞춰야 합니다.

**Medium - 감사자의 읽기 범위와 개인정보 최소화가 불완전함**  
근거: 역할 표는 감사자가 “조직 내 감사 이벤트 읽기” 가능, “휴가 사유 전문 읽기” 금지라고 합니다. FR-105는 사유 전문 제외만 명시하고, 감사 이벤트에 actor, request ID, 상태, timestamp를 남깁니다. 하지만 감사자가 request ID를 통해 상세 API나 다른 경로에서 사유를 조회할 수 없도록 하는 연결 제한, actor 식별자 노출 수준, 보존 기간은 없습니다.  
영향: 감사 화면이 사유를 직접 담지 않아도 request ID 기반 우회 조회나 과도한 개인정보 노출이 생길 수 있습니다.  
수정 방향: 감사자 API는 감사 이벤트 전용 projection만 반환하고 leave detail 접근 권한과 분리한다고 명시하세요. actor 표시 수준, request ID 링크 가능 여부, 보존/삭제 정책도 최소 기준을 정하면 좋습니다.

**Low - API 지연 목표가 출시 전 결정으로만 되어 있어 현재 검증 불가능함**  
근거: NFR과 Open decisions에 “내부 베타 측정 후 제품 책임자가 정식 출시 전에 결정”이라고 되어 있습니다. 날짜, 결정 산출물, 출시 gate 기준은 없습니다.  
영향: 성능 목표가 없어 베타 종료 전까지 성능 회귀를 판단하기 어렵고, 출시 직전 비기능 요구가 뒤늦게 생길 수 있습니다.  
수정 방향: 지금 수치를 invent할 필요는 없지만, “베타 종료일”, “결정 문서/owner”, “목표 미정 기간의 계측 필수 지표” 정도는 exit condition으로 두세요.

**Open Questions**

- 권한 없는 요청에 대해 신청 존재 여부를 숨길 것인지, 항상 403을 줄 것인지, 감사 이벤트에는 어떤 수준까지 원본 ID와 상태를 남길 것인지 결정이 필요합니다.
- People Platform 장애 시 팀 승인함 조회와 상세 조회도 503 fail-closed인지 명확히 해야 합니다.
- 취소와 상태 명령 멱등성은 현재 PRD 의도상 P0로 보이므로 AC 보강이 필요합니다.

검토는 제공된 PRD 원문만 기준으로 했고, 요청대로 파일 생성이나 저장소 탐색은 하지 않았습니다.