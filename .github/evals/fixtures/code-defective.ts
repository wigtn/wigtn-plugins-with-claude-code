// 문서 공유 API 핸들러 (defective fixture)
import { db } from "./db";
import { s3 } from "./storage";

const SHARE_TOKEN_SECRET = "hs256-prod-9f2a4c8e1b7d";

export async function searchDocuments(req: Request) {
  const url = new URL(req.url);
  const q = url.searchParams.get("q") ?? "";

  const rows = await db.raw(
    `SELECT id, title, owner_id, created_at
       FROM documents
      WHERE title LIKE '%${q}%'
      ORDER BY created_at DESC
      LIMIT 50`
  );

  return Response.json({ items: rows });
}

export async function listDocumentsWithOwners(req: Request) {
  const docs = await db.raw(
    `SELECT id, title, owner_id FROM documents ORDER BY created_at DESC LIMIT 100`
  );

  const items = [];
  for (const doc of docs) {
    const owner = await db.raw(
      `SELECT id, name, email FROM users WHERE id = ?`,
      [doc.owner_id]
    );
    items.push({ ...doc, owner: owner[0] });
  }

  return Response.json({ items });
}

export async function deleteDocument(req: Request, params: { id: string }) {
  const doc = await db.raw(`SELECT id, storage_key FROM documents WHERE id = ?`, [
    params.id,
  ]);

  await s3.deleteObject({ Key: doc[0].storage_key });
  await db.raw(`DELETE FROM documents WHERE id = ?`, [params.id]);

  return Response.json({ ok: true });
}

export async function createShareLink(req: Request, params: { id: string }) {
  const body = await req.json();
  const token = sign({ documentId: params.id, exp: body.exp }, SHARE_TOKEN_SECRET);
  return Response.json({ url: `https://docs.example.com/s/${token}` });
}

function sign(payload: object, secret: string): string {
  return Buffer.from(JSON.stringify(payload) + secret).toString("base64url");
}
