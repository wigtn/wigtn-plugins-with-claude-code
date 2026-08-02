#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
study_dir="$(cd "$script_dir/.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${SKILL_BEHAVIOR_TMP_ROOT:-/tmp/wigtn-skill-behavior-v1}"
fixtures="$script_dir/fixtures"; runs="$script_dir/runs"
arms=(M56-BARE M56-V2); repeat=2
python3 "$script_dir/generate_fixtures.py" "$fixtures"
mkdir -p "$tmp_root" "$runs"
for arm in "${arms[@]}"; do mkdir -p "$tmp_root/$arm-home" "$runs/$arm"; ln -sf "$auth_file" "$tmp_root/$arm-home/auth.json"; done
if ! CODEX_HOME="$tmp_root/M56-V2-home" "$codex_bin" --disable remote_plugin --disable apps plugin list 2>/dev/null \
 | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
 CODEX_HOME="$tmp_root/M56-V2-home" "$codex_bin" --disable remote_plugin --disable apps \
  plugin marketplace add "$study_dir/candidate-marketplace" --json > "$runs/M56-V2/setup-marketplace.json"
 CODEX_HOME="$tmp_root/M56-V2-home" "$codex_bin" --disable remote_plugin --disable apps \
  plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/M56-V2/setup-plugin.json"
fi
if [[ ! -f "$runs/MANIFEST.txt" ]]; then
 {
  printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'codex_cli=%s\nrepeat=%s\nmodel=gpt-5.6-sol\neffort=medium\n' "$("$codex_bin" --version)" "$repeat"
  shasum -a 256 "$study_dir/EXTENSION-PROTOCOL.md" "$script_dir/generate_fixtures.py" \
   "$script_dir/score.py" "$fixtures"/*/* \
   "$study_dir/candidate-marketplace/plugins/wigtn-plugins-with-codex/skills/"*/SKILL.md
 } > "$runs/MANIFEST.txt"
fi
tree_hash(){
 find "$1" -type f ! -name TASK.md ! -name '*.pyc' ! -path '*/__pycache__/*' -print0 \
  | sort -z | xargs -0 shasum -a 256 | shasum -a 256 | cut -d' ' -f1
}
run_one(){
 local arm="$1"
 local task="$2"
 local idx="$3"
 local work="$tmp_root/work/$arm/$task-$idx"
 local output="$runs/$arm/$task.$idx.md"
 local log="$runs/$arm/$task.$idx.log"
 local meta="$runs/$arm/$task.$idx.meta"
 [[ -f "$meta" ]] && return 0
 mkdir -p "$(dirname "$work")"; cp -R "$fixtures/$task" "$work"
 if [[ "$task" == release-readiness ]]; then
  (cd "$work" && git init -q && git config user.email eval@example.com && git config user.name Eval \
   && git add baseline.py test_baseline.py && git commit -qm baseline && cp modified.py baseline.py)
 fi
 before="$(tree_hash "$work")"; head_before="$(git -C "$work" rev-parse HEAD 2>/dev/null || true)"
 started="$(date +%s)"; set +e
 CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
  -a never -m gpt-5.6-sol -c 'model_reasoning_effort="medium"' -s workspace-write -C "$work" \
  exec --ephemeral --ignore-rules --skip-git-repo-check -o "$output" - < "$work/TASK.md" > "$log" 2>&1
 model_rc=$?
 test_rc=na
 if [[ "$task" == verified-delivery ]]; then (cd "$work" && python3 -m unittest -q) > "$runs/$arm/$task.$idx.test.log" 2>&1; test_rc=$?; fi
 set -e
 after="$(tree_hash "$work")"; head_after="$(git -C "$work" rev-parse HEAD 2>/dev/null || true)"
 loaded=no; rg -q '# (Acceptance Verifier|Design Direction|Handdrawn Diagram|Hand-drawn Diagram|Release Readiness|Verified Delivery|WIGTN Presentation)' "$log" && loaded=yes
 {
  printf 'arm=%s\ntask=%s\nrepeat=%s\nmodel_exit=%s\ntest_exit=%s\n' "$arm" "$task" "$idx" "$model_rc" "$test_rc"
  printf 'tree_changed=%s\nhead_changed=%s\nskill_loaded=%s\nduration_seconds=%s\n' \
   "$([[ "$before" == "$after" ]] && echo no || echo yes)" \
   "$([[ "$head_before" == "$head_after" ]] && echo no || echo yes)" "$loaded" "$(( $(date +%s)-started ))"
 } > "$meta"
}
run_arm(){ local arm="$1" d task i; for d in "$fixtures"/*; do task="$(basename "$d")"; for ((i=1;i<=repeat;i++)); do run_one "$arm" "$task" "$i"; done; done; }
status_code=0; run_arm M56-BARE & p1=$!; run_arm M56-V2 & p2=$!; wait "$p1" || status_code=1; wait "$p2" || status_code=1
[[ "$status_code" -eq 0 ]] || exit "$status_code"
python3 "$script_dir/score.py" "$runs"
