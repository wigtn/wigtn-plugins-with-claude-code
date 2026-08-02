#!/usr/bin/env python3
"""Post-hoc corrections for cache-only mutations and signature-dot aliases."""

from __future__ import annotations

import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

ARMS = ("M56-BARE", "M56-V2")


def load(path: Path):
    spec = importlib.util.spec_from_file_location("frozen", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def source_intact(fixtures: Path, work: Path, task: str) -> bool:
    fixture = fixtures / task
    if task == "release-readiness":
        expected = {
            "baseline.py": (fixture / "modified.py").read_bytes(),
            "modified.py": (fixture / "modified.py").read_bytes(),
            "test_baseline.py": (fixture / "test_baseline.py").read_bytes(),
            "user-note.txt": (fixture / "user-note.txt").read_bytes(),
        }
    else:
        expected = {
            path.relative_to(fixture).as_posix(): path.read_bytes()
            for path in fixture.rglob("*")
            if path.is_file() and path.name != "TASK.md" and path.suffix != ".pyc"
        }
    actual = {
        path.relative_to(work).as_posix(): path.read_bytes()
        for path in work.rglob("*")
        if path.is_file()
        and path.name != "TASK.md"
        and path.suffix != ".pyc"
        and "__pycache__" not in path.parts
        and ".git" not in path.parts
    }
    return actual == expected


def main(root_arg: str) -> int:
    root = Path(root_arg)
    script_dir = root.parent
    frozen = load(script_dir / "score.py")
    fixtures = script_dir / "fixtures"
    work_root = Path("/tmp/wigtn-skill-behavior-v1/work")
    aggregate = defaultdict(lambda: defaultdict(list))
    for arm in ARMS:
        for meta_path in sorted((root / arm).glob("*.meta")):
            task, repeat, _ = meta_path.name.split(".", 2)
            meta = frozen.fields(meta_path)
            work = work_root / arm / f"{task}-{repeat}"
            if task in ("acceptance-verifier", "design-direction", "release-readiness"):
                meta["tree_changed"] = "no" if source_intact(fixtures, work, task) else "yes"
            text = (root / arm / f"{task}.{repeat}.md").read_text(errors="ignore")
            checks = frozen.checks(task, text, meta)
            if task == "wigtn-presentation":
                lowered = text.casefold()
                checks["dot"] = checks["dot"] or any(
                    marker in lowered
                    for marker in ("signature-dot", "page__dot", "시그니처 점", "signature dot")
                )
            for criterion, passed in checks.items():
                aggregate[arm][task].append(int(passed))

    out = [
        "# Six-skill behavior results — corrected adjudication\n",
        "> Post-hoc corrections: ignore Python bytecode caches in mutation checks; accept semantically equivalent signature-dot names.",
        "",
        "| Task | M56-BARE | M56-V2 |",
        "|---|---:|---:|",
    ]
    for task in sorted(set(aggregate["M56-BARE"]) | set(aggregate["M56-V2"])):
        cells = []
        for arm in ARMS:
            values = aggregate[arm][task]
            cells.append(f"{sum(values)}/{len(values)} ({sum(values)/len(values):.1%})")
        out.append(f"| {task} | {' | '.join(cells)} |")
    for arm in ARMS:
        values = [value for task in aggregate[arm].values() for value in task]
        out.append(f"- {arm} aggregate: {sum(values)}/{len(values)} ({sum(values)/len(values):.1%})")
    (root / "RESULTS-CORRECTED.md").write_text("\n".join(out) + "\n")
    print(root / "RESULTS-CORRECTED.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
