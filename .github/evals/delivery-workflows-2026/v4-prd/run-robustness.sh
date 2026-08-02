#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../../.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${V4_ROBUST_TMP_ROOT:-/tmp/wigtn-v4-robustness-v1}"
runs="$script_dir/runs/M55-V4R"
candidate="$repo_root/.codex-plugin-staging"
fixture="$repo_root/.github/evals/model-harness-2026/fixtures/review-universal.txt"

mkdir -p "$tmp_root/home" "$tmp_root/work" "$runs"
ln -sf "$auth_file" "$tmp_root/home/auth.json"
if ! CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps \
  plugin list 2>/dev/null | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
  CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps \
    plugin marketplace add "$candidate" --json > "$runs/setup-marketplace.json"
  CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps \
    plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/setup-plugin.json"
fi

if [[ ! -f "$runs/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\ncodex_cli=%s\nmodel=gpt-5.5\neffort=medium\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$("$codex_bin" --version)"
    shasum -a 256 "$script_dir/ROBUSTNESS-PROTOCOL.md" \
      "$script_dir/run-robustness.sh" "$script_dir/score-robustness.py" \
      "$candidate/plugins/wigtn-plugins-with-codex/skills/product-spec/SKILL.md" \
      "$candidate/plugins/wigtn-plugins-with-codex/skills/product-spec/references/review-contract.md" \
      "$fixture"
  } > "$runs/MANIFEST.txt"
fi

run_one() {
  local repeat="$1" stem="$runs/review-universal.$repeat" started rc
  [[ -s "$stem.md" && -s "$stem.meta.json" ]] && return 0
  started="$(date +%s)"; set +e
  CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps \
    -a never -m gpt-5.5 -c 'model_reasoning_effort="medium"' \
    -s read-only -C "$tmp_root/work" exec --ephemeral --ignore-rules \
    --skip-git-repo-check -o "$stem.md" - < "$fixture" > "$stem.log" 2>&1
  rc=$?; set -e
  python3 - "$stem.meta.json" "$repeat" "$rc" "$(( $(date +%s)-started ))" <<'PY'
import json,sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({
 "arm":"M55-V4R","repeat":int(sys.argv[2]),"exit_code":int(sys.argv[3]),
 "duration_seconds":int(sys.argv[4])
},indent=2)+"\n")
PY
  [[ "$rc" -eq 0 ]]
}

status=0
for start in 1 3 5; do
  batch=()
  for repeat in "$start" "$((start+1))"; do
    [[ "$repeat" -le 5 ]] || continue
    run_one "$repeat" & batch+=("$!")
  done
  for pid in "${batch[@]}"; do wait "$pid" || status=1; done
done
[[ "$status" -eq 0 ]] || exit "$status"
python3 "$script_dir/score-robustness.py" "$script_dir"
