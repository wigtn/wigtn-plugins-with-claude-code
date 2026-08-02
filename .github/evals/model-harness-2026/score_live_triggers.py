#!/usr/bin/env python3
"""Inspect Codex logs for skill bodies loaded during live trigger cases."""

from __future__ import annotations

import sys
from pathlib import Path


MARKERS = {
    "product-spec": ("# Product Spec", "# PRD Template", "# PRD Review Checklist"),
    "screen-spec": ("# Screen Spec", "# Screen Specification"),
    "acceptance-verifier": ("# Acceptance Verifier", "# Evidence Matrix"),
    "release-readiness": ("# Release Readiness", "# Git Safety"),
    "design-direction": ("# Design Direction",),
    "handdrawn-diagram": ("# Handdrawn Diagram",),
    "verified-delivery": ("# Verified Delivery",),
    "wigtn-presentation": ("# WIGTN Presentation",),
}


def main(root_arg: str) -> int:
    root = Path(root_arg)
    out = ["# GPT‑5.6 실제 스킬 트리거 점검\n", "| Case | Expected | Loaded | Result |", "|---:|---|---|---|"]
    passed = 0
    total = 0
    for meta in sorted(root.glob("*.meta"), key=lambda p: int(p.name.split(".", 1)[0])):
        index, expected, _ = meta.name.split(".", 2)
        log = (root / f"{index}.{expected}.log").read_text(encoding="utf-8", errors="ignore")
        loaded = [
            skill
            for skill, markers in MARKERS.items()
            if any(marker.casefold() in log.casefold() for marker in markers)
        ]
        actual = loaded[0] if len(loaded) == 1 else ("none" if not loaded else "ambiguous")
        ok = actual == expected
        passed += ok
        total += 1
        out.append(
            f"| {index} | {expected} | {', '.join(loaded) if loaded else 'none'} | "
            f"{'PASS' if ok else 'FAIL'} |"
        )
    out.append(f"\n**{passed}/{total} passed.**")
    (root / "RESULTS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(root / "RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
