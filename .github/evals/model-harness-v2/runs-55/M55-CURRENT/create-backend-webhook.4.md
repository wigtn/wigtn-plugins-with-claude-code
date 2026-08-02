# 결제 완료 웹훅 전달 API PRD

## Context and Problem

결제가 완료된 후 고객사 시스템이 후속 처리를 자동화할 수 있도록, 사전에 등록된 고객사 HTTPS endpoint로 결제 완료 이벤트를 전달해야 한다. 네트워크 실패나 고객사 서버 장애가 있을 수 있으므로 최소 1회 전달을 보장하고, 고객사는 동일 이벤트를 여러 번 받을 수 있음을 전제로 event ID 기반 멱등 처리를 할 수 있어야 한다.

이번 범위에는 고객사 endpoint 등록 UI, replay 대시보드, 수동 재전송 기능은 포함하지 않는다.

## Goals

- 결제 완료 시 등록된 고객사 HTTPS endpoint로 웹훅 이벤트를 전달한다.
- 네트워크 실패 및 일시적 실패에 대해 지수 백오프 기반 자동 재시도를 수행한다.
- 고객사가 중복 수신을 감지할 수 있도록 모든 이벤트에 고유 event ID를 포함한다.
- 고객사별 endpoint, secret, 이벤트, 전달 이력 데이터가 격리되도록 한다.
- 1차 출시에서 운영자가 자동 재시도 상태와 실패 원인을 추적할 수 있는 최소한의 내부 관측성을 제공한다.

## Non-goals

- 고객사용 UI 또는 endpoint 등록 UI 구현
- replay 대시보드
- 수동 재전송 기능
- 근거 없는 처리량, 지연 시간, 성공률 SLA 정의
- 서명 알고리즘 또는 secret rotation 정책 최종 확정
- 결제 완료 외 이벤트 타입 지원
- 고객사의 멱등 처리 구현

## Users and Key Scenarios

- **고객사 서버**: 결제 완료 이벤트를 HTTPS endpoint로 수신하고 주문, 정산, 알림 등 후속 처리를 수행한다.
- **내부 결제 시스템**: 결제 완료 상태 전환 후 웹훅 전달 이벤트를 생성한다.
- **내부 운영자/개발자**: 전달 실패, 재시도 상태, 응답 코드, 오류 원인을 내부 로그 또는 운영 도구로 확인한다.
- **보안 담당자**: 웹훅 서명 방식과 secret rotation 정책을 결정한다.

## Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-101 | 결제가 최종적으로 완료 상태가 되면 `payment.completed` 웹훅 이벤트를 생성해야 한다. | Must |
| FR-102 | 각 웹훅 이벤트는 전역적으로 고유한 `event_id`를 가져야 한다. | Must |
| FR-103 | 동일 결제 완료 상태에 대해 중복 이벤트가 생성되지 않도록 내부 이벤트 생성은 멱등적이어야 한다. | Must |
| FR-104 | 이벤트 payload에는 최소한 `event_id`, `event_type`, `created_at`, `customer_id`, `payment_id`, 결제 완료 시각, 결제 금액, 통화, 결제 상태를 포함해야 한다. | Must |
| FR-105 | 고객사별로 등록된 활성 HTTPS endpoint가 있는 경우에만 이벤트 전달을 시도해야 한다. | Must |
| FR-106 | endpoint 등록, 수정, 비활성화는 기존 내부 API가 담당하며, 본 기능은 해당 등록 정보를 읽어 사용한다. | Must |
| FR-107 | 전달 대상 endpoint는 HTTPS URL이어야 하며 HTTP endpoint로는 전달하지 않아야 한다. | Must |
| FR-108 | 각 전달 요청에는 event ID가 포함된 헤더를 제공해야 한다. 예: `X-Webhook-Event-Id`. | Must |
| FR-109 | 각 전달 요청에는 이벤트 타입이 포함된 헤더를 제공해야 한다. 예: `X-Webhook-Event-Type`. | Should |
| FR-110 | 고객사 endpoint가 2xx 응답을 반환하면 해당 전달 시도를 성공으로 기록해야 한다. | Must |
| FR-111 | 네트워크 오류, timeout, 5xx 응답, 재시도 대상 429 응답은 실패로 기록하고 자동 재시도해야 한다. | Must |
| FR-112 | 4xx 응답은 기본적으로 영구 실패로 처리하되, 429는 재시도 가능 실패로 처리해야 한다. | Must |
| FR-113 | 재시도는 지수 백오프를 사용해야 하며, retry 간격과 최대 시도 횟수는 설정값으로 관리해야 한다. | Must |
| FR-114 | 자동 재시도는 최소 1회 전달 보장 관점에서 원본 이벤트가 성공하거나 최종 실패 상태가 될 때까지 관리되어야 한다. | Must |
| FR-115 | 동일 이벤트가 여러 번 전달될 수 있으므로 API 문서와 payload 구조는 고객사 멱등 처리를 전제로 해야 한다. | Must |
| FR-116 | 각 전달 시도는 `event_id`, `customer_id`, endpoint 식별자, attempt 번호, 요청 시각, 응답 시각, 응답 코드, 성공/실패 상태, 오류 유형을 기록해야 한다. | Must |
| FR-117 | 고객사별 데이터 격리를 위해 이벤트 생성, endpoint 조회, 전달 이력 조회/기록은 `customer_id` 경계를 기준으로 수행되어야 한다. | Must |
| FR-118 | 다른 고객사의 endpoint 또는 secret이 잘못 사용되지 않도록 전달 작업은 이벤트의 `customer_id`와 endpoint의 소유 고객사를 검증해야 한다. | Must |
| FR-119 | 서명 검증 방식이 확정되지 않았더라도, 향후 서명 헤더 추가와 secret rotation을 수용할 수 있도록 전달 요청 생성부를 확장 가능하게 설계해야 한다. | Should |
| FR-120 | 서명 방식 확정 전에는 production 공개 출시 여부를 보안 담당자 승인에 의존해야 한다. | Must |
| FR-121 | replay 대시보드와 수동 재전송 API/버튼은 1차 출시 범위에서 제공하지 않아야 한다. | Must |

## API Contract

### Outbound Webhook Request

- Method: `POST`
- URL: 고객사별 등록 HTTPS endpoint
- Content-Type: `application/json`

Required headers:

| Header | Description |
|---|---|
| `Content-Type: application/json` | JSON payload |
| `X-Webhook-Event-Id` | 중복 수신 감지를 위한 고유 이벤트 ID |
| `X-Webhook-Event-Type` | 예: `payment.completed` |
| `X-Webhook-Created-At` | 이벤트 생성 시각 |

Signature-related headers are open decisions and must not be finalized in this PRD.

### Example Payload

```json
{
  "event_id": "evt_123",
  "event_type": "payment.completed",
  "created_at": "2026-07-27T10:15:30Z",
  "customer_id": "cus_123",
  "data": {
    "payment_id": "pay_123",
    "status": "completed",
    "completed_at": "2026-07-27T10:15:00Z",
    "amount": 50000,
    "currency": "KRW"
  }
}
```

## Delivery State Model

| State | Meaning |
|---|---|
| `pending` | 이벤트가 생성되었고 아직 전달 시도 전 |
| `delivering` | 전달 작업이 진행 중 |
| `succeeded` | 고객사 endpoint가 2xx 응답을 반환 |
| `retry_scheduled` | 재시도 가능한 실패 후 다음 시도 예약됨 |
| `failed_terminal` | 최대 재시도 도달 또는 영구 실패 응답으로 자동 전달 종료 |

## Non-functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| NFR-101 | 처리량과 지연 SLA는 실제 측정 전까지 명시하지 않는다. | Must |
| NFR-102 | 재시도 큐/작업자는 장애 후 재시작되어도 미완료 이벤트를 잃지 않아야 한다. | Must |
| NFR-103 | 전달 payload와 로그에는 필요한 결제 완료 정보만 포함하고 불필요한 민감 정보를 포함하지 않아야 한다. | Must |
| NFR-104 | customer_id 기반 데이터 접근 경계를 테스트로 검증해야 한다. | Must |
| NFR-105 | 웹훅 전달 결과는 내부 운영자가 장애 원인 분석에 사용할 수 있을 만큼 구조화 로그 또는 저장된 전달 이력으로 남아야 한다. | Must |
| NFR-106 | endpoint 호출 timeout은 설정 가능해야 한다. | Should |
| NFR-107 | 재시도 설정값은 배포 없이 조정 가능하거나 최소한 환경 설정으로 분리되어야 한다. | Should |

## Acceptance Criteria

| ID | Observable Criterion | Verification Method |
|---|---|---|
| AC-101 | 결제 상태가 완료로 전환되면 `payment.completed` 이벤트가 생성된다. | 결제 완료 시나리오 통합 테스트 |
| AC-102 | 생성된 이벤트에는 고유 `event_id`가 포함된다. | 단위 테스트 및 payload 검증 |
| AC-103 | 동일 결제 완료 이벤트 처리 요청이 중복 발생해도 내부 이벤트가 중복 생성되지 않는다. | 멱등성 테스트 |
| AC-104 | 활성 HTTPS endpoint가 등록된 고객사에만 POST 요청이 전송된다. | 통합 테스트 |
| AC-105 | HTTP endpoint 또는 비활성 endpoint에는 전송하지 않는다. | endpoint 필터링 테스트 |
| AC-106 | 고객사 endpoint가 2xx 응답을 반환하면 전달 상태가 `succeeded`가 된다. | mock endpoint 테스트 |
| AC-107 | 네트워크 오류 또는 5xx 응답이면 지수 백오프 기반 재시도가 예약된다. | retry scheduler 테스트 |
| AC-108 | 429 응답은 재시도 가능 실패로 처리된다. | 응답 코드별 처리 테스트 |
| AC-109 | 400, 401, 403, 404 등 4xx 응답은 429를 제외하고 영구 실패로 처리된다. | 응답 코드별 처리 테스트 |
| AC-110 | 모든 전달 시도는 attempt 번호, 상태, 응답 코드 또는 오류 유형과 함께 기록된다. | 전달 이력 저장 검증 |
| AC-111 | A 고객사 이벤트가 B 고객사 endpoint로 전달되지 않는다. | tenant isolation 테스트 |
| AC-112 | A 고객사 secret 또는 endpoint가 B 고객사 전달 작업에서 참조되지 않는다. | tenant boundary 테스트 |
| AC-113 | 동일 `event_id`가 고객사에 여러 번 전달될 수 있으며 payload와 헤더에서 고객사가 이를 식별할 수 있다. | 재시도 시나리오 테스트 |
| AC-114 | replay 대시보드와 수동 재전송 기능이 노출되지 않는다. | API route/UI scope 확인 |
| AC-115 | PRD 또는 API 문서에 처리량/지연 SLA 수치가 임의로 기재되지 않는다. | 문서 검토 |

## Assumptions

- 결제 완료 상태는 기존 결제 시스템에서 신뢰 가능한 최종 상태로 정의되어 있다.
- endpoint 등록 정보는 기존 내부 API 또는 저장소에서 고객사별로 조회 가능하다.
- 고객사는 중복 이벤트 수신 가능성을 문서로 안내받고, `event_id` 기준 멱등 처리를 수행한다.
- 1차 출시에서는 결제 완료 이벤트 타입만 필요하다.
- 2xx 응답은 고객사가 이벤트를 정상 수신한 것으로 간주한다.
- 429는 고객사 측 rate limit 또는 일시적 제한으로 보고 재시도한다.
- 고객사별 데이터 격리는 현재 시스템의 `customer_id` 또는 tenant 식별자를 기준으로 구현 가능하다.
- 운영자는 UI 없이도 로그, DB, APM, 내부 콘솔 등 기존 수단으로 전달 실패를 확인할 수 있다.

## Open Decisions

| ID | Decision | Owner | Needed By |
|---|---|---|---|
| OD-101 | 웹훅 서명 알고리즘: 예: HMAC-SHA256 여부, timestamp 포함 여부, canonical payload 방식 | 보안 담당자 | production 공개 전 |
| OD-102 | secret rotation 주기와 grace period 정책 | 보안 담당자 | production 공개 전 |
| OD-103 | 서명 관련 헤더 이름과 버전 관리 방식 | 보안 담당자/API 담당자 | 고객사 연동 문서 작성 전 |
| OD-104 | 최대 재시도 횟수와 백오프 상한값 | 제품/엔지니어링 | 구현 전 |
| OD-105 | endpoint 호출 timeout 기본값 | 엔지니어링 | 구현 전 |
| OD-106 | 최종 실패 이벤트의 운영 알림 기준 | 운영/엔지니어링 | 출시 전 |
| OD-107 | 고객사별 rate limiting 또는 동시 전달 제한 필요 여부 | 엔지니어링 | 부하 측정 후 |
| OD-108 | 처리량과 지연 SLA | 제품/엔지니어링 | 실제 측정 데이터 확보 후 |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| 서명 방식 미확정 | 고객사가 이벤트 출처를 검증하기 어려움 | production 공개 전 보안 결정 필수, 전달 모듈은 서명 확장 가능하게 설계 |
| 중복 전달 | 고객사 후속 처리 중복 발생 가능 | `event_id` 제공, 멱등 처리 문서화 |
| 고객사 endpoint 장애 | 결제 완료 후 고객사 반영 지연 | 지수 백오프 자동 재시도, 전달 이력 기록 |
| tenant boundary 오류 | 다른 고객사 데이터 또는 endpoint로 이벤트 전달 가능 | customer_id 검증, 격리 테스트, 전달 작업 생성 시 소유권 확인 |
| 무제한 재시도 | 큐 적체 및 비용 증가 | 최대 재시도 횟수와 terminal failure 상태 도입 |
| SLA 미정 상태의 기대치 불일치 | 고객사 또는 내부 이해관계자 기대 관리 실패 | 1차 출시 문서에 측정 전 SLA 미제공 명시 |

## Delivery Outline

1. 결제 완료 이벤트 생성 지점 정의 및 멱등 이벤트 생성 구현
2. 고객사별 활성 HTTPS endpoint 조회 연동
3. 웹훅 payload 및 기본 헤더 구성
4. 전달 작업 큐/worker 구현
5. 응답 코드 및 네트워크 오류별 성공/재시도/영구 실패 처리
6. 지수 백오프 retry scheduler 구현
7. 전달 이력 저장 및 구조화 로그 추가
8. customer_id 기반 데이터 격리 테스트 추가
9. 보안 담당자 결정 후 서명 및 secret rotation 정책 반영
10. 내부 운영 확인 절차와 고객사 연동 문서 작성

## Out of Scope for First Release

- 고객사 endpoint 등록 UI
- 고객사용 replay dashboard
- 운영자 수동 재전송 기능
- 결제 완료 외 이벤트
- SLA 수치 공개
- 고객사별 상세 delivery analytics 화면