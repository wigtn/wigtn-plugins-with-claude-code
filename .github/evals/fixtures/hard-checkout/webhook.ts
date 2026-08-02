import { db } from "./db";
import { PaymentEvent } from "./types";

export async function handlePaymentWebhook(evt: PaymentEvent) {
  if (evt.type === "payment.captured") {
    await db.raw(
      `UPDATE orders SET status = 'paid' WHERE id = ?`,
      [evt.orderId]
    );
    await db.raw(
      `INSERT INTO ledger (order_id, amount, kind) VALUES (?, ?, 'capture')`,
      [evt.orderId, evt.amount]
    );
  }

  if (evt.type === "payment.failed") {
    await db.raw(`UPDATE orders SET status = 'pending' WHERE id = ?`, [
      evt.orderId,
    ]);
  }

  return { received: true };
}
