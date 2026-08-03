#!/usr/bin/env bash
# 리뷰 3-arm (A0/A1/A2) — 검출 + **오탐**.  PROTOCOL-REVIEW.md 를 따른다.
#
#   bash run-review.sh          # 4 픽스처 × 3 arm = 48콜
#   DRY=1 bash run-review.sh    # arm 검증만
#
# 격리·arm 검증은 run.sh 와 동일한 방식이다(ERRATA E-07/E-08 참조).
# 차이는 과제뿐이다: PRD 생성이 아니라 파일 리뷰.
#
# 왜 오탐이 주 지표인가:
#   검출률은 세 arm 모두 천장이라 정보가 없다(FINDING-01). 오탐은 천장이 아니다.
#   그리고 이 저장소의 게이트 규칙은 critical ≥1 -> FAIL 이므로, 깨끗한 파일에
#   critical 을 다는 것은 **결백한 커밋을 막는다**는 실제 피해다.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
HERE="$REPO/.github/evals/harness-3arm"
RUNS="$HERE/runs-review"
STAGE="$HERE/.stage"
RUNCALL="$REPO/.github/evals/lib/runcall.py"
FIXDIR="$REPO/.github/evals/fixtures"

DRY="${DRY:-0}"
TIMEOUT="${TIMEOUT:-900}"
PAR="${PAR:-3}"
MODEL="${MODEL:-claude-opus-5}"
ARMS=(A0 A1 A2)

# 픽스처: 파일 / 반복 / 리뷰어 / clean|dirty
#   clean 픽스처의 반복을 더 준다 — 오탐이 주 지표이고 천장이 아니기 때문이다.
SPECS=(
  "prd-defective.md  3 prd-reviewer  dirty"
  "code-defective.ts 3 code-reviewer dirty"
  "prd-clean.md      5 prd-reviewer  clean"
  "code-clean.ts     5 code-reviewer clean"
)

ISO=(--setting-sources project)
PROBE='List the exact names of every skill and agent available to you whose name contains '"'"'wigtn'"'"'. One per line, nothing else. If none exist, output exactly: NONE'

say() { printf '%s\n' "$*"; }
die() { printf 'ABORT: %s\n' "$*" >&2; exit 1; }

set_arm_args() {
  EXTRA=("${ISO[@]}")
  case "$1" in
    A0) : ;;
    A1) EXTRA+=(--plugin-dir "$STAGE/A1") ;;
    A2) EXTRA+=(--plugin-dir "$STAGE/A2") ;;
  esac
}

stage_arms() {
  rm -rf "$STAGE"; mkdir -p "$STAGE"
  local wt="$STAGE/wt-A1"
  git -C "$REPO" worktree prune >/dev/null 2>&1
  git -C "$REPO" worktree add --detach "$wt" main >/dev/null 2>&1
  [ -d "$wt/plugins/wigtn-plugins" ] || die "main worktree 생성 실패"
  cp -R "$wt/plugins/wigtn-plugins" "$STAGE/A1"
  cp -R "$REPO/plugins/wigtn-plugins" "$STAGE/A2"
  for a in A1 A2; do   # E-07: version 유일화
    python3 - "$STAGE/$a/.claude-plugin/plugin.json" "$a" <<'PY'
import json,sys
p,arm=sys.argv[1],sys.argv[2]
d=json.load(open(p)); d["version"]=f'{d["version"]}-arm{arm}'
json.dump(d,open(p,"w"),indent=2)
PY
  done
  say "  A1 reviewer=$(wc -l < "$STAGE/A1/agents/code-reviewer.md" | tr -d ' ')줄 · A2 reviewer=$(wc -l < "$STAGE/A2/agents/code-reviewer.md" | tr -d ' ')줄"
}

verify_arm() {
  local arm="$1" wd out n_wigtn n_par
  wd="$(mktemp -d)"; set_arm_args "$arm"
  out="$( cd "$wd" && claude -p "$PROBE" --model "$MODEL" "${EXTRA[@]}" \
            --allowedTools Read </dev/null 2>&1 )"
  rm -rf "$wd"
  n_wigtn=$(printf '%s' "$out" | grep -c 'wigtn-plugins:')
  n_par=$(printf '%s' "$out" | grep -c 'parallel-.*-coordinator')
  case "$arm" in
    A0) [ "$n_wigtn" -eq 0 ] || die "A0 오염 — wigtn $n_wigtn 개" ;;
    A1) [ "$n_par" -ge 1 ] || die "A1 미적재 (E-07 재발 의심)" ;;
    A2) { [ "$n_wigtn" -ge 1 ] && [ "$n_par" -eq 0 ]; } || die "A2 서명 불일치 (wigtn=$n_wigtn par=$n_par)" ;;
  esac
  say "  ok  $arm (wigtn=$n_wigtn parallel=$n_par)"
}

# 과제 문구는 세 arm 동일. A1/A2 만 "플러그인 리뷰어로 수행하라"가 붙는다.
# subagent_type 문자열도 A1/A2 가 **같다**(wigtn-plugins:<agent>) — 이름이 아니라
# 내용만 다르다. 이름을 바꾸면 그 자체가 교란이 된다.
build_prompt() { # $1=경로 $2=에이전트 $3=clean|dirty $4=arm
  local p="아래 파일을 리뷰해서 문제를 전부 찾아라.

파일: $1

요구사항:
- 모든 지적에 파일 경로/라인 또는 문서 섹션 번호를 증거로 단다.
- 마지막에 반드시 JSON 블록을 낸다: {\"findings\":[{\"severity\":\"critical|major|minor|info\",\"where\":\"...\",\"what\":\"...\"}]}"
  [ "$3" = "clean" ] && p="$p
- 이 파일은 문제가 없을 수도 있다. **근거 없는 감점을 하지 마라.** 실제 결함만 보고한다."
  [ "$4" != "A0" ] && p="$p

리뷰는 반드시 subagent_type \"wigtn-plugins:$2\" 서브에이전트를 띄워 그 에이전트의 리뷰 프로토콜대로 수행하고, 그 결과를 그대로 출력한다."
  printf '%s' "$p"
}

one_call() { # $1=arm $2=fixture $3=agent $4=clean/dirty $5=rep
  local arm="$1" fx="$2" ag="$3" kind="$4" r="$5"
  local cell="$RUNS/${MODEL}__${arm}" key="${fx}.${r}"
  local out="$cell/${key}.txt"
  [ -e "$out" ] && return 0
  mkdir -p "$cell/logs"
  local wd; wd="$(mktemp -d)"; set_arm_args "$arm"

  python3 "$RUNCALL" \
    --meta "$cell/logs/${key}.meta" --stdout "$out" --stderr "$cell/logs/${key}.stderr" \
    --timeout "$TIMEOUT" --cwd "$wd" \
    --kv "model=$MODEL" --kv "arm=$arm" --kv "fixture=$fx" --kv "kind=$kind" \
    --kv "rep=$r" --kv "parallel=$PAR" \
    -- claude -p "$(build_prompt "$FIXDIR/$fx" "$ag" "$kind" "$arm")" \
       --model "$MODEL" "${EXTRA[@]}" \
       --allowedTools "Agent Read Glob Grep" --output-format json
  local rc=$?
  rm -rf "$wd"
  if [ "$rc" -ne 0 ]; then
    rm -f "$out"   # E-02: 실패한 콜의 부분 산출물을 결과로 남기지 않는다
    say "  FAIL   $arm $key ($(grep -m1 '^exit_reason=' "$cell/logs/${key}.meta"))"
  else
    say "  ok     $arm $key ($(wc -c < "$out" | tr -d ' ')바이트)"
  fi
}

say "리뷰 3-arm — model=$MODEL arms=${ARMS[*]} par=$PAR"
total=0; for s in "${SPECS[@]}"; do set -- $s; total=$((total + $2)); done
say "총 $((total * ${#ARMS[@]}))콜 (arm당 $total), 타임아웃 ${TIMEOUT}초"

say "[1/3] 스테이징"; stage_arms
say "[2/3] arm 검증"; for a in "${ARMS[@]}"; do verify_arm "$a"; done
[ "$DRY" = "1" ] && { say "DRY=1 — 멈춘다"; exit 0; }

say "[3/3] 실행"
n=0
for arm in "${ARMS[@]}"; do
  for s in "${SPECS[@]}"; do
    set -- $s
    fx="$1"; reps="$2"; ag="$3"; kind="$4"
    for r in $(seq 1 "$reps"); do
      one_call "$arm" "$fx" "$ag" "$kind" "$r" &
      n=$((n+1)); [ $((n % PAR)) -eq 0 ] && wait
    done
  done
done
wait
say ""
say "분석: python3 $HERE/analyze-review.py"
