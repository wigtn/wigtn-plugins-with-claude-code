# 결제 완료 웹훅 전달 API PRD

## Context And Problem

결제가 완료되면 고객사가 등록한 HTTPS endpoint로 결제 완료 이벤트를 전달해야 한다. 고객사는 이 이벤트를 통해 자체 주문 상태 변경, 서비스 활성화, 회계 처리 등 후속 처리를 수행한다.

웹훅 전달은 네트워크 실패, 고객사 서버 장애, 중복 전달 가능성을 전제로 설계되어야 한다. 1차 출시 범위에는 UI, replay 대시보드, 수동 재전송 기능이 포함되지 않는다.

## Goals

- 결제 완료 시 등록된 고객사 HTTPS endpoint로 이벤트를 자동 전달한다.
- 최소 1회 전달을 보장한다.
- 네트워크 실패 또는 일시적 전달 실패 시 지수 백오프로 재시도한다.
- 고객사가 중복 이벤트를 안전하게 처리할 수 있도록 고유 `event_id`를 제공한다.
- 고객사별 데이터 격리를 보장한다.
- 서명 검증 방식과 secret rotation 정책이 확정되지 않았더라도 추후 적용 가능한 구조로 구현한다.

## Non-Goals

- endpoint 등록 UI 제공
- endpoint 등록 내부 API 신규 구현 또는 변경
- replay 대시보드
- 운영자 수동 재전송 기능
- 처리량, 지연 시간 SLA 수치 정의
- 서명 알고리즘 또는 secret rotation 주기 최종 결정
- 고객사 SDK 제공

## Users And Key Scenarios

- 고객사 개발자: 결제 완료 이벤트를 받아 고객사 시스템의 주문 또는 구독 상태를 갱신한다.
- 내부 결제 시스템: 결제 완료 상태 전환 후 웹훅 이벤트 생성을 요청한다.
- 내부 운영/개발팀: 전달 실패, 재시도 상태, 고객사별 이벤트 격리 여부를 로그와 데이터로 확인한다.

주요 시나리오:

1. 결제가 완료된다.
2. 시스템은 해당 고객사의 등록된 HTTPS endpoint를 조회한다.
3. 결제 완료 이벤트를 생성하고 고유 `event_id`를 부여한다.
4. 시스템은 고객사 endpoint로 HTTPS POST 요청을 보낸다.
5. 고객사 endpoint가 성공 응답을 반환하면 전달을 완료 처리한다.
6. 네트워크 실패 또는 실패 응답이면 지수 백오프 정책에 따라 재시도한다.
7. 같은 이벤트가 여러 번 전달될 수 있으므로 고객사는 `event_id`로 멱등 처리한다.

## Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-101 | 결제 상태가 완료로 확정되면 결제 완료 웹훅 이벤트를 생성해야 한다. | Must |
| FR-102 | 각 이벤트에는 전역적으로 고유한 `event_id`가 포함되어야 한다. | Must |
| FR-103 | 웹훅 payload에는 이벤트 타입, 이벤트 생성 시각, 고객사 식별자, 결제 식별자, 결제 완료 시각, 결제 결과에 필요한 최소 데이터를 포함해야 한다. | Must |
| FR-104 | 시스템은 기존 내부 API를 통해 등록된 고객사별 HTTPS endpoint를 사용해야 한다. | Must |
| FR-105 | HTTP가 아닌 endpoint는 전달 대상에서 제외하거나 등록 단계에서 이미 거부된 것으로 간주해야 하며, 전달 API는 HTTPS endpoint만 호출해야 한다. | Must |
| FR-106 | 결제 완료 이벤트는 해당 결제의 고객사 endpoint로만 전달되어야 한다. | Must |
| FR-107 | 고객사별 이벤트, 전달 시도, 재시도 상태는 다른 고객사 데이터와 논리적으로 격리되어야 한다. | Must |
| FR-108 | 최초 전달 실패 시 지수 백오프 방식으로 자동 재시도해야 한다. | Must |
| FR-109 | 재시도는 같은 `event_id`를 유지해야 한다. | Must |
| FR-110 | 동일 이벤트가 여러 번 전달될 수 있음을 전제로 최소 1회 전달 방식을 사용해야 한다. | Must |
| FR-111 | 고객사 endpoint가 성공으로 간주되는 응답을 반환하면 해당 이벤트 전달을 완료 상태로 기록해야 한다. | Must |
| FR-112 | 고객사 endpoint 호출 결과, HTTP status, 오류 유형, 시도 횟수, 다음 재시도 예정 시각을 기록해야 한다. | Must |
| FR-113 | 재시도 한도 또는 만료 정책은 설정값으로 분리해야 하며, 하드코딩하지 않아야 한다. | Should |
| FR-114 | 서명 검증 방식이 확정되기 전이라도, 향후 요청 서명 헤더와 고객사별 secret을 적용할 수 있도록 전달 요청 생성부를 확장 가능하게 구성해야 한다. | Should |
| FR-115 | endpoint가 등록되어 있지 않은 고객사의 결제 완료 이벤트는 외부 호출 없이 미전달 사유를 기록해야 한다. | Must |
| FR-116 | 1차 출시에서는 replay 대시보드와 수동 재전송 API를 제공하지 않아야 한다. | Must |

## Event Payload Contract

초기 payload 필드 예시:

```json
{
  "event_id": "evt_...",
  "event_type": "payment.completed",
  "created_at": "2026-07-27T12:34:56Z",
  "customer_id": "cus_...",
  "payment_id": "pay_...",
  "payment_completed_at": "2026-07-27T12:34:50Z",
  "data": {
    "amount": 10000,
    "currency": "KRW",
    "status": "completed"
  }
}
```

요구사항:

- `event_id`는 재시도 간 변경되지 않는다.
- `event_type`의 최초 값은 `payment.completed`로 한다.
- payload에는 다른 고객사의 데이터가 포함되면 안 된다.
- 민감정보, 카드 원문 정보, 인증 정보는 포함하지 않는다.
- 필드 추가는 하위 호환 방식으로만 수행한다.

## Delivery Semantics

- 전달 방식: HTTPS POST
- 보장 수준: 최소 1회 전달
- 중복 가능성: 있음
- 고객사 멱등 처리 기준: `event_id`
- 실패 시 처리: 지수 백오프 재시도
- 성공 판정: 열린 결정 `OD-102` 참조
- 재시도 종료 조건: 열린 결정 `OD-103` 참조

## UX, Roles, Routes, And States

UI는 이번 범위에 없다.

API/시스템 상태는 다음을 지원해야 한다.

| State | Description |
|---|---|
| `pending` | 이벤트 생성 후 아직 전달 시도 전 |
| `delivering` | 전달 시도 중 |
| `delivered` | 성공 응답을 받아 완료 처리됨 |
| `retry_scheduled` | 실패 후 다음 재시도 예정 |
| `failed_terminal` | 재시도 정책상 더 이상 자동 재시도하지 않음 |
| `skipped_no_endpoint` | 등록된 endpoint가 없어 외부 호출하지 않음 |

## Non-Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| NFR-101 | 고객사별 데이터 접근은 tenant/customer boundary를 기준으로 제한되어야 한다. | Must |
| NFR-102 | 로그와 저장 데이터에 secret, 인증 토큰, 민감 결제 정보가 노출되면 안 된다. | Must |
| NFR-103 | 처리량과 지연 SLA는 이번 PRD에서 수치화하지 않는다. 출시 전 관측 지표를 수집할 수 있어야 한다. | Must |
| NFR-104 | 이벤트 생성, 전달 시도, 성공, 실패, 재시도 예약은 관측 가능한 로그 또는 메트릭으로 남아야 한다. | Must |
| NFR-105 | 재시도 워커가 일시 중단되어도 저장된 상태를 기준으로 재개할 수 있어야 한다. | Must |
| NFR-106 | 웹훅 전달은 결제 완료 트랜잭션의 정합성을 훼손하지 않아야 한다. 외부 endpoint 장애가 결제 완료 자체를 롤백시키면 안 된다. | Must |
| NFR-107 | 고객사 endpoint 응답 지연이 시스템 리소스를 무기한 점유하지 않도록 요청 timeout을 설정해야 한다. | Must |

## Acceptance Criteria

| ID | Maps To | Observable Criterion | Verification Method |
|---|---|---|---|
| AC-101 | FR-101, FR-102 | 결제 완료 처리 후 `payment.completed` 이벤트가 생성되고 고유 `event_id`가 저장된다. | 단위/통합 테스트 |
| AC-102 | FR-104, FR-106 | 고객사 A 결제 이벤트는 고객사 A의 등록 endpoint로만 전달된다. | 통합 테스트 |
| AC-103 | FR-107, NFR-101 | 고객사 A의 이벤트 조회 또는 처리 경로에서 고객사 B의 이벤트가 노출되지 않는다. | 권한/격리 테스트 |
| AC-104 | FR-108, FR-109 | 최초 전달 실패 후 다음 재시도가 예약되며 재시도 payload의 `event_id`가 동일하다. | 통합 테스트 |
| AC-105 | FR-111 | 성공 응답을 받은 이벤트는 `delivered` 상태로 변경되고 추가 재시도가 예약되지 않는다. | 통합 테스트 |
| AC-106 | FR-112 | 전달 실패 시 오류 유형, HTTP status 또는 네트워크 오류, 시도 횟수, 다음 재시도 예정 시각이 기록된다. | 통합 테스트/로그 검증 |
| AC-107 | FR-115 | endpoint가 없는 고객사의 이벤트는 외부 HTTP 호출 없이 `skipped_no_endpoint` 상태 또는 동등한 사유로 기록된다. | 통합 테스트 |
| AC-108 | NFR-102 | 로그와 저장된 전달 기록에 secret, 인증 토큰, 카드 원문 정보가 포함되지 않는다. | 보안 테스트/로그 샘플 검토 |
| AC-109 | NFR-106 | 고객사 endpoint 장애가 발생해도 결제 완료 상태는 유지된다. | 장애 주입 테스트 |
| AC-110 | FR-116 | replay 대시보드와 수동 재전송 기능이 노출되지 않는다. | API/라우트 검증 |

## Reasonable Assumptions

| ID | Assumption |
|---|---|
| A-101 | 결제 완료 상태는 기존 결제 시스템에서 신뢰 가능한 단일 이벤트 또는 상태 전환으로 감지할 수 있다. |
| A-102 | endpoint 등록과 고객사 식별 정보는 기존 내부 API 또는 저장소에서 조회 가능하다. |
| A-103 | 고객사 endpoint는 HTTPS POST JSON 요청을 받을 수 있다. |
| A-104 | 고객사는 `event_id`를 저장해 멱등 처리를 수행할 책임이 있다. |
| A-105 | 1차 출시는 단일 이벤트 타입 `payment.completed`만 대상으로 한다. |
| A-106 | 내부 운영자는 DB, 로그, 메트릭 등 기존 운영 도구로 상태를 확인할 수 있으며 별도 UI는 필요하지 않다. |
| A-107 | 서명 방식 미확정 상태에서도, 서명 적용 전까지는 네트워크 계층의 HTTPS와 고객사 endpoint 등록 통제를 기본 보안 장치로 사용한다. 단, 프로덕션 출시 전 보안 승인 필요 여부는 열린 결정으로 둔다. |

## Open Decisions

| ID | Decision Needed | Owner |
|---|---|---|
| OD-101 | 웹훅 서명 알고리즘, 서명 대상 문자열, 헤더 이름, timestamp 허용 오차를 결정해야 한다. | 보안 담당자 |
| OD-102 | 성공 응답으로 인정할 HTTP status 범위를 결정해야 한다. 예: 2xx 전체 또는 특정 status. | 제품/엔지니어링 |
| OD-103 | 최대 재시도 횟수, 최대 재시도 기간, terminal failure 전환 기준을 결정해야 한다. | 제품/엔지니어링 |
| OD-104 | secret rotation 주기와 dual-secret 허용 기간을 결정해야 한다. | 보안 담당자 |
| OD-105 | payload에 포함할 결제 상세 필드의 최종 범위를 결정해야 한다. | 제품/결제 도메인 담당 |
| OD-106 | 처리량과 지연 목표는 실제 관측 데이터 수집 후 별도 SLA/SLO로 정의해야 한다. | 제품/엔지니어링 |
| OD-107 | 실패 이벤트의 운영 알림 기준을 정해야 한다. 예: terminal failure 발생 시, 특정 고객사 연속 실패 시. | 운영/엔지니어링 |

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| 중복 전달로 고객사 시스템이 중복 처리함 | 고객사 주문/권한 상태 오류 | `event_id`를 필수 제공하고 문서에 멱등 처리 요구 명시 |
| 고객사 endpoint 장애가 장기화됨 | 이벤트 전달 지연 및 재시도 적체 | 지수 백오프, 재시도 한도 설정값, terminal 상태 기록 |
| 서명 방식 미확정 | 보안 승인 지연 또는 출시 차단 | 서명 적용 지점을 구조적으로 분리하고 OD-101/OD-104를 출시 전 결정 항목으로 관리 |
| 고객사 데이터 혼입 | 심각한 데이터 유출 | tenant/customer boundary 기반 조회, 저장, 전달 테스트 필수화 |
| 근거 없는 SLA 설정 | 잘못된 기대치와 운영 부담 | 1차 출시는 관측 지표 수집만 요구하고 SLA 수치는 정의하지 않음 |

## Delivery Outline

1. 이벤트 모델 정의
   - `event_id`, `customer_id`, `event_type`, payload, 상태, 생성 시각 저장
2. 결제 완료 이벤트 생성 연결
   - 결제 완료 상태 전환 후 `payment.completed` 이벤트 생성
3. endpoint 조회 및 전달 워커 구현
   - 고객사별 HTTPS endpoint 조회
   - POST JSON 요청
   - timeout 적용
4. 전달 결과 기록
   - 성공, 실패, HTTP status, 오류 유형, 시도 횟수 저장
5. 재시도 스케줄링
   - 지수 백오프
   - 설정 기반 retry limit
   - 동일 `event_id` 유지
6. 데이터 격리 및 보안 검증
   - 고객사 boundary 테스트
   - 민감정보 로그 검증
7. 관측성 추가
   - 이벤트 생성 수
   - 전달 성공/실패 수
   - 재시도 예약 수
   - terminal failure 수
   - 지연 시간은 측정만 하고 SLA로 해석하지 않음

## Out Of Scope For First Release

- replay 대시보드
- 수동 재전송
- endpoint 등록 UI
- 고객사별 웹훅 설정 화면
- 고객사 SDK
- SLA 수치 공표
- secret rotation 자동화, 단 보안 결정 후 별도 구현 가능하도록 확장점은 유지한다.