#!/usr/bin/env python3
"""규모 실험용 코드베이스 생성기.

왜 생성기인가: 손으로 80개 파일을 쓰면 재현이 안 되고, 규모를 바꿔가며
같은 결함 세트를 유지할 수 없다. 이 실험의 독립변수는 **규모 하나**이므로
나머지는 전부 고정되어야 한다.

사용:
    python3 .github/evals/gen_scale.py 40 fixtures/scale-40

출력:
    <out>/            생성된 코드베이스 (contracts.ts + N개 모듈)
    <out>/../labels-scale-<N>.json   심어둔 결함 라벨 (score.py 형식)

결함은 항상 같은 12종이고, 규모가 커질수록 **깨끗한 필러 모듈만** 늘어난다.
즉 신호는 고정, 잡음만 증가 — 검출률 하락은 순수하게 규모 탓이다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ── 도메인 어휘 (모듈마다 다르게 보이도록) ────────────────────────────────
DOMAINS = [
    ("invoice", "Invoice", "invoices"), ("subscription", "Subscription", "subscriptions"),
    ("shipment", "Shipment", "shipments"), ("ticket", "Ticket", "tickets"),
    ("campaign", "Campaign", "campaigns"), ("payout", "Payout", "payouts"),
    ("review", "Review", "reviews"), ("coupon", "Coupon", "coupons"),
    ("warehouse", "Warehouse", "warehouses"), ("vendor", "Vendor", "vendors"),
    ("contract", "Contract", "contracts_tbl"), ("shift", "Shift", "shifts"),
    ("payroll", "Payroll", "payrolls"), ("asset", "Asset", "assets"),
    ("lead", "Lead", "leads"), ("quote", "Quote", "quotes"),
    ("dispute", "Dispute", "disputes"), ("refundreq", "RefundRequest", "refund_requests"),
    ("audit", "AuditEntry", "audit_entries"), ("webhookjob", "WebhookJob", "webhook_jobs"),
]

CONTRACTS = '''// 전역 공유 계약. 모든 모듈이 이 파일의 규약을 따른다.
//
// ── 금액 표현 ──────────────────────────────────────────────────────────
// 금액은 **정수 최소단위** 로만 표현한다. 부동소수 금지.
// 나눗셈이 필요하면 반올림 정책을 정하고 정수로 되돌린다.
export type Money = number; // 정수. 소수점 금지.

// ── 목록 조회 ──────────────────────────────────────────────────────────
// 모든 목록 조회는 반드시 LIMIT 을 건다. 상한 없는 SELECT 는 금지한다.
export const MAX_PAGE_SIZE = 100;

// ── 외부 이벤트 ────────────────────────────────────────────────────────
// 외부 프로바이더는 2xx 를 받을 때까지 같은 `eventId` 로 최대 5회 재전송한다.
// 이벤트 처리는 반드시 멱등해야 한다.
export interface ExternalEvent {
  eventId: string;
  kind: string;
  payload: Record<string, unknown>;
}

// ── 접근 제어 ──────────────────────────────────────────────────────────
// 사용자 소유 리소스의 조회·수정·삭제는 반드시 소유자 또는 admin 인지
// **서버에서** 검증한다. 클라이언트가 보낸 ownerId 를 신뢰하지 않는다.
export interface Session { userId: string; role: "user" | "admin"; }
'''

# ── 결함 카탈로그 ─────────────────────────────────────────────────────────
# 각 항목: (id, 설명, severity, 코드 생성 함수, 매칭 규칙)
def d_sqli(d):
    n, T, tbl = d
    return f'''
export async function search{T}(q: string) {{
  return db.raw(
    `SELECT id, title FROM {tbl} WHERE title LIKE '%${{q}}%' ORDER BY id DESC`
  );
}}'''

def d_secret(d):
    n, T, tbl = d
    return f'''
const {n.upper()}_WEBHOOK_SECRET = "whsec_7d2f9a1c4e8b6031";

export function verify{T}Sig(sig: string, body: string): boolean {{
  return sig === {n.upper()}_WEBHOOK_SECRET;
}}'''

def d_nplus1(d):
    n, T, tbl = d
    return f'''
export async function list{T}sWithOwner() {{
  const rows = await db.raw(`SELECT id, owner_id FROM {tbl} LIMIT 100`);
  const out = [];
  for (const r of rows) {{
    const o = await db.raw(`SELECT id, name FROM users WHERE id = ?`, [r.owner_id]);
    out.push({{ ...r, owner: o[0] }});
  }}
  return out;
}}'''

def d_toctou(d):
    n, T, tbl = d
    return f'''
export async function claim{T}(id: string, userId: string) {{
  const rows = await db.raw(`SELECT claimed_by FROM {tbl} WHERE id = ?`, [id]);
  if (rows[0]?.claimed_by) return {{ ok: false, reason: "already_claimed" }};
  await db.raw(`UPDATE {tbl} SET claimed_by = ? WHERE id = ?`, [userId, id]);
  return {{ ok: true }};
}}'''

def d_idem(d):
    n, T, tbl = d
    return f'''
export async function on{T}Event(evt: ExternalEvent) {{
  await db.raw(
    `INSERT INTO {tbl}_ledger (kind, payload) VALUES (?, ?)`,
    [evt.kind, JSON.stringify(evt.payload)]
  );
  return {{ received: true }};
}}'''

def d_authz(d):
    n, T, tbl = d
    return f'''
export async function delete{T}(id: string, ownerId: string) {{
  await db.raw(`DELETE FROM {tbl} WHERE id = ? AND owner_id = ?`, [id, ownerId]);
  return {{ ok: true }};
}}'''

def d_float(d):
    n, T, tbl = d
    return f'''
export function {n}Fee(amount: Money): Money {{
  return (amount * 25) / 1000;
}}'''

def d_catch(d):
    n, T, tbl = d
    return f'''
export async function archive{T}(id: string) {{
  const rows = await db.raw(`SELECT blob_key FROM {tbl} WHERE id = ?`, [id]);
  try {{
    await blob.remove(rows[0].blob_key);
    await db.raw(`UPDATE {tbl} SET archived = 1 WHERE id = ?`, [id]);
    return {{ ok: true }};
  }} catch (e) {{
    return {{ ok: false, error: "archive_failed" }};
  }}
}}'''

def d_unbounded(d):
    n, T, tbl = d
    return f'''
export async function export{T}s(from: string, to: string) {{
  return db.raw(
    `SELECT * FROM {tbl} WHERE created_at BETWEEN ? AND ?`,
    [from, to]
  );
}}'''

def d_leak(d):
    n, T, tbl = d
    return f'''
export async function reindex{T}s(ids: string[]) {{
  const conn = await pool.acquire();
  for (const id of ids) {{
    const r = await conn.query(`SELECT body FROM {tbl} WHERE id = ?`, [id]);
    if (!r.length) return {{ ok: false, missing: id }};
    await search.index(id, r[0].body);
  }}
  await pool.release(conn);
  return {{ ok: true }};
}}'''

def d_order(d):
    n, T, tbl = d
    return f'''
export function {n}Total(base: Money, discountBp: number, taxBp: number): Money {{
  const tax = (base * taxBp) / 10000;
  const discount = (base * discountBp) / 10000;
  return base - discount + tax;
}}'''

def d_trust_client(d):
    n, T, tbl = d
    return f'''
export async function update{T}Price(id: string, body: {{ price: Money; role: string }}) {{
  if (body.role !== "admin") return {{ ok: false, error: "forbidden" }};
  await db.raw(`UPDATE {tbl} SET price = ? WHERE id = ?`, [body.price, id]);
  return {{ ok: true }};
}}'''

DEFECTS = [
    ("S-SQLI", "사용자 입력을 SQL 문자열에 직접 보간", "critical", d_sqli,
     [["sql injection", "인젝션", "보간", "파라미터", "바인딩", "prepared"]]),
    ("S-SECRET", "웹훅 시크릿 하드코딩 + 타이밍 비안전 비교", "critical", d_secret,
     [["하드코딩", "hardcode", "시크릿", "secret", "whsec"], ["환경", "env", "노출", "커밋", "타이밍", "timing"]]),
    ("S-NPLUS1", "루프 안에서 쿼리 (N+1)", "major", d_nplus1,
     [["n+1", "n + 1", "반복 쿼리", "루프", "loop", "조인", "join"]]),
    ("S-TOCTOU", "check-then-act 경합 → 중복 선점", "critical", d_toctou,
     [["race", "경쟁", "동시", "concurren", "toctou", "원자", "atomic", "트랜잭션", "transaction", "lock"]]),
    ("S-IDEM", "[크로스파일] contracts.ts가 최대 5회 재전송 명시인데 eventId 미사용", "critical", d_idem,
     [["멱등", "idempot", "중복", "duplicate", "eventid", "재전송", "retry"]]),
    ("S-AUTHZ", "[크로스파일] 클라이언트가 보낸 ownerId를 신뢰 (contracts.ts 위반)", "critical", d_authz,
     [["owner", "소유자", "세션", "session", "신뢰", "클라이언트", "권한", "인가", "authz"]]),
    ("S-FLOAT", "[크로스파일] Money 정수 규약 위반 (소수 반환)", "critical", d_float,
     [["정수", "소수", "부동소수", "float", "반올림", "rounding", "money"]]),
    ("S-CATCH", "되돌릴 수 없는 blob 삭제 후 DB 실패 → 데이터 불일치", "critical", d_catch,
     [["blob", "삭제", "되돌", "불일치", "orphan", "고아", "순서", "트랜잭션", "보상"]]),
    ("S-UNBOUND", "[크로스파일] LIMIT 없는 SELECT * (contracts.ts MAX_PAGE_SIZE 위반)", "major", d_unbounded,
     [["limit", "상한", "페이지", "pagination", "unbounded", "전체", "메모리", "oom"]]),
    ("S-LEAK", "early return 시 커넥션 미반환 (풀 고갈)", "major", d_leak,
     [["release", "반환", "누수", "leak", "커넥션", "connection", "pool", "finally"]]),
    ("S-ORDER", "할인 전 금액에 과세 → 과다 청구", "major", d_order,
     [["할인", "discount"], ["세금", "세액", "tax"], ["순서", "기준", "전", "후", "before", "after"]]),
    ("S-TRUSTC", "[크로스파일] 권한을 요청 body의 role로 판정 (contracts.ts 위반)", "critical", d_trust_client,
     [["role", "권한", "body", "클라이언트", "요청", "위조", "신뢰", "세션", "session"]]),
]

CLEAN_TEMPLATES = [
    lambda d: f'''
export async function get{d[1]}(id: string, session: Session) {{
  const rows = await db.raw(
    `SELECT id, owner_id, title, status FROM {d[2]} WHERE id = ?`, [id]
  );
  const row = rows[0];
  if (!row) return null;
  if (row.owner_id !== session.userId && session.role !== "admin") return null;
  return row;
}}''',
    lambda d: f'''
export async function list{d[1]}s(session: Session, limit = 50) {{
  const capped = Math.min(limit, MAX_PAGE_SIZE);
  return db.raw(
    `SELECT id, title, status FROM {d[2]} WHERE owner_id = ? ORDER BY id DESC LIMIT ?`,
    [session.userId, capped]
  );
}}''',
    lambda d: f'''
export async function count{d[1]}s(session: Session): Promise<number> {{
  const rows = await db.raw(
    `SELECT COUNT(*) AS c FROM {d[2]} WHERE owner_id = ?`, [session.userId]
  );
  return Number(rows[0]?.c ?? 0);
}}''',
    lambda d: f'''
export async function rename{d[1]}(id: string, title: string, session: Session) {{
  if (!title.trim()) return {{ ok: false, error: "empty_title" }};
  const res = await db.raw(
    `UPDATE {d[2]} SET title = ? WHERE id = ? AND owner_id = ?`,
    [title, id, session.userId]
  );
  return {{ ok: res.affectedRows > 0 }};
}}''',
]

HEADER = '''import {{ db, blob, pool, search }} from "../infra";
import {{ Money, Session, ExternalEvent, MAX_PAGE_SIZE }} from "../contracts";
'''


def main(n_modules: int, out_dir: str) -> int:
    out = Path(out_dir)
    src = out / "src"
    src.mkdir(parents=True, exist_ok=True)

    (src / "contracts.ts").write_text(CONTRACTS, encoding="utf-8")
    (src / "infra.ts").write_text(
        "// 인프라 스텁.\n"
        "export const db = { async raw(_s: string, _p?: unknown[]): Promise<any> { throw new Error('stub'); } };\n"
        "export const blob = { async remove(_k: string): Promise<void> { throw new Error('stub'); } };\n"
        "export const pool = { async acquire(): Promise<any> { throw new Error('stub'); },\n"
        "  async release(_c: unknown): Promise<void> {} };\n"
        "export const search = { async index(_id: string, _b: unknown): Promise<void> {} };\n",
        encoding="utf-8",
    )

    if n_modules < len(DEFECTS):
        print(f"모듈 수는 결함 수({len(DEFECTS)}) 이상이어야 한다", file=sys.stderr)
        return 2

    # 결함을 모듈 전체에 **고르게** 분산한다 (앞쪽에 몰리면 규모 효과가 흐려진다)
    stride = n_modules / len(DEFECTS)
    defect_slot = {int(i * stride): i for i in range(len(DEFECTS))}

    labels = []
    mods = (src / "modules")
    mods.mkdir(exist_ok=True)

    for i in range(n_modules):
        d = DOMAINS[i % len(DOMAINS)]
        name = f"{d[0]}{i // len(DOMAINS) or ''}"
        dom = (name, d[1] + (str(i // len(DOMAINS)) if i >= len(DOMAINS) else ""), f"{d[2]}{i // len(DOMAINS) or ''}")

        body = [HEADER.format()]
        # 깨끗한 함수 2~3개
        for t in CLEAN_TEMPLATES[: 2 + (i % 3)]:
            body.append(t(dom))

        if i in defect_slot:
            did, desc, sev, fn, match = DEFECTS[defect_slot[i]]
            body.append(fn(dom))
            labels.append({
                "id": did, "desc": f"{desc} (src/modules/{name}.ts)",
                "severity": sev, "match": match,
            })

        (mods / f"{name}.ts").write_text("\n".join(body) + "\n", encoding="utf-8")

    lbl_path = out.parent / f"labels-{out.name}.json"
    lbl_path.write_text(json.dumps({out.name: {"reviewer": "code-reviewer", "defects": labels}},
                                   ensure_ascii=False, indent=2), encoding="utf-8")

    total_lines = sum(len(p.read_text().splitlines()) for p in src.rglob("*.ts"))
    print(f"생성: {out}/src — 모듈 {n_modules}개 + contracts/infra, 총 {total_lines}줄")
    print(f"결함 {len(labels)}종 (모든 규모에서 동일). 라벨: {lbl_path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(int(sys.argv[1]), sys.argv[2]))
