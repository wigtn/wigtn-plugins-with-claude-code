#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
study_dir=$(cd "$script_dir/.." && pwd)
repo_root=$(cd "$study_dir/../../.." && pwd)
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-/Users/hyeonman/.codex/auth.json}"
tmp_root="${ACTUAL_REPO_TMP_ROOT:-/tmp/wigtn-actual-repos-2026}"
runs="$script_dir/runs"
arms=(AR-M56-BARE AR-M56-REFORMED AR-M55-REFORMED)
tasks=(game-timeline game-path home-youtube home-usage-url plugin-gate-command plugin-manifest-contract)

model_for() {
  [ "$1" = AR-M55-REFORMED ] && printf 'gpt-5.5' || printf 'gpt-5.6-sol'
}

mkdir -p "$tmp_root" "$runs/prompt-input"
for arm in "${arms[@]}"; do
  mkdir -p "$tmp_root/$arm-home" "$tmp_root/$arm-work" "$runs/$arm"
  ln -sf "$auth_file" "$tmp_root/$arm-home/auth.json"
done

for arm in AR-M56-REFORMED AR-M55-REFORMED; do
  if ! CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" \
    --disable remote_plugin --disable apps plugin list 2>/dev/null |
    grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"
  then
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" \
      --disable remote_plugin --disable apps \
      plugin marketplace add "$repo_root/.codex-plugin-staging" --json \
      > "$runs/$arm/setup-marketplace.json"
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" \
      --disable remote_plugin --disable apps \
      plugin add wigtn-plugins-with-codex@wigtn --json \
      > "$runs/$arm/setup-plugin.json"
  fi
done

for arm in "${arms[@]}"; do
  probe="기능을 구현하고 검증해줘"
  if [ "$arm" != AR-M56-BARE ]; then
    probe='$wigtn-plugins-with-codex:verified-delivery 기능을 구현하고 검증해줘'
  fi
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    -C "$tmp_root/$arm-work" debug prompt-input "$probe" > "$runs/prompt-input/$arm.json"
done

python3 - "$runs/prompt-input" <<'PY'
import json
import sys
from pathlib import Path
root=Path(sys.argv[1])
entry="- wigtn-plugins-with-codex:verified-delivery:"
for path in root.glob("*.json"):
    text=path.read_text(errors="ignore")
    installed=path.stem != "AR-M56-BARE"
    assert (entry in text) == installed, (path.stem, entry in text, installed)
    messages=json.loads(text)
    user=[
        item.get("text","")
        for message in messages if message.get("role") == "user"
        for item in message.get("content",[]) if isinstance(item,dict)
    ]
    invoked=any(v.lstrip().startswith("$wigtn-plugins-with-codex:verified-delivery") for v in user)
    assert invoked == installed, (path.stem, invoked, installed)
print("actual-repository routing preflight: PASS")
PY

if [ ! -f "$runs/MANIFEST.txt" ]; then
  {
    printf 'created_utc=%s\ncodex_cli=%s\nrepetitions=3\nmodels=gpt-5.6-sol,gpt-5.5\neffort=medium\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$("$codex_bin" --version)"
    shasum -a 256 "$study_dir/PROTOCOL.md" "$study_dir/FUNCTION-MATRIX.md" \
      "$script_dir/"*.py "$script_dir/run.sh" \
      "$script_dir/visible/"*/* "$script_dir/hidden/"* \
      "$repo_root/.codex-plugin-staging/plugins/wigtn-plugins-with-codex/skills/verified-delivery/"*.md \
      "$repo_root/.codex-plugin-staging/plugins/wigtn-plugins-with-codex/skills/verified-delivery/agents/openai.yaml" \
      "$repo_root/.codex-plugin-staging/plugins/wigtn-plugins-with-codex/skills/verified-delivery/references/"*.md
  } > "$runs/MANIFEST.txt"
fi

run_commands() {
  local repo=$1 setup=$2 log=$3
  python3 - "$repo" "$setup" "$log" <<'PY'
import json
import subprocess
import sys
from pathlib import Path
repo=Path(sys.argv[1])
setup=json.loads(Path(sys.argv[2]).read_text())
log=Path(sys.argv[3])
rc=0
with log.open("w") as out:
    for command in setup["visible_commands"]:
        out.write(f"$ {command}\n")
        result=subprocess.run(command,cwd=repo,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        out.write(result.stdout)
        out.write(f"\nexit={result.returncode}\n")
        if result.returncode != 0:
            rc=1
print(rc)
PY
}

run_hidden() {
  local task=$1 repo=$2 log=$3 rc=0
  mkdir -p "$repo/eval-hidden"
  case "$task" in
    game-timeline|game-path)
      cp "$script_dir/hidden/$task.test.ts" "$repo/eval-hidden/$task.test.ts"
      (cd "$repo" && npm test -- --run "eval-hidden/$task.test.ts") > "$log" 2>&1 || rc=$?
      ;;
    home-youtube|home-usage-url)
      cp "$script_dir/hidden/$task.test.mts" "$repo/eval-hidden/$task.test.mts"
      (cd "$repo" && node --experimental-strip-types --test "eval-hidden/$task.test.mts") > "$log" 2>&1 || rc=$?
      ;;
    plugin-gate-command)
      bash "$script_dir/hidden/plugin-gate-command.sh" "$repo" > "$log" 2>&1 || rc=$?
      ;;
    plugin-manifest-contract)
      python3 "$script_dir/hidden/plugin-manifest-contract.py" "$repo" > "$log" 2>&1 || rc=$?
      ;;
  esac
  rm -rf "$repo/eval-hidden"
  printf '%s' "$rc"
}

run_one() {
  local arm=$1 task=$2 rep=$3 stem repo started rc visible_rc hidden_rc patch_lines
  stem="$runs/$arm/$task.$rep"
  repo="$tmp_root/$arm-work/$task-$rep"
  [ -s "$stem.state.json" ] && [ -s "$stem.meta.json" ] && return 0
  python3 "$script_dir/setup_repo.py" "$task" "$repo" > "$stem.setup.json"
  python3 - "$stem.setup.json" "$stem.prompt.txt" "$arm" <<'PY'
import json
import sys
from pathlib import Path
data=json.loads(Path(sys.argv[1]).read_text())
prefix="$wigtn-plugins-with-codex:verified-delivery\n\n" if sys.argv[3] != "AR-M56-BARE" else ""
Path(sys.argv[2]).write_text(prefix+data["prompt"]+"\n",encoding="utf-8")
PY
  started=$(date +%s)
  set +e
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    -a never -m "$(model_for "$arm")" -c 'model_reasoning_effort="medium"' \
    -s workspace-write -C "$repo" exec --ephemeral --ignore-rules \
    -o "$stem.out.md" - < "$stem.prompt.txt" > "$stem.log" 2>&1
  rc=$?
  visible_rc=$(run_commands "$repo" "$stem.setup.json" "$stem.visible.log")
  hidden_rc=$(run_hidden "$task" "$repo" "$stem.hidden.log")
  set -e
  git -C "$repo" diff -- . ':(exclude)notes/eval-user-draft.txt' > "$stem.patch"
  patch_lines=$(wc -l < "$stem.patch" | tr -d ' ')
  python3 "$script_dir/collect_state.py" "$repo" "$stem.setup.json" > "$stem.state.json"
  python3 - "$stem.meta.json" "$arm" "$task" "$rep" "$rc" "$visible_rc" "$hidden_rc" \
    "$(( $(date +%s)-started ))" "$patch_lines" <<'PY'
import json
import sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({
    "arm":sys.argv[2],"task":sys.argv[3],"repeat":int(sys.argv[4]),
    "exit_code":int(sys.argv[5]),"visible_exit":int(sys.argv[6]),
    "hidden_exit":int(sys.argv[7]),"duration_seconds":int(sys.argv[8]),
    "patch_lines":int(sys.argv[9]),
},indent=2)+"\n")
PY
}

run_arm() {
  local arm=$1 task rep
  for task in "${tasks[@]}"; do
    for rep in 1 2 3; do run_one "$arm" "$task" "$rep"; done
  done
}

status=0
for arm in "${arms[@]}"; do run_arm "$arm" & done
for pid in $(jobs -p); do wait "$pid" || status=1; done
[ "$status" -eq 0 ] || exit "$status"
python3 "$script_dir/score.py" "$script_dir"
