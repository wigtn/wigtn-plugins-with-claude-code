#!/usr/bin/env bash
# 모델 세대 × 하네스 2×2 실행기.  PROTOCOL.md 를 따른다.
#
#   bash run.sh            # 기본: 3 fixture × 3회 = 36콜
#   REPS=2 FIX=2 bash run.sh   # 축소: 2 fixture × 2회 = 16콜
#   DRY=1 bash run.sh          # 실행 계획만 출력 (모델 호출 0)
#
# 이어달리기 안전: 이미 결과 파일이 있으면 그 칸은 건너뛴다.
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
echo "  출력: $RUNS"
[ "$DRY" = "1" ] && { echo "  (DRY — 모델 호출 없이 종료)"; exit 0; }

command -v claude >/dev/null || { echo "claude CLI 없음"; exit 1; }
mkdir -p "$RUNS"

done_n=0; skip_n=0; fail_n=0
for model in "${MODELS[@]}"; do
  for arm in "${ARMS[@]}"; do
    for f in $(seq 1 "$FIX"); do
      for r in $(seq 1 "$REPS"); do
        key="${model}__${arm}__f${f}__r${r}"
        out="$RUNS/$key"
        if [ -s "$out/PRD.md" ]; then skip_n=$((skip_n+1)); continue; fi
        rm -rf "$out"; mkdir -p "$out"

        # A0 는 저장소 밖 + 플러그인 실제 비활성화 (오염 통제)
        # A1 은 로컬 플러그인 로드
        if [ "$arm" = "A0" ]; then
          wd="$(mktemp -d)"
          args=(--settings '{"enabledPlugins":{"wigtn-plugins":false}}')
        else
          wd="$(mktemp -d)"
          args=(--plugin-dir "$REPO/plugins")
        fi

        started=$(date +%s)
        ( cd "$wd" && timeout "$TIMEOUT" claude -p "$(fixture_text "$f")" \
            --model "$model" "${args[@]}" \
            --allowedTools "Read Write Edit Glob Grep" \
            > "$out/stdout.log" 2> "$out/stderr.log" )
        status=$?
        finished=$(date +%s)

        # 산출물 회수
        find "$wd" -maxdepth 3 -iname 'PRD*.md' -exec cp {} "$out/PRD.md" \; 2>/dev/null
        [ -s "$out/PRD.md" ] || cp "$out/stdout.log" "$out/PRD.md" 2>/dev/null

        printf 'model=%s\narm=%s\nfixture=%s\nrep=%s\nstatus=%s\nseconds=%s\n' \
          "$model" "$arm" "$f" "$r" "$status" "$((finished-started))" > "$out/meta"
        rm -rf "$wd"

        if [ "$status" -eq 0 ] && [ -s "$out/PRD.md" ]; then
          done_n=$((done_n+1)); echo "  ok   $key ($((finished-started))s)"
        else
          fail_n=$((fail_n+1)); echo "  FAIL $key (status=$status)"
        fi
      done
    done
  done
done

echo
echo "완료 $done_n / 건너뜀 $skip_n / 실패 $fail_n"
echo "채점: python3 $REPO/.github/evals/score_prd.py $RUNS/*"
echo "오염검사: grep -lc 'Scale Grade\\|Has FE Components\\|5\\.4\\.1' $RUNS/*A0*/PRD.md"
