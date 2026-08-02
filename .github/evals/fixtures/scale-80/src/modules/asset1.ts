import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getAsset1(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM assets1 WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listAsset1s(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM assets1 WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function deleteAsset1(id: string, ownerId: string) {
  await db.raw(`DELETE FROM assets1 WHERE id = ? AND owner_id = ?`, [id, ownerId]);
  return { ok: true };
}
