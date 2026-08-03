# PRD: 쿠폰(할인) 기능

- **문서 버전**: v0.1 (Draft)
- **작성일**: 2026-08-04
- **상태**: 리뷰 대기 — §12 "결정 필요 사항" 확정 후 v1.0 승격

---

## 1. 배경 및 문제 정의

온라인 강의 플랫폼에 할인 수단이 없어 프로모션을 진행하려면 강의 정가 자체를 일시적으로 내리는 방식밖에 없다. 이 방식은 다음 문제를 만든다.

- 정가를 건드리므로 정가 인식이 훼손되고, 프로모션 종료 후 원복 누락 사고가 발생한다.
- 특정 대상(신규 가입자, 이탈 수강생, 제휴사 등)에게만 선택적으로 할인을 줄 수 없다.
- 할인의 효과(사용률, 매출 기여)를 측정할 데이터가 남지 않는다.

쿠폰을 도입해 **정가를 유지한 채 결제 시점에만 할인을 적용**하고, 발행·사용 이력을 추적 가능하게 만든다.

## 2. 목표 / 비목표

### 2.1 목표

1. 관리자가 조건(할인 방식, 유효기간, 대상 강의, 수량)을 지정해 쿠폰을 발행할 수 있다.
2. 수강생이 결제 화면에서 쿠폰을 적용해 할인된 금액으로 결제할 수 있다.
3. **한 번 사용된 쿠폰은 어떤 상황에서도 다시 사용될 수 없다** (동시 요청 포함).
4. **만료·소진·비활성 쿠폰은 적용될 수 없다.**
5. 발행 대비 사용 현황을 관리자가 조회할 수 있다.

### 2.2 비목표 (이번 범위 아님)

- 쿠폰 **중복 적용**(한 결제에 2장 이상) — 1차는 1결제 1쿠폰 고정
- 자동 적립형 포인트/마일리지, 적립금과의 혼합 결제
- 개인화 추천 쿠폰, 자동 발행 캠페인 엔진(가입 시 자동 지급 등)
- 구독/정기결제 상품에 대한 반복 할인
- 제휴사 정산, 쿠폰별 수익 배분

### 2.3 성공 지표

| 지표 | 목표 |
| --- | --- |
| 쿠폰 적용 결제의 결제 성공률 | 일반 결제 대비 -1%p 이내 |
| 중복 사용 사고 건수 | **0건** (하드 요구) |
| 만료 쿠폰 적용 성공 건수 | **0건** (하드 요구) |
| 쿠폰 발행 → 첫 사용까지 관리자 개입 | 0회 (셀프서비스) |
| 쿠폰 사용률(사용/발행) 대시보드 제공 | 출시와 동시 |

## 3. 용어 정의

| 용어 | 정의 |
| --- | --- |
| **쿠폰 정책(CouponPolicy)** | 할인 규칙의 원본. "10월 신규가입 20% 할인" 같은 캠페인 단위. 관리자가 생성. |
| **쿠폰(Coupon)** | 정책에서 파생되어 실제로 사용 가능한 단위. 코드 또는 특정 수강생 소유. |
| **공개형(PUBLIC)** | 하나의 코드를 여러 수강생이 각각 1회씩 사용. 총 수량으로 제한. (예: `WELCOME20`) |
| **개별발급형(ISSUED)** | 수강생 1명에게 귀속된 고유 코드. 소유자만 사용 가능. |
| **사용(Redeem)** | 결제 승인과 함께 쿠폰이 소모되어 재사용 불가 상태가 되는 것. |
| **선점(Reserve)** | 결제 승인 전, 해당 쿠폰을 임시로 잠가 다른 결제가 쓰지 못하게 하는 것. |

## 4. 사용자 스토리

### 관리자

- A1. 나는 할인율/할인액, 유효기간, 적용 대상 강의, 발행 수량을 지정해 쿠폰 정책을 만들고 싶다.
- A2. 나는 특정 수강생 목록에 쿠폰을 일괄 발급하고 싶다.
- A3. 나는 발행한 쿠폰의 사용 현황(발행/사용/잔여/할인 총액)을 보고 싶다.
- A4. 나는 문제가 생긴 쿠폰 정책을 즉시 중단시키고 싶다 (이미 사용된 건은 유지).
- A5. 나는 오발급된 개별 쿠폰을 회수하고 싶다.

### 수강생

- S1. 나는 결제 화면에서 코드를 입력해 할인을 받고 싶다.
- S2. 나는 내가 보유한 쿠폰 목록과 각각의 만료일을 보고 싶다.
- S3. 나는 쿠폰을 왜 쓸 수 없는지(만료/대상 아님/최소금액 미달) 명확히 알고 싶다.
- S4. 나는 결제를 취소/환불했을 때, 쓴 쿠폰이 살아 돌아오길 기대한다.

## 5. 기능 요구사항

### 5.1 쿠폰 정책 (관리자)

**FR-1. 정책 생성.** 관리자는 다음 속성으로 정책을 만든다.

| 속성 | 필수 | 설명 |
| --- | --- | --- |
| `name` | O | 관리용 이름 |
| `discountType` | O | `PERCENTAGE` \| `FIXED_AMOUNT` |
| `discountValue` | O | 정률: 1~100(%), 정액: 1원 이상 |
| `maxDiscountAmount` | △ | 정률일 때만. 미설정 시 상한 없음 |
| `minOrderAmount` | X | 기본 0원. 결제 원금이 이 값 미만이면 적용 불가 |
| `scope` | O | `ALL` \| `COURSE` \| `CATEGORY` — 적용 대상 범위 |
| `targetIds` | △ | `scope`가 ALL이 아닐 때 필수 |
| `issueType` | O | `PUBLIC` \| `ISSUED` |
| `code` | △ | PUBLIC일 때 필수, 유일해야 함 |
| `totalQuantity` | X | null이면 무제한 |
| `perUserLimit` | O | 기본 1. 동일 수강생의 최대 사용 횟수 |
| `validFrom` / `validUntil` | O | 절대 기간. 서버 시각 기준(KST) |
| `validDays` | △ | ISSUED 한정 — 발급일로부터 N일. `validUntil`과 택일 |

**FR-2. 검증 규칙.** 다음은 생성 시점에 거부한다.

- `PERCENTAGE`인데 `discountValue`가 1~100 범위 밖
- `validFrom >= validUntil`
- PUBLIC인데 `code`가 이미 존재 (대소문자 무시 비교)
- `scope != ALL`인데 `targetIds`가 비어 있음

**FR-3. 정책 상태.** `DRAFT` → `ACTIVE` → (`SUSPENDED` ↔ `ACTIVE`) → `ENDED`

- `SUSPENDED`: 신규 사용 즉시 차단. **이미 완료된 결제는 되돌리지 않는다.**
- `ENDED`: `validUntil` 경과 시 자동 전이 (배치 또는 조회 시 판정).

**FR-4. 개별 발급.** 관리자는 수강생 ID 목록(또는 CSV)을 올려 ISSUED 쿠폰을 일괄 발급한다. 발급 결과는 성공/실패 건수로 리포트하고, 실패 사유(존재하지 않는 사용자, 이미 보유 등)를 함께 반환한다.

**FR-5. 회수.** 관리자는 미사용 쿠폰을 `REVOKED`로 전환할 수 있다. 이미 `USED`인 쿠폰은 회수 불가.

### 5.2 쿠폰 조회·적용 (수강생)

**FR-6. 보유 쿠폰 목록.** 사용 가능 / 사용 완료 / 만료 탭으로 구분. 각 항목에 할인 조건, 적용 대상, 만료일(D-day) 표시.

**FR-7. 결제 화면 적용.**

- 코드 직접 입력 + 보유 쿠폰 선택 UI 둘 다 제공.
- 적용 시 **미리보기 API**로 최종 결제 금액을 즉시 계산해 보여준다. 이 단계에서는 쿠폰을 소모하지 않는다.
- 1결제 1쿠폰. 다른 쿠폰 선택 시 기존 것은 자동 해제.

**FR-8. 적용 가능성 판정.** 아래 순서로 검사하고, **첫 번째 실패 사유**를 사용자에게 반환한다.

| # | 검사 | 실패 코드 | 사용자 메시지 |
| --- | --- | --- | --- |
| 1 | 코드 존재 | `COUPON_NOT_FOUND` | 존재하지 않는 쿠폰이에요. |
| 2 | 정책 `ACTIVE` | `COUPON_INACTIVE` | 현재 사용할 수 없는 쿠폰이에요. |
| 3 | 소유자 일치 (ISSUED) | `COUPON_NOT_OWNED` | 존재하지 않는 쿠폰이에요.<sup>*</sup> |
| 4 | 기간 내 (`validFrom ≤ now < validUntil`) | `COUPON_EXPIRED` | 유효기간이 지난 쿠폰이에요. |
| 5 | 미사용 상태 | `COUPON_ALREADY_USED` | 이미 사용한 쿠폰이에요. |
| 6 | 잔여 수량 > 0 | `COUPON_EXHAUSTED` | 준비된 수량이 모두 소진됐어요. |
| 7 | 사용자별 한도 미초과 | `COUPON_USER_LIMIT` | 이 쿠폰은 1회만 사용할 수 있어요. |
| 8 | 대상 강의 일치 | `COUPON_NOT_APPLICABLE` | 이 강의에는 사용할 수 없는 쿠폰이에요. |
| 9 | 최소 결제금액 충족 | `COUPON_MIN_AMOUNT` | {N}원 이상 결제 시 사용할 수 있어요. |

<sup>*</sup> 남의 쿠폰 코드를 넣었을 때 "다른 사람 것"이라고 알려주면 코드 유효성이 노출되므로 `NOT_FOUND`와 동일 메시지로 응답한다. (로그에는 실제 사유 기록)

**FR-9. 할인 금액 계산.**

```
base       = 강의 정가 (쿠폰 적용 대상 상품 금액)
raw        = discountType == PERCENTAGE
             ? floor(base * discountValue / 100)
             : discountValue
discount   = min(raw, maxDiscountAmount ?? ∞, base)
final      = base - discount
```

- 원 단위 **내림(floor)**. 부가세 포함 최종가 기준으로 계산한다.
- `final`이 0원이면 PG 호출 없이 **0원 결제**로 처리하고 수강 권한을 즉시 부여한다. (§8 E-3)

### 5.3 결제 연동 — 중복 사용 방지 (핵심)

**FR-10. 2단계 소모 (선점 → 확정).**

```
[1] 결제 요청       : reserve()  — 쿠폰을 RESERVED로 잠금 + 만료시각(now+15분) 기록
[2] PG 결제 승인     : (외부)
[3-a] 승인 성공     : confirm()  — RESERVED → USED, usedAt/orderId 기록
[3-b] 승인 실패/이탈 : release()  — RESERVED → AVAILABLE
[3-c] 응답 유실     : 배치가 예약 만료 시각 경과분을 AVAILABLE로 회수
```

**FR-11. 동시성 보장.** 다음 중 하나 이상으로 **DB 레벨에서** 보장한다. 애플리케이션 레벨 검사만으로는 불충분하다.

- **유니크 제약**: `coupon_redemption(coupon_id)` 유니크 인덱스 — 같은 쿠폰의 두 번째 사용 INSERT가 물리적으로 실패.
  - 사용자별 한도까지 강제하려면 `(policy_id, user_id, seq)` 유니크.
- **조건부 UPDATE**: `UPDATE coupon SET status='RESERVED' WHERE id=? AND status='AVAILABLE'` → 영향 행 수가 0이면 실패 처리.
- 잔여 수량 차감도 동일하게 `WHERE remaining > 0` 조건부 UPDATE 또는 원자적 카운터로 처리한다. **읽고-계산해서-쓰기 금지.**

> **AC**: 동일 쿠폰에 대해 100개 동시 결제 요청을 보냈을 때, 정확히 1건만 성공하고 99건은 `COUPON_ALREADY_USED`를 받는다.

**FR-12. 멱등성.** 결제 요청에 `Idempotency-Key`를 받아, 동일 키의 재요청은 쿠폰을 다시 소모하지 않고 최초 결과를 그대로 반환한다.

**FR-13. 만료 판정 기준 시점.** 유효기간 검사는 **결제 승인 확정(confirm) 시점의 서버 시각**을 기준으로 한 번 더 수행한다. 미리보기 때 유효했더라도 결제 진행 중 만료되면 거부한다. (클라이언트 시각은 절대 신뢰하지 않는다.)

### 5.4 취소·환불

**FR-14. 전액 환불** 시 쿠폰을 복원한다. 단 **복원 시점에 이미 만료된 쿠폰은 복원하지 않는다** (`EXPIRED`로 전환). 사용자에게는 환불 완료 안내에 이 사실을 함께 표기한다.

**FR-15. 부분 환불** 시 쿠폰은 복원하지 않는다. 환불액은 실제 결제액(할인 후) 기준으로 안분한다.

```
환불액 = 부분환불 요청액 × (실결제액 / 정가)
```

**FR-16. 감사 로그.** 쿠폰의 모든 상태 전이(발급/선점/사용/해제/복원/회수)를 이력 테이블에 append-only로 남긴다. 누가·언제·어떤 주문으로 전이했는지 추적 가능해야 한다.

### 5.5 관리자 대시보드

**FR-17.** 정책별로 발행 수 / 사용 수 / 사용률 / 총 할인액 / 쿠폰 적용 매출을 조회한다. 기간 필터, CSV 내보내기 지원.

## 6. 데이터 모델 (개념)

```
coupon_policy
  id, name, discount_type, discount_value, max_discount_amount,
  min_order_amount, scope, target_ids, issue_type, code(UNIQUE, nullable),
  total_quantity, issued_count, used_count, per_user_limit,
  valid_from, valid_until, valid_days, status, created_by, created_at

coupon                                   -- ISSUED만 행 생성. PUBLIC은 redemption으로 관리
  id, policy_id, user_id, code(UNIQUE), status, issued_at,
  expires_at, reserved_until, used_at, order_id, version

coupon_redemption                        -- 실제 사용 사실의 단일 진실 원천
  id, policy_id, coupon_id(UNIQUE, nullable), user_id, order_id(UNIQUE),
  discount_amount, base_amount, status, reserved_until, created_at

coupon_history                           -- append-only 감사 로그
  id, coupon_id, policy_id, from_status, to_status, actor, reason,
  order_id, created_at
```

**쿠폰 상태**: `AVAILABLE` → `RESERVED` → `USED` / `EXPIRED` / `REVOKED`
(`RESERVED` → `AVAILABLE` 복귀 가능, `USED` → `AVAILABLE` 은 환불에 한해 가능)

**인덱스 요구**

- `coupon_policy.code` UNIQUE (대소문자 정규화 후 저장)
- `coupon.code` UNIQUE
- `coupon_redemption.order_id` UNIQUE ← 멱등성
- `coupon_redemption.coupon_id` UNIQUE (부분 인덱스: status != RELEASED) ← 중복 사용 차단
- `(policy_id, user_id)` 복합 ← 사용자별 한도 조회

## 7. API 개요

| Method | Endpoint | 설명 |
| --- | --- | --- |
| POST | `/admin/coupon-policies` | 정책 생성 |
| PATCH | `/admin/coupon-policies/{id}/status` | ACTIVE / SUSPENDED 전환 |
| POST | `/admin/coupon-policies/{id}/issue` | 대상자 일괄 발급 |
| DELETE | `/admin/coupons/{id}` | 회수 (REVOKED) |
| GET | `/admin/coupon-policies/{id}/stats` | 사용 현황 |
| GET | `/me/coupons?status=available` | 보유 쿠폰 목록 |
| POST | `/orders/{orderId}/coupon/preview` | 적용 미리보기 (소모 없음) |
| POST | `/orders/{orderId}/coupon` | 선점(reserve) — 결제 요청과 함께 |
| DELETE | `/orders/{orderId}/coupon` | 해제(release) |

- 미리보기 응답: `{ applicable, discountAmount, finalAmount, reason? }`
- 실패 응답: `{ code, message }` — 코드는 §5.2 FR-8 표 기준

## 8. 엣지 케이스

| # | 상황 | 처리 |
| --- | --- | --- |
| E-1 | 결제 진행 중 관리자가 정책을 SUSPEND | 이미 `RESERVED`인 건은 확정 허용. 신규 선점만 차단. |
| E-2 | 결제 진행 중 쿠폰 만료 (`validUntil` 경과) | confirm 시점 재검증에서 거부. 선점 해제 후 결제 롤백. |
| E-3 | 할인액 ≥ 정가 → 0원 결제 | PG 미호출, 주문은 `PAID(0원)`으로 생성, 수강권 즉시 부여, 쿠폰은 `USED`. |
| E-4 | 무료 강의에 쿠폰 적용 시도 | `COUPON_MIN_AMOUNT` 또는 대상 불가로 거부. |
| E-5 | 사용자가 결제창에서 이탈 (응답 없음) | `reserved_until` 15분 경과 시 배치가 `AVAILABLE`로 회수. |
| E-6 | 같은 사용자가 탭 2개에서 동시 결제 | FR-11 조건부 UPDATE로 1건만 성공. |
| E-7 | PG는 승인됐는데 confirm 단계에서 서버 장애 | 결제 대사(reconciliation) 배치가 PG 승인 건과 redemption을 대조해 보정. 승인 건 우선. |
| E-8 | 장바구니에 여러 강의 (`scope=COURSE`) | 대상 강의 금액에만 할인 적용. 대상 강의가 없으면 `NOT_APPLICABLE`. |
| E-9 | 환불 시점에 쿠폰이 이미 만료 | 복원하지 않고 `EXPIRED` 처리 + 안내 문구 노출. (FR-14) |
| E-10 | 코드 무차별 대입(brute force) | IP·계정당 코드 시도 분당 10회 제한, 초과 시 429. 코드는 추측 어려운 난수 8자 이상. |
| E-11 | 정책 수정으로 할인율 변경 | 이미 발급된 쿠폰은 **발급 시점 조건을 스냅샷으로 고정**. 소급 적용하지 않는다. |
| E-12 | 서버 타임존 불일치 | 모든 시각은 UTC 저장, KST 표기. 만료 판정은 서버 UTC 기준. |

## 9. 비기능 요구사항

- **성능**: 미리보기 API p95 < 200ms. 선점 API p95 < 300ms.
- **정합성**: 중복 사용 0건은 성능보다 우선한다. 필요 시 락 경합을 감수한다.
- **가용성**: 쿠폰 서비스 장애 시 **쿠폰 없는 정가 결제는 계속 가능해야 한다** (기능 격리).
- **보안**: 할인 금액은 **항상 서버에서 재계산**한다. 클라이언트가 보낸 금액은 검증용으로만 쓰고 신뢰하지 않는다.
- **관측성**: 쿠폰 적용 실패 사유별 카운터, 선점→확정 전환율, 미회수 선점 수를 메트릭으로 노출. 중복 사용 시도 탐지 시 알림.

## 10. 출시 계획

| 단계 | 범위 |
| --- | --- |
| **Phase 1 (MVP)** | 정책 생성, PUBLIC 코드형 쿠폰, 코드 입력 적용, 2단계 소모, 전액 환불 복원, 기본 통계 |
| **Phase 2** | ISSUED 개별 발급/일괄 발급, 보유 쿠폰 목록 UI, 회수, 부분 환불 안분 |
| **Phase 3** | 카테고리 범위, CSV 내보내기, 대시보드 고도화 |

## 11. QA 체크리스트 (인수 기준)

- [ ] 동일 쿠폰 100 동시 요청 → 성공 정확히 1건 (FR-11)
- [ ] `validUntil` 1초 전 선점 → 1초 후 confirm → 거부 (E-2)
- [ ] 동일 `Idempotency-Key` 2회 요청 → 쿠폰 1회만 소모 (FR-12)
- [ ] 정률 30% + 상한 10,000원, 정가 50,000원 → 할인 10,000원
- [ ] 최소금액 30,000원 쿠폰을 29,999원 주문에 적용 → `COUPON_MIN_AMOUNT`
- [ ] 전액 환불 → 쿠폰 재사용 가능 / 만료 후 환불 → 재사용 불가 (FR-14)
- [ ] 남의 ISSUED 코드 입력 → `COUPON_NOT_FOUND` 메시지 (FR-8 각주)
- [ ] 클라이언트에서 `discountAmount` 조작 → 서버 재계산값으로 결제 (§9 보안)
- [ ] 결제창 이탈 15분 후 → 쿠폰 재사용 가능 (E-5)

## 12. 결정 필요 사항 (Open Questions)

기획/결제 담당 확인 후 확정한다. 아래는 이 문서의 **잠정 가정**이며, 다르게 정해지면 §5가 바뀐다.

1. **선점 TTL 15분** — PG사 결제창 세션 만료 시간과 맞춰야 한다. 현재 PG 정책 확인 필요.
2. **환불 시 복원 정책** — 본 문서는 "전액 환불 시 복원, 단 만료 시 미복원"을 가정했다. 프로모션 쿠폰은 복원하지 않는 정책도 흔하다. 어느 쪽인가?
3. **부분 환불 안분식** — 정가 기준 vs 실결제액 기준. 본 문서는 실결제액 기준을 가정.
4. **1결제 1쿠폰 제약** — 향후 중복 적용을 열 계획이 있다면 데이터 모델에서 `order_id` 유니크를 지금 걸면 안 된다. 확정 필요.
5. **부가세/세금계산서 처리** — 할인이 공급가액에 반영되는지, 회계팀 요건 확인 필요.
6. **PUBLIC 쿠폰의 `coupon` 행 생성 여부** — 본 문서는 redemption만으로 관리하는 안을 택했다. 발급 시점에 행을 미리 만드는 안 대비 장단 검토 필요.

---

**Appendix. 상태 전이도**

```
             issue
               ↓
          ┌─────────┐  reserve   ┌──────────┐  confirm   ┌────────┐
          │AVAILABLE│ ─────────→ │ RESERVED │ ─────────→ │  USED  │
          └─────────┘            └──────────┘            └────────┘
             ↑  │                     │                      │
   refund    │  │ expire      release │                      │ refund
   (미만료)   │  ↓                     │                      │ (전액)
          ┌─────────┐  ←──────────────┘                      │
          │ EXPIRED │  ←──────────────────────────────────────
          └─────────┘         (환불 시점에 이미 만료)
               ↑
          ┌─────────┐
          │ REVOKED │  ← admin revoke (AVAILABLE에서만 가능)
          └─────────┘
```
