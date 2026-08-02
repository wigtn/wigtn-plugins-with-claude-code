#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


def run(cwd: Path, *args: str) -> tuple[int, str, str]:
    result = subprocess.run(list(args), cwd=cwd, text=True, capture_output=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(repo_arg: str, setup_arg: str) -> int:
    repo = Path(repo_arg)
    setup = json.loads(Path(setup_arg).read_text())
    _, head, _ = run(repo, "git", "rev-parse", "HEAD")
    _, delta, _ = run(repo, "git", "rev-list", "--count", f"{setup['base_head']}..HEAD")
    _, paths, _ = run(repo, "git", "diff", "--name-only", setup["base_head"], "HEAD")
    _, status, _ = run(repo, "git", "status", "--porcelain=v1")
    _, staged, _ = run(repo, "git", "diff", "--cached", "--name-only")
    _, branch, _ = run(repo, "git", "branch", "--show-current")
    _, message, _ = run(repo, "git", "log", "-1", "--pretty=%B")
    hashes = {}
    for name in ("task.txt", "unrelated.txt", "app.py", "test_app.py", "AGENTS.md", ".env"):
        path = repo / name
        if path.exists():
            hashes[name] = sha(path)
    remote_after = ""
    if setup["remote_path"]:
        _, remote_after, _ = run(
            Path(setup["remote_path"]), "git", "rev-parse", "refs/heads/main"
        )
    state = {
        "head": head,
        "head_delta": int(delta or 0),
        "commit_paths": sorted(filter(None, paths.splitlines())),
        "status": status,
        "staged_paths": sorted(filter(None, staged.splitlines())),
        "branch": branch,
        "last_message": message,
        "hashes": hashes,
        "remote_after": remote_after,
    }
    print(json.dumps(state, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
