**산출물 계약 감사**

| Contract | 존재 여부 | 적용성 판단 | 근거 | 감사 결과 |
|---|---:|---|---|---|
| Pages/routes | 있음 | Required가 맞음 | `Pages and routes`에 직원 신청, 상세, 팀 승인함, 감사 이력 route가 있음 | 대체로 충족. 다만 각 route의 빈 목록, 권한 거부, 로딩, 오류 상태는 별도 상태 계약에 의존함 |
| State matrix | 없음 | Required가 맞음 | Applicability에서 Required라고 선언했지만 실제 상태 행렬은 없음 | 미충족. 목록·폼·처리·감사 화면의 가시 상태와 명령 가능 여부를 검증할 기준이 없음 |
| User flow | 있음 | Required가 맞음 | 신청 → 검증 → PENDING → 취소/승인/반려 흐름이 있음 | 부분 충족. 정상 생명주기는 보이나 조회 권한, 팀 이동, 멱등 재시도, 동시성 실패, HR 장애 흐름은 빠져 있음 |

**Findings**

| 영향도 | 문제 | 근거 | 수정 방향 |
|---|---|---|---|
| High | `State matrix`가 Required인데 실제 행렬이 없어 UI·API 상태 검증이 불가능함 | Applicability는 “목록·폼·처리의 사용자 가시 상태”가 있다고 하지만, 본문에는 상태별 화면/버튼/오류/빈 상태/권한 거부 상태가 없음 | 최소한 role x page x request status x system state 기준으로 `볼 수 있는 데이터`, `가능한 action`, `비활성/숨김 처리`, `오류 표시`, `재시도 가능성`을 표로 추가해야 함 |
| High | 멱등성 계약이 불완전해 구현마다 다른 보안·정합성 결과가 나올 수 있음 | FR-106은 “모든 생성·상태 명령은 idempotency key”라고 하지만 AC-108은 신청만 검증함. 같은 key로 다른 payload, 다른 actor, 다른 endpoint, 다른 조직에서 재사용될 때의 응답이 없음 | idempotency key scope를 `actor + org + endpoint + command type` 등으로 명시하고, 동일 key/동일 payload 재시도와 동일 key/다른 payload 재사용의 결과를 구분해야 함. 승인·반려·취소 재시도 AC도 추가 필요 |
| High | 겹침 방지의 동시 생성 시나리오가 검증되지 않음 | FR-101은 PENDING·APPROVED와 겹칠 수 없다고 하고 FR-106은 조건부 갱신을 말하지만, AC에는 동시에 겹치는 휴가 2건을 생성하는 테스트가 없음 | 동일 직원의 겹치는 기간에 대해 동시 신청 시 하나만 PENDING이 되고 다른 하나는 409가 되는 AC를 추가해야 함. DB 제약, range lock, serializable transaction 등 구현 제약도 결정 필요 |
| High | 휴가 사유 전문에 대한 접근·마스킹 정책이 route와 감사 요구에서 충분히 분리되지 않음 | 감사자는 “휴가 사유 전문 읽기”가 금지되어 있고, Risk에는 직원 본인과 현재 팀장만 읽는다고 되어 있음. 하지만 `/leave/:id` 상세가 소유 직원·현재 팀장에게 허용된다는 것 외에 응답 필드별 경계가 없음 | 상세 응답을 role별 필드 계약으로 분리해야 함. 감사 이력에는 reason 원문 금지뿐 아니라 request summary, rejection reason, idempotency key, denial target 식별자 등 민감 필드 마스킹 규칙도 명시 필요 |
| Medium | 취소 기능이 요구사항에는 있으나 acceptance coverage가 없음 | FR-102는 PENDING에서 CANCELLED 전이를 허용하고, 직원 권한에도 “대기 취소”가 있으나 AC에는 취소 성공/실패/감사 이벤트 검증이 없음 | PENDING 취소 성공, APPROVED/REJECTED/CANCELLED 취소 실패, 타인 취소 403, 취소 감사 이벤트를 AC로 추가해야 함 |
| Medium | 반려 사유와 휴가 신청 사유의 저장·노출 정책이 불균형함 | FR-103은 반려 사유 1~500자를 요구하지만, FR-105의 “휴가 사유 전문은 기록하지 않는다”는 휴가 사유만 언급함. 반려 사유가 감사 이벤트나 로그에 들어가도 되는지 불명확함 | `leave reason`과 `rejection reason` 각각에 대해 저장 위치, 감사 이벤트 포함 여부, 로그 포함 여부, 조회 가능 role을 명시해야 함 |
| Medium | People Platform 장애 시나리오가 처리 요청에만 명시되어 조회·목록·신청 시점에는 불명확함 | Authorization에는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”이라고 되어 있음. 팀 승인함 조회, 상세 조회, 신청 생성 시 현재 조직/팀 확인 실패는 별도 정의가 없음 | HR 의존 작업별 장애 응답을 정해야 함. 예: 팀장 목록/상세/처리 모두 503 fail-closed, 직원 본인 조회는 세션 소유권만으로 허용 가능한지 여부 결정 |
| Medium | “현재 팀장” 기준은 정했지만 팀 이동과 기존 승인 이력의 조회 경계가 더 필요함 | FR-104와 AC-107은 이동 후 새 팀장이 PENDING 신청을 처리하고 이전 팀장은 접근을 잃는다고 함. 이미 APPROVED/REJECTED 된 과거 신청을 이전 팀장이 계속 볼 수 있는지, 새 팀장이 볼 수 있는지 불명확함 | 상태별로 팀 이동 후 조회 권한을 분리해야 함. 특히 PENDING 처리 권한과 과거 결정 조회 권한을 같은 규칙으로 둘지 결정 필요 |
| Medium | “일 단위 KST 달력일”은 명확하지만 휴일·주말·잔여 휴가·최대 기간 정책이 빠져 도메인 검증 범위가 모호함 | Non-goals에 급여 연동은 제외되어 있으나, 잔여 휴가 검증 자체가 제외인지 포함인지 불명확함. FR-101은 기간 유효성과 겹침만 다룸 | 잔여 휴가/휴일/주말/최대 연속일 검증을 명시적으로 Non-goal 또는 Requirement로 분류해야 함 |
| Low | 감사 이벤트의 실패/거부 이벤트 기준이 좁게 정의되어 있음 | FR-105는 생성·승인·반려·취소와 권한 거부를 기록한다고 함. 유효성 실패, 충돌 409, HR 503, 멱등 replay는 감사 대상인지 불명확함 | 감사 이벤트 taxonomy를 추가해 `success state change`, `authorization denied`, `validation rejected`, `conflict`, `dependency failure`, `idempotent replay` 기록 여부를 구분해야 함 |
| Low | API 지연 목표가 출시 전 결정으로 남아 있어 현재 단계에서는 검증 불가능함 | NFR과 Open decisions에 “내부 베타 후 결정”이라고 되어 있음 | 현재 PRD 기준에서는 의도적으로 미정인 항목으로 볼 수 있음. 다만 정식 출시 gate라면 owner, 결정일, 측정 방식, 최소 임시 기준을 추가하는 편이 안전함 |

요약하면 핵심 생명주기와 권한 방향은 잡혀 있지만, 계약상 Required인 `State matrix`가 실제로 없고, 멱등성·동시성·민감 필드·People Platform 장애 범위가 구현 가능한 수준까지 닫히지 않았습니다. 특히 `FR-106`은 좋은 방향의 요구사항이지만 AC가 신청 재시도 하나에만 묶여 있어 승인/반려/취소와 충돌 생성까지 검증 범위를 넓혀야 합니다.