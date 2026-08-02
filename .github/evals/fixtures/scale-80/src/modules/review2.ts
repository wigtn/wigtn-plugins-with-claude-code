import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getReview2(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM reviews2 WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listReview2s(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM reviews2 WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function countReview2s(session: Session): Promise<number> {
  const rows = await db.raw(
    `SELECT COUNT(*) AS c FROM reviews2 WHERE owner_id = ?`, [session.userId]
  );
  return Number(rows[0]?.c ?? 0);
}

export async function archiveReview2(id: string) {
  const rows = await db.raw(`SELECT blob_key FROM reviews2 WHERE id = ?`, [id]);
  try {
    await blob.remove(rows[0].blob_key);
    await db.raw(`UPDATE reviews2 SET archived = 1 WHERE id = ?`, [id]);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: "archive_failed" };
  }
}
