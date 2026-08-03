#!/usr/bin/env bash
# 3-arm 하네스 비교 실행기.  PROTOCOL.md 를 따른다.  일탈은 ERRATA.md 에 기록.
#
#   bash run.sh                     # 3 arm × 3 fixture × 5 rep = 45콜
#   REPS=2 FIX=1 bash run.sh        # 축소
#   DRY=1 bash run.sh               # 실행 계획만 (모델 호출 0)
#   MODEL=claude-opus-4-8 bash run.sh
#
# 이어달리기 안전: 이미 산출물이 있는 칸은 건너뛴다.
#
# ── 격리 (실측 확정) ────────────────────────────────────────────────────
# 저장소 안 cwd 에서 돌리면 사용자 설치본(구 하네스)이 그대로 노출된다.
# 저장소 밖 임시 cwd 에서는 NONE 이다. 따라서 격리는 cwd 로 한다.
# --settings 의 enabledPlugins 에 의존하지 않는다 (P-6: 교체가 아니라 병합).
#
# ── E-07 (신규) ─────────────────────────────────────────────────────────
# --plugin-dir 는 name+version 이 설치본과 같으면 조용히 무시된다.
# A1(main) 은 설치본과 wigtn-plugins@0.1.14 로 동일해서 로드되지 않았다.
# 스테이징 사본의 version 에 arm 접미사를 붙여 유일화한다. name 은 그대로 둔다
# (이름을 바꾸면 모델이 보는 네임스페이스가 달라져 그 자체가 교란이 된다).
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
HERE="$REPO/.github/evals/harness-3arm"
RUNS="$HERE/runs"
STAGE="$HERE/.stage"
RUNCALL="$REPO/.github/evals/lib/runcall.py"

REPS="${REPS:-5}"
FIX="${FIX:-3}"
DRY="${DRY:-0}"
TIMEOUT="${TIMEOUT:-1800}"
PAR="${PAR:-3}"
MODEL="${MODEL:-claude-opus-5}"
ARMS=(A0 A1 A2)

# arm 서명 — PROTOCOL.md 의 표와 일치해야 한다.
#   A0: wigtn 항목 0개
#   A1: parallel-digging-coordinator 존재
#   A2: wigtn 항목 있으나 parallel-* 부재
PROBE='List the exact names of every skill and agent available to you whose name contains '"'"'wigtn'"'"'. One per line, nothing else. If none exist, output exactly: NONE'

say() { printf '%s\n' "$*"; }
die() { printf 'ABORT: %s\n' "$*" >&2; exit 1; }

fixture_text() {
  case "$1" in
    1) printf '%s' "사내 팀원들이 쓸 휴가 신청/승인 웹 서비스를 만들려고 한다. 신청자는 휴가를 신청하고, 팀장은 승인/반려하며, 관리자는 전체 현황을 본다. 이 기능의 PRD를 작성해서 PRD.md 파일로 저장해줘." ;;
    2) printf '%s' "온라인 강의 플랫폼에 쿠폰 기능을 추가하려고 한다. 관리자가 쿠폰을 발행하고, 수강생이 결제 시 적용하며, 중복 사용과 만료를 막아야 한다. 이 기능의 PRD를 작성해서 PRD.md 파일로 저장해줘." ;;
    3) printf '%s' "물류 스타트업에서 배송 기사용 모바일 앱에 실시간 배송 추적 기능을 넣으려고 한다. 기사는 위치를 공유하고, 고객은 지도에서 위치를 보며, 관리자는 지연 건을 모니터링한다. 이 기능의 PRD를 작성해서 PRD.md 파일로 저장해줘." ;;
  esac
}

# ── arm 스테이징 ────────────────────────────────────────────────────────
stage_arms() {
  rm -rf "$STAGE"; mkdir -p "$STAGE"
  # A1 = main (구 하네스). worktree 로 뽑아 작업 트리를 건드리지 않는다.
  local wt="$STAGE/wt-A1"
  git -C "$REPO" worktree add --detach "$wt" main >/dev/null 2>&1 \
    || die "main worktree 생성 실패"
  cp -R "$wt/plugins/wigtn-plugins" "$STAGE/A1"
  # A2 = HEAD (PR본)
  cp -R "$REPO/plugins/wigtn-plugins" "$STAGE/A2"

  # E-07: version 유일화
  for a in A1 A2; do
    python3 - "$STAGE/$a/.claude-plugin/plugin.json" "$a" <<'PY'
import json,sys
p,arm=sys.argv[1],sys.argv[2]
d=json.load(open(p)); d["version"]=f'{d["version"]}-arm{arm}'
json.dump(d,open(p,"w"),indent=2)
PY
  done

  say "  스테이징 서명:"
  for a in A1 A2; do
    say "    $a  prd=$(wc -l < "$STAGE/$a/commands/prd.md" | tr -d ' ')줄" \
        "reviewer=$(wc -l < "$STAGE/$a/agents/code-reviewer.md" | tr -d ' ')줄" \
        "parallel-coord=$(ls "$STAGE/$a/agents/" | grep -c parallel)" \
        "ver=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' "$STAGE/$a/.claude-plugin/plugin.json")"
  done
}

arm_args() {  # $1=arm -> stdout: 추가 인자
  case "$1" in
    A0) : ;;
    A1) printf '%s\n%s' "--plugin-dir" "$STAGE/A1" ;;
    A2) printf '%s\n%s' "--plugin-dir" "$STAGE/A2" ;;
  esac
}

# ── arm 검증: 어느 arm 이 로드됐는지 서명으로 확인 ──────────────────────
verify_arm() {
  local arm="$1" wd out n_wigtn n_par
  wd="$(mktemp -d)"
  mapfile -t extra < <(arm_args "$arm")
  out="$( cd "$wd" && claude -p "$PROBE" --model "$MODEL" \
            ${extra[@]+"${extra[@]}"} --allowedTools Read </dev/null 2>&1 )"
  rm -rf "$wd"
  n_wigtn=$(printf '%s' "$out" | grep -c 'wigtn-plugins:')
  n_par=$(printf '%s' "$out" | grep -c 'parallel-.*-coordinator')

  case "$arm" in
    A0) [ "$n_wigtn" -eq 0 ] || { printf '%s\n' "$out" | head -8 >&2
          die "A0 오염 — wigtn 항목이 $n_wigtn 개 보인다 (0이어야 함)"; } ;;
    A1) [ "$n_par" -ge 1 ] || { printf '%s\n' "$out" | head -8 >&2
          die "A1 미적재 — parallel-*-coordinator 가 없다 (E-07 재발 의심)"; } ;;
    A2) { [ "$n_wigtn" -ge 1 ] && [ "$n_par" -eq 0 ]; } || { printf '%s\n' "$out" | head -8 >&2
          die "A2 서명 불일치 — wigtn=$n_wigtn parallel=$n_par (각각 ≥1, 0 이어야 함)"; } ;;
  esac
  say "  ok  $arm 검증 (wigtn=$n_wigtn parallel=$n_par)"
}

# ── 단일 콜 ─────────────────────────────────────────────────────────────
one_call() {
  local arm="$1" f="$2" r="$3"
  local cell="$RUNS/${MODEL}__${arm}" key="f${f}r${r}"
  local out="$cell/prd.${key}.md"
  [ -e "$out" ] && return 0

  mkdir -p "$cell/logs"
  local wd; wd="$(mktemp -d)"
  mapfile -t extra < <(arm_args "$arm")

  python3 "$RUNCALL" \
    --meta "$cell/logs/${key}.meta" \
    --stdout "$cell/logs/${key}.stdout" \
    --stderr "$cell/logs/${key}.stderr" \
    --timeout "$TIMEOUT" --cwd "$wd" \
    --kv "model=$MODEL" --kv "arm=$arm" --kv "fixture=$f" --kv "rep=$r" \
    --kv "parallel=$PAR" \
    -- claude -p "$(fixture_text "$f")" --model "$MODEL" \
       ${extra[@]+"${extra[@]}"} \
       --allowedTools "Read Write Edit Glob Grep" --output-format json
  local rc=$?

  # E-02: 조용한 폴백 금지. 산출물 없음과 계측 실패를 절대 섞지 않는다.
  local produced
  produced="$(find "$wd" -maxdepth 3 -iname '*PRD*.md' -print -quit 2>/dev/null)"
  if [ "$rc" -ne 0 ]; then
    say "  FAIL   $arm $key — 계측 실패, 채점 제외 ($(grep -m1 '^exit_reason=' "$cell/logs/${key}.meta"))"
  elif [ -n "$produced" ] && [ -s "$produced" ]; then
    cp "$produced" "$out"
    printf 'artifact=ok\nlines=%s\n' "$(wc -l < "$out" | tr -d ' ')" >> "$cell/logs/${key}.meta"
    say "  ok     $arm $key ($(wc -l < "$out" | tr -d ' ')줄)"
  else
    : > "$out"
    printf 'artifact=nofile\nlines=0\n' >> "$cell/logs/${key}.meta"
    say "  NOFILE $arm $key — 파일 미생성. 빈 산출물로 채점(0점)한다"
  fi
  rm -rf "$wd"
}

# ── main ────────────────────────────────────────────────────────────────
say "3-arm 하네스 비교 — model=$MODEL arms=${ARMS[*]} fix=$FIX reps=$REPS par=$PAR"
say "총 $((${#ARMS[@]} * FIX * REPS))콜, 타임아웃 ${TIMEOUT}초"

[ -x "$(command -v python3)" ] || die "python3 없음"
[ -f "$RUNCALL" ] || die "runcall.py 없음: $RUNCALL"

say "[1/3] arm 스테이징"
stage_arms

say "[2/3] arm 검증 (서명 대조)"
for arm in "${ARMS[@]}"; do verify_arm "$arm"; done

if [ "$DRY" = "1" ]; then say "DRY=1 — 여기서 멈춘다"; exit 0; fi

say "[3/3] 실행"
n=0
for arm in "${ARMS[@]}"; do
  for f in $(seq 1 "$FIX"); do
    for r in $(seq 1 "$REPS"); do
      one_call "$arm" "$f" "$r" &
      n=$((n+1))
      if [ $((n % PAR)) -eq 0 ]; then wait; fi
    done
  done
done
wait

say ""
say "채점:"
say "  python3 $REPO/.github/evals/score_prd.py $RUNS/${MODEL}__A0 $RUNS/${MODEL}__A1 $RUNS/${MODEL}__A2"
say "분석:"
say "  python3 $HERE/analyze.py"
