# PRD: 결제 완료 웹훅 전달 API

## 1. 문서 개요

### 목적

결제가 완료되면 해당 고객사가 등록한 HTTPS endpoint로 결제 완료 이벤트를 전달하는 서버 측 웹훅 기능을 제공한다.

웹훅은 최소 1회(at-least-once) 전달을 보장한다. 따라서 동일 이벤트가 중복 전달될 수 있으며, 고객사가 중복을 식별할 수 있도록 모든 이벤트에 고유하고 불변인 `event_id`를 포함한다.

### 대상 사용자

- 결제 완료 데이터를 자사 시스템에서 처리하려는 고객사 개발자
- 웹훅 운영 및 장애 대응을 담당하는 내부 운영자
- endpoint와 고객사 설정을 관리하는 기존 내부 API

### 이번 출시의 성공 기준

- 결제 완료 이벤트가 누락되지 않고 전달 작업으로 생성된다.
- 일시적인 네트워크 또는 고객사 endpoint 장애 시 자동으로 재시도된다.
- 모든 전달 시도와 결과를 고객사 단위로 추적할 수 있다.
- 한 고객사의 이벤트, endpoint 및 secret이 다른 고객사에 노출되지 않는다.
- 동일 이벤트의 모든 재시도에서 같은 `event_id`가 사용된다.
- 확정되지 않은 처리량이나 지연 수치를 출시 보장으로 제시하지 않는다.

---

## 2. 범위

### 포함

- 결제 완료 시 웹훅 이벤트 생성
- 고객사가 기존 내부 API를 통해 등록한 HTTPS endpoint 조회
- 고객사 endpoint로 서버 간 HTTP POST 요청 전송
- 최소 1회 전달
- 네트워크 실패 및 재시도 가능한 응답에 대한 지수 백오프 재시도
- 고유한 이벤트 ID 제공
- 전달 상태 및 시도 이력 저장
- 고객사별 데이터 격리
- 웹훅 요청 인증을 위한 서명 기능의 확장 지점
- 운영 모니터링, 로그 및 경보에 필요한 데이터 제공

### 제외

- endpoint 등록·수정·삭제 UI
- 신규 endpoint 관리 API
- replay 대시보드
- 고객사 또는 운영자의 수동 재전송
- 처리량 또는 전달 지연 SLA 보장
- 결제 완료 이외의 이벤트 유형
- 고객사별 payload 커스터마이징
- 순서가 다른 결제 이벤트 간의 전달 순서 보장

---

## 3. 용어

- **고객사(tenant)**: 독립된 데이터 및 설정 경계를 갖는 웹훅 수신 주체
- **이벤트**: 결제 완료라는 비즈니스 사실을 표현하는 불변 레코드
- **전달(delivery)**: 이벤트를 특정 endpoint로 전송하는 작업
- **전달 시도(attempt)**: 하나의 HTTP 요청과 그 결과
- **event ID**: 이벤트를 고유하게 식별하는 불변 ID
- **최소 1회 전달**: 성공이 확인될 때까지 재시도할 수 있어 동일 이벤트가 중복 도착할 수 있는 전달 방식
- **종료 실패**: 자동 재시도가 더 이상 예정되지 않은 상태

---

## 4. 사용자 시나리오

### 정상 전달

1. 결제 시스템이 결제를 완료 상태로 확정한다.
2. 웹훅 시스템이 고객사와 결제 정보를 포함한 이벤트를 한 번 생성한다.
3. 등록된 활성 HTTPS endpoint를 조회한다.
4. 이벤트 payload를 HTTP POST로 전달한다.
5. 고객사 endpoint가 성공 응답을 반환한다.
6. 전달을 `succeeded` 상태로 기록한다.

### 일시적 실패 후 성공

1. 첫 요청에서 연결 실패, timeout 또는 재시도 가능한 HTTP 응답이 발생한다.
2. 실패 원인과 시각을 전달 시도 이력에 기록한다.
3. 지수 백오프 정책으로 다음 시도를 예약한다.
4. 재시도 요청은 최초 요청과 동일한 `event_id`를 사용한다.
5. 성공 응답이 확인되면 추가 자동 재시도를 중단한다.

### 중복 수신

1. 고객사 endpoint가 요청을 처리했지만 응답이 웹훅 시스템에 도착하지 않는다.
2. 웹훅 시스템은 성공을 확인하지 못해 동일 이벤트를 재전송한다.
3. 고객사는 `event_id`를 기준으로 이미 처리한 이벤트인지 확인한다.
4. 이미 처리된 이벤트라면 비즈니스 처리를 반복하지 않고 성공 응답을 반환한다.

### endpoint가 없는 경우

1. 결제 완료 시점에 활성 endpoint가 없다.
2. 이벤트 생성 여부와 전달 작업 생성 여부를 정의된 정책에 따라 기록한다.
3. endpoint가 나중에 등록되더라도 1차 출시에서는 과거 이벤트가 자동 replay되지 않는다.

---

## 5. 기능 요구사항

### FR-1. 결제 완료 감지

- 기존 결제 시스템에서 결제가 최종 완료 상태가 된 사실을 입력으로 받아야 한다.
- 동일 결제가 중복 통지되더라도 동일한 결제 완료 사실에 대해 이벤트가 무제한 중복 생성되지 않아야 한다.
- 결제 완료 처리와 이벤트 생성 사이의 장애로 이벤트가 누락되지 않는 구조를 사용해야 한다.
- 권장 구현은 결제 상태 변경과 동일 트랜잭션에서 outbox 레코드를 기록한 후 비동기 전달 시스템이 이를 소비하는 방식이다.
- 결제 완료가 취소되거나 환불되는 경우는 별도의 이벤트이며 이번 범위에 포함하지 않는다.

### FR-2. 이벤트 생성

각 이벤트는 최소한 다음 정보를 가져야 한다.

- `event_id`: 전역적으로 고유한 불변 ID
- `event_type`: `payment.completed`
- `event_version`: payload 스키마 버전
- `occurred_at`: 결제 완료가 확정된 시각
- `created_at`: 이벤트 레코드 생성 시각
- `tenant_id`: 고객사 식별자
- `payment_id`: 고객사 범위 내 결제 식별자
- `data`: 결제 완료 payload
- 이벤트 생성 중복 방지를 위한 내부 idempotency key

`event_id`는 재시도마다 새로 생성하지 않는다. 서로 다른 endpoint로 동일 이벤트를 전달하는 경우에도 이벤트 자체의 `event_id`는 동일하며, 각 전달 작업은 별도의 `delivery_id`를 가진다.

### FR-3. endpoint 결정

- endpoint 정보는 기존 내부 API 또는 그 API가 관리하는 저장소에서 조회한다.
- 결제 이벤트의 `tenant_id`와 동일한 고객사에 속한 활성 endpoint만 사용할 수 있다.
- endpoint는 반드시 HTTPS URL이어야 한다.
- 전달 작업에는 사용된 endpoint의 식별자와 전달 당시 URL 또는 endpoint 설정 버전을 기록해야 한다.
- endpoint 설정 변경이 이미 생성된 전달 작업에 미치는 영향은 열린 결정으로 관리한다.
- endpoint가 없거나 비활성 상태인 경우 외부 요청을 보내지 않고 그 사유를 기록한다.

### FR-4. HTTP 요청

웹훅은 다음 형태의 HTTP 요청으로 전달한다.

```http
POST {registered_https_endpoint}
Content-Type: application/json
User-Agent: {service-identifier}
X-Webhook-Event-Id: {event_id}
X-Webhook-Event-Type: payment.completed
X-Webhook-Event-Version: {event_version}
X-Webhook-Delivery-Id: {delivery_id}
X-Webhook-Timestamp: {request_timestamp}
X-Webhook-Signature: {signature}
```

예시 payload:

```json
{
  "id": "evt_...",
  "type": "payment.completed",
  "version": "1",
  "occurred_at": "RFC3339 timestamp",
  "data": {
    "payment_id": "pay_...",
    "status": "completed",
    "completed_at": "RFC3339 timestamp",
    "amount": {
      "value": "10000",
      "currency": "KRW"
    }
  }
}
```

- 실제 결제 필드와 개인정보 포함 범위는 기존 결제 도메인 모델 및 데이터 정책에 맞춰 확정한다.
- payload는 동일 이벤트의 재시도 사이에서 변경되지 않아야 한다.
- 요청 timestamp, signature, delivery attempt 관련 헤더는 시도마다 달라질 수 있다.
- 고객사가 모르는 필드를 무시할 수 있도록 하위 호환 가능한 스키마 진화 원칙을 적용한다.
- 호환성을 깨는 변경에는 새로운 `event_version`을 사용한다.

### FR-5. 성공 판정

합리적 가정으로, 고객사 endpoint의 모든 `2xx` 응답을 전달 성공으로 간주한다.

- 응답 body는 성공 판정에 사용하지 않는다.
- 성공한 전달 작업은 자동으로 다시 전송하지 않는다.
- 성공 응답을 수신하기 전에 연결이 끊기면 실제 고객사 처리 여부와 관계없이 실패로 간주할 수 있으며, 이후 중복 전달이 발생할 수 있다.

### FR-6. 실패 분류 및 재시도

다음 실패는 자동 재시도 대상으로 분류한다.

- DNS 해석 실패
- 연결 실패
- TLS 연결 실패
- 연결 또는 응답 timeout
- HTTP `408`
- HTTP `429`
- HTTP `5xx`
- 성공 응답 수신 여부가 불확실한 네트워크 오류

다음 응답은 기본적으로 재시도하지 않는 종료 실패로 분류한다.

- `408`, `429`를 제외한 HTTP `4xx`

추가 요구사항:

- 재시도 간격은 지수 백오프를 사용한다.
- 동시에 몰리는 재시도를 방지하기 위해 jitter를 적용한다.
- `Retry-After` 처리 여부 및 우선순위는 열린 결정으로 둔다.
- 최초 간격, 배수, 최대 간격, 최대 시도 횟수 또는 최대 재시도 기간은 측정과 운영 정책을 바탕으로 확정한다.
- 프로세스 재시작 후에도 예정된 재시도가 유실되지 않도록 다음 시도 시각을 영속 저장한다.
- 동일 전달 작업이 여러 worker에서 동시에 실행되지 않도록 lease, lock 또는 원자적 상태 전이를 사용한다.
- worker 장애로 lock이 영구 유지되지 않도록 복구 가능한 lease 방식을 사용한다.

### FR-7. 전달 상태

전달 작업은 최소한 다음 상태를 지원한다.

- `pending`: 최초 전달 대기
- `in_progress`: worker가 전달 처리 중
- `retry_scheduled`: 실패 후 다음 시도 예약
- `succeeded`: 성공 응답 확인
- `failed_terminal`: 재시도하지 않는 실패 또는 재시도 정책 소진
- `not_deliverable`: 활성 endpoint가 없어 전달할 수 없음

허용되는 주요 상태 전이는 다음과 같다.

```text
pending → in_progress → succeeded
                      → retry_scheduled → in_progress
                      → failed_terminal
pending → not_deliverable
```

상태 전이는 원자적으로 기록되어야 한다.

### FR-8. 전달 시도 이력

각 시도에 대해 다음 정보를 저장한다.

- `attempt_id`
- `delivery_id`
- `tenant_id`
- 시도 번호
- 요청 시작·종료 시각
- 결과 분류
- HTTP status code
- timeout 또는 네트워크 오류 코드
- 다음 시도 예정 시각
- 응답 시간
- endpoint 식별자 및 설정 버전
- 서명 key 버전 또는 secret 식별자
- 요청 payload의 무결성을 확인할 수 있는 hash

민감한 응답 body와 secret은 로그 또는 시도 이력에 저장하지 않는다. 응답 body 보관이 운영상 필요해질 경우 별도 데이터 정책과 크기 제한을 확정해야 한다.

### FR-9. 고객사 멱등 처리 지원

- 모든 요청의 헤더와 body에 동일한 `event_id`를 제공한다.
- 고객사 문서에는 중복 전달 가능성을 명시한다.
- 고객사에는 `event_id`를 영속 저장하고 이미 처리한 ID의 비즈니스 작업을 반복하지 않는 방식을 권고한다.
- `delivery_id`는 전송 작업 식별용이며 비즈니스 이벤트 중복 제거에는 `event_id`를 사용한다.

### FR-10. 서명 및 secret

- 모든 웹훅 요청은 출시 전 확정되는 방식에 따라 서명되어야 한다.
- 서명 대상에 최소한 요청 timestamp와 원본 request body가 포함될 수 있도록 구현 경계를 설계한다.
- JSON을 재직렬화하면 검증 결과가 달라질 수 있으므로, 서명은 실제 전송되는 body bytes를 대상으로 수행해야 한다.
- 서명 알고리즘, 헤더 형식, 허용 시간 오차, replay 방지 정책은 보안 담당자의 결정 후 확정한다.
- secret은 고객사별로 분리하고 평문 로그에 출력하지 않는다.
- secret은 승인된 암호화 저장소 또는 secret manager에 보관한다.
- rotation 중 복수 key 버전을 지원할 수 있도록 `key_id` 또는 secret 버전을 식별할 수 있는 구조를 준비한다.
- 서명 방식과 secret rotation 정책 확정은 외부 출시의 선행 조건이다.

### FR-11. 고객사별 데이터 격리

- 이벤트, 전달 작업, 전달 시도, endpoint 및 secret에는 모두 `tenant_id`를 연결한다.
- 모든 조회와 상태 변경에는 서버가 인증된 컨텍스트에서 얻은 `tenant_id` 조건을 강제한다.
- 요청 입력으로 받은 `tenant_id`만 신뢰해 데이터 범위를 결정해서는 안 된다.
- `tenant_id`와 리소스 ID를 함께 사용하는 복합 제약 또는 이에 준하는 저장소 수준 보호를 적용한다.
- worker가 전달 작업을 처리할 때도 이벤트, endpoint 및 secret의 `tenant_id` 일치를 검증한다.
- 고객사 간 endpoint, payload, 로그, metric label 및 secret이 섞이지 않아야 한다.
- 운영자 접근은 최소 권한 원칙과 감사 로그를 적용한다.
- 고객사 ID처럼 고카디널리티인 값은 기본 metric label로 노출하지 않는다.

### FR-12. Endpoint 네트워크 안전성

- HTTPS 인증서 검증을 비활성화할 수 없어야 한다.
- redirect 허용 여부는 출시 전 확정해야 하며, 기본 가정은 redirect를 따라가지 않는 것이다.
- endpoint 등록 시스템에서 SSRF 방어가 보장되는지 확인해야 한다.
- 전달 시점에도 내부망, loopback, link-local, 클라우드 metadata 주소 등 금지 대상에 대한 방어가 필요하다.
- DNS rebinding을 고려해 등록 시 검증만으로 충분하다고 가정하지 않는다.
- 지원 TLS 버전과 cipher 정책은 조직 보안 기준을 따른다.

---

## 6. 데이터 모델

### WebhookEvent

| 필드 | 설명 |
|---|---|
| `event_id` | 이벤트 고유 ID |
| `tenant_id` | 고객사 ID |
| `event_type` | `payment.completed` |
| `event_version` | payload 스키마 버전 |
| `payment_id` | 결제 ID |
| `idempotency_key` | 이벤트 중복 생성 방지 키 |
| `occurred_at` | 결제 완료 시각 |
| `created_at` | 이벤트 생성 시각 |
| `payload` | 불변 payload |
| `payload_hash` | payload 무결성 확인값 |

`idempotency_key`에는 결제 완료 상태 전이의 고유 식별자를 사용하는 것이 권장된다. 최소한 `tenant_id`, `payment_id`, 완료 전이 버전을 조합해 유일성 제약을 적용해야 한다.

### WebhookDelivery

| 필드 | 설명 |
|---|---|
| `delivery_id` | 전달 작업 고유 ID |
| `tenant_id` | 고객사 ID |
| `event_id` | 이벤트 ID |
| `endpoint_id` | endpoint ID |
| `endpoint_version` | 전달에 사용한 설정 버전 |
| `status` | 현재 전달 상태 |
| `attempt_count` | 수행한 시도 수 |
| `next_attempt_at` | 다음 시도 예정 시각 |
| `lease_until` | worker lease 만료 시각 |
| `last_error_class` | 최근 오류 분류 |
| `created_at` | 생성 시각 |
| `updated_at` | 최종 변경 시각 |
| `succeeded_at` | 성공 시각 |

### WebhookDeliveryAttempt

| 필드 | 설명 |
|---|---|
| `attempt_id` | 시도 고유 ID |
| `tenant_id` | 고객사 ID |
| `delivery_id` | 전달 작업 ID |
| `attempt_number` | 시도 순번 |
| `started_at` | 요청 시작 시각 |
| `finished_at` | 요청 종료 시각 |
| `result` | 성공, HTTP 실패, timeout 등 |
| `http_status` | HTTP status code |
| `error_code` | 정규화된 오류 코드 |
| `duration` | 응답 시간 |
| `next_attempt_at` | 다음 재시도 시각 |
| `signing_key_version` | 사용한 key 버전 |

---

## 7. 비기능 요구사항

### 신뢰성

- 결제 완료 이벤트 생성과 비동기 전달 사이에 유실 구간이 없어야 한다.
- 미처리 작업과 재시도 예약은 프로세스 메모리가 아닌 영속 저장소에 보관한다.
- worker가 작업 수행 중 종료되어도 lease 만료 후 다시 처리할 수 있어야 한다.
- 중복 처리보다 이벤트 유실 방지를 우선한다.

### 성능

- 처리량, 동시성, 전달 지연 목표는 현재 정하지 않는다.
- 시스템은 worker 수와 queue 소비량을 조절할 수 있는 구조로 구현한다.
- 고객사 endpoint의 지연이 다른 고객사의 전달을 장시간 차단하지 않도록 작업을 격리한다.
- 고객사별 동시성 또는 rate limit 도입 여부는 실제 측정 후 결정한다.

### 관측 가능성

최소한 다음 항목을 측정할 수 있어야 한다.

- 생성된 이벤트 수
- 전달 시도 수
- 성공 및 실패 수
- 실패 원인별 분포
- retry 예약 작업 수
- 종료 실패 수
- pending 작업의 대기 시간 분포
- HTTP 응답 시간 분포
- 결제 완료 시점부터 전달 성공까지의 시간 분포
- queue 또는 저장소에 남은 작업 수
- 오래된 `in_progress` 작업 수

경보 임계값은 운영 데이터가 확보된 후 정한다. 다만 이벤트 생성 또는 전달 worker가 완전히 중단된 상태를 탐지할 수 있는 health signal은 출시 시 제공해야 한다.

### 개인정보와 보존

- payload에는 전달 목적에 필요한 최소 정보만 포함한다.
- 카드번호, 인증정보, secret 등 결제 민감정보를 포함하지 않는다.
- 이벤트, 전달 이력 및 로그의 보존 기간은 개인정보 및 감사 정책에 따라 확정한다.
- 로그에는 secret, 서명 원문 및 불필요한 payload를 남기지 않는다.

---

## 8. API 계약 및 고객사 문서

이번 범위에 endpoint 관리 UI나 신규 등록 API는 없지만, 고객사 통합 문서에는 다음 내용을 제공해야 한다.

- 요청 메서드와 payload 예시
- 각 필드와 timestamp 형식
- `event_id` 기반 멱등 처리 방법
- 중복 및 비순차 전달 가능성
- 성공으로 인정되는 HTTP 응답
- timeout 전에 빠르게 `2xx`를 반환하고 후속 작업은 비동기로 처리하라는 권고
- 재시도 대상 응답
- 서명 생성·검증 절차
- secret rotation 절차
- 지원 TLS 조건
- payload 버전 변경 정책

서명 및 rotation이 확정되기 전에는 해당 문서를 최종 공개하지 않는다.

---

## 9. 합리적 가정

다음은 구현을 구체화하기 위해 적용하는 가정이며, 반대 결정이 내려지면 요구사항을 갱신한다.

- 하나의 결제는 하나의 고객사에만 속한다.
- 기존 결제 시스템은 결제 완료를 식별할 수 있는 안정적인 상태 전이 또는 이벤트를 제공한다.
- 기존 내부 API는 endpoint의 `tenant_id`, 활성 상태 및 설정 버전을 제공한다.
- 웹훅은 비동기로 전달되며 결제 완료 API의 응답을 기다리게 하지 않는다.
- HTTP `2xx` 전체를 성공으로 간주한다.
- `408`, `429`, `5xx`와 네트워크 오류는 재시도한다.
- 그 외 `4xx`는 자동 재시도하지 않는다.
- HTTP redirect는 기본적으로 따라가지 않는다.
- 동일 이벤트의 payload는 재시도 사이에서 불변이다.
- 고객사가 endpoint를 변경해도 자동으로 과거 이벤트를 replay하지 않는다.
- 전달 순서는 보장하지 않는다.
- 결제 완료 이벤트의 금액은 부동소수점이 아닌 문자열 또는 정수 기반 형식으로 표현한다.
- timestamp는 UTC 기반 RFC 3339 형식으로 전달한다.

---

## 10. 열린 결정

### 출시 전 반드시 확정할 결정

1. **서명 검증 방식**
   - 알고리즘
   - 서명 헤더 형식
   - 서명 대상 문자열 구성
   - timestamp 허용 오차
   - replay 방지 방식
   - key ID 또는 버전 표현 방식

2. **Secret rotation 정책**
   - rotation 주기
   - 구·신 secret 동시 유효 기간
   - rotation 시작 및 완료 절차
   - 유출 시 긴급 폐기 절차
   - 현재 endpoint 관리 API가 복수 key 버전을 지원하는지 여부

3. **재시도 정책의 실제 파라미터**
   - 최초 지연
   - 지수 배수
   - 최대 지연
   - 최대 시도 횟수 또는 최대 기간
   - jitter 방식
   - `Retry-After` 존중 여부
   - 종료 실패 이후 자동 보존·삭제 정책

4. **네트워크 정책**
   - 연결 timeout과 전체 요청 timeout
   - 허용 TLS 버전
   - redirect 정책
   - 최대 응답 body 읽기 크기
   - egress IP 고정 및 고객사 allowlist 지원 여부
   - endpoint 등록 및 전달 시 SSRF 방어 책임 경계

5. **Payload 계약**
   - 결제 완료 이벤트에 포함할 최종 필드
   - 개인정보 및 상점 정보의 포함 범위
   - 초기 `event_version`
   - 고객사에 노출되는 결제 ID의 형식

6. **Endpoint 변경 처리**
   - 전달 작업 생성 당시 URL을 고정할지
   - 각 재시도 시 최신 endpoint 설정을 조회할지
   - endpoint 비활성화가 예약된 재시도에 미치는 영향

### 측정 이후 결정할 사항

- 처리량 목표
- 전달 지연 SLA 또는 SLO
- worker 동시성
- 고객사별 rate limit
- queue 분할 또는 우선순위 정책
- 경보 임계값
- 이벤트 및 시도 이력 보존 기간
- 고객사별 noisy-neighbor 방지를 위한 격리 수준

근거가 확보되기 전에는 위 항목에 임의의 수치를 설정하거나 외부 SLA로 약속하지 않는다.

---

## 11. 예외 및 장애 처리

- 이벤트 저장 성공 후 queue 발행이 실패하면 outbox poller가 다시 발행해야 한다.
- queue 메시지가 중복 소비되면 `delivery_id`와 원자적 상태 전이로 동시 처리를 제한한다.
- 고객사 endpoint가 요청을 처리했으나 응답이 유실되면 동일 `event_id`로 재시도한다.
- payload 직렬화 또는 서명 생성에 실패하면 외부 요청을 보내지 않고 내부 오류로 기록한다.
- tenant, event, endpoint 또는 secret의 소유 관계가 일치하지 않으면 전달을 차단하고 보안 이벤트로 기록한다.
- 인증서 검증 실패는 재시도 가능 오류로 기록하되, 반복적인 설정 오류가 무한 재시도로 이어지지 않도록 전체 재시도 한도를 적용한다.
- 재시도 정책이 소진되면 `failed_terminal`로 전환한다. 1차 출시에서는 이 상태를 UI에서 replay하거나 수동 재전송할 수 없다.
- 운영자가 DB 상태를 직접 변경하는 방식은 공식 재전송 기능으로 제공하지 않는다.

---

## 12. 수용 기준

### 이벤트 생성

- 결제가 완료되면 해당 고객사의 `payment.completed` 이벤트와 전달 작업이 생성된다.
- 동일한 결제 완료 입력을 반복 처리해도 idempotency 제약에 따라 의도하지 않은 별도 이벤트가 생성되지 않는다.
- 결제 완료 처리 직후 프로세스가 종료되어도 이벤트가 최종적으로 전달 대상에 포함된다.

### 전달

- 등록된 활성 HTTPS endpoint로 JSON POST 요청을 보낸다.
- 요청 header와 body 모두에 동일한 `event_id`가 포함된다.
- `2xx` 응답을 받으면 전달 상태가 `succeeded`가 되고 추가 재시도가 예약되지 않는다.
- retry 대상 오류가 발생하면 지수 백오프와 jitter를 적용해 다음 시도가 영속적으로 예약된다.
- 모든 재시도는 동일한 이벤트 payload와 `event_id`를 사용한다.
- retry 대상이 아닌 `4xx` 응답은 `failed_terminal`로 처리된다.
- 정책 한도에 도달한 전달은 `failed_terminal`로 처리된다.

### 격리 및 보안

- 고객사 A의 작업이 고객사 B의 endpoint 또는 secret을 사용하려 하면 요청이 차단된다.
- 저장소의 모든 주요 리소스가 `tenant_id`로 연결되고 고객사 범위 조건 없이 조회되지 않는다.
- HTTPS가 아닌 endpoint에는 요청하지 않는다.
- TLS 인증서 검증 실패를 무시하지 않는다.
- secret과 전체 서명 값이 애플리케이션 로그에 기록되지 않는다.
- 보안 담당자가 승인한 서명 검증 시나리오가 통합 테스트를 통과해야 외부 출시할 수 있다.

### 운영

- 각 전달 시도에 결과, HTTP status 또는 오류 분류, 수행 시간, 다음 시도 시각이 기록된다.
- pending, retry, 성공, 실패 및 작업 대기 시간을 측정할 수 있다.
- worker 중단과 처리 정체를 운영자가 탐지할 수 있다.
- UI, replay 대시보드 또는 수동 재전송 기능이 노출되지 않는다.

---

## 13. 테스트 요구사항

- 정상 `2xx` 응답
- 각 retry 대상 HTTP 응답
- retry하지 않는 `4xx` 응답
- DNS, 연결, TLS 및 timeout 오류
- 응답 유실로 인한 중복 전달
- 동일 이벤트의 payload와 `event_id` 불변성
- 중복 결제 완료 입력
- worker가 요청 전·후에 종료되는 경우
- lease 만료 후 작업 복구
- 여러 worker의 동일 작업 경쟁
- endpoint 없음 또는 비활성화
- endpoint 변경 중 재시도
- 잘못된 tenant 관계
- secret 또는 signing key 버전 불일치
- SSRF 금지 대상 endpoint
- redirect 응답
- 최대 크기 또는 직렬화할 수 없는 payload
- 재시도 정책 소진
- metric과 로그에서 secret 및 민감정보가 노출되지 않는지 검증

---

## 14. 출시 조건

다음 조건을 모두 충족해야 1차 출시할 수 있다.

- 결제 완료부터 이벤트 생성까지의 유실 방지 구조 구현
- 최소 1회 전달 및 영속적 재시도 구현
- 고객사별 데이터 격리 검증
- 보안 담당자가 서명 방식과 secret rotation 정책 승인
- SSRF 및 TLS 정책 검토 완료
- 최종 payload 스키마 확정
- 재시도 및 timeout 파라미터 확정
- 고객사 통합 문서 제공
- 핵심 metric, health check 및 장애 경보 준비
- 중복 전달, worker 장애 및 고객사 간 격리에 대한 통합 테스트 통과

처리량과 지연 SLA는 출시 조건으로 임의 설정하지 않는다. 출시 전 부하 테스트 결과는 시스템의 초기 운영 설정을 정하는 근거로만 사용하며, 외부 SLA는 실제 운영 측정 이후 별도로 결정한다.