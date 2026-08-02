# 결제 완료 웹훅 전달 API PRD

## 1. Context and Problem

결제가 완료된 후 고객사 시스템이 후속 처리를 자동화할 수 있도록, 플랫폼은 등록된 고객사 HTTPS endpoint로 `payment.completed` 이벤트를 전달해야 한다.

현재 endpoint 등록은 기존 내부 API가 담당하므로, 이번 범위는 결제 완료 이벤트 발생 이후 웹훅 전달, 재시도, 중복 수신 대응, 고객사별 데이터 격리까지로 제한한다.

## 2. Goals

- 결제 완료 이벤트를 등록된 고객사 HTTPS endpoint로 최소 1회 전달한다.
- 네트워크 실패 또는 일시적 실패에 대해 지수 백오프 기반 재시도를 수행한다.
- 고객사가 동일 이벤트를 여러 번 받을 수 있음을 전제로, 이벤트 식별 가능한 `event_id`를 제공한다.
- 고객사별 데이터가 다른 고객사로 전달되거나 조회되지 않도록 격리한다.
- 1차 출시에서 운영자가 자동 전달 상태를 추적할 수 있는 최소한의 내부 기록을 남긴다.

## 3. Non-goals

- 고객사용 UI 제공
- endpoint 등록 UI 또는 API 구현
- replay 대시보드
- 수동 재전송 기능
- 처리량 SLA 또는 지연 SLA 확정
- 서명 검증 방식 및 secret rotation 정책 확정
- 결제 승인, 취소, 환불 등 결제 완료 외 이벤트 지원

## 4. Users and Key Scenarios

### Primary Users

- 고객사 백엔드 시스템
- 내부 결제/플랫폼 운영 시스템
- 내부 운영자 또는 엔지니어

### Key Scenarios

1. 결제가 완료되면 고객사 endpoint로 `payment.completed` 이벤트가 전달된다.
2. 고객사 endpoint가 일시적으로 실패하면 시스템은 지수 백오프로 재시도한다.
3. 고객사가 같은 이벤트를 여러 번 수신해도 `event_id`로 멱등 처리를 할 수 있다.
4. 특정 고객사의 결제 이벤트는 해당 고객사의 등록 endpoint로만 전달된다.
5. 최종 실패한 전달 건은 내부 기록으로 확인 가능하다.

## 5. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-101 | 결제 완료 상태가 확정되면 `payment.completed` 웹훅 이벤트를 생성해야 한다. | Must |
| FR-102 | 각 이벤트에는 전역적으로 고유한 `event_id`가 포함되어야 한다. | Must |
| FR-103 | 이벤트 payload에는 고객사가 결제 완료를 식별하고 처리하는 데 필요한 결제 식별자, 고객사 식별자, 결제 상태, 완료 시각이 포함되어야 한다. | Must |
| FR-104 | 웹훅은 해당 고객사에 등록된 HTTPS endpoint로만 전달되어야 한다. | Must |
| FR-105 | endpoint가 없거나 비활성 상태인 고객사에 대해서는 전달을 시도하지 않고 내부 상태로 기록해야 한다. | Must |
| FR-106 | HTTP 요청은 `POST` 방식으로 전송해야 한다. | Must |
| FR-107 | 고객사 endpoint가 성공 응답을 반환하면 전달 성공으로 기록해야 한다. | Must |
| FR-108 | 네트워크 오류, timeout, 또는 실패 응답에 대해서는 재시도 대상으로 기록해야 한다. | Must |
| FR-109 | 재시도는 지수 백오프를 사용해야 한다. | Must |
| FR-110 | 최대 재시도 횟수 또는 최종 실패 판정 기준이 필요하다. 단, 구체 수치는 출시 전 운영 정책으로 확정해야 한다. | Must |
| FR-111 | 동일 이벤트가 여러 번 전달될 수 있으므로 API 계약에 중복 가능성을 명시해야 한다. | Must |
| FR-112 | 고객사별 webhook endpoint, delivery 기록, event payload는 tenant/customer 경계로 격리되어야 한다. | Must |
| FR-113 | 각 전달 시도마다 시도 시각, 대상 endpoint, HTTP status 또는 오류 유형, retry count, 결과 상태를 기록해야 한다. | Must |
| FR-114 | 1차 출시 범위에서는 운영자가 임의로 replay 또는 수동 재전송을 실행할 수 없어야 한다. | Must |
| FR-115 | 서명 검증 방식이 확정되기 전까지 payload 또는 header 구조는 향후 서명 header 추가가 가능한 형태로 설계해야 한다. | Should |
| FR-116 | 실패한 전달이 결제 완료 처리 자체를 롤백하거나 실패시키지 않아야 한다. | Must |

## 6. API Contract

### Event Type

```json
{
  "event_id": "evt_...",
  "event_type": "payment.completed",
  "created_at": "2026-07-27T10:30:00Z",
  "customer_id": "cus_...",
  "data": {
    "payment_id": "pay_...",
    "status": "completed",
    "completed_at": "2026-07-27T10:29:58Z",
    "amount": 10000,
    "currency": "KRW"
  }
}
```

### Delivery Request

- Method: `POST`
- URL: 고객사별 등록 HTTPS endpoint
- Content-Type: `application/json`
- Body: webhook event payload
- Signature headers: 미정. 보안 담당자 결정 후 추가.

### Success Criteria

성공 응답의 정확한 HTTP status 범위는 열린 결정이다. 기본 가정은 `2xx` 응답을 성공으로 본다.

## 7. Event and Delivery States

### Event State

- `created`: 결제 완료 이벤트 생성됨
- `delivery_scheduled`: 전달 작업 예약됨
- `delivered`: 하나 이상의 전달 성공
- `delivery_failed`: 재시도 한도 또는 최종 실패 조건 도달
- `skipped`: 활성 endpoint가 없어 전달하지 않음

### Delivery Attempt State

- `pending`
- `in_progress`
- `succeeded`
- `retry_scheduled`
- `failed_final`

## 8. Non-functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| NFR-101 | 웹훅 전달은 최소 1회 보장(at-least-once)을 목표로 해야 하며, exactly-once 전달을 보장하지 않는다. | Must |
| NFR-102 | 처리량과 지연 SLA는 현재 미정이며, 1차 출시에서는 실제 측정 가능한 지표를 수집해야 한다. | Must |
| NFR-103 | 고객사 간 데이터 혼선을 방지하기 위해 모든 이벤트 생성, 조회, 전달, 기록 저장 경로에서 customer/tenant scope 검증이 필요하다. | Must |
| NFR-104 | endpoint URL은 HTTPS만 허용해야 한다. | Must |
| NFR-105 | timeout과 retry 정책은 무한 대기를 방지해야 한다. | Must |
| NFR-106 | webhook payload에는 결제 완료 처리에 필요한 최소 데이터만 포함해야 한다. | Should |
| NFR-107 | 로그에는 민감정보가 과도하게 남지 않도록 해야 한다. | Should |
| NFR-108 | 관측을 위해 이벤트 생성 수, 전달 성공 수, 재시도 수, 최종 실패 수를 측정 가능해야 한다. | Should |

## 9. Acceptance Criteria

| ID | Observable criterion | Verification method |
|---|---|---|
| AC-101 | 결제 완료 이벤트 발생 시 고객사의 등록 HTTPS endpoint로 `payment.completed` 요청이 전송된다. | 통합 테스트 |
| AC-102 | 전송 payload에 `event_id`, `event_type`, `created_at`, `customer_id`, `payment_id`, `status`, `completed_at`이 포함된다. | API 계약 테스트 |
| AC-103 | 고객사 endpoint가 네트워크 오류를 반환하면 즉시 성공 처리하지 않고 재시도 예약 상태가 된다. | 통합 테스트 |
| AC-104 | 재시도 간격이 이전 시도보다 증가하는 지수 백오프 방식으로 계산된다. | 단위 테스트 |
| AC-105 | 동일 이벤트 재전달 시 `event_id`가 변경되지 않는다. | 단위/통합 테스트 |
| AC-106 | A 고객사의 결제 완료 이벤트가 B 고객사의 endpoint로 전달되지 않는다. | 격리 테스트 |
| AC-107 | endpoint가 없는 고객사는 전달 시도 없이 `skipped` 또는 동등한 내부 상태로 기록된다. | 통합 테스트 |
| AC-108 | replay 대시보드 또는 수동 재전송 API가 1차 출시 범위에 포함되지 않는다. | 범위 검증 |
| AC-109 | 서명 검증 미확정 상태가 API 문서에 열린 결정으로 명시되어 있다. | 문서 검토 |
| AC-110 | 결제 완료 처리 성공 여부가 고객사 webhook 응답 실패에 의해 롤백되지 않는다. | 통합 테스트 |

## 10. Reasonable Assumptions

- 결제 완료 이벤트는 내부 결제 시스템에서 신뢰 가능한 “완료 확정” 상태 이후 발생한다.
- endpoint 등록, 수정, 비활성화는 기존 내부 API가 이미 담당한다.
- 1차 출시에서는 단일 고객사당 하나 이상의 endpoint 가능 여부가 확정되지 않았으므로, 구현은 최소 단일 endpoint를 지원하고 확장 가능성을 고려한다.
- `2xx` HTTP 응답을 전달 성공으로 간주한다.
- 고객사는 `event_id`를 이용해 자체적으로 멱등 처리를 한다.
- 웹훅 전달 실패는 결제 완료 상태 자체를 변경하지 않는다.
- 운영자는 DB, 로그, 내부 관측 도구 등을 통해 전달 실패를 확인할 수 있으나, 별도 replay UI는 없다.

## 11. Open Decisions

| ID | Decision | Owner |
|---|---|---|
| OD-101 | 웹훅 서명 방식: HMAC 알고리즘, header 이름, timestamp 포함 여부, canonical string 정의 | 보안 담당자 |
| OD-102 | secret rotation 주기와 dual-secret 허용 기간 | 보안 담당자 |
| OD-103 | 최대 재시도 횟수, 최대 retry window, dead-letter 처리 방식 | 플랫폼/운영 |
| OD-104 | HTTP timeout 기본값 | 플랫폼/운영 |
| OD-105 | 성공으로 인정할 HTTP status 범위 | 플랫폼/운영 |
| OD-106 | 고객사당 다중 endpoint 지원 여부 | 제품/플랫폼 |
| OD-107 | payload에 포함할 금액, 통화, 주문 ID, 사용자 식별자 등 상세 필드 범위 | 제품/보안 |
| OD-108 | 처리량 및 지연 목표 수립 여부와 측정 기간 | 제품/플랫폼 |
| OD-109 | 최종 실패 건의 알림 채널 또는 에스컬레이션 정책 | 운영 |

## 12. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| 서명 정책 미정으로 고객사 보안 검증이 지연될 수 있음 | High | 1차 API 구조에 signature header 확장 지점을 남기고, 보안 결정 전 외부 GA 범위를 제한 |
| at-least-once 특성으로 고객사가 중복 처리할 수 있음 | High | `event_id`를 필수 제공하고 문서에 중복 가능성 명시 |
| retry 폭증으로 내부 큐 또는 고객사 endpoint에 부하 발생 가능 | Medium | 지수 백오프, 최대 재시도 한도, timeout 적용 |
| 고객사 데이터가 다른 endpoint로 전달될 경우 심각한 데이터 유출 발생 | High | tenant scope 검증, 격리 테스트, delivery 기록의 customer binding 강제 |
| SLA 수치가 없어 출시 품질 판단이 어려움 | Medium | 1차 출시에서 처리량, 지연, 실패율 메트릭을 수집하고 이후 SLA 확정 |

## 13. Delivery Outline

1. 이벤트 모델 정의: `event_id`, `event_type`, `customer_id`, payload, 상태.
2. 결제 완료 이벤트 발행 지점 연결.
3. 고객사 endpoint 조회 및 HTTPS 검증.
4. webhook delivery worker 구현.
5. delivery attempt 기록 및 상태 전이 구현.
6. 지수 백오프 retry scheduler 구현.
7. tenant/customer 격리 검증 추가.
8. API 계약 문서 작성: 중복 전달, `event_id`, 성공 응답 기준, 서명 미정 명시.
9. 관측 지표 추가: 생성, 성공, 재시도, 최종 실패, skipped.
10. 출시 전 열린 결정 중 Must 항목 확정: retry 한도, timeout, 성공 status 범위.