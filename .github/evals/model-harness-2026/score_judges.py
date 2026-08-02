#!/usr/bin/env python3
"""Aggregate anonymized judge JSON without changing malformed judgments."""

from __future__ import annotations

import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path


ARMS = ("M55-CURRENT", "M56-BARE", "M56-CURRENT", "M56-OPT")
CRITERIA = (
    "task_fidelity",
    "correctness",
    "specificity_traceability",
    "restraint",
    "usability",
)


def load_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def main(study_arg: str) -> int:
    study = Path(study_arg)
    runs = study / "judge-runs"
    mapping = json.loads((study / "judge-prompts/blind-map.json").read_text())
    rows = []
    invalid = []
    winner_by_bundle: dict[str, dict[str, set[str]]] = defaultdict(dict)

    for judge in ("J55", "J56"):
        for path in sorted((runs / judge).glob("*.json")):
            key = path.stem
            try:
                result = load_json(path)
                scores = result["scores"]
                first = set(result["ranking"][0])
                winner_by_bundle[key][judge] = {mapping[key][alias] for alias in first}
                for alias, arm in mapping[key].items():
                    values = scores[alias]
                    calculated = sum(int(values[name]) for name in CRITERIA)
                    reported = int(values["total"])
                    if calculated != reported:
                        raise ValueError(f"{alias} total {reported} != {calculated}")
                    rows.append(
                        {
                            "judge": judge,
                            "bundle": key,
                            "alias": alias,
                            "arm": arm,
                            **{name: int(values[name]) for name in CRITERIA},
                            "total": calculated,
                            "is_first": int(alias in first),
                        }
                    )
            except Exception as exc:
                invalid.append(f"{path}: {exc}")

    if invalid:
        (runs / "INVALID.txt").write_text("\n".join(invalid) + "\n", encoding="utf-8")
        print("\n".join(invalid), file=sys.stderr)

    if not rows:
        return 2

    with (runs / "JUDGE-SCORES.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    out = ["# 익명 품질 판정 결과\n"]
    out.append("| Arm | 평균 /100 | 중앙값 /100 | 1위 포함 | task | correctness | traceability | restraint | usability |")
    out.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for arm in ARMS:
        arm_rows = [r for r in rows if r["arm"] == arm]
        totals = [r["total"] * 5 for r in arm_rows]
        cells = []
        for criterion in CRITERIA:
            cells.append(f"{statistics.mean(r[criterion] for r in arm_rows):.2f}")
        out.append(
            f"| {arm} | {statistics.mean(totals):.1f} | {statistics.median(totals):.1f} | "
            f"{sum(r['is_first'] for r in arm_rows)}/{len(arm_rows)} | {' | '.join(cells)} |"
        )

    comparable = [v for v in winner_by_bundle.values() if set(v) == {"J55", "J56"}]
    exact = sum(v["J55"] == v["J56"] for v in comparable)
    overlap = sum(bool(v["J55"] & v["J56"]) for v in comparable)
    out.append("\n## Judge 일치도\n")
    out.append(f"- 유효 bundle: {len(comparable)}/18")
    out.append(f"- 1위 집합 완전 일치: {exact}/{len(comparable)}")
    out.append(f"- 1위 후보가 하나 이상 겹침: {overlap}/{len(comparable)}")
    out.append(f"- 파싱/합계 오류: {len(invalid)}")

    (runs / "JUDGE-RESULTS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(runs / "JUDGE-RESULTS.md")
    return 0 if not invalid else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
