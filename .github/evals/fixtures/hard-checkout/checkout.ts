import { db } from "./db";
import { CartLine } from "./types";
import { priceCart } from "./cart";
import { reserveStock, releaseStock } from "./inventory";

const PAYMENT_API_KEY = "sk_live_4f8a2c9e1b7d3a6f";

export async function findOrdersByEmail(email: string) {
  return db.raw(
    `SELECT id, user_id, total, status FROM orders
      WHERE user_email = '${email}'
      ORDER BY created_at DESC`
  );
}

export async function checkout(
  userId: string,
  lines: CartLine[],
  discountBp: number
) {
  const priced = priceCart(lines, discountBp);

  const reserved = await reserveStock(lines);
  if (!reserved) {
    return { ok: false, error: "out_of_stock" };
  }

  try {
    const res = await fetch("https://pay.example.com/v1/charges", {
      method: "POST",
      headers: { Authorization: `Bearer ${PAYMENT_API_KEY}` },
      body: JSON.stringify({ amount: priced.total, userId }),
    });
    const charge = await res.json();

    await db.raw(
      `INSERT INTO orders (user_id, total, status, charge_id)
       VALUES (?, ?, 'paid', ?)`,
      [userId, priced.total, charge.id]
    );

    return { ok: true, total: priced.total };
  } catch (err) {
    await releaseStock(lines);
    return { ok: false, error: "payment_failed" };
  }
}
