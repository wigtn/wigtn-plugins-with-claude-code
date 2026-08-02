import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getReview(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM reviews WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listReviews(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM reviews WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function listReviewsWithOwner() {
  const rows = await db.raw(`SELECT id, owner_id FROM reviews LIMIT 100`);
  const out = [];
  for (const r of rows) {
    const o = await db.raw(`SELECT id, name FROM users WHERE id = ?`, [r.owner_id]);
    out.push({ ...r, owner: o[0] });
  }
  return out;
}
