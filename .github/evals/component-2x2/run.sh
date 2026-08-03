#!/usr/bin/env bash
# 리뷰 컴포넌트 × 모델 세대 2×2.  PROTOCOL.md 를 따른다.  일탈은 ERRATA.md 에.
#
#   bash run.sh        # 40콜 (10 픽스처-반복 × 4셀)
#   DRY=1 bash run.sh  # 계획만
#
# 출력: runs/<model>__<arm>/<fixture>.<n>.txt   ← score.py 가 기대하는 레이아웃 그대로
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
HERE="$REPO/.github/evals/component-2x2"
FIX="$REPO/.github/evals/fixtures"
RUNS="$HERE/runs"
DRY="${DRY:-0}"
TIMEOUT="${TIMEOUT:-600}"

MODELS=(claude-opus-4-8 claude-opus-5)
ARMS=(A0 A1)

# 전역 활성 플러그인 전부 OFF (P-6: enabledPlugins 는 병합이다. 키는 name@marketplace)
PLUGINS_OFF='{"enabledPlugins":{"wigtn-plugins@wigtn-plugins":false,"prd@wigtn-plugins":false,"implement@wigtn-plugins":false,"public-commands@wigtn-plugins":false,"frontend-development@wigtn-plugins":false,"backend-development@wigtn-plugins":false,"mobile-development@wigtn-plugins":false,"ai-development@wigtn-plugins":false}}'

# 픽스처: 파일명 / 반복수 / 리뷰어 에이전트 / 깨끗한가
SPECS=(
  "prd-defective.md 3 prd-reviewer  dirty"
  "code-defective.ts 3 code-reviewer dirty"
  "prd-clean.md      2 prd-reviewer  clean"
  "code-clean.ts     2 code-reviewer clean"
)

run_with_timeout() { local s="$1"; shift; "$@" & local p=$!; ( sleep "$s"; kill -9 "$p" 2>/dev/null ) & local w=$!
  wait "$p" 2>/dev/null; local rc=$?; kill -9 "$w" 2>/dev/null; wait "$w" 2>/dev/null; return $rc; }

# 프롬프트 — README.md 의 기존 실행 규약을 그대로 따른다.
#  ① 픽스처 절대경로 + 리뷰 프로토콜대로  ② severity JSON 블록  ③ 깨끗한 픽스처엔 근거없는 감점 금지
# A0/A1 차이는 **리뷰어를 누가 수행하는가**뿐이다. 과제 문구는 동일하다.
build_prompt() { # $1=픽스처경로 $2=에이전트 $3=clean/dirty $4=arm
  local common="아래 파일을 리뷰해서 문제를 전부 찾아라.

파일: $1

요구사항:
- 모든 지적에 파일 경로/라인 또는 문서 섹션 번호를 증거로 단다.
- 마지막에 반드시 JSON 블록을 낸다: {\"findings\":[{\"severity\":\"critical|major|minor|info\",\"where\":\"...\",\"what\":\"...\"}]}"
  if [ "$3" = "clean" ]; then
    common="$common
- 이 파일은 문제가 없을 수도 있다. **근거 없는 감점을 하지 마라.** 실제 결함만 보고한다."
  fi
  if [ "$4" = "A1" ]; then
    printf '%s' "$common

리뷰는 반드시 subagent_type \"wigtn-local:$2\" 서브에이전트를 띄워 그 에이전트의 리뷰 프로토콜대로 수행하고, 그 결과를 그대로 출력한다."
  else
    printf '%s' "$common"
  fi
}

echo "== 컴포넌트 2x2 =="
echo "  모델 ${MODELS[*]} / arm ${ARMS[*]}"
echo "  픽스처: prd-defective(3) code-defective(3) prd-clean(2) code-clean(2) = 10/셀 -> 40콜"
[ "$DRY" = "1" ] && exit 0
command -v claude >/dev/null || { echo "claude CLI 없음"; exit 1; }

# ── 처치 arm 검증 (E-05 재발 방지) ──────────────────────────────────────
# --plugin-dir 로 올린 플러그인은 PLUGINS_OFF 와 이름이 겹치면 같이 꺼진다.
# 스테이징 사본을 wigtn-local 로 리네임해 충돌을 없애고, 실행 전에 실제로
# 로드되는지 확인한다. 안 보이면 시작하지 않는다 (처치 없이 40콜 태우는 사고 방지).
# 사본을 시작 시점에 뜨므로 실행 중 플러그인을 수정해도 처치가 흔들리지 않는다(동결).
STAGE="$HERE/.stage/wigtn-local"
rm -rf "$(dirname "$STAGE")"; mkdir -p "$(dirname "$STAGE")"
cp -r "$REPO/plugins/wigtn-plugins" "$STAGE"
python3 - "$STAGE" <<'PYEOF'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]) / ".claude-plugin" / "plugin.json"
d = json.loads(p.read_text()); d["name"] = "wigtn-local"
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
PYEOF

pw="$(mktemp -d)"
probe=$( cd "$pw" && claude -p "List every skill name available to you right now, one per line." \
   --model "${MODELS[0]}" --settings "$PLUGINS_OFF" --plugin-dir "$STAGE" --allowedTools Read < /dev/null 2>&1 )
rm -rf "$pw"
if printf '%s' "$probe" | grep -q "wigtn-local:"; then echo "처치 검증 ok"; else
  echo "ABORT — A1 에 플러그인이 로드되지 않는다" >&2; printf '%s\n' "$probe" | head -15 >&2; exit 1; fi

ok=0; skip=0; fail=0
for model in "${MODELS[@]}"; do
  for arm in "${ARMS[@]}"; do
    cell="$RUNS/${model}__${arm}"; mkdir -p "$cell/logs"
    for spec in "${SPECS[@]}"; do
      set -- $spec; fixture="$1"; reps="$2"; agent="$3"; kind="$4"
      for n in $(seq 1 "$reps"); do
        out="$cell/${fixture}.${n}.txt"
        [ -e "$out" ] && { skip=$((skip+1)); continue; }
        wd="$(mktemp -d)"; cp "$FIX/$fixture" "$wd/"
        args=(--settings "$PLUGINS_OFF")
        [ "$arm" = "A1" ] && args+=(--plugin-dir "$STAGE")
        st=$(date +%s)
        ( cd "$wd" && run_with_timeout "$TIMEOUT" claude -p "$(build_prompt "$wd/$fixture" "$agent" "$kind" "$arm")" \
            --model "$model" "${args[@]}" --allowedTools "Read Bash Agent Task" \
            > "$out" 2> "$cell/logs/${fixture}.${n}.stderr" )
        rc=$?; en=$(date +%s)
        if [ "$rc" -ne 0 ] || [ ! -s "$out" ]; then
          rm -f "$out"; fail=$((fail+1)); echo "  FAIL $model $arm $fixture.$n (rc=$rc)"
        else
          ok=$((ok+1)); echo "  ok   $model $arm $fixture.$n ($((en-st))s)"
        fi
        printf 'model=%s\narm=%s\nfixture=%s\nrep=%s\nrc=%s\nseconds=%s\n' \
          "$model" "$arm" "$fixture" "$n" "$rc" "$((en-st))" > "$cell/logs/${fixture}.${n}.meta"
        rm -rf "$wd"
      done
    done
  done
done

echo; echo "완료 $ok / 건너뜀 $skip / 실패 $fail"
echo "채점:  for d in $RUNS/*/; do echo \"== \$d\"; python3 $REPO/.github/evals/score.py \"\$d\"; done"
echo "오염:  grep -lE 'Scale Grade|Has FE Components|5\\.4\\.1|롤업' $RUNS/*A0/*.txt"
