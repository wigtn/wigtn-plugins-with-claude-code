#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
tmp_root="${V2_REGRESSION_TMP_ROOT:-/tmp/wigtn-v2-regression-v1}"
repeat="${V2_REGRESSION_REPEAT:-5}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
current_marketplace="$repo_root/.codex-plugin-staging"
v2_marketplace="$script_dir/candidate-marketplace"
runs="$script_dir/runs-regression"
arms=(M56-BARE M56-CURRENT M56-V2)
fixtures=(
  create-ui-internal
  create-backend-webhook
  create-mobile-expense
  review-contract-clean
  review-missing-applicability
  review-missing-pages
  review-missing-states
  review-missing-flow
  review-missing-acceptance
  review-missing-delivery
  review-universal
)

fixture_path() {
  case "$1" in
    create-*|review-universal)
      printf '%s/.github/evals/model-harness-2026/fixtures/%s.txt' "$repo_root" "$1"
      ;;
    *) printf '%s/fixtures/%s.txt' "$script_dir" "$1" ;;
  esac
}

marketplace_for() {
  case "$1" in
    M56-CURRENT) printf '%s' "$current_marketplace" ;;
    M56-V2) printf '%s' "$v2_marketplace" ;;
    *) printf '%s' "" ;;
  esac
}

test -x "$codex_bin"
test -f "$auth_file"
mkdir -p "$tmp_root" "$runs/prompt-input"
for arm in "${arms[@]}"; do
  mkdir -p "$tmp_root/$arm-home" "$tmp_root/$arm-work" "$runs/$arm"
  ln -sf "$auth_file" "$tmp_root/$arm-home/auth.json"
done

for arm in M56-CURRENT M56-V2; do
  home="$tmp_root/$arm-home"
  marketplace="$(marketplace_for "$arm")"
  if ! CODEX_HOME="$home" "$codex_bin" --disable remote_plugin --disable apps \
    plugin list 2>/dev/null | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
    CODEX_HOME="$home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin marketplace add "$marketplace" --json > "$runs/$arm/setup-marketplace.json"
    CODEX_HOME="$home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/$arm/setup-plugin.json"
  fi
done

if [[ ! -f "$runs/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'codex_cli=%s\nrepeat=%s\nmodel=gpt-5.6-sol\neffort=medium\n' \
      "$("$codex_bin" --version)" "$repeat"
    printf '\n# frozen-input-sha256\n'
    shasum -a 256 \
      "$script_dir/STUDY-PROTOCOL.md" \
      "$script_dir/score_regression.py" \
      "$script_dir/candidate-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/SKILL.md" \
      "$script_dir/candidate-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/references/"*.md \
      "$script_dir/candidate-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/scripts/validate-prd.py" \
      "$script_dir/fixtures/"* \
      "$repo_root/.github/evals/model-harness-2026/fixtures/create-"*.txt \
      "$repo_root/.github/evals/model-harness-2026/fixtures/review-universal.txt"
  } > "$runs/MANIFEST.txt"
fi

for arm in "${arms[@]}"; do
  target="$runs/prompt-input/$arm.json"
  if [[ ! -f "$target" ]]; then
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      -C "$tmp_root/$arm-work" debug prompt-input "PRD를 검토해줘" > "$target"
  fi
done

python3 - "$runs/prompt-input" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1])
bare=(root/"M56-BARE.json").read_text(errors="ignore").casefold()
assert "product-spec" not in bare and "wigtn-plugins-with-codex" not in bare
for arm in ("M56-CURRENT","M56-V2"):
    assert "product-spec" in (root/f"{arm}.json").read_text(errors="ignore").casefold()
print("prompt-input isolation: PASS")
PY

run_one() {
  local arm="$1" fixture="$2" index="$3"
  local output="$runs/$arm/$fixture.$index.md"
  local log="$runs/$arm/$fixture.$index.log"
  local meta="$runs/$arm/$fixture.$index.meta"
  local started finished rc
  [[ -s "$output" && -f "$meta" ]] && return 0
  started="$(date +%s)"
  set +e
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" \
    --disable remote_plugin --disable apps \
    -a never -m gpt-5.6-sol -c 'model_reasoning_effort="medium"' \
    -s read-only -C "$tmp_root/$arm-work" \
    exec --ephemeral --ignore-rules --skip-git-repo-check \
    -o "$output" - < "$(fixture_path "$fixture")" > "$log" 2>&1
  rc=$?
  set -e
  finished="$(date +%s)"
  {
    printf 'arm=%s\nfixture=%s\nrepeat=%s\n' "$arm" "$fixture" "$index"
    printf 'model=gpt-5.6-sol\nreasoning_effort=medium\n'
    printf 'duration_seconds=%s\nexit_code=%s\n' "$((finished-started))" "$rc"
  } > "$meta"
  [[ "$rc" -eq 0 ]] || return "$rc"
}

run_arm() {
  local arm="$1" fixture index pid
  local arm_status=0
  local batch_pids=()
  for fixture in "${fixtures[@]}"; do
    for ((index=1; index<=repeat; index++)); do
      run_one "$arm" "$fixture" "$index" &
      batch_pids+=("$!")
      if [[ "${#batch_pids[@]}" -ge 2 ]]; then
        for pid in "${batch_pids[@]}"; do
          wait "$pid" || arm_status=1
        done
        batch_pids=()
      fi
    done
  done
  for pid in "${batch_pids[@]}"; do
    wait "$pid" || arm_status=1
  done
  return "$arm_status"
}

status_code=0
pids=()
for arm in "${arms[@]}"; do run_arm "$arm" & pids+=("$!"); done
for pid in "${pids[@]}"; do wait "$pid" || status_code=1; done
[[ "$status_code" -eq 0 ]] || exit "$status_code"
python3 "$script_dir/score_regression.py" "$runs"
