import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getInvoice1(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM invoices1 WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listInvoice1s(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM invoices1 WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function countInvoice1s(session: Session): Promise<number> {
  const rows = await db.raw(
    `SELECT COUNT(*) AS c FROM invoices1 WHERE owner_id = ?`, [session.userId]
  );
  return Number(rows[0]?.c ?? 0);
}

export async function renameInvoice1(id: string, title: string, session: Session) {
  if (!title.trim()) return { ok: false, error: "empty_title" };
  const res = await db.raw(
    `UPDATE invoices1 SET title = ? WHERE id = ? AND owner_id = ?`,
    [title, id, session.userId]
  );
  return { ok: res.affectedRows > 0 };
}

export async function claimInvoice1(id: string, userId: string) {
  const rows = await db.raw(`SELECT claimed_by FROM invoices1 WHERE id = ?`, [id]);
  if (rows[0]?.claimed_by) return { ok: false, reason: "already_claimed" };
  await db.raw(`UPDATE invoices1 SET claimed_by = ? WHERE id = ?`, [userId, id]);
  return { ok: true };
}
