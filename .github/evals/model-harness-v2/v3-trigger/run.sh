#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
study_dir="$(cd "$script_dir/.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${V3_TRIGGER_TMP_ROOT:-/tmp/wigtn-v3-trigger-v1}"
runs="$script_dir/runs"
mkdir -p "$tmp_root/home" "$tmp_root/work" "$runs"
ln -sf "$auth_file" "$tmp_root/home/auth.json"
if ! CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps plugin list 2>/dev/null \
 | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
 CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps \
  plugin marketplace add "$study_dir/candidate-v3-marketplace" --json > "$runs/setup-marketplace.json"
 CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps \
  plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/setup-plugin.json"
fi
if [[ ! -f "$runs/MANIFEST.txt" ]]; then
 {
  printf 'created_utc=%s\nmodel=gpt-5.6-sol\neffort=low\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  shasum -a 256 "$study_dir/V3-PROTOCOL.md" "$script_dir/prompts.tsv" "$script_dir/score.py" \
   "$study_dir/candidate-v3-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/SKILL.md"
 } > "$runs/MANIFEST.txt"
fi
run_one(){
 local index="$1" expected="$2" prompt="$3"
 local output="$runs/$index.$expected.md" log="$runs/$index.$expected.log" meta="$runs/$index.$expected.meta"
 [[ -s "$output" && -f "$meta" ]] && return 0
 started="$(date +%s)"; set +e
 printf '%s\n' "$prompt" | CODEX_HOME="$tmp_root/home" "$codex_bin" --disable remote_plugin --disable apps \
  -a never -m gpt-5.6-sol -c 'model_reasoning_effort="low"' -s read-only -C "$tmp_root/work" \
  exec --ephemeral --ignore-rules --skip-git-repo-check -o "$output" - > "$log" 2>&1
 rc=$?; set -e
 printf 'expected=%s\nexit_code=%s\nduration_seconds=%s\n' "$expected" "$rc" "$(( $(date +%s)-started ))" > "$meta"
 [[ "$rc" -eq 0 ]]
}
index=0; batch=(); status=0
while IFS=$'\t' read -r expected prompt; do
 index=$((index+1)); run_one "$index" "$expected" "$prompt" & batch+=("$!")
 if [[ "${#batch[@]}" -ge 2 ]]; then
  for pid in "${batch[@]}"; do wait "$pid" || status=1; done
  batch=()
 fi
done < "$script_dir/prompts.tsv"
if [[ -n "${batch[0]-}" ]]; then
 for pid in "${batch[@]}"; do wait "$pid" || status=1; done
fi
[[ "$status" -eq 0 ]] || exit "$status"
python3 "$script_dir/score.py" "$runs"
