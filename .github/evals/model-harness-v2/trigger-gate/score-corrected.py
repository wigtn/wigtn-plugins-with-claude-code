#!/usr/bin/env python3
"""Post-hoc marker correction for the frozen trigger scorer."""

from __future__ import annotations

import sys
from pathlib import Path

MARKERS = {
    "product-spec": ("# Product Spec", "# PRD Create Contract", "# PRD Review Contract"),
    "screen-spec": ("# Screen Spec",),
    "acceptance-verifier": ("# Acceptance Verifier", "# Evidence Matrix"),
    "design-direction": ("# Design Direction",),
    "handdrawn-diagram": ("# Handdrawn Diagram", "# Hand-drawn Diagram"),
    "wigtn-presentation": ("# WIGTN Presentation",),
    "release-readiness": ("# Release Readiness", "# Git Safety"),
    "verified-delivery": ("# Verified Delivery",),
}


def main(root_arg: str) -> int:
    root = Path(root_arg)
    rows = []
    tp = tn = fp = fn = 0
    for meta in sorted(root.glob("*.meta"), key=lambda path: int(path.name.split(".", 1)[0])):
        index, expected, _ = meta.name.split(".", 2)
        log = (root / f"{index}.{expected}.log").read_text(errors="ignore").casefold()
        loaded = [
            skill
            for skill, markers in MARKERS.items()
            if any(marker.casefold() in log for marker in markers)
        ]
        actual = loaded[0] if len(loaded) == 1 else ("none" if not loaded else "ambiguous")
        passed = actual == expected
        if expected == "none":
            tn += passed
            fp += not passed
        else:
            tp += passed
            fn += not passed
        rows.append((index, expected, actual, passed))
    out = [
        "# v2 live trigger gate — corrected marker adjudication\n",
        "> Post-hoc correction: the frozen scorer omitted the actual `# Hand-drawn Diagram` title.",
        "",
        "| # | Expected | Actual | Result |",
        "|---:|---|---|---|",
    ]
    out += [
        f"| {index} | {expected} | {actual} | {'PASS' if passed else 'FAIL'} |"
        for index, expected, actual, passed in rows
    ]
    out += [
        f"\n- positive recall: {tp}/{tp+fn} ({tp/(tp+fn):.1%})",
        f"- negative specificity: {tn}/{tn+fp} ({tn/(tn+fp):.1%})",
    ]
    (root / "RESULTS-CORRECTED.md").write_text("\n".join(out) + "\n")
    print(root / "RESULTS-CORRECTED.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
