#!/usr/bin/env python3
"""라벨링 픽스처 채점 — 검출률과 오탐률을 함께 낸다.

검출률만 보면 "전부 critical로 찍기" 전략이 이긴다. 그래서 깨끗한 픽스처에
대한 오탐(critical/major 보고)을 반드시 짝으로 본다.

사용:
    python3 .github/evals/score.py runs/<run-dir>

<run-dir> 안의 파일명 규칙:  <fixture>.<n>.txt   (예: prd-defective.md.1.txt)
파일 내용은 리뷰어 에이전트의 출력 원문. JSON 블록이 있으면 severity 집계에
쓰고, 없으면 텍스트 휴리스틱으로 센다.

출력은 마크다운 표 — before/after 비교에 그대로 붙인다.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABELS = json.loads((HERE / "labels.json").read_text(encoding="utf-8"))

SEV_CRIT = re.compile(r"\bcritical\b", re.I)
SEV_MAJOR = re.compile(r"\bmajor\b", re.I)


def detected(text: str, groups: list[list[str]]) -> bool:
    """모든 AND 그룹에서 최소 하나씩 걸리면 그 결함을 지목한 것으로 인정."""
    low = text.lower()
    return all(any(kw.lower() in low for kw in group) for group in groups)


def count_severities(text: str) -> tuple[int, int] | None:
    """critical / major 보고 건수. JSON 블록이 없으면 None — 추정하지 않는다.

    산문에서 "critical" 단어를 세는 폴백을 두면 조용히 틀린 숫자가 나온다.
    (실제로 그렇게 해서 findings 0건인 실행이 'critical 3건'으로 집계됐다.)
    측정할 수 없으면 측정할 수 없다고 말한다.
    """
    for m in re.finditer(r"```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```", text, re.S):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else data.get("findings", [])
        if isinstance(items, list):
            sev = [str(i.get("severity", "")).lower() for i in items if isinstance(i, dict)]
            return sev.count("critical"), sev.count("major")
    return None


def main(run_dir: str) -> int:
    root = Path(run_dir)
    if not root.is_dir():
        print(f"실행 디렉토리를 찾을 수 없음: {run_dir}", file=sys.stderr)
        return 2

    runs: dict[str, list[Path]] = defaultdict(list)
    for f in sorted(root.glob("*.txt")):
        fixture = re.sub(r"\.\d+\.txt$", "", f.name)
        runs[fixture].append(f)

    if not runs:
        print(f"{run_dir} 안에 <fixture>.<n>.txt 가 없음", file=sys.stderr)
        return 2

    print(f"# 픽스처 eval 결과 — `{root.name}`\n")

    # ── 검출률 ────────────────────────────────────────────────────────
    print("## 검출률 (심어둔 결함을 잡았는가)\n")
    print("| 픽스처 | 결함 | severity | 검출 | 비율 |")
    print("|---|---|---|---|---|")
    totals: dict[str, list[int]] = {}
    for fixture, files in sorted(runs.items()):
        spec = LABELS.get(fixture)
        if not spec or not spec["defects"]:
            continue
        hits_total = 0
        n = len(files)
        for d in spec["defects"]:
            hits = sum(detected(f.read_text(encoding="utf-8"), d["match"]) for f in files)
            hits_total += hits
            mark = "✅" if hits == n else ("🟡" if hits else "❌")
            print(f"| `{fixture}` | {d['id']} {d['desc'][:38]} | {d['severity']} | {mark} {hits}/{n} | {hits/n:.0%} |")
        totals[fixture] = [hits_total, len(spec["defects"]) * n]

    print()
    for fixture, (hit, tot) in totals.items():
        print(f"- **`{fixture}` 종합 검출률: {hit}/{tot} = {hit/tot:.0%}**")

    # ── 오탐률 ────────────────────────────────────────────────────────
    print("\n## 오탐 (깨끗한 픽스처에 무엇을 다는가)\n")
    print("> **critical 만 오탐 지표로 쓴다.** 게이트의 차단 조건이 `critical ≥1` 이고,")
    print("> 현실적인 PRD·코드에는 major/minor 지적거리가 늘 있기 때문이다 — 그건 리뷰가")
    print("> 하라고 있는 일이지 오탐이 아니다.\n")
    print("| 픽스처 | 실행 | critical | major | 판정 |")
    print("|---|---|---|---|---|")
    for fixture, files in sorted(runs.items()):
        spec = LABELS.get(fixture)
        if not spec or not spec.get("expect_clean"):
            continue
        for i, f in enumerate(sorted(files), 1):
            res = count_severities(f.read_text(encoding="utf-8"))
            if res is None:
                print(f"| `{fixture}` | {i} | — | — | ⚠️ JSON 블록 없음 (집계 제외) |")
                continue
            c, m = res
            verdict = "✅ 무결" if c == 0 else f"❌ 오탐 critical {c}건"
            print(f"| `{fixture}` | {i} | {c} | {m} | {verdict} |")

    print("\n> 검출률과 오탐률은 **함께** 봐야 한다. 검출률만 올리는 가장 쉬운 방법은")
    print("> 모든 것을 critical로 찍는 것이고, 그러면 게이트가 무의미해진다.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else str(HERE / "runs" / "baseline")))
