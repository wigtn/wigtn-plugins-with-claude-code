# PRD — 쿠폰(Coupon) 기능

> **Type**: product-feature
> **Feature Key**: coupon
> **작성일**: 2026-08-03
> **대상 제품**: 온라인 강의 플랫폼

---

## 1. Overview

### 1.1 Problem Statement
현재 플랫폼에는 할인 수단이 없다. 마케팅·프로모션·재구매 유도를 위해 가격을 조정하려면 강의 판매가 자체를 임시로 바꾸는 수밖에 없어, 대상을 특정할 수 없고 되돌리기도 번거롭다. 관리자가 조건부 할인 수단(쿠폰)을 발행하고 수강생이 결제 시 적용할 수 있어야 한다. 이때 **한 쿠폰이 중복 사용되거나 만료된 쿠폰이 적용되는 사고**는 금액 손실로 직결되므로 반드시 막아야 한다.

### 1.2 Goals
- 관리자가 할인 쿠폰을 발행/조회/비활성화할 수 있다.
- 수강생이 결제 시 쿠폰 코드를 입력해 할인을 적용받는다.
- 동일 쿠폰의 **중복 사용을 원자적으로 차단**한다(동시 요청 포함).
- **만료·비활성·사용횟수 초과** 쿠폰의 적용을 차단한다.
- 쿠폰 적용 내역을 결제와 연결해 추적·정산 가능하게 한다.

### 1.3 Non-Goals
- **자동 발급/추천 쿠폰** (행동 기반 자동 발급 엔진) — 이번 범위 밖. 관리자 수동 발행만.
- **쿠폰 조합 사용**(한 결제에 2장 이상 동시 적용) — 이번 범위 밖. 1결제 1쿠폰.
- **적립금/포인트/멤버십 등급 할인** — 별도 기능. 쿠폰만 다룬다.
- **쿠폰 전용 마케팅 발송(이메일/푸시)** — 발송 채널은 별도 기능. 본 PRD는 코드 생성·검증·소진까지만.
- **부분 환불 시 쿠폰 자동 재발급** — 환불 정책은 별도 PRD. 본 문서는 환불 시 사용 이력 처리 규칙(§4.3)만 명시.

### 1.4 Scope
**포함**: 쿠폰 발행/관리(Admin), 쿠폰 검증·미리보기(결제 전), 쿠폰 소진(결제 확정 시), 사용 이력 기록, 중복/만료/한도 차단 로직.
**제외**: 결제 게이트웨이(PG) 연동 자체, 강의 카탈로그, 환불 처리 파이프라인(연동 지점만 정의).

---

## 2. User Stories

### 2.1 Primary User
- **관리자(admin)**: `As a 관리자, I want to 할인 조건(할인율/정액, 유효기간, 사용 한도)을 지정한 쿠폰을 발행하고 싶다 so that 특정 프로모션에 맞춰 통제된 할인을 제공할 수 있다.`
- **수강생(student)**: `As a 수강생, I want to 결제 시 쿠폰 코드를 입력해 할인 금액을 미리 확인하고 적용하고 싶다 so that 강의를 더 저렴하게 구매할 수 있다.`

### 2.2 Acceptance Criteria (Gherkin)

**AC-1 쿠폰 발행 (정상)**
```gherkin
Given 관리자로 로그인했고
When 할인율 20%, 최대 할인 30,000원, 유효기간 2026-09-01~2026-09-30, 총 사용 한도 100회로 쿠폰을 발행하면
Then 고유 쿠폰 코드가 생성되고 상태가 active가 되며 목록에 노출된다
```

**AC-2 쿠폰 적용 미리보기 (정상)**
```gherkin
Given 수강생이 100,000원 강의를 장바구니에 담았고
And 유효한 쿠폰 "WELCOME20"(20% 할인, 최대 30,000원)이 존재할 때
When 결제 화면에서 "WELCOME20"을 입력하면
Then 할인액 20,000원과 최종 결제금액 80,000원이 표시된다
```

**AC-3 만료 쿠폰 차단 (실패)**
```gherkin
Given 유효기간이 2026-07-31에 끝난 쿠폰 "SUMMER"이 존재하고
And 현재 날짜가 2026-08-03일 때
When 수강생이 "SUMMER"을 입력하면
Then "만료된 쿠폰입니다" 오류(EXPIRED)가 반환되고 할인이 적용되지 않는다
```

**AC-4 중복 사용 차단 — 1인 1회 (실패)**
```gherkin
Given 수강생 A가 쿠폰 "ONCE"을 이미 한 번 사용해 결제를 완료했고
And "ONCE"의 1인당 사용 한도가 1회일 때
When 수강생 A가 다시 "ONCE"을 적용하려 하면
Then "이미 사용한 쿠폰입니다" 오류(ALREADY_USED)가 반환된다
```

**AC-5 중복 사용 차단 — 동시 요청 경합 (실패)**
```gherkin
Given 총 사용 한도가 1회 남은 쿠폰 "LAST"이 존재하고
When 서로 다른 두 수강생이 동시에 "LAST"으로 결제 확정을 요청하면
Then 정확히 한 건만 성공하고 나머지는 "쿠폰이 모두 소진되었습니다" 오류(SOLD_OUT)를 받는다
And 쿠폰의 사용 횟수는 한도를 초과하지 않는다
```

**AC-6 비활성 쿠폰 차단 (실패)**
```gherkin
Given 관리자가 쿠폰 "STOP"을 비활성화했을 때
When 수강생이 "STOP"을 입력하면
Then "사용할 수 없는 쿠폰입니다" 오류(INACTIVE)가 반환된다
```

**AC-7 최소 주문금액 미달 (실패)**
```gherkin
Given 쿠폰 "MIN50"의 최소 주문금액이 50,000원일 때
When 수강생이 40,000원 강의에 "MIN50"을 적용하면
Then "최소 주문금액 50,000원 이상부터 사용 가능합니다" 오류(MIN_AMOUNT_NOT_MET)가 반환된다
```

**AC-8 권한 부족 (실패)**
```gherkin
Given 수강생 권한으로 로그인했을 때
When 쿠폰 발행 API(POST /admin/coupons)를 호출하면
Then 403 Forbidden이 반환되고 쿠폰이 생성되지 않는다
```

**AC-9 결제 실패 시 소진 롤백 (실패)**
```gherkin
Given 수강생이 쿠폰 "PAYOK"을 적용해 결제를 시작했고 쿠폰 사용이 예약(reserved)되었을 때
When PG 결제가 최종 실패하면
Then 쿠폰 예약이 해제(released)되어 다시 사용 가능한 상태로 복구된다
```

### 2.3 User Roles

| Role Key | 한국어 명칭 | 권한 범위 |
|---|---|---|
| `admin` | 관리자 | 쿠폰 발행/조회/수정/비활성화, 전체 사용 이력 조회 |
| `student` | 수강생 | 본인 결제 건에 쿠폰 검증·적용, 본인 사용 이력 조회 |
| `guest` | 비로그인 사용자 | 권한 없음(쿠폰 기능 접근 불가, 로그인 유도) |

---

## 3. Functional Requirements

| ID | Requirement | Priority | Dependencies |
|---|---|---|---|
| FR-001 | 관리자는 쿠폰을 발행한다: 코드(수동/자동생성), 할인유형(정률/정액), 할인값, 최대할인액(정률 시), 최소주문금액, 유효기간(시작/종료), 총 사용한도, 1인당 사용한도, 대상 범위(전체/특정 강의) | P0 | — |
| FR-002 | 코드는 플랫폼 내 유일해야 하며, 자동 생성 시 충돌 없는 코드를 발급한다 | P0 | FR-001 |
| FR-003 | 관리자는 쿠폰을 비활성화(`inactive`)할 수 있다. 비활성 쿠폰은 신규 적용 불가하되 기존 사용 이력은 보존된다 | P0 | FR-001 |
| FR-004 | 관리자는 쿠폰 목록/상세와 사용 현황(발급수/사용수/잔여)을 조회한다 | P1 | FR-001 |
| FR-005 | 수강생은 결제 전 쿠폰 코드를 검증하고 할인액·최종금액을 미리 확인한다(소진 없이 계산만) | P0 | FR-001 |
| FR-006 | 검증은 다음을 모두 통과해야 성공한다: 존재·active·유효기간 내·최소주문금액 충족·총한도 잔여·1인당 한도 잔여·대상 강의 일치 | P0 | FR-005 |
| FR-007 | 결제 확정 시 쿠폰을 원자적으로 1회 소진하고 사용 이력(누가/언제/어느 결제/할인액)을 기록한다 | P0 | FR-006 |
| FR-008 | 동시 요청 하에서도 총 사용한도·1인당 한도를 초과하지 않도록 원자적 차감을 보장한다 | P0 | FR-007 |
| FR-009 | 결제 실패/취소 시 예약된 쿠폰 사용을 해제해 재사용 가능 상태로 복구한다 | P0 | FR-007 |
| FR-010 | 만료·비활성·한도초과·최소금액미달 각각에 대해 구분된 오류 코드를 반환한다 | P0 | FR-006 |
| FR-011 | 수강생은 본인 쿠폰 사용 이력을 조회한다 | P2 | FR-007 |
| FR-012 | 만료된 쿠폰은 배치 또는 조회 시점 판정으로 `expired` 상태로 취급한다(별도 저장 없이 유효기간 비교로 판정) | P1 | FR-001 |

> **무모순 확인**: 검증(FR-005/006)은 소진 없이 계산만, 소진(FR-007)은 결제 확정 시 원자적 1회. "1결제 1쿠폰"(§1.3) 전제와 충돌 없음. 비활성(FR-003)은 신규 적용만 차단하고 이력은 보존 — FR-011과 충돌 없음.

---

## 4. Non-Functional Requirements

### 4.0 Scale Grade
**Startup** — 온라인 강의 플랫폼의 초기 서비스 규모를 가정(DAU 1,000~10,000). 프로모션 시 특정 쿠폰에 순간 트래픽이 몰릴 수 있어 동시성 정확성은 Growth 수준으로 설계하되, 전체 인프라 목표는 Startup 등급으로 잡는다.

### 4.1 Performance
- 쿠폰 검증 API(`POST /coupons/validate`): **p95 < 200ms**, 평시 50 req/s 처리.
- 쿠폰 소진 API(`POST /coupons/redeem`): **p95 < 300ms**(원자적 차감 포함).
- 프로모션 피크: 단일 인기 쿠폰에 대해 **동시 200 req 경합**에서도 한도 초과 0건, 데이터 정합성 100%.

### 4.2 Availability
- 목표 가용성 **99.9%**(월 다운타임 ≤ 43분).
- 쿠폰 서비스 장애 시 **결제는 쿠폰 없이 정상 진행 가능**해야 한다(쿠폰은 결제의 선택적 부가 기능 — fail-open on availability, fail-closed on correctness). 단 검증·소진 로직 자체는 오류 시 할인 미적용으로 안전하게 실패(fail-closed)한다.

### 4.3 Data
- **쿠폰 마스터**: 서비스 운영 기간 동안 보관. 비활성/만료 후에도 정산·감사 목적 보존.
- **사용 이력**: 결제와 연결되므로 **전자상거래 거래기록 보존의무에 준해 5년 보관**.
- **개인정보**: 사용 이력은 사용자 ID(내부 식별자)만 저장, 결제·회원 정보와는 참조로 연결. 회원 탈퇴 시 사용 이력은 익명화(사용자 ID를 비식별 처리)하되 거래 통계는 보존.
- **환불 연동 규칙**: 결제 환불 시 사용 이력은 삭제하지 않고 상태를 `refunded`로 표기. 쿠폰 사용 횟수 복원 여부는 관리자 정책 플래그(`restore_on_refund`)로 제어(기본: 복원 안 함).

### 4.4 Recovery
- RPO ≤ 5분(DB PITR 기준), RTO ≤ 30분. 쿠폰 사용 이력은 금액과 직결되므로 손실 시 결제 로그로 재구성 가능하도록 결제-쿠폰 참조 무결성을 유지한다.

### 4.5 Security
- **인증**: 모든 쿠폰 API는 인증 필수. `guest`는 접근 불가(401).
- **인가 규칙**:
  - `POST/PUT/DELETE /admin/coupons/**`, `GET /admin/coupons/**` → **`admin` 전용**. `student` 호출 시 403.
  - `POST /coupons/validate`, `POST /coupons/redeem` → **`student`**(본인 결제 컨텍스트). redeem은 요청자와 결제 소유자가 일치해야 하며 불일치 시 403.
  - `GET /coupons/me/usages` → **`student` 본인 이력만**. 타인 이력 요청 차단.
- **전송/저장 보호**: 전 구간 TLS. 쿠폰 코드는 평문 저장(공개 코드 성격)하되 발급 로그·관리자 액션은 감사 로그로 남긴다.
- **입력 검증**: 코드 형식(영숫자, 4~20자) 화이트리스트 검증, 할인율 0~100, 정액 할인 ≥ 0, 최소주문금액 ≥ 0, 유효기간 start < end 강제. **최종 할인 후 결제금액이 음수가 되지 않도록** 서버에서 재검증(할인액 = min(계산액, 주문금액)).
- **부정 사용 방지**: 코드 대입(brute-force) 방지를 위해 사용자·IP 단위 검증 시도 **rate limit(분당 10회, 429)** 적용. 카운터는 다중 인스턴스 간 공유되는 **중앙 저장소(Redis 등)**에 키 `ratelimit:{userId|ip}:validate`로 관리한다(인메모리 금지 — 인스턴스 수만큼 한도가 느슨해짐).

---

## 5. Technical Design

### 5.1 API Specification

#### POST /admin/coupons — 쿠폰 발행 (인가: admin)
- **Request**
```json
{
  "code": "WELCOME20",            // optional; 미지정 시 서버 자동 생성
  "discountType": "PERCENT",      // PERCENT | FIXED
  "discountValue": 20,             // PERCENT: 0~100, FIXED: 원 단위
  "maxDiscountAmount": 30000,      // PERCENT일 때 상한(optional)
  "minOrderAmount": 50000,
  "startsAt": "2026-09-01T00:00:00+09:00",
  "endsAt": "2026-09-30T23:59:59+09:00",
  "totalLimit": 100,               // null이면 무제한
  "perUserLimit": 1,
  "targetScope": "ALL",            // ALL | COURSE
  "targetCourseIds": []            // targetScope=COURSE일 때 필수
}
```
- **Response 201**
```json
{ "id": "cpn_01H...", "code": "WELCOME20", "status": "active", "createdAt": "2026-08-03T10:00:00+09:00" }
```
- **Error**: `400 VALIDATION_ERROR`(형식/범위 위반, start≥end), `409 DUPLICATE_CODE`(코드 중복), `403 FORBIDDEN`(admin 아님)

#### GET /admin/coupons — 쿠폰 목록/사용현황 (인가: admin)
- **Request**: query `status`, `page`, `size`
- **Response 200**: `{ "items": [{ "id","code","status","totalLimit","usedCount","remaining","endsAt" }], "page","size","total" }`
- **Error**: `403 FORBIDDEN`

#### PATCH /admin/coupons/{id}/deactivate — 비활성화 (인가: admin)
- **Response 200**: `{ "id","status":"inactive" }`
- **Error**: `404 NOT_FOUND`, `403 FORBIDDEN`

#### POST /coupons/validate — 쿠폰 검증·미리보기 (인가: student)
- **Request**
```json
{ "code": "WELCOME20", "orderAmount": 100000, "courseIds": ["crs_1"] }
```
- **Response 200**
```json
{ "valid": true, "discountAmount": 20000, "finalAmount": 80000, "couponId": "cpn_01H..." }
```
- **Error(200 with valid:false 또는 4xx)**: `EXPIRED`, `INACTIVE`, `NOT_FOUND`, `MIN_AMOUNT_NOT_MET`, `SOLD_OUT`, `ALREADY_USED`, `NOT_APPLICABLE`(대상 강의 불일치), `429 RATE_LIMITED`

#### POST /coupons/redeem — 쿠폰 소진(결제 확정 시, 예약) (인가: student, 본인 결제)
- **Request**: `{ "code": "WELCOME20", "orderId": "ord_1", "orderAmount": 100000, "courseIds": ["crs_1"] }`
- **Response 200**: `{ "redemptionId": "rdm_1", "state": "reserved", "discountAmount": 20000 }`
- **Error**: `409 ALREADY_USED`, `409 SOLD_OUT`, `410 EXPIRED`, `403 FORBIDDEN`(요청자≠결제소유자), 원자적 차감 실패 시 어떤 경우에도 초과 소진 없음

#### POST /coupons/redemptions/{id}/commit — 결제 성공 확정 (인가: system 전용)
- **Response 200**: `{ "state": "used" }` — `WHERE state='reserved'`로 reserved → used 멱등 전이. 신뢰된 결제 시스템(system 서비스 계정)만 호출.

#### POST /coupons/redemptions/{id}/release — 결제 실패/취소 시 해제 (인가: system 전용)
- **Response 200**: `{ "state": "released" }` — `WHERE state='reserved'`로 reserved → released 멱등 전이 + 동일 트랜잭션에서 `used_count` 원복. 영향 행 0이면 no-op. system 서비스 계정만 호출.

#### GET /coupons/me/usages — 본인 사용 이력 (인가: student 본인)
- **Response 200**: `{ "items": [{ "couponCode","orderId","discountAmount","state","usedAt" }] }`
- **Error**: `401 UNAUTHENTICATED`

> **인가 주체 요약**: `/admin/**`=admin, `/coupons/validate|redeem|me/**`=student(본인), commit/release는 **system 서비스 계정 전용**(결제 진위 위조 방지).

### 5.2 Database Schema

```sql
-- 쿠폰 마스터
CREATE TABLE coupons (
  id             TEXT PRIMARY KEY,
  code           TEXT NOT NULL UNIQUE,               -- 유일 코드 (FR-002)
  discount_type  TEXT NOT NULL CHECK (discount_type IN ('PERCENT','FIXED')),
  discount_value INTEGER NOT NULL CHECK (discount_value >= 0),
  max_discount_amount INTEGER,                        -- PERCENT 상한, nullable
  min_order_amount    INTEGER NOT NULL DEFAULT 0 CHECK (min_order_amount >= 0),
  starts_at      TIMESTAMPTZ NOT NULL,
  ends_at        TIMESTAMPTZ NOT NULL,
  total_limit    INTEGER,                             -- null=무제한
  per_user_limit INTEGER NOT NULL DEFAULT 1,
  used_count     INTEGER NOT NULL DEFAULT 0,          -- 원자적 차감 대상
  status         TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive')),
  target_scope   TEXT NOT NULL DEFAULT 'ALL' CHECK (target_scope IN ('ALL','COURSE')),
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (starts_at < ends_at),
  CHECK (discount_type <> 'PERCENT' OR discount_value <= 100)
);

-- 대상 강의 (target_scope=COURSE)
CREATE TABLE coupon_target_courses (
  coupon_id TEXT NOT NULL REFERENCES coupons(id) ON DELETE CASCADE,
  course_id TEXT NOT NULL,
  PRIMARY KEY (coupon_id, course_id)
);

-- 사용 이력 / 예약 (중복 사용·한도의 정본)
CREATE TABLE coupon_redemptions (
  id              TEXT PRIMARY KEY,
  coupon_id       TEXT NOT NULL REFERENCES coupons(id),
  user_id         TEXT NOT NULL,
  order_id        TEXT NOT NULL,
  discount_amount INTEGER NOT NULL,
  state           TEXT NOT NULL CHECK (state IN ('reserved','used','released','refunded')),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  used_at         TIMESTAMPTZ,
  -- 1인당 1회(perUserLimit=1) 및 결제 단위 멱등성 보장용 유니크 제약
  UNIQUE (coupon_id, order_id)
);

CREATE INDEX idx_redemptions_user ON coupon_redemptions (user_id);
```

> **1인당 한도(perUserLimit ≥ 1) 강제(FR-008)**: `perUserLimit=1`이 아닌 경우도 지원해야 하므로(재구매 유도용 "1인 N회") 부분 유니크 인덱스 대신 **카운트 기반 검증**을 표준으로 한다. 소진 트랜잭션에서
> `SELECT count(*) FROM coupon_redemptions WHERE coupon_id=? AND user_id=? AND state IN ('reserved','used') FOR UPDATE`
> 로 현재 사용 수를 잠금 후 조회하고, `< per_user_limit`일 때만 삽입한다(초과 시 `ALREADY_USED`). `perUserLimit=1` 최적화가 필요하면 부분 유니크 인덱스를 보조로 둘 수 있으나, 정본은 카운트 검증이다.
>
> **총 한도 동시성(FR-008)**: 소진은 단일 트랜잭션에서
> `UPDATE coupons SET used_count = used_count + 1 WHERE id = ? AND (total_limit IS NULL OR used_count < total_limit)`
> 를 실행하고 **영향 행 0이면 SOLD_OUT**으로 실패시킨다. 애플리케이션 락이 아닌 **DB 원자성**에 의존해 경합을 해결한다.
>
> **commit/release 멱등성·상태 가드(FR-009)**: 사가 재시도·중복 콜백에 대비해 상태 전이는 조건부 UPDATE로 멱등 처리한다. commit은 `WHERE state='reserved'`로 `used`로 전이하고, release는 `WHERE state='reserved'`로 `released` 전이 **및 동일 트랜잭션에서** `UPDATE coupons SET used_count = used_count - 1 WHERE id=?`를 수행한다. **영향 행 0이면 no-op**을 반환해 `used_count` 이중 원복(→ 한도 초과 소진)을 방지한다.

### 5.3 Architecture
- **모놀리식 서비스 내 Coupon 모듈**(도메인 경계 분리). 결제(Payment) 모듈과는 `redeem → PG 결제 → commit/release`의 사가(saga) 패턴으로 연동.
- 상태 전이: `reserved → used`(결제 성공) / `reserved → released`(결제 실패) / `used → refunded`(환불).
- 만료는 저장 상태가 아니라 **조회 시점 `now() vs ends_at` 비교로 판정**(FR-012). 별도 배치는 통계용으로만 선택 적용.
- 결제 서비스 장애와 무관하게 검증/소진은 독립 트랜잭션. 정합성 오류는 항상 fail-closed(할인 미적용).

#### 5.4 Pages

| Route | Audience | Auth | Linked FRs | Has FE Components | Primary State | Responsive |
|---|---|---|---|---|---|---|
| `/admin/coupons` | admin | Required | FR-004 | Yes | success(목록) | Yes |
| `/admin/coupons/new` | admin | Required | FR-001, FR-002 | Yes | success(폼) | Yes |
| `/admin/coupons/:id` | admin | Required | FR-003, FR-004 | Yes | success(상세) | Yes |
| `/checkout` (쿠폰 입력 영역) | student | Required | FR-005, FR-006, FR-010 | Yes | success(금액 미리보기) | Yes |
| `/mypage/coupons` | student | Required | FR-011 | Yes | success(이력) | Yes |

#### 5.4.1 Page State Matrix

| Route | loading | empty | error | success | no-permission | 비고 |
|---|---|---|---|---|---|---|
| `/admin/coupons` | 스켈레톤 테이블 | "발행된 쿠폰 없음" + 발행 CTA | 조회 실패 배너+재시도 | 쿠폰 목록/사용현황 | 403 안내→홈 | admin 전용 |
| `/admin/coupons/new` | 제출 중 버튼 로딩 | N/A(폼) | 필드 인라인 오류 / DUPLICATE_CODE 토스트 | 생성 완료→상세 이동 | 403 안내 | 유효성 즉시 검증 |
| `/admin/coupons/:id` | 스켈레톤 | N/A | 404/조회 실패 | 상세+비활성화 버튼 | 403 안내 | — |
| `/checkout` | 검증 중 스피너 | 코드 미입력 기본 상태 | EXPIRED/INACTIVE/MIN_AMOUNT/SOLD_OUT/ALREADY_USED/NOT_APPLICABLE/NOT_FOUND 인라인 메시지 | 할인액·최종금액 표시 | 401→로그인 유도 | rate limit(429) 안내 |
| `/mypage/coupons` | 스켈레톤 | "사용한 쿠폰 없음" | 조회 실패 재시도 | 사용 이력 리스트 | 401→로그인 | 본인 이력만 |

#### 5.5 User Flow

```mermaid
flowchart TD
    A[관리자: /admin/coupons/new] -->|발행 요청| B{입력 검증}
    B -->|형식/범위 위반| A
    B -->|코드 중복 DUPLICATE_CODE| A
    B -->|통과| C[쿠폰 생성 active] --> D[/admin/coupons 목록]
    D -->|비활성화| E[status=inactive]

    S[수강생: /checkout] --> F[쿠폰 코드 입력]
    F -->|POST /coupons/validate| G{검증}
    G -->|만료 EXPIRED| F
    G -->|비활성 INACTIVE| F
    G -->|최소금액 미달 MIN_AMOUNT_NOT_MET| F
    G -->|소진 SOLD_OUT| F
    G -->|이미 사용 ALREADY_USED| F
    G -->|유효| H[할인액·최종금액 표시]
    H -->|결제하기 → POST /coupons/redeem| I{원자적 소진}
    I -->|영향행 0 SOLD_OUT/ALREADY_USED| F
    I -->|reserved 성공| J[PG 결제]
    J -->|성공 → commit| K[state=used, 결제 완료]
    J -->|실패 → release| L[state=released, 재사용 가능]
    K --> M[/mypage/coupons 이력]
```

---

## 6. Implementation Phases

### Phase 1 — 쿠폰 도메인 & 발행 (P0 기반)
- **Tasks**: DB 스키마(coupons, coupon_target_courses, coupon_redemptions) 마이그레이션, 코드 유일성/자동생성(FR-002), 발행 API(FR-001), 입력 검증(§4.5), admin 인가.
- **Deliverable**: 관리자가 쿠폰을 발행/조회/비활성화(FR-003, FR-004)할 수 있는 백엔드 + 최소 Admin UI.

### Phase 2 — 검증·미리보기 (P0)
- **Tasks**: `POST /coupons/validate`(FR-005/006), 구분된 오류 코드(FR-010), rate limit, `/checkout` 쿠폰 입력 UI + 금액 미리보기.
- **Deliverable**: 수강생이 결제 전 할인액을 정확히 확인. 만료·비활성·최소금액 차단 동작.

### Phase 3 — 소진·동시성·사가 (P0 핵심)
- **Tasks**: `redeem/commit/release`(FR-007/009), 원자적 차감 + 부분 유니크 인덱스(FR-008), 결제 사가 연동, 동시성 부하 테스트(200 동시 요청 초과 0건 검증).
- **Deliverable**: 중복 사용·한도 초과·만료 적용이 동시성 환경에서도 100% 차단. 결제 실패 시 복구.

### Phase 4 — 이력·정산·부가 (P1/P2)
- **Tasks**: 본인 사용 이력(FR-011), 관리자 사용현황 집계 고도화, 환불 연동 상태(`refunded`, `restore_on_refund`), 만료 통계 배치(FR-012).
- **Deliverable**: 사용자/관리자 이력 화면, 환불·정산 정합성.

---

## 7. Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| 중복/만료 부정 적용 건수 | 0건 | 사용 이력 vs 한도 정합성 감사 쿼리(주간) |
| 동시성 한도 초과 발생 | 0건 | 부하 테스트 + 프로덕션 `used_count ≤ total_limit` 불변식 모니터링 |
| 쿠폰 검증 API p95 | < 200ms | APM(요청 지연 분포) |
| 쿠폰 적용 결제 전환율 | 발행 대비 사용률 ≥ 30% | `used redemptions / issued coupons` |
| 쿠폰 관련 결제 오류율 | < 0.5% | redeem/commit 실패율 대비 전체 결제 |
```
