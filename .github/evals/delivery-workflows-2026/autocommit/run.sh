#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
study_dir="$(cd "$script_dir/.." && pwd)"
repo_root="$(cd "$study_dir/../../.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${DELIVERY_AC_TMP_ROOT:-/tmp/wigtn-delivery-autocommit-v2}"
runs="$script_dir/runs"
arms=(AC-M56-BARE AC-M56-PLUGIN AC-M55-PLUGIN)
tasks=(commit-scoped secret-untracked prepare-only review-only no-changes failing-check detached-head commit-push push-only vague-complete)

model_for(){ [[ "$1" == AC-M55-PLUGIN ]] && printf 'gpt-5.5' || printf 'gpt-5.6-sol'; }
mkdir -p "$tmp_root" "$runs"
for arm in "${arms[@]}"; do
  mkdir -p "$tmp_root/$arm-home" "$tmp_root/$arm-work" "$runs/$arm"
  ln -sf "$auth_file" "$tmp_root/$arm-home/auth.json"
done
for arm in AC-M56-PLUGIN AC-M55-PLUGIN; do
  if ! CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    plugin list 2>/dev/null | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin marketplace add "$repo_root/.codex-plugin-staging" --json > "$runs/$arm/setup-marketplace.json"
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/$arm/setup-plugin.json"
  fi
done

if [[ ! -f "$runs/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\ncodex_cli=%s\nrepetitions=3\neffort=medium\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$("$codex_bin" --version)"
    shasum -a 256 "$study_dir/PROTOCOL.md" "$script_dir/"*.py "$script_dir/run.sh" \
      "$repo_root/.codex-plugin-staging/plugins/wigtn-plugins-with-codex/skills/release-readiness/"*.md \
      "$repo_root/.codex-plugin-staging/plugins/wigtn-plugins-with-codex/skills/release-readiness/references/"*.md
  } > "$runs/MANIFEST.txt"
fi

run_one(){
  local arm="$1" task="$2" rep="$3" stem repo prompt started rc
  stem="$runs/$arm/$task.$rep"; repo="$tmp_root/$arm-work/$task-$rep"
  [[ -s "$stem.state.json" && -s "$stem.meta.json" ]] && return 0
  python3 "$script_dir/setup_repo.py" "$task" "$repo" > "$stem.setup.json"
  python3 - "$stem.setup.json" "$stem.prompt.txt" <<'PY'
import json,sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text())
Path(sys.argv[2]).write_text(d["prompt"]+"\n",encoding="utf-8")
PY
  started="$(date +%s)"; set +e
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    -a never -m "$(model_for "$arm")" -c 'model_reasoning_effort="medium"' \
    -s danger-full-access -C "$repo" exec --ephemeral --ignore-rules \
    -o "$stem.out.md" - < "$stem.prompt.txt" > "$stem.log" 2>&1
  rc=$?; set -e
  python3 "$script_dir/collect_state.py" "$repo" "$stem.setup.json" > "$stem.state.json"
  python3 - "$stem.meta.json" "$arm" "$task" "$rep" "$rc" "$(( $(date +%s)-started ))" <<'PY'
import json,sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({
 "arm":sys.argv[2],"task":sys.argv[3],"repeat":int(sys.argv[4]),
 "exit_code":int(sys.argv[5]),"duration_seconds":int(sys.argv[6])
},indent=2)+"\n")
PY
}

run_arm(){
  local arm="$1" task rep
  for task in "${tasks[@]}"; do
    for rep in 1 2 3; do run_one "$arm" "$task" "$rep"; done
  done
}
status=0
for arm in "${arms[@]}"; do run_arm "$arm" & done
for pid in $(jobs -p); do wait "$pid" || status=1; done
[[ "$status" -eq 0 ]] || exit "$status"
python3 "$script_dir/score.py" "$script_dir"
