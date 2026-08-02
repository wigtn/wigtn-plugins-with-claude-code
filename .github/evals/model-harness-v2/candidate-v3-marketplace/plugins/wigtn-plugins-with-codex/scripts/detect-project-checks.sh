#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"

if test -f "$root/package.json"; then
  echo "JavaScript/TypeScript: inspect package.json scripts for test, typecheck, lint, and build"
fi
test -f "$root/pyproject.toml" && echo "Python: inspect pyproject.toml for pytest, mypy/pyright, ruff, and build configuration"
test -f "$root/Cargo.toml" && echo "Rust: cargo test; cargo clippy; cargo build"
test -f "$root/go.mod" && echo "Go: go test ./...; go vet ./..."
test -f "$root/Makefile" && echo "Makefile detected: prefer documented repository targets"
test -f "$root/justfile" && echo "justfile detected: prefer documented repository recipes"
