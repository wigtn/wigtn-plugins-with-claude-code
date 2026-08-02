#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUNS = ROOT / "runs"
ARMS = ("AR-M56-BARE", "AR-M56-REFORMED", "AR-M55-REFORMED")
TASKS = (
    "game-timeline",
    "game-path",
    "home-youtube",
    "home-usage-url",
    "plugin-gate-command",
    "plugin-manifest-contract",
)
SEED = "wigtn-actual-repos-2026-blind-v1"


def artifact(stem: Path, suffix: str) -> Path:
    return Path(f"{stem}{suffix}")


def candidate(arm: str, task: str, repeat: int) -> dict:
    stem = RUNS / arm / f"{task}.{repeat}"
    setup = json.loads(artifact(stem, ".setup.json").read_text())
    state = json.loads(artifact(stem, ".state.json").read_text())
    meta = json.loads(artifact(stem, ".meta.json").read_text())
    changed = set(state["changed_paths"]) - {"notes/eval-user-draft.txt"}
    return {
        "arm": arm,
        "task": task,
        "repeat": repeat,
        "stem": str(stem.relative_to(ROOT)),
        "prompt": setup["prompt"],
        "hidden": meta["hidden_exit"] == 0,
        "visible": meta["visible_exit"] == 0,
        "integrity": state["frozen_hashes"] == setup["frozen_hashes"],
        "scope": changed.issubset(set(setup["allowed_paths"]))
        and set(state["untracked_paths"]).issubset(set(setup["allowed_paths"])),
        "patch_lines": meta["patch_lines"],
        "patch": artifact(stem, ".patch").read_text(errors="replace"),
    }


def median(arm: str, task: str) -> dict:
    rows = [candidate(arm, task, repeat) for repeat in range(1, 4)]
    rows.sort(
        key=lambda row: (
            -int(row["hidden"]),
            -int(row["visible"]),
            -int(row["integrity"]),
            -int(row["scope"]),
            row["patch_lines"],
            row["repeat"],
        )
    )
    return rows[0]


def main() -> int:
    missing = [
        RUNS / arm / f"{task}.3.meta.json"
        for arm in ARMS
        for task in TASKS
        if not (RUNS / arm / f"{task}.3.meta.json").is_file()
    ]
    if missing:
        raise SystemExit("actual-repository runs incomplete; packet not generated")

    mapping: dict[str, dict[str, str]] = {}
    packet = [
        "# Actual-repository human blind packet\n",
        "> Do not open `BLIND-MAP.json`. Follow `HUMAN-REVIEW-PROTOCOL.md`.\n",
    ]
    for task in TASKS:
        rows = [median(arm, task) for arm in ARMS]
        rows.sort(
            key=lambda row: hashlib.sha256(
                f"{SEED}:{task}:{row['arm']}".encode()
            ).hexdigest()
        )
        labels = dict(zip(("A", "B", "C"), rows))
        mapping[task] = {
            label: f"{row['arm']} repeat {row['repeat']}"
            for label, row in labels.items()
        }
        packet += [f"\n## {task}\n", "### Issue\n", rows[0]["prompt"]]
        for label, row in labels.items():
            packet += [
                f"\n### Candidate {label}\n",
                f"- Visible checks: {'PASS' if row['visible'] else 'FAIL'}\n"
                f"- Hidden checks: {'PASS' if row['hidden'] else 'FAIL'}\n"
                f"- Frozen tests: {'intact' if row['integrity'] else 'changed'}\n"
                f"- Scope: {'PASS' if row['scope'] else 'FAIL'}\n",
                "```diff\n",
                row["patch"],
                "```\n",
            ]
        packet += [
            "\n### Reviewer form\n",
            "| Candidate | Completeness | Correctness/safety | Scope | Maintainability | Verification | Total /20 |\n",
            "|---|---:|---:|---:|---:|---:|---:|\n",
            "| A | | | | | | |\n",
            "| B | | | | | | |\n",
            "| C | | | | | | |\n\n",
            "- Preference (A/B/C/Tie):\n- Confidence (low/medium/high):\n"
            "- Blocker/high findings with exact location:\n",
        ]
    (HERE / "BLIND-MAP.json").write_text(
        json.dumps(mapping, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (HERE / "HUMAN-REVIEW-PACKET.md").write_text(
        "".join(packet), encoding="utf-8"
    )
    print(HERE / "HUMAN-REVIEW-PACKET.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
