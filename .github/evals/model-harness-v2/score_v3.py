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

ARMS = ("M56-V3", "M55-V3")
CONTRACTS = ("applicability", "pages", "states", "flow", "acceptance", "delivery")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def tokens(path: Path) -> int | None:
    found = re.findall(
        r"(?:tokens used|total tokens)\s*[:=]?\s*([\d,]+)",
        path.read_text(errors="ignore"),
        re.I,
    )
    return int(found[-1].replace(",", "")) if found else None


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


def main(runs_arg: str) -> int:
    runs = Path(runs_arg)
    study = runs.parent
    regression = load(study / "score_regression.py", "regression")
    v1 = regression.load_v1(study)
    labels = json.loads((study / "fixtures/review-labels.json").read_text())
    validator = (
        study
        / "candidate-v3-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/scripts/validate-prd.py"
    )
    scores = defaultdict(lambda: defaultdict(list))
    durations = defaultdict(list)
    token_values = defaultdict(list)
    for arm in ARMS:
        for output in sorted((runs / arm).glob("*.md")):
            fixture, repeat = output.stem.rsplit(".", 1)
            text = output.read_text(errors="ignore")
            meta = dict(
                line.split("=", 1)
                for line in (runs / arm / f"{fixture}.{repeat}.meta").read_text().splitlines()
                if "=" in line
            )
            durations[arm].append(int(meta["duration_seconds"]))
            value = tokens(runs / arm / f"{fixture}.{repeat}.log")
            if value is not None:
                token_values[arm].append(value)
            if fixture.startswith("create-"):
                scores[arm]["create"].extend(v1.create_checks(fixture, text).values())
            elif fixture == "review-universal":
                scores[arm]["universal"].extend(robust_universal(v1, text).values())
            else:
                audit = regression.parse_contract_audit(text)
                missing = labels[fixture]["missing"]
                scores[arm]["contract-review"].extend(
                    audit.get(contract) == ("missing" if contract == missing else "present")
                    for contract in CONTRACTS
                )
                if missing:
                    scores[arm]["omission-recall"].append(audit.get(missing) == "missing")
                else:
                    scores[arm]["clean-specificity"].append(
                        all(audit.get(contract) == "present" for contract in CONTRACTS)
                    )
    out = [
        "# v3 confirmation results\n",
        "| Arm | create | omission recall | contract review | clean specificity | robust universal | strict validator | tokens median | duration median |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        cells = []
        for family in ("create", "omission-recall", "contract-review", "clean-specificity", "universal"):
            values = scores[arm][family]
            cells.append(
                "N/A" if not values else f"{sum(values)}/{len(values)} ({sum(values)/len(values):.1%})"
            )
        create_outputs = sorted((runs / arm).glob("create-*.md"))
        valid = sum(
            subprocess.run(
                [sys.executable, str(validator), str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
            for path in create_outputs
        )
        cells.append(f"{valid}/{len(create_outputs)} ({valid/len(create_outputs):.1%})")
        out.append(
            f"| {arm} | {' | '.join(cells)} | {statistics.median(token_values[arm]):.0f} | "
            f"{statistics.median(durations[arm]):.0f}s |"
        )
    (runs / "RESULTS.md").write_text("\n".join(out) + "\n")
    print(runs / "RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
