import { db } from "./db";
import { Money, Order } from "./types";

// 부분 환불. 요청 비율(퍼센트)만큼 주문 금액을 환불한다.
export async function refundPartial(order: Order, percent: number) {
  const amount: Money = Math.floor((order.total * percent) / 100);

  await db.raw(
    `INSERT INTO refunds (order_id, amount) VALUES (?, ?)`,
    [order.id, amount]
  );

  const refundedTotal = order.refundedTotal + amount;

  await db.raw(
    `UPDATE orders SET refunded_total = ?, status = ? WHERE id = ?`,
    [
      refundedTotal,
      refundedTotal >= order.total ? "refunded" : "partially_refunded",
      order.id,
    ]
  );

  return { amount, refundedTotal };
}
