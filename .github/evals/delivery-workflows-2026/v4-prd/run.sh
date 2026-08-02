#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
study_dir="$(cd "$script_dir/.." && pwd)"
repo_root="$(cd "$study_dir/../../.." && pwd)"
fixture_root="$repo_root/.github/evals/model-harness-v2"
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex}"
auth_file="${CODEX_AUTH_FILE:-$HOME/.codex/auth.json}"
tmp_root="${V4_CONFIRM_TMP_ROOT:-/tmp/wigtn-v4-confirm-v2}"
runs="$script_dir/runs"
candidate="$repo_root/.codex-plugin-staging"
arms=(M56-V4 M55-V4)

fixture_path() {
  case "$1" in
    create-*|review-universal)
      printf '%s/.github/evals/model-harness-2026/fixtures/%s.txt' "$repo_root" "$1"
      ;;
    *) printf '%s/fixtures/%s.txt' "$fixture_root" "$1" ;;
  esac
}
model_for(){ [[ "$1" == M55-V4 ]] && printf 'gpt-5.5' || printf 'gpt-5.6-sol'; }
repetitions_for() {
  local arm="$1" fixture="$2"
  if [[ "$arm" == M56-V4 ]]; then
    case "$fixture" in
      review-contract-clean) printf 7 ;;
      *) printf 3 ;;
    esac
  else
    case "$fixture" in
      review-contract-clean) printf 3 ;;
      review-universal) printf 2 ;;
      *) printf 1 ;;
    esac
  fi
}

fixtures=(
  create-ui-internal create-backend-webhook create-mobile-expense
  review-contract-clean review-missing-applicability review-missing-pages
  review-missing-states review-missing-flow review-missing-acceptance
  review-missing-delivery review-universal
)

mkdir -p "$tmp_root" "$runs/prompt-input"
for arm in "${arms[@]}"; do
  mkdir -p "$tmp_root/$arm-home" "$tmp_root/$arm-work" "$runs/$arm"
  ln -sf "$auth_file" "$tmp_root/$arm-home/auth.json"
  if ! CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    plugin list 2>/dev/null | grep -q "wigtn-plugins-with-codex@wigtn.*installed, enabled"; then
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin marketplace add "$candidate" --json > "$runs/$arm/setup-marketplace.json"
    CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
      plugin add wigtn-plugins-with-codex@wigtn --json > "$runs/$arm/setup-plugin.json"
  fi
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    -C "$tmp_root/$arm-work" debug prompt-input "PRD를 검토해줘" > "$runs/prompt-input/$arm.json"
done

python3 - "$runs/prompt-input" "$tmp_root" <<'PY'
from pathlib import Path
import sys
for path in Path(sys.argv[1]).glob("*.json"):
    text=path.read_text(errors="ignore").casefold()
    assert "wigtn-plugins-with-codex:product-spec" in text
    arm = path.stem
    skills = list((Path(sys.argv[2]) / f"{arm}-home" / "plugins" / "cache").glob(
        "**/skills/product-spec/SKILL.md"
    ))
    assert len(skills) == 1
    body = skills[0].read_text(errors="ignore").casefold()
    assert "at most five material findings" in body
    assert "present` means the required artifact exists" in body
print("v4 prompt-input treatment: PASS")
PY

if [[ ! -f "$runs/MANIFEST.txt" ]]; then
  {
    printf 'created_utc=%s\ncodex_cli=%s\neffort=medium\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$("$codex_bin" --version)"
    shasum -a 256 "$script_dir/PROTOCOL.md" "$script_dir/run.sh" "$script_dir/score.py" \
      "$candidate/plugins/wigtn-plugins-with-codex/skills/product-spec/SKILL.md" \
      "$candidate/plugins/wigtn-plugins-with-codex/skills/product-spec/agents/openai.yaml" \
      "$candidate/plugins/wigtn-plugins-with-codex/skills/product-spec/references/"*.md \
      "$candidate/plugins/wigtn-plugins-with-codex/skills/product-spec/scripts/validate-prd.py" \
      "$fixture_root/fixtures/"* \
      "$repo_root/.github/evals/model-harness-2026/fixtures/create-"*.txt \
      "$repo_root/.github/evals/model-harness-2026/fixtures/review-universal.txt"
  } > "$runs/MANIFEST.txt"
fi

run_one(){
  local arm="$1" fixture="$2" rep="$3" stem started rc
  stem="$runs/$arm/$fixture.$rep"
  [[ -s "$stem.md" && -s "$stem.meta.json" ]] && return 0
  started="$(date +%s)"; set +e
  CODEX_HOME="$tmp_root/$arm-home" "$codex_bin" --disable remote_plugin --disable apps \
    -a never -m "$(model_for "$arm")" -c 'model_reasoning_effort="medium"' \
    -s read-only -C "$tmp_root/$arm-work" exec --ephemeral --ignore-rules \
    --skip-git-repo-check -o "$stem.md" - < "$(fixture_path "$fixture")" \
    > "$stem.log" 2>&1
  rc=$?; set -e
  python3 - "$stem.meta.json" "$arm" "$fixture" "$rep" "$rc" "$(( $(date +%s)-started ))" <<'PY'
import json,sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({
 "arm":sys.argv[2],"fixture":sys.argv[3],"repeat":int(sys.argv[4]),
 "exit_code":int(sys.argv[5]),"duration_seconds":int(sys.argv[6])
},indent=2)+"\n")
PY
}

run_arm(){
  local arm="$1" fixture rep count pid status=0 batch=()
  for fixture in "${fixtures[@]}"; do
    count="$(repetitions_for "$arm" "$fixture")"
    for ((rep=1; rep<=count; rep++)); do
      run_one "$arm" "$fixture" "$rep" & batch+=("$!")
      if [[ "${#batch[@]}" -ge 2 ]]; then
        for pid in "${batch[@]}"; do wait "$pid" || status=1; done
        batch=()
      fi
    done
  done
  if [[ "${#batch[@]}" -gt 0 ]]; then
    for pid in "${batch[@]}"; do wait "$pid" || status=1; done
  fi
  return "$status"
}

status=0
run_arm M56-V4 & p1=$!
run_arm M55-V4 & p2=$!
wait "$p1" || status=1
wait "$p2" || status=1
[[ "$status" -eq 0 ]] || exit "$status"
python3 "$script_dir/score.py" "$script_dir"
