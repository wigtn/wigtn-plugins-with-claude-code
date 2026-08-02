**산출물 계약 감사**

| Contract | 존재 | 적용성 판단 | 근거 | 보완 필요 |
|---|---:|---:|---|---|
| Pages/routes | 있음 | Required 맞음 | 직원 신청, 팀장 승인함, 상세, 감사 이력 화면이 정의됨 | 각 route별 권한 실패, 빈 상태, 감사자 데이터 노출 범위가 충분히 연결되지 않음 |
| State matrix | 있음 | Required 맞음 | 목록·폼·승인 상세의 Empty/Loading/Error/Success/Recovery가 있음 | `/audit/leave`, `/leave/:id`의 직원 상세, 403/404, 취소 후 상태 등 일부 surface 누락 |
| User flow | 있음 | Required 맞음 | 신청 → 검증 → PENDING → CANCELLED/APPROVED/REJECTED 흐름 있음 | 권한 거부, 팀 이동, 동시 처리, HR 장애, 멱등 재시도 흐름은 빠짐 |

**Findings**

**High — 권한 거부 감사 이벤트 요구가 데이터 노출과 충돌할 수 있음**

근거: FR-105는 “생성·승인·반려·취소와 권한 거부를 actor, request ID, 이전/이후 상태, timestamp로 기록”한다고 합니다. 하지만 권한 거부는 타 조직/타 팀/타인 신청 접근처럼 신청 존재 여부나 상태 자체를 노출하면 안 되는 상황을 포함합니다. 이때 `request ID`, 이전/이후 상태를 항상 기록하거나 조회 가능하게 만들면 감사자 또는 내부 로그 소비자가 존재하지 않아야 할 리소스 존재를 추론할 수 있습니다.

수정 방향: 감사 이벤트 스키마를 이벤트 유형별로 나누세요. 권한 거부는 `resource_id` nullable 또는 해시 처리, `previous_state`/`next_state` nullable, `denial_reason_code`, `actor`, `timestamp`, `correlation_id` 정도로 제한하는 식이 안전합니다. 감사자 조회 화면에서도 휴가 사유뿐 아니라 리소스 존재 추론 가능 필드를 어떻게 마스킹할지 명시해야 합니다.

**High — 멱등성 요구가 검증 가능할 만큼 구체적이지 않음**

근거: FR-106은 모든 생성·상태 명령이 idempotency key와 조건부 갱신을 사용한다고 하지만 key scope, TTL, 재시도 응답, payload mismatch 처리, 사용자/조직별 격리 기준이 없습니다. 같은 idempotency key가 다른 payload로 재사용되거나 다른 actor/조직에서 충돌할 때의 기대 동작도 불명확합니다.

수정 방향: `idempotency_key`는 `organization_id + actor_id + operation + key` 단위로 유일해야 하는지, 저장 기간, 동일 key/동일 payload 재요청 시 이전 결과 반환 여부, 동일 key/다른 payload 시 `409` 또는 `422` 반환 여부를 요구사항에 추가하세요.

**High — 상태 전이와 “최종 결정 번복 없음”은 명확하지만 승인 후 취소 불가 정책의 제품 영향이 열려 있음**

근거: Non-goals에 “최종 결정 번복”이 제외되어 있고 FR-102는 PENDING에서만 APPROVED/REJECTED/CANCELLED로 한 번 전이한다고 합니다. 따라서 APPROVED 휴가는 직원도 취소할 수 없습니다. 이는 정책일 수 있지만, 미래 휴가가 승인된 뒤 실제로 취소해야 하는 일반 업무 케이스가 완전히 배제됩니다.

수정 방향: 정말로 승인 후 취소가 범위 밖이면 “승인 후 취소·철회는 지원하지 않으며 운영 절차로 처리한다”처럼 명시하세요. 지원해야 한다면 상태 전이, 권한, 감사 이벤트, 중복 검사에서 APPROVED 취소 정책을 별도 요구사항으로 분리해야 합니다.

**Medium — 감사 이력 화면의 상태·권한·필터 계약이 부족함**

근거: Pages/routes에는 `/audit/leave`가 있으나 State matrix에는 감사 이력 surface가 없습니다. 감사자는 “조직 내 감사 이벤트 읽기”만 가능하다고 되어 있지만 검색 조건, pagination, 기간 제한, 권한 거부 이벤트의 노출 수준, 휴가 사유 전문 외 다른 개인정보 노출 기준이 없습니다.

수정 방향: 감사 이력의 Empty/Loading/Error/Success/Recovery를 추가하고, 필터 최소 단위인 기간, actor, event type, request ID 조회 가능 여부를 정의하세요. 감사자가 읽을 수 있는 필드 allowlist도 필요합니다.

**Medium — HR/People Platform 의존성이 처리 시점에만 선명하고 조회 시점에는 덜 선명함**

근거: FR-103, FR-104는 팀장이 “승인 시점” 현재 팀 직원 PENDING 신청만 처리한다고 합니다. Authorization 섹션은 People Platform 실패 시 처리 요청은 fail-closed 503이라고 합니다. 하지만 팀 승인함 목록 조회, 상세 조회, 직원 이동 직후 캐시 불일치, People Platform 장애 시 조회가 503인지 빈 목록인지가 정의되지 않았습니다.

수정 방향: “목록·상세·처리 모두 현재 People Platform 관계로 판단한다” 또는 “목록은 캐시 허용, 처리는 강검증”처럼 일관된 정책을 정하세요. 캐시를 허용한다면 최대 지연 시간과 처리 전 재검증을 명시해야 합니다.

**Medium — 날짜 규칙이 최소 검증만 있고 업무 달력 기준이 부족함**

근거: FR-101은 KST 달력일, 시작/종료 포함, 시작일 ≤ 종료일, PENDING/APPROVED 중복 금지만 정의합니다. 과거 날짜 신청, 당일 신청, 최대 연속 일수, 주말·공휴일 포함 여부, 조직 휴무일, REJECTED/CANCELLED와의 재신청 허용은 일부만 추론 가능합니다.

수정 방향: “캘린더 데이 기준으로 주말·공휴일도 기간에 포함한다” 또는 “영업일만 차감한다” 중 하나를 명시하세요. 과거/당일/미래 신청 제한과 최대 기간도 테스트 가능한 규칙으로 추가하는 편이 좋습니다.

**Medium — Delivery exit condition이 UI·상태 matrix·감사 화면까지 검증하지 않음**

근거: Delivery는 FR 중심 테스트만 있습니다. Pages/routes, State matrix, User flow 계약은 존재하지만 각 phase의 exit condition에는 route 접근 제어, 화면 상태, 오류 복구, 입력 유지, 감사 이력 조회 검증이 직접 연결되지 않습니다.

수정 방향: Delivery에 route 권한 테스트, 주요 화면 상태 테스트, 403/409/503 recovery 테스트, 감사 이력 필드 마스킹 테스트를 추가하세요. 산출물 계약이 구현 검증까지 이어져야 합니다.

**Low — 지연 목표가 open decision으로 남아 있어 출시 기준으로는 검증 불가능함**

근거: NFR과 Assumptions 모두 API 지연 목표를 내부 베타 후 제품 책임자가 결정한다고 합니다. 현재 PRD 단계에서는 허용 가능하지만, 정식 출시 PRD의 exit condition으로는 측정 기준이 없습니다.

수정 방향: 베타 단계에서는 “측정만 수행”으로 두고, GA 이전 gate로 `p95`, 대상 API, 측정 기간, 제외 조건을 결정해야 한다고 명시하세요.

**Low — 반려 사유의 공개 범위가 명시되지 않음**

근거: FR-103은 반려 사유 1~500자만 정의합니다. 휴가 사유는 직원 본인과 현재 팀장만 읽는다고 되어 있지만, 반려 사유를 직원, 팀장, 감사자가 각각 볼 수 있는지 명확하지 않습니다.

수정 방향: 반려 사유의 작성자, 열람자, 감사 이벤트 포함 여부를 명시하세요. 감사 이벤트에는 전문을 넣지 않는 정책이 반려 사유에도 적용되는지 분리해서 적는 것이 좋습니다.