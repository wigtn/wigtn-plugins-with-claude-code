#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"
git -C "$root" status --short
git -C "$root" diff --stat
git -C "$root" diff --cached --stat
