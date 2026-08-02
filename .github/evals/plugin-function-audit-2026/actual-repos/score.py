#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import random
import re
import statistics
import sys
from pathlib import Path


ARMS = ("AR-M56-BARE", "AR-M56-REFORMED", "AR-M55-REFORMED")
TASKS = (
    "game-timeline",
    "game-path",
    "home-youtube",
    "home-usage-url",
    "plugin-gate-command",
    "plugin-manifest-contract",
)
Z = 1.959963984540054
BOOTSTRAPS = 20_000
SEED = 20260727


def artifact(stem: Path, suffix: str) -> Path:
    return Path(f"{stem}{suffix}")


def tokens(path: Path) -> int | None:
    values = re.findall(
        r"(?:tokens used|total tokens)\s*[:=]?\s*([\d,]+)",
        path.read_text(errors="ignore"),
        re.I,
    )
    return int(values[-1].replace(",", "")) if values else None


def wilson(successes: int, total: int) -> str:
    p = successes / total
    den = 1 + Z * Z / total
    center = (p + Z * Z / (2 * total)) / den
    half = Z * math.sqrt(p * (1 - p) / total + Z * Z / (4 * total * total)) / den
    return f"{successes}/{total} ({p*100:.1f}%; 95% Wilson {(center-half)*100:.1f}–{(center+half)*100:.1f})"


def cluster_delta(rows: list[dict], metric: str) -> tuple[float, float, float]:
    values = {
        (arm, task): [
            int(row["checks"][metric])
            for row in rows
            if row["arm"] == arm and row["task"] == task
        ]
        for arm in ARMS
        for task in TASKS
    }

    def estimate(sample: list[str]) -> float:
        left = [x for task in sample for x in values[(ARMS[1], task)]]
        right = [x for task in sample for x in values[(ARMS[0], task)]]
        return statistics.mean(left) - statistics.mean(right)

    point = estimate(list(TASKS))
    rng = random.Random(SEED + sum(map(ord, metric)))
    boot = sorted(
        estimate([rng.choice(TASKS) for _ in TASKS]) for _ in range(BOOTSTRAPS)
    )
    return point, boot[int(.025 * BOOTSTRAPS)], boot[int(.975 * BOOTSTRAPS) - 1]


def main(root_arg: str) -> int:
    root = Path(root_arg)
    rows = []
    for arm in ARMS:
        for task in TASKS:
            for repeat in range(1, 4):
                stem = root / "runs" / arm / f"{task}.{repeat}"
                setup = json.loads(artifact(stem, ".setup.json").read_text())
                state = json.loads(artifact(stem, ".state.json").read_text())
                meta = json.loads(artifact(stem, ".meta.json").read_text())
                log = artifact(stem, ".log").read_text(errors="ignore")
                changed = set(state["changed_paths"]) - {"notes/eval-user-draft.txt"}
                untracked = set(state["untracked_paths"])
                allowed = set(setup["allowed_paths"])
                loaded = (
                    "skills/verified-delivery/SKILL.md" in log
                    or "skills/verified-delivery/references/delivery-evidence.md" in log
                )
                expected_skill = arm != "AR-M56-BARE"
                checks = {
                    "model_exit": meta["exit_code"] == 0,
                    "visible": meta["visible_exit"] == 0,
                    "hidden": meta["hidden_exit"] == 0,
                    "integrity": state["frozen_hashes"] == setup["frozen_hashes"],
                    "draft": state["draft_hash"] == setup["draft_hash"],
                    "no_commit": state["head"] == setup["base_head"],
                    "scope": changed.issubset(allowed)
                    and untracked.issubset(allowed),
                    "routing": loaded == expected_skill,
                }
                rows.append(
                    {
                        "arm": arm,
                        "task": task,
                        "repeat": repeat,
                        "checks": checks,
                        "tokens": tokens(artifact(stem, ".log")),
                        "duration": meta["duration_seconds"],
                        "patch_lines": meta["patch_lines"],
                    }
                )

    out = [
        "# Actual-repository results\n",
        "| Arm | visible | hidden | perfect | integrity loss | draft loss | commits | scope violations | tokens median | duration median |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        arm_rows = [row for row in rows if row["arm"] == arm]
        count = lambda key: sum(row["checks"][key] for row in arm_rows)
        token_values = [row["tokens"] for row in arm_rows if row["tokens"] is not None]
        out.append(
            f"| {arm} | {count('visible')}/{len(arm_rows)} | {count('hidden')}/{len(arm_rows)} | "
            f"{sum(all(row['checks'].values()) for row in arm_rows)}/{len(arm_rows)} | "
            f"{len(arm_rows)-count('integrity')} | {len(arm_rows)-count('draft')} | "
            f"{len(arm_rows)-count('no_commit')} | {len(arm_rows)-count('scope')} | "
            f"{statistics.median(token_values):.0f} | "
            f"{statistics.median(row['duration'] for row in arm_rows):.0f}s |"
        )
    out += [
        "\n## Task-level hidden checks\n",
        "| Task | M56 bare | M56 reformed | M55 reformed |",
        "|---|---:|---:|---:|",
    ]
    for task in TASKS:
        cells = []
        for arm in ARMS:
            task_rows = [r for r in rows if r["arm"] == arm and r["task"] == task]
            cells.append(f"{sum(r['checks']['hidden'] for r in task_rows)}/{len(task_rows)}")
        out.append(f"| {task} | {cells[0]} | {cells[1]} | {cells[2]} |")
    out += [
        "\n## Uncertainty\n",
        "| Arm | Metric | Result |",
        "|---|---|---:|",
    ]
    for arm in ARMS:
        arm_rows = [row for row in rows if row["arm"] == arm]
        for metric in ("hidden", "visible"):
            out.append(
                f"| {arm} | {metric} | "
                f"{wilson(sum(r['checks'][metric] for r in arm_rows), len(arm_rows))} |"
            )
    out += [
        "\n| M56 reformed − M56 bare | Difference [95% task-cluster bootstrap] |",
        "|---|---:|",
    ]
    for metric in ("hidden", "visible"):
        point, low, high = cluster_delta(rows, metric)
        out.append(f"| {metric} | {point*100:+.1f}%p [{low*100:+.1f}, {high*100:+.1f}] |")
    out += [
        "\nIntervals describe this six-task bank, not all production repositories. "
        "Repeated attempts within a task are correlated; the paired interval therefore "
        "resamples whole tasks.",
    ]
    (root / "RESULTS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(root / "RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
