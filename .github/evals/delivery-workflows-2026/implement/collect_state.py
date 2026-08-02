#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


def run(cwd: Path, *args: str) -> str:
    return subprocess.run(
        list(args), cwd=cwd, text=True, capture_output=True
    ).stdout.strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(repo_arg: str, setup_arg: str) -> int:
    repo = Path(repo_arg)
    setup = json.loads(Path(setup_arg).read_text())
    status = run(repo, "git", "status", "--porcelain=v1")
    changed = run(repo, "git", "diff", "--name-only", "HEAD").splitlines()
    untracked = []
    for line in status.splitlines():
        if line.startswith("?? "):
            name = line[3:]
            if "__pycache__" not in name and not name.endswith(".pyc"):
                untracked.append(name)
    hashes = {}
    for name in setup["test_hashes"]:
        path = repo / name
        if path.exists():
            hashes[name] = sha(path)
    draft = repo / "notes/user-draft.txt"
    state = {
        "head": run(repo, "git", "rev-parse", "HEAD"),
        "changed_paths": sorted(changed),
        "untracked_paths": sorted(untracked),
        "status": status,
        "test_hashes": hashes,
        "draft_hash": sha(draft) if draft.exists() else "",
    }
    print(json.dumps(state, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
