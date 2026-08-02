#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
study_dir="$(cd "$script_dir/.." && pwd)"
repo_root="$(cd "$study_dir/../../.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${IMPLEMENTATION_BENCH_TMP_ROOT:-/tmp/wigtn-implementation-bench-v1}"
fixtures="$script_dir/fixtures"
runs="$script_dir/runs"
arms=(M56-BARE M56-CURRENT M56-V2)

python3 "$script_dir/generate_tasks.py" "$fixtures"
mkdir -p "$tmp_root" "$runs"

for arm in "${arms[@]}"; do
  mkdir -p "$tmp_root/$arm-home" "$runs/$arm"
  ln -sf "$auth_file" "$tmp_root/$arm-home/auth.json"
done

setup_plugin() {
  local arm="$1" marketplace="$2"
  local home="$tmp_root/$arm-home"
  if ! CODEX_HOME="$home" "$codex_bin" --disable remote_plugin --disable apps \
    plugin list 2>/dev/null | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
    CODEX_HOME="$home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin marketplace add "$marketplace" --json > "$runs/$arm/setup-marketplace.json"
    CODEX_HOME="$home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/$arm/setup-plugin.json"
  fi
}
setup_plugin M56-CURRENT "$repo_root/.codex-plugin-staging"
setup_plugin M56-V2 "$study_dir/candidate-marketplace"

if [[ ! -f "$runs/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'codex_cli=%s\nmodel=gpt-5.6-sol\neffort=medium\n' "$("$codex_bin" --version)"
    shasum -a 256 "$study_dir/EXTENSION-PROTOCOL.md" "$script_dir/generate_tasks.py" \
      "$script_dir/score.py"
    find "$fixtures" -type f ! -name '*.pyc' -print0 \
      | sort -z | xargs -0 shasum -a 256
  } > "$runs/MANIFEST.txt"
fi

run_one() {
  local arm="$1" task="$2"
  local work="$tmp_root/work/$arm/$task"
  local output="$runs/$arm/$task.out.md"
  local log="$runs/$arm/$task.log"
  local meta="$runs/$arm/$task.meta"
  [[ -f "$meta" ]] && return 0
  mkdir -p "$(dirname "$work")"
  cp -R "$fixtures/$task" "$work"
  test_hash_before="$(shasum -a 256 "$work/test_implementation.py" | cut -d' ' -f1)"
  started="$(date +%s)"
  set +e
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" \
    --disable remote_plugin --disable apps \
    -a never -m gpt-5.6-sol -c 'model_reasoning_effort="medium"' \
    -s workspace-write -C "$work" \
    exec --ephemeral --ignore-rules --skip-git-repo-check \
    -o "$output" - < "$work/TASK.md" > "$log" 2>&1
  model_rc=$?
  (cd "$work" && python3 -m unittest -v) > "$runs/$arm/$task.test.log" 2>&1
  test_rc=$?
  set -e
  test_hash_after="$(shasum -a 256 "$work/test_implementation.py" | cut -d' ' -f1)"
  {
    printf 'arm=%s\ntask=%s\nmodel_exit=%s\ntest_exit=%s\n' "$arm" "$task" "$model_rc" "$test_rc"
    printf 'test_integrity=%s\n' "$([[ "$test_hash_before" == "$test_hash_after" ]] && echo intact || echo modified)"
    printf 'duration_seconds=%s\n' "$(( $(date +%s) - started ))"
    if rg -q '# (Product Spec|Screen Spec|Acceptance Verifier|Release Readiness|Verified Delivery)' "$log"; then
      printf 'wigtn_skill_loaded=yes\n'
    else
      printf 'wigtn_skill_loaded=no\n'
    fi
  } > "$meta"
}

run_arm() {
  local arm="$1" task
  for task_dir in "$fixtures"/*; do
    [[ -d "$task_dir" ]] || continue
    task="$(basename "$task_dir")"
    run_one "$arm" "$task"
  done
}

status_code=0
pids=()
for arm in "${arms[@]}"; do run_arm "$arm" & pids+=("$!"); done
for pid in "${pids[@]}"; do wait "$pid" || status_code=1; done
[[ "$status_code" -eq 0 ]] || exit "$status_code"
python3 "$script_dir/score.py" "$runs"
