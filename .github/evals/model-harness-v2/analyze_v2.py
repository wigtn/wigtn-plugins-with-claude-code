#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ARMS = ("M56-BARE", "M56-CURRENT", "M56-V2")
COMPARISONS = (
    ("M56-V2", "M56-CURRENT", "v2 − current"),
    ("M56-V2", "M56-BARE", "v2 − bare"),
    ("M56-CURRENT", "M56-BARE", "current − bare"),
)
FAMILIES = ("create", "omission-recall", "contract-review", "clean-specificity", "universal")


def wilson(passed: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    proportion = passed / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    half = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return center - half, center + half


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    weight = index - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def paired_clusters(rows: list[dict[str, str]], family: str, left: str, right: str):
    values = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row["family"] == family and row["arm"] in (left, right):
            key = (row["fixture"], row["repeat"])
            values[key][row["arm"]].append(int(row["passed"]))
    bundles = defaultdict(list)
    for (fixture, repeat), arms in values.items():
        if left not in arms or right not in arms:
            continue
        bundles[fixture].append(
            statistics.mean(arms[left]) - statistics.mean(arms[right])
        )
    return bundles


def cluster_bootstrap(bundles, seed: int = 20260727, draws: int = 10000):
    fixtures = sorted(bundles)
    observed = statistics.mean(value for fixture in fixtures for value in bundles[fixture])
    if len(fixtures) == 1:
        return observed, None, None
    rng = random.Random(seed)
    samples = []
    for _ in range(draws):
        selected = [rng.choice(fixtures) for _ in fixtures]
        samples.append(
            statistics.mean(value for fixture in selected for value in bundles[fixture])
        )
    return observed, percentile(samples, 0.025), percentile(samples, 0.975)


def main(runs_arg: str) -> int:
    runs = Path(runs_arg)
    with (runs / "SCORES.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    out = ["# v2 paired effects\n", "## Arm rates with Wilson intervals\n"]
    out += ["| Family | Arm | Passed | Rate [95% Wilson] |", "|---|---|---:|---:|"]
    for family in FAMILIES:
        for arm in ARMS:
            selected = [int(row["passed"]) for row in rows if row["family"] == family and row["arm"] == arm]
            low, high = wilson(sum(selected), len(selected))
            out.append(
                f"| {family} | {arm} | {sum(selected)}/{len(selected)} | "
                f"{sum(selected)/len(selected):.1%} [{low:.1%}, {high:.1%}] |"
            )

    out += [
        "\n## Paired fixture-cluster bootstrap\n",
        "| Family | Comparison | Δ percentage points [95% cluster bootstrap] | Fixture clusters |",
        "|---|---|---:|---:|",
    ]
    for family in FAMILIES:
        for left, right, label in COMPARISONS:
            bundles = paired_clusters(rows, family, left, right)
            observed, low, high = cluster_bootstrap(bundles)
            interval = (
                f"{observed*100:+.1f} [not estimated: one fixture]"
                if low is None
                else f"{observed*100:+.1f} [{low*100:+.1f}, {high*100:+.1f}]"
            )
            out.append(f"| {family} | {label} | {interval} | {len(bundles)} |")

    (runs / "EFFECTS.md").write_text("\n".join(out) + "\n")
    print(runs / "EFFECTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
