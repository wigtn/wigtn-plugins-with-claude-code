#!/usr/bin/env bash
# WIGTN 프롬프트 표면 측정 — 임의의 git ref에 대해 동일 방법으로 재실행 가능.
#
# 사용법:  .github/scripts/measure.sh <git-ref>        (예: main, HEAD, v0.1.14)
#
# 측정 대상은 "모델이 읽는 지시문"이다. 참조 데이터(디자인 스타일 가이드,
# 템플릿)는 on-demand 로드라 상시 비용이 없어 별도 집계한다.
#
# 주의: 이 스크립트는 기계적으로 셀 수 있는 것만 센다. 출력 품질은 측정하지 않는다.
#       품질 비교는 docs/evals/ 의 behavioral probe 문서를 따른다.

set -uo pipefail

REF="${1:?usage: measure.sh <git-ref>}"
ROOT="$(git rev-parse --show-toplevel)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

git -C "$ROOT" archive "$REF" | tar -x -C "$WORK" || {
  echo "ref를 찾을 수 없음: $REF" >&2; exit 1; }

P="$WORK/plugins/wigtn-plugins"
[ -d "$P" ] || { echo "플러그인 디렉토리 없음: $REF" >&2; exit 1; }

lines() { [ -f "$1" ] && wc -l < "$1" | tr -d ' ' || echo 0; }
chars() { [ -f "$1" ] && wc -c < "$1" | tr -d ' ' || echo 0; }
# 프론트매터(첫 --- 블록)만 = 상시 로드되는 description 비용
fm_chars() { [ -f "$1" ] && awk '/^---$/{c++} c==1{print} c==2{exit}' "$1" | wc -c | tr -d ' ' || echo 0; }
# 저장소 전역 grep 카운트 (플러그인 + 루트 문서)
hits() { grep -rIl "$1" "$P" "$WORK"/*.md 2>/dev/null | wc -l | tr -d ' '; }
occ()  { grep -rIo "$1" "$P" "$WORK"/*.md 2>/dev/null | wc -l | tr -d ' '; }

echo "# 프롬프트 표면 측정: $REF"
echo
echo "commit: $(git -C "$ROOT" rev-parse --short "$REF") · 측정: $(git -C "$ROOT" log -1 --format=%ad --date=short "$REF")"
echo

# ── 1. 지시문 표면 ─────────────────────────────────────────────
echo "## 1. 지시문 표면 (모델이 읽는 것)"
echo
echo "| 구분 | 파일 수 | 줄 | 문자 | ~토큰 |"
echo "|---|---|---|---|---|"
for grp in commands agents skills; do
  case $grp in
    commands) files=$(find "$P/commands" -maxdepth 1 -name '*.md' 2>/dev/null | sort) ;;
    agents)   files=$(find "$P/agents"   -maxdepth 1 -name '*.md' 2>/dev/null | sort) ;;
    skills)   files=$(find "$P/skills" -name 'SKILL.md' 2>/dev/null | sort) ;;
  esac
  n=0; l=0; c=0
  for f in $files; do n=$((n+1)); l=$((l+$(lines "$f"))); c=$((c+$(chars "$f"))); done
  printf "| %s | %d | %d | %d | %d |\n" "$grp" "$n" "$l" "$c" "$((c/4))"
done
# 참조 파일(on-demand)
refl=0; refc=0; refn=0
for f in $(find "$P" -name '*.md' 2>/dev/null | grep -E '/(references|templates|styles|common)/' | sort); do
  refn=$((refn+1)); refl=$((refl+$(lines "$f"))); refc=$((refc+$(chars "$f")))
done
printf "| (참조·템플릿·스타일 = on-demand) | %d | %d | %d | %d |\n" "$refn" "$refl" "$refc" "$((refc/4))"
echo

# ── 2. 진입점별 비용 ───────────────────────────────────────────
echo "## 2. 진입점별 프롬프트 비용 (커맨드 본문만, 디스패치 전)"
echo
echo "| 진입점 | 줄 | ~토큰 |"
echo "|---|---|---|"
for f in "$P"/commands/*.md; do
  [ -f "$f" ] || continue
  printf "| /%s | %d | %d |\n" "$(basename "$f" .md)" "$(lines "$f")" "$(( $(chars "$f") / 4 ))"
done
echo

# ── 3. 상시 로드 비용 ─────────────────────────────────────────
echo "## 3. 상시 로드 비용 (frontmatter description — 세션마다 무조건)"
echo
tot=0; cnt=0
for f in "$P"/agents/*.md "$P"/commands/*.md $(find "$P/skills" -name 'SKILL.md' 2>/dev/null); do
  [ -f "$f" ] || continue
  tot=$((tot + $(fm_chars "$f"))); cnt=$((cnt+1))
done
echo "- 컴포넌트 ${cnt}개 · $tot 문자 · ~$((tot/4)) 토큰"
echo

# ── 4. 죽은 코드 / 실행 불가 참조 ──────────────────────────────
echo "## 4. 죽은 코드·실행 불가 참조 (등장 횟수)"
echo
echo "| 항목 | 등장 | 비고 |"
echo "|---|---|---|"
printf "| \`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS\` | %s | false 분기가 no-op |\n" "$(occ 'CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS')"
printf "| \`TaskCreate\`/\`TaskUpdate\` | %s | agent-team teammate 전용 → 일반 서브에이전트에서 실행 불가 |\n" "$(occ 'Task\(Create\|Update\)')"
printf "| \`speedup\`/\`sequential_estimate\`/\`total_duration\` | %s | 모델이 측정 불가 → 날조 표면 |\n" "$(occ 'speedup\|sequential_estimate\|total_duration')"
printf "| \`file_locks\` | %s | 선언만 있고 강제 주체 없음 |\n" "$(occ 'file_locks')"
printf "| \`contract_override\` | %s | 같은 파일이 금지한 점수 조작을 수행하는 필드 |\n" "$(occ 'contract_override')"
echo

# ── 5. 계약 중복·드리프트 ─────────────────────────────────────
echo "## 5. 계약 중복 (같은 사실이 몇 개 파일에 재진술되는가)"
echo
echo "| 계약 | 재진술 파일 수 |"
echo "|---|---|"
printf "| 게이트 롤업 임계값 (\`critical\`/\`major\`/\`minor\` 판정) | %s |\n" "$(hits 'minor ≥5\|minor >= 5\|critical ≥1\|critical >= 1')"
printf "| Context Harvest 절차 | %s |\n" "$(hits 'Context Harvest')"
printf "| 100점 점수 루브릭 | %s |\n" "$(grep -rIl '100점\|100-point\|Quality Score' "$P/agents" "$P/commands" 2>/dev/null | wc -l | tr -d ' ')"
echo

# ── 6. frontmatter 위생 ───────────────────────────────────────
echo "## 6. frontmatter 위생"
echo
na=$(find "$P/agents" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
nt=$(grep -lE '^tools:' "$P"/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
nh=$(grep -lE '^effort: high' "$P"/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "- 에이전트 ${na}개 중 \`tools:\` 명시: ${nt}개 (미명시는 실행 컨텍스트에 따라 능력이 달라짐)"
echo "- \`effort: high\` 일률 적용: ${nh}개"
echo
echo "---"
echo "_measure.sh — 기계적 지표만. 출력 품질은 측정하지 않음._"
