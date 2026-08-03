#!/usr/bin/env bash
# WIGTN commit gate — PreToolUse:Bash
#
# 두 게이트는 서로 독립이다 (이전에는 하나의 if 안에 중첩돼 있었다):
#
#   게이트 1 — 객관 체크 (.wigtn/checks.sh)
#       모든 `git commit`에 실행된다. 커밋 메시지를 보지 않는다.
#       이전 구현은 메시지에 "Quality Score:"가 있을 때만 실행했기 때문에,
#       그 한 줄을 빼면 객관 검증까지 함께 꺼졌다 — 강제 대상이 강제 여부를 골랐다.
#
#   게이트 2 — 리뷰 PASS 아티팩트 (.wigtn/gate-pass)
#       파이프라인 커밋(메시지에 "Quality Gate: PASS")에 적용된다.
#       수동 커밋은 이 게이트의 대상이 아니다 — 리뷰를 주장하지 않았으므로.
#       레거시 신호 "Quality Score:"도 계속 인식한다 — 구버전 설치본이
#       그 문자열을 쓰기 때문이다. 신호를 좁히면 구버전이 무검증 통과한다.
#
# 면제: 충돌 해소·히스토리 재작성 중에는 게이트 1을 건너뛴다. 그렇지 않으면
# 20커밋 리베이스가 typecheck를 20번 돌려서, 사람이 hook을 통째로 끄게 된다.
#
# exit 2 = 차단. 그 외 non-zero는 Claude Code에서 비차단 오류이므로,
# 이 스크립트를 못 찾거나 실행에 실패하면 fail-open이다 (의도된 동작).

set -u

INPUT=$(cat)
CMD=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
[ -n "$CMD" ] || exit 0

# `git ... commit`이 명령 위치에 있을 때만 반응한다.
# 문자열 안의 "git commit"(예: grep -r "git commit")은 명령 위치가 아니므로 걸리지 않는다.
# 놓치는 쪽(fail-open)이 오차단보다 안전하다 — 위협 모델은 게으른 스킵이지 회피가 아니다.
printf '%s' "$CMD" \
  | grep -qE '(^|[;&|(][[:space:]]*)git[[:space:]]+([^[:space:]]+[[:space:]]+){0,4}commit([[:space:]]|$)' \
  || exit 0

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
GIT_DIR=$(git rev-parse --absolute-git-dir 2>/dev/null) || exit 0

# ── 면제 (G-02): 저작 커밋이 아닌 경우 ──────────────────────────────────
# 충돌 해소·리베이스·체리픽·리버트·bisect 중에는 사용자가 새 코드를 쓰는 게 아니라
# 기존 커밋을 재적용하는 중이다. 여기서 검사를 돌리면 순수 마찰이다.
for marker in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD BISECT_LOG; do
  [ -e "$GIT_DIR/$marker" ] && exit 0
done
[ -d "$GIT_DIR/rebase-merge" ] && exit 0
[ -d "$GIT_DIR/rebase-apply" ] && exit 0

# ── 게이트 1: 객관 체크 — 모든 커밋 ────────────────────────────────────
# 모델이 못 꾸미는 exit code에 게이트를 바인딩한다.
# ("리뷰가 좋았음"이 아니라 "객관 검증이 실제로 통과했음")
#
# 검사기가 감지되는데 checks.sh가 없으면 **차단하지 않고 여기서 생성한다.**
# 차단하면 사용자가 마찰을 피하려 opt-out을 눌러 게이트가 영구히 꺼진다.
# 생성하면 마찰 0으로 게이트가 켜지고, 부수 효과로 **삭제가 더 이상 opt-out이 아니게 된다**
# (다음 커밋에서 hook이 다시 만든다). opt-out은 오직 가시적 마커뿐이다.
HOOK_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || exit 0
# shellcheck source=./checks-lib.sh
. "$HOOK_DIR/checks-lib.sh" 2>/dev/null || exit 0

CHECKS_STATE=$(wigtn_checks_state "$ROOT")

# opt-out은 끌 수 있되 **조용히** 꺼지지 않는다. 커밋마다 사유를 다시 보여준다.
if [ "$CHECKS_STATE" = "optout" ]; then
  echo "WIGTN: 객관 게이트 OFF — $ROOT/$WIGTN_OPTOUT_FILE" >&2
  echo "  사유: $(wigtn_optout_reason "$ROOT")" >&2
  echo "  되돌리기: 이 파일을 삭제한다." >&2
fi

# 감지됐지만 없음 → 지금 만든다 (차단하지 않는다)
if [ "$CHECKS_STATE" = "missing" ]; then
  if bash "$HOOK_DIR/scaffold-checks.sh" >/dev/null 2>&1 && [ -x "$ROOT/.wigtn/checks.sh" ]; then
    echo "WIGTN: 검사기를 감지해 .wigtn/checks.sh를 생성했다. 이제 커밋마다 실행된다." >&2
    echo "  내용 조정: .wigtn/checks.sh 편집 · 끄기: $ROOT/$WIGTN_OPTOUT_FILE 에 사유를 적는다" >&2
    CHECKS_STATE=present
  fi
fi

if [ "$CHECKS_STATE" = "present" ] && [ -x "$ROOT/.wigtn/checks.sh" ]; then
  if ! ( cd "$ROOT" && ./.wigtn/checks.sh >/tmp/wigtn-checks.log 2>&1 ); then
    echo "BLOCKED: WIGTN 객관 체크 실패 (.wigtn/checks.sh)." >&2
    echo "  로그: /tmp/wigtn-checks.log" >&2
    echo "  해결: 검사를 통과시키거나, 검사 내용을 조정하려면 .wigtn/checks.sh를 편집한다." >&2
    echo "  이 프로젝트에서 끄려면: $ROOT/$WIGTN_OPTOUT_FILE 에 사유를 한 줄 적는다 (git status에 보인다)." >&2
    exit 2
  fi
fi

# ── 게이트 2: 리뷰 PASS 아티팩트 — 파이프라인 커밋만 ────────────────────
if printf '%s' "$CMD" | grep -qE 'Quality Gate: PASS|Quality Score:'; then
  if [ -z "$(find "$ROOT/.wigtn/gate-pass" -mmin -30 2>/dev/null)" ]; then
    echo "BLOCKED: 커밋 메시지가 품질 게이트 통과를 주장하지만 WIGTN PASS 기록이 없다." >&2
    echo "  필요한 파일: $ROOT/.wigtn/gate-pass (30분 이내)" >&2
    echo "  해결: /auto-commit 품질 게이트를 실행한다." >&2
    echo "  긴급 핫픽스: --no-review (Quality Gate: PASS 줄을 생략). 객관 체크는 그래도 실행된다." >&2
    exit 2
  fi
fi

exit 0
