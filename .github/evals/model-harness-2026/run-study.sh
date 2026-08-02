#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
tmp_root="${HARNESS_STUDY_TMP_ROOT:-/tmp/wigtn-model-harness-study-v1}"
repeat="${HARNESS_STUDY_REPEAT:-2}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
source_marketplace="$repo_root/.codex-plugin-staging"
opt_marketplace="$tmp_root/opt-marketplace"
runs_root="$script_dir/runs"

arms=(M55-CURRENT M56-BARE M56-CURRENT M56-OPT)
fixtures=(
  create-ui-internal
  create-backend-webhook
  create-mobile-expense
  review-universal
  review-convention
  review-clean
  screen-admin
)

model_for() {
  case "$1" in
    M55-CURRENT) printf '%s' "gpt-5.5" ;;
    *) printf '%s' "gpt-5.6-sol" ;;
  esac
}

home_for() {
  printf '%s/%s-home' "$tmp_root" "$1"
}

work_for() {
  printf '%s/%s-work' "$tmp_root" "$1"
}

marketplace_for() {
  case "$1" in
    M55-CURRENT|M56-CURRENT) printf '%s' "$source_marketplace" ;;
    M56-OPT) printf '%s' "$opt_marketplace" ;;
    M56-BARE) printf '%s' "" ;;
  esac
}

test -x "$codex_bin" || { echo "Codex CLI not executable: $codex_bin" >&2; exit 2; }
test -f "$auth_file" || { echo "Codex auth missing: $auth_file" >&2; exit 2; }
test -f "$source_marketplace/.agents/plugins/marketplace.json" || {
  echo "Marketplace missing: $source_marketplace" >&2
  exit 2
}

mkdir -p "$tmp_root" "$runs_root/prompt-input"

if [[ ! -d "$opt_marketplace" ]]; then
  cp -R "$source_marketplace" "$opt_marketplace"
  patch -s -p1 -d "$opt_marketplace" < "$script_dir/arms/optimized.patch"
fi

for arm in "${arms[@]}"; do
  mkdir -p "$(home_for "$arm")" "$(work_for "$arm")" "$runs_root/$arm"
  ln -sf "$auth_file" "$(home_for "$arm")/auth.json"
done

setup_plugin() {
  local arm="$1"
  local marketplace
  local home_dir
  marketplace="$(marketplace_for "$arm")"
  home_dir="$(home_for "$arm")"
  [[ -n "$marketplace" ]] || return 0

  if CODEX_HOME="$home_dir" "$codex_bin" --disable remote_plugin --disable apps \
    plugin list 2>/dev/null | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
    return 0
  fi

  CODEX_HOME="$home_dir" "$codex_bin" --disable remote_plugin --disable apps \
    plugin marketplace add "$marketplace" --json \
    > "$runs_root/$arm/setup-marketplace.json"
  CODEX_HOME="$home_dir" "$codex_bin" --disable remote_plugin --disable apps \
    plugin add wigtn-plugins-with-codex@wigtn --json \
    > "$runs_root/$arm/setup-plugin.json"
}

for arm in M55-CURRENT M56-CURRENT M56-OPT; do
  setup_plugin "$arm"
done

if [[ ! -f "$runs_root/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'codex_cli=%s\n' "$("$codex_bin" --version)"
    printf 'repeat=%s\n' "$repeat"
    printf 'effort=medium\n'
    printf 'source_commit=%s\n' "$(git -C "$repo_root" rev-parse HEAD)"
    printf '\n# frozen-input-sha256\n'
    shasum -a 256 \
      "$script_dir/STUDY-PROTOCOL.md" \
      "$script_dir/PLUGIN-AUDIT.md" \
      "$script_dir/arms/optimized.patch" \
      "$script_dir/score_study.py" \
      "$script_dir"/fixtures/*.txt
  } > "$runs_root/MANIFEST.txt"
fi

capture_prompt_input() {
  local arm="$1"
  local target="$runs_root/prompt-input/$arm.json"
  [[ -f "$target" ]] && return 0
  CODEX_HOME="$(home_for "$arm")" "$codex_bin" \
    --disable remote_plugin --disable apps -C "$(work_for "$arm")" \
    debug prompt-input "PRD를 작성해줘" > "$target"
}

for arm in "${arms[@]}"; do
  capture_prompt_input "$arm"
done

python3 - "$runs_root/prompt-input" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
bare = (root / "M56-BARE.json").read_text(encoding="utf-8", errors="ignore").casefold()
if "product-spec" in bare or "wigtn-plugins-with-codex" in bare:
    raise SystemExit("M56-BARE prompt-input is contaminated by WIGTN plugin")
for name in ("M55-CURRENT", "M56-CURRENT", "M56-OPT"):
    text = (root / f"{name}.json").read_text(encoding="utf-8", errors="ignore").casefold()
    if "product-spec" not in text:
        raise SystemExit(f"{name} prompt-input does not contain product-spec")
print("prompt-input isolation: PASS")
PY

run_one() {
  local arm="$1"
  local fixture="$2"
  local index="$3"
  local model
  local output="$runs_root/$arm/$fixture.$index.md"
  local log="$runs_root/$arm/$fixture.$index.log"
  local meta="$runs_root/$arm/$fixture.$index.meta"
  local started
  local finished
  local status

  [[ -s "$output" ]] && return 0
  model="$(model_for "$arm")"
  started="$(date +%s)"
  set +e
  CODEX_HOME="$(home_for "$arm")" "$codex_bin" \
    --disable remote_plugin --disable apps \
    -a never -m "$model" -c 'model_reasoning_effort="medium"' \
    -s read-only -C "$(work_for "$arm")" \
    exec --ephemeral --ignore-rules --skip-git-repo-check \
    -o "$output" - < "$script_dir/fixtures/$fixture.txt" > "$log" 2>&1
  status=$?
  set -e
  finished="$(date +%s)"

  {
    printf 'arm=%s\n' "$arm"
    printf 'fixture=%s\n' "$fixture"
    printf 'repeat=%s\n' "$index"
    printf 'model=%s\n' "$model"
    printf 'reasoning_effort=medium\n'
    printf 'started_epoch=%s\n' "$started"
    printf 'finished_epoch=%s\n' "$finished"
    printf 'duration_seconds=%s\n' "$((finished - started))"
    printf 'exit_code=%s\n' "$status"
  } > "$meta"

  if [[ "$status" -ne 0 ]]; then
    echo "$arm $fixture.$index failed; inspect $log" >&2
    return "$status"
  fi
}

run_arm() {
  local arm="$1"
  local fixture
  local index
  for fixture in "${fixtures[@]}"; do
    for ((index = 1; index <= repeat; index++)); do
      run_one "$arm" "$fixture" "$index"
    done
  done
}

status=0
pids=()
for arm in "${arms[@]}"; do
  run_arm "$arm" &
  pids+=("$!")
done
for pid in "${pids[@]}"; do
  wait "$pid" || status=1
done
[[ "$status" -eq 0 ]] || exit "$status"

python3 "$script_dir/score_study.py" "$runs_root"
printf 'Study complete: %s\n' "$runs_root/RESULTS.md"
