# PRD — 온라인 강의 플랫폼 쿠폰 기능

> **Type**: product-feature
> **Feature Key**: coupon
> **Author**: contact@wigtn.com
> **Date**: 2026-08-03
> **Status**: Draft

---

## 1. Overview

### 1.1 Problem Statement
현재 플랫폼에는 가격 할인 수단이 없다. 관리자는 프로모션(신규 가입, 재구매, 특정 강의 홍보)을 진행하고 싶어도 개별 결제 금액을 조정할 방법이 없어, 수동 환불·별도 이체 같은 비정상 프로세스로 처리하고 있다. 이는 정산 오류와 CS 부하를 유발한다. 수강생 입장에서도 할인 혜택을 받을 표준 경로가 없다.

### 1.2 Goals
- 관리자가 UI에서 직접 쿠폰을 발행·관리(활성/비활성)할 수 있다.
- 수강생이 결제 화면에서 쿠폰 코드를 입력해 할인을 적용받을 수 있다.
- 동일 쿠폰의 **중복 사용(재사용)을 서버에서 원자적으로 차단**한다.
- **만료된 쿠폰**(기간·수량·비활성)의 적용을 차단한다.
- 쿠폰 적용 내역이 결제·정산 데이터와 정합성 있게 기록된다.

### 1.3 Non-Goals
- **자동 발급/트리거 쿠폰**(가입 즉시 자동 지급, 이벤트 기반 자동 발급)은 이번 범위 밖 — 관리자 수동 발행만 다룬다.
- **1인 다회 사용(perUserLimit ≥ 2) 쿠폰**은 이번 범위 밖 — v1은 `perUserLimit=1` 고정.
- **쿠폰 간 중복 적용(스태킹)**은 지원하지 않는다 — 결제당 쿠폰 1장.
- **적립금/포인트/멤버십** 등 쿠폰 외 할인 수단은 다루지 않는다.
- **프로모션 코드 대량 자동 생성/CSV 업로드**는 이번 범위 밖(Phase 이후 과제).
- **결제 게이트웨이(PG) 연동 자체**는 기존 결제 시스템을 전제로 하며 이 PRD의 신규 구현 대상이 아니다 — 최종 결제 금액 전달 인터페이스만 정의한다.

### 1.4 Scope
| 포함 | 제외 |
|---|---|
| 관리자 쿠폰 CRUD(발행/조회/비활성화) | 쿠폰 자동 발급 |
| 정액/정률 할인 타입 | 쿠폰 스태킹 |
| 결제 시 쿠폰 검증·적용 API | 포인트/적립금 |
| 중복 사용 방지(원자적 사용 처리) | PG 신규 연동 |
| 만료(기간/수량/상태) 검증 | 대량 코드 생성 |
| 쿠폰 사용 이력 기록 | 다국가/다통화 |

---

## 2. User Stories

### 2.1 Primary User
- **관리자(admin)**: As an admin, I want to 할인 조건과 유효기간·수량이 정해진 쿠폰을 발행하고 싶다 so that 통제된 프로모션을 정산 오류 없이 운영할 수 있다.
- **수강생(student)**: As a student, I want to 결제 시 쿠폰 코드를 입력해 할인을 적용받고 싶다 so that 더 저렴하게 강의를 구매할 수 있다.

### 2.2 Acceptance Criteria

**AC-1 (쿠폰 발행 — 정상)**
```gherkin
Given 관리자로 로그인한 상태에서
When 코드 "WELCOME10", 할인 정률 10%, 유효기간 2026-08-01~2026-08-31, 총 수량 1000장으로 발행하면
Then 쿠폰이 status=active 로 생성되고 목록에 노출된다
```

**AC-2 (쿠폰 발행 — 코드 중복 실패)**
```gherkin
Given 이미 코드 "WELCOME10"이 존재할 때
When 관리자가 동일 코드로 다시 발행하면
Then 409 Conflict 와 "이미 존재하는 쿠폰 코드입니다" 메시지를 받고 생성되지 않는다
```

**AC-3 (쿠폰 적용 — 정상)**
```gherkin
Given 결제 대상 강의 금액이 50,000원이고 쿠폰 "WELCOME10"(10%)이 유효할 때
When 수강생이 결제 화면에서 해당 코드를 적용하면
Then 할인액 5,000원이 계산되어 최종 결제금액 45,000원이 미리보기로 표시된다
```

**AC-4 (쿠폰 적용 — 만료: 기간)**
```gherkin
Given 오늘이 2026-09-01 이고 쿠폰 유효기간이 2026-08-31 까지일 때
When 수강생이 해당 코드를 적용하면
Then 422 와 "만료된 쿠폰입니다" 메시지를 받고 할인이 적용되지 않는다
```

**AC-5 (쿠폰 적용 — 만료: 수량 소진)**
```gherkin
Given 총 발행 수량이 소진(remaining=0)된 쿠폰일 때
When 수강생이 해당 코드를 적용하면
Then 422 와 "쿠폰이 모두 소진되었습니다" 메시지를 받는다
```

**AC-6 (쿠폰 적용 — 비활성 상태)**
```gherkin
Given 관리자가 status=inactive 로 비활성화한 쿠폰일 때
When 수강생이 해당 코드를 적용하면
Then 422 와 "사용할 수 없는 쿠폰입니다" 메시지를 받는다
```

**AC-7 (중복 사용 방지 — 동일 유저 재사용)**
```gherkin
Given 수강생 A가 이미 쿠폰 "WELCOME10"으로 결제를 완료한 상태에서
When A가 같은 쿠폰을 다시 적용(미리보기)하려 하면
Then validate 는 422 와 reason=ALREADY_USED("이미 사용한 쿠폰입니다")를 반환한다
And 결제 확정(redeem) 단계에서 재사용이 시도되면 유니크 제약 위반으로 409 를 반환하고 사용되지 않는다
```
> 상태코드 규약: 미리보기(validate)는 검증 실패를 422(reason 포함)로 통일하고, 확정(redeem)의 동시성·중복 경합 패배만 409로 구분한다.

**AC-8 (중복 사용 방지 — 동시 결제 경합)**
```gherkin
Given 잔여 수량이 1장인 쿠폰에 두 결제 요청이 동시에 확정을 시도할 때
When 두 요청이 거의 동시에 사용 처리를 시도하면
Then 정확히 1건만 성공하고, 나머지는 409 를 받아 잔여 수량이 음수가 되지 않는다
```

**AC-9 (권한 부족)**
```gherkin
Given 수강생(student) 권한으로 로그인한 상태에서
When 쿠폰 발행 API(POST /admin/coupons)를 호출하면
Then 403 Forbidden 을 받고 쿠폰이 생성되지 않는다
```

**AC-10 (최소 결제 금액 미달)**
```gherkin
Given 쿠폰 최소 주문금액 조건이 30,000원이고 결제 대상 금액이 20,000원일 때
When 수강생이 해당 코드를 적용하면
Then 422 와 "최소 주문금액 30,000원 이상부터 사용 가능합니다" 메시지를 받는다
```

### 2.3 User Roles
| Role Key | 한국어 명칭 | 권한 범위 |
|---|---|---|
| admin | 관리자 | 쿠폰 발행/수정/비활성화/전체 사용 이력 조회 |
| student | 수강생 | 결제 시 본인 쿠폰 적용, 본인 사용 이력 조회 |
| guest | 비로그인 방문자 | 쿠폰 기능 접근 불가(결제 진입 전 로그인 필요) |

---

## 3. Functional Requirements

| ID | Requirement | Priority | Dependencies |
|---|---|---|---|
| FR-001 | 관리자는 쿠폰을 발행할 수 있다(코드, 할인타입 fixed/percentage, 할인값, 유효기간 시작/종료, 총 수량, 최소 주문금액, 최대 할인액 상한). | P0 | — |
| FR-002 | 쿠폰 코드는 시스템 전역에서 유일해야 하며 중복 발행은 거부된다. | P0 | FR-001 |
| FR-003 | 관리자는 쿠폰 목록을 상태·기간별로 조회할 수 있다. | P1 | FR-001 |
| FR-004 | 관리자는 쿠폰을 비활성화(status=inactive)할 수 있으며, 이후 적용이 차단된다. | P0 | FR-001 |
| FR-005 | 수강생은 결제 전 쿠폰 코드를 입력해 할인 적용 결과(할인액·최종금액)를 미리 볼 수 있다(미확정 검증). | P0 | FR-001 |
| FR-006 | 시스템은 쿠폰 적용 시 유효성(상태·기간·수량·최소금액)을 검증한다. | P0 | FR-005 |
| FR-007 | 시스템은 결제 확정 시 쿠폰 사용을 **원자적으로** 기록하고 잔여 수량을 차감한다. | P0 | FR-006 |
| FR-008 | 동일 수강생이 동일 쿠폰을 두 번 사용하는 것을 차단한다. 이번 범위에서 `perUserLimit=1`(1인 1회)로 고정하며, 유니크 제약으로 강제한다(perUserLimit≥2는 Non-Goal, §1.2 이후 과제). | P0 | FR-007 |
| FR-009 | 동시 결제 경합 시에도 잔여 수량이 음수가 되지 않도록 보장한다. | P0 | FR-007 |
| FR-010 | 할인 계산은 정률 시 최대 할인액 상한을 적용하고, 최종 금액은 0원 미만이 되지 않는다. | P0 | FR-005 |
| FR-011 | 쿠폰 사용 이력(누가/언제/어떤 결제에)을 기록하고 조회할 수 있다. | P1 | FR-007 |
| FR-012 | 결제 취소/환불 시 쿠폰 사용을 복원한다: 해당 redemption을 status=refunded로 전이하고 잔여 수량을 +1 복구한다. **복구는 멱등**해야 하며(이미 refunded면 재복원 금지), `remaining_quantity`는 `total_quantity`를 초과하지 않는다. | P1 | FR-007 |

> FR 간 무모순 확인: guest는 쿠폰 기능 접근 불가(§2.3) ↔ FR-005/006/007 모두 인증 사용자(student) 전제 — 모순 없음. FR-007(원자적 사용)과 FR-012(복원)는 상태 전이(used → refunded)로 양립.

---

## 4. Non-Functional Requirements

### 4.0 Scale Grade
**Startup** — 온라인 강의 플랫폼의 결제 부가 기능으로, 예상 DAU 1,000~10,000 구간. 프로모션 기간에 결제 트래픽이 집중되나 상시 대규모 동시성은 아님. (근거 미확정 시 상향 검토 가능.)

### 4.1 Performance
- 쿠폰 검증(미리보기) API: p95 < 200ms, p99 < 400ms.
- 쿠폰 사용 확정(원자적 차감 포함): p95 < 300ms.
- 프로모션 피크 처리량: 100 req/s(쿠폰 검증), 30 req/s(사용 확정) 지속 처리.
- 동시성: 단일 쿠폰에 대한 동시 확정 요청 50건에서도 수량 정합성 100% 유지.

### 4.2 Availability
- 목표 가용성 99.9%(월 다운타임 ≤ ~43분).
- 쿠폰은 부가 기능이므로 **결제 진입/확정 자체를 막지 않는다**(graceful degradation). 폴백 경계는 단계로 나눈다:
  - **확정 이전(validate/미리보기 단계) 쿠폰 서비스 장애**: 할인 미적용(할인액 0)으로 폴백해 결제를 그대로 진행한다.
  - **확정(redeem) 단계 실패**: redeem은 결제 확정과 동일 트랜잭션이므로, 사용자가 쿠폰 적용을 선택한 결제에서 redeem이 실패하면 **결제 전체를 롤백**하고 사용자에게 "쿠폰 없이 재시도" 또는 재시도를 안내한다(잘못된 금액으로 결제가 확정되는 것을 방지 — fail-closed). 즉 쿠폰 계층 장애가 결제를 자동 롤백시키는 것은 "쿠폰을 적용한 결제"에 한정되며, 쿠폰 미적용 결제는 영향받지 않는다.
- 어떤 경우에도 **부정 할인은 통과시키지 않는다**(fail-closed).

### 4.3 Data
- 쿠폰 사용 이력은 정산·회계 근거로 **최소 5년 보관**(전자상거래 거래기록 보존 정책 준수).
- 개인정보: 사용 이력에 user_id(내부 식별자)만 저장하고 이메일 등 PII는 저장하지 않는다.
- 쿠폰 삭제는 물리 삭제 대신 soft-delete(status=inactive/deleted)로 처리해 이력 정합성을 보존한다.

### 4.4 Recovery
- RTO ≤ 1시간, RPO ≤ 5분. 쿠폰 사용 이력은 결제 트랜잭션과 동일 DB 트랜잭션 경계에서 커밋되어 유실 시에도 결제 기록으로 재구성 가능.

### 4.5 Security
- **인증**: 세션/JWT 기반. 모든 쿠폰 API는 인증 필수(guest 접근 불가).
- **인가 규칙**:
  | 리소스/액션 | admin | student |
  |---|---|---|
  | POST /admin/coupons (발행) | ✅ | ❌ 403 |
  | GET /admin/coupons (전체 목록) | ✅ | ❌ 403 |
  | PATCH /admin/coupons/{id} (비활성화) | ✅ | ❌ 403 |
  | POST /coupons/validate (적용 미리보기) | ✅ | ✅(본인 결제 컨텍스트) |
  | POST /coupons/redeem (사용 확정) | ✅ | ✅(본인 결제만) |
  | GET /coupons/me/history | ✅ | ✅(본인 이력만) |
- **전송/저장 보호**: 전 구간 TLS 1.2+. 쿠폰 코드는 대소문자 정규화 후 저장.
- **입력 검증**: 할인값 범위(정률 1~100%, 정액 ≥ 0), 유효기간 start < end, 수량 ≥ 1, 코드 정규식 `^[A-Z0-9_-]{4,20}$`. 서버 측 재검증 필수(클라이언트 계산 금액 신뢰 금지).
- **남용 방지**: 쿠폰 코드 추측 공격 대비, `validate`·`redeem` 모두 사용자당 rate limit(예: validate 10 req/min, redeem 5 req/min) 적용. redeem은 추가로 orderId 소유권 검증으로 타인 결제 사용을 차단한다.
- **코드 열거 방지**: `validate`는 미존재 코드와 무효 코드를 구분 노출하지 않도록 미존재도 422(reason=INVALID)로 일반화해 유효 코드 존재 여부 누출을 막는다.

---

## 5. Technical Design

### 5.1 API Specification

#### POST /admin/coupons — 쿠폰 발행 (인가 주체: admin)
- **Request**
```json
{
  "code": "WELCOME10",
  "discountType": "percentage",
  "discountValue": 10,
  "maxDiscountAmount": 10000,
  "minOrderAmount": 30000,
  "startsAt": "2026-08-01T00:00:00+09:00",
  "endsAt": "2026-08-31T23:59:59+09:00",
  "totalQuantity": 1000,
  "perUserLimit": 1
}
```
- **Response 201**
```json
{ "id": "cpn_01H...", "code": "WELCOME10", "status": "active", "remainingQuantity": 1000 }
```
- **Error**: `400` 검증 실패 / `401` 미인증 / `403` 권한 부족 / `409` 코드 중복

#### GET /admin/coupons — 쿠폰 목록 (인가 주체: admin)
- **Request**: `?status=active&page=1&size=20`
- **Response 200**: `{ "items": [ ... ], "page": 1, "total": 42 }`
- **Error**: `401` / `403`

#### PATCH /admin/coupons/{id} — 비활성화 (인가 주체: admin)
- **Request**: `{ "status": "inactive" }`
- **Response 200**: `{ "id": "cpn_...", "status": "inactive" }`
- **Error**: `401` / `403` / `404` 미존재

#### POST /coupons/validate — 적용 미리보기 (인가 주체: student/admin, 본인 결제 컨텍스트)
- **Request**
```json
{ "code": "WELCOME10", "orderAmount": 50000, "courseId": "crs_123" }
```
- **Response 200**
```json
{ "valid": true, "discountAmount": 5000, "finalAmount": 45000 }
```
- **Error**: `401` / `404` 코드 없음 / `422` `{ "valid": false, "reason": "EXPIRED|SOLD_OUT|INACTIVE|MIN_ORDER_NOT_MET|ALREADY_USED", "message": "..." }` / `429` rate limit

#### POST /coupons/redeem — 사용 확정 (인가 주체: student/admin, 본인 결제만)
- **Request**
```json
{ "code": "WELCOME10", "orderId": "ord_789", "orderAmount": 50000 }
```
- **Response 200**
```json
{ "redeemed": true, "discountAmount": 5000, "finalAmount": 45000, "redemptionId": "rdm_..." }
```
- **동작**: 결제 확정 트랜잭션 내에서 잔여 수량 원자적 차감 + 사용 이력 insert(유니크 제약 `(coupon_id, user_id)` on perUserLimit). 실패 시 전체 롤백.
- **Error**: `401` / `403` 타인 결제 / `409` `ALREADY_USED` 또는 동시성 경합 패배 / `422` 검증 실패

#### GET /coupons/me/history — 본인 사용 이력 (인가 주체: student/admin)
- **Response 200**: `{ "items": [ { "code": "...", "discountAmount": 5000, "usedAt": "...", "orderId": "..." } ] }`
- **Error**: `401`

### 5.2 Database Schema
```sql
-- 쿠폰 마스터
CREATE TABLE coupons (
  id                 VARCHAR(32) PRIMARY KEY,
  code               VARCHAR(20) NOT NULL,
  discount_type      VARCHAR(10) NOT NULL CHECK (discount_type IN ('fixed','percentage')),
  discount_value     INTEGER NOT NULL,
  max_discount_amount INTEGER,                 -- percentage 상한, NULL=무제한
  min_order_amount   INTEGER NOT NULL DEFAULT 0,
  starts_at          TIMESTAMPTZ NOT NULL,
  ends_at            TIMESTAMPTZ NOT NULL,
  total_quantity     INTEGER NOT NULL CHECK (total_quantity >= 1),
  remaining_quantity INTEGER NOT NULL CHECK (remaining_quantity >= 0),  -- 음수 방지
  per_user_limit     INTEGER NOT NULL DEFAULT 1,
  status             VARCHAR(10) NOT NULL DEFAULT 'active'
                     CHECK (status IN ('active','inactive','deleted')),
  created_by         VARCHAR(32) NOT NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_period CHECK (starts_at < ends_at)
);
CREATE UNIQUE INDEX uq_coupons_code ON coupons (UPPER(code)) WHERE status <> 'deleted';

-- 쿠폰 사용 이력 (중복 사용 방지의 핵심)
CREATE TABLE coupon_redemptions (
  id              VARCHAR(32) PRIMARY KEY,
  coupon_id       VARCHAR(32) NOT NULL REFERENCES coupons(id),
  user_id         VARCHAR(32) NOT NULL,
  order_id        VARCHAR(32) NOT NULL,
  discount_amount INTEGER NOT NULL,
  status          VARCHAR(10) NOT NULL DEFAULT 'used'
                  CHECK (status IN ('used','refunded')),
  used_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- 1인 N회 제약: perUserLimit=1인 쿠폰의 재사용 차단 (AC-7)
CREATE UNIQUE INDEX uq_redemption_user ON coupon_redemptions (coupon_id, user_id)
  WHERE status = 'used';
CREATE UNIQUE INDEX uq_redemption_order ON coupon_redemptions (order_id) WHERE status = 'used';
```
- **동시성 차감(AC-8/9)**: `UPDATE coupons SET remaining_quantity = remaining_quantity - 1 WHERE id = ? AND remaining_quantity > 0` 의 영향 행 수로 성공 판정(원자적). 0행이면 SOLD_OUT.

### 5.3 Architecture
- 기존 결제 도메인에 **Coupon 모듈**을 추가. `redeem`은 결제 확정 서비스가 **동일 DB 트랜잭션 경계**에서 호출(쿠폰 사용과 결제 기록의 원자성 보장).
- 검증은 **조회(상태·잔여·기사용 read) + 순수 계산(할인액·상한·하한)** 2단계로 분리한다. 할인 계산부는 부수효과 없는 순수 함수로 두어 미리보기/확정에서 동일하게 재사용 → 클라이언트-서버 금액 일치 보장.
- 쿠폰 서비스 장애 시 결제 오케스트레이터가 할인 미적용으로 폴백(§4.2 fail-closed).

#### 5.4 Pages
| Route | Audience | Auth | Linked FRs | Has FE Components | Primary State | Responsive |
|---|---|---|---|---|---|---|
| /admin/coupons | admin | Required | FR-003, FR-004 | Yes | success(목록) | Yes |
| /admin/coupons/new | admin | Required | FR-001, FR-002 | Yes | success(폼) | Yes |
| /checkout (쿠폰 입력 영역) | student | Required | FR-005, FR-006, FR-010 | Yes | success(미리보기) | Yes |
| /coupons/history | student | Required | FR-011 | Yes | success(이력) | Yes |

#### 5.4.1 Page State Matrix
| Route | loading | empty | error | success | no-permission | 비고 |
|---|---|---|---|---|---|---|
| /admin/coupons | 스켈레톤 목록 | "발행된 쿠폰이 없습니다" | 조회 실패 재시도 배너 | 쿠폰 테이블 | 403 안내→홈 이동 | admin 전용 |
| /admin/coupons/new | 제출 버튼 비활성 스피너 | N/A(입력 폼) | 필드별 검증 에러/409 코드중복 인라인 | 생성 완료→목록 이동 | 403 안내 | 코드중복=409 |
| /checkout | 쿠폰 검증 중 인라인 스피너 | N/A | 422 사유 메시지(만료/소진/최소금액/이미사용) | 할인액·최종금액 표시 | 로그인 유도 | guest는 로그인 후 진입 |
| /coupons/history | 스켈레톤 | "사용한 쿠폰이 없습니다" | 조회 실패 재시도 | 이력 리스트 | 본인 외 접근 불가 | 본인 이력만 |

#### 5.5 User Flow
```mermaid
flowchart TD
    A[수강생 결제 화면 진입] --> B{로그인?}
    B -- 아니오 --> B1[로그인 유도] --> A
    B -- 예 --> C[쿠폰 코드 입력]
    C --> D[POST /coupons/validate]
    D --> E{유효?}
    E -- 코드없음 404 --> E1[코드를 확인하세요]
    E -- 만료/소진/비활성/최소금액 422 --> E2[사유 메시지 표시] --> C
    E -- 이미 사용 --> E3[이미 사용한 쿠폰입니다] --> C
    E -- 예 --> F[할인액·최종금액 미리보기]
    F --> G[결제하기]
    G --> H[결제 확정 트랜잭션 내 POST /coupons/redeem]
    H --> I{원자적 차감 성공?}
    I -- 경합 패배/소진 409 --> J[쿠폰 적용 실패 안내→할인없이 재확인] --> F
    I -- 예 --> K[결제 완료 + 사용 이력 기록]
    K --> L{추후 환불?}
    L -- 예 --> M[FR-012 사용 복원: 수량 복구·이력 refunded]

    subgraph ADMIN[관리자]
      N[/admin/coupons/new] --> O[POST /admin/coupons]
      O --> P{코드 중복?}
      P -- 예 409 --> Q[중복 에러 인라인]
      P -- 아니오 --> R[쿠폰 생성→목록]
    end
```

---

## 6. Implementation Phases

### Phase 1 — 쿠폰 발행/관리 (Backend + Admin UI)
- **Tasks**: FR-001, FR-002, FR-003, FR-004 / DB 스키마(coupons) / 코드 유니크 제약 / /admin/coupons API / admin 목록·발행 화면
- **Deliverable**: 관리자가 쿠폰을 발행·조회·비활성화할 수 있고 코드 중복이 차단된다.

### Phase 2 — 쿠폰 검증/미리보기 (결제 전 적용)
- **Tasks**: FR-005, FR-006, FR-010 / validate 순수 함수 / POST /coupons/validate / checkout 쿠폰 입력 UI / 상태 매트릭스 반영
- **Deliverable**: 수강생이 결제 전 할인액·최종금액을 미리 볼 수 있고 만료/최소금액 등이 정확히 거부된다.

### Phase 3 — 사용 확정 & 동시성/중복 방지 (핵심 안전성)
- **Tasks**: FR-007, FR-008, FR-009 / redeem 원자적 차감 / 유니크 제약(coupon_id,user_id / order_id) / 결제 트랜잭션 통합 / 동시성 부하 테스트
- **Deliverable**: 재사용·초과 사용·경합 상황에서 수량 정합성 100% 보장(AC-7/8/9 통과).

### Phase 4 — 이력 & 환불 복원
- **Tasks**: FR-011, FR-012 / /coupons/me/history / 환불 시 사용 복원 / 5년 보관 정책 반영
- **Deliverable**: 사용 이력 조회 및 환불 시 쿠폰 복원이 동작한다.

---

## 7. Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| 쿠폰 사용 수량 정합성 | 오차 0건(remaining 음수·초과사용 0) | DB 정합성 감사 쿼리(주간) |
| 중복 사용 차단율 | 100% | redeem 409 로그 vs 실제 중복 시도 |
| 검증 API p95 지연 | < 200ms | APM 대시보드 |
| 프로모션 결제 전환 기여 | 쿠폰 적용 결제 비율 측정 가능 | 결제 이벤트에 coupon_id 태깅 |
| 쿠폰 관련 CS 문의 | 수동 할인 대비 50% 감소 | CS 티켓 분류 집계 |
| 부정 할인 통과 | 0건 | 서버 재검증 로그·정산 대사 |
