**산출물 계약 감사**

| Contract | Applicable? | Status | Evidence | Audit |
|---|---:|---|---|---|
| Applicability ledger | Yes | Present | `## Applicability` 표 | 계약별 Required 판단은 있음 |
| Pages and routes | Yes | Missing | Applicability에는 “직원 신청과 팀장 처리 화면”만 있음 | 실제 페이지/라우트 목록, 진입 조건, 화면별 권한이 없음 |
| Empty/loading/error/success/recovery state matrix | Yes | Present | `## State matrix` | 주요 surface는 있으나 감사자 surface는 없음 |
| Mermaid user or system flow | Yes | Present | `## User flow` mermaid | 신청-결정 생명주기는 표현됨 |
| Acceptance precondition/action/result mapped to requirement IDs | Yes | Present | `AC-101`~`AC-108` | 일부 요구사항은 미검증 상태로 남음 |
| Delivery phases mapped to requirement IDs and exit conditions | Yes | Present | `## Delivery` | 단계별 ID와 exit condition 있음 |

**Findings**

**High - 페이지/라우트 계약이 Required인데 실제 산출물이 없다.**  
근거: Applicability에서 `Pages/routes`를 Required로 선언했지만, PRD 본문에는 직원 신청 화면, 내 휴가 목록/상세, 팀장 승인 상세, 감사자 감사 이벤트 조회 등 페이지/라우트 단위 정의가 없다.  
영향: 구현자가 라우팅, 접근 제어, 화면별 데이터 노출 범위를 임의 해석하게 된다. 특히 감사자 역할과 팀장 조회 권한은 UI 진입점이 명확하지 않아 보안 테스트도 빠질 수 있다.  
수정 방향: 최소한 화면/route, 접근 가능 role, 주요 데이터, 금지 데이터, 연결 FR/AC를 표로 추가해야 한다.

**High - 직원 취소 흐름이 요구사항에는 암시되지만 acceptance coverage가 없다.**  
근거: 권한 표는 “대기 취소”를 허용하고, `FR-102`는 `PENDING -> CANCELLED`를 허용하며, user flow에도 “직원 취소”가 있다. 그러나 AC에는 취소 성공, 타인 취소 거부, 이미 승인/반려된 신청 취소 실패, 취소 감사 이벤트 검증이 없다.  
영향: 취소가 구현되지 않거나, 구현되어도 권한/상태/감사/동시성 보장이 빠질 수 있다. 승인과 취소 동시성은 `AC-106`에 있지만 정상 취소 자체의 계약은 없다.  
수정 방향: `FR-10x`로 직원 취소 명령을 명시하고, `PENDING` 본인 신청만 취소 가능, 성공 시 `CANCELLED`, 감사 이벤트 1건, 비대기 상태는 `409`, 타인 신청은 `403` 같은 AC를 추가한다.

**High - 감사 이벤트의 조직 경계가 필드 수준에서 성립하지 않는다.**  
근거: `FR-105`는 감사 이벤트를 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고만 한다. 반면 감사자는 “조직 내 감사 이벤트 읽기”가 가능하고, authorization에는 조직 ID를 세션에서 결정한다고 되어 있다.  
영향: 감사 이벤트에 `organization ID` 또는 동등한 tenant boundary key가 없으면 조직별 조회와 격리를 안정적으로 검증할 수 없다. 멀티테넌트 환경에서는 보안 결함으로 이어질 수 있다.  
수정 방향: 감사 이벤트 필수 필드에 `organization ID`, 대상 신청 ID, action type, result/success-denied, actor role 정도를 명시하고, 감사자 조회는 세션 조직으로 서버 필터링한다고 AC로 검증한다.

**High - idempotency key 범위와 재사용 의미가 불명확하다.**  
근거: `FR-106`은 모든 생성·상태 명령이 idempotency key를 사용한다고 하지만, key가 actor/org/operation/resource/body 중 무엇에 귀속되는지 없다. `AC-108`도 신청 재시도만 검증한다.  
영향: 같은 key를 다른 사용자, 다른 조직, 다른 명령, 다른 payload에 재사용했을 때 중복 처리·오처리·정보 노출 가능성이 있다. 상태 명령 승인/반려/취소의 멱등성도 검증되지 않는다.  
수정 방향: idempotency scope를 `organization + actor + operation + target resource(optional)`로 정의하고, 같은 key에 다른 payload가 오면 `409` 또는 명시 오류를 반환하게 한다. 승인/반려/취소 재시도 AC도 추가한다.

**Medium - 반려 사유의 저장·노출·감사 처리 경계가 부족하다.**  
근거: `FR-103`은 반려 사유 1~500자를 요구하지만, data boundary와 risks는 “휴가 사유”만 다룬다. 반려 사유를 누가 읽을 수 있는지, 감사자에게 노출되는지, 로그 제외 대상인지 명확하지 않다.  
영향: 반려 사유에 민감정보가 들어갈 수 있는데 감사자나 로그에 노출될 수 있다.  
수정 방향: 반려 사유를 휴가 사유와 같은 민감 텍스트로 취급할지 결정하고, 읽기 권한 및 감사/로그 제외 여부를 명시한다.

**Medium - 권한 거부 감사 이벤트의 shape가 모순적이다.**  
근거: `FR-105`는 권한 거부도 `이전/이후 상태`와 함께 기록한다고 한다. 하지만 권한 거부에서는 신청이 존재하지 않거나, 존재해도 actor에게 상태를 노출하면 안 되는 경우가 있다.  
영향: 거부 감사 기록을 만들기 위해 대상 상태를 조회하거나 기록하다가 존재 여부·상태 정보가 새어 나갈 수 있다.  
수정 방향: 거부 이벤트는 `action, actor, target reference if safe, denial reason category, timestamp, request ID`처럼 별도 shape를 허용하고, 민감한 대상 상태는 권한 확인 후에만 기록한다고 명시한다.

**Medium - People Platform 장애 처리 범위가 처리 요청에만 묶여 있다.**  
근거: Authorization에는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고 되어 있다. 그러나 목록/상세 조회, 팀 이동 후 접근 회수, 팀장 조회에도 현재 팀 관계 확인이 필요하다.  
영향: 조회 경로에서 People Platform 실패 시 이전 팀장이 계속 접근하거나, 팀장 화면이 부정확한 데이터를 보여줄 수 있다.  
수정 방향: 현재 팀 관계가 필요한 모든 조회·처리 작업의 장애 정책을 명시한다. 예: 팀장 목록/상세/처리는 fail-closed, 직원 본인 조회는 People Platform 비의존 등.

**Medium - 감사자 role이 기능 요구사항과 acceptance에서 빠져 있다.**  
근거: Users table에는 감사자가 있지만 FR/AC에는 감사 이벤트 조회 요구사항, 휴가 사유 전문 비노출 검증, 조직 경계 검증이 없다.  
영향: 감사자 권한이 선언만 되고 구현·테스트 계약이 없다.  
수정 방향: 감사자 조회 FR과 AC를 추가한다. 조직 내 이벤트만 조회, 휴가 사유/반려 사유 전문 미노출, 상태 변경 불가를 검증해야 한다.

**Low - API 지연 목표가 출시 전 결정으로만 남아 있어 현재 PRD에서는 검증 불가능하다.**  
근거: NFR에 “내부 베타 측정 후 제품 책임자가 정식 출시 전에 결정”이라고 되어 있다.  
영향: 현 단계에서는 성능 acceptance가 없다. 다만 open decision으로 관리되고 있어 즉시 blocker는 아니다.  
수정 방향: 베타 종료 시점의 의사결정 산출물과 출시 gate를 Delivery 또는 AC에 연결한다.

검증은 사용자가 제공한 PRD 본문만 기준으로 수행했습니다. 저장소 탐색이나 파일 생성은 하지 않았습니다.