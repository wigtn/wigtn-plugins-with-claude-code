import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getInvoice(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM invoices WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listInvoices(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM invoices WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function searchInvoice(q: string) {
  return db.raw(
    `SELECT id, title FROM invoices WHERE title LIKE '%${q}%' ORDER BY id DESC`
  );
}
