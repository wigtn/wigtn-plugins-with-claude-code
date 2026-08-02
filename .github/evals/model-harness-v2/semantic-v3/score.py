#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

JUDGES = ("J55", "J56")
ARMS = ("M56-CURRENT", "M56-V2", "M56-V3")
DIMENSIONS = ("completeness", "correctness", "feasibility", "traceability", "concision")


def parse_json(path: Path) -> dict:
    text = path.read_text(errors="ignore").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def main(root_arg: str) -> int:
    root = Path(root_arg)
    mapping = json.loads((root / "BLIND-MAP.json").read_text())
    records = []
    defects = defaultdict(lambda: defaultdict(lambda: {"blocker": [], "high": []}))
    for judge in JUDGES:
        for path in sorted((root / "runs" / judge).glob("*.json")):
            data = parse_json(path)
            fixture = data["fixture"]
            reverse = mapping[fixture]["labels"]
            seen = set()
            for candidate in data["candidates"]:
                label = candidate["label"]
                if label in seen or label not in reverse:
                    raise ValueError(f"invalid label {judge}/{fixture}/{label}")
                seen.add(label)
                arm = reverse[label]
                scores = [int(candidate[key]) for key in DIMENSIONS]
                if any(score < 0 or score > 4 for score in scores):
                    raise ValueError(f"invalid score {judge}/{fixture}/{label}")
                records.append(
                    {
                        "judge": judge,
                        "fixture": fixture,
                        "arm": arm,
                        "scores": scores,
                        "blockers": candidate.get("blockers", []),
                        "high": candidate.get("high", []),
                    }
                )
                defects[fixture][arm]["blocker"].append(
                    len(candidate.get("blockers", []))
                )
                defects[fixture][arm]["high"].append(len(candidate.get("high", [])))
            if seen != {"A", "B", "C"}:
                raise ValueError(f"missing labels {judge}/{fixture}")

    out = [
        "# V3 semantic confirmation results\n",
        "| Arm | semantic /100 | completeness | correctness | feasibility | traceability | concision | judge blockers | judge high |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    summaries = {}
    for arm in ARMS:
        rows = [record for record in records if record["arm"] == arm]
        dimension_means = [
            statistics.mean(record["scores"][index] for record in rows)
            for index in range(len(DIMENSIONS))
        ]
        blockers = sum(len(record["blockers"]) for record in rows)
        high = sum(len(record["high"]) for record in rows)
        total = statistics.mean(sum(record["scores"]) for record in rows) * 5
        summaries[arm] = {
            "semantic": total,
            "dimensions": dict(zip(DIMENSIONS, dimension_means)),
            "blockers": blockers,
            "high": high,
        }
        out.append(
            f"| {arm} | {total:.1f} | "
            + " | ".join(f"{value:.2f}" for value in dimension_means)
            + f" | {blockers} | {high} |"
        )
    v3 = summaries["M56-V3"]
    current = summaries["M56-CURRENT"]
    v2 = summaries["M56-V2"]
    gates = {
        "semantic_noninferiority_vs_current_minus_5": v3["semantic"]
        >= current["semantic"] - 5,
        "concision_not_below_v2": v3["dimensions"]["concision"]
        >= v2["dimensions"]["concision"],
    }
    out.extend(
        [
            "\n## Frozen gates\n",
            "| Gate | Result |",
            "|---|---|",
            *[
                f"| {name} | {'PASS' if passed else 'FAIL'} |"
                for name, passed in gates.items()
            ],
            "\n## Dual-judge defect consensus\n",
        ]
    )
    consensus_blocker = False
    for fixture in sorted(defects):
        for arm in ARMS:
            blockers = defects[fixture][arm]["blocker"]
            high = defects[fixture][arm]["high"]
            blocker_consensus = all(value > 0 for value in blockers)
            consensus_blocker |= arm == "M56-V3" and blocker_consensus
            out.append(
                f"- {fixture} / {arm}: blocker consensus={'yes' if blocker_consensus else 'no'}; "
                f"high consensus={'yes' if all(value > 0 for value in high) else 'no'}; "
                f"counts={blockers}/{high}"
            )
    out.append(
        f"\n- no V3 consensus blocker: {'PASS' if not consensus_blocker else 'FAIL'}"
    )
    (root / "RESULTS.md").write_text("\n".join(out) + "\n")
    print(root / "RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
