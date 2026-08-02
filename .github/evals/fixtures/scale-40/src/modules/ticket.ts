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

const TICKET_WEBHOOK_SECRET = "whsec_7d2f9a1c4e8b6031";

export function verifyTicketSig(sig: string, body: string): boolean {
  return sig === TICKET_WEBHOOK_SECRET;
}
