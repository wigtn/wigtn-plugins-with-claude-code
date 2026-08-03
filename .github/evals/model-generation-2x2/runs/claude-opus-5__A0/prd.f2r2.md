# PRD: 쿠폰 (Coupon) 기능

| 항목 | 내용 |
| --- | --- |
| 문서 상태 | Draft |
| 작성일 | 2026-08-03 |
| 대상 제품 | 온라인 강의 플랫폼 |
| 관련 시스템 | 결제, 강의 카탈로그, 회원, 정산 |

---

## 1. 개요

### 1.1 배경

현재 플랫폼에는 강의 가격을 할인할 수 있는 수단이 강의 자체의 가격 변경밖에 없다. 이 때문에

- 마케팅 캠페인(신규 가입, 재방문 유도, 제휴사 프로모션)을 실행할 수 없다.
- CS 대응(불만 고객 보상, 환불 대신 크레딧 제공)을 수기로 처리한다.
- 할인의 대상·기간·수량을 제어할 수 없어 매출 손실 위험을 통제하기 어렵다.

### 1.2 문제 정의

1. **관리자**는 조건(대상 강의, 할인율, 기간, 수량)을 지정해 할인 수단을 발행할 방법이 없다.
2. **수강생**은 결제 시 할인을 적용할 방법이 없다.
3. 할인 수단을 도입할 경우 **중복 사용**과 **만료된 쿠폰 사용**으로 인한 금전적 손실이 발생할 수 있으며, 특히 동시 요청 상황에서 취약하다.

### 1.3 목표 (Goals)

- G1. 관리자가 조건부 쿠폰을 발행하고 배포·회수·모니터링할 수 있다.
- G2. 수강생이 결제 플로우에서 쿠폰을 등록·선택·적용하고 최종 결제 금액을 확인할 수 있다.
- G3. 동시 요청 환경을 포함해 **쿠폰 1건은 정확히 1회만 사용**됨을 시스템이 보장한다.
- G4. 만료·조건 미충족 쿠폰은 결제 확정 시점에 반드시 차단된다.
- G5. 결제 실패·취소·환불 시 쿠폰 상태가 일관되게 복원된다.

### 1.4 비목표 (Non-Goals) — 이번 범위 제외

- 적립금/포인트/크레딧 시스템
- 구독·정기결제에 대한 반복 할인 적용
- 추천인(referral) 자동 쿠폰 발급 엔진
- 쿠폰 간 자동 최적 조합 추천 (스태킹은 v1에서 금지)
- 강사가 직접 쿠폰을 발행하는 셀프서비스 (관리자만 발행)
- 다국가 통화 및 세금 규칙 (KRW 단일 통화 가정)

---

## 2. 성공 지표

| 구분 | 지표 | 목표 |
| --- | --- | --- |
| 정확성 | 쿠폰 중복 사용 발생 건수 | **0건** (하드 요구사항) |
| 정확성 | 만료 쿠폰 적용 성공 건수 | **0건** (하드 요구사항) |
| 정확성 | 할인 금액 오차로 인한 CS 티켓 | 월 0건 |
| 활용도 | 쿠폰 사용률 (사용 / 발급) | 출시 후 8주 내 25% 이상 |
| 전환 | 쿠폰 적용 세션의 결제 완료율 | 미적용 대비 +10%p |
| 성능 | 쿠폰 검증 API p95 지연 | < 200ms |
| 운영 | 캠페인 발행 소요 시간 | 관리자 1인 5분 이내 |

---

## 3. 사용자 및 핵심 시나리오

### 3.1 페르소나

- **마케팅 관리자**: 캠페인 단위로 쿠폰을 발행하고 성과를 본다.
- **CS 담당자**: 개별 고객에게 보상 쿠폰을 1장 발급한다.
- **수강생**: 강의를 결제할 때 보유 쿠폰 중 가장 유리한 것을 적용한다.

### 3.2 사용자 스토리

| ID | 스토리 |
| --- | --- |
| US-1 | 관리자로서, 특정 카테고리 강의에 대해 20% 할인(최대 3만원) 쿠폰을 1,000장 한정으로 발행하고 싶다. |
| US-2 | 관리자로서, 발행한 쿠폰의 발급/사용/잔여 수량과 할인 총액을 대시보드에서 보고 싶다. |
| US-3 | 관리자로서, 오발행된 캠페인을 즉시 중단(회수)하고 싶다. |
| US-4 | CS 담당자로서, 특정 회원에게만 보이는 쿠폰을 1장 지급하고 싶다. |
| US-5 | 수강생으로서, 받은 코드를 입력해 내 계정에 쿠폰을 등록하고 싶다. |
| US-6 | 수강생으로서, 결제 화면에서 적용 가능한 쿠폰만 보고 선택해 최종 금액을 확인하고 싶다. |
| US-7 | 수강생으로서, 왜 이 쿠폰을 못 쓰는지(최소금액 미달, 대상 아님, 만료) 이유를 알고 싶다. |
| US-8 | 수강생으로서, 결제를 취소하면 사용한 쿠폰을 다시 쓸 수 있길 기대한다. |

---

## 4. 도메인 모델

### 4.1 용어

| 용어 | 정의 |
| --- | --- |
| **쿠폰 정책 (CouponPolicy)** | 할인 규칙·조건·기간의 정의. 캠페인 단위. 관리자가 만드는 대상. |
| **쿠폰 코드 (CouponCode)** | 정책을 사용자에게 전달하는 문자열. 공용(public) / 개별(unique) 두 종류. |
| **보유 쿠폰 (UserCoupon)** | 특정 회원에게 귀속된 쿠폰 1장. **사용/만료의 단위이자 중복 사용 방지의 단위**. |
| **사용 이력 (CouponRedemption)** | 보유 쿠폰이 특정 주문에 사용된 기록. 불변(immutable). |

### 4.2 핵심 설계 결정

> **결정 1. 사용 단위는 `UserCoupon` 1행이다.**
> 코드가 아니라 "회원에게 귀속된 쿠폰 1장"을 소진 단위로 삼는다. 공용 코드도 사용자가 등록(발급)하는 순간 `UserCoupon` 행이 생성되며, 이 행에 대한 상태 전이가 유일한 소진 경로다. 이 설계로 중복 사용 방지가 단일 행의 조건부 UPDATE 문제로 축소된다.

> **결정 2. 쿠폰 스태킹(중복 적용)은 v1에서 금지한다.**
> 주문 1건당 쿠폰 1장. 할인 조합 규칙은 복잡도와 오류 위험이 크므로 v2로 미룬다.

> **결정 3. 만료 판정은 배치가 아니라 사용 시점 계산이 기준이다.**
> 배치는 UI 표시용 상태 갱신일 뿐이며, 실제 차단은 결제 확정 트랜잭션 내부의 `valid_until > now()` 검사로 이루어진다. 배치 지연이 금전적 손실로 이어지지 않게 한다.

### 4.3 상태 머신 (UserCoupon)

```
                ┌──────────────┐
   발급 ───────▶│  AVAILABLE   │
                └──────┬───────┘
                       │ 결제 확정 (원자적 전이)
                       ▼
                ┌──────────────┐   결제 취소/환불    ┌──────────────┐
                │     USED     │────────────────────▶│  AVAILABLE   │
                └──────────────┘   (기간 남은 경우)   └──────────────┘
                       │                                    │
                       │ 취소했으나 이미 기간 만료           │ valid_until 경과
                       ▼                                    ▼
                ┌──────────────────────────────────────────────┐
                │                   EXPIRED                    │
                └──────────────────────────────────────────────┘
                       ▲
                       │ 관리자 회수
                ┌──────┴───────┐
                │   REVOKED    │
                └──────────────┘
```

| 상태 | 의미 | 진입 조건 |
| --- | --- | --- |
| `AVAILABLE` | 사용 가능 | 발급 완료, 기간 내 |
| `USED` | 사용 완료 | 결제 확정 성공 |
| `EXPIRED` | 만료 | `valid_until` 경과 |
| `REVOKED` | 회수 | 관리자가 정책 또는 개별 쿠폰 중단 |

`PENDING`(결제 시도 중 임시 점유) 상태는 두지 않는다. 결제 확정 전까지 쿠폰은 `AVAILABLE`을 유지하고, 소진은 결제 승인 트랜잭션 안에서 한 번에 일어난다. 이유는 §7.1 참조.

---

## 5. 기능 요구사항

### 5.1 관리자 — 쿠폰 정책 발행

**FR-A1. 정책 생성 폼**

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| 캠페인명 | ✓ | 내부 식별용 |
| 사용자 노출명 | ✓ | 예: "여름방학 20% 할인" |
| 할인 유형 | ✓ | `FIXED_AMOUNT` (정액) / `PERCENTAGE` (정률) |
| 할인 값 | ✓ | 정액: 원 단위 / 정률: 1~100 |
| 최대 할인 금액 | 정률 시 ✓ | 정률 쿠폰의 할인 상한 (cap) |
| 최소 주문 금액 | | 미달 시 적용 불가 |
| 적용 범위 | ✓ | `ALL` / `CATEGORY` / `COURSE` / `INSTRUCTOR` |
| 범위 대상 ID | 범위 지정 시 ✓ | 다중 선택 가능 |
| 제외 대상 ID | | 범위 내 특정 강의 제외 |
| 유효기간 유형 | ✓ | `ABSOLUTE`(시작~종료) / `RELATIVE`(발급 후 N일) |
| 총 발행 한도 | | 미입력 시 무제한 |
| 1인당 발급 한도 | ✓ | 기본값 1 |
| 코드 유형 | ✓ | `PUBLIC`(공용 코드 1개) / `UNIQUE`(1회용 코드 N개 생성) / `DIRECT`(코드 없이 지정 회원에게 직접 지급) |
| 대상 회원 조건 | | `ALL` / `NEW_USER`(구매 이력 없음) / `SPECIFIC`(회원 ID 목록·CSV 업로드) |

**FR-A2.** 정책 생성 시 미리보기로 "10만원 강의에 적용 시 → 8만원" 형태의 계산 결과를 보여준다.

**FR-A3.** `UNIQUE` 코드는 생성 시 지정 수량만큼 발급하고 CSV로 내려받을 수 있다. 코드는 혼동 문자(`0/O`, `1/I/l`)를 제외한 대문자·숫자 12자리, 암호학적 난수로 생성한다.

**FR-A4. 정책 수정 제약**
- 이미 1건이라도 사용된 정책은 **할인 유형·할인 값·적용 범위를 수정할 수 없다.** (이미 발급된 쿠폰의 가치가 사후 변경되는 것을 방지)
- 수정 가능 항목: 노출명, 종료일 단축, 총 발행 한도 증가, 활성/중단.

**FR-A5. 회수(Revoke)**
- 정책 단위 중단: 미사용 `UserCoupon`을 일괄 `REVOKED` 처리. 이미 `USED`인 건은 영향 없음.
- 개별 회수: 특정 회원의 쿠폰 1장 회수.
- 모든 회수는 사유 입력 필수이며 감사 로그에 남는다.

**FR-A6. 대시보드**
- 정책별: 발급 수 / 사용 수 / 사용률 / 잔여 수량 / 총 할인 금액 / 쿠폰 적용 주문의 총 결제액.
- 기간 필터 및 CSV 내보내기.

**FR-A7. 권한**
- 정책 생성·수정·회수: `ADMIN_MARKETING` 이상.
- 개별 쿠폰 지급: `CS_AGENT` 이상. 단 1회 지급 최대 매수 및 일일 한도를 둔다.
- 조회: `ADMIN_VIEWER` 이상.

### 5.2 수강생 — 쿠폰 등록 및 보관함

**FR-U1.** 마이페이지 > 쿠폰함에서 보유 쿠폰을 `사용 가능` / `사용 완료` / `만료` 탭으로 본다. 사용 가능 탭은 만료 임박순 정렬이 기본이다.

**FR-U2.** 코드 입력창에 코드를 입력해 쿠폰을 등록한다. 입력값은 대소문자를 구분하지 않고 공백·하이픈을 무시한다.

**FR-U3.** 등록 실패 시 사유별 메시지를 반환한다.

| 사유 | 메시지 |
| --- | --- |
| 존재하지 않는 코드 | "존재하지 않는 쿠폰 코드입니다." |
| 이미 사용된 unique 코드 | "이미 사용된 쿠폰 코드입니다." |
| 이미 본인이 등록함 | "이미 등록한 쿠폰입니다. 쿠폰함에서 확인하세요." |
| 발행 한도 소진 | "쿠폰이 모두 소진되었습니다." |
| 1인당 한도 초과 | "이 쿠폰은 계정당 N장까지 등록할 수 있습니다." |
| 기간 종료 | "종료된 쿠폰입니다." |
| 대상 회원 아님 | "이 쿠폰을 사용할 수 있는 대상이 아닙니다." |

**FR-U4.** 만료 3일 전 쿠폰이 있으면 알림(앱 푸시/이메일)을 1회 발송한다. 알림 수신 여부는 설정에서 끌 수 있다.

**FR-U5.** 코드 입력은 **계정당 분당 5회, 시간당 20회**로 제한한다. 초과 시 429와 함께 쿨다운을 안내한다. (무작위 대입으로 유효 코드를 찾아내는 것을 방지)

### 5.3 결제 — 쿠폰 적용

**FR-P1.** 결제 페이지에서 현재 주문에 **적용 가능한** 쿠폰 목록을 노출한다. 적용 불가 쿠폰은 목록 하단에 회색 처리하고 사유를 함께 표시한다(US-7).

**FR-P2.** 기본 정렬은 **할인 금액이 가장 큰 순**이며, 최대 할인 쿠폰을 자동 선택하지 않고 사용자가 명시적으로 선택한다.

**FR-P3.** 쿠폰 선택 시 즉시 금액 요약을 갱신한다.

```
강의 금액          100,000원
쿠폰 할인          -20,000원   (여름방학 20% 할인)
─────────────────────────────
최종 결제 금액      80,000원
```

**FR-P4.** 주문 상품이 변경되면 선택된 쿠폰의 유효성을 재검증하고, 무효해졌으면 자동 해제 후 사용자에게 알린다.

**FR-P5. 할인 계산 규칙**
- 정률: `floor(주문금액 × 할인율 / 100)`, 이후 `min(계산값, 최대할인금액)` 적용. 원 단위 절사.
- 정액: `min(할인값, 주문금액)` — 할인이 주문금액을 초과해도 음수가 되지 않는다.
- 최종 결제 금액이 0원이 되는 경우, 결제사 호출 없이 **0원 결제**로 즉시 주문을 완료한다.
- 다중 상품 주문에서 특정 강의에만 적용되는 쿠폰은 **해당 강의의 금액에만** 할인을 계산한다.

**FR-P6.** 결제 요청은 클라이언트가 계산한 금액을 신뢰하지 않는다. 서버가 쿠폰 ID와 주문 정보를 받아 금액을 재계산하며, 클라이언트가 보낸 예상 금액과 다르면 결제를 중단하고 재확인을 요구한다.

### 5.4 검증 규칙 (결제 확정 시점, 전부 통과해야 함)

| # | 규칙 | 실패 시 코드 |
| --- | --- | --- |
| V1 | 쿠폰이 요청 회원의 소유 | `COUPON_NOT_OWNED` |
| V2 | 상태가 `AVAILABLE` | `COUPON_ALREADY_USED` / `COUPON_REVOKED` |
| V3 | `valid_from <= now() < valid_until` | `COUPON_EXPIRED` |
| V4 | 정책이 `ACTIVE` | `COUPON_POLICY_INACTIVE` |
| V5 | 주문 금액 >= 최소 주문 금액 | `MIN_ORDER_AMOUNT_NOT_MET` |
| V6 | 주문 상품이 적용 범위에 포함, 제외 목록에 없음 | `COUPON_NOT_APPLICABLE` |
| V7 | 대상 회원 조건 충족 (예: 신규 회원) | `NOT_ELIGIBLE_USER` |
| V8 | 주문에 이미 적용된 다른 쿠폰 없음 | `COUPON_STACKING_NOT_ALLOWED` |
| V9 | 이미 보유·수강 중인 강의가 아님 | `ALREADY_ENROLLED` |

동일한 검증 함수를 결제 페이지 조회(FR-P1)와 결제 확정(§7.1) 양쪽에서 재사용해 두 시점의 판정이 어긋나지 않게 한다.

### 5.5 중복 사용 방지 (핵심 요구사항)

**FR-C1. 데이터 무결성**
- `coupon_redemptions.user_coupon_id`에 **UNIQUE 제약**을 건다. 애플리케이션 로직이 실패해도 DB가 2회 사용을 물리적으로 거부한다. 최후의 방어선.

**FR-C2. 원자적 상태 전이**
- 소진은 조건부 UPDATE 한 문장으로 수행한다.
  ```sql
  UPDATE user_coupons
     SET status = 'USED', used_at = now(), order_id = :orderId, version = version + 1
   WHERE id = :userCouponId
     AND user_id = :userId
     AND status = 'AVAILABLE'
     AND valid_until > now();
  ```
- **영향 행 수가 1이 아니면 즉시 롤백**하고 결제를 실패시킨다. 조회 후 갱신(read-then-write) 패턴은 금지한다.

**FR-C3. 트랜잭션 경계**
- 쿠폰 소진과 주문 확정은 **동일 DB 트랜잭션**에 포함한다. 결제사(PG) 승인은 이 트랜잭션 밖에 있으므로 §7.1의 순서를 따른다.

**FR-C4. 멱등성**
- 결제 확정 API는 `Idempotency-Key` 헤더를 필수로 받는다. 동일 키 재요청은 최초 처리 결과를 그대로 반환하며 쿠폰을 재차 소진하지 않는다.
- 네트워크 재시도, 사용자의 결제 버튼 더블클릭, PG 웹훅 중복 발송이 모두 이 경로로 흡수된다.

**FR-C5. 발행 한도 동시성**
- 총 발행 한도가 있는 정책의 발급은 원자적 증가로 처리한다.
  ```sql
  UPDATE coupon_policies
     SET issued_count = issued_count + 1
   WHERE id = :policyId
     AND (max_issue_count IS NULL OR issued_count < max_issue_count);
  ```
- 1인당 발급 한도는 `UNIQUE(policy_id, user_id, seq)` 형태의 제약으로 보강한다.

**FR-C6. 클라이언트 보호**
- 결제 버튼은 요청 중 비활성화한다. 단 이는 UX 보완일 뿐이며, 정합성은 FR-C1~C4에만 의존한다.

### 5.6 만료 처리

**FR-E1.** 유효기간 유형
- `ABSOLUTE`: 정책의 `valid_from` ~ `valid_until`을 그대로 쿠폰에 복사.
- `RELATIVE`: 발급 시각 + N일. 종료 시각은 해당 일자의 `23:59:59 KST`로 절상한다.
- 두 유형 모두 정책 종료일을 넘길 수 없다. `min(계산된 만료일, 정책 종료일)`.

**FR-E2.** 시간대는 저장·비교 모두 UTC로 하고, 표시만 `Asia/Seoul`로 변환한다.

**FR-E3.** 만료 배치를 15분 주기로 실행해 `AVAILABLE` 이면서 `valid_until < now()`인 쿠폰을 `EXPIRED`로 전이한다. **이는 표시 목적일 뿐**이며, 실제 차단은 V3(§5.4)의 실시간 검사가 담당한다.

**FR-E4.** 결제 페이지에 진입해 쿠폰을 선택한 뒤 결제 완료 전에 만료되면, 결제 확정에서 V3로 차단되고 "선택하신 쿠폰의 유효기간이 만료되었습니다. 다시 확인해 주세요." 안내와 함께 결제 페이지로 되돌린다.

### 5.7 결제 실패·취소·환불

**FR-R1. 결제 실패**: 쿠폰 소진은 결제 승인 이후에만 커밋되므로 실패 시 쿠폰은 `AVAILABLE`을 유지한다. 별도 복원 로직이 필요 없다.

**FR-R2. 전액 환불**
- 쿠폰의 기간이 남아 있으면 → `AVAILABLE`로 복원하고 `coupon_redemptions.reverted_at`을 기록한다.
- 기간이 이미 지났으면 → `EXPIRED`로 전이한다. 만료된 쿠폰을 되살리지 않는다.
- 환불 금액은 **실제 결제 금액**(할인 후)을 기준으로 한다.

**FR-R3. 부분 환불**: 다중 상품 주문에서 쿠폰이 적용된 강의만 환불하는 경우, 쿠폰은 **복원하지 않는다.** (남은 상품이 최소 주문 금액 조건을 더 이상 충족하지 못하는 등 재계산이 모호하므로) 이 정책은 환불 화면에 명시한다.

**FR-R4. 어뷰징 방지**: "쿠폰 적용 결제 → 환불 → 쿠폰 재사용" 반복이 가능하므로, 동일 쿠폰의 복원 횟수를 **최대 3회**로 제한하고 초과 시 자동 `REVOKED` 처리 후 운영팀에 알린다.

**FR-R5. 정산**: 강사 정산 기준 금액은 쿠폰 할인 부담 주체에 따라 달라진다. **v1에서는 할인 전액을 플랫폼이 부담**하며, 강사 정산은 정가 기준으로 계산한다. (강사 분담 모델은 v2)

---

## 6. 데이터 모델

```sql
-- 쿠폰 정책 (캠페인)
CREATE TABLE coupon_policies (
  id                BIGSERIAL PRIMARY KEY,
  name              VARCHAR(200) NOT NULL,           -- 내부 캠페인명
  display_name      VARCHAR(200) NOT NULL,           -- 사용자 노출명
  discount_type     VARCHAR(20)  NOT NULL,           -- FIXED_AMOUNT | PERCENTAGE
  discount_value    INT          NOT NULL,
  max_discount_amount INT,                           -- PERCENTAGE 시 필수
  min_order_amount  INT          NOT NULL DEFAULT 0,
  scope_type        VARCHAR(20)  NOT NULL,           -- ALL | CATEGORY | COURSE | INSTRUCTOR
  validity_type     VARCHAR(20)  NOT NULL,           -- ABSOLUTE | RELATIVE
  valid_from        TIMESTAMPTZ,
  valid_until       TIMESTAMPTZ,
  valid_days        INT,                             -- RELATIVE 시 필수
  code_type         VARCHAR(20)  NOT NULL,           -- PUBLIC | UNIQUE | DIRECT
  max_issue_count   INT,                             -- NULL = 무제한
  issued_count      INT          NOT NULL DEFAULT 0,
  per_user_limit    INT          NOT NULL DEFAULT 1,
  target_user_type  VARCHAR(20)  NOT NULL DEFAULT 'ALL',
  status            VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE', -- ACTIVE | INACTIVE | TERMINATED
  created_by        BIGINT       NOT NULL,
  created_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),

  CONSTRAINT chk_percentage_cap
    CHECK (discount_type <> 'PERCENTAGE' OR max_discount_amount IS NOT NULL),
  CONSTRAINT chk_discount_range
    CHECK (discount_value > 0
           AND (discount_type <> 'PERCENTAGE' OR discount_value <= 100)),
  CONSTRAINT chk_issued_within_limit
    CHECK (max_issue_count IS NULL OR issued_count <= max_issue_count)
);

-- 정책 적용 범위 (포함/제외)
CREATE TABLE coupon_policy_scopes (
  id           BIGSERIAL PRIMARY KEY,
  policy_id    BIGINT      NOT NULL REFERENCES coupon_policies(id),
  target_type  VARCHAR(20) NOT NULL,   -- CATEGORY | COURSE | INSTRUCTOR
  target_id    BIGINT      NOT NULL,
  is_exclusion BOOLEAN     NOT NULL DEFAULT false,
  UNIQUE (policy_id, target_type, target_id, is_exclusion)
);

-- 쿠폰 코드
CREATE TABLE coupon_codes (
  id         BIGSERIAL PRIMARY KEY,
  policy_id  BIGINT      NOT NULL REFERENCES coupon_policies(id),
  code       VARCHAR(32) NOT NULL,
  is_public  BOOLEAN     NOT NULL,     -- true: 공용 재사용 코드
  claimed_by BIGINT,                   -- UNIQUE 코드 소유자
  claimed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (code)                        -- 코드는 전역 유일
);
CREATE INDEX idx_coupon_codes_policy ON coupon_codes(policy_id);

-- 보유 쿠폰 : 사용/만료의 단위
CREATE TABLE user_coupons (
  id             BIGSERIAL   PRIMARY KEY,
  policy_id      BIGINT      NOT NULL REFERENCES coupon_policies(id),
  code_id        BIGINT      REFERENCES coupon_codes(id),
  user_id        BIGINT      NOT NULL,
  status         VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE', -- AVAILABLE|USED|EXPIRED|REVOKED
  valid_from     TIMESTAMPTZ NOT NULL,
  valid_until    TIMESTAMPTZ NOT NULL,
  issued_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  used_at        TIMESTAMPTZ,
  order_id       BIGINT,
  revert_count   SMALLINT    NOT NULL DEFAULT 0,
  version        INT         NOT NULL DEFAULT 0,
  CONSTRAINT chk_used_has_order
    CHECK (status <> 'USED' OR order_id IS NOT NULL)
);
CREATE INDEX idx_user_coupons_lookup
  ON user_coupons(user_id, status, valid_until);
-- 1인 1매 정책의 중복 발급 차단 (per_user_limit = 1 인 정책)
CREATE UNIQUE INDEX uq_user_coupon_single
  ON user_coupons(policy_id, user_id)
  WHERE status <> 'REVOKED';

-- 사용 이력 : 중복 사용 방지의 최종 방어선
CREATE TABLE coupon_redemptions (
  id              BIGSERIAL   PRIMARY KEY,
  user_coupon_id  BIGINT      NOT NULL REFERENCES user_coupons(id),
  order_id        BIGINT      NOT NULL,
  user_id         BIGINT      NOT NULL,
  order_amount    INT         NOT NULL,   -- 할인 전
  discount_amount INT         NOT NULL,
  final_amount    INT         NOT NULL,   -- 실제 결제
  redeemed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  reverted_at     TIMESTAMPTZ,
  revert_reason   VARCHAR(200),
  CONSTRAINT uq_redemption_per_coupon UNIQUE (user_coupon_id), -- ★ 중복 사용 물리 차단
  CONSTRAINT uq_redemption_per_order  UNIQUE (order_id),       -- ★ 주문당 1쿠폰 (스태킹 금지)
  CONSTRAINT chk_amounts
    CHECK (discount_amount >= 0
           AND final_amount = order_amount - discount_amount
           AND final_amount >= 0)
);

-- 관리자 감사 로그
CREATE TABLE coupon_audit_logs (
  id         BIGSERIAL   PRIMARY KEY,
  actor_id   BIGINT      NOT NULL,
  action     VARCHAR(50) NOT NULL,   -- CREATE_POLICY | UPDATE_POLICY | REVOKE | GRANT ...
  target_type VARCHAR(30) NOT NULL,
  target_id  BIGINT      NOT NULL,
  payload    JSONB,
  reason     VARCHAR(500),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

> `uq_redemption_per_coupon`이 이 기능 전체의 정합성을 떠받친다. 어떤 리팩터링에서도 이 제약을 제거해서는 안 된다.

---

## 7. 처리 흐름

### 7.1 결제 확정 시퀀스 (중복 사용 방지 핵심)

```
사용자          API 서버                    DB                        PG
  │                │                        │                         │
  │─ 결제요청 ────▶│                        │                         │
  │  (couponId,    │                        │                         │
  │   Idem-Key)    │                        │                         │
  │                │─ 멱등키 조회 ─────────▶│                         │
  │                │  (이미 처리? → 기존 결과 반환)                    │
  │                │                        │                         │
  │                │─ [TX1] 시작 ──────────▶│                         │
  │                │  주문 PENDING 생성      │                         │
  │                │  쿠폰 V1~V9 검증        │                         │
  │                │  금액 서버 재계산       │                         │
  │                │─ [TX1] 커밋 ──────────▶│                         │
  │                │                        │                         │
  │                │─ 결제 승인 요청 ───────────────────────────────▶│
  │                │◀─ 승인 성공 ───────────────────────────────────│
  │                │                        │                         │
  │                │─ [TX2] 시작 ──────────▶│                         │
  │                │  ① UPDATE user_coupons SET status='USED'         │
  │                │     WHERE id=? AND status='AVAILABLE'            │
  │                │     AND valid_until > now()                      │
  │                │     → 영향 행 0 이면 ROLLBACK + PG 결제 취소      │
  │                │  ② INSERT coupon_redemptions (UNIQUE 위반 시 중단)│
  │                │  ③ 주문 PAID 전이, 수강권 부여                    │
  │                │─ [TX2] 커밋 ──────────▶│                         │
  │◀─ 완료 ────────│                        │                         │
```

**설계 근거**
- 쿠폰 소진을 PG 승인 **이후**에 두어, 결제 실패 시 쿠폰이 잠기는 문제를 없앤다.
- TX2에서 쿠폰 소진에 실패하면(= 그 찰나에 다른 요청이 먼저 소진) 전체를 롤백하고 **PG 결제를 즉시 취소**한 뒤 사용자에게 재시도를 안내한다. 이 경우는 동일 사용자의 동시 요청에서만 발생하며, `Idempotency-Key`가 대부분을 먼저 걸러낸다.
- TX2 실패 후 PG 취소마저 실패하면 `payment_reconciliation_queue`에 적재하고 알림을 발송한다. 미처리 건은 운영 대시보드에 노출된다.

### 7.2 쿠폰 등록(코드 입력) 흐름

1. 코드 정규화 (대문자 변환, 공백·하이픈 제거)
2. Rate limit 확인 (FR-U5)
3. `coupon_codes`에서 코드 조회 → 없으면 `CODE_NOT_FOUND`
4. 정책 상태·기간·대상 회원 조건 검증
5. `UNIQUE` 코드면 `claimed_by IS NULL` 조건부 UPDATE로 선점
6. 발행 한도 원자적 증가 (FR-C5) → 실패 시 5번 롤백
7. `user_coupons` INSERT (`valid_from`/`valid_until` 계산은 FR-E1)
8. 성공 응답에 쿠폰 상세와 만료일을 포함

---

## 8. API 설계

### 8.1 수강생 API

| Method | Path | 설명 |
| --- | --- | --- |
| `GET` | `/api/v1/me/coupons?status=available` | 보유 쿠폰 목록 |
| `POST` | `/api/v1/me/coupons` | 코드로 쿠폰 등록 `{ code }` |
| `GET` | `/api/v1/orders/{orderId}/applicable-coupons` | 해당 주문에 적용 가능/불가 쿠폰과 예상 할인액 |
| `POST` | `/api/v1/orders/{orderId}/coupon` | 쿠폰 선택(가결제 금액 계산) `{ userCouponId }` |
| `DELETE` | `/api/v1/orders/{orderId}/coupon` | 쿠폰 선택 해제 |
| `POST` | `/api/v1/payments` | 결제 확정. `Idempotency-Key` 헤더 필수 |

**`GET /orders/{orderId}/applicable-coupons` 응답 예시**

```json
{
  "orderAmount": 100000,
  "applicable": [
    {
      "userCouponId": 8812,
      "displayName": "여름방학 20% 할인",
      "discountType": "PERCENTAGE",
      "discountValue": 20,
      "expectedDiscount": 20000,
      "finalAmount": 80000,
      "validUntil": "2026-08-31T14:59:59Z"
    }
  ],
  "notApplicable": [
    {
      "userCouponId": 8790,
      "displayName": "백엔드 카테고리 1만원 할인",
      "reasonCode": "COUPON_NOT_APPLICABLE",
      "reasonMessage": "이 강의에는 사용할 수 없는 쿠폰입니다."
    }
  ]
}
```

**에러 응답 형식**

```json
{
  "errorCode": "COUPON_EXPIRED",
  "message": "선택하신 쿠폰의 유효기간이 만료되었습니다.",
  "field": "userCouponId"
}
```

### 8.2 관리자 API

| Method | Path | 설명 |
| --- | --- | --- |
| `POST` | `/api/v1/admin/coupon-policies` | 정책 생성 |
| `GET` | `/api/v1/admin/coupon-policies` | 정책 목록·검색 |
| `PATCH` | `/api/v1/admin/coupon-policies/{id}` | 정책 수정 (FR-A4 제약) |
| `POST` | `/api/v1/admin/coupon-policies/{id}/codes` | UNIQUE 코드 대량 생성 |
| `GET` | `/api/v1/admin/coupon-policies/{id}/codes/export` | 코드 CSV 다운로드 |
| `POST` | `/api/v1/admin/coupon-policies/{id}/grant` | 지정 회원에게 직접 지급 |
| `POST` | `/api/v1/admin/coupon-policies/{id}/terminate` | 정책 중단 + 미사용 쿠폰 회수 |
| `POST` | `/api/v1/admin/user-coupons/{id}/revoke` | 개별 회수 |
| `GET` | `/api/v1/admin/coupon-policies/{id}/stats` | 통계 |

---

## 9. 엣지 케이스

| # | 상황 | 처리 |
| --- | --- | --- |
| EC-1 | 결제 버튼 더블클릭 | `Idempotency-Key`로 두 번째 요청은 첫 결과 반환 |
| EC-2 | 두 기기에서 동시에 같은 쿠폰으로 다른 강의 결제 | 조건부 UPDATE에서 하나만 성공, 다른 쪽은 PG 취소 후 실패 응답 |
| EC-3 | 결제 페이지 진입 후 쿠폰 만료 | V3로 차단, 결제 페이지 복귀 (FR-E4) |
| EC-4 | 쿠폰 선택 후 관리자가 정책 중단 | V4로 차단, "종료된 프로모션입니다" 안내 |
| EC-5 | 할인 후 금액 0원 | PG 호출 없이 0원 결제로 주문 완료 (FR-P5) |
| EC-6 | 정액 쿠폰 > 주문 금액 | 할인액을 주문 금액으로 절삭, 잔액 이월 없음 |
| EC-7 | 정률 쿠폰 계산 시 소수점 | 원 단위 절사(floor) — 사용자에게 불리하지 않은 방향으로 반올림하지 않고 플랫폼 손실을 감수하는 절사 채택 |
| EC-8 | 다중 상품 중 일부만 쿠폰 대상 | 대상 강의 금액 기준으로만 할인 계산 |
| EC-9 | 이미 수강 중인 강의 재결제 | V9로 차단 (쿠폰 무관하게 결제 자체를 막음) |
| EC-10 | 전액 환불 후 기간 남음 | 쿠폰 `AVAILABLE` 복원 (FR-R2) |
| EC-11 | 전액 환불 후 기간 지남 | `EXPIRED` 전이, 복원 없음 |
| EC-12 | 부분 환불 | 쿠폰 복원 없음, 환불 화면에 고지 (FR-R3) |
| EC-13 | 환불·재사용 반복 어뷰징 | 복원 3회 초과 시 자동 `REVOKED` (FR-R4) |
| EC-14 | 무작위 코드 대입 | Rate limit + 12자리 난수 코드 (FR-U5, FR-A3) |
| EC-15 | 발행 한도 근처 동시 등록 | 원자적 `issued_count` 증가로 초과 발급 차단 (FR-C5) |
| EC-16 | 회원 탈퇴 | 보유 쿠폰 전량 `REVOKED`, 사용 이력은 정산 목적으로 보존 |
| EC-17 | PG 웹훅 중복 수신 | 멱등 처리, 쿠폰 재소진 없음 |
| EC-18 | TX2 롤백 후 PG 취소 실패 | 정산 큐 적재 + 즉시 알림 (§7.1) |

---

## 10. 비기능 요구사항

**성능**
- 적용 가능 쿠폰 조회 p95 < 200ms (보유 쿠폰 100장 기준)
- 결제 확정 시 쿠폰 검증 오버헤드 < 50ms
- 정책 상세는 캐시하되, `user_coupons` 상태는 **캐시하지 않는다.** (stale 상태로 중복 사용이 통과하는 것을 방지)

**동시성**
- 동일 쿠폰 100 동시 요청 부하 테스트에서 성공 1건 / 실패 99건이어야 한다. 이 테스트는 CI 회귀 스위트에 포함한다.

**보안**
- 쿠폰 코드는 예측 불가한 난수. 순차 증가 코드 금지.
- 모든 검증은 서버에서 수행. 클라이언트 계산 금액 불신 (FR-P6).
- 타인의 `userCouponId`로 요청 시 V1에서 차단하되, 응답은 "사용할 수 없는 쿠폰"으로 통일해 소유 여부를 노출하지 않는다.

**관측성**
- 구조화 로그: `couponId`, `policyId`, `userId`, `orderId`, `resultCode`.
- 알림: 쿠폰 소진 실패율 1% 초과, TX2 롤백 발생, 정산 큐 적체.
- 대시보드: 정책별 사용 추이, 실패 사유별 분포.

**데이터**
- 사용 이력은 최소 5년 보관 (세금·정산 목적).
- `user_coupons`는 만료 후 1년 경과 시 아카이브 테이블로 이관.

---

## 11. 분석 이벤트

| 이벤트 | 속성 |
| --- | --- |
| `coupon_registered` | policyId, codeType, source |
| `coupon_list_viewed` | orderId, applicableCount, notApplicableCount |
| `coupon_selected` | userCouponId, policyId, expectedDiscount |
| `coupon_deselected` | userCouponId, reason |
| `coupon_redeemed` | userCouponId, orderId, discountAmount, finalAmount |
| `coupon_redemption_failed` | userCouponId, errorCode |
| `coupon_expired_unused` | policyId, userId, issuedAt |

---

## 12. 릴리스 계획

| 단계 | 범위 | 기간 |
| --- | --- | --- |
| **M1. 도메인 기반** | 스키마, 정책 CRUD, 코드 생성, 할인 계산 엔진 + 단위 테스트 | W1–W2 |
| **M2. 결제 연동** | 검증 규칙, 원자적 소진, 멱등성, 동시성 부하 테스트 | W3–W4 |
| **M3. 사용자 UI** | 쿠폰함, 코드 등록, 결제 화면 적용 | W4–W5 |
| **M4. 관리자 UI** | 정책 발행 화면, 대시보드, 회수, 감사 로그 | W5–W6 |
| **M5. 운영 준비** | 환불 연동, 만료 배치, 알림, 모니터링, 내부 QA | W6–W7 |
| **M6. 점진 출시** | 내부 테스트 캠페인 → 소규모 실제 캠페인 → 전체 오픈 | W8 |

**출시 게이트 (전부 충족해야 전체 오픈)**
- [ ] 동시성 테스트: 동일 쿠폰 100 동시 요청 → 성공 정확히 1건
- [ ] 멱등성 테스트: 동일 키 10회 요청 → 소진 1회, 결제 1건
- [ ] 만료 경계 테스트: `valid_until` 전후 1초 시점 동작 검증
- [ ] 환불 시나리오 4종(전액/부분/기간내/기간외) 통과
- [ ] 금액 계산 회귀 테스트 (절사, cap, 0원, 초과 정액)
- [ ] 감사 로그가 모든 관리자 액션을 기록

---

## 13. 가정 및 열린 질문

**가정 (다르면 알려주면 반영)**
- A1. 통화는 KRW 단일, 최소 단위는 1원.
- A2. 관계형 DB(PostgreSQL 가정)를 사용하며 트랜잭션을 쓸 수 있다.
- A3. 외부 PG를 통해 결제하며 결제 취소 API가 있다.
- A4. 강의는 단건 구매 모델이며 구독은 이번 범위 밖이다.
- A5. 할인 부담은 전액 플랫폼이며 강사 정산은 정가 기준이다 (FR-R5).

**열린 질문**
| # | 질문 | 결정 필요 시점 |
| --- | --- | --- |
| Q1 | 쿠폰 스태킹을 v2에 정말 넣을 것인가? 넣는다면 우선순위·조합 규칙은? | M6 이후 |
| Q2 | 강사 부담 쿠폰(강사 정산에서 차감)을 지원할 것인가? | M4 이전 |
| Q3 | 부분 환불 시 쿠폰 미복원(FR-R3)이 CS 부담으로 이어질 가능성은? | M5 |
| Q4 | 장바구니(다중 강의) 결제가 실제로 존재하는가? 없다면 EC-8·FR-R3이 단순해진다 | **M1 이전** |
| Q5 | 만료 임박 알림 채널(푸시/이메일/둘 다)과 발송 시점 | M5 |
| Q6 | 쿠폰 코드 노출 경로(이메일·SNS·제휴사 API)에 따라 코드 유형 기본값이 달라짐 | M2 |
