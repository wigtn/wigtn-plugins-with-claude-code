#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ARMS = ("IM-M56-BARE", "IM-M56-ORDINARY", "IM-M56-VERIFIED", "IM-M55-VERIFIED")
DIMS = ("completeness", "correctness", "scope_discipline", "maintainability", "evidence_quality")


def parse(path: Path):
    text = path.read_text(errors="ignore")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise
        return json.loads(match.group())


def main(root_arg: str) -> int:
    root = Path(root_arg)
    mapping = json.loads((root / "BLIND-MAP.json").read_text())
    records = []
    consensus = defaultdict(lambda: defaultdict(lambda: {"blocker": [], "high": []}))
    for judge_dir in sorted((root / "runs").glob("J*")):
        for path in sorted(judge_dir.glob("*.json")):
            data = parse(path)
            task = data["task"]
            labels = mapping[task]["labels"]
            seen = set()
            for candidate in data["candidates"]:
                label = candidate["label"]
                if label in seen or label not in labels:
                    raise ValueError(f"invalid label {judge_dir.name}/{task}/{label}")
                seen.add(label)
                scores = [int(candidate[key]) for key in DIMS]
                if any(value < 0 or value > 4 for value in scores):
                    raise ValueError("score out of range")
                arm = labels[label]
                records.append(
                    {
                        "judge": judge_dir.name,
                        "task": task,
                        "arm": arm,
                        "scores": scores,
                        "blockers": candidate.get("blockers", []),
                        "high": candidate.get("high", []),
                    }
                )
                consensus[task][arm]["blocker"].append(len(candidate.get("blockers", [])))
                consensus[task][arm]["high"].append(len(candidate.get("high", [])))
            if seen != {"A", "B", "C", "D"}:
                raise ValueError(f"missing labels {judge_dir.name}/{task}")
    out = [
        "# Blind implementation quality results\n",
        "| Arm | quality /100 | completeness | correctness | scope | maintainability | evidence | blockers | high |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        rows = [row for row in records if row["arm"] == arm]
        means = [
            statistics.mean(row["scores"][index] for row in rows)
            for index in range(len(DIMS))
        ]
        quality = statistics.mean(sum(row["scores"]) for row in rows) * 5
        out.append(
            f"| {arm} | {quality:.1f} | "
            + " | ".join(f"{value:.2f}" for value in means)
            + f" | {sum(len(row['blockers']) for row in rows)} | "
            f"{sum(len(row['high']) for row in rows)} |"
        )
    out.append("\n## Dual-judge consensus\n")
    for task in sorted(consensus):
        for arm in ARMS:
            b = consensus[task][arm]["blocker"]
            h = consensus[task][arm]["high"]
            out.append(
                f"- {task} / {arm}: blocker={'yes' if all(x > 0 for x in b) else 'no'}; "
                f"high={'yes' if all(x > 0 for x in h) else 'no'}; counts={b}/{h}"
            )
    (root / "RESULTS.md").write_text("\n".join(out) + "\n")
    print(root / "RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
