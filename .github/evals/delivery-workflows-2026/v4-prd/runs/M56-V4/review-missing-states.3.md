## 산출물 계약 감사

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability`에서 Pages/routes, State matrix, User flow를 모두 `Required`로 판정하고 근거를 제시함 |
| Pages and routes | Present | 4개 화면의 route, 허용 역할, 주요 동작이 정의됨 |
| Empty/loading/error/success/recovery state matrix | Missing | 적용성에서는 `Required`로 선언했지만 화면별 empty/loading/error/success/recovery 상태표가 없음 |
| Mermaid user or system flow | Present | 신청 검증부터 PENDING 및 세 가지 종결 상태까지 Mermaid 흐름이 존재함 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~108이 Requirement, Given, When, Then, Verification과 연결됨 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3에 FR ID와 검증 가능한 종료 조건이 있음 |

## Findings

### High — 동시 신청에서 기간 중복 불변식을 보장하거나 검증할 계약이 없다

- 근거: `FR-101`, `FR-106`, `AC-102`, `AC-106`, `AC-108`
- 문제: `FR-106`의 조건부 갱신은 기존 신청의 상태 경쟁에는 유효하지만, 서로 다른 idempotency key로 동시에 생성되는 두 신규 신청은 각각 “겹침 없음”을 읽고 모두 삽입될 수 있다. 비교할 단일 기존 행이 없으므로 조건부 갱신만으로 `FR-101`의 기간 중복 금지를 보장한다고 볼 수 없다.
- 영향: 동일 직원에게 겹치는 PENDING 신청이 생겨 핵심 휴가 무결성이 깨질 수 있다. 현재 AC는 순차 충돌과 승인/취소 경쟁만 검증한다.
- 수정 방향: 동일 직원·기간 범위의 생성 경쟁에서 “최대 한 건만 성공”한다는 원자적 보장 방식을 명시한다. 서로 다른 키의 동시 중복 신청을 실행해 한 건만 PENDING, 다른 한 건은 409가 되고 성공 감사 이벤트도 한 건뿐임을 검증하는 AC를 추가한다.

### High — 권한 거부 감사가 테넌트 경계와 자원 존재 여부를 누설할 수 있다

- 근거: `FR-105`, `Authorization and data boundaries`, `AC-105`, 감사자 권한
- 문제: 권한 거부 이벤트를 어느 조직 감사 스트림에 기록할지, 거부 전에 대상 신청을 조회하는지, 거부 이벤트의 이전/이후 상태를 어떻게 기록할지가 없다. 타 조직 ID를 추측한 요청에서 403과 실제 상태를 기록하면 대상 존재나 상태가 감사자 또는 공격자에게 노출될 수 있다.
- 또한 감사 필드에 leave ID, action, outcome이 명시되지 않아 request ID만으로 특정 신청의 생성·처리 이력을 안정적으로 재구성하기 어렵다.
- 영향: 조직 간 정보 노출, 감사 이벤트 오귀속, 감사 이력 화면의 추적 불가능성이 발생할 수 있다.
- 수정 방향: 비인가 자원 접근의 외부 응답 정책(예: 존재 여부를 숨기는 일관된 응답), 조회·권한검사 순서, 거부 이벤트 소속 조직과 상태 필드의 null/redaction 규칙을 정한다. 감사 스키마에는 최소한 event ID, resource ID, action, outcome, actor/tenant 경계를 포함하고 감사자의 조직 필터링을 서버에서 강제한다.

### High — 멱등성 계약이 키 재사용과 상태 명령의 의미를 결정하지 못한다

- 근거: `FR-106`, `AC-108`
- 문제: 모든 생성·상태 명령에 멱등성을 요구하지만 AC는 신청 생성 재시도만 다룬다. 키의 범위(actor/organization/endpoint), 요청 payload fingerprint, 보존 기간, 같은 키에 다른 payload를 보낸 경우, 최초 요청 처리 중 재시도, 성공 후 재시도 응답이 정의되지 않았다.
- 영향: 다른 명령이 같은 키를 충돌해 잘못된 결과를 재생하거나, 승인·반려·취소 재시도에서 200/409 및 감사 이벤트 수가 구현마다 달라질 수 있다.
- 수정 방향: 키의 유일성 범위와 요청 결합 규칙을 명시하고, 동일 키·동일 요청은 최초 결과를 재생하며 이벤트를 중복 생성하지 않도록 한다. 동일 키·다른 payload의 오류, 동시 재시도, 승인·반려·취소 각각의 재시도 AC를 추가한다.

### High — 팀 이동 이후 조회 권한과 People Platform 장애 범위가 불명확하다

- 근거: `FR-103`, `FR-104`, Pages and routes, Authorization, Risks
- 문제: `FR-104`는 이동한 직원의 PENDING 신청만 새 팀장이 처리한다고 설명한다. APPROVED/REJECTED/CANCELLED 상세와 사유도 새 팀장이 읽는지, 이전 팀장이 모든 상태에서 즉시 접근을 잃는지는 정해지지 않았다. 또한 People Platform 실패 시 “처리 요청”을 503으로 한다는 표현이 승인·반려만 의미하는지, 팀 목록·상세·취소까지 포함하는지 모호하다.
- 영향: 전 팀장의 민감한 휴가 사유 열람이 남거나, 새 팀장이 불필요하게 과거 사유 전체를 보게 될 수 있다. 장애 시 읽기 및 명령별 동작도 일관되게 검증할 수 없다.
- 수정 방향: 상태별·작업별 권한표에 현재 팀 관계의 적용 시점, 이동 전후 조회 범위, 사유 공개 범위를 명시한다. 각 작업에서 People Platform이 필수인지와 장애 시 503, 캐시 허용 여부, 상태·입력 보존 및 재시도 동작을 정하고 이동 및 장애 테스트를 추가한다.

### High — 필수 UI 상태 계약과 여러 P0 실패 경로의 수용 기준이 빠져 있다

- 근거: `Applicability`, Pages and routes, `FR-101`~`FR-106`, `AC-101`~`AC-108`, NFR
- 문제: 필수라고 선언한 state matrix가 없다. 특히 빈 목록, 로딩, 검증 오류, 403/404, 중복 409, People Platform 503, 동시성 패배 후 새 상태 반영, 재시도 중복 방지에 대한 화면 동작과 복구 경로가 정의되지 않았다.
- 독립 AC도 직원 취소, 유효하지 않은 반려 사유, 타 조직 조회·명령, 권한 거부 감사의 원자성/실패, 모든 상태 명령의 멱등성을 직접 검증하지 않는다. 감사 장애 주입 NFR은 “이벤트 존재”만 말하고 동기 트랜잭션과 outbox의 최종 확인 시점 차이를 정하지 않는다.
- 영향: P0 구현이 서로 다른 UX와 오류 의미를 가져도 현재 계약상 합격할 수 있다. 원자성 및 보안 회귀도 출시 검증에서 누락될 수 있다.
- 수정 방향: 화면/주요 작업별 empty·loading·success·error·recovery matrix를 추가한다. 누락된 P0 경로에는 Given/When/Then AC를 보강하고, outbox 사용 시 이벤트 관찰 기한·재처리·중복 금지 조건을 명시한다. API 지연 목표의 결정 시점도 “베타 종료일까지”와 “정식 출시 전” 중 하나의 출시 게이트로 통일해야 한다.

검토 범위는 제공된 PRD 원문뿐이며, 저장소·구현·테스트 증거는 확인하지 않았다. 따라서 위 평가는 문서 계약의 완결성과 검증 가능성에 대한 것이다.