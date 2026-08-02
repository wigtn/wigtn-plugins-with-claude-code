import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getContract(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM contracts_tbl WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listContracts(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM contracts_tbl WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function countContracts(session: Session): Promise<number> {
  const rows = await db.raw(
    `SELECT COUNT(*) AS c FROM contracts_tbl WHERE owner_id = ?`, [session.userId]
  );
  return Number(rows[0]?.c ?? 0);
}

export function contractTotal(base: Money, discountBp: number, taxBp: number): Money {
  const tax = (base * taxBp) / 10000;
  const discount = (base * discountBp) / 10000;
  return base - discount + tax;
}
