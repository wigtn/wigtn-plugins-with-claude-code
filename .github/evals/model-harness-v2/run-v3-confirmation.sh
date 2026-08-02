#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${V3_CONFIRM_TMP_ROOT:-/tmp/wigtn-v3-confirm-v1}"
runs="$script_dir/runs-v3"
repeat=5
arms=(M56-V3 M55-V3)
full_fixtures=(
  create-ui-internal create-backend-webhook create-mobile-expense
  review-contract-clean review-missing-applicability review-missing-pages
  review-missing-states review-missing-flow review-missing-acceptance
  review-missing-delivery review-universal
)
targeted_fixtures=(
  create-ui-internal create-backend-webhook create-mobile-expense review-universal
)

fixture_path() {
  case "$1" in
    create-*|review-universal)
      printf '%s/.github/evals/model-harness-2026/fixtures/%s.txt' "$repo_root" "$1"
      ;;
    *) printf '%s/fixtures/%s.txt' "$script_dir" "$1" ;;
  esac
}
model_for(){ [[ "$1" == M55-V3 ]] && printf 'gpt-5.5' || printf 'gpt-5.6-sol'; }

mkdir -p "$tmp_root" "$runs/prompt-input"
for arm in "${arms[@]}"; do
  mkdir -p "$tmp_root/$arm-home" "$tmp_root/$arm-work" "$runs/$arm"
  ln -sf "$auth_file" "$tmp_root/$arm-home/auth.json"
  if ! CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    plugin list 2>/dev/null | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin marketplace add "$script_dir/candidate-v3-marketplace" --json > "$runs/$arm/setup-marketplace.json"
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/$arm/setup-plugin.json"
  fi
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    -C "$tmp_root/$arm-work" debug prompt-input "PRD를 검토해줘" > "$runs/prompt-input/$arm.json"
done

python3 - "$runs/prompt-input" <<'PY'
from pathlib import Path
import sys
for path in Path(sys.argv[1]).glob("*.json"):
    text = path.read_text(errors="ignore").casefold()
    assert "product-spec" in text and "wigtn-plugins-with-codex" in text
print("v3 prompt-input plugin presence: PASS")
PY

if [[ ! -f "$runs/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'codex_cli=%s\nrepeat=%s\neffort=medium\n' "$("$codex_bin" --version)" "$repeat"
    shasum -a 256 "$script_dir/V3-PROTOCOL.md" "$script_dir/score_v3.py" \
      "$script_dir/candidate-v3-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/SKILL.md" \
      "$script_dir/candidate-v3-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/references/"*.md \
      "$script_dir/candidate-v3-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/scripts/validate-prd.py" \
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
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    -a never -m "$(model_for "$arm")" -c 'model_reasoning_effort="medium"' \
    -s read-only -C "$tmp_root/$arm-work" \
    exec --ephemeral --ignore-rules --skip-git-repo-check \
    -o "$output" - < "$(fixture_path "$fixture")" > "$log" 2>&1
  rc=$?
  set -e
  {
    printf 'arm=%s\nfixture=%s\nrepeat=%s\n' "$arm" "$fixture" "$index"
    printf 'model=%s\nreasoning_effort=medium\n' "$(model_for "$arm")"
    printf 'duration_seconds=%s\nexit_code=%s\n' "$(( $(date +%s)-started ))" "$rc"
  } > "$meta"
  [[ "$rc" -eq 0 ]]
}

run_arm() {
  local arm="$1" fixture index pid status=0
  local batch=()
  local fixtures=()
  if [[ "$arm" == M56-V3 ]]; then fixtures=("${full_fixtures[@]}"); else fixtures=("${targeted_fixtures[@]}"); fi
  for fixture in "${fixtures[@]}"; do
    for ((index=1; index<=repeat; index++)); do
      run_one "$arm" "$fixture" "$index" &
      batch+=("$!")
      if [[ "${#batch[@]}" -ge 2 ]]; then
        for pid in "${batch[@]}"; do wait "$pid" || status=1; done
        batch=()
      fi
    done
  done
  if [[ -n "${batch[0]-}" ]]; then
    for pid in "${batch[@]}"; do wait "$pid" || status=1; done
  fi
  return "$status"
}

status=0
run_arm M56-V3 & p1=$!
run_arm M55-V3 & p2=$!
wait "$p1" || status=1
wait "$p2" || status=1
[[ "$status" -eq 0 ]] || exit "$status"
python3 "$script_dir/score_v3.py" "$runs"
