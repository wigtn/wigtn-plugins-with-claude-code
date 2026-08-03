#!/usr/bin/env python3
"""3-arm 하네스 비교 분석기.  PROTOCOL.md 의 사전등록 규칙을 그대로 구현한다.

주 산출물은 총점이 아니라 **항목별 표**다. 총점은 어느 지시를 지워야 하는지
알려주지 않는다.

설계 원칙 — 이 저장소가 이미 당한 사고를 되풀이하지 않는다:
  E-02  "결과 없음"과 "0점"을 절대 같은 값으로 렌더하지 않는다.
  구 analyze.py  nan 을 비교에 넣어 `nan < x == False` 를 "방향성 없음"으로
        출력했다. 데이터 없음이 반증으로 둔갑했다. 여기서는 데이터가 없으면
        비교를 **수행하지 않고** `n/a` 로 표기한다.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from score_prd import CHECKS, score  # noqa: E402  (사전등록 채점기, 수정 금지)

ARMS = ["A0", "A1", "A2", "A3"]
MODEL = sys.argv[1] if len(sys.argv) > 1 else "claude-opus-5"

# PROTOCOL.md "A2 설계 규칙" 의 임계값. 결과를 보고 바꾸지 않는다.
ALREADY_KNOWN = 0.80   # A0 통과율 이상 -> 지시가 밥값 못 함, 삭제 대상
LOAD_BEARING = 0.25    # A0 통과율 이하 & A1 높음 -> 진짜 계약, 유지
REJECT_MARGIN = 0.05   # A2 가 A1 보다 이만큼 낮으면 감축 기각


def read_meta(p: Path) -> dict:
    d = {}
    if p.exists():
        for line in p.read_text(errors="ignore").splitlines():
            k, _, v = line.partition("=")
            d[k.strip()] = v.strip()
    return d


def load_arm(arm: str) -> dict | None:
    cell = HERE / "runs" / f"{MODEL}__{arm}"
    files = sorted(cell.glob("prd.*.md"))
    if not files:
        return None
    runs = []
    for f in files:
        got, lines = score(f)
        meta = read_meta(cell / "logs" / f"{f.stem.split('.', 1)[1]}.meta")
        tok = meta.get("billed_tokens", "unknown")
        runs.append({
            "key": f.stem.split(".", 1)[1],
            "got": got,
            "lines": lines,
            "fixture": meta.get("fixture", "?"),
            "verdict": meta.get("verdict", "?"),
            "artifact": meta.get("artifact", "?"),
            "tokens": int(tok) if tok.isdigit() else None,
            "seconds": int(meta["seconds"]) if meta.get("seconds", "").isdigit() else None,
        })
    return {"arm": arm, "runs": runs, "n": len(runs)}


def pct(hits: int, n: int) -> str:
    return f"{hits}/{n} ({hits / n:.0%})" if n else "n/a"


def main() -> int:
    arms = {a: d for a in ARMS if (d := load_arm(a))}
    if not arms:
        print(f"채점할 산출물이 없다: runs/{MODEL}__*/prd.*.md", file=sys.stderr)
        return 2

    print(f"# 3-arm 하네스 비교 — {MODEL}\n")
    print("| arm | n | 계약 준수율 | 평균 줄수 | 평균 토큰 | 항목당 토큰 |")
    print("|---|---|---|---|---|---|")
    summary = {}
    for a, d in arms.items():
        n = d["n"]
        hits = sum(sum(1 for r in d["runs"] if r["got"][k]) for k, _, _ in CHECKS)
        denom = len(CHECKS) * n
        toks = [r["tokens"] for r in d["runs"] if r["tokens"] is not None]
        avg_tok = sum(toks) / len(toks) if toks else None
        # 항목당 토큰: 충족 항목 1개를 얻는 데 든 토큰. 준수율이 같아도 이게
        # 다르면 그게 결론이다.
        per_item = (avg_tok / (hits / n)) if (avg_tok and hits) else None
        summary[a] = {"rate": hits / denom if denom else None,
                      "avg_tok": avg_tok, "per_item": per_item, "n": n,
                      "tok_n": len(toks)}
        print(f"| **{a}** | {n} | {pct(hits, denom)} "
              f"| {sum(r['lines'] for r in d['runs']) / n:.0f} "
              f"| {f'{avg_tok:,.0f}' if avg_tok else 'n/a'}"
              f"{'' if len(toks) == n else f' (n={len(toks)})'} "
              f"| {f'{per_item:,.0f}' if per_item else 'n/a'} |")

    # ── 항목별 표 — 이 실험의 주 산출물 ────────────────────────────────
    print("\n## 항목별 통과율 — A3 설계 입력\n")
    hdr = " | ".join(f"{a} (n={d['n']})" for a, d in arms.items())
    print(f"| 계약 항목 | {hdr} | 판정 |")
    print("|---" * (len(arms) + 2) + "|")

    verdicts = {}
    for key, desc, _ in CHECKS:
        cells, rates = [], {}
        for a, d in arms.items():
            hits = sum(1 for r in d["runs"] if r["got"][key])
            rates[a] = hits / d["n"]
            mark = "✅" if hits == d["n"] else ("🟡" if hits else "❌")
            cells.append(f"{mark} {hits}/{d['n']}")

        a0 = rates.get("A0")
        a1 = rates.get("A1")
        if a0 is None:
            v = "n/a (A0 없음)"
        elif a0 >= ALREADY_KNOWN:
            v = "🗑️ **삭제** — 모델이 이미 함"
        elif a0 <= LOAD_BEARING and a1 is not None and a1 >= 0.8:
            v = "✅ **유지** — 진짜 계약"
        elif a0 <= LOAD_BEARING and a1 is not None:
            v = "⚠️ 지시가 작동 안 함 — 수정/삭제"
        else:
            v = "⏸️ 판정 보류 — n 추가"
        verdicts[key] = (v, rates)
        print(f"| {desc} | {' | '.join(cells)} | {v} |")

    # ── 사전등록 기각 규칙 ────────────────────────────────────────────
    print("\n## 사전등록 판정\n")
    r1, r2 = summary.get("A1", {}).get("rate"), summary.get("A2", {}).get("rate")
    if r1 is None or r2 is None:
        print(f"- **A2 기각 규칙: 판정 불가** — A1={'있음' if r1 is not None else '없음'}, "
              f"A2={'있음' if r2 is not None else '없음'}. "
              "데이터가 없는 것을 '통과'로도 '기각'으로도 읽지 않는다.")
    else:
        gap = r1 - r2
        ok = gap < REJECT_MARGIN
        print(f"- A1 {r1:.0%} vs A2 {r2:.0%} — 격차 {gap:+.1%}p "
              f"(기각선 {REJECT_MARGIN:.0%}p)")
        print(f"- **감축 판정: {'유지' if ok else '기각 — 해당 절을 되살린다'}**")

    t1, t2 = summary.get("A1", {}).get("avg_tok"), summary.get("A2", {}).get("avg_tok")
    if t1 and t2 and r1 is not None and r2 is not None:
        print(f"- 토큰 {t1:,.0f} → {t2:,.0f} ({(t2 / t1 - 1):+.0%})")
        if r2 + REJECT_MARGIN < r1:
            print("  - 준수율이 기각선 아래이므로 **토큰 절감을 이득이라 부르지 않는다.**")
        elif t2 < t1:
            print("  - 준수율을 유지하며 토큰이 낮다 → **감축이 이득**")
        else:
            print("  - 준수율은 유지했으나 토큰이 줄지 않았다 → 감축의 비용 근거 없음")

    # ── 계측 건전성 ───────────────────────────────────────────────────
    print("\n## 계측 건전성\n")
    for a, d in arms.items():
        vs = {}
        for r in d["runs"]:
            vs[r["artifact"]] = vs.get(r["artifact"], 0) + 1
        miss = summary[a]["n"] - summary[a]["tok_n"]
        print(f"- **{a}**: " + ", ".join(f"{k}={v}" for k, v in sorted(vs.items()))
              + (f" · 토큰 미기록 {miss}건" if miss else " · 토큰 전건 기록"))
    print("\n> `nofile`은 빈 파일로 0점 채점된다(계약 불이행). `fail`(계측 실패)은")
    print("> 애초에 산출물이 없어 이 표에 포함되지 않는다. 둘을 섞지 않는다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
