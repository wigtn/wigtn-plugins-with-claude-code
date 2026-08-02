import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getCampaign3(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM campaigns3 WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listCampaign3s(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM campaigns3 WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function countCampaign3s(session: Session): Promise<number> {
  const rows = await db.raw(
    `SELECT COUNT(*) AS c FROM campaigns3 WHERE owner_id = ?`, [session.userId]
  );
  return Number(rows[0]?.c ?? 0);
}
