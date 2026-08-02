# 결제 완료 웹훅 전달 API PRD

## Context and Problem

결제가 완료되면 고객사가 사전에 등록한 HTTPS endpoint로 결제 완료 이벤트를 전달해야 한다. 고객사는 이 이벤트를 기반으로 주문 확정, 서비스 활성화, 내부 정산 처리 등을 자동화한다.

웹훅 전달은 네트워크 실패, 고객사 endpoint 장애, 중복 전달 가능성을 전제로 설계해야 한다. 1차 출시 범위에는 UI, replay 대시보드, 수동 재전송 기능은 포함하지 않는다.

## Goals

- 결제 완료 시 등록된 고객사 HTTPS endpoint로 이벤트를 자동 전달한다.
- 네트워크 또는 일시적 실패 시 최소 1회 전달을 보장하기 위해 재시도한다.
- 동일 이벤트가 여러 번 전달될 수 있으므로 고객사가 중복 처리를 방어할 수 있는 `event_id`를 제공한다.
- 고객사별 데이터가 섞이지 않도록 이벤트 생성, 저장, 조회, 전달 전 과정에서 tenant 격리를 보장한다.
- 처리량과 지연 시간을 측정할 수 있도록 관측 지표를 남긴다.

## Non-goals

- endpoint 등록 UI 개발
- endpoint 등록 내부 API 개발 또는 변경
- replay 대시보드
- 수동 재전송 기능
- 고객사별 웹훅 설정 화면
- 근거 없는 처리량, 지연 SLA 정의
- 서명 알고리즘 또는 secret rotation 정책 최종 결정

## Users and Key Scenarios

- 고객사 시스템: 결제 완료 이벤트를 수신하고 자체 비즈니스 로직을 실행한다.
- 내부 결제 시스템: 결제 완료 상태가 확정되면 웹훅 이벤트를 생성한다.
- 운영자/개발자: 전달 성공률, 실패 원인, 재시도 상태를 로그와 메트릭으로 확인한다.

주요 시나리오:

1. 결제가 완료된다.
2. 시스템이 고객사별 등록 endpoint를 조회한다.
3. 결제 완료 웹훅 이벤트를 생성한다.
4. 고객사 HTTPS endpoint로 이벤트를 전달한다.
5. 고객사 endpoint가 성공 응답을 반환하면 전달을 완료 처리한다.
6. 네트워크 실패 또는 실패 응답이면 지수 백오프로 재시도한다.
7. 동일 이벤트가 재전달될 수 있으므로 고객사는 `event_id`로 멱등 처리한다.

## Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-101 | 결제 상태가 “완료”로 확정된 시점에 결제 완료 웹훅 이벤트를 생성한다. | Must |
| FR-102 | 각 이벤트는 전역적으로 고유한 `event_id`를 가진다. | Must |
| FR-103 | 이벤트에는 고객사가 중복 처리를 할 수 있도록 동일 결제 완료 건에 대해 안정적인 `event_id`를 포함한다. | Must |
| FR-104 | 이벤트는 해당 결제의 고객사 tenant에 등록된 HTTPS endpoint로만 전달한다. | Must |
| FR-105 | endpoint URL scheme이 HTTPS가 아닌 경우 전달 대상에서 제외하고 실패 상태로 기록한다. | Must |
| FR-106 | 고객사 endpoint 등록과 관리는 기존 내부 API를 사용하며, 본 범위에서는 새 UI나 등록 API를 만들지 않는다. | Must |
| FR-107 | 웹훅 payload에는 최소한 `event_id`, `event_type`, `occurred_at`, `tenant_id`, `payment_id`, 결제 완료 상태 정보가 포함된다. | Must |
| FR-108 | `event_type`은 결제 완료를 식별할 수 있는 안정적인 값으로 제공한다. 예: `payment.completed`. | Must |
| FR-109 | HTTP POST 방식으로 고객사 endpoint에 이벤트를 전달한다. | Must |
| FR-110 | 2xx 응답을 전달 성공으로 처리한다. | Must |
| FR-111 | 네트워크 오류, timeout, 5xx 응답은 재시도 대상으로 처리한다. | Must |
| FR-112 | 4xx 응답은 기본적으로 영구 실패로 처리하되, 정책상 재시도할 4xx가 있다면 별도 설정으로 분리한다. | Should |
| FR-113 | 재시도는 지수 백오프를 사용한다. | Must |
| FR-114 | 최대 재시도 횟수, 백오프 상한, timeout 값은 설정 가능해야 한다. | Must |
| FR-115 | 최종 실패한 이벤트는 상태, 실패 사유, 마지막 시도 시각, 시도 횟수를 보존한다. | Must |
| FR-116 | 같은 이벤트가 여러 번 전달될 수 있음을 API 문서에 명시한다. | Must |
| FR-117 | 고객사별 이벤트, endpoint, 전달 시도 기록은 tenant 기준으로 격리되어야 한다. | Must |
| FR-118 | 한 고객사의 endpoint 장애나 재시도 적체가 다른 고객사의 이벤트 전달을 막지 않아야 한다. | Should |
| FR-119 | 서명 검증 방식이 확정되면 적용할 수 있도록 요청 서명 헤더 추가 지점을 설계한다. | Must |
| FR-120 | secret rotation 정책이 확정되면 복수 secret 또는 grace period를 지원할 수 있도록 데이터 모델 변경 가능성을 고려한다. | Should |
| FR-121 | replay 대시보드와 수동 재전송 API/기능은 1차 출시에서 제공하지 않는다. | Must |
| FR-122 | 전달 성공, 실패, 재시도, 최종 실패에 대한 로그와 메트릭을 기록한다. | Must |

## API Contract

### Delivery Request

Method: `POST`  
Destination: 고객사별 등록 HTTPS endpoint

Example payload:

```json
{
  "event_id": "evt_123",
  "event_type": "payment.completed",
  "occurred_at": "2026-07-27T10:15:30Z",
  "tenant_id": "tenant_456",
  "payment_id": "pay_789",
  "payment": {
    "id": "pay_789",
    "status": "completed",
    "completed_at": "2026-07-27T10:15:29Z"
  }
}
```

### Headers

초기 필수 헤더:

```http
Content-Type: application/json
User-Agent: <service-name>/<version>
```

보안 담당자 결정 이후 추가 예정:

```http
Webhook-Signature: <open decision>
Webhook-Timestamp: <open decision>
```

## Non-functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| NFR-101 | 전달은 at-least-once 모델이다. exactly-once 전달은 보장하지 않는다. | Must |
| NFR-102 | 고객사 endpoint 호출은 timeout을 가져야 하며 무기한 대기하지 않는다. | Must |
| NFR-103 | retry worker 또는 queue 장애 시에도 생성된 이벤트가 유실되지 않도록 durable storage 또는 durable queue를 사용한다. | Must |
| NFR-104 | 로그에는 tenant 식별자, event_id, delivery attempt id, 응답 코드, 실패 유형을 남긴다. | Must |
| NFR-105 | 민감 결제 정보는 payload와 로그에 필요한 최소 범위로만 포함한다. | Must |
| NFR-106 | 처리량과 지연 SLA는 1차 출시 전에 임의 수치로 정의하지 않는다. 대신 실제 측정을 위한 메트릭을 수집한다. | Must |
| NFR-107 | 수집 메트릭에는 생성부터 첫 전달 시도까지의 지연, 성공까지의 지연, 재시도 횟수, 성공률, 최종 실패율이 포함된다. | Must |
| NFR-108 | tenant별 큐, 파티셔닝, rate limit 또는 동등한 격리 수단을 통해 고객사 간 영향 전파를 줄인다. | Should |

## Acceptance Criteria

| ID | Observable Criterion | Verification Method |
|---|---|---|
| AC-101 | 결제가 완료되면 `payment.completed` 이벤트가 생성된다. | 결제 완료 이벤트 발생 테스트 |
| AC-102 | 생성된 모든 이벤트는 고유한 `event_id`를 가진다. | 이벤트 저장소 uniqueness 테스트 |
| AC-103 | 동일 이벤트 재시도 시 payload의 `event_id`가 바뀌지 않는다. | 실패 후 재시도 통합 테스트 |
| AC-104 | 등록된 HTTPS endpoint로 HTTP POST 요청이 전송된다. | mock endpoint 통합 테스트 |
| AC-105 | endpoint가 2xx를 반환하면 전달 상태가 성공으로 저장된다. | mock 200/204 응답 테스트 |
| AC-106 | 네트워크 오류 또는 5xx 응답이면 재시도 작업이 예약된다. | timeout/500 응답 테스트 |
| AC-107 | 재시도 간격은 이전 시도보다 증가하는 지수 백오프 형태다. | retry schedule 단위 테스트 |
| AC-108 | 최대 재시도 후에도 실패하면 최종 실패 상태와 사유가 기록된다. | retry exhaustion 테스트 |
| AC-109 | 한 tenant의 이벤트가 다른 tenant의 endpoint로 전달되지 않는다. | multi-tenant 격리 테스트 |
| AC-110 | HTTPS가 아닌 endpoint는 호출하지 않고 실패 또는 설정 오류로 기록된다. | HTTP URL 등록 상태 테스트 |
| AC-111 | replay 대시보드와 수동 재전송 기능이 노출되지 않는다. | API route/UI route 확인 |
| AC-112 | 전달 관련 로그와 메트릭이 event_id와 tenant 기준으로 조회 가능하다. | observability 검증 |
| AC-113 | 문서에는 at-least-once 전달과 중복 수신 가능성이 명시되어 있다. | API 문서 리뷰 |

## Reasonable Assumptions

- endpoint 등록 정보는 기존 내부 API 또는 내부 저장소를 통해 tenant 기준으로 조회할 수 있다.
- 결제 완료 상태는 내부 결제 시스템에서 신뢰 가능한 단일 이벤트 또는 상태 전이로 감지할 수 있다.
- 고객사는 `event_id`를 사용해 멱등 처리를 구현할 수 있다.
- 1차 출시에서는 결제 완료 이벤트 1종만 지원한다.
- payload에는 결제 완료 처리에 필요한 최소 정보만 포함하고, 상세 결제 정보가 필요하면 고객사가 별도 API로 조회한다.
- retry 정책의 구체 수치는 기존 플랫폼 표준이 있다면 그것을 따른다.

## Open Decisions

| ID | Decision | Owner |
|---|---|---|
| OD-101 | 웹훅 서명 방식: HMAC 알고리즘, 서명 대상 문자열, timestamp 포함 여부, 헤더 이름 | 보안 담당자 |
| OD-102 | secret rotation 주기와 grace period 정책 | 보안 담당자 |
| OD-103 | 최대 재시도 횟수, 백오프 초기값, 백오프 상한, 전체 retry window | 플랫폼/백엔드 |
| OD-104 | 4xx 응답 중 재시도할 상태 코드가 있는지 여부 | 백엔드/운영 |
| OD-105 | payload에 포함할 결제 상세 필드의 최종 범위 | 결제 도메인 담당자 |
| OD-106 | tenant별 격리 구현 방식: 큐 분리, 파티셔닝, rate limit, worker pool 분리 중 선택 | 백엔드/플랫폼 |
| OD-107 | SLA 정의 시점과 기준: 실제 운영 측정 후 별도 확정 | 제품/플랫폼 |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| 고객사 endpoint 장애로 재시도 적체 발생 | 다른 이벤트 전달 지연 | tenant별 격리와 retry queue 분리 또는 rate limit 적용 |
| 중복 전달로 고객사 중복 처리 발생 | 주문/서비스 중복 처리 | 안정적인 `event_id` 제공 및 문서에 멱등 처리 요구 명시 |
| 서명 정책 미확정 | 고객사 보안 요구 미충족 가능 | 보안 결정 전까지 production rollout gate로 관리하거나 제한된 고객사 beta로 운영 |
| payload 과다 노출 | 개인정보/결제정보 노출 위험 | 최소 필드 원칙 적용, 로그 마스킹 |
| SLA 미정 상태에서 기대치 불일치 | 고객사 계약/운영 리스크 | 1차 출시 문서에 SLA 미정 및 측정 중임을 명시 |

## Delivery Outline

1. 결제 완료 이벤트 생성 지점 확정
2. webhook event 및 delivery attempt 저장 모델 정의
3. tenant 기준 endpoint 조회 연동
4. HTTPS endpoint 검증 및 POST 전달 구현
5. 성공/실패 상태 기록
6. 지수 백오프 retry worker 구현
7. tenant 격리와 실패 적체 방지 정책 적용
8. 로그, 메트릭, 알림 최소 세트 추가
9. API 문서에 payload, 중복 전달, retry, 보안 미확정 항목 명시
10. 보안 담당자 결정 후 서명/secret rotation 정책 반영

## Launch Criteria

- 모든 Must 요구사항의 acceptance criteria가 통과한다.
- 서명 방식 미확정 상태로 출시할 경우, 출시 범위와 고객사 제한 여부가 명시적으로 승인되어야 한다.
- 처리량과 지연 SLA는 숫자로 약속하지 않고, 측정 메트릭만 운영 대시보드 또는 로그에서 확인 가능해야 한다.
- replay 대시보드와 수동 재전송 기능이 외부 또는 내부 사용자에게 노출되지 않아야 한다.