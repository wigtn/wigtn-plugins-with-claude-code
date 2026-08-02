**계약 감사표**
| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger | Present | `Applicability` 표가 있고 Pages/routes, State matrix, User flow를 Required로 판정함 |
| Pages and routes | Present | `/leave`, `/leave/:id`, `/team/leave`, `/audit/leave` 정의 |
| Empty/loading/error/success/recovery state matrix | Present | `State matrix`에 Empty/Loading/Error/Success/Recovery 정의 |
| Mermaid user or system flow | Present | `User flow`에 Mermaid lifecycle 포함 |
| Acceptance precondition/action/result mapped to requirement IDs | Present | `AC-101`~`AC-108`이 FR ID, Given/When/Then/Verification 포함 |
| Delivery phases mapped to requirement IDs and exit conditions | Present | Phase 1~3이 Requirement IDs와 exit condition 포함 |

**Findings**
| Impact | Finding | Evidence | 수정 방향 |
|---|---|---|---|
| high | 직원 취소 경로가 핵심 상태 전이인데 acceptance coverage가 없다. 구현자가 취소 권한, PENDING 제한, 감사 이벤트, 동시성 처리를 빠뜨려도 PRD상 검증 실패로 잡기 어렵다. | `FR-102`는 PENDING에서 `CANCELLED` 전이를 허용하고, `FR-105`는 취소 감사 기록을 요구한다. `/leave/:id`도 취소를 primary action으로 둔다. 그러나 `AC-101`~`AC-108`에 직원 취소 성공/실패 기준이 없다. | `AC`에 “소유 직원이 PENDING 신청 취소 시 CANCELLED와 감사 이벤트 1건”, “타인 또는 terminal 상태 취소 시 403/409 및 상태 불변”을 추가한다. 동시 승인/취소는 `AC-106`과 연결한다. |
| high | 감사자 권한과 휴가 사유 비노출이 검증 불가능하다. 개인정보/민감정보 경계가 요구사항에는 있으나 release gate가 없다. | Role 표는 감사자가 “휴가 사유 전문 읽기” 금지라고 하고, `FR-105`는 감사 이벤트에 휴가 사유 전문을 기록하지 않는다고 한다. `Risks`도 로그·감사 이벤트 제외를 말한다. 하지만 AC에는 `/audit/leave` 조회, reason redaction, 상태 변경 금지 검증이 없다. | 감사자 AC를 추가한다: 감사자는 조직 내 이벤트 메타데이터만 조회 가능, reason 전문 미포함, 상태 변경 API 호출은 403과 상태 불변. 로그/감사 payload schema에 reason 금지 필드를 명시한다. |
| high | People Platform 장애 시 fail-closed 범위가 “처리 요청”으로만 제한되어 조회 권한에서 보안 공백이 생긴다. 팀장 조회도 현재 팀장 관계 확인이 필요한데 장애 처리 기준이 없다. | `FR-104`는 작업별로 현재 팀을 검사한다고 하고, 직원 이동 후 이전 팀장은 접근을 잃는다고 한다. 그런데 `Authorization and data boundaries`는 “인사 시스템이 실패하면 처리 요청은 fail-closed 503”만 명시한다. `/team/leave`, `/leave/:id` 팀장 조회 실패 동작은 미정이다. | People Platform 의존 작업을 분류하고, 현재 팀장 관계가 필요한 조회·처리 모두 fail-closed 503으로 명시한다. 캐시 사용 시 TTL, stale 허용 여부, 팀 이동 이벤트 반영 기준도 정한다. |
| medium | idempotency key의 범위와 재사용 의미가 부족해 중복 방지와 보안 동작이 구현마다 달라질 수 있다. | `FR-106`은 모든 생성·상태 명령에 idempotency key를 요구하지만, `AC-108`은 신청 생성 재시도만 다룬다. key가 조직/actor/operation/request body에 묶이는지, 다른 payload로 같은 key를 재사용하면 409인지, 보존 기간이 얼마인지는 없다. | key scope를 `organization + actor + operation + key` 등으로 정의하고 request fingerprint 불일치 시 409를 명시한다. 상태 명령 승인/반려/취소 각각의 재시도 AC와 중복 감사 이벤트 금지 기준을 추가한다. |
| medium | 감사 이벤트의 이전/이후 상태 필드가 권한 거부 이벤트에 적용될 때 모호하다. 구현자가 denial 이벤트에 어떤 상태를 넣어야 하는지, request ID가 실제 신청 ID인지 시도 ID인지 다르게 해석할 수 있다. | `FR-105`는 생성·승인·반려·취소와 권한 거부를 `actor, request ID, 이전/이후 상태, timestamp`로 기록한다고 한다. 생성의 이전 상태만 `null`로 정의되어 있고, 권한 거부의 이전/이후 상태 규칙은 없다. | 감사 이벤트 타입별 schema를 나눈다. 권한 거부는 `attempted_request_id`, `target_request_id` nullable 여부, `before_state` 조회 가능 시 값/불가 시 null, `after_state` null 또는 unchanged 같은 규칙을 명시한다. |

검증기는 실행하지 않았습니다. 사용자가 저장소 탐색과 파일 생성을 하지 말라고 했고, 제공된 PRD 원문만 리뷰 대상으로 삼았습니다.