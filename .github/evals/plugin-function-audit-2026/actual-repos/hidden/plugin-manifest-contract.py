#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


source = Path(sys.argv[1]).resolve()
checker = source / ".github/scripts/check_contracts.py"


def invoke(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(checker), "--root", str(root), "--format", "json"],
        text=True,
        capture_output=True,
    )


with tempfile.TemporaryDirectory() as raw:
    base = Path(raw)
    clean = invoke(source)
    assert clean.returncode == 0 and clean.stderr == ""
    clean_data = json.loads(clean.stdout)
    assert set(clean_data) == {"ok", "checked", "errors"}
    assert clean_data["ok"] is True and clean_data["errors"] == []

    fixture = base / "broken"
    shutil.copytree(
        source,
        fixture,
        ignore=shutil.ignore_patterns(".git", "node_modules", ".github/evals", "notes"),
    )
    manifest = fixture / "plugins/wigtn-plugins/.claude-plugin/plugin.json"
    data = json.loads(manifest.read_text())
    data["agents"].append(data["agents"][0])
    data["commands"][0] = "./agents/pr-reviewer.md"
    data["skills"] = data["skills"][1:]
    manifest.write_text(json.dumps(data))

    first = invoke(fixture)
    second = invoke(fixture)
    assert first.returncode != 0 and first.stderr == ""
    assert first.stdout == second.stdout
    result = json.loads(first.stdout)
    assert result["ok"] is False
    assert result["checked"] >= 1
    assert len(result["errors"]) >= 3
    for error in result["errors"]:
        assert set(error) == {"code", "path", "message"}
        assert all(isinstance(error[key], str) for key in error)

print("hidden contract JSON cases: PASS")
