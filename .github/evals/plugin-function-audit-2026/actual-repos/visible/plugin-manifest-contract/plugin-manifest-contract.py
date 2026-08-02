#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


root = Path(__file__).resolve().parents[1]
checker = root / ".github" / "scripts" / "check_contracts.py"

text = subprocess.run(
    [sys.executable, str(checker), "--root", str(root)],
    text=True,
    capture_output=True,
)
assert text.returncode == 0 and "통과" in text.stdout

machine = subprocess.run(
    [sys.executable, str(checker), "--root", str(root), "--format", "json"],
    text=True,
    capture_output=True,
)
assert machine.returncode == 0, machine.stdout + machine.stderr
data = json.loads(machine.stdout)
assert data["ok"] is True
assert isinstance(data["checked"], int) and data["checked"] >= 70
assert data["errors"] == []
assert set(data) == {"ok", "checked", "errors"}
print("visible contract JSON cases: PASS")
