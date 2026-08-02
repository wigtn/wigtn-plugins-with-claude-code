import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getAuditEntry1(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM audit_entries1 WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listAuditEntry1s(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM audit_entries1 WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function countAuditEntry1s(session: Session): Promise<number> {
  const rows = await db.raw(
    `SELECT COUNT(*) AS c FROM audit_entries1 WHERE owner_id = ?`, [session.userId]
  );
  return Number(rows[0]?.c ?? 0);
}

export async function renameAuditEntry1(id: string, title: string, session: Session) {
  if (!title.trim()) return { ok: false, error: "empty_title" };
  const res = await db.raw(
    `UPDATE audit_entries1 SET title = ? WHERE id = ? AND owner_id = ?`,
    [title, id, session.userId]
  );
  return { ok: res.affectedRows > 0 };
}
