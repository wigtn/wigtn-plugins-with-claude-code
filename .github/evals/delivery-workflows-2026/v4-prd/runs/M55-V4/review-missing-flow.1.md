**Contract Audit**
| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow 적용성을 선언함 |
| Pages and routes | Present | `Pages and routes` 표에 `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 있음 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix` 표가 있음 |
| Mermaid user or system flow | Missing | 다단계 생명주기라고 선언했지만 Mermaid user/system flow 산출물은 없음 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `Acceptance criteria`가 `Requirement`, `Given`, `When`, `Then`, `Verification`을 포함함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | `Delivery` 표가 phase별 requirement IDs와 exit condition을 포함함 |

**Findings**

1. **Medium: 적용 선언된 user flow 산출물이 누락됨**
근거: `Applicability`에서 `User flow`를 Required로 선언했고, 신청부터 최종 결정까지 다단계 생명주기라고 설명하지만, 검토 계약상 요구되는 Mermaid user/system flow가 없음.
영향: PENDING에서 APPROVED/REJECTED/CANCELLED로 가는 경로, 직원 이동 후 권한 재판정, 동시 승인·취소의 승패 흐름을 구현자와 QA가 같은 방식으로 해석하기 어렵다.
수정 방향: 생성, 조회, 취소, 승인, 반려, 팀 이동, 권한 거부, 동시 요청의 주요 경로를 하나의 Mermaid flow로 추가한다.

2. **High: 취소 권한과 취소 API 동작이 FR/AC 수준에서 불완전함**
근거: `Users, roles, and permissions`는 직원의 “대기 취소”를 허용하고, `FR-102`, `FR-105`, `AC-106`은 CANCELLED/취소를 언급하지만, 취소 명령의 주체, 조건, 응답, 감사 이벤트를 직접 검증하는 FR/AC가 없음.
영향: 직원 본인만 취소 가능한지, 팀장이 취소할 수 없는지, APPROVED/REJECTED/CANCELLED 재취소가 409인지 403인지가 구현마다 달라질 수 있다.
수정 방향: “소유 직원만 본인 PENDING 신청을 CANCELLED로 전이할 수 있다”는 명시 요구사항과 정상 취소, 타인 취소, 최종 상태 취소 실패 AC를 추가한다.

3. **Medium: State matrix가 선언된 화면 범위를 충분히 덮지 못함**
근거: `Pages and routes`에는 `팀 승인함`과 `감사 이력`이 있지만 `State matrix`에는 `내 휴가`, `신청 폼`, `승인 상세`만 있음.
영향: 팀 승인함의 empty/loading/error/success/recovery, 감사 이력의 권한·필터·오류 상태가 검증 불가능하다. 특히 감사자는 휴가 사유 전문을 볼 수 없다는 데이터 경계가 UI 상태와 연결되지 않는다.
수정 방향: `/team/leave`와 `/audit/leave` 표면을 state matrix에 추가하고, 감사 이력의 redaction/empty/error/retry 상태를 명시한다.

4. **High: idempotency key의 보안·정합성 범위가 불명확함**
근거: `FR-106`은 모든 생성·상태 명령에 idempotency key를 요구하고, `AC-108`은 같은 key 재시도 시 같은 신청 ID와 중복 이벤트 없음만 검증함. 그러나 key의 scope, payload mismatch 처리, actor/org/operation별 분리, 보존 기간이 정의되지 않음.
영향: 다른 사용자 또는 다른 명령에서 같은 key가 충돌하거나, 같은 key로 다른 본문을 재전송했을 때 잘못된 기존 결과가 반환될 수 있다. 이는 교차 사용자 데이터 노출이나 상태 오염으로 이어질 수 있다.
수정 방향: idempotency key를 조직·actor·operation·request body fingerprint 기준으로 스코프하고, 같은 key 다른 payload는 409 또는 422로 고정하며, 재시도 응답과 보존 기간을 AC에 넣는다.

5. **Medium: 권한 거부 감사 요구가 검증 범위와 이벤트 스키마에서 모호함**
근거: `FR-105`는 생성·승인·반려·취소와 권한 거부를 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 하지만, 권한 거부는 상태 전이가 없고 대상 신청을 노출하면 안 되는 경우가 있다. `AC-105`는 처리 권한 거부만 다루며 조회·상세·목록·감사 접근 거부는 빠져 있음.
영향: 403 감사 이벤트가 리소스 존재 여부를 누설하거나, 반대로 필요한 보안 감사가 누락될 수 있다. “이전/이후 상태”가 없는 거부 이벤트를 어떻게 기록할지도 구현자가 임의 결정하게 된다.
수정 방향: 권한 거부 이벤트에 `event type/outcome`, redacted resource reference, nullable previous/next state 규칙을 정의하고, 조회·처리·감사 접근 거부에 대한 최소 AC를 추가한다.