#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../.." && pwd)"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
eval_tmp_root="${CODEX56_TMP_ROOT:-/tmp/wigtn-codex56-prd-create-v1}"
model="${CODEX56_MODEL:-gpt-5.6-sol}"
effort="${CODEX56_EFFORT:-high}"
repeat="${CODEX56_REPEAT:-3}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
prompt_file="$script_dir/prompts/prd-create.txt"
patch_file="$script_dir/arms/a2-contract.patch"
runs_root="$script_dir/runs/prd-create"
source_marketplace="$repo_root/.codex-plugin-staging"
a2_marketplace="$eval_tmp_root/a2-marketplace"

if [[ ! -x "$codex_bin" ]]; then
  echo "Codex CLI를 실행할 수 없음: $codex_bin" >&2
  exit 2
fi

if [[ ! -f "$auth_file" ]]; then
  echo "Codex 인증 파일을 찾을 수 없음: $auth_file" >&2
  exit 2
fi

if [[ ! -f "$source_marketplace/.agents/plugins/marketplace.json" ]]; then
  echo "Codex 플러그인 marketplace를 찾을 수 없음: $source_marketplace" >&2
  exit 2
fi

mkdir -p \
  "$eval_tmp_root/a0-home" "$eval_tmp_root/a1-home" "$eval_tmp_root/a2-home" \
  "$eval_tmp_root/a0-work" "$eval_tmp_root/a1-work" "$eval_tmp_root/a2-work" \
  "$runs_root/A0" "$runs_root/A1" "$runs_root/A2" "$runs_root/prompt-input"

for arm in a0 a1 a2; do
  ln -sf "$auth_file" "$eval_tmp_root/$arm-home/auth.json"
done

if [[ ! -d "$a2_marketplace" ]]; then
  cp -R "$source_marketplace" "$a2_marketplace"
  patch -s -p1 -d "$a2_marketplace" < "$patch_file"
fi

if ! CODEX_HOME="$eval_tmp_root/a1-home" "$codex_bin" \
  --disable remote_plugin --disable apps plugin list 2>/dev/null \
  | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
  CODEX_HOME="$eval_tmp_root/a1-home" "$codex_bin" \
    --disable remote_plugin --disable apps \
    plugin marketplace add "$source_marketplace" --json \
    > "$runs_root/A1/setup-marketplace.json"
  CODEX_HOME="$eval_tmp_root/a1-home" "$codex_bin" \
    --disable remote_plugin --disable apps \
    plugin add wigtn-plugins-with-codex@wigtn --json \
    > "$runs_root/A1/setup-plugin.json"
fi

if ! CODEX_HOME="$eval_tmp_root/a2-home" "$codex_bin" \
  --disable remote_plugin --disable apps plugin list 2>/dev/null \
  | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
  CODEX_HOME="$eval_tmp_root/a2-home" "$codex_bin" \
    --disable remote_plugin --disable apps \
    plugin marketplace add "$a2_marketplace" --json \
    > "$runs_root/A2/setup-marketplace.json"
  CODEX_HOME="$eval_tmp_root/a2-home" "$codex_bin" \
    --disable remote_plugin --disable apps \
    plugin add wigtn-plugins-with-codex@wigtn --json \
    > "$runs_root/A2/setup-plugin.json"
fi

capture_prompt_input() {
  local arm="$1"
  local home_dir="$2"
  local work_dir="$3"
  local target="$runs_root/prompt-input/$arm.json"

  if [[ -f "$target" ]]; then
    return
  fi

  CODEX_HOME="$home_dir" "$codex_bin" \
    --disable remote_plugin --disable apps -C "$work_dir" \
    debug prompt-input "$(sed -n '1,8p' "$prompt_file")" > "$target"
}

capture_prompt_input A0 "$eval_tmp_root/a0-home" "$eval_tmp_root/a0-work"
capture_prompt_input A1 "$eval_tmp_root/a1-home" "$eval_tmp_root/a1-work"
capture_prompt_input A2 "$eval_tmp_root/a2-home" "$eval_tmp_root/a2-work"

run_one() {
  local arm="$1"
  local home_dir="$2"
  local work_dir="$3"
  local index="$4"
  local output="$runs_root/$arm/prd.$index.md"
  local log="$runs_root/$arm/prd.$index.log"
  local meta="$runs_root/$arm/prd.$index.meta"
  local started
  local finished
  local status

  if [[ -s "$output" ]]; then
    return
  fi

  started="$(date +%s)"
  set +e
  CODEX_HOME="$home_dir" "$codex_bin" \
    --disable remote_plugin --disable apps \
    -a never -m "$model" -c "model_reasoning_effort=\"$effort\"" \
    -s read-only -C "$work_dir" \
    exec --ephemeral --ignore-rules --skip-git-repo-check \
    -o "$output" - < "$prompt_file" > "$log" 2>&1
  status=$?
  set -e
  finished="$(date +%s)"

  {
    printf 'arm=%s\n' "$arm"
    printf 'model=%s\n' "$model"
    printf 'reasoning_effort=%s\n' "$effort"
    printf 'started_epoch=%s\n' "$started"
    printf 'finished_epoch=%s\n' "$finished"
    printf 'duration_seconds=%s\n' "$((finished - started))"
    printf 'exit_code=%s\n' "$status"
  } > "$meta"

  if [[ "$status" -ne 0 ]]; then
    echo "$arm run $index 실패 — $log 확인" >&2
    return "$status"
  fi
}

run_arm() {
  local arm="$1"
  local home_dir="$2"
  local work_dir="$3"
  local index

  for ((index = 1; index <= repeat; index++)); do
    run_one "$arm" "$home_dir" "$work_dir" "$index"
  done
}

run_arm A0 "$eval_tmp_root/a0-home" "$eval_tmp_root/a0-work" &
pid_a0=$!
run_arm A1 "$eval_tmp_root/a1-home" "$eval_tmp_root/a1-work" &
pid_a1=$!
run_arm A2 "$eval_tmp_root/a2-home" "$eval_tmp_root/a2-work" &
pid_a2=$!

status=0
wait "$pid_a0" || status=1
wait "$pid_a1" || status=1
wait "$pid_a2" || status=1

if [[ "$status" -ne 0 ]]; then
  exit "$status"
fi

python3 "$script_dir/../score_prd.py" \
  "$runs_root/A0" "$runs_root/A1" "$runs_root/A2" \
  > "$runs_root/RESULT.md"

python3 "$script_dir/score_prd_contract.py" \
  "$runs_root/A0" "$runs_root/A1" "$runs_root/A2" \
  > "$runs_root/RESULT-CONTRACT.md"

printf '완료: %s\n' "$runs_root/RESULT.md"
