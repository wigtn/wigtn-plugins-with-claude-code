**프로젝트 산출물 계약 감사**

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `Pages and routes`에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 주요 surface별 상태와 recovery 정의 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid lifecycle 정의 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `Acceptance criteria`가 `Requirement`, `Given`, `When`, `Then`, `Verification` 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Missing | PRD에 단계별 delivery phase, 각 phase의 FR 매핑, exit condition 없음 |

**Findings**

**High: Delivery phase 계약이 누락되어 출시 범위와 검증 게이트가 불명확함**  
근거: 산출물 계약상 `Delivery phases mapped to requirement IDs and exit conditions`가 필요하지만 PRD에 해당 섹션이 없다. 특히 `API 지연 목표는 내부 베타 측정 후 ... 결정`처럼 베타와 정식 출시가 언급되므로 phase 구분이 실제로 필요하다.  
영향: P0 기능 전체를 한 번에 구현해야 하는지, 베타에서 감사·권한·동시성까지 필수인지, 정식 출시 전 차단 조건이 무엇인지 검증할 수 없다.  
수정 방향: 예를 들어 `MVP/internal beta/GA` 같은 phase를 두고 각 phase에 `FR-101~FR-106`, 관련 AC, exit condition을 명시해야 한다. 지연 목표 결정도 GA exit condition으로 연결하는 편이 낫다.

**High: 직원 취소 기능의 acceptance coverage가 부족함**  
근거: 권한 표는 직원에게 `대기 취소`를 허용하고, `FR-102`와 user flow도 `PENDING -> CANCELLED`를 포함한다. 하지만 AC에는 직원 취소 성공, 비소유자 취소 거부, APPROVED/REJECTED/CANCELLED 재취소 거부가 없다.  
영향: 핵심 상태 전이 중 하나가 구현·테스트 계약에서 빠져 있어, 취소 권한이나 감사 이벤트 누락을 잡기 어렵다.  
수정 방향: `PENDING 본인 신청 취소 -> CANCELLED + 감사 이벤트`, `최종 상태 취소 시도 -> 409`, `타인 신청 취소 시도 -> 403 + 권한 거부 감사` AC를 추가한다.

**High: idempotency key의 범위와 재사용 규칙이 검증 불가능함**  
근거: `FR-106`은 모든 생성·상태 명령에 idempotency key를 요구하고, `AC-108`은 같은 key 재시도 시 같은 신청 ID와 중복 이벤트 없음만 검증한다. 그러나 key의 scope가 actor별인지 조직별인지 endpoint별인지, TTL, 같은 key로 다른 payload를 보냈을 때의 응답이 없다.  
영향: 중복 방지 구현이 서비스마다 달라질 수 있고, 잘못하면 한 사용자의 key가 다른 작업을 막거나, 다른 payload 재사용으로 의도치 않은 결과가 반환될 수 있다.  
수정 방향: key scope를 `organization + actor + command type + idempotency key`처럼 정의하고, 동일 key·동일 payload는 기존 결과 반환, 동일 key·상이 payload는 `409` 또는 `422`로 고정한다. 상태 명령에도 별도 AC가 필요하다.

**Medium: 권한 거부 감사 이벤트의 필드 의미가 모호함**  
근거: `FR-105`는 생성·승인·반려·취소와 권한 거부를 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 한다. 하지만 권한 거부는 신청을 조회할 권한이 없거나 존재 여부를 숨겨야 할 수 있어 `request ID`, `이전/이후 상태`를 항상 기록할 수 없다.  
영향: 보안상 숨겨야 할 리소스 존재를 감사 로그나 응답 처리 과정에서 드러낼 수 있고, 구현자가 거부 이벤트 스키마를 임의로 해석하게 된다.  
수정 방향: 권한 거부 이벤트는 `target request ID if known/authorized-safe`, `attempted action`, `decision=DENIED`, `reason code`, `before/after state=null or redacted`처럼 별도 필드 규칙을 둔다.

**Medium: 목록·상세별 데이터 노출 범위가 충분히 구분되지 않음**  
근거: 감사자는 휴가 사유 전문을 읽을 수 없고, 위험 완화에는 사유를 직원 본인과 현재 팀장만 읽는다고 되어 있다. 하지만 `/team/leave`, `/audit/leave`, `/leave/:id` 각각에서 어떤 필드가 노출되는지 명시되어 있지 않다.  
영향: 팀 승인함 목록이나 감사 이력에서 사유 전문, 조직/팀 이동 정보, 거부 사유 등이 과다 노출될 수 있다.  
수정 방향: surface별 response field policy를 추가한다. 예: 팀장 상세에는 휴가 사유 허용, 팀장 목록에는 최소 요약만, 감사 이력에는 사유 전문 금지 및 상태·행위·actor metadata만 허용.

**Medium: “현재 팀장” 판정 시점은 있으나 People Platform 장애·변경 중 경계조건이 덜 닫혀 있음**  
근거: `FR-103`은 승인 시점 현재 팀 직원만 처리한다고 하고, Authorization은 People Platform 실패 시 fail-closed 503이라고 한다. 그러나 조회와 처리 사이 팀 이동, People Platform 응답 지연/캐시, 멤버십 변경 직후 처리의 기준이 없다.  
영향: 이전 팀장이 조회한 상세 화면에서 처리 버튼을 누르는 race는 서버 검사로 막히겠지만, 캐시 사용 여부에 따라 결과가 달라질 수 있다.  
수정 방향: 처리 명령은 반드시 최신 People Platform 권한 확인을 사용한다고 명시하고, 캐시 허용 여부와 최대 staleness를 정한다. `AC-107`에 “이전 팀장이 기존 상세에서 처리 시 403/409” 케이스를 추가한다.

**Low: API 지연 목표가 NFR이 아니라 open decision에 가까움**  
근거: Non-functional requirements에 `API 지연 목표는 내부 베타 측정 후 제품 책임자가 정식 출시 전에 결정`이라고 되어 있어 현재 검증 가능한 기준이 아니다.  
영향: 성능 요구사항으로는 테스트·출시 판단에 사용할 수 없다.  
수정 방향: 지금은 `Open decisions`로 유지하고, delivery phase의 GA exit condition에 “latency SLO 확정 및 측정 대시보드 존재”처럼 검증 가능한 조건으로 둔다.

**Open Questions**

- 감사 이벤트에서 `request ID`는 휴가 신청 ID인지, HTTP/request correlation ID인지 불명확하다. 둘 다 필요하면 `leaveRequestId`와 `correlationId`로 분리하는 것이 좋다.
- 반려 사유는 휴가 사유와 별개의 민감 데이터로 보이는데, 감사자 열람 가능 여부가 명시되어 있지 않다.  
- 휴가 일수 계산에서 주말·공휴일을 포함한 “KST 달력일”인지, 단순 날짜 범위인지 현재 문장만으로는 대체로 단순 범위로 읽히지만 명시하면 구현 오해가 줄어든다.