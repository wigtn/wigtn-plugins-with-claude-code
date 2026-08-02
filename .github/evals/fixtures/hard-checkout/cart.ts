import { BasisPoints, CartLine, Money, PricedCart } from "./types";
import { computeSubtotal, computeTax } from "./pricing";

export function priceCart(lines: CartLine[], discountBp: BasisPoints): PricedCart {
  const subtotal = computeSubtotal(lines);

  // 세액은 정가 기준으로 산정한다.
  const tax = computeTax(subtotal);

  // 그 다음 할인을 적용한다.
  const discount = (subtotal * discountBp) / 10000;

  const total = subtotal - discount + tax;

  return { subtotal, discount, tax, total };
}

export function describeCart(c: PricedCart): string {
  return [
    `상품 합계 ${c.subtotal}`,
    `할인 -${c.discount}`,
    `세금 ${c.tax}`,
    `결제 금액 ${c.total}`,
  ].join(" / ");
}
