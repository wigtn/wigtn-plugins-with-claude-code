// 문서 공유 API 핸들러 (clean fixture)
import { createHmac, timingSafeEqual } from "node:crypto";
import { db } from "./db";
import { s3 } from "./storage";
import { requireSession, type Session } from "./auth";

const SHARE_TOKEN_SECRET = process.env.SHARE_TOKEN_SECRET;
if (!SHARE_TOKEN_SECRET) {
  throw new Error("SHARE_TOKEN_SECRET is not configured");
}

const SHARE_TTL_MS = 7 * 24 * 60 * 60 * 1000;

export async function searchDocuments(req: Request) {
  const session = await requireSession(req);
  const q = new URL(req.url).searchParams.get("q") ?? "";
  // LIKE 메타문자를 이스케이프한다. 바인딩이라 인젝션은 아니지만,
  // 이스케이프하지 않으면 q="%" 가 전체 매칭이 되어 검색 의미가 달라진다.
  const pattern = `%${q.replace(/[\\%_]/g, (c) => `\\${c}`)}%`;

  const rows = await db.raw(
    `SELECT id, title, owner_id, created_at
       FROM documents
      WHERE owner_id = ? AND title LIKE ? ESCAPE '\\'
      ORDER BY created_at DESC
      LIMIT 50`,
    [session.userId, pattern]
  );

  return Response.json({ items: rows });
}

export async function listDocumentsWithOwners(req: Request) {
  const session = await requireSession(req);

  const items = await db.raw(
    `SELECT d.id, d.title, d.owner_id, u.name AS owner_name, u.email AS owner_email
       FROM documents d
       JOIN users u ON u.id = d.owner_id
      WHERE d.owner_id = ? OR ? = 'admin'
      ORDER BY d.created_at DESC
      LIMIT 100`,
    [session.userId, session.role]
  );

  return Response.json({ items });
}

export async function deleteDocument(req: Request, params: { id: string }) {
  const session = await requireSession(req);

  const rows = await db.raw(
    `SELECT id, owner_id, storage_key FROM documents WHERE id = ?`,
    [params.id]
  );
  const doc = rows[0];
  if (!doc) {
    return Response.json({ error: "not_found" }, { status: 404 });
  }
  if (doc.owner_id !== session.userId && session.role !== "admin") {
    return Response.json({ error: "forbidden" }, { status: 403 });
  }

  // 순서가 중요하다: DB 행 삭제와 감사 로그를 한 트랜잭션으로 먼저 커밋하고,
  // 되돌릴 수 없는 스토리지 삭제는 그 뒤에 한다. 반대로 하면 DELETE 실패 시
  // 본문만 사라진 좀비 행이 남는다(복구 불가). 이 순서에서 남을 수 있는 것은
  // 고아 객체뿐이고, 그건 reaper가 정리할 수 있다.
  try {
    await db.transaction(async (tx) => {
      await tx.raw(`DELETE FROM documents WHERE id = ?`, [params.id]);
      await tx.raw(
        `INSERT INTO audit_log (actor_id, action, target_id) VALUES (?, 'document.delete', ?)`,
        [session.userId, params.id]
      );
    });
  } catch (err) {
    console.error("document delete failed", { id: params.id, err });
    return Response.json({ error: "delete_failed" }, { status: 500 });
  }

  try {
    await s3.deleteObject({ Key: doc.storage_key });
  } catch (err) {
    // 삭제는 이미 확정됐다. 고아 객체는 reaper가 수거하므로 500을 내지 않는다.
    console.error("storage cleanup deferred", { key: doc.storage_key, err });
  }

  return Response.json({ ok: true });
}

export async function createShareLink(req: Request, params: { id: string }) {
  const session = await requireSession(req);

  const rows = await db.raw(`SELECT owner_id FROM documents WHERE id = ?`, [
    params.id,
  ]);
  if (!rows[0]) {
    return Response.json({ error: "not_found" }, { status: 404 });
  }
  if (rows[0].owner_id !== session.userId) {
    return Response.json({ error: "forbidden" }, { status: 403 });
  }

  const exp = Date.now() + SHARE_TTL_MS;
  const token = sign(params.id, exp);
  return Response.json({ url: `https://docs.example.com/s/${token}`, exp });
}

function sign(documentId: string, exp: number): string {
  const payload = Buffer.from(JSON.stringify({ documentId, exp })).toString(
    "base64url"
  );
  const mac = createHmac("sha256", SHARE_TOKEN_SECRET!)
    .update(payload)
    .digest("base64url");
  return `${payload}.${mac}`;
}

export function verifyShareToken(token: string): { documentId: string } | null {
  const [payload, mac] = token.split(".");
  if (!payload || !mac) return null;

  const expected = createHmac("sha256", SHARE_TOKEN_SECRET!)
    .update(payload)
    .digest("base64url");
  const a = Buffer.from(mac);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !timingSafeEqual(a, b)) return null;

  const claims = JSON.parse(Buffer.from(payload, "base64url").toString());
  if (claims.exp < Date.now()) return null;
  return { documentId: claims.documentId };
}
