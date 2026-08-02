#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ARMS = ("IM-M56-BARE", "IM-M56-ORDINARY", "IM-M56-VERIFIED", "IM-M55-VERIFIED")
TASKS = ("expense-approval", "webhook-delivery", "tenant-search", "config-migration")


def artifact(stem: Path, suffix: str) -> Path:
    return Path(f"{stem}{suffix}")


def load(path: Path):
    spec = importlib.util.spec_from_file_location("fixture_setup", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def order_for(task: str) -> list[str]:
    return sorted(
        ARMS,
        key=lambda arm: hashlib.sha256(
            f"wigtn-delivery-blind:{task}:{arm}".encode()
        ).hexdigest(),
    )


def choose(run_root: Path, arm: str, task: str):
    candidates = []
    for repeat in range(1, 4):
        stem = run_root / arm / f"{task}.{repeat}"
        meta = json.loads(artifact(stem, ".meta.json").read_text())
        state = json.loads(artifact(stem, ".state.json").read_text())
        setup = json.loads(artifact(stem, ".setup.json").read_text())
        integrity = state["test_hashes"] == setup["test_hashes"]
        scope = (
            set(state["changed_paths"]) - {"notes/user-draft.txt"}
        ).issubset(set(setup["source_paths"])) and not state["untracked_paths"]
        quality = (
            meta["hidden_exit"] == 0,
            meta["visible_exit"] == 0,
            integrity,
            scope,
            -meta["patch_lines"],
            -repeat,
        )
        candidates.append((quality, repeat, stem))
    return sorted(candidates, key=lambda row: row[0])[1]


def main(study_arg: str) -> int:
    study = Path(study_arg)
    run_root = study / "implement/runs"
    out = study / "blind/prompts"
    out.mkdir(parents=True, exist_ok=True)
    fixtures = load(study / "implement/setup_repo.py")
    mapping = {}
    human_sections = []
    for task in TASKS:
        selected = {arm: choose(run_root, arm, task) for arm in ARMS}
        labels = {}
        blocks = []
        for label, arm in zip(("A", "B", "C", "D"), order_for(task)):
            quality, repeat, stem = selected[arm]
            labels[label] = arm
            meta = json.loads(artifact(stem, ".meta.json").read_text())
            patch = artifact(stem, ".patch").read_text(errors="ignore")
            blocks.append(
                f"\n## Candidate {label}\n\n"
                f"Visible tests: {'PASS' if meta['visible_exit'] == 0 else 'FAIL'}\n\n"
                f"Hidden tests: {'PASS' if meta['hidden_exit'] == 0 else 'FAIL'}\n\n"
                f"```diff\n{patch}\n```\n"
            )
        base = "\n".join(
            f"### {name}\n```python\n{content}\n```"
            for name, content in fixtures.FILES[task].items()
        )
        task_prompt = fixtures.TASKS[task]["prompt"]
        prompt = f"""You are an independent senior code evaluator.

Four anonymous candidates implemented the same task from the same base repository.
Do not infer model, plugin, or workflow identity. Test results are evidence but do
not replace patch inspection.

Score each candidate 0..4 on:
- completeness: all requested behavior and edge cases are implemented
- correctness: invariants, authorization, security, and failure behavior are sound
- scope_discipline: no unrelated or test-oriented implementation shortcuts
- maintainability: clear, minimal, project-native design
- evidence_quality: implementation and executed-test evidence support the claims

For blocker/high defects, cite a file or identifying diff line and explain impact.
Return JSON only:
{{
  "task": "{task}",
  "candidates": [
    {{
      "label": "A",
      "completeness": 0,
      "correctness": 0,
      "scope_discipline": 0,
      "maintainability": 0,
      "evidence_quality": 0,
      "blockers": [{{"location": "...", "finding": "...", "impact": "..."}}],
      "high": [{{"location": "...", "finding": "...", "impact": "..."}}],
      "summary": "..."
    }}
  ],
  "ranking_best_to_worst": ["A", "B", "C", "D"]
}}

All labels must appear exactly once and all scores must be integers 0..4.

## Task

{task_prompt}

## Base repository

{base}

## Anonymous candidates
{''.join(blocks)}
"""
        (out / f"{task}.txt").write_text(prompt)
        human_sections.append(
            f"# Task: {task}\n\n"
            f"## Request\n\n{task_prompt}\n\n"
            f"## Base repository\n\n{base}\n\n"
            f"## Anonymous candidates\n{''.join(blocks)}\n"
            "## Reviewer scores\n\n"
            "| Candidate | completeness 0–4 | correctness 0–4 | scope 0–4 | "
            "maintainability 0–4 | evidence 0–4 |\n"
            "|---|---:|---:|---:|---:|---:|\n"
            "| A |  |  |  |  |  |\n"
            "| B |  |  |  |  |  |\n"
            "| C |  |  |  |  |  |\n"
            "| D |  |  |  |  |  |\n\n"
            "**Ranking best to worst:**\n\n"
            "**Confidence (low / medium / high):**\n\n"
            "**Blocker/high findings with exact location and impact:**\n\n"
        )
        mapping[task] = {
            "labels": labels,
            "selection": {
                arm: {"repeat": repeat, "quality": list(quality)}
                for arm, (quality, repeat, _stem) in selected.items()
            },
        }
    (study / "blind/BLIND-MAP.json").write_text(
        json.dumps(mapping, indent=2, ensure_ascii=False) + "\n"
    )
    packet = """# Human blind review packet

> Do not open `BLIND-MAP.json`, model logs, or token/duration data before both
> reviewers submit independent scores.

Use `HUMAN-REVIEW-PROTOCOL.md`. Score every candidate 0–4 for completeness,
correctness, scope discipline, maintainability, and evidence quality. A test
PASS is evidence, not permission to skip patch inspection. Cite every
blocker/high finding by exact file or identifying diff line and state its
impact. Submit ranking and confidence independently.

---

""" + "\n\n---\n\n".join(human_sections)
    (study / "blind/HUMAN-REVIEW-PACKET.md").write_text(
        packet, encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
