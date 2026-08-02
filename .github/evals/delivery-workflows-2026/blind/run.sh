#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
study_dir="$(cd "$script_dir/.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${DELIVERY_BLIND_TMP_ROOT:-/tmp/wigtn-delivery-blind-v1}"
runs="$script_dir/runs"

python3 "$script_dir/make_prompts.py" "$study_dir"
mkdir -p "$tmp_root/work" "$runs"
for judge in J55 J56; do
  mkdir -p "$tmp_root/$judge-home" "$runs/$judge"
  ln -sf "$auth_file" "$tmp_root/$judge-home/auth.json"
done
if [[ ! -f "$runs/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\ncodex_cli=%s\neffort=medium\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$("$codex_bin" --version)"
    shasum -a 256 "$study_dir/PROTOCOL.md" "$script_dir/"*.py "$script_dir/run.sh" \
      "$script_dir/BLIND-MAP.json" "$script_dir/prompts/"*.txt
  } > "$runs/MANIFEST.txt"
fi
model_for(){ [[ "$1" == J55 ]] && printf 'gpt-5.5' || printf 'gpt-5.6-sol'; }
run_judge(){
  local judge="$1" prompt task stem started rc
  for prompt in "$script_dir/prompts/"*.txt; do
    task="$(basename "$prompt" .txt)"; stem="$runs/$judge/$task"
    [[ -s "$stem.json" && -s "$stem.meta.json" ]] && continue
    started="$(date +%s)"; set +e
    CODEX_HOME="$tmp_root/$judge-home" "$codex_bin" --disable remote_plugin --disable apps \
      -a never -m "$(model_for "$judge")" -c 'model_reasoning_effort="medium"' \
      -s read-only -C "$tmp_root/work" exec --ephemeral --ignore-rules --skip-git-repo-check \
      -o "$stem.json" - < "$prompt" > "$stem.log" 2>&1
    rc=$?; set -e
    python3 - "$stem.meta.json" "$judge" "$task" "$rc" "$(( $(date +%s)-started ))" <<'PY'
import json,sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({
 "judge":sys.argv[2],"task":sys.argv[3],"exit_code":int(sys.argv[4]),
 "duration_seconds":int(sys.argv[5])
},indent=2)+"\n")
PY
    [[ "$rc" -eq 0 ]] || return "$rc"
  done
}
status=0
run_judge J55 & p1=$!
run_judge J56 & p2=$!
wait "$p1" || status=1
wait "$p2" || status=1
[[ "$status" -eq 0 ]] || exit "$status"
python3 "$script_dir/score.py" "$script_dir"
