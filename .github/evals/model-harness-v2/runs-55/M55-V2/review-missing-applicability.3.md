**프로젝트 산출물 계약 감사**

| Contract | 적용성 | Status | Evidence |
|---|---:|---|---|
| Applicability ledger | 적용 | Missing | 이 PRD가 어떤 산출물 계약을 적용/N/A로 판단했는지 별도 ledger가 없음 |
| Pages and routes | 적용 | Present | `Pages and routes` 섹션 존재 |
| Empty/loading/error/success/recovery state matrix | 적용 | Present | `State matrix` 섹션 존재 |
| Mermaid user or system flow | 적용 | Present | `User flow` Mermaid 존재 |
| Acceptance precondition/action/result mapped to requirement IDs | 적용 | Present | AC-101~108이 FR ID와 Given/When/Then/Verification 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | 적용 | Present | `Delivery` 섹션이 Phase별 Requirement IDs와 exit condition 포함 |

**Findings**

**High: 권한 거부 감사 이벤트의 필수 필드가 정의와 충돌합니다.**  
영향도: FR-105는 권한 거부도 `이전/이후 상태`와 함께 기록한다고 하지만, 권한 거부는 리소스가 없거나 조회 권한이 없어 상태를 노출하면 안 되는 경우가 있습니다. 잘못 구현하면 감사 이벤트가 존재하지 않는 신청의 상태를 기록하거나, 403 응답 경로에서 민감한 상태 존재 여부를 누출할 수 있습니다.  
근거: FR-105 “생성·승인·반려·취소와 권한 거부를 actor, request ID, 이전/이후 상태…” / AC-105 “403, 상태 불변, 권한 거부 감사”  
수정 방향: 권한 거부 감사 이벤트 스키마를 별도로 정의하세요. 예: `actor`, `request ID`, `attempted action`, `resource type`, `resource ID if safely known`, `reason category`, `timestamp`; 상태 필드는 “권한 확인 후 안전하게 확인 가능한 경우만” 또는 `null` 허용으로 명시해야 합니다.

**High: 감사자의 데이터 경계가 검증 가능하지 않습니다.**  
영향도: 감사자는 “휴가 사유 전문 읽기 금지”인데, 감사 이벤트에 어떤 필드가 포함되는지 충분히 좁혀져 있지 않아 사유가 request payload, rejection reason, error detail, metadata, search index, export에 섞일 수 있습니다. 특히 반려 사유는 1~500자로 받지만 감사자 열람 가능 여부가 불명확합니다.  
근거: 역할 표 “감사자: 휴가 사유 전문 읽기 금지” / FR-103 “반려 사유는 1~500자” / FR-105 “휴가 사유 전문은 기록하지 않는다” / Risks “휴가 사유는 직원 본인과 현재 팀장만 읽으며 로그·감사 이벤트에 넣지 않는다”  
수정 방향: “휴가 사유”와 “반려 사유”를 분리해서 민감도와 열람권한을 명시하세요. 감사 이벤트 payload allowlist를 정의하고, 감사자 API/화면/내보내기에서 사유류 필드가 빠지는 AC를 추가해야 합니다.

**Medium: 조회 권한과 처리 권한의 범위가 섞여 있어 최종 상태 신청 접근이 모호합니다.**  
영향도: 현재 팀장이 `PENDING`만 처리한다는 것은 명확하지만, `APPROVED/REJECTED/CANCELLED` 상세 조회 가능 여부가 불분명합니다. 구현마다 “현재 팀장 전체 조회 가능” 또는 “PENDING만 조회 가능”으로 갈릴 수 있고, 직원 이동 후 이전 팀장의 과거 승인 건 열람 권한도 달라집니다.  
근거: FR-103 “현재 팀 직원 PENDING 신청만 처리” / FR-104 “직원 이동 후에는 새 팀장이 PENDING 신청을 처리하고 이전 팀장은 접근을 잃는다” / Pages `/leave/:id` “소유 직원, 현재 팀장”  
수정 방향: 조회와 처리 권한을 분리하세요. 예: 현재 팀장은 현재 팀 직원의 모든 상태를 조회 가능한지, 대기 건만 조회 가능한지, 과거 팀장은 자신이 처리한 과거 이벤트를 볼 수 있는지 명시해야 합니다.

**Medium: 멱등성 키 범위와 재사용 규칙이 부족합니다.**  
영향도: 같은 idempotency key가 사용자/조직/엔드포인트/요청 본문 간에 어떻게 스코프되는지 없으면 중복 신청 방지는 되더라도 다른 사용자의 요청 충돌, 서로 다른 payload 재시도 처리, 승인/취소 명령 재시도 처리에서 보안·정합성 문제가 생길 수 있습니다.  
근거: FR-106 “모든 생성·상태 명령은 idempotency key…” / AC-108은 신청 재시도만 검증  
수정 방향: 키 scope를 `organization + actor + operation + key` 등으로 정의하고, 동일 키에 다른 payload가 오면 409 또는 422로 처리하는 규칙을 넣으세요. 승인·반려·취소 재시도 AC도 추가하는 편이 안전합니다.

**Medium: 날짜 경계 조건이 일부 검증 불가능합니다.**  
영향도: “KST 달력일”은 있지만 신청 가능한 과거/당일/미래 범위, 최대 휴가 기간, 종료일 상한, 조직 휴무일/주말 포함 여부가 없습니다. 구현자는 10년짜리 신청이나 과거 신청을 허용할지 임의 결정하게 됩니다.  
근거: FR-101 “KST 달력일의 시작일·종료일… 날짜는 양끝을 포함”  
수정 방향: 최소한 과거일 허용 여부, 최대 연속 일수, 주말/공휴일 포함 계산 여부, 날짜 저장 기준을 명시하세요. 비즈니스에서 아직 미결이면 open decision으로 올려야 합니다.

**Low: NFR의 API 지연 목표가 출시 전 결정이라 현재 acceptance로 검증할 수 없습니다.**  
영향도: 내부 베타 전까지는 괜찮지만, 이 PRD만으로는 성능 완료 기준이 없습니다. Delivery exit condition에도 성능 기준이 없어 정식 출시 gate에서 누락될 수 있습니다.  
근거: Non-functional requirements “API 지연 목표는 내부 베타 측정 후…” / Assumptions and open decisions 동일  
수정 방향: 현재는 “미정”으로 유지하되, 출시 전 blocking decision으로 owner/date/측정 지표를 명시하세요. 예: p95 기준, 측정 API, 베타 종료일.

**Open Questions**

- 팀장은 현재 팀 직원의 최종 상태 신청과 사유를 계속 조회할 수 있나요, 아니면 PENDING 처리 대상만 볼 수 있나요?
- 반려 사유는 감사자가 볼 수 있는 운영상 사유인가요, 아니면 휴가 사유와 같은 민감정보로 취급하나요?
- 과거일 신청, 최대 기간, 주말/공휴일 포함 정책은 의도적으로 제외된 범위인가요?