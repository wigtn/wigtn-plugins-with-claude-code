#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
tmp_root="${HARNESS_STUDY_TMP_ROOT:-/tmp/wigtn-model-harness-study-v1}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
prompt_root="$script_dir/judge-prompts"
runs_root="$script_dir/judge-runs"

python3 "$script_dir/make_blind_prompts.py" "$script_dir"
mkdir -p "$runs_root"

for judge in J55 J56; do
  mkdir -p "$tmp_root/$judge-home" "$tmp_root/$judge-work" "$runs_root/$judge"
  ln -sf "$auth_file" "$tmp_root/$judge-home/auth.json"
done

if [[ ! -f "$runs_root/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'codex_cli=%s\n' "$("$codex_bin" --version)"
    printf 'effort=medium\n'
    printf '\n# judge-protocol-and-prompt-sha256\n'
    shasum -a 256 "$script_dir/JUDGE-PROTOCOL.md" "$script_dir/make_blind_prompts.py" \
      "$prompt_root/blind-map.json" "$prompt_root"/*.txt
  } > "$runs_root/MANIFEST.txt"
fi

model_for() {
  [[ "$1" == "J55" ]] && printf '%s' "gpt-5.5" || printf '%s' "gpt-5.6-sol"
}

run_one() {
  local judge="$1"
  local prompt="$2"
  local key
  local output log meta started finished status
  key="$(basename "$prompt" .txt)"
  output="$runs_root/$judge/$key.json"
  log="$runs_root/$judge/$key.log"
  meta="$runs_root/$judge/$key.meta"
  [[ -s "$output" ]] && return 0
  started="$(date +%s)"
  set +e
  CODEX_HOME="$tmp_root/$judge-home" "$codex_bin" \
    --disable remote_plugin --disable apps \
    -a never -m "$(model_for "$judge")" -c 'model_reasoning_effort="medium"' \
    -s read-only -C "$tmp_root/$judge-work" \
    exec --ephemeral --ignore-rules --skip-git-repo-check \
    -o "$output" - < "$prompt" > "$log" 2>&1
  status=$?
  set -e
  finished="$(date +%s)"
  {
    printf 'judge=%s\nmodel=%s\nfixture_repeat=%s\n' "$judge" "$(model_for "$judge")" "$key"
    printf 'duration_seconds=%s\nexit_code=%s\n' "$((finished-started))" "$status"
  } > "$meta"
  [[ "$status" -eq 0 ]] || return "$status"
}

run_judge() {
  local judge="$1" prompt
  for prompt in "$prompt_root"/*.txt; do run_one "$judge" "$prompt"; done
}

status=0
run_judge J55 & pid55=$!
run_judge J56 & pid56=$!
wait "$pid55" || status=1
wait "$pid56" || status=1
[[ "$status" -eq 0 ]] || exit "$status"
printf 'Judge runs complete: %s\n' "$runs_root"
