#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
study_dir="$(cd "$script_dir/.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${V2_GOLD_TMP_ROOT:-/tmp/wigtn-v2-semantic-gold-v1}"
runs="$script_dir/runs"
judges=(J55 J56)

python3 "$script_dir/make_prompts.py" "$study_dir"
mkdir -p "$tmp_root/work" "$runs"
for judge in "${judges[@]}"; do
  mkdir -p "$tmp_root/$judge-home" "$runs/$judge"
  ln -sf "$auth_file" "$tmp_root/$judge-home/auth.json"
done
if [[ ! -f "$runs/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'codex_cli=%s\neffort=medium\n' "$("$codex_bin" --version)"
    shasum -a 256 "$study_dir/EXTENSION-PROTOCOL.md" "$script_dir/make_prompts.py" \
      "$script_dir/score.py" "$script_dir/BLIND-MAP.json" "$script_dir/prompts/"*.txt
  } > "$runs/MANIFEST.txt"
fi
model_for(){ [[ "$1" == J55 ]] && printf 'gpt-5.5' || printf 'gpt-5.6-sol'; }
run_judge(){
  local judge="$1" prompt fixture output log meta started rc
  for prompt in "$script_dir/prompts/"*.txt; do
    fixture="$(basename "$prompt" .txt)"
    output="$runs/$judge/$fixture.json"; log="$runs/$judge/$fixture.log"; meta="$runs/$judge/$fixture.meta"
    [[ -s "$output" && -f "$meta" ]] && continue
    started="$(date +%s)"; set +e
    CODEX_HOME="$tmp_root/$judge-home" "$codex_bin" --disable remote_plugin --disable apps \
      -a never -m "$(model_for "$judge")" -c 'model_reasoning_effort="medium"' \
      -s read-only -C "$tmp_root/work" exec --ephemeral --ignore-rules --skip-git-repo-check \
      -o "$output" - < "$prompt" > "$log" 2>&1
    rc=$?; set -e
    {
      printf 'judge=%s\nmodel=%s\nfixture=%s\nexit_code=%s\nduration_seconds=%s\n' \
        "$judge" "$(model_for "$judge")" "$fixture" "$rc" "$(( $(date +%s)-started ))"
    } > "$meta"
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
