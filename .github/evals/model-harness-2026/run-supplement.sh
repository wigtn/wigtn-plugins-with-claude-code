#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
tmp_root="${HARNESS_STUDY_TMP_ROOT:-/tmp/wigtn-model-harness-study-v1}"
repeat="${HARNESS_STUDY_REPEAT:-2}"
runs_root="$script_dir/runs-supplement"
arms=(M55-CURRENT M56-BARE M56-CURRENT M56-OPT)
fixtures=(review-convention-v2 review-clean-v2)

model_for() {
  [[ "$1" == "M55-CURRENT" ]] && printf '%s' "gpt-5.5" || printf '%s' "gpt-5.6-sol"
}

mkdir -p "$runs_root"
if [[ ! -f "$runs_root/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'codex_cli=%s\n' "$("$codex_bin" --version)"
    printf 'repeat=%s\n' "$repeat"
    printf 'effort=medium\n'
    printf '\n# frozen-input-sha256\n'
    shasum -a 256 "$script_dir/AMENDMENT-01.md" "$script_dir"/fixtures/review-*-v2.txt
  } > "$runs_root/MANIFEST.txt"
fi

run_one() {
  local arm="$1"
  local fixture="$2"
  local index="$3"
  local output="$runs_root/$arm/$fixture.$index.md"
  local log="$runs_root/$arm/$fixture.$index.log"
  local meta="$runs_root/$arm/$fixture.$index.meta"
  local started finished status
  [[ -s "$output" ]] && return 0
  mkdir -p "$runs_root/$arm"
  started="$(date +%s)"
  set +e
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" \
    --disable remote_plugin --disable apps \
    -a never -m "$(model_for "$arm")" -c 'model_reasoning_effort="medium"' \
    -s read-only -C "$tmp_root/$arm-work" \
    exec --ephemeral --ignore-rules --skip-git-repo-check \
    -o "$output" - < "$script_dir/fixtures/$fixture.txt" > "$log" 2>&1
  status=$?
  set -e
  finished="$(date +%s)"
  {
    printf 'arm=%s\nfixture=%s\nrepeat=%s\n' "$arm" "$fixture" "$index"
    printf 'model=%s\nreasoning_effort=medium\n' "$(model_for "$arm")"
    printf 'duration_seconds=%s\nexit_code=%s\n' "$((finished-started))" "$status"
  } > "$meta"
  [[ "$status" -eq 0 ]] || return "$status"
}

run_arm() {
  local arm="$1" fixture index
  for fixture in "${fixtures[@]}"; do
    for ((index=1; index<=repeat; index++)); do
      run_one "$arm" "$fixture" "$index"
    done
  done
}

status=0
pids=()
for arm in "${arms[@]}"; do run_arm "$arm" & pids+=("$!"); done
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
[[ "$status" -eq 0 ]] || exit "$status"
printf 'Supplement complete: %s\n' "$runs_root"
