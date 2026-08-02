#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import random
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ARMS = ("M56-BARE", "M56-CURRENT", "M56-V2", "M56-V3")
COMPARISONS = (
    ("M56-V3", "M56-CURRENT", "v3 − current"),
    ("M56-V3", "M56-V2", "v3 − v2"),
    ("M56-V3", "M56-BARE", "v3 − bare"),
)
CONTRACTS = ("applicability", "pages", "states", "flow", "acceptance", "delivery")
FAMILIES = (
    "create",
    "omission-recall",
    "contract-review",
    "clean-specificity",
    "universal",
)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def robust_universal(v1, text: str):
    checks = v1.review_checks("review-universal", text)
    checks["qualitative_nfr"] = checks["qualitative_nfr"] or bool(
        re.search(
            r"(?:성능|NFR|충분히\s*빠).{0,180}"
            r"(?:측정\s*불가능|검증\s*불가능|판정.{0,30}(?:없|불가능)|기준.{0,30}없|정성적)",
            text,
            re.I | re.S,
        )
    )
    return checks


def wilson(passed: int, total: int, z: float = 1.959963984540054):
    proportion = passed / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    half = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / total
            + z * z / (4 * total * total)
        )
        / denominator
    )
    return center - half, center + half


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    weight = index - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def cluster_bootstrap(bundles, seed: int = 20260727, draws: int = 10000):
    fixtures = sorted(bundles)
    observed = statistics.mean(
        value for fixture in fixtures for value in bundles[fixture]
    )
    if len(fixtures) == 1:
        return observed, None, None
    rng = random.Random(seed)
    samples = []
    for _ in range(draws):
        selected = [rng.choice(fixtures) for _ in fixtures]
        samples.append(
            statistics.mean(
                value for fixture in selected for value in bundles[fixture]
            )
        )
    return observed, percentile(samples, 0.025), percentile(samples, 0.975)


def main(study_arg: str) -> int:
    study = Path(study_arg)
    regression = load(study / "score_regression.py", "regression")
    v1 = regression.load_v1(study)
    labels = json.loads((study / "fixtures/review-labels.json").read_text())
    roots = {
        "M56-BARE": study / "runs-regression/M56-BARE",
        "M56-CURRENT": study / "runs-regression/M56-CURRENT",
        "M56-V2": study / "runs-regression/M56-V2",
        "M56-V3": study / "runs-v3/M56-V3",
    }
    records = []
    for arm, root in roots.items():
        for output in sorted(root.glob("*.md")):
            fixture, repeat = output.stem.rsplit(".", 1)
            text = output.read_text(errors="ignore")
            families = {}
            if fixture.startswith("create-"):
                families["create"] = v1.create_checks(fixture, text)
            elif fixture == "review-universal":
                families["universal"] = robust_universal(v1, text)
            else:
                audit = regression.parse_contract_audit(text)
                missing = labels[fixture]["missing"]
                families["contract-review"] = {
                    contract: audit.get(contract)
                    == ("missing" if contract == missing else "present")
                    for contract in CONTRACTS
                }
                if missing:
                    families["omission-recall"] = {
                        missing: audit.get(missing) == "missing"
                    }
                else:
                    families["clean-specificity"] = {
                        "clean": all(
                            audit.get(contract) == "present"
                            for contract in CONTRACTS
                        )
                    }
            for family, checks in families.items():
                for check, passed in checks.items():
                    records.append(
                        {
                            "arm": arm,
                            "fixture": fixture,
                            "repeat": repeat,
                            "family": family,
                            "check": check,
                            "passed": int(passed),
                        }
                    )

    out = [
        "# v3 descriptive effects\n",
        "> Alias-robust scorer; confirmatory gates remain in `V3-PROTOCOL.md`.",
        "\n## Arm rates with Wilson intervals\n",
        "| Family | Arm | Passed | Rate [95% Wilson] |",
        "|---|---|---:|---:|",
    ]
    for family in FAMILIES:
        for arm in ARMS:
            selected = [
                row["passed"]
                for row in records
                if row["family"] == family and row["arm"] == arm
            ]
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
            values = defaultdict(lambda: defaultdict(list))
            for row in records:
                if row["family"] == family and row["arm"] in (left, right):
                    key = (row["fixture"], row["repeat"])
                    values[key][row["arm"]].append(row["passed"])
            bundles = defaultdict(list)
            for (fixture, _repeat), arms in values.items():
                if left in arms and right in arms:
                    bundles[fixture].append(
                        statistics.mean(arms[left])
                        - statistics.mean(arms[right])
                    )
            observed, low, high = cluster_bootstrap(bundles)
            interval = (
                f"{observed * 100:+.1f} [not estimated: one fixture]"
                if low is None
                else f"{observed * 100:+.1f} [{low * 100:+.1f}, {high * 100:+.1f}]"
            )
            out.append(f"| {family} | {label} | {interval} | {len(bundles)} |")
    target = study / "runs-v3/EFFECTS.md"
    target.write_text("\n".join(out) + "\n")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
