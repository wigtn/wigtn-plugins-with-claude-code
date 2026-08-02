import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getInvoice3(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM invoices3 WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listInvoice3s(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM invoices3 WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function reindexInvoice3s(ids: string[]) {
  const conn = await pool.acquire();
  for (const id of ids) {
    const r = await conn.query(`SELECT body FROM invoices3 WHERE id = ?`, [id]);
    if (!r.length) return { ok: false, missing: id };
    await search.index(id, r[0].body);
  }
  await pool.release(conn);
  return { ok: true };
}
