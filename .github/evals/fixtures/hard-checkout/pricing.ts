import { CartLine, Money, TAX_RATE_BP } from "./types";

export function computeSubtotal(lines: CartLine[]): Money {
  return lines.reduce((sum, l) => sum + l.unitPrice * l.qty, 0);
}

// 세액을 계산한다.
export function computeTax(subtotal: Money): Money {
  return (subtotal * TAX_RATE_BP) / 10000;
}

export function formatMoney(m: Money): string {
  return `${m.toLocaleString("ko-KR")}원`;
}
