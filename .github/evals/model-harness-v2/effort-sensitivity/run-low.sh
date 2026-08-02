#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
study_dir="$(cd "$script_dir/.." && pwd)"
repo_root="$(cd "$study_dir/../../.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${V2_LOW_TMP_ROOT:-/tmp/wigtn-v2-low-v1}"
runs="$script_dir/runs-low"
repeat=3
fixtures=(
 create-ui-internal create-backend-webhook create-mobile-expense
 review-contract-clean review-missing-applicability review-missing-pages
 review-missing-states review-missing-flow review-missing-acceptance
 review-missing-delivery review-universal
)
fixture_path() {
 case "$1" in
  create-*|review-universal) printf '%s/.github/evals/model-harness-2026/fixtures/%s.txt' "$repo_root" "$1" ;;
  *) printf '%s/fixtures/%s.txt' "$study_dir" "$1" ;;
 esac
}
mkdir -p "$tmp_root/home" "$tmp_root/work" "$runs"
ln -sf "$auth_file" "$tmp_root/home/auth.json"
if ! CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps plugin list 2>/dev/null \
 | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
 CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps \
  plugin marketplace add "$study_dir/candidate-marketplace" --json > "$runs/setup-marketplace.json"
 CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps \
  plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/setup-plugin.json"
fi
if [[ ! -f "$runs/MANIFEST.txt" ]]; then
 {
  printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'codex_cli=%s\nrepeat=%s\nmodel=gpt-5.6-sol\neffort=low\n' "$("$codex_bin" --version)" "$repeat"
  shasum -a 256 "$study_dir/EXTENSION-PROTOCOL.md" "$script_dir/score.py" \
   "$study_dir/candidate-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/SKILL.md" \
   "$study_dir/candidate-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/references/"*.md \
   "$study_dir/fixtures/"* "$repo_root/.github/evals/model-harness-2026/fixtures/create-"*.txt \
   "$repo_root/.github/evals/model-harness-2026/fixtures/review-universal.txt"
 } > "$runs/MANIFEST.txt"
fi
run_one(){
  local fixture="$1" i="$2"
  local output="$runs/$fixture.$i.md"
  local log="$runs/$fixture.$i.log"
  local meta="$runs/$fixture.$i.meta"
  [[ -s "$output" && -f "$meta" ]] && return 0
  started="$(date +%s)"
  set +e
  CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps \
   -a never -m gpt-5.6-sol -c 'model_reasoning_effort="low"' \
   -s read-only -C "$tmp_root/work" exec --ephemeral --ignore-rules --skip-git-repo-check \
   -o "$output" - < "$(fixture_path "$fixture")" > "$log" 2>&1
  rc=$?
  set -e
  {
   printf 'fixture=%s\nrepeat=%s\nmodel=gpt-5.6-sol\nreasoning_effort=low\n' "$fixture" "$i"
   printf 'duration_seconds=%s\nexit_code=%s\n' "$(( $(date +%s)-started ))" "$rc"
  } > "$meta"
  [[ "$rc" -eq 0 ]]
}
status=0
batch=()
for fixture in "${fixtures[@]}"; do
 for ((i=1;i<=repeat;i++)); do
  run_one "$fixture" "$i" &
  batch+=("$!")
  if [[ "${#batch[@]}" -ge 2 ]]; then
   for pid in "${batch[@]}"; do wait "$pid" || status=1; done
   batch=()
  fi
 done
done
for pid in "${batch[@]}"; do wait "$pid" || status=1; done
[[ "$status" -eq 0 ]] || exit "$status"
python3 "$script_dir/score.py" "$study_dir"
