**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Missing | 적용성은 Required로 선언했지만 실제 페이지/라우트 목록, 진입 조건, 화면별 권한 경계가 없음 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 내 휴가, 신청 폼, 승인 상세 상태가 있음 |
| Mermaid user or system flow | Present | `User flow` Mermaid가 신청, 검증, 취소, 승인, 반려를 표현함 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `Acceptance criteria`가 AC별 Given/When/Then/Verification과 FR 매핑을 포함함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery`가 Phase별 Requirement IDs와 exit condition을 포함함 |

**Findings**

**High - Pages/routes 계약이 적용 대상인데 실제 산출물이 없습니다.**  
근거: `Applicability`는 Pages/routes를 Required로 선언했고 “직원 신청과 팀장 처리 화면이 있다”고 했지만, 본문에는 어떤 화면/라우트가 존재하는지, 각 화면의 접근 권한, 조회 범위, 상세 화면에서 사유 노출 여부가 명시되지 않았습니다.  
영향: 구현자가 “내 휴가”, “승인 상세” 정도만 추정해야 하며, 팀장 목록 화면, 직원 상세 화면, 감사자 화면의 존재 여부와 접근 제어가 검증 불가능합니다. 특히 감사자는 감사 이벤트를 읽을 수 있으므로 화면/API 경계가 없으면 휴가 사유 전문 비노출 요구와 충돌할 수 있습니다.  
수정 방향: `Pages/routes` 표를 추가해 직원 목록/신청/상세, 팀장 대기 목록/상세 처리, 감사 이벤트 조회 화면 또는 API를 명시하고, 각 surface별 role, allowed data fields, forbidden fields, 상태별 행동을 정의해야 합니다.

**High - 취소 기능의 정상/거부/감사/멱등성 검증이 부족합니다.**  
근거: `Users, roles, and permissions`는 직원의 “대기 취소”를 허용하고, `FR-102`는 PENDING에서 CANCELLED 전이를 허용합니다. 그러나 AC에는 단독 취소 성공 기준이 없고, `FR-105`의 “취소 감사 이벤트”도 취소 AC로 검증되지 않습니다. `FR-106`은 모든 상태 명령의 idempotency를 요구하지만 취소 재시도 검증도 없습니다.  
영향: 취소가 핵심 상태 전이인데 승인/반려보다 덜 명세되어, 구현상 취소 누락, 타인 취소 허용, 중복 취소 이벤트, 승인과 경합 시 잘못된 최종 상태가 발생해도 PRD 통과 여부를 판단하기 어렵습니다.  
수정 방향: “본인 PENDING 신청 취소 성공”, “타인/최종 상태 취소 거부”, “동일 idempotency key 취소 재시도”, “승인/취소 경합” AC를 분리해 추가해야 합니다.

**High - 실패 감사 정책이 부분적으로 모순되거나 원자성 범위가 불명확합니다.**  
근거: `FR-105`는 “생성·승인·반려·취소와 권한 거부”를 감사 기록한다고 합니다. `AC-105`는 403에 권한 거부 감사를 요구합니다. 반면 `AC-102`는 날짜 충돌 409에서 “신청·성공 감사 이벤트 없음”이라고만 하며 실패 감사 여부가 불명확합니다. `FR-106`의 원자성은 “상태와 감사 이벤트”에 초점이 있어, 상태 변경이 없는 권한 거부 감사의 원자성/중복 방지 기준도 빠져 있습니다.  
영향: 어떤 실패가 감사 대상인지 구현마다 달라질 수 있고, 권한 거부 재시도나 공격성 반복 요청에서 감사 이벤트가 중복 폭증하거나 누락될 수 있습니다.  
수정 방향: 감사 대상 실패를 명확히 분류해야 합니다. 예: 403 권한 거부는 감사, 409 비즈니스 충돌은 감사하지 않음 또는 별도 이벤트. 권한 거부 이벤트에도 idempotency/dedup 기준, 기록 필드, 개인정보 제외 기준을 정의해야 합니다.

**Medium - 상태 명령 멱등성은 요구하지만 신청만 검증합니다.**  
근거: `FR-106`은 “모든 생성·상태 명령”에 idempotency key를 요구하지만 `AC-108`은 신청 재시도만 다룹니다. 승인, 반려, 취소 재시도 시 같은 응답을 반환하는지, 이미 성공한 명령의 중복 감사 이벤트를 막는지에 대한 AC가 없습니다.  
영향: 승인/반려 API 재시도에서 중복 감사 이벤트가 생기거나, 같은 키 재시도에 409를 반환하는 구현도 PRD상 배제하기 어렵습니다.  
수정 방향: 승인/반려/취소 각각에 대해 같은 idempotency key 재시도 결과, 다른 key로 최종 상태 재명령 시 결과, 감사 이벤트 중복 금지 기준을 추가해야 합니다.

**Medium - 팀장 권한의 “현재 팀” 판정 모델이 구현 가능 수준까지 닫혀 있지 않습니다.**  
근거: `FR-103`, `FR-104`, `AC-107`은 승인 시점의 현재 팀장을 기준으로 처리한다고 하지만, People Platform에서 팀장 관계가 여러 명일 때, 겸직/대행/공석일 때, 직원 이동 시점과 요청 처리 시점이 경합할 때의 판정 기준이 없습니다.  
영향: 접근 권한이 인사 데이터의 순간 상태에 의존하므로, 경계 사례에서 이전 팀장과 새 팀장이 모두 접근하거나 모두 접근하지 못하는 문제가 생길 수 있습니다.  
수정 방향: “현재 팀장 관계”의 단일 진실 공급원, effective timestamp, 다중 팀장 허용 여부, 공석 처리, 캐시 허용 여부와 TTL 또는 캐시 금지 기준을 명시해야 합니다.

**Medium - 조회 실패와 데이터 노출 경계가 처리 명령보다 약합니다.**  
근거: `Authorization and data boundaries`는 인사 시스템 실패 시 “처리 요청”을 fail-closed 503으로 둡니다. 하지만 팀장 목록/상세 조회에서 People Platform이 실패할 때의 동작은 명시하지 않습니다. `Risks`는 휴가 사유를 직원 본인과 현재 팀장만 읽는다고 하지만, 감사자 조회 surface와 API 응답 필드 계약이 없습니다.  
영향: 조회 API가 오래된 팀장 캐시로 사유를 노출하거나, 인사 장애 중 상세 조회를 허용하는 구현이 가능해집니다. 감사자에게 request ID만으로 상세 리소스 접근 경로가 열리는지도 검증하기 어렵습니다.  
수정 방향: 조회도 fail-closed 대상인지 정의하고, role별 응답 필드 표를 추가해야 합니다. 감사 이벤트에는 사유 전문뿐 아니라 사유 요약, validation payload, raw request body도 금지한다고 명시하는 편이 안전합니다.

**Low - 날짜 정책의 경계값 검증이 일부 빠져 있습니다.**  
근거: `FR-101`은 KST 달력일, 시작/종료 순서, 사유 1~500자, PENDING/APPROVED 겹침 금지를 정의합니다. 그러나 과거일 신청 가능 여부, 최대 연속 휴가일, 종료일 포함 계산의 예시, KST 기준 변환 입력 형식은 없습니다.  
영향: 제품 정책 차이가 구현으로 흘러 들어가고, API 클라이언트가 UTC timestamp를 보내는 경우 날짜 밀림 버그를 만들 수 있습니다.  
수정 방향: 입력은 `YYYY-MM-DD` KST calendar date로 제한하는지, 과거일 허용 여부, 최대 기간 정책을 명시하고 AC에 경계값을 추가해야 합니다.

**Low - NFR의 성능 목표가 출시 전 결정으로만 남아 검증 가능성이 낮습니다.**  
근거: `Non-functional requirements`는 “API 지연 목표는 내부 베타 측정 후 제품 책임자가 정식 출시 전에 결정”이라고 합니다.  
영향: 현재 PRD만으로는 성능 acceptance가 없고, 출시 준비 시점에 별도 게이트가 없으면 결정 누락이 발생할 수 있습니다.  
수정 방향: 지금 수치를 invent할 필요는 없지만, Delivery나 open decision에 “정식 출시 전 latency SLO가 AC로 추가되어야 함”을 exit condition으로 묶어야 합니다.

검토는 제공된 PRD 원문만 대상으로 했고, 저장소 탐색이나 파일 생성은 하지 않았습니다.