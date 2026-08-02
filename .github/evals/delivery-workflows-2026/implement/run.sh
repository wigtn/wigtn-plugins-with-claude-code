#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
study_dir="$(cd "$script_dir/.." && pwd)"
repo_root="$(cd "$study_dir/../../.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${DELIVERY_IM_TMP_ROOT:-/tmp/wigtn-delivery-implement-v4}"
runs="$script_dir/runs"
arms=(IM-M56-BARE IM-M56-ORDINARY IM-M56-VERIFIED IM-M55-VERIFIED)
tasks=(expense-approval webhook-delivery tenant-search config-migration)

model_for(){ [[ "$1" == IM-M55-VERIFIED ]] && printf 'gpt-5.5' || printf 'gpt-5.6-sol'; }
mkdir -p "$tmp_root" "$runs/prompt-input"
for arm in "${arms[@]}"; do
  mkdir -p "$tmp_root/$arm-home" "$tmp_root/$arm-work" "$runs/$arm"
  ln -sf "$auth_file" "$tmp_root/$arm-home/auth.json"
done
for arm in IM-M56-ORDINARY IM-M56-VERIFIED IM-M55-VERIFIED; do
  if ! CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    plugin list 2>/dev/null | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin marketplace add "$repo_root/.codex-plugin-staging" --json > "$runs/$arm/setup-marketplace.json"
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/$arm/setup-plugin.json"
  fi
done
for arm in "${arms[@]}"; do
  probe="이 저장소 기능을 구현해줘"
  if [[ "$arm" == IM-M56-VERIFIED || "$arm" == IM-M55-VERIFIED ]]; then
    probe='$wigtn-plugins-with-codex:verified-delivery 기능을 구현하고 검증해줘'
  fi
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    -C "$tmp_root/$arm-work" debug prompt-input "$probe" > "$runs/prompt-input/$arm.json"
done
python3 - "$runs/prompt-input" <<'PY'
import json
from pathlib import Path
import sys
root=Path(sys.argv[1])
entry="- wigtn-plugins-with-codex:verified-delivery:"
for path in root.glob("*.json"):
    text=path.read_text(errors="ignore")
    installed=path.stem != "IM-M56-BARE"
    assert (entry in text) == installed, (path.stem, entry in text, installed)
    messages=json.loads(text)
    user_items=[
        item.get("text","")
        for message in messages if message.get("role") == "user"
        for item in message.get("content",[]) if isinstance(item,dict)
    ]
    invoked=any(
        value.lstrip().startswith("$wigtn-plugins-with-codex:verified-delivery")
        for value in user_items
    )
    expected_invocation=path.stem in {"IM-M56-VERIFIED","IM-M55-VERIFIED"}
    assert invoked == expected_invocation, (path.stem, invoked, expected_invocation)
print("verified-delivery discovery and invocation preflight: PASS")
PY

if [[ ! -f "$runs/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\ncodex_cli=%s\nrepetitions=3\neffort=medium\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$("$codex_bin" --version)"
    shasum -a 256 "$study_dir/PROTOCOL.md" "$script_dir/"*.py "$script_dir/run.sh" \
      "$script_dir/hidden/"*.py \
      "$runs/prompt-input/"*.json \
      "$repo_root/.codex-plugin-staging/plugins/wigtn-plugins-with-codex/skills/verified-delivery/"*.md \
      "$repo_root/.codex-plugin-staging/plugins/wigtn-plugins-with-codex/skills/verified-delivery/agents/openai.yaml" \
      "$repo_root/.codex-plugin-staging/plugins/wigtn-plugins-with-codex/skills/verified-delivery/references/"*.md
  } > "$runs/MANIFEST.txt"
fi

run_one(){
  local arm="$1" task="$2" rep="$3" stem repo prompt started rc visible_rc hidden_rc patch_lines
  stem="$runs/$arm/$task.$rep"; repo="$tmp_root/$arm-work/$task-$rep"
  [[ -s "$stem.state.json" && -s "$stem.meta.json" ]] && return 0
  python3 "$script_dir/setup_repo.py" "$task" "$repo" > "$stem.setup.json"
  python3 - "$stem.setup.json" "$stem.prompt.txt" "$arm" <<'PY'
import json,sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text())
prefix="$wigtn-plugins-with-codex:verified-delivery\n\n" if sys.argv[3] in {"IM-M56-VERIFIED","IM-M55-VERIFIED"} else ""
Path(sys.argv[2]).write_text(prefix+d["prompt"]+"\n",encoding="utf-8")
PY
  started="$(date +%s)"; set +e
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    -a never -m "$(model_for "$arm")" -c 'model_reasoning_effort="medium"' \
    -s workspace-write -C "$repo" exec --ephemeral --ignore-rules \
    -o "$stem.out.md" - < "$stem.prompt.txt" > "$stem.log" 2>&1
  rc=$?
  (cd "$repo" && python3 -m unittest -v) > "$stem.visible.log" 2>&1; visible_rc=$?
  PYTHONPATH="$repo" python3 "$script_dir/hidden/$task.py" > "$stem.hidden.log" 2>&1; hidden_rc=$?
  set -e
  git -C "$repo" diff -- . ':(exclude)notes/user-draft.txt' > "$stem.patch"
  patch_lines="$(wc -l < "$stem.patch" | tr -d ' ')"
  python3 "$script_dir/collect_state.py" "$repo" "$stem.setup.json" > "$stem.state.json"
  python3 - "$stem.meta.json" "$arm" "$task" "$rep" "$rc" "$visible_rc" "$hidden_rc" "$(( $(date +%s)-started ))" "$patch_lines" <<'PY'
import json,sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({
 "arm":sys.argv[2],"task":sys.argv[3],"repeat":int(sys.argv[4]),
 "exit_code":int(sys.argv[5]),"visible_exit":int(sys.argv[6]),
 "hidden_exit":int(sys.argv[7]),"duration_seconds":int(sys.argv[8]),
 "patch_lines":int(sys.argv[9])
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
