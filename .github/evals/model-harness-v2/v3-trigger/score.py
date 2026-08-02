#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

MARKERS = {
    "product-spec": ("# Product Spec", "# PRD Create Contract", "# PRD Review Contract"),
    "screen-spec": ("# Screen Spec",),
    "acceptance-verifier": ("# Acceptance Verifier",),
    "design-direction": ("# Design Direction",),
    "handdrawn-diagram": ("# Handdrawn Diagram", "# Hand-drawn Diagram"),
    "wigtn-presentation": ("# WIGTN Presentation",),
    "release-readiness": ("# Release Readiness",),
    "verified-delivery": ("# Verified Delivery",),
}


def main(root_arg: str) -> int:
    root = Path(root_arg)
    rows = []
    for meta in sorted(root.glob("*.meta"), key=lambda path: int(path.name.split(".", 1)[0])):
        index, expected, _ = meta.name.split(".", 2)
        text = (root / f"{index}.{expected}.log").read_text(errors="ignore").casefold()
        loaded = [
            skill for skill, markers in MARKERS.items()
            if any(marker.casefold() in text for marker in markers)
        ]
        actual = loaded[0] if len(loaded) == 1 else ("none" if not loaded else "ambiguous")
        rows.append((index, expected, actual, expected == actual))
    out = [
        "# v3 targeted trigger results\n",
        "| # | Expected | Actual | Result |", "|---:|---|---|---|",
        *[f"| {i} | {e} | {a} | {'PASS' if ok else 'FAIL'} |" for i, e, a, ok in rows],
    ]
    positives = [ok for _, expected, _, ok in rows if expected != "none"]
    negatives = [ok for _, expected, _, ok in rows if expected == "none"]
    out += [
        f"\n- positive: {sum(positives)}/{len(positives)}",
        f"- negative: {sum(negatives)}/{len(negatives)}",
    ]
    (root / "RESULTS.md").write_text("\n".join(out) + "\n")
    print(root / "RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
