#!/usr/bin/env bash
# 모델 세대 × 하네스 2×2 실행기.  PROTOCOL.md 를 따른다.  일탈은 ERRATA.md 에 기록.
#
#   bash run.sh                # 3 fixture × 3회 × 2모델 × 2arm = 36콜
#   REPS=2 FIX=2 bash run.sh   # 축소
#   DRY=1 bash run.sh          # 실행 계획만 (모델 호출 0)
#
# 이어달리기 안전: 이미 산출물이 있는 칸은 건너뛴다.
#
# ── E-01 수정: 산출물 파일명 ────────────────────────────────────────────
# 이전 판은 runs/<key>/PRD.md 로 썼는데, 사전등록된 채점기(score_prd.py)는
# 디렉터리 안의 prd.*.md 를 글로브한다. 즉 **아무것도 채점되지 않는** 상태였다.
# 채점기는 프로토콜상 수정 금지이므로, 러너의 출력 레이아웃을 채점기에 맞춘다:
#   runs/<model>__<arm>/prd.f<fixture>r<rep>.md   ← 한 디렉터리 = 2×2의 한 칸
#
# ── E-02 수정: 조용한 폴백 제거 ─────────────────────────────────────────
# 이전 판은 산출물이 없으면 stdout.log 를 PRD.md 로 복사했다. 그러면 "모델이
# 파일을 안 만들었다"와 "모델이 PRD를 썼다"가 같은 파일로 섞인다. 이 저장소가
# EXPERIMENT.md §6-5 에서 스스로 채점기 버그로 기록한 바로 그 패턴이다.
# 이제 세 결과를 구분해 기록한다:
#   ok      status=0 + 산출물 있음        → 채점 대상
#   nofile  status=0 + 산출물 없음        → 빈 파일로 채점 대상 (진짜 0점, 큰 소리로 보고)
#   fail    status≠0 (타임아웃·API 오류)  → 계측 실패. 채점 제외, 로그 보존
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
HERE="$REPO/.github/evals/model-generation-2x2"
RUNS="$HERE/runs"
REPS="${REPS:-3}"
FIX="${FIX:-3}"
DRY="${DRY:-0}"
TIMEOUT="${TIMEOUT:-600}"

MODELS=(claude-opus-4-8 claude-opus-5)
ARMS=(A0 A1)

# 전역 활성 플러그인 전부 OFF. 키는 `<plugin>@<marketplace>` 형식이어야 한다.
PLUGINS_OFF='{"enabledPlugins":{"wigtn-plugins@wigtn-plugins":false,"prd@wigtn-plugins":false,"implement@wigtn-plugins":false,"public-commands@wigtn-plugins":false,"frontend-development@wigtn-plugins":false,"backend-development@wigtn-plugins":false,"mobile-development@wigtn-plugins":false,"ai-development@wigtn-plugins":false}}'

# macOS에는 GNU timeout 이 없다(coreutils 미설치). 이식 가능한 워치독으로 대체한다.
# 최초 실행 16콜이 status=127 로 전멸한 원인이 이것이었다 — runs-discarded-no-timeout/ 참고.
run_with_timeout() { # $1=초  나머지=명령
  local secs="$1"; shift
  "$@" &
  local pid=$!
  ( sleep "$secs"; kill -9 "$pid" 2>/dev/null ) &
  local watch=$!
  wait "$pid" 2>/dev/null; local rc=$?
  kill -9 "$watch" 2>/dev/null; wait "$watch" 2>/dev/null
  return $rc
}

# 동일 프롬프트 — 양쪽 arm에 그대로 준다 (PROTOCOL: 프롬프트 규약)
fixture_text() {
  case "$1" in
    1) printf '%s' "사내 팀원들이 쓸 휴가 신청/승인 웹 서비스를 만들려고 한다. 신청자는 휴가를 신청하고, 팀장은 승인/반려하며, 관리자는 전체 현황을 본다. 이 기능의 PRD를 작성해서 PRD.md 파일로 저장해줘." ;;
    2) printf '%s' "온라인 강의 플랫폼에 쿠폰 기능을 추가하려고 한다. 관리자가 쿠폰을 발행하고, 수강생이 결제 시 적용하며, 중복 사용과 만료를 막아야 한다. 이 기능의 PRD를 작성해서 PRD.md 파일로 저장해줘." ;;
    3) printf '%s' "물류 스타트업에서 배송 기사용 모바일 앱에 실시간 배송 추적 기능을 넣으려고 한다. 기사는 위치를 공유하고, 고객은 지도에서 위치를 보며, 관리자는 지연 건을 모니터링한다. 이 기능의 PRD를 작성해서 PRD.md 파일로 저장해줘." ;;
  esac
}

echo "== 2x2 실행 계획 =="
echo "  모델: ${MODELS[*]}"
echo "  arm : ${ARMS[*]}   (A0=플러그인 끔, A1=플러그인 켬)"
echo "  규모: fixture ${FIX} x 반복 ${REPS}  ->  총 $((${#MODELS[@]} * ${#ARMS[@]} * FIX * REPS))콜"
echo "  출력: $RUNS/<model>__<arm>/prd.f<n>r<n>.md"
[ "$DRY" = "1" ] && { echo "  (DRY — 모델 호출 없이 종료)"; exit 0; }

command -v claude >/dev/null || { echo "claude CLI 없음"; exit 1; }

# ── E-05: 처치 arm 검증 (treatment verification) ────────────────────────
# 대조군 오염만 검사하고 처치군은 안 봤다가, A1 18콜이 **플러그인 없이** 돌았다.
# 원인: --plugin-dir 로 올린 플러그인의 키가 PLUGINS_OFF 의 키와 같아서 같이 꺼졌고,
#       그때 보이던 스킬은 전부 마켓플레이스 구버전이었다(P-5).
# 처방 두 가지:
#   1) 스테이징 사본을 `wigtn-local` 로 리네임해 OFF 목록과 이름이 겹치지 않게 한다
#   2) 실행 전에 스킬이 실제로 보이는지 확인하고, 안 보이면 **아예 시작하지 않는다**
STAGE="${STAGE:-$HERE/.stage/wigtn-local}"
rm -rf "$(dirname "$STAGE")"; mkdir -p "$(dirname "$STAGE")"
cp -r "$REPO/plugins/wigtn-plugins" "$STAGE"
python3 - "$STAGE" <<'PYEOF'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]) / ".claude-plugin" / "plugin.json"
d = json.loads(p.read_text()); d["name"] = "wigtn-local"
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
PYEOF

echo "== 처치 검증 =="
probe_wd="$(mktemp -d)"
probe=$( cd "$probe_wd" && claude -p "List every skill name available to you right now, one per line. If none, print NONE." \
          --model "${MODELS[0]}" --settings "$PLUGINS_OFF" --plugin-dir "$STAGE" \
          --allowedTools "Read" < /dev/null 2>&1 )
rm -rf "$probe_wd"
if printf '%s' "$probe" | grep -q "wigtn-local:prd"; then
  echo "  ok — A1 처치 확인됨 (wigtn-local:prd 로드됨)"
else
  echo "  ABORT — A1 arm 에 플러그인이 로드되지 않는다. 실행을 시작하지 않는다." >&2
  printf '%s\n' "$probe" | head -20 >&2
  exit 1
fi

done_n=0; skip_n=0; fail_n=0; nofile_n=0
for model in "${MODELS[@]}"; do
  for arm in "${ARMS[@]}"; do
    cell="$RUNS/${model}__${arm}"
    mkdir -p "$cell/logs"
    for f in $(seq 1 "$FIX"); do
      for r in $(seq 1 "$REPS"); do
        key="f${f}r${r}"
        out="$cell/prd.${key}.md"
        [ -e "$out" ] && { skip_n=$((skip_n+1)); continue; }

        # A0 는 저장소 밖 + 플러그인 실제 비활성화 (오염 통제)
        # A1 은 로컬 플러그인 로드
        wd="$(mktemp -d)"
        # E-04: --settings 의 enabledPlugins 는 **병합**된다(교체 아님). 프로브 P-6 참조.
        # 따라서 마켓플레이스 키를 하나하나 false 로 적어야 실제로 꺼진다.
        # A1 도 같은 OFF 를 깔고 --plugin-dir 로 로컬 사본만 얹는다 — 안 그러면
        # 구버전(마켓플레이스)과 신버전이 동시에 로드된다(P-5).
        args=(--settings "$PLUGINS_OFF")
        [ "$arm" = "A1" ] && args+=(--plugin-dir "$STAGE")

        started=$(date +%s)
        ( cd "$wd" && run_with_timeout "$TIMEOUT" claude -p "$(fixture_text "$f")" \
            --model "$model" "${args[@]}" \
            --allowedTools "Read Write Edit Glob Grep" \
            > "$cell/logs/${key}.stdout" 2> "$cell/logs/${key}.stderr" )
        status=$?
        finished=$(date +%s)

        produced="$(find "$wd" -maxdepth 3 -iname '*PRD*.md' -print -quit 2>/dev/null)"
        if [ "$status" -ne 0 ]; then
          verdict=fail; fail_n=$((fail_n+1))
          echo "  FAIL   $model $arm $key (status=$status) — 계측 실패, 채점 제외"
        elif [ -n "$produced" ] && [ -s "$produced" ]; then
          cp "$produced" "$out"; verdict=ok; done_n=$((done_n+1))
          echo "  ok     $model $arm $key ($((finished-started))s, $(wc -l < "$out" | tr -d ' ')줄)"
        else
          : > "$out"; verdict=nofile; nofile_n=$((nofile_n+1))
          echo "  NOFILE $model $arm $key — 파일 미생성. 빈 산출물로 채점(0점)한다"
        fi

        printf 'model=%s\narm=%s\nfixture=%s\nrep=%s\nstatus=%s\nverdict=%s\nseconds=%s\n' \
          "$model" "$arm" "$f" "$r" "$status" "$verdict" "$((finished-started))" \
          > "$cell/logs/${key}.meta"
        rm -rf "$wd"
      done
    done
  done
done

echo
echo "완료 $done_n / 건너뜀 $skip_n / 파일없음 $nofile_n / 계측실패 $fail_n"
echo
echo "채점:"
echo "  python3 $REPO/.github/evals/score_prd.py $RUNS/claude-opus-4-8__A0 $RUNS/claude-opus-4-8__A1 $RUNS/claude-opus-5__A0 $RUNS/claude-opus-5__A1"
echo "오염검사 (A0에 플러그인 고유 용어가 섞였는가):"
echo "  grep -lE 'Scale Grade|Has FE Components|5\\.4\\.1' $RUNS/*A0/prd.*.md"
