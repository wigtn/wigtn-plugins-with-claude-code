**계약 감사**

| Contract | Applicable? | Status | Evidence |
|---|---:|---|---|
| Applicability ledger | Yes | Present | `Applicability` 표가 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Yes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Yes | Present | `State matrix`가 내 휴가, 신청 폼, 승인 상세 상태를 정의 |
| Mermaid user or system flow | Yes | Present | `User flow` Mermaid가 신청부터 취소/승인/반려까지 표현 |
| Acceptance precondition/action/result mapped to requirement IDs | Yes | Present | AC-101~AC-108이 FR ID, Given/When/Then/Verification을 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Yes | Missing | 출시/베타/운영 전환 단계와 각 단계별 FR·exit condition 매핑 없음 |

**Findings**

**High**

1. 직원 취소가 제품 동작으로 등장하지만 검증 가능한 요구사항과 AC가 부족합니다.  
영향: 취소 권한, 취소 가능 시점, 감사 이벤트, 동시성 처리 방식이 구현마다 달라질 수 있습니다. 특히 승인과 취소 동시 요청은 AC-106에만 간접 등장하고, 직원 단독 취소 성공/실패 케이스가 없습니다.  
근거: `Users, roles, and permissions`의 직원 Allowed에 “대기 취소”, `User flow`의 `PENDING -> CANCELLED`, FR-105의 “취소” 감사 기록. 하지만 Functional requirements에는 “직원은 본인 PENDING 신청만 취소 가능” 같은 독립 요건이 없고 Acceptance criteria에도 취소 성공, 이미 처리된 신청 취소 409, 타인 신청 취소 403이 없습니다.  
수정 방향: 취소를 별도 FR로 명시하고 AC를 추가하세요. 최소한 본인 PENDING만 취소 가능, APPROVED/REJECTED/CANCELLED는 취소 불가, 취소 감사 이벤트 원자 기록, 동시 승인/취소 중 단일 성공을 검증해야 합니다.

2. 감사 이벤트 스키마가 권한 거부 이벤트에 맞지 않고 보안상 애매합니다.  
영향: 권한 거부 감사에서 `request ID`, 이전/이후 상태를 기록하면 존재하지 않거나 접근 불가인 신청의 존재·상태를 과도하게 노출할 수 있습니다. 반대로 기록하지 않으면 FR-105와 충돌합니다.  
근거: FR-105는 “생성·승인·반려·취소와 권한 거부를 actor, request ID, 이전/이후 상태, timestamp로 기록”한다고 합니다. 권한 거부는 상태 전이가 아니므로 “이전/이후 상태”가 정의되지 않습니다. 감사자는 “휴가 사유 전문 읽기 금지”만 명시되어 있고, 거부 이벤트에서 신청 존재나 상태 노출 범위는 정의되지 않았습니다.  
수정 방향: 이벤트 유형별 필드 계약을 분리하세요. 권한 거부는 `attempted_action`, `actor`, `resource_reference policy`, `decision`, `timestamp`, `reason_code`처럼 상태 전이와 다른 스키마를 쓰고, 감사자에게 보일 수 있는 식별자와 마스킹 규칙을 명시해야 합니다.

3. Delivery phase 계약이 누락되어 출시 전 결정사항의 종료 조건이 없습니다.  
영향: API 지연 목표가 “정식 출시 전 결정”으로 남아 있지만, 어떤 단계에서 무엇이 충족되어야 출시 가능한지 검증할 수 없습니다.  
근거: `Non-functional requirements`와 `Assumptions and open decisions`는 API 지연 목표를 내부 베타 후 결정한다고 하지만, delivery phases와 exit condition 매핑이 없습니다. Review contract상 해당 계약은 적용 대상이며 Missing입니다.  
수정 방향: 예: 내부 베타, 출시 후보, 정식 출시 단계로 나누고 각 단계의 exit condition을 FR/AC에 연결하세요. API 지연 목표 결정도 정식 출시 exit condition으로 묶어야 합니다.

**Medium**

4. 날짜·타임존 규칙이 “KST 달력일” 수준에서 멈춰 경계 조건 검증이 부족합니다.  
영향: 서버 저장 방식, 클라이언트 표시, DST는 KST에 없더라도 타임존 변환, 종료일 포함 계산, 조직 외 지역 사용자의 입력 해석에서 오류가 날 수 있습니다.  
근거: FR-101은 “KST 달력일”과 양끝 포함만 정의합니다. 하지만 서버가 date-only로 저장하는지, UTC timestamp로 변환하는지, API 입력 포맷이 무엇인지, 겹침 판정이 `[start_date, end_date]`인지 명확하지 않습니다.  
수정 방향: API 입력을 `YYYY-MM-DD` date-only로 고정하고, 겹침 조건과 저장 기준을 명시하세요. AC에 종료일=다음 신청 시작일 같은 포함 경계 충돌 케이스를 추가하는 것이 좋습니다.

5. 멱등성 키 범위와 재사용 정책이 불명확합니다.  
영향: 같은 key가 다른 payload나 다른 actor/action에서 재사용될 때 보안·데이터 무결성 문제가 생길 수 있습니다.  
근거: FR-106은 “모든 생성·상태 명령은 idempotency key”를 요구하고 AC-108은 신청 재시도만 검증합니다. 키 scope, TTL, payload mismatch 처리, 상태 명령의 멱등 응답 규칙은 없습니다.  
수정 방향: 키를 `actor + organization + action + key` 범위로 제한하고, 동일 key 다른 payload는 409 또는 422로 정의하세요. 승인/반려/취소 재시도 AC도 추가해야 합니다.

6. 팀장 조회 권한과 처리 권한의 기준 시점은 명시됐지만 목록/상세에서의 개인정보 노출 범위가 부족합니다.  
영향: 새 팀장이 이전 팀에서 제출된 휴가 사유를 볼 수 있는 것은 의도일 수 있으나, PRD가 “현재 팀장” 원칙만 말하고 사유 조회 범위를 명시적으로 승인하지 않아 개인정보 정책 해석이 흔들립니다.  
근거: FR-103은 승인 시점 기준, FR-104는 직원 이동 후 새 팀장이 접근·처리한다고 합니다. Risks에는 “휴가 사유는 직원 본인과 현재 팀장만 읽음”이 있으나 감사자 외 다른 역할의 상세 필드 노출 표는 없습니다.  
수정 방향: 상세 응답 필드별 접근 표를 추가하세요. 직원, 현재 팀장, 이전 팀장, 감사자 각각에게 사유/상태/날짜/actor 표시 범위를 명확히 해야 합니다.

**Low**

7. 팀장 본인의 신청 처리 금지와 “현재 팀 직원” 조건의 자기 소속 예외가 더 구체화되면 좋습니다.  
영향: 팀장이 자기 자신도 팀 소속 직원인 조직 모델에서 필터링 실수가 발생할 수 있습니다.  
근거: FR-103과 AC-105는 본인 신청 처리 금지를 말하지만, `/team/leave` 목록에서 본인 신청을 숨길지 표시하되 처리만 막을지는 불명확합니다.  
수정 방향: 목록·상세·처리별로 본인 신청 정책을 나누어 정의하세요. 보수적으로는 팀장 승인함에서 본인 신청을 제외하고 직접 URL 접근도 403으로 정의하는 편이 명확합니다.

8. 감사 이벤트의 시간 기준이 불명확합니다.  
영향: KST 달력일과 audit timestamp가 섞이면 감사·정렬·장애 분석에서 혼동이 생길 수 있습니다.  
근거: FR-105는 `timestamp`만 요구합니다. 시간대, 정밀도, 서버 생성 여부가 없습니다.  
수정 방향: 감사 timestamp는 서버 생성 UTC ISO-8601 등으로 고정하고, UI 표시만 KST로 변환한다고 명시하세요.

검증기는 실행하지 않았습니다. 사용자가 PRD 원문만 제공했고, 파일 생성·저장소 탐색을 하지 말라고 했기 때문입니다.