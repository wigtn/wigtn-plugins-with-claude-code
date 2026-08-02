#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ARMS = ("M56-BARE", "M56-CURRENT", "M56-V2")
FIXTURES = ("create-ui-internal", "create-backend-webhook", "create-mobile-expense")


def load(path: Path):
    spec = importlib.util.spec_from_file_location("v1_score", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def order_for(fixture: str) -> list[str]:
    return sorted(
        ARMS,
        key=lambda arm: hashlib.sha256(f"wigtn-v2-gold:{fixture}:{arm}".encode()).hexdigest(),
    )


def main(study_arg: str) -> int:
    study = Path(study_arg)
    repo = study.parents[2]
    runs = study / "runs-regression"
    out_dir = study / "semantic-gold/prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    scorer = load(study.parent / "model-harness-2026/score_study.py")
    mapping = {}
    for fixture in FIXTURES:
        selected = {}
        selection_scores = {}
        for arm in ARMS:
            candidates = []
            for path in sorted((runs / arm).glob(f"{fixture}.*.md")):
                checks = scorer.create_checks(fixture, path.read_text(errors="ignore"))
                candidates.append((sum(checks.values()), int(path.stem.rsplit(".", 1)[1]), path))
            if len(candidates) != 5:
                raise RuntimeError(f"{arm}/{fixture}: expected 5 outputs, got {len(candidates)}")
            score, repeat, path = max(candidates, key=lambda row: (row[0], -row[1]))
            selected[arm] = path
            selection_scores[arm] = {"score": score, "repeat": repeat, "total": len(scorer.create_checks(fixture, path.read_text(errors="ignore")))}
        labels = {}
        blocks = []
        for label, arm in zip(("A", "B", "C"), order_for(fixture)):
            labels[label] = arm
            blocks.append(
                f"\n## Candidate {label}\n\n"
                + selected[arm].read_text(errors="ignore")
            )
        brief = (
            repo / ".github/evals/model-harness-2026/fixtures" / f"{fixture}.txt"
        ).read_text(errors="ignore")
        prompt = f"""You are an independent product-specification evaluator.

Compare three anonymous PRDs written from the exact same brief. Do not infer model or harness identity.
Score each candidate from 0 to 4 on:
- completeness: applicable product and delivery contracts are covered
- correctness: requirements do not contradict the brief or invent harmful policy
- feasibility: behavior, data, security, failure modes, and delivery decisions are implementable
- traceability: stable requirements and observable acceptance criteria connect intent to delivery
- concision: useful information density without needless ceremony

Format alone is not quality. Do not reward a heading unless its content is applicable and useful.
For every blocker/high defect, cite the candidate section or a short identifying phrase and explain the impact.
A blocker prevents safe implementation or release. A high defect creates material rework, security, or product risk.

Return JSON only:
{{
  "fixture": "{fixture}",
  "candidates": [
    {{
      "label": "A",
      "completeness": 0,
      "correctness": 0,
      "feasibility": 0,
      "traceability": 0,
      "concision": 0,
      "blockers": [{{"location": "...", "finding": "...", "impact": "..."}}],
      "high": [{{"location": "...", "finding": "...", "impact": "..."}}],
      "summary": "..."
    }}
  ],
  "ranking_best_to_worst": ["A", "B", "C"]
}}

All five scores must be integers 0..4 and all three labels must appear exactly once.

## Source brief

{brief}

## Anonymous candidates
{''.join(blocks)}
"""
        (out_dir / f"{fixture}.txt").write_text(prompt, encoding="utf-8")
        mapping[fixture] = {
            "labels": labels,
            "selection": selection_scores,
            "paths": {arm: str(path) for arm, path in selected.items()},
        }
    (study / "semantic-gold/BLIND-MAP.json").write_text(
        json.dumps(mapping, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
