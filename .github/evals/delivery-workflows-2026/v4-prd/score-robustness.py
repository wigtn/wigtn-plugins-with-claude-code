#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def robust_checks(v1, text: str) -> dict[str, bool]:
    checks = v1.review_checks("review-universal", text)
    checks["qualitative_nfr"] = checks["qualitative_nfr"] or bool(
        re.search(
            r"(?:성능|NFR|충분히\s*빠).{0,220}"
            r"(?:관찰\s*가능한\s*기준.{0,20}(?:아니|없)|"
            r"측정\s*불가능|검증\s*불가능|모호|정량.{0,30}필요|"
            r"p(?:90|95|99)|응답\s*시간)",
            text,
            re.I | re.S,
        )
    )
    return checks


def main(root_arg: str) -> int:
    root = Path(root_arg)
    repo = root.parents[3]
    prior = repo / ".github/evals/model-harness-v2"
    regression = load(prior / "score_regression.py", "regression")
    v1 = regression.load_v1(prior)
    rows = []
    for path in sorted((root / "runs" / "M55-V4R").glob("*.md")):
        checks = robust_checks(v1, path.read_text(errors="ignore"))
        rows.append((path.name, checks))
    if len(rows) != 5:
        raise ValueError(f"expected 5 follow-up outputs, found {len(rows)}")
    total = sum(len(checks) for _, checks in rows)
    passed = sum(sum(checks.values()) for _, checks in rows)
    out = [
        "# GPT-5.5 v4 robustness follow-up",
        "",
        f"- Aggregate: **{passed}/{total} ({passed/total:.1%})**",
        f"- Perfect calls: **{sum(all(c.values()) for _, c in rows)}/{len(rows)}**",
        f"- Gate: **{'PASS' if passed == total else 'FAIL'}**",
        "",
        "| Run | FR contradiction | authorization | qualitative NFR | acceptance | expiry |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, checks in rows:
        out.append(
            f"| {name} | "
            + " | ".join("PASS" if value else "FAIL" for value in checks.values())
            + " |"
        )
    (root / "ROBUSTNESS-RESULTS.md").write_text("\n".join(out) + "\n")
    print(root / "ROBUSTNESS-RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
