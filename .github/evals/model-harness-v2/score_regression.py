#!/usr/bin/env python3
"""Score the v2 release-gate regression."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path


ARMS = ("M56-BARE", "M56-CURRENT", "M56-V2")
CONTRACTS = ("applicability", "pages", "states", "flow", "acceptance", "delivery")


def load_v1(study: Path):
    path = study.parent / "model-harness-2026/score_study.py"
    spec = importlib.util.spec_from_file_location("v1_score", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def parse_contract_audit(text: str) -> dict[str, str]:
    result = {}
    aliases = {
        "applicability": ("applicability", "적용성"),
        "pages": ("pages", "routes", "페이지", "경로"),
        "states": ("state matrix", "상태 매트릭스", "empty/loading", "빈 상태"),
        "flow": ("mermaid", "user flow", "system flow", "사용자 흐름", "시스템 흐름"),
        "acceptance": ("acceptance", "수용 기준", "precondition", "given"),
        "delivery": ("delivery", "phase", "구현 단계", "출시 단계"),
    }
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        key = cells[0].casefold()
        status = cells[1].casefold()
        name = next(
            (name for name, terms in aliases.items() if any(term in key for term in terms)),
            None,
        )
        if not name:
            continue
        if any(term in status for term in ("missing", "누락", "없음", "필요")):
            result[name] = "missing"
        elif any(term in status for term in ("n/a", "해당 없음", "비해당")):
            result[name] = "na"
        elif any(term in status for term in ("present", "있음", "충족", "존재")):
            result[name] = "present"
    return result


def tokens(log: str) -> int | None:
    found = re.findall(r"(?:tokens used|total tokens)\s*[:=]?\s*([\d,]+)", log, re.I)
    return int(found[-1].replace(",", "")) if found else None


def meta(path: Path) -> dict[str, str]:
    return dict(
        line.split("=", 1)
        for line in path.read_text(errors="ignore").splitlines()
        if "=" in line
    )


def main(runs_arg: str) -> int:
    runs = Path(runs_arg)
    study = runs.parent
    v1 = load_v1(study)
    labels = json.loads((study / "fixtures/review-labels.json").read_text())
    validator = (
        study
        / "candidate-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/scripts/validate-prd.py"
    )
    rows = []
    for arm in ARMS:
        for output in sorted((runs / arm).glob("*.md")):
            fixture, repeat = output.stem.rsplit(".", 1)
            text = output.read_text(errors="ignore")
            m = meta(runs / arm / f"{fixture}.{repeat}.meta")
            log_path = runs / arm / f"{fixture}.{repeat}.log"
            log = log_path.read_text(errors="ignore") if log_path.exists() else ""
            base = {
                "arm": arm,
                "fixture": fixture,
                "repeat": repeat,
                "duration": int(m["duration_seconds"]),
                "tokens": tokens(log) or "",
                "lines": text.count("\n") + 1,
            }
            if fixture.startswith("create-"):
                checks = v1.create_checks(fixture, text)
                for criterion, passed in checks.items():
                    rows.append({**base, "family": "create", "criterion": criterion, "passed": int(passed)})
            elif fixture == "review-universal":
                checks = v1.review_checks("review-universal", text)
                for criterion, passed in checks.items():
                    rows.append({**base, "family": "universal", "criterion": criterion, "passed": int(passed)})
            else:
                audit = parse_contract_audit(text)
                expected_missing = labels[fixture]["missing"]
                for contract in CONTRACTS:
                    expected = "missing" if contract == expected_missing else "present"
                    rows.append(
                        {
                            **base,
                            "family": "contract-review",
                            "criterion": contract,
                            "passed": int(audit.get(contract) == expected),
                        }
                    )
                if expected_missing:
                    rows.append(
                        {
                            **base,
                            "family": "omission-recall",
                            "criterion": expected_missing,
                            "passed": int(audit.get(expected_missing) == "missing"),
                        }
                    )
                else:
                    rows.append(
                        {
                            **base,
                            "family": "clean-specificity",
                            "criterion": "no-missing",
                            "passed": int(all(audit.get(c) == "present" for c in CONTRACTS)),
                        }
                    )

    with (runs / "SCORES.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    summary = defaultdict(lambda: defaultdict(list))
    for row in rows:
        summary[row["arm"]][row["family"]].append(row["passed"])

    out = ["# v2 Release-Gate Results\n"]
    families = ("create", "omission-recall", "contract-review", "clean-specificity", "universal")
    out.append("| Arm | " + " | ".join(families) + " | tokens median | duration median |")
    out.append("|---|" + "---:|" * (len(families) + 2))
    for arm in ARMS:
        cells = []
        for family in families:
            vals = summary[arm][family]
            cells.append(f"{sum(vals)}/{len(vals)} ({sum(vals)/len(vals):.1%})")
        unique = {}
        for row in rows:
            if row["arm"] == arm:
                unique[(row["fixture"], row["repeat"])] = row
        token_values = [int(r["tokens"]) for r in unique.values() if r["tokens"] != ""]
        duration_values = [r["duration"] for r in unique.values()]
        out.append(
            f"| {arm} | {' | '.join(cells)} | {statistics.median(token_values):.0f} | "
            f"{statistics.median(duration_values):.0f}s |"
        )

    # Deterministic validator is meaningful for generated PRDs from every arm.
    import subprocess

    validator_counts = {}
    for arm in ARMS:
        outputs = sorted((runs / arm).glob("create-*.md"))
        passed = sum(
            subprocess.run(
                [sys.executable, str(validator), str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
            for path in outputs
        )
        validator_counts[arm] = (passed, len(outputs))
    out.append("\n## Deterministic validator\n")
    for arm, (passed, total) in validator_counts.items():
        out.append(f"- {arm}: {passed}/{total} ({passed/total:.1%})")

    (runs / "RESULTS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(runs / "RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
