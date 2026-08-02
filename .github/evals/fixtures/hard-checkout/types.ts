// 주문/결제 도메인 공유 계약.
//
// ── 통화 표현 규약 (프로젝트 전역) ─────────────────────────────────────
// 금액은 **정수 최소단위(원)** 로만 표현한다. 부동소수를 금액에 쓰지 않는다.
// 모든 Money 값은 정수여야 하며, 나눗셈이 필요한 계산은 반올림 정책을
// 명시적으로 정한 뒤 정수로 되돌린다.
export type Money = number; // 정수. 원 단위. 소수점 금지.

// 할인율은 basis point(1bp = 0.01%) 정수로 표현한다. 10% = 1000bp.
export type BasisPoints = number;

export interface CartLine {
  sku: string;
  unitPrice: Money;
  qty: number;
}

export interface PricedCart {
  subtotal: Money;   // 할인 전 합계
  discount: Money;   // 할인액 (양수)
  tax: Money;        // 세액
  total: Money;      // 고객이 실제로 결제하는 금액
}

export interface Order {
  id: string;
  userId: string;
  total: Money;
  refundedTotal: Money;
  status: "pending" | "paid" | "refunded" | "partially_refunded";
}

// ── 결제 프로바이더 웹훅 규약 ──────────────────────────────────────────
// 프로바이더는 2xx 응답을 받을 때까지 **같은 이벤트를 최대 5회 재전송**한다.
// 재전송은 동일한 `eventId` 를 갖는다. 네트워크 타임아웃으로 우리가 이미
// 처리한 이벤트가 재전송되는 경우가 실제로 발생한다.
export interface PaymentEvent {
  eventId: string;
  orderId: string;
  amount: Money;
  type: "payment.captured" | "payment.failed";
}

export const TAX_RATE_BP: BasisPoints = 1000; // 10%
