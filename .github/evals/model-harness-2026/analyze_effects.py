#!/usr/bin/env python3
"""Paired cluster-bootstrap effect estimates used by REPORT.md."""

from __future__ import annotations

import csv
import random
import sys
from collections import defaultdict
from pathlib import Path


ARMS = ("M55-CURRENT", "M56-BARE", "M56-CURRENT", "M56-OPT")
PAIRS = (
    ("M56-CURRENT", "M55-CURRENT", "model generation"),
    ("M56-CURRENT", "M56-BARE", "current harness"),
    ("M56-OPT", "M56-CURRENT", "redesign"),
    ("M56-OPT", "M56-BARE", "optimized net"),
)


def bootstrap(
    left: dict[str, float],
    right: dict[str, float],
    *,
    seed: int,
    iterations: int = 10_000,
) -> tuple[float, float, float]:
    keys = sorted(set(left) & set(right))
    observed = sum(left[key] - right[key] for key in keys) / len(keys)
    rng = random.Random(seed)
    samples = []
    for _ in range(iterations):
        draw = [rng.choice(keys) for _ in keys]
        samples.append(sum(left[key] - right[key] for key in draw) / len(draw))
    samples.sort()
    return observed, samples[249], samples[9749]


def main(study_arg: str) -> int:
    study = Path(study_arg)
    primary = list(csv.DictReader((study / "runs/SCORES.csv").open()))
    judges = list(csv.DictReader((study / "judge-runs/JUDGE-SCORES.csv").open()))

    structural_raw: dict[str, dict[str, list[int]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in primary:
        if row["family"] not in {"create", "screen"}:
            continue
        key = f"{row['fixture']}:{row['repeat']}"
        structural_raw[row["arm"]][key].append(int(row["passed"]))
    structural = {
        arm: {key: sum(values) / len(values) for key, values in cells.items()}
        for arm, cells in structural_raw.items()
    }

    judge_raw: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for row in judges:
        judge_raw[row["arm"]][row["bundle"]].append(int(row["total"]) * 5)
    judge = {
        arm: {key: sum(values) / len(values) for key, values in cells.items()}
        for arm, cells in judge_raw.items()
    }

    out = ["# Paired effect estimates\n"]
    out.append(
        "구조 점수는 결함이 확인된 두 리뷰 픽스처를 제외하고 PRD 생성+화면정의만 사용한다. "
        "Judge 점수는 18개 bundle에서 두 judge 평균을 cluster로 사용한다.\n"
    )
    out.append("| Contrast | Structural Δpp [95% bootstrap CI] | Blind quality Δ/100 [95% bootstrap CI] |")
    out.append("|---|---:|---:|")
    for index, (left, right, label) in enumerate(PAIRS):
        s = bootstrap(structural[left], structural[right], seed=20260727 + index)
        j = bootstrap(judge[left], judge[right], seed=20260827 + index)
        out.append(
            f"| {label}: `{left}` − `{right}` | "
            f"{s[0]*100:+.1f} [{s[1]*100:+.1f}, {s[2]*100:+.1f}] | "
            f"{j[0]:+.1f} [{j[1]:+.1f}, {j[2]:+.1f}] |"
        )
    (study / "EFFECTS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(study / "EFFECTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
