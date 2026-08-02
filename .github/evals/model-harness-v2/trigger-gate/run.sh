#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
study_dir="$(cd "$script_dir/.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${V2_TRIGGER_TMP_ROOT:-/tmp/wigtn-v2-trigger-gate-v1}"
runs="$script_dir/runs"
home="$tmp_root/home"
work="$tmp_root/work"
mkdir -p "$home" "$work" "$runs"
ln -sf "$auth_file" "$home/auth.json"
if ! CODEX_HOME="$home" "$codex_bin" --disable remote_plugin --disable apps plugin list 2>/dev/null \
  | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
  CODEX_HOME="$home" "$codex_bin" --disable remote_plugin --disable apps \
    plugin marketplace add "$study_dir/candidate-marketplace" --json > "$runs/setup-marketplace.json"
  CODEX_HOME="$home" "$codex_bin" --disable remote_plugin --disable apps \
    plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/setup-plugin.json"
fi
if [[ ! -f "$runs/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'codex_cli=%s\nmodel=gpt-5.6-sol\neffort=low\n' "$("$codex_bin" --version)"
    shasum -a 256 "$study_dir/EXTENSION-PROTOCOL.md" "$script_dir/prompts.tsv" "$script_dir/score.py" \
      "$study_dir/candidate-marketplace/plugins/wigtn-plugins-with-codex/skills/"*/SKILL.md
  } > "$runs/MANIFEST.txt"
fi

index=0
while IFS=$'\t' read -r expected prompt; do
  index=$((index+1))
  output="$runs/$index.$expected.md"; log="$runs/$index.$expected.log"; meta="$runs/$index.$expected.meta"
  [[ -f "$meta" ]] && continue
  started="$(date +%s)"
  set +e
  printf '%s\n' "$prompt" | CODEX_HOME="$home" "$codex_bin" \
    --disable remote_plugin --disable apps -a never -m gpt-5.6-sol \
    -c 'model_reasoning_effort="low"' -s read-only -C "$work" \
    exec --ephemeral --ignore-rules --skip-git-repo-check -o "$output" - > "$log" 2>&1
  rc=$?
  set -e
  {
    printf 'expected=%s\nexit_code=%s\nduration_seconds=%s\n' "$expected" "$rc" "$(( $(date +%s)-started ))"
  } > "$meta"
  [[ "$rc" -eq 0 ]] || exit "$rc"
done < "$script_dir/prompts.tsv"
python3 "$script_dir/score.py" "$runs"
