**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 표시함 |
| Pages and routes | Missing | 직원 신청과 팀장 처리 “화면이 있다”고만 되어 있고 실제 페이지/route/화면 목록 계약은 없음 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 내 휴가, 신청 폼, 승인 상세의 상태가 있음 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid 생명주기 흐름이 있음 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `Acceptance criteria`가 AC별로 FR, Given/When/Then/Verification을 매핑함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery`가 Phase별 FR과 exit condition을 매핑함 |

**Findings**

1. **medium - Pages/routes 계약이 Required인데 실제 산출물이 누락됨**
   - 근거: `Applicability`는 Pages/routes를 Required로 선언하지만, PRD에는 직원 신청/목록/상세, 팀장 승인 상세, 감사자 감사 이벤트 조회 등 접근 가능한 페이지나 route 단위 계약이 없음.
   - 영향: 구현자가 화면 경계와 권한 경계를 다르게 해석할 수 있음. 특히 감사자는 역할에 포함되어 있지만 감사자 화면/API surface가 state matrix, route 계약, acceptance에서 빠져 있음.
   - 수정 방향: 최소한 surface 목록을 `내 휴가 목록`, `휴가 신청`, `내 휴가 상세`, `팀 승인 대기/상세`, `감사 이벤트 조회`처럼 명시하고 각 surface의 접근 역할과 주요 데이터 범위를 연결해야 함.

2. **high - 겹침 검사의 범위가 불명확함**
   - 근거: `FR-101`은 “PENDING·APPROVED 신청과 겹칠 수 없다”고 하지만 같은 직원 기준인지, 같은 조직 기준인지, 팀 기준인지 명시하지 않음. `AC-102`도 “PENDING 또는 APPROVED 기간과 겹침”만 말함.
   - 영향: 전사적으로 같은 날짜 휴가가 금지되는 것으로 잘못 구현될 수 있고, 반대로 조직/소유자 격리 없이 충돌 검사가 구현되면 타인의 휴가 존재를 추론하는 정보 노출이 생김.
   - 수정 방향: “동일 조직 내 동일 신청 소유자의 PENDING 또는 APPROVED 휴가 기간과 겹칠 수 없다”처럼 충돌 scope를 명시하고, AC-102도 동일 소유자/타 소유자 케이스를 나눠 검증해야 함.

3. **high - 조회 권한과 휴가 사유 노출 범위가 상태·시점별로 충분히 정의되지 않음**
   - 근거: 역할 표는 팀장이 “현재 팀 직원 신청 조회” 가능하다고 하고, `FR-103`은 현재 팀 직원 `PENDING` 신청만 처리한다고 함. `Risks`는 휴가 사유를 직원 본인과 현재 팀장만 읽는다고 함. 하지만 현재 팀장이 `APPROVED/REJECTED/CANCELLED` 상세와 사유까지 읽을 수 있는지, 팀 이동 후 새 팀장이 과거 신청 사유를 읽는지, 이전 팀장이 최종 처리 후에도 조회 가능한지 불명확함.
   - 영향: 민감한 휴가 사유가 조직 이동이나 상태 변경 후 과다 노출될 수 있음. 구현마다 목록 조회와 상세 조회 권한이 달라질 가능성이 큼.
   - 수정 방향: 조회 권한을 `목록 메타데이터`, `상세`, `사유 전문`으로 분리하고, 역할·상태·현재 팀 관계·팀 이동 후 접근 정책을 표로 고정해야 함.

4. **medium - 취소 기능은 요구사항에 있지만 정상 취소 acceptance가 없음**
   - 근거: 역할 표와 flow에는 직원의 `PENDING` 취소가 있고 `FR-102`, `FR-105`, `FR-106`도 취소를 포함하지만, AC에는 승인과 취소 동시성인 `AC-106`만 있고 정상 취소, 타인 취소 금지, 이미 최종 상태 취소 시 409 검증이 없음.
   - 영향: 취소가 실제 구현 완료 기준에서 빠질 수 있고, 권한/감사/멱등성 처리가 승인·반려와 다르게 구현될 수 있음.
   - 수정 방향: 정상 취소 AC, 비소유자 취소 403 AC, 최종 상태 취소 409 AC, 취소 멱등성 재시도 AC를 추가하는 것이 좋음.

5. **medium - 감사 이벤트 스키마가 거부·실패 케이스에 대해 모순적으로 해석될 수 있음**
   - 근거: `FR-105`는 생성·승인·반려·취소와 권한 거부를 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 함. 하지만 권한 거부나 생성 전 검증 실패에는 휴가 request ID 또는 이전/이후 상태가 없을 수 있음. `AC-102`는 충돌 시 “신청·성공 감사 이벤트 없음”이라고만 하며 실패 감사 여부를 명확히 하지 않음.
   - 영향: 감사 이벤트 저장이 실패하거나, 거부 이벤트가 누락되거나, 존재하지 않아야 할 request ID를 만들게 될 수 있음. 보안 감사 관점에서도 403과 409, 503의 기록 정책이 불균일해질 수 있음.
   - 수정 방향: 감사 이벤트 타입별 필수 필드를 분리해야 함. 예: 상태 변경 이벤트는 request ID와 prev/next state 필수, 권한 거부 이벤트는 target request ID가 있을 때만 nullable로 기록, 검증 실패/충돌은 감사 대상 여부를 명시.