#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ARMS = ("M56-V4", "M55-V4")
CONTRACTS = ("applicability", "pages", "states", "flow", "acceptance", "delivery")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def tokens(path: Path) -> int | None:
    values = re.findall(
        r"(?:tokens used|total tokens)\s*[:=]?\s*([\d,]+)",
        path.read_text(errors="ignore"),
        re.I,
    )
    return int(values[-1].replace(",", "")) if values else None


def main(root_arg: str) -> int:
    root = Path(root_arg)
    repo = root.parents[3]
    prior = repo / ".github/evals/model-harness-v2"
    regression = load(prior / "score_regression.py", "regression")
    v1 = regression.load_v1(prior)
    labels = json.loads((prior / "fixtures/review-labels.json").read_text())
    validator = (
        repo
        / ".codex-plugin-staging/plugins/wigtn-plugins-with-codex/skills/"
        "product-spec/scripts/validate-prd.py"
    )
    scores = defaultdict(lambda: defaultdict(list))
    durations = defaultdict(list)
    token_values = defaultdict(list)
    outputs = defaultdict(list)
    for arm in ARMS:
        for output in sorted((root / "runs" / arm).glob("*.md")):
            fixture, _repeat = output.stem.rsplit(".", 1)
            meta = json.loads(output.with_suffix(".meta.json").read_text())
            if meta["exit_code"] != 0:
                raise ValueError(f"model failure: {output}")
            text = output.read_text(errors="ignore")
            outputs[arm].append((fixture, output))
            durations[arm].append(meta["duration_seconds"])
            value = tokens(output.with_suffix(".log"))
            if value is not None:
                token_values[arm].append(value)
            if fixture.startswith("create-"):
                scores[arm]["create"].extend(v1.create_checks(fixture, text).values())
            elif fixture == "review-universal":
                checks = v1.review_checks(fixture, text)
                checks["qualitative_nfr"] = checks["qualitative_nfr"] or bool(
                    re.search(
                        r"(?:성능|NFR|충분히\s*빠).{0,180}"
                        r"(?:측정\s*불가능|검증\s*불가능|판정.{0,30}(?:없|불가능)|"
                        r"기준.{0,30}없|정성적)",
                        text,
                        re.I | re.S,
                    )
                )
                scores[arm]["universal"].extend(checks.values())
            else:
                audit = regression.parse_contract_audit(text)
                missing = labels[fixture]["missing"]
                scores[arm]["contract"].extend(
                    audit.get(contract) == ("missing" if contract == missing else "present")
                    for contract in CONTRACTS
                )
                if missing:
                    scores[arm]["omission"].append(audit.get(missing) == "missing")
                else:
                    scores[arm]["clean"].append(
                        all(audit.get(contract) == "present" for contract in CONTRACTS)
                    )

    out = [
        "# v4 PRD confirmation results\n",
        "| Arm | create | omission recall | contract review | clean specificity | universal | validator | tokens median | duration median |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        cells = []
        for metric in ("create", "omission", "contract", "clean", "universal"):
            values = scores[arm][metric]
            cells.append(f"{sum(values)}/{len(values)} ({sum(values)/len(values):.1%})")
        create = [path for fixture, path in outputs[arm] if fixture.startswith("create-")]
        valid = sum(
            subprocess.run(
                [sys.executable, str(validator), str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
            for path in create
        )
        cells.append(f"{valid}/{len(create)} ({valid/len(create):.1%})")
        out.append(
            f"| {arm} | {' | '.join(cells)} | "
            f"{statistics.median(token_values[arm]):.0f} | "
            f"{statistics.median(durations[arm]):.0f}s |"
        )
    (root / "RESULTS.md").write_text("\n".join(out) + "\n")
    print(root / "RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
