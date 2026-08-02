import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getWarehouse3(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM warehouses3 WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listWarehouse3s(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM warehouses3 WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function countWarehouse3s(session: Session): Promise<number> {
  const rows = await db.raw(
    `SELECT COUNT(*) AS c FROM warehouses3 WHERE owner_id = ?`, [session.userId]
  );
  return Number(rows[0]?.c ?? 0);
}

export async function renameWarehouse3(id: string, title: string, session: Session) {
  if (!title.trim()) return { ok: false, error: "empty_title" };
  const res = await db.raw(
    `UPDATE warehouses3 SET title = ? WHERE id = ? AND owner_id = ?`,
    [title, id, session.userId]
  );
  return { ok: res.affectedRows > 0 };
}
