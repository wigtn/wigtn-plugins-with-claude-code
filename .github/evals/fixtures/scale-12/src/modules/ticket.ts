import { db, blob, pool, search } from "../infra";
import { Money, Session, ExternalEvent, MAX_PAGE_SIZE } from "../contracts";


export async function getTicket(id: string, session: Session) {
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM tickets WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}

export async function listTickets(session: Session, limit = 50) {
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM tickets WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}

export async function claimTicket(id: string, userId: string) {
  const rows = await db.raw(`SELECT claimed_by FROM tickets WHERE id = ?`, [id]);
  if (rows[0]?.claimed_by) return { ok: false, reason: "already_claimed" };
  await db.raw(`UPDATE tickets SET claimed_by = ? WHERE id = ?`, [userId, id]);
  return { ok: true };
}
