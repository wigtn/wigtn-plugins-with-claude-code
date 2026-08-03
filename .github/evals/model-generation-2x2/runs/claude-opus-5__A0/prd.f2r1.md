# PRD: 온라인 강의 플랫폼 쿠폰 기능

| 항목 | 내용 |
| --- | --- |
| 문서 버전 | v1.0 |
| 작성일 | 2026-08-03 |
| 상태 | Draft (리뷰 대기) |
| 대상 릴리스 | TBD |

---

## 1. 개요

### 1.1 배경

현재 플랫폼에는 강의 가격을 할인할 수 있는 수단이 정가 변경밖에 없다. 이 때문에

- 마케팅 캠페인(신규 가입 유도, 시즌 프로모션)을 실행할 때마다 강의 가격 자체를 수정해야 하고,
- 특정 고객군(재수강생, 기업 교육 담당자, CS 보상 대상자)에게만 선별적으로 혜택을 주는 것이 불가능하며,
- 할인으로 발생한 매출 변화를 캠페인별로 귀속시켜 측정할 수 없다.

쿠폰은 위 세 가지 문제를 한 번에 해결하는 표준적인 수단이다.

### 1.2 목표

1. 관리자가 코드로 정의된 할인 혜택(쿠폰)을 발행하고 관리할 수 있다.
2. 수강생이 결제 과정에서 쿠폰 코드를 입력해 할인을 적용받을 수 있다.
3. **어떤 상황에서도 쿠폰이 정해진 횟수를 초과해 사용되거나, 만료된 뒤에 사용되지 않는다.**
4. 관리자가 쿠폰별 사용 현황과 할인 금액을 확인할 수 있다.

### 1.3 성공 지표

| 지표 | 목표 |
| --- | --- |
| 쿠폰 초과 사용(중복 사용) 건수 | **0건** — 타협 불가 |
| 만료·비활성 쿠폰의 사용 성사 건수 | **0건** — 타협 불가 |
| 쿠폰 검증 API p95 응답 시간 | < 300ms |
| 쿠폰 적용 결제의 결제 실패율 | 미적용 결제 대비 +1%p 이내 |
| 첫 캠페인 쿠폰 사용률(발급 대비 사용) | 15% 이상 |

### 1.4 범위 외 (Non-goals)

이번 릴리스에서 다루지 **않는다**. 향후 확장은 §9 참고.

- 쿠폰 자동 추천 / 최적 쿠폰 자동 선택
- 쿠폰 중복 적용(한 결제에 2장 이상)
- 추천인 코드, 적립금, 마일리지 등 쿠폰 외 할인 수단
- 구독(정기결제)에 대한 쿠폰 적용 — 단건 강의 결제만 대상
- 쿠폰 코드 대량 생성 후 CSV 다운로드 등 대량 배포 파이프라인
- 사용자 간 쿠폰 양도/선물

---

## 2. 용어 정의

| 용어 | 정의 |
| --- | --- |
| **쿠폰(Coupon)** | 관리자가 정의한 할인 혜택의 템플릿. 코드, 할인 방식, 유효기간, 사용 조건을 가진다. |
| **발행(Issue)** | 관리자가 쿠폰을 생성하고 활성화하는 행위. |
| **사용/교환(Redemption)** | 수강생이 결제를 완료하면서 쿠폰을 소모하는 행위. 결제 성공과 1:1로 대응한다. |
| **적용(Apply)** | 결제 전 단계에서 쿠폰을 장바구니/주문서에 붙여 할인 금액을 미리 계산하는 행위. **아직 소모된 것이 아니다.** |
| **선점(Hold)** | 결제 승인 직전, 쿠폰 사용 권한을 짧은 시간 독점적으로 확보하는 상태. |
| **공개 쿠폰** | 코드를 아는 누구나 사용 가능. 전체 사용 한도로 제어. |
| **지정 쿠폰** | 특정 사용자에게만 귀속. 해당 사용자만 사용 가능. |

---

## 3. 사용자 및 시나리오

### 3.1 페르소나

- **마케팅 담당자(관리자)** — 캠페인 기간에 맞춰 쿠폰을 발행하고 성과를 본다. 개발자 도움 없이 스스로 처리하고 싶다.
- **CS 담당자(관리자)** — 불만 고객에게 개별 보상 쿠폰을 즉시 발급하고 싶다.
- **수강생** — 결제 화면에서 코드를 넣고 얼마가 깎이는지 바로 확인하고 싶다. 안 되면 왜 안 되는지 알고 싶다.

### 3.2 핵심 시나리오

**S1. 신규 가입 프로모션**
마케팅 담당자가 `WELCOME30`(30% 할인, 최대 3만원, 8/1~8/31, 1인 1회, 전체 1,000회)을 발행한다. 수강생이 결제 화면에서 코드를 입력하면 즉시 할인 금액이 반영되고, 결제 완료 시 사용 처리된다. 같은 계정으로 재사용 시도하면 "이미 사용한 쿠폰"으로 거절된다.

**S2. CS 보상**
CS 담당자가 특정 수강생에게만 `유효기간 7일, 1회 한정, 5,000원 할인` 지정 쿠폰을 발급한다. 다른 계정이 코드를 알아내도 사용할 수 없다.

**S3. 만료 직전 동시 요청**
수강생이 만료 1초 전에 결제를 시작하고 결제사 승인이 3초 걸린다. 쿠폰 유효성은 **결제 승인 요청 시점**을 기준으로 판정하며, 선점된 쿠폰은 그 결제 트랜잭션이 끝날 때까지 유효하다. (§6.3)

**S4. 마지막 1장 경쟁**
전체 한도 1,000회 중 999회가 소진된 쿠폰에 100명이 동시에 결제를 시도한다. 정확히 1명만 성공하고 나머지 99명은 "한도 소진" 안내를 받으며, 이때 **결제는 발생하지 않는다.** (§6.4)

---

## 4. 기능 요구사항

### 4.1 관리자 — 쿠폰 발행

> **FR-A1** 관리자는 다음 속성을 지정해 쿠폰을 생성할 수 있다.

| 속성 | 필수 | 설명 | 제약 |
| --- | --- | --- | --- |
| 쿠폰명 | ✅ | 관리용 이름 | 1~100자 |
| 코드 | ✅ | 사용자가 입력하는 문자열 | 4~20자, 영문 대문자+숫자, **전역 유일**. 미입력 시 자동 생성 |
| 할인 유형 | ✅ | `정률(PERCENTAGE)` / `정액(FIXED_AMOUNT)` | |
| 할인 값 | ✅ | 정률: 1~100(%), 정액: 1원 이상 | |
| 최대 할인 금액 | 정률 시 ✅ | 정률 쿠폰의 할인 상한 | 1원 이상 |
| 최소 주문 금액 | | 이 금액 미만 주문에는 사용 불가 | 기본 0 |
| 유효 시작 일시 | ✅ | | |
| 유효 종료 일시 | ✅ | | 시작 일시보다 이후 |
| 전체 사용 한도 | | 쿠폰 총 사용 가능 횟수 | 미지정 시 무제한 |
| 1인당 사용 한도 | ✅ | 한 사용자가 사용 가능한 횟수 | 기본 1 |
| 적용 대상 | ✅ | `전체` / `특정 강의` / `특정 카테고리` | |
| 대상 사용자 | | 지정 시 해당 사용자만 사용 가능(지정 쿠폰) | |

> **FR-A2** 코드는 대소문자를 구분하지 않는다. 입력된 코드는 대문자로 정규화해 저장·조회한다.
> **FR-A3** 시각적으로 혼동되는 문자(`0/O`, `1/I/l`)는 자동 생성 코드에서 제외한다.
> **FR-A4** 관리자는 쿠폰을 **비활성화**할 수 있다. 비활성화 즉시 신규 사용이 차단되며, 이미 완료된 결제에는 영향이 없다.
> **FR-A5** 관리자는 쿠폰을 **삭제할 수 없다.** 사용 이력의 정합성을 위해 비활성화만 가능하다.
> **FR-A6** 1회 이상 사용된 쿠폰은 **할인 조건(할인 유형/값/최소 주문 금액/적용 대상)을 수정할 수 없다.** 유효 종료 일시 단축과 전체 한도 증가만 허용한다. 조건을 바꾸려면 새 쿠폰을 발행한다.
> **FR-A7** 모든 쿠폰 생성·수정·비활성화는 **감사 로그**(행위자, 시각, 변경 전후 값)를 남긴다.

### 4.2 관리자 — 쿠폰 조회 및 현황

> **FR-A8** 관리자는 쿠폰 목록을 상태(활성/예정/만료/소진/비활성), 코드, 이름으로 필터·검색할 수 있다.
> **FR-A9** 쿠폰 상세에서 사용 횟수 / 잔여 한도 / 누적 할인 금액 / 쿠폰 적용 매출을 확인할 수 있다.
> **FR-A10** 쿠폰별 사용 이력(사용자, 주문번호, 사용 일시, 할인 금액)을 조회할 수 있다.

### 4.3 수강생 — 쿠폰 적용

> **FR-U1** 수강생은 결제 화면에서 쿠폰 코드를 직접 입력할 수 있다.
> **FR-U2** 코드 입력 시 **실시간 검증**이 수행되고, 성공 시 할인 금액과 최종 결제 금액이 즉시 갱신된다.
> **FR-U3** 검증 실패 시 **사유별로 구분된 메시지**를 보여준다. (§4.5)
> **FR-U4** 수강생은 적용한 쿠폰을 결제 전에 해제할 수 있다.
> **FR-U5** 한 결제에는 **쿠폰 1장만** 적용 가능하다. 이미 적용된 상태에서 새 코드를 입력하면 교체 여부를 확인한다.
> **FR-U6** 수강생은 마이페이지 > 내 쿠폰함에서 본인에게 발급된 지정 쿠폰과 사용 이력을 볼 수 있다.

### 4.4 결제 연동

> **FR-P1** 최종 결제 금액은 **서버에서 재계산**한다. 클라이언트가 보낸 할인 금액·최종 금액은 신뢰하지 않으며, 불일치 시 결제를 거부한다.
> **FR-P2** 쿠폰 사용 처리(redemption)는 **결제 성공 시에만** 확정된다.
> **FR-P3** 결제 실패·취소·이탈 시 쿠폰은 **자동으로 복구**되어 재사용 가능하다.
> **FR-P4** 할인 후 결제 금액이 0원이 되는 경우, PG 결제를 생략하고 즉시 수강 등록 처리한다.
> **FR-P5** 결제 요청에는 **멱등성 키(Idempotency-Key)** 를 필수로 요구한다. 동일 키의 재요청은 최초 결과를 그대로 반환하며 쿠폰을 추가로 소모하지 않는다.

### 4.5 환불 정책

> **FR-R1** 쿠폰 적용 결제를 **전액 환불**하면 쿠폰 사용 이력은 `REFUNDED` 상태가 되고, 다음 조건을 **모두** 만족할 때 쿠폰 사용 횟수가 복구된다.
> - 쿠폰이 아직 유효기간 내일 것
> - 쿠폰이 비활성화되지 않았을 것
>
> 조건을 만족하지 않으면 복구하지 않고, 환불 화면에 그 사실을 안내한다.
>
> **FR-R2** 환불 금액은 **실제 결제 금액(할인 후)** 기준이다. 정가 기준으로 환불하지 않는다.
> **FR-R3** 부분 환불은 이번 범위에서 지원하지 않는다.

### 4.6 검증 실패 메시지

| 코드 | 조건 | 사용자 메시지 |
| --- | --- | --- |
| `NOT_FOUND` | 존재하지 않는 코드 | 존재하지 않는 쿠폰 코드입니다. |
| `INACTIVE` | 관리자가 비활성화 | 사용할 수 없는 쿠폰입니다. |
| `NOT_STARTED` | 유효 시작 전 | {시작일}부터 사용할 수 있는 쿠폰입니다. |
| `EXPIRED` | 유효기간 만료 | 유효기간이 지난 쿠폰입니다. (~{종료일}) |
| `GLOBAL_LIMIT_EXCEEDED` | 전체 한도 소진 | 준비된 수량이 모두 소진되었습니다. |
| `USER_LIMIT_EXCEEDED` | 1인당 한도 초과 | 이미 사용한 쿠폰입니다. |
| `NOT_ELIGIBLE_USER` | 지정 쿠폰의 대상자가 아님 | 존재하지 않는 쿠폰 코드입니다. ※ |
| `NOT_APPLICABLE_COURSE` | 적용 대상 강의가 아님 | 이 강의에는 사용할 수 없는 쿠폰입니다. |
| `MIN_AMOUNT_NOT_MET` | 최소 주문 금액 미달 | {최소금액}원 이상 결제 시 사용할 수 있습니다. |

※ **의도적으로 `NOT_FOUND`와 동일한 메시지를 노출한다.** "당신은 대상이 아니다"라는 응답은 코드가 실재한다는 사실을 알려주어 코드 열거(enumeration) 공격의 단서가 된다.

---

## 5. 데이터 모델

```
coupons
  id                  PK
  code                VARCHAR(20)  UNIQUE NOT NULL   -- 대문자 정규화
  name                VARCHAR(100) NOT NULL
  discount_type       ENUM('PERCENTAGE','FIXED_AMOUNT') NOT NULL
  discount_value      INT NOT NULL
  max_discount_amount INT NULL
  min_order_amount    INT NOT NULL DEFAULT 0
  starts_at           TIMESTAMPTZ NOT NULL
  expires_at          TIMESTAMPTZ NOT NULL
  total_limit         INT NULL          -- NULL = 무제한
  used_count          INT NOT NULL DEFAULT 0
  per_user_limit      INT NOT NULL DEFAULT 1
  target_type         ENUM('ALL','COURSE','CATEGORY') NOT NULL
  target_ids          JSONB NULL
  assigned_user_id    BIGINT NULL FK   -- 지정 쿠폰
  is_active           BOOLEAN NOT NULL DEFAULT TRUE
  created_by          BIGINT FK
  created_at / updated_at

  CHECK (expires_at > starts_at)
  CHECK (discount_type <> 'PERCENTAGE' OR (discount_value BETWEEN 1 AND 100))
  CHECK (discount_type <> 'PERCENTAGE' OR max_discount_amount IS NOT NULL)
  CHECK (total_limit IS NULL OR used_count <= total_limit)   -- ★ 초과 사용 최종 방어선
  INDEX (is_active, expires_at)

coupon_redemptions
  id                PK
  coupon_id         BIGINT FK NOT NULL
  user_id           BIGINT FK NOT NULL
  order_id          BIGINT FK NOT NULL
  discount_amount   INT NOT NULL
  original_amount   INT NOT NULL
  final_amount      INT NOT NULL
  status            ENUM('HELD','REDEEMED','RELEASED','REFUNDED') NOT NULL
  held_until        TIMESTAMPTZ NULL     -- HELD 상태의 만료 시각
  redeemed_at       TIMESTAMPTZ NULL
  created_at

  UNIQUE (order_id)                                          -- 주문당 쿠폰 1장
  UNIQUE (coupon_id, user_id, order_id)
  PARTIAL UNIQUE (coupon_id, user_id) WHERE status IN ('HELD','REDEEMED')
                                                             -- ★ per_user_limit = 1 인 경우의 중복 사용 방어선
  INDEX (coupon_id, status)
  INDEX (status, held_until)                                 -- 만료 hold 정리용
```

> **설계 노트 — 왜 DB 제약을 최종 방어선으로 두는가**
> 애플리케이션 레벨의 "조회 후 확인 후 증가" 패턴은 동시 요청에서 반드시 깨진다. `used_count <= total_limit` CHECK 제약과 partial unique index는 애플리케이션 로직에 버그가 있어도 초과 사용을 **물리적으로 불가능**하게 만든다. §1.3의 "0건" 목표는 이 제약이 있어야만 보장된다.

### 5.1 Redemption 상태 전이

```
                   ┌──── 결제 승인 성공 ────► REDEEMED ──── 전액 환불 ────► REFUNDED
                   │                                                          │
[없음] ── 선점 ──► HELD                                        (조건 충족 시 used_count 복구)
                   │
                   └─ 결제 실패 / 취소 / 이탈 / hold 만료 ──► RELEASED
                                                                (used_count 복구)
```

| 전이 | 트리거 | `used_count` |
| --- | --- | --- |
| → `HELD` | 결제 승인 요청 직전 선점 | **+1** |
| `HELD` → `REDEEMED` | PG 승인 성공 | 변화 없음 |
| `HELD` → `RELEASED` | PG 승인 실패 / 사용자 취소 / hold TTL 경과 | **-1** |
| `REDEEMED` → `REFUNDED` | 전액 환불 | 조건부 **-1** (FR-R1) |

---

## 6. 핵심 로직

### 6.1 할인 금액 계산

```
if discount_type == FIXED_AMOUNT:
    discount = discount_value
else:  # PERCENTAGE
    discount = floor(original_amount * discount_value / 100)
    discount = min(discount, max_discount_amount)

discount = min(discount, original_amount)   # 결제 금액이 음수가 되지 않도록
final_amount = original_amount - discount
```

- 원 단위 **내림(floor)** 으로 통일한다. 반올림은 사업자에게 불리한 방향으로 1원이 새므로 쓰지 않는다.
- `discount == original_amount`(0원 결제)는 허용한다. (FR-P4)

### 6.2 검증 순서

비용이 낮고 실패 가능성이 높은 순으로 검사해 불필요한 조회를 줄인다.

1. 코드 정규화 → 쿠폰 조회 (`NOT_FOUND`)
2. `is_active` 확인 (`INACTIVE`)
3. 기간 확인 (`NOT_STARTED` / `EXPIRED`)
4. 지정 쿠폰이면 `assigned_user_id` 일치 확인 (`NOT_ELIGIBLE_USER`)
5. 적용 대상 강의 확인 (`NOT_APPLICABLE_COURSE`)
6. 최소 주문 금액 확인 (`MIN_AMOUNT_NOT_MET`)
7. 전체 한도 확인 (`GLOBAL_LIMIT_EXCEEDED`)
8. 1인당 한도 확인 — 사용자의 `HELD`+`REDEEMED` 카운트 조회 (`USER_LIMIT_EXCEEDED`)

### 6.3 만료 판정 기준 시각

> **결제 승인 요청 직전의 선점(HELD) 시각**을 기준으로 판정한다.

- 적용 화면 진입 시점이 아니다 — 사용자가 화면을 오래 열어둔 사이 만료될 수 있다.
- PG 승인 완료 시점도 아니다 — 승인에 수 초가 걸리는데, 이미 돈이 빠져나간 뒤 "만료됨"으로 거절하면 환불 처리가 필요해진다.
- 선점에 성공한 결제는 PG 승인이 유효기간을 넘겨 끝나더라도 **정상 처리한다.** hold TTL은 **10분**.
- 시각 비교는 모두 **UTC**로 하고, 관리자 입력·표시는 `Asia/Seoul` 기준으로 변환한다. `expires_at`은 **exclusive**(해당 시각 도달 시 만료)로 다룬다.

### 6.4 동시성 제어

결제 승인 요청 직전, 단일 트랜잭션에서 다음을 수행한다.

```sql
BEGIN;

-- ① 조건부 UPDATE. 한도 초과 시 0 rows → 트랜잭션 중단
UPDATE coupons
   SET used_count = used_count + 1
 WHERE id = :coupon_id
   AND is_active = TRUE
   AND now() >= starts_at
   AND now() <  expires_at
   AND (total_limit IS NULL OR used_count < total_limit);
-- affected rows = 0  →  ROLLBACK, GLOBAL_LIMIT_EXCEEDED 반환

-- ② redemption 선점. partial unique index 위반 시 중복 사용 → 트랜잭션 중단
INSERT INTO coupon_redemptions
       (coupon_id, user_id, order_id, discount_amount, status, held_until)
VALUES (:coupon_id, :user_id, :order_id, :discount, 'HELD', now() + interval '10 minutes');
-- unique violation  →  ROLLBACK, USER_LIMIT_EXCEEDED 반환

COMMIT;
```

- 조건부 `UPDATE`의 `WHERE`절이 **원자적 검사-후-증가**를 수행한다. 별도 SELECT로 확인한 뒤 UPDATE하면 안 된다.
- 이 트랜잭션이 커밋된 **후에** PG 승인을 호출한다. 승인 실패 시 보상 트랜잭션으로 `RELEASED` 처리 + `used_count` 감소.
- `per_user_limit > 1`인 쿠폰은 partial unique index가 동작하지 않으므로, 해당 사용자 행에 대해 `SELECT ... FOR UPDATE`로 직렬화한 뒤 카운트를 확인한다.

### 6.5 미아(orphan) hold 정리

PG 응답이 유실되거나 서버가 죽어 `HELD`로 남는 레코드가 생길 수 있다.

- **1분 주기 배치**가 `status='HELD' AND held_until < now()` 인 레코드를 조회한다.
- 각 건에 대해 **PG 거래 상태를 조회**한 뒤,
  - 승인됨 → `REDEEMED`로 전환 (사용자가 돈을 냈으므로 수강권을 준다)
  - 미승인/실패 → `RELEASED` + `used_count` 감소
- 상태 조회 없이 무조건 해제하면 "결제는 됐는데 쿠폰 사용 이력이 없는" 상태가 생기므로 반드시 대사(reconciliation)를 거친다.

---

## 7. API 명세 (초안)

### 7.1 쿠폰 검증 (수강생)

```
POST /api/v1/coupons/validate
Authorization: Bearer <token>

{ "code": "welcome30", "courseId": 1234 }
```

성공 `200`
```json
{
  "valid": true,
  "coupon": { "code": "WELCOME30", "name": "신규가입 30% 할인",
              "discountType": "PERCENTAGE", "expiresAt": "2026-08-31T14:59:59Z" },
  "originalAmount": 99000, "discountAmount": 29700, "finalAmount": 69300
}
```

실패 `200` — 검증 실패는 HTTP 에러가 아니라 정상 응답의 결과값이다.
```json
{ "valid": false, "reason": "EXPIRED",
  "message": "유효기간이 지난 쿠폰입니다. (~2026년 8월 31일)" }
```

> **Rate limit**: 사용자당 **분당 10회**. 초과 시 `429`. 코드 무차별 대입 방지.

### 7.2 결제 생성 (쿠폰 포함)

```
POST /api/v1/orders
Idempotency-Key: <uuid>

{ "courseId": 1234, "couponCode": "WELCOME30", "expectedFinalAmount": 69300 }
```

- `expectedFinalAmount`는 **검증용**이다. 서버 재계산 결과와 다르면 `409 AMOUNT_MISMATCH`로 거절하고, 클라이언트는 금액을 갱신해 사용자에게 재확인을 요청한다.
- 쿠폰 사용 불가 시 `409` + `reason` 코드.

### 7.3 관리자 API

```
POST   /api/v1/admin/coupons              쿠폰 발행
GET    /api/v1/admin/coupons              목록·검색
GET    /api/v1/admin/coupons/{id}         상세 + 사용 현황
PATCH  /api/v1/admin/coupons/{id}         수정 (FR-A6 제약)
POST   /api/v1/admin/coupons/{id}/deactivate   비활성화
GET    /api/v1/admin/coupons/{id}/redemptions  사용 이력
```

---

## 8. 비기능 요구사항

| 구분 | 요구사항 |
| --- | --- |
| **성능** | 검증 API p95 < 300ms. 쿠폰 조회는 `code` 유니크 인덱스 단건 조회. |
| **동시성** | 단일 쿠폰에 대해 **초당 500건**의 동시 사용 시도에서 초과 사용 0건. |
| **보안** | 검증 API rate limit(§7.1). 대상 아님 응답은 `NOT_FOUND`로 위장(§4.5). 관리자 API는 `ADMIN` 권한 필수. |
| **정합성** | 쿠폰 사용과 주문 생성은 동일 트랜잭션 경계 안에서 처리. PG 호출은 트랜잭션 밖. |
| **감사성** | 모든 상태 전이와 관리자 조작은 로그로 남기며 삭제 불가. |
| **모니터링** | 쿠폰 사용률, 검증 실패 사유별 분포, `HELD` 적체 건수, 보상 트랜잭션 실패 건수를 대시보드화. `HELD` 적체가 임계치를 넘으면 알림. |

---

## 9. 마일스톤

| 단계 | 범위 | 산출물 |
| --- | --- | --- |
| **M1** | 데이터 모델, 쿠폰 CRUD, 관리자 발행 화면 | 관리자가 쿠폰을 만들 수 있다 |
| **M2** | 검증 API, 결제 화면 연동, 할인 계산 | 수강생이 할인을 받을 수 있다 |
| **M3** | 선점/확정/해제, 동시성 제어, 미아 hold 배치 | **중복 사용·만료 사용 0건 보장** |
| **M4** | 사용 현황 대시보드, 환불 연동, 내 쿠폰함 | 운영 가능 상태 |

> M3는 M2와 **분리하되 같은 릴리스에 포함**한다. M2까지만 배포하면 중복 사용이 가능한 상태로 노출된다.

---

## 10. 향후 확장 (This release 이후)

- 쿠폰 대량 생성 및 코드 CSV 내보내기
- 쿠폰 자동 발급 트리거(가입, 첫 구매, 수료, 휴면 복귀)
- 쿠폰 중복 적용 및 적용 우선순위 정책
- 구독 결제 쿠폰 (첫 N개월 할인)
- 부분 환불 시 할인액 비례 배분
- 캠페인 단위 그룹핑 및 A/B 테스트

---

## 11. 미해결 질문

| # | 질문 | 결정 필요 주체 |
| --- | --- | --- |
| Q1 | 정률 쿠폰의 최대 할인 금액을 필수로 강제할 것인가? (실수로 고가 강의에 90% 할인이 나가는 사고 방지 목적) | 마케팅 + 재무 |
| Q2 | hold TTL 10분이 PG 승인 최대 소요 시간을 충분히 덮는가? | 결제 담당 |
| Q3 | 환불 시 쿠폰 복구를 기본값으로 할 것인가, 관리자 승인제로 할 것인가? | CS + 재무 |
| Q4 | 기업 교육 등 B2B 대량 발급 요구가 이번 릴리스에 필요한가? | 세일즈 |
| Q5 | 0원 결제 시 PG를 완전히 우회해도 정산·세금계산서 처리에 문제가 없는가? | 재무 |
