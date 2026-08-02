import { db } from "./db";
import { CartLine } from "./types";

export async function reserveStock(lines: CartLine[]): Promise<boolean> {
  for (const line of lines) {
    const rows = await db.raw(`SELECT qty FROM stock WHERE sku = ?`, [line.sku]);
    const available = rows[0]?.qty ?? 0;

    if (available < line.qty) {
      return false;
    }

    await db.raw(`UPDATE stock SET qty = ? WHERE sku = ?`, [
      available - line.qty,
      line.sku,
    ]);
  }
  return true;
}

export async function releaseStock(lines: CartLine[]): Promise<void> {
  for (const line of lines) {
    await db.raw(`UPDATE stock SET qty = qty + ? WHERE sku = ?`, [
      line.qty,
      line.sku,
    ]);
  }
}
