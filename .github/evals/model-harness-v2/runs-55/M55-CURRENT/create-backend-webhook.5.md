# 결제 완료 웹훅 전달 API PRD

## Context and Problem

결제가 완료되면 고객사가 사전에 등록한 HTTPS endpoint로 결제 완료 이벤트를 전달해야 한다. 고객사는 이 이벤트를 기반으로 주문 확정, 서비스 활성화, 내부 정산 처리 등을 수행할 수 있다.

웹훅 전달은 네트워크 실패, 고객사 endpoint 장애, 중복 전달 가능성을 전제로 설계되어야 한다. 1차 출시 범위에서는 UI, replay 대시보드, 수동 재전송 기능은 포함하지 않는다.

## Goals

- 결제 완료 시 등록된 고객사 HTTPS endpoint로 이벤트를 전달한다.
- 최소 1회 전달(at-least-once delivery)을 보장한다.
- 네트워크 실패 또는 일시적 전달 실패 시 지수 백오프로 자동 재시도한다.
- 고객사가 중복 이벤트를 안전하게 처리할 수 있도록 고유한 event ID를 제공한다.
- 고객사별 데이터 격리를 보장한다.
- 보안 담당자가 최종 결정할 서명 검증 방식과 secret rotation 정책을 수용할 수 있는 구조를 마련한다.

## Non-goals

- 웹훅 endpoint 등록 UI
- 웹훅 endpoint 등록 API 신규 구현
- replay 대시보드
- 운영자 또는 고객사 수동 재전송 기능
- 처리량, 지연 시간 SLA 수치 정의
- 결제 완료 외 이벤트 타입 지원
- 고객사 endpoint의 비즈니스 처리 성공 여부 보장

## Users and Key Scenarios

- 고객사 시스템: 결제 완료 이벤트를 수신하고 내부 시스템에 반영한다.
- 결제 플랫폼 백엔드: 결제 완료 상태 전환을 감지하고 웹훅 이벤트를 생성 및 전달한다.
- 내부 운영자: 1차 출시에서는 UI 없이 로그와 운영 관측 도구를 통해 전달 상태를 확인한다.
- 보안 담당자: 서명 검증 방식과 secret rotation 정책을 확정한다.

핵심 시나리오:

1. 결제가 완료된다.
2. 시스템은 해당 고객사의 등록된 HTTPS endpoint를 조회한다.
3. 결제 완료 이벤트를 고유 event ID와 함께 생성한다.
4. 고객사 endpoint로 HTTPS 요청을 보낸다.
5. 고객사 endpoint가 성공 응답을 반환하면 전달을 완료 처리한다.
6. 네트워크 오류 또는 실패 응답이면 지수 백오프로 재시도한다.
7. 같은 event ID가 여러 번 전달될 수 있으므로 고객사는 event ID 기준으로 멱등 처리한다.

## Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-101 | 결제가 완료 상태로 확정되면 결제 완료 웹훅 이벤트를 생성해야 한다. | Must |
| FR-102 | 이벤트에는 전역적으로 고유한 `event_id`가 포함되어야 한다. | Must |
| FR-103 | 동일 결제 완료 건에 대해 재시도되는 전달은 동일한 `event_id`를 사용해야 한다. | Must |
| FR-104 | 이벤트에는 고객사 식별자, 결제 식별자, 이벤트 타입, 이벤트 생성 시각이 포함되어야 한다. | Must |
| FR-105 | 이벤트 타입은 1차 출시에서 결제 완료만 지원한다. 예: `payment.completed`. | Must |
| FR-106 | 시스템은 기존 내부 API를 통해 등록된 고객사 HTTPS endpoint를 조회해야 한다. | Must |
| FR-107 | 등록된 endpoint가 없거나 비활성 상태인 경우 외부 전달을 시도하지 않고 관측 가능한 실패 또는 스킵 상태를 기록해야 한다. | Must |
| FR-108 | endpoint URL은 HTTPS만 허용해야 한다. | Must |
| FR-109 | 웹훅 전달은 최소 1회 전달 방식이어야 한다. | Must |
| FR-110 | 네트워크 오류, timeout, 5xx 응답, 재시도 대상으로 분류된 실패 응답에는 지수 백오프 재시도를 수행해야 한다. | Must |
| FR-111 | 2xx 응답은 전달 성공으로 처리해야 한다. | Must |
| FR-112 | 4xx 응답의 재시도 여부는 정책으로 분리되어야 하며, 기본 정책은 열린 결정으로 남긴다. | Should |
| FR-113 | 재시도 횟수, 최대 재시도 기간, timeout 값은 설정 가능해야 하며 근거 없는 SLA 수치로 고정하지 않는다. | Must |
| FR-114 | 각 전달 시도는 attempt 단위로 기록되어야 한다. | Must |
| FR-115 | 이벤트 생성 상태, 전달 성공 상태, 재시도 대기 상태, 최종 실패 상태를 구분해 저장해야 한다. | Must |
| FR-116 | 고객사별 데이터는 조회, 저장, 처리, 로그 관점에서 격리되어야 한다. | Must |
| FR-117 | 한 고객사의 endpoint, secret, 이벤트, 전달 기록이 다른 고객사 요청 또는 처리 경로에서 접근되지 않아야 한다. | Must |
| FR-118 | 웹훅 payload에는 해당 고객사에 속한 결제 데이터만 포함해야 한다. | Must |
| FR-119 | 서명 헤더 또는 검증용 메타데이터를 추가할 수 있는 확장 지점을 제공해야 한다. | Must |
| FR-120 | 서명 검증 방식과 secret rotation 주기가 확정되기 전까지 특정 알고리즘이나 주기를 제품 요구사항으로 고정하지 않는다. | Must |
| FR-121 | replay 대시보드와 수동 재전송 기능은 1차 출시 API 및 운영 기능 범위에서 제외해야 한다. | Must |
| FR-122 | 전달 처리량과 지연 시간은 관측 가능하게 측정해야 하지만, 1차 출시 PRD에서는 SLA 수치를 정의하지 않는다. | Must |

## Event Payload Requirements

초기 payload는 구현팀이 기존 결제 도메인 모델과 개인정보 정책을 기준으로 확정하되, 최소 필드는 다음을 만족해야 한다.

```json
{
  "event_id": "evt_...",
  "event_type": "payment.completed",
  "created_at": "2026-07-27T00:00:00Z",
  "customer_id": "cus_...",
  "payment": {
    "payment_id": "pay_...",
    "status": "completed",
    "completed_at": "2026-07-27T00:00:00Z"
  }
}
```

payload 원칙:

- `event_id`는 고객사의 멱등 처리 기준이다.
- `event_type`은 1차 출시에서 `payment.completed`만 사용한다.
- payload에는 해당 고객사가 소유한 결제 정보만 포함한다.
- 민감정보, 카드 원문 정보, 불필요한 개인정보는 포함하지 않는다.
- 향후 필드 추가를 허용하되 기존 필드 의미를 깨지 않는다.

## UX, Roles, Routes, and States

UI는 이번 범위에 없다.

API 및 내부 상태는 다음을 지원해야 한다.

- `event_created`: 결제 완료 이벤트가 생성됨
- `delivery_pending`: 전달 대기 중
- `delivery_attempted`: 개별 전달 시도 기록됨
- `delivery_succeeded`: 고객사 endpoint가 성공 응답 반환
- `retry_scheduled`: 재시도 예약됨
- `delivery_failed`: 설정된 재시도 정책상 더 이상 자동 재시도하지 않음
- `delivery_skipped`: endpoint 미등록, 비활성, 또는 정책상 전달 불가

## Non-functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| NFR-101 | 웹훅 전달 요청은 HTTPS를 사용해야 한다. | Must |
| NFR-102 | 고객사별 endpoint, secret, 이벤트, 전달 기록은 tenant boundary를 기준으로 격리되어야 한다. | Must |
| NFR-103 | 전달 작업은 결제 완료 트랜잭션의 핵심 상태 확정을 불필요하게 지연시키지 않아야 한다. | Must |
| NFR-104 | 이벤트 생성과 전달 시도는 장애 복구 후에도 이어서 처리할 수 있도록 내구성 있게 저장되어야 한다. | Must |
| NFR-105 | 재시도 스케줄은 프로세스 재시작 후에도 유실되지 않아야 한다. | Must |
| NFR-106 | 각 전달 시도에 대해 endpoint, 응답 코드, 오류 유형, attempt 번호, 시각, 다음 재시도 예정 시각을 관측 가능하게 기록해야 한다. | Must |
| NFR-107 | 처리량과 지연 시간은 메트릭으로 수집해야 하며, SLA 수치는 실제 측정 후 별도 결정한다. | Must |
| NFR-108 | 로그에는 secret, 서명 원문 키, 민감 결제 정보가 남지 않아야 한다. | Must |
| NFR-109 | 동일 이벤트의 중복 전달 가능성을 문서화해야 한다. | Must |

## Acceptance Criteria

| ID | Observable criterion | Verification method |
|---|---|---|
| AC-101 | 결제가 완료되면 `payment.completed` 이벤트가 생성된다. | 결제 완료 시나리오 통합 테스트 |
| AC-102 | 생성된 이벤트마다 `event_id`가 존재하고 중복되지 않는다. | 단위 테스트 및 DB unique 제약 검증 |
| AC-103 | 동일 이벤트 재시도 시 payload의 `event_id`가 바뀌지 않는다. | 재시도 시나리오 테스트 |
| AC-104 | 등록된 HTTPS endpoint가 있는 고객사에는 웹훅 요청이 전송된다. | mock endpoint 통합 테스트 |
| AC-105 | endpoint가 2xx 응답을 반환하면 전달 상태가 성공으로 기록된다. | mock endpoint 응답 테스트 |
| AC-106 | 네트워크 오류 또는 timeout 발생 시 지수 백오프 재시도가 예약된다. | fault injection 테스트 |
| AC-107 | 재시도 예약 정보가 저장되고 프로세스 재시작 후에도 이어서 처리된다. | worker restart 테스트 |
| AC-108 | endpoint가 없거나 비활성인 고객사는 외부 요청 없이 스킵 또는 실패 상태가 기록된다. | endpoint 미등록 테스트 |
| AC-109 | HTTP endpoint는 전달 대상으로 사용되지 않는다. | endpoint 정책 테스트 |
| AC-110 | 고객사 A의 이벤트 처리 경로에서 고객사 B의 endpoint 또는 payload가 사용되지 않는다. | tenant isolation 테스트 |
| AC-111 | payload에는 해당 고객사의 결제 데이터만 포함된다. | 권한 및 fixture 기반 통합 테스트 |
| AC-112 | 로그와 전달 기록에 secret 또는 민감 결제 정보가 노출되지 않는다. | 로그 스냅샷/보안 테스트 |
| AC-113 | replay 대시보드와 수동 재전송 API 또는 UI가 1차 출시 산출물에 포함되지 않는다. | 범위 검토 |
| AC-114 | 처리량 및 지연 메트릭은 수집되지만 SLA 수치 알림 기준은 PRD에서 임의로 고정하지 않는다. | 메트릭 존재 검증 및 설정 검토 |

## Reasonable Assumptions

- 결제 완료 상태는 기존 결제 시스템에서 신뢰 가능한 단일 상태 전환으로 제공된다.
- endpoint 등록과 활성화 여부 관리는 기존 내부 API가 담당한다.
- 고객사는 중복 웹훅을 받을 수 있다는 계약을 수용하고 `event_id` 기준 멱등 처리를 구현한다.
- 웹훅 전달 성공 여부는 고객사 endpoint의 HTTP 응답 기준으로 판단한다.
- 1차 출시에서는 결제 완료 이벤트만 발행하므로 이벤트 스키마 버전 관리는 최소화하되, 향후 확장을 막지 않는다.
- 운영자는 1차 출시에서 대시보드 대신 로그, 메트릭, 내부 관측 도구로 상태를 확인한다.

## Open Decisions

| ID | Decision | Owner | Needed by |
|---|---|---|---|
| OD-101 | 웹훅 서명 알고리즘, 헤더 이름, timestamp 포함 여부, replay 방지 방식 | 보안 담당자 | 외부 고객사 연동 문서 확정 전 |
| OD-102 | secret rotation 주기와 다중 secret 유효 기간 | 보안 담당자 | 운영 정책 확정 전 |
| OD-103 | 4xx 응답 중 재시도 대상 분류 여부 | 제품/백엔드/운영 | 재시도 정책 구현 전 |
| OD-104 | 최대 재시도 횟수, 최대 재시도 기간, timeout 기본값 | 백엔드/운영 | 배포 설정 확정 전 |
| OD-105 | 최종 실패 이벤트의 운영 알림 방식 | 운영/백엔드 | 운영 런북 작성 전 |
| OD-106 | 고객사에 제공할 공식 웹훅 연동 문서 범위 | 제품/개발자 경험 | 고객사 베타 시작 전 |
| OD-107 | 실제 측정 후 처리량과 지연 SLA를 정의할지 여부 | 제품/운영 | 1차 출시 이후 관측 데이터 확보 후 |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| 고객사 endpoint 장애로 재시도 작업이 누적됨 | 전달 지연, 큐 적체 | 재시도 백오프, 최대 재시도 정책, 메트릭 수집 |
| 중복 전달로 고객사 시스템이 중복 처리함 | 고객사 데이터 오류 | `event_id` 제공, 멱등 처리 문서화 |
| tenant boundary 오류로 다른 고객사 데이터가 전달됨 | 중대한 보안 사고 | tenant-scoped 조회, 테스트, 로그 검증 |
| 서명 방식 미확정으로 고객사 보안 연동이 지연됨 | 출시 또는 연동 지연 | 서명 확장 지점 마련, 보안 결정 항목 분리 |
| SLA 수치 없이 운영 기대치가 불명확함 | 고객사 커뮤니케이션 리스크 | 1차 출시에서 메트릭 수집 후 근거 기반 SLA 결정 |

## Delivery Outline

1. 이벤트 모델 및 전달 상태 모델 정의
2. 결제 완료 상태 전환에서 `payment.completed` 이벤트 생성
3. 기존 내부 API를 통한 고객사 endpoint 조회 연동
4. HTTPS endpoint 검증 및 tenant-scoped 전달 처리
5. 전달 worker 및 지수 백오프 재시도 구현
6. 전달 attempt 기록, 상태 전이, 메트릭/로그 추가
7. 서명 확장 지점 추가
8. 통합 테스트, 실패 시나리오 테스트, tenant isolation 테스트 작성
9. 고객사 중복 전달 및 `event_id` 멱등 처리 안내 문서 초안 작성

## Out of Scope Confirmation

1차 출시에는 다음이 포함되지 않는다.

- endpoint 등록 UI
- replay 대시보드
- 수동 재전송 기능
- 처리량 또는 지연 SLA 숫자 약속
- 결제 완료 외 이벤트 타입
- 보안 담당자가 확정하지 않은 서명 방식 또는 rotation 주기 강제 정의