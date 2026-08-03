# PRD — 온라인 강의 플랫폼 쿠폰 기능

> **Type**: product-feature
> **Scale Grade**: Startup
> **Status**: Draft
> **Author**: contact@wigtn.com
> **Date**: 2026-08-03

---

## 1. Overview

### 1.1 Problem Statement
현재 온라인 강의 플랫폼에는 가격 할인 수단이 없다. 마케팅(신규 가입 유치, 재구매 유도, 제휴 프로모션)을 위해 할인을 적용하려면 강의 정가 자체를 수동으로 변경해야 하며, 이는 (1) 특정 사용자·기간·강의에만 선별 할인을 줄 수 없고, (2) 할인 종료 후 원복을 수동으로 처리해야 하며, (3) 누가 얼마나 할인받았는지 추적이 불가능하다. 결과적으로 프로모션 실행 속도가 느리고 매출 분석이 어렵다.

또한 할인을 코드 기반으로 운영할 경우 **동일 쿠폰의 중복·재사용**과 **만료된 쿠폰 사용**을 시스템이 막지 못하면 매출 누수와 정산 오류가 발생한다. 이 두 가지는 본 기능의 핵심 방어 지점이다.

### 1.2 Goals
- 관리자가 코드에서 정가를 건드리지 않고 쿠폰을 발행/관리할 수 있다.
- 수강생이 결제 화면에서 쿠폰 코드를 입력해 즉시 할인 금액을 확인하고 적용할 수 있다.
- 쿠폰의 **중복 사용**과 **만료 사용**을 시스템이 원자적으로 차단한다.
- 모든 쿠폰 발행·사용·취소 이력을 추적해 정산·분석 근거를 남긴다.

### 1.3 Non-Goals
- **적립금/포인트 시스템** — 쿠폰과 별개 도메인이며 이번 범위 밖.
- **쿠폰 조합(스태킹) 사용** — 1회 결제당 1개 쿠폰만 허용(§3 FR-006). 다중 쿠폰 동시 적용은 향후 과제.
- **자동 발급 트리거(회원가입/생일 등 이벤트 기반 자동 발행)** — 이번엔 관리자 수동/일괄 발행만 지원.
- **환율/다중 통화 할인** — 단일 통화(KRW) 가정.
- **부분 환불(partial refund) 복원** — 전액 환불 시에만 쿠폰을 복원(FR-009). 다중 강의 주문의 일부만 환불되는 경우 쿠폰은 복원하지 않는다(이번 범위 밖, 향후 비례 복원 과제).
- **추천인/제휴사 정산 로직** — 쿠폰 사용 데이터는 남기되 외부 정산 연동은 범위 밖.
- **결제 게이트웨이(PG) 자체 구현** — 기존/외부 PG 연동을 전제로 하며 본 PRD는 할인 계산과 최종 결제 금액 확정까지만 책임진다.

### 1.4 Scope
**포함**: 쿠폰 정의(정액/정률), 발행(단일·일괄), 유효성 규칙(기간·최소주문금액·대상강의·사용횟수), 결제 시 검증·적용, 중복/만료 차단, 사용 이력, 환불 시 쿠폰 복원, 관리자/수강생 UI, 관련 API·스키마.
**제외**: 위 §1.3 Non-Goals 전체.

---

## 2. User Stories

### 2.1 Primary User
- **관리자(admin)**: "As a 관리자, I want to 할인 조건과 유효기간을 지정해 쿠폰을 발행하고 상태를 관리하고 싶다 so that 정가를 바꾸지 않고 선별적 프로모션을 빠르게 실행하고 추적할 수 있다."
- **수강생(student)**: "As a 수강생, I want to 결제 화면에서 쿠폰 코드를 입력해 할인 금액을 확인하고 적용하고 싶다 so that 더 저렴하게 강의를 구매할 수 있다."

### 2.2 Acceptance Criteria

**AC-1 쿠폰 발행 (정상)**
```gherkin
Given 관리자로 로그인한 상태에서
When 할인유형=정률(20%), 유효기간=2026-08-01~2026-08-31, 최소주문금액=50,000원, 대상=전체강의로 쿠폰을 생성하면
Then 상태=active인 쿠폰이 생성되고 고유 쿠폰 코드가 발급된다
```

**AC-2 쿠폰 적용 (정상)**
```gherkin
Given 수강생이 80,000원 강의를 장바구니에 담고 유효한 정률 20% 쿠폰 코드를 입력하면
When 쿠폰 적용을 요청하면
Then 할인액 16,000원이 계산되고 최종 결제금액 64,000원이 표시된다
```

**AC-3 만료 쿠폰 차단 (실패)**
```gherkin
Given 유효기간이 2026-07-31에 종료된 쿠폰을
When 수강생이 2026-08-03에 적용을 시도하면
Then "만료된 쿠폰입니다" 오류(EXPIRED)가 반환되고 할인이 적용되지 않는다
```

**AC-4 중복 사용 차단 (실패)**
```gherkin
Given 1인 1회 사용 제한 쿠폰을 이미 사용해 결제를 완료한 수강생이
When 동일 쿠폰을 다시 적용해 결제를 시도하면
Then "이미 사용한 쿠폰입니다" 오류(ALREADY_USED)가 반환된다
```

**AC-5 동시 결제 경합 차단 (실패)**
```gherkin
Given 총 사용 한도가 1회 남은 쿠폰에 대해
When 두 명의 수강생이 거의 동시에 결제 확정을 요청하면
Then 정확히 1건만 성공(redeemed)하고 나머지는 "쿠폰이 모두 소진되었습니다" 오류(SOLD_OUT)를 받는다
```

**AC-6 최소 주문금액 미달 (실패)**
```gherkin
Given 최소주문금액 50,000원 쿠폰을
When 수강생이 30,000원 강의 결제에 적용하면
Then "최소 주문금액 50,000원 이상부터 사용 가능합니다" 오류(MIN_AMOUNT_NOT_MET)가 반환된다
```

**AC-7 대상 강의 불일치 (실패)**
```gherkin
Given 특정 강의(A)에만 적용되는 쿠폰을
When 수강생이 강의(B) 결제에 적용하면
Then "해당 강의에 사용할 수 없는 쿠폰입니다" 오류(NOT_APPLICABLE)가 반환된다
```

**AC-8 권한 부족 (권한)**
```gherkin
Given 수강생(student) 권한으로 로그인한 상태에서
When 쿠폰 발행 API(POST /admin/coupons)를 호출하면
Then 403 Forbidden이 반환되고 쿠폰이 생성되지 않는다
```

**AC-9 환불 시 쿠폰 복원**
```gherkin
Given 쿠폰을 사용해 결제한 주문이
When 관리자/시스템에 의해 전액 환불되면
Then 해당 쿠폰 사용 이력이 canceled로 전환되고, 1인 1회/총 한도 카운트가 복원되어 재사용이 가능해진다
```

### 2.3 User Roles

| Role Key | 한국어 명칭 | 권한 범위 |
|---|---|---|
| `admin` | 관리자 | 쿠폰 생성·수정·비활성화·삭제, 발행 내역/사용 이력 조회, 환불에 따른 복원 처리 |
| `student` | 수강생 | 자신의 결제에 쿠폰 코드 검증·적용, 본인 보유/사용 쿠폰 조회 |
| `system` | 시스템 | 결제 확정 시 쿠폰 원자적 사용 처리, 환불 웹훅 수신 시 복원 처리(내부 서비스 계정) |

---

## 3. Functional Requirements

| ID | Requirement | Priority | Dependencies |
|---|---|---|---|
| FR-001 | 관리자는 쿠폰을 생성한다: 할인유형(정액 KRW / 정률 %), 할인값, 정률 시 최대할인액(상한), 유효기간(시작~종료), 최소주문금액, 대상 범위(전체/특정 강의·카테고리), 사용 제한(1인 N회, 총 발행/사용 한도) | P0 | — |
| FR-002 | 관리자는 쿠폰 코드를 발급한다: (a) 공용 단일 코드(예: `WELCOME20`), (b) 1인 전용 유니크 코드 일괄 생성(N개) | P0 | FR-001 |
| FR-003 | 관리자는 쿠폰 목록을 조회하고 상태(active/inactive/expired/exhausted)를 관리(비활성화)한다 | P0 | FR-001 |
| FR-004 | 수강생은 결제 전 쿠폰 코드를 입력해 유효성을 검증하고 할인 적용 후 예상 결제금액을 미리 확인한다(비확정 미리보기) | P0 | FR-001 |
| FR-005 | 시스템은 할인 금액을 계산한다: 정액=min(할인값, 주문금액), 정률=min(주문금액×율, 최대할인액), 최종금액은 0원 미만이 될 수 없다 | P0 | FR-004 |
| FR-006 | 시스템은 결제 확정 시 쿠폰을 **원자적으로 1회만** 사용 처리한다: 1인 1회/총 한도/동시성 경합을 DB 제약·잠금으로 차단하고, 1결제=1쿠폰만 허용한다 | P0 | FR-004, FR-005 |
| FR-007 | 시스템은 적용/확정 시점에 만료·기간·최소주문금액·대상강의·활성상태를 재검증한다(미리보기 값 신뢰 금지) | P0 | FR-004 |
| FR-008 | 시스템은 모든 사용 이력(누가·어느 쿠폰·어느 주문·할인액·시각·상태)을 기록하고 관리자가 조회한다 | P1 | FR-006 |
| FR-009 | 결제가 **전액** 환불되면 시스템은 해당 쿠폰 사용을 canceled 처리하고 사용 카운트(total_used·1인 카운트)를 복원한다. 부분 환불은 복원하지 않는다(§1.3) | P1 | FR-006, FR-008 |
| FR-010 | 수강생은 본인에게 귀속(assigned)된 유니크 쿠폰 및 본인이 사용한 쿠폰 목록·상태를 조회한다. 공용(shared) 코드는 귀속 개념이 없어 조회 대상이 아니다 | P2 | FR-002 |

> **무모순 확인**: FR-006(1결제 1쿠폰)와 §1.3(스태킹 비허용)은 일관됨. FR-004(미리보기)는 비확정이며 FR-007(확정 시 재검증)이 최종 권위를 가진다 — 미리보기와 확정의 검증 책임이 분리되어 모순 없음.

---

## 4. Non-Functional Requirements

### 4.0 Scale Grade
**Startup** — 온라인 강의 플랫폼 초기 단계로 DAU 1,000~10,000 구간을 가정. 프로모션 기간에 결제 요청이 특정 강의/쿠폰에 몰리는 스파이크는 존재하나 상시 대규모 트래픽은 아님. (근거: 신규 기능·초기 시장, 결제라는 저빈도 액션 중심.)

### 4.1 Performance
- 쿠폰 검증/미리보기 API(`POST /coupons/validate`): **p95 < 200ms**, p99 < 400ms.
- 결제 확정 시 쿠폰 사용 처리(`POST /coupons/redeem`): **p95 < 300ms** (DB 트랜잭션 포함).
- 동시성 목표: 단일 쿠폰에 대한 **동시 확정 요청 100 req/s** 상황에서 총 한도를 초과하는 사용이 **0건**(정합성 절대 보장, 성능보다 우선).
- 관리자 쿠폰 목록 조회: 1만 건 기준 p95 < 500ms (페이지네이션 50건/페이지).

### 4.2 Availability
- 목표 가용성 **99.5%** (월 다운타임 ~3.6h 이내).
- 쿠폰 검증/사용 서비스 장애 시: 결제 플로우는 **쿠폰 미적용 정가 결제로 graceful degradation**을 허용하되, 사용 처리(redeem)가 불확실하면 결제를 **확정하지 않고 실패 처리**한다(중복 사용 방지 > 결제 성공률).

### 4.3 Data
- 쿠폰 정의·사용 이력은 정산/분쟁 대응을 위해 **최소 5년 보관**(전자상거래 거래기록 준용).
- 개인정보: 사용 이력은 `user_id`(내부 식별자)만 참조하고 이름·연락처 등 PII를 직접 저장하지 않는다.
- 삭제 정책: 쿠폰은 물리 삭제 대신 **soft delete(비활성화)**를 기본으로 한다(사용 이력 무결성 유지). 사용자 탈퇴 시 사용 이력은 익명화(`user_id` → 해시) 후 보존.

### 4.4 Recovery
- **RPO ≤ 5분** (DB PITR/복제 기반), **RTO ≤ 1시간**.
- 쿠폰 사용 처리는 결제 트랜잭션과 동일 트랜잭션(또는 idempotent redeem)으로 묶어, 장애 복구 후에도 "결제됨 but 쿠폰 미사용" 또는 "쿠폰 사용됨 but 결제 실패" 불일치가 남지 않게 한다.

### 4.5 Security
- **인증**: 모든 API는 JWT 기반 인증 필수(비로그인 접근 불가). `system` 역할은 서버 간 내부 인증(서비스 토큰).
- **인가 규칙**:
  - 쿠폰 생성/수정/비활성화/발행내역·전체 사용이력 조회 → **`admin` 전용**.
  - 쿠폰 검증(validate)·본인 결제 적용·본인 쿠폰 조회 → **`student`**. student는 타인의 사용 이력·관리 API 접근 불가.
  - redeem(사용 확정)·환불 복원 → **`system`** (내부 결제 서비스). student가 직접 redeem 호출 불가.
- **전송/저장 보호**: 전 구간 TLS 1.2+. 쿠폰 코드는 평문 저장하되 유니크 코드는 추측 불가능하도록 **암호학적 난수 기반 12자 이상**(예: base32, 사람이 읽기 쉬운 문자셋)으로 생성.
- **입력 검증**: 코드 형식/길이 검증, 할인율 0~100% 범위, 할인값·최소주문금액 음수 불가, 유효기간 시작<종료 검증. 코드 대입(brute-force) 방지를 위해 validate/redeem에 **IP·계정당 rate limit**(예: 분당 10회) 적용.

---

## 5. Technical Design

### 5.1 API Specification

> 공통 오류 코드: `EXPIRED`, `ALREADY_USED`, `SOLD_OUT`, `MIN_AMOUNT_NOT_MET`, `NOT_APPLICABLE`, `INACTIVE`, `INVALID_CODE`, `FORBIDDEN`, `RATE_LIMITED`.

#### POST /admin/coupons — 쿠폰 생성 (인가: `admin`)
**Request**
```json
{
  "name": "8월 신규회원 20% 할인",
  "discountType": "percentage",       // "percentage" | "fixed"
  "discountValue": 20,                 // % 또는 KRW
  "maxDiscountAmount": 30000,          // percentage일 때 상한(선택)
  "minOrderAmount": 50000,
  "startsAt": "2026-08-01T00:00:00+09:00",
  "endsAt": "2026-08-31T23:59:59+09:00",
  "scope": { "type": "course", "courseIds": ["c_123"] }, // "all" | "course" | "category"
  "perUserLimit": 1,
  "totalLimit": 1000,
  "codeStrategy": "shared"             // "shared" | "unique"
}
```
**Response 201**
```json
{ "couponId": "cp_abc", "code": "WELCOME20", "status": "active", "createdAt": "2026-08-03T10:00:00+09:00" }
```
**Error**: 400 `VALIDATION`(율/기간/금액 위반), 403 `FORBIDDEN`(non-admin).

#### POST /admin/coupons/{id}/issue-codes — 유니크 코드 일괄 발급 (인가: `admin`)
**Request** `{ "count": 500 }`
**Response 201** `{ "issued": 500, "sampleCodes": ["A1B2C3D4E5F6", "..."] }`
**Error**: 400(codeStrategy가 unique가 아님), 403 `FORBIDDEN`.

#### PATCH /admin/coupons/{id} — 상태/속성 수정 (인가: `admin`)
**Request** `{ "status": "inactive" }`
**Response 200** `{ "couponId": "cp_abc", "status": "inactive" }`
**Error**: 404, 403.

#### GET /admin/coupons?status=&page= — 목록 조회 (인가: `admin`)
**Response 200** `{ "items": [...], "page": 1, "total": 1200 }`

#### GET /admin/coupons/{id}/redemptions — 사용 이력 (인가: `admin`)
**Response 200** `{ "items": [{ "userId":"u_1","orderId":"o_9","discountAmount":16000,"status":"redeemed","redeemedAt":"..." }], "total": 34 }`

#### POST /coupons/validate — 쿠폰 검증·미리보기 (인가: `student`, 비확정)
**Request**
```json
{ "code": "WELCOME20", "orderAmount": 80000, "courseIds": ["c_123"] }
```
**Response 200**
```json
{ "valid": true, "couponId":"cp_abc", "discountAmount": 16000, "finalAmount": 64000 }
```
**검증 실패(항상 HTTP 200, `valid:false`로 통일 — 클라이언트 분기 단일화)**
```json
{ "valid": false, "reason": "EXPIRED", "message": "만료된 쿠폰입니다" }
```
`reason` ∈ {EXPIRED, ALREADY_USED, MIN_AMOUNT_NOT_MET, NOT_APPLICABLE, INACTIVE, INVALID_CODE}.
프로토콜/인프라 오류만 비-200: 429 `RATE_LIMITED`, 401(미인증).

#### POST /coupons/redeem — 결제 확정 시 사용 처리 (인가: `system`, 멱등)
**Request**
```json
{ "code": "WELCOME20", "userId": "u_1", "orderId": "o_9", "orderAmount": 80000, "courseIds": ["c_123"], "idempotencyKey": "o_9-cp_abc" }
```
**Response 200** `{ "redeemed": true, "redemptionId": "rd_1", "discountAmount": 16000, "finalAmount": 64000 }`
**Error**: 409 `ALREADY_USED` / `SOLD_OUT`, 422 `EXPIRED`/`MIN_AMOUNT_NOT_MET`/`NOT_APPLICABLE`/`INACTIVE`, 403 `FORBIDDEN`(비-system). 동일 `idempotencyKey` 재요청은 최초 결과를 그대로 반환(중복 차감 없음).

#### POST /coupons/redemptions/{id}/cancel — 환불 시 복원 (인가: `system`)
**Response 200** `{ "canceled": true, "restored": true }`
**Error**: 404, 409(이미 canceled), 403.

#### GET /me/coupons — 본인 쿠폰 조회 (인가: `student`)
**Response 200** `{ "items": [{ "code":"...","status":"available|used|expired","couponId":"..." }] }`

### 5.2 Database Schema

```sql
-- 쿠폰 정의
-- 참고: 모든 ID는 외부 노출용 prefix 문자열(coupons=cp_, redemptions=rd_)을 정본으로 쓴다.
CREATE TABLE coupons (
  id              VARCHAR(32) PRIMARY KEY,          -- 예: 'cp_abc' (API 노출 ID와 동일)
  name            VARCHAR(200) NOT NULL,
  discount_type   VARCHAR(16) NOT NULL,          -- 'percentage' | 'fixed'
  discount_value  INT NOT NULL,                   -- % 또는 KRW
  max_discount    INT NULL,                        -- percentage 상한
  min_order_amount INT NOT NULL DEFAULT 0,
  scope_type      VARCHAR(16) NOT NULL,            -- 'all' | 'course' | 'category'
  code_strategy   VARCHAR(16) NOT NULL,            -- 'shared' | 'unique'
  per_user_limit  INT NOT NULL DEFAULT 1,
  total_limit     INT NULL,                         -- NULL=무제한
  total_used      INT NOT NULL DEFAULT 0,           -- 소진 판정용 카운터
  starts_at       TIMESTAMPTZ NOT NULL,
  ends_at         TIMESTAMPTZ NOT NULL,
  status          VARCHAR(16) NOT NULL DEFAULT 'active', -- active|inactive|expired|exhausted
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at      TIMESTAMPTZ NULL,                 -- soft delete
  CHECK (starts_at < ends_at),
  CHECK (discount_value >= 0),
  CHECK (min_order_amount >= 0),
  -- 정률 쿠폰은 0~100% 로 DB 레벨에서도 강제(앱 검증 우회 방지, m-3)
  CHECK (discount_type <> 'percentage' OR (discount_value >= 0 AND discount_value <= 100))
);

-- 쿠폰 코드 (shared=1행, unique=N행)
CREATE TABLE coupon_codes (
  id                BIGINT PRIMARY KEY,
  coupon_id         VARCHAR(32) NOT NULL REFERENCES coupons(id),
  code              VARCHAR(32) NOT NULL,
  assigned_user_id  VARCHAR(64) NULL,   -- unique 전략에서 특정 수강생에게 귀속(shared는 NULL). /me/coupons 소유 근거
  UNIQUE (code)
);
CREATE INDEX idx_codes_assigned_user ON coupon_codes(assigned_user_id);

-- 쿠폰 적용 대상(scope_type=course/category일 때)
CREATE TABLE coupon_targets (
  coupon_id  VARCHAR(32) NOT NULL REFERENCES coupons(id),
  target_id  VARCHAR(64) NOT NULL,   -- course_id 또는 category_id (생성 시 존재 검증, m-2)
  PRIMARY KEY (coupon_id, target_id)
);

-- 사용 이력 (중복 사용 방지의 핵심)
CREATE TABLE coupon_redemptions (
  id              VARCHAR(32) PRIMARY KEY,           -- 예: 'rd_1'
  coupon_id       VARCHAR(32) NOT NULL REFERENCES coupons(id),
  code            VARCHAR(32) NOT NULL,
  user_id         VARCHAR(64) NOT NULL,
  order_id        VARCHAR(64) NOT NULL,
  discount_amount INT NOT NULL,
  status          VARCHAR(16) NOT NULL,   -- 'redeemed' | 'canceled'
  idempotency_key VARCHAR(128) NOT NULL,
  redeemed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  canceled_at     TIMESTAMPTZ NULL,
  -- 멱등: 동일 결제-쿠폰 재요청 차단
  UNIQUE (idempotency_key),
  -- 1인 1회 제한 강제(활성 사용만): partial unique index로 구현
  UNIQUE (coupon_id, user_id) WHERE status = 'redeemed'  -- per_user_limit=1 케이스
);
CREATE INDEX idx_redemptions_coupon ON coupon_redemptions(coupon_id);
```

> per_user_limit>1 인 경우는 위 partial unique 대신 애플리케이션에서 `COUNT(*) WHERE status='redeemed'` 검사를 잠금과 함께 수행한다(§5.3).

### 5.3 Architecture

**중복 사용 방지 전략 (핵심)** — 3중 방어:
1. **멱등키**: `coupon_redemptions.idempotency_key`에 UNIQUE 제약. 동일 결제 재시도 시 중복 삽입이 DB 레벨에서 실패 → 최초 결과 반환.
2. **1인 1회 제약**: partial unique index `(coupon_id, user_id) WHERE status='redeemed'`로 DB가 강제. (다회 허용 쿠폰은 트랜잭션 내 `SELECT ... FOR UPDATE`로 사용자 사용횟수 카운트 후 삽입.)
3. **총 한도 경합**: redeem 트랜잭션에서 `UPDATE coupons SET total_used = total_used + 1 WHERE id=? AND (total_limit IS NULL OR total_used < total_limit)` 를 실행하고 **영향 행 수 0이면 SOLD_OUT** 반환. 원자적 조건부 업데이트로 동시 요청 경합을 해소(§AC-5).

**상태 전이(exhausted/expired)**:
- redeem 성공 후 `total_used == total_limit` 도달 시 **같은 트랜잭션에서 `status='exhausted'`** 로 전이한다. cancel로 카운트가 다시 한도 미만이 되면 `active`로 원복한다.
- 만료: redeem/validate 트랜잭션에서 `now()` 기준 `starts_at <= now() < ends_at` 및 `status='active'`를 재확인(lazy check). 배치 잡(1일 1회)이 `ends_at < now()` 쿠폰을 `expired`로 일괄 전환한다.
- `status`는 소진/만료의 캐시일 뿐 **권위 판정은 항상 실시간 재검증**(FR-007)이 가진다.

**흐름 — 정확히-한번(exactly-once) 보장(M-5)**: 로컬 DB와 외부 PG는 하나의 ACID 트랜잭션으로 묶을 수 없으므로 **예약→확정 2단계**로 처리한다.
1. 결제 승인 직전 `POST /coupons/redeem`(멱등키=orderId+couponId) 호출 → redemption을 `redeemed`로 기록하고 카운트 차감(위 3중 방어).
2. redeem 성공 시에만 PG 승인을 요청한다.
3. PG 승인 **실패/타임아웃** 시 시스템이 즉시 `.../cancel`을 호출해 보상(카운트 복원)한다.
4. 3의 보상마저 유실될 경우를 대비해 **reconciliation 배치**(예: 10분 주기)가 "redeemed 이나 대응 결제가 확정되지 않은" redemption을 찾아 auto-cancel 한다.
- 환불 웹훅 수신 시 `system`이 `.../cancel` 호출 → redemption `canceled` + `total_used` 감소.

**스택 가정**(greenfield): Next.js(App Router) + Route Handlers, PostgreSQL(트랜잭션·partial index 지원), 결제는 외부 PG 연동. 관리자/수강생 UI는 동일 앱 내 라우트 분리.

#### 5.4 Pages

| Route | Audience | Auth | Linked FRs | Has FE Components | Primary State | Responsive |
|---|---|---|---|---|---|---|
| `/admin/coupons` | `admin` | 필수 | FR-003, FR-008 | Yes | success(목록) | Desktop 우선 |
| `/admin/coupons/new` | `admin` | 필수 | FR-001, FR-002 | Yes | success(폼) | Desktop 우선 |
| `/admin/coupons/[id]` | `admin` | 필수 | FR-003, FR-008 | Yes | success(상세+이력) | Desktop 우선 |
| `/checkout` (쿠폰 입력 영역) | `student` | 필수 | FR-004, FR-005, FR-007 | Yes | success(적용됨) | 반응형(모바일 포함) |
| `/me/coupons` | `student` | 필수 | FR-010 | Yes | success(목록) | 반응형(모바일 포함) |

#### 5.4.1 Page State Matrix

| Route | loading | empty | error | success | no-permission | 비고 |
|---|---|---|---|---|---|---|
| `/admin/coupons` | 목록 스켈레톤 | "발행된 쿠폰 없음" + 생성 CTA | 로드 실패 재시도 배너 | 쿠폰 테이블(상태 배지) | 관리자 아니면 403 리다이렉트 | 상태 필터 탭 |
| `/admin/coupons/new` | — | — | 필드 인라인 검증 오류(율/기간/금액) | 생성 완료 → 상세로 이동 | 403 리다이렉트 | 저장 중 버튼 disabled |
| `/admin/coupons/[id]` | 상세+이력 스켈레톤 | "사용 이력 없음" | 404/로드 실패 | 상세 + 사용이력 표 | 403 리다이렉트 | 비활성화 액션 |
| `/checkout` | 검증 중 스피너(입력칸) | 코드 미입력 기본 상태 | 오류 메시지(EXPIRED/ALREADY_USED/MIN_AMOUNT/NOT_APPLICABLE 등) | 할인액·최종금액 갱신 | 비로그인 시 로그인 유도 | 적용/해제 토글 |
| `/me/coupons` | 목록 스켈레톤 | "보유 쿠폰 없음" | 로드 실패 재시도 | 쿠폰 카드 목록(상태별) | 비로그인 리다이렉트 | 사용/만료 필터 |

#### 5.5 User Flow

```mermaid
flowchart TD
    A[관리자: /admin/coupons/new] -->|조건 입력·생성| B{검증 OK?}
    B -->|No| A
    B -->|Yes| C[쿠폰 active 생성 + 코드 발급]
    C --> D[/admin/coupons 목록]

    S[수강생: /checkout 쿠폰코드 입력] --> V[POST /coupons/validate]
    V --> W{유효?}
    W -->|No: EXPIRED/MIN/NOT_APPLICABLE/ALREADY_USED| X[오류 메시지 표시, 정가 유지]
    W -->|Yes| Y[할인액·최종금액 미리보기]
    Y --> Z[결제하기]
    Z --> R[system: POST /coupons/redeem 재검증+원자적 사용]
    R --> Q{사용 성공?}
    Q -->|SOLD_OUT/ALREADY_USED/EXPIRED| X
    Q -->|Yes| P[PG 승인 확정 + redemption redeemed]
    P --> RF{환불 발생?}
    RF -->|Yes| CL[system: cancel → canceled + total_used 복원]
    RF -->|No| END[완료]
```

---

## 6. Implementation Phases

### Phase 1 — 쿠폰 도메인·발행 (P0 기반)
- **Tasks**: DB 스키마(coupons/coupon_codes/coupon_targets), FR-001 생성 API, FR-002 코드 발급(shared/unique), FR-003 목록·상태 관리 API + `/admin/coupons`·`/new` UI, §4.5 인가·입력검증.
- **Deliverable**: 관리자가 쿠폰을 발행/조회/비활성화할 수 있다.

### Phase 2 — 검증·적용·중복/만료 차단 (P0 핵심)
- **Tasks**: FR-005 할인 계산, FR-004 `/coupons/validate` + `/checkout` 쿠폰 입력 UI, FR-007 확정 재검증, FR-006 `/coupons/redeem` 원자적 사용(멱등키·partial unique·조건부 total_used 업데이트), lazy 만료 처리 + 만료 배치, rate limit.
- **Deliverable**: 수강생이 쿠폰을 적용해 결제할 수 있고, 중복·만료·경합·미달·대상불일치가 모두 차단된다(AC-2~AC-7).

### Phase 3 — 이력·환불 복원·수강생 조회 (P1/P2)
- **Tasks**: FR-008 사용 이력 기록·조회 UI(`/admin/coupons/[id]`), FR-009 환불 시 cancel/복원, FR-010 `/me/coupons`.
- **Deliverable**: 전체 사용 이력 추적, 환불 시 정합성 복원, 수강생 본인 쿠폰 확인(AC-9).

---

## 7. Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| 중복 사용 발생 건수 | 0건 | redemption 로그 감사(총 한도/1인 한도 초과 0) |
| 만료 쿠폰 사용 차단율 | 100% | redeem 거부 로그 / 만료 쿠폰 시도 |
| 동시 경합 정합성 | 초과 사용 0건 @ 100 req/s | 부하 테스트(동일 쿠폰 동시 확정) |
| validate p95 응답시간 | < 200ms | APM 계측 |
| 쿠폰 발행→첫 사용 리드타임 | < 5분(관리자 작업 기준) | 발행/사용 타임스탬프 차 |
| 쿠폰 적용 결제 전환율 | 프로모션별 추적 | 쿠폰 적용 결제 / 쿠폰 검증 성공 |
