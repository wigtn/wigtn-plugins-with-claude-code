**계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Missing | 어떤 산출물 계약이 이 PRD에 적용/N/A인지 별도 원장으로 선언한 섹션이 없음. 이 기능은 사용자 화면·상태·수명주기가 있어 계약 적용 대상임. |
| Pages and routes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의. |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 내 휴가, 신청 폼, 승인 상세의 상태별 UX 정의. |
| Mermaid user or system flow | Present | `User flow`에 Mermaid flowchart 있음. |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `Acceptance criteria`가 AC별 `Requirement`, `Given`, `When`, `Then`, `Verification` 포함. |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery`가 Phase별 Requirement IDs와 exit condition 포함. |

**Findings**

**High - 직원 취소가 기능 요구사항과 인수조건에서 충분히 검증되지 않음**

영향: 직원의 “대기 취소”는 역할 표, 상태 전이, 플로우, 감사 대상에 등장하지만 별도 FR/AC가 없어 구현자가 취소 권한·상태 조건·감사 이벤트·동시성 처리를 누락해도 PRD상 실패로 판정하기 어렵습니다.

근거: `Users, roles and permissions`는 직원에게 “대기 취소”를 허용하고, `FR-102`는 `PENDING -> CANCELLED`를 허용하며, `FR-105`는 취소 감사를 요구합니다. 하지만 `Acceptance criteria`에는 취소 성공/실패/권한/동시성 케이스가 없습니다. `FR-106`의 동시성 예시는 승인과 취소 동시 요청만 다루지만, 취소 자체의 actor 조건은 별도로 검증되지 않습니다.

수정 방향: 취소 전용 요구사항 또는 FR-104 하위 조건으로 “소유 직원만 본인 PENDING 신청을 CANCELLED로 전이 가능”을 명시하고, AC에 성공 취소, 이미 처리된 신청 취소 409, 타인 취소 403, 감사 이벤트 1건을 추가하세요.

**High - 감사 이벤트 스키마가 감사자 조회 요구와 보안 경계를 만족하기에 불충분함**

영향: 감사자는 조직 내 이벤트를 읽어야 하지만 이벤트 필드가 `actor`, `request ID`, `이전/이후 상태`, `timestamp`만으로 정의되어 있어 이벤트 종류, 조직 범위, 대상자, 실패 사유 범주, 거부된 작업 같은 핵심 감사 질의를 검증하기 어렵습니다. 반대로 `request ID`만으로 상세 API를 타고 휴가 사유에 접근할 수 있으면 감사자 금지사항과 충돌할 수 있습니다.

근거: `FR-105`는 생성·승인·반려·취소와 권한 거부를 기록한다고 하지만 공통 필드만 나열합니다. `Users, roles and permissions`는 감사자가 “조직 내 감사 이벤트 읽기”는 가능하나 “휴가 사유 전문 읽기”는 금지합니다. `Authorization and data boundaries`는 감사자용 상세 조회 차단이나 audit event redaction 경계를 별도로 명시하지 않습니다.

수정 방향: audit event에 최소 `event_type`, `organization_id`, `target_employee_id` 또는 제한된 subject reference, `outcome`, `denial_reason_code`, `request_id`를 명시하고, 감사자 API는 leave detail/reason을 역참조하지 못한다고 못박으세요. 감사 이벤트에는 반려 사유와 휴가 사유 전문이 모두 제외되는지도 분리해 명시하는 편이 안전합니다.

**Medium - 반려 사유와 휴가 사유의 개인정보 처리 경계가 서로 다르게 정의되지 않음**

영향: 휴가 사유 전문은 로그·감사 이벤트에서 제외한다고 되어 있지만, 반려 사유는 1~500자 요구만 있고 노출·감사·로그 제외 여부가 없습니다. 반려 사유도 개인정보나 민감한 설명을 포함할 수 있어 감사자 조회, 로그, 알림, 상세 화면에서 과노출될 수 있습니다.

근거: `FR-101`은 직원 사유를 정의하고, `FR-103`은 반려 사유를 정의합니다. `FR-105`는 “휴가 사유 전문은 기록하지 않는다”고만 하고, `Risks and mitigations`도 “휴가 사유”만 언급합니다.

수정 방향: “휴가 사유”와 “반려 사유”를 별도 데이터로 정의하고 각 필드의 조회 가능 역할, 감사 이벤트 포함 여부, 로그 마스킹 원칙을 명시하세요.

**Medium - 날짜·중복 판정의 시간대/경계 조건은 KST만으로는 검증이 모호함**

영향: “KST 달력일”은 방향이 맞지만 저장·비교 기준, 과거 날짜 허용 여부, 종료일 포함 overlap 로직, 조직별 휴일/주말 포함 여부가 불명확합니다. 특히 클라이언트가 다른 시간대에 있거나 서버가 UTC timestamp로 저장하면 하루 밀림 버그가 생길 수 있습니다.

근거: `FR-101`은 KST 달력일, 양끝 포함, 시작일<=종료일, PENDING·APPROVED와 겹침 금지를 요구합니다. 하지만 날짜 타입이 date-only인지, 과거 신청 가능 여부, 같은 시작/종료일 허용 여부, 주말 포함 정책은 없습니다.

수정 방향: 날짜는 KST 기준 `LocalDate` 또는 date-only로 저장/검증한다고 정의하고, overlap predicate를 “`new_start <= existing_end && existing_start <= new_end`”처럼 관찰 가능하게 명시하세요. 과거일·당일·주말 포함 정책도 결정 항목으로 분리하세요.

**Medium - idempotency key 범위와 응답 재현 규칙이 부족함**

영향: 같은 key 재시도는 AC-108에 있지만, key의 scope가 사용자별인지 조직별인지 endpoint별인지, payload가 다르면 409인지, key 보존 기간이 얼마인지가 없어 중복 신청 방지와 재시도 안정성을 일관되게 구현하기 어렵습니다.

근거: `FR-106`은 모든 생성·상태 명령에 idempotency key를 요구하고, `AC-108`은 신청 재시도만 검증합니다. 승인/반려/취소 명령의 idempotency 재시도 결과는 AC에 없습니다.

수정 방향: key scope를 `organization + actor + operation + key` 등으로 정의하고, 동일 key/동일 payload는 동일 결과 반환, 동일 key/다른 payload는 충돌, 보존 기간과 상태 명령 재시도 동작을 AC로 추가하세요.

**Low - API 지연 목표가 출시 전 결정으로 남아 있어 현재 PRD만으로는 비기능 검증이 불가능함**

영향: 베타 전 구현 범위에서는 성능 합격/불합격 기준이 없습니다. 출시 차단 조건이면 괜찮지만, 현재 산출물만으로는 테스트 설계가 불가능합니다.

근거: `Non-functional requirements`와 `Assumptions and open decisions` 모두 API 지연 목표를 나중에 제품 책임자가 결정한다고 둡니다.

수정 방향: 지금 수치를 정하지 않을 거라면 “현재 Phase exit에서는 성능 SLO 검증 제외, 출시 승인 전 별도 PRD 업데이트 필요”처럼 적용 범위를 명시하세요.

**Low - Delivery phase와 감사 원자성 요구의 순서가 어긋날 수 있음**

영향: `FR-106`은 상태와 감사 이벤트 원자성을 P0로 요구하지만, `Delivery`는 FR-105 감사를 Phase 3로 둡니다. Phase 2에서 상태 전이·동시성·멱등성을 완료한다고 해도 감사 원자성이 빠진 구현이 임시로 통과할 수 있습니다.

근거: `FR-106`은 “상태와 감사 이벤트는 같은 트랜잭션 또는 transactional outbox로 원자성 보장”을 요구합니다. `Delivery`는 Phase 2에 FR-106, Phase 3에 FR-105를 배치합니다.

수정 방향: Phase 2의 FR-106 exit condition을 “감사 이벤트 저장 인터페이스 포함”으로 제한하거나, FR-106의 감사 원자성 검증을 Phase 3로 명확히 이동하세요. 현재처럼 두 요구가 서로 다른 phase에 있으면 검증 책임이 흐려집니다.