#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${V2_M55_TMP_ROOT:-/tmp/wigtn-v2-m55-v1}"
runs="$script_dir/runs-55"
repeat="${V2_M55_REPEAT:-5}"
arms=(M55-CURRENT M55-V2)
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
  [[ "$1" == "M55-CURRENT" ]] \
    && printf '%s' "$repo_root/.codex-plugin-staging" \
    || printf '%s' "$script_dir/candidate-marketplace"
}

test -x "$codex_bin"
test -f "$auth_file"
mkdir -p "$tmp_root" "$runs/prompt-input"
for arm in "${arms[@]}"; do
  mkdir -p "$tmp_root/$arm-home" "$tmp_root/$arm-work" "$runs/$arm"
  ln -sf "$auth_file" "$tmp_root/$arm-home/auth.json"
  if ! CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    plugin list 2>/dev/null | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin marketplace add "$(marketplace_for "$arm")" --json > "$runs/$arm/setup-marketplace.json"
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/$arm/setup-plugin.json"
  fi
  if [[ ! -f "$runs/prompt-input/$arm.json" ]]; then
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      -C "$tmp_root/$arm-work" debug prompt-input "PRD를 검토해줘" > "$runs/prompt-input/$arm.json"
  fi
done

python3 - "$runs/prompt-input" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
for arm in ("M55-CURRENT", "M55-V2"):
    text = (root / f"{arm}.json").read_text(errors="ignore").casefold()
    assert "product-spec" in text and "wigtn-plugins-with-codex" in text
print("prompt-input plugin presence: PASS")
PY

if [[ ! -f "$runs/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'codex_cli=%s\nrepeat=%s\nmodel=gpt-5.5\neffort=medium\n' \
      "$("$codex_bin" --version)" "$repeat"
    shasum -a 256 \
      "$script_dir/STUDY-PROTOCOL.md" "$script_dir/EXTENSION-PROTOCOL.md" "$script_dir/score_55.py" \
      "$script_dir/candidate-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/SKILL.md" \
      "$script_dir/candidate-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/references/"*.md \
      "$script_dir/fixtures/"* \
      "$repo_root/.github/evals/model-harness-2026/fixtures/create-"*.txt \
      "$repo_root/.github/evals/model-harness-2026/fixtures/review-universal.txt"
  } > "$runs/MANIFEST.txt"
fi

run_one() {
  local arm="$1" fixture="$2" index="$3"
  local output="$runs/$arm/$fixture.$index.md"
  local log="$runs/$arm/$fixture.$index.log"
  local meta="$runs/$arm/$fixture.$index.meta"
  local started rc
  [[ -s "$output" && -f "$meta" ]] && return 0
  started="$(date +%s)"
  set +e
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" \
    --disable remote_plugin --disable apps \
    -a never -m gpt-5.5 -c 'model_reasoning_effort="medium"' \
    -s read-only -C "$tmp_root/$arm-work" \
    exec --ephemeral --ignore-rules --skip-git-repo-check \
    -o "$output" - < "$(fixture_path "$fixture")" > "$log" 2>&1
  rc=$?
  set -e
  {
    printf 'arm=%s\nfixture=%s\nrepeat=%s\n' "$arm" "$fixture" "$index"
    printf 'model=gpt-5.5\nreasoning_effort=medium\n'
    printf 'duration_seconds=%s\nexit_code=%s\n' "$(( $(date +%s)-started ))" "$rc"
  } > "$meta"
  [[ "$rc" -eq 0 ]]
}

run_arm() {
  local arm="$1" fixture index pid arm_status=0
  local batch_pids=()
  for fixture in "${fixtures[@]}"; do
    for ((index=1; index<=repeat; index++)); do
      run_one "$arm" "$fixture" "$index" &
      batch_pids+=("$!")
      if [[ "${#batch_pids[@]}" -ge 2 ]]; then
        for pid in "${batch_pids[@]}"; do wait "$pid" || arm_status=1; done
        batch_pids=()
      fi
    done
  done
  for pid in "${batch_pids[@]}"; do wait "$pid" || arm_status=1; done
  return "$arm_status"
}

status_code=0
run_arm M55-CURRENT & p1=$!
run_arm M55-V2 & p2=$!
wait "$p1" || status_code=1
wait "$p2" || status_code=1
[[ "$status_code" -eq 0 ]] || exit "$status_code"
python3 "$script_dir/score_55.py" "$runs"
