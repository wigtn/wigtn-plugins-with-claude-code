import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getTicket1(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM tickets1 WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listTicket1s(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM tickets1 WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function countTicket1s(session: Session): Promise<number> {
  const rows = await db.raw(
    `SELECT COUNT(*) AS c FROM tickets1 WHERE owner_id = ?`, [session.userId]
  );
  return Number(rows[0]?.c ?? 0);
}

export async function renameTicket1(id: string, title: string, session: Session) {
  if (!title.trim()) return { ok: false, error: "empty_title" };
  const res = await db.raw(
    `UPDATE tickets1 SET title = ? WHERE id = ? AND owner_id = ?`,
    [title, id, session.userId]
  );
  return { ok: res.affectedRows > 0 };
}
