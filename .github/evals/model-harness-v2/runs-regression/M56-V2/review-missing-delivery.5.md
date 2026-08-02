## 산출물 계약 감사

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability`가 존재하며 화면·상태·흐름을 Required로 판정했다. 다만 delivery phases의 적용성 판정은 빠져 있다. |
| Pages and routes | Present | 4개 화면의 경로·역할·주요 행동이 정의돼 있다. |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`가 존재한다. 단, 실제 화면 전체를 포괄하지 않는 문제는 아래 finding에 포함했다. |
| Mermaid user or system flow | Present | 신청 검증부터 취소·승인·반려까지의 상태 흐름이 Mermaid로 제공된다. |
| Acceptance precondition/action/result mapped to requirement IDs | Present | AC-101~108이 FR ID와 Given/When/Then/Verification을 포함한다. |
| Delivery phases mapped to requirement IDs and exit conditions | Missing | 단계별 범위, 연결된 FR ID, 진입·종료 조건이 없고 `Applicability`에서도 Required/N/A 판정하지 않았다. |

## Findings

| 영향도 | Finding | 영향·근거 | 수정 방향 |
|---|---|---|---|
| **blocker** | 동시 생성 시 기간 중복 금지를 보장할 수 없다 | FR-101은 PENDING·APPROVED 기간과의 중복을 금지하지만, FR-106의 “조건부 갱신”은 동일 신청의 상태 경쟁만 해결한다. 서로 다른 두 신청을 동시에 생성하면 둘 다 사전 중복 검사를 통과하는 write-skew가 가능하다. AC-102도 순차 충돌만 검증한다. | 직원별 기간 불변식을 DB 배타 제약, 직렬화 트랜잭션, 직원 단위 잠금 등으로 원자적으로 보장한다고 명시하고, 동시 중복 생성 중 정확히 한 건만 성공하는 AC를 추가한다. |
| **high** | 현재 팀 권한 판정과 상태 갱신 사이의 일관성 계약이 없다 | FR-103·104는 “승인 시점 현재 팀”을 요구하지만 People Platform 조회 후 상태 갱신 전에 팀 이동이 발생할 수 있다. 오래된 캐시 사용 가능 여부와 권한 판정의 유효 시점도 없다. 이전 팀장이 이동 직후 처리할 가능성이 남아 보안 경계를 검증할 수 없다. | 팀 정보 버전 또는 조회 시각을 상태 명령에 결부하고 커밋 직전 재검증하는 등 권한 판정의 원자성·신선도 기준을 정한다. 캐시 허용 여부, timeout, stale 응답, 조직 이동 시 동작도 명시한다. 해당 경쟁조건 테스트를 추가한다. |
| **high** | P0 요구사항 상당수가 acceptance coverage 없이 남아 있다 | AC에는 취소 성공·불법 상태 전이·승인/반려/취소의 멱등성·People Platform 503·전체 감사 필드·감사자 권한·사유 비노출 검증이 없다. FR-105는 생성·승인·반려·취소와 권한 거부를 모두 요구하지만 현재 AC는 일부 이벤트의 “한 건” 존재만 확인한다. | FR별 positive/negative AC를 보충하고 actor, request ID, 이전/이후 상태, timestamp, 민감정보 부재까지 관찰 가능한 assertion으로 만든다. 특히 모든 상태 명령의 멱등 재시도와 장애 주입 결과를 포함한다. |
| **high** | 멱등성의 식별·충돌 의미가 정의되지 않았다 | FR-106은 모든 명령에 idempotency key를 요구하지만 AC-108은 신청만 다룬다. 키 범위, 보존 기간, 동일 키에 다른 payload가 온 경우, 최초 요청 처리 중 재시도, 실패 응답 재생 여부가 없다. 구현마다 중복 처리나 잘못된 응답 재사용이 달라질 수 있다. | 키의 주체·조직·명령별 scope, payload fingerprint, TTL, concurrent replay, 키 재사용 오류 코드와 어떤 결과를 저장·재생할지 정의한다. 승인·반려·취소 각각의 AC를 둔다. |
| **high** | 휴가 사유와 처리 사유의 읽기 경계가 불완전하다 | `/leave/:id`는 “현재 팀장”에게 허용되고 위험 절에는 휴가 사유를 현재 팀장이 읽는다고 하지만, 최종 처리 후에도 읽을 수 있는지, 팀 이동 후 새 팀장이 과거 최종 건까지 읽는지 명확하지 않다. 반려 사유의 열람 주체와 감사 이벤트 포함 여부도 정의되지 않았다. 불필요한 민감정보 노출 가능성이 있다. | PENDING/최종 상태 및 팀 이동 전후에 따른 신청 사유·반려 사유의 필드별 열람 정책을 명시한다. 목록 응답에는 필요한 최소 필드만 제공하고, 권한별 직렬화 및 필드 비노출 테스트를 추가한다. |
| **medium** | 감사 기록이 “감사 가능”하다는 운영 계약이 부족하다 | FR-105는 이벤트 생성 필드만 정의한다. 변경 불가능성, 보존·삭제 정책, 정렬·페이지네이션, 중복 식별자, 접근 기록이 없다. 권한 거부 이벤트의 이전/이후 상태가 null인지 동일 값인지도 불명확하다. `/audit/leave`의 성공·실패 상태 역시 state matrix에 없다. | 이벤트 ID·event type·outcome·reason code와 nullable 상태 규칙을 정하고, append-only/변조 방지 및 보존 정책을 제품 요구 수준에서 명시한다. 감사 조회의 조직 경계, 필터, 페이지네이션 및 감사 조회 자체의 접근 기록 여부를 결정한다. |
| **medium** | 권한 거부 감사와 fail-closed 동작의 실패 의미가 없다 | FR-105는 권한 거부 기록을 요구하지만, 감사 저장이 실패하면 403을 반환할지 5xx로 명령 전체를 실패시킬지 정의하지 않는다. 권한 확인을 위해 존재 여부를 먼저 드러내면 타 조직 ID 열거 시 403/404 차이로 정보가 노출될 수도 있다. | 거부 이벤트 기록 실패 정책과 outbox 적용 범위를 정한다. 비인가·타 조직·존재하지 않는 ID의 외부 응답 정책을 통일하고, 상태·응답 본문·타이밍에서 자원 존재가 노출되지 않는지 테스트한다. |
| **medium** | State matrix가 선언된 화면을 모두 다루지 않는다 | matrix는 `내 휴가`, `신청 폼`, `승인 상세`만 포함한다. Pages/routes에 있는 `팀 승인함`, `감사 이력`, 일반 `휴가 상세`의 empty/loading/error/success/recovery가 없다. 팀 이동으로 접근을 잃은 경우와 People Platform 503 복구도 표현되지 않는다. | 각 route를 matrix의 surface와 1:1로 추적하고 403·404·409·503, 빈 목록, 접근 상실, 재시도 및 입력 보존 행동을 채운다. |
| **medium** | 사용자 흐름이 핵심 분기 일부를 감춘다 | Mermaid 흐름에는 팀 이동, 권한 거부, 중복 요청, 동시 명령 패배, 인사 시스템 장애가 없다. 이들은 모두 P0 요구나 명시적 복구 동작에 영향을 준다. | 정상 상태 생명주기는 유지하되, 처리 명령의 권한 재평가·409 경쟁 패배·503 복구를 별도 subflow로 추가해 FR/AC와 연결한다. |
| **medium** | 입력 길이와 날짜 검증의 관찰 가능한 규칙이 부족하다 | FR-101·103의 1~500자가 byte/code point/grapheme 중 무엇인지, 공백만 있는 입력과 Unicode 정규화가 유효한지 없다. KST 달력일이라고 했지만 API 표현 형식과 timestamp를 날짜로 변환하는지 여부도 없다. 클라이언트마다 다른 검증 결과가 날 수 있다. | API가 `YYYY-MM-DD` 날짜만 받는지 정하고, 길이 단위·trim·공백 입력·Unicode 처리와 오류 필드/코드를 명시한다. 경계값 및 DST와 무관한 KST 날짜 테스트를 추가한다. |
| **medium** | Delivery phases 계약이 누락됐다 | 정식 출시 전 지연 목표를 결정한다고 했지만 어떤 단계가 이를 막는지, P0 전체가 언제 완료되는지, exit condition이 없다. 따라서 미결정 성능 목표를 가진 채 출시 가능 여부를 판정할 수 없다. | 최소한 beta와 release 단계별 FR 범위 및 테스트·성능 목표 결정 같은 exit condition을 작성한다. 적용하지 않을 사유가 있다면 Applicability에서 N/A 근거를 남긴다. |
| **low** | 성능 목표 결정 시점이 두 표현으로 나뉜다 | NFR은 “정식 출시 전”, open decision은 “내부 베타 종료일까지”라고 한다. 베타 종료와 출시 간 관계가 명시되지 않아 실질 deadline이 모호하다. 목표 수치 자체를 지금 임의로 정할 필요는 없다. | 하나의 책임자·결정일·측정 데이터·승인 기준으로 통일하고 delivery phase의 exit condition에 연결한다. |

가장 먼저 막아야 할 것은 동시 중복 신청 불변식과 팀 권한 판정의 경쟁조건입니다. 둘 다 현재 문서대로 구현하면 테스트가 통과하더라도 실제 운영에서 P0 데이터·권한 규칙을 위반할 수 있습니다.

검토 범위는 제공된 PRD 본문뿐이며, 요청에 따라 저장소 탐색·파일 생성·문서 재작성·validator 실행은 하지 않았습니다.