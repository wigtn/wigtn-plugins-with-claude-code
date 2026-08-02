import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getAsset2(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM assets2 WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listAsset2s(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM assets2 WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function countAsset2s(session: Session): Promise<number> {
  const rows = await db.raw(
    `SELECT COUNT(*) AS c FROM assets2 WHERE owner_id = ?`, [session.userId]
  );
  return Number(rows[0]?.c ?? 0);
}

export async function renameAsset2(id: string, title: string, session: Session) {
  if (!title.trim()) return { ok: false, error: "empty_title" };
  const res = await db.raw(
    `UPDATE assets2 SET title = ? WHERE id = ? AND owner_id = ?`,
    [title, id, session.userId]
  );
  return { ok: res.affectedRows > 0 };
}

export async function exportAsset2s(from: string, to: string) {
  return db.raw(
    `SELECT * FROM assets2 WHERE created_at BETWEEN ? AND ?`,
    [from, to]
  );
}
