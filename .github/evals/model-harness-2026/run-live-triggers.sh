#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
tmp_root="${HARNESS_STUDY_TMP_ROOT:-/tmp/wigtn-model-harness-study-v1}"
home_dir="$tmp_root/M56-CURRENT-home"
work_dir="$tmp_root/M56-CURRENT-work"
runs="$script_dir/trigger-live/runs"
mkdir -p "$runs"

index=0
while IFS=$'\t' read -r expected prompt; do
  index=$((index + 1))
  output="$runs/$index.$expected.md"
  log="$runs/$index.$expected.log"
  meta="$runs/$index.$expected.meta"
  [[ -s "$output" ]] && continue
  started="$(date +%s)"
  set +e
  printf '%s\n' "$prompt" | CODEX_HOME="$home_dir" "$codex_bin" \
    --disable remote_plugin --disable apps \
    -a never -m gpt-5.6-sol -c 'model_reasoning_effort="medium"' \
    -s read-only -C "$work_dir" \
    exec --ephemeral --ignore-rules --skip-git-repo-check \
    -o "$output" - > "$log" 2>&1
  status=$?
  set -e
  {
    printf 'expected=%s\nduration_seconds=%s\nexit_code=%s\n' \
      "$expected" "$(( $(date +%s) - started ))" "$status"
  } > "$meta"
  [[ "$status" -eq 0 ]] || exit "$status"
done < "$script_dir/trigger-live/prompts.tsv"

python3 "$script_dir/score_live_triggers.py" "$runs"
