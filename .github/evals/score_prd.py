#!/usr/bin/env python3
"""생성된 PRD 채점 — 필수 섹션 존재 여부(기계 판정) + 분량.

실험 2의 질문: **템플릿이 실제로 값을 하는가?**
이 저장소는 "산출물 템플릿은 모델이 좋아져도 가치가 있다"고 계속 주장해 왔지만
한 번도 측정하지 않았다. 맨 모델(A0)도 알아서 State Matrix를 쓴다면
템플릿도 감가상각 대상이다.

채점 항목은 **플러그인 자신의 게이트가 Critical로 취급하는 것들**이다.
즉 플러그인이 "이게 없으면 불합격"이라고 선언한 기준으로 스스로를 평가한다.

사용: python3 .github/evals/score_prd.py runs/E2-A0 runs/E2-A1 [runs/E2-A2]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# (키, 설명, 정규식들 — 하나라도 걸리면 존재로 인정)
CHECKS = [
    ("roles", "User Roles 표 (역할별 권한)",
     [r"user\s*roles", r"##\s*.*역할", r"\|\s*role\s*key\s*\|", r"권한\s*범위"]),
    ("pages", "Pages 표 (화면 목록)",
     [r"##\s*.*pages", r"\|\s*page\s*\|", r"화면\s*목록", r"has\s*fe\s*components"]),
    ("state_matrix", "State Matrix (Empty/Loading/Error/Success)",
     [r"state\s*matrix", r"상태\s*매트릭스",
      r"(empty|비어).{0,80}(loading|로딩).{0,80}(error|오류|에러)"]),
    ("user_flow", "User Flow 다이어그램 (Mermaid)",
     [r"```mermaid", r"user\s*flow", r"플로우차트", r"flowchart"]),
    ("nfr_quant", "정량적 NFR (p95/ms/초/동시성 수치)",
     [r"p9[59]", r"\d+\s*ms\b", r"\d+\s*초\s*(이내|미만)", r"\d+\s*req/s", r"동시\s*접속\s*\d+"]),
    ("acceptance", "수용 기준 (Given/When/Then)",
     [r"\bgiven\b.{0,200}\bwhen\b", r"scenario\s*:", r"acceptance\s*criteria"]),
    ("authz", "권한/인가 명세 (관리자 삭제 등)",
     [r"인가", r"authoriz", r"권한\s*(검증|체크|확인)", r"role\s*[=:]+\s*[\"']?admin"]),
    ("fr_table", "FR 테이블 (ID가 붙은 요구사항)",
     [r"\bfr-\d+", r"\|\s*fr[-_ ]?id\s*\|", r"\breq-\d+"]),
    ("nongoals", "Non-Goals (범위 밖 명시)",
     [r"non[- ]goals?", r"범위\s*밖", r"하지\s*않는\s*것"]),
    ("phases", "구현 단계 (Phase 분할)",
     [r"phase\s*\d", r"##\s*.*구현\s*단계", r"마일스톤"]),
]


def score(path: Path) -> tuple[dict, int]:
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    # 주의: 아래 패턴은 전부 소문자로 쓴다 (텍스트를 소문자화했으므로)
    got = {}
    for key, _desc, pats in CHECKS:
        got[key] = any(re.search(p, text, re.S) for p in pats)
    return got, len(text.splitlines())


def main(dirs: list[str]) -> int:
    arms = {}
    for d in dirs:
        p = Path(d)
        files = sorted(p.glob("prd.*.md"))
        if not files:
            print(f"{d}: prd.*.md 없음", file=sys.stderr)
            continue
        arms[p.name] = [score(f) for f in files]

    if not arms:
        return 2

    print("# 실험 2 — PRD 생성 품질\n")
    print("채점 기준은 **플러그인 자신의 게이트가 Critical로 보는 항목**이다.\n")

    hdr = " | ".join(f"{a} (n={len(v)})" for a, v in arms.items())
    print(f"| 필수 요소 | {hdr} |")
    print("|---" * (len(arms) + 1) + "|")

    totals = {a: 0 for a in arms}
    for key, desc, _ in CHECKS:
        cells = []
        for a, runs in arms.items():
            hits = sum(1 for g, _ in runs if g[key])
            totals[a] += hits
            mark = "✅" if hits == len(runs) else ("🟡" if hits else "❌")
            cells.append(f"{mark} {hits}/{len(runs)}")
        print(f"| {desc} | {' | '.join(cells)} |")

    print()
    n_checks = len(CHECKS)
    for a, runs in arms.items():
        denom = n_checks * len(runs)
        print(f"- **{a}: {totals[a]}/{denom} = {totals[a]/denom:.0%}** "
              f"· 평균 {sum(l for _, l in runs) / len(runs):.0f}줄")

    print("\n> 읽는 법: A0(플러그인 없음)가 이미 높으면 **템플릿은 감가상각 대상**이다.")
    print("> A1/A2가 뚜렷이 높으면 템플릿은 모델 능력과 무관하게 값을 한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["runs/E2-A0", "runs/E2-A1"]))
