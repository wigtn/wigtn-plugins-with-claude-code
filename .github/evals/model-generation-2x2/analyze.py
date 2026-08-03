#!/usr/bin/env python3
"""2×2 분석 — PROTOCOL.md 의 판정 규칙을 그대로 코드로 옮긴 것.

프로토콜이 정한 것 (결과를 보기 전에 정해진 것들):

  하네스 효과(M) = A1(M) − A0(M)          ← 같은 모델 안에서만 뺀다
  논지 입증: 효과(5) < 효과(4.8)           ← 세대가 오르며 하네스 효과 감소
  논지 반증: 효과(5) ≥ 효과(4.8)

  대각선 비교(A1(5) − A0(4.8))는 하네스 효과라고 부르지 않는다 —
  모델과 하네스가 동시에 바뀌기 때문이다.

  방향성 인정 조건: fixture 3개 중 **2개 이상**에서 같은 방향.
  (fixture당 arm당 n=3 이라 소수점 차이를 신호로 읽지 않는다)

채점기는 score_prd.py 를 그대로 import 한다 — 채점 로직을 여기서 재구현하지 않는다.

사용: python3 analyze.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from score_prd import CHECKS, score  # noqa: E402  (사전등록 채점기를 그대로 쓴다)

MODELS = ["claude-opus-4-8", "claude-opus-5"]
ARMS = ["A0", "A1"]
CONTAMINATION = re.compile(r"Scale Grade|Has FE Components|5\.4\.1", re.I)


def cell(model: str, arm: str) -> dict:
    """한 칸(model×arm)의 fixture별 점수. 반환: {fixture: [비율, ...]}"""
    d = HERE / "runs" / f"{model}__{arm}"
    out: dict[int, list[float]] = {1: [], 2: [], 3: []}
    dirty: list[str] = []
    for f in sorted(d.glob("prd.*.md")):
        m = re.match(r"prd\.f(\d)r(\d)\.md", f.name)
        if not m:
            continue
        got, _ = score(f)
        out[int(m.group(1))].append(sum(got.values()) / len(CHECKS))
        if arm == "A0" and CONTAMINATION.search(f.read_text(encoding="utf-8", errors="ignore")):
            dirty.append(f.name)
    if dirty:
        print(f"  ⚠️  오염 의심 — {model} {arm}: {', '.join(dirty)}", file=sys.stderr)
    return out


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def main() -> int:
    data = {(m, a): cell(m, a) for m in MODELS for a in ARMS}

    # ── 2×2 표 ─────────────────────────────────────────────────────────
    print("# 2×2 결과 — 모델 세대 × 하네스\n")
    print("측정 축: **계약 준수율** (플러그인 자신의 게이트가 Critical로 보는 10항목)\n")
    print("| | A0 — 하네스 없음 | A1 — 플러그인 | 하네스 효과 |")
    print("|---|---|---|---|")
    effect = {}
    for m in MODELS:
        a0 = mean([v for xs in data[(m, "A0")].values() for v in xs])
        a1 = mean([v for xs in data[(m, "A1")].values() for v in xs])
        effect[m] = a1 - a0
        print(f"| **{m}** | {a0:.0%} | {a1:.0%} | **{a1 - a0:+.0f}%p** |".replace(
            f"{a1 - a0:+.0f}", f"{(a1 - a0) * 100:+.0f}"))

    # ── 프로토콜 판정 ──────────────────────────────────────────────────
    e48, e5 = effect["claude-opus-4-8"], effect["claude-opus-5"]
    print(f"\n## 프로토콜 판정\n")
    print(f"- 하네스 효과(4.8) = **{e48:+.0%}p**")
    print(f"- 하네스 효과(5)   = **{e5:+.0%}p**")
    verdict = "입증 — 세대가 오르며 하네스 효과 감소" if e5 < e48 else "**반증** — 효과가 유지되거나 증가"
    print(f"- 논지: {verdict}")

    # ── fixture별 방향 (≥2/3 일치해야 방향 인정) ────────────────────────
    print("\n### fixture별 방향 (프로토콜: 3개 중 2개 이상 같은 방향일 때만 인정)\n")
    print("| fixture | 효과(4.8) | 효과(5) | 효과 감소? |")
    print("|---|---|---|---|")
    agree = 0
    for f in (1, 2, 3):
        e = {}
        for m in MODELS:
            e[m] = mean(data[(m, "A1")][f]) - mean(data[(m, "A0")][f])
        dec = e["claude-opus-5"] < e["claude-opus-4-8"]
        agree += dec
        print(f"| f{f} | {e['claude-opus-4-8']:+.0%}p | {e['claude-opus-5']:+.0%}p | "
              f"{'예' if dec else '아니오'} |")
    print(f"\n→ **{agree}/3** fixture에서 효과 감소. "
          f"{'방향성 인정' if agree >= 2 else '**방향성 인정 불가** — 프로토콜 기준(2/3) 미달'}")

    # ── 항목별: 무엇이 하네스 없이는 안 나오는가 ────────────────────────
    print("\n### 항목별 준수율 (하네스가 실제로 무엇을 만들어내는가)\n")
    hdr = " | ".join(f"{m.replace('claude-opus-', 'O')} {a}" for m in MODELS for a in ARMS)
    print(f"| 항목 | {hdr} |")
    print("|---" * 5 + "|")
    for i, (key, desc, _) in enumerate(CHECKS):
        cells = []
        for m in MODELS:
            for a in ARMS:
                d = HERE / "runs" / f"{m}__{a}"
                files = sorted(d.glob("prd.*.md"))
                hits = sum(1 for f in files if score(f)[0][key])
                cells.append(f"{hits}/{len(files)}" if files else "—")
        print(f"| {desc} | {' | '.join(cells)} |")

    # ── ERRATA E-03 사전 판정 ──────────────────────────────────────────
    print("\n### ERRATA E-03 사전 판정 (계약 파일 분리를 유지할 것인가)\n")
    print("결과를 보기 전에 정한 기준: **A1 준수율 90% 미만이면 간접 참조를 기각하고 인라인으로 되돌린다.**\n")
    for m in MODELS:
        a1 = mean([v for xs in data[(m, "A1")].values() for v in xs])
        print(f"- {m} A1 = **{a1:.0%}** → "
              f"{'유지' if a1 >= 0.90 else '**기각 — 인라인 복귀**'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
