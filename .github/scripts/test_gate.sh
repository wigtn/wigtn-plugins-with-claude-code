#!/usr/bin/env bash
# 커밋 게이트 회귀 테스트 (hooks/gate.sh).
#
# 모델을 호출하지 않으므로 100% 결정론이다 — 실제 git 저장소 픽스처 위에서
# gate.sh를 돌려 exit code만 본다. 게이트 동작을 바꾸는 PR은 여기서 막힌다.
#
# 실행: bash .github/scripts/test_gate.sh

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
GATE="$REPO_ROOT/plugins/wigtn-plugins/hooks/gate.sh"
TMP=$(mktemp -d)
PASS=0; FAIL=0

trap 'rm -rf "$TMP"' EXIT

setup_repo() {
  rm -rf "$TMP/repo"; mkdir -p "$TMP/repo"; cd "$TMP/repo" || exit 1
  git init -q .
  git config user.email t@example.com; git config user.name t
  echo x > a.txt; git add a.txt; git commit -qm init
  mkdir -p .wigtn
}
mk_checks() { # $1 = exit code
  printf '#!/usr/bin/env bash\nexit %s\n' "$1" > .wigtn/checks.sh
  chmod +x .wigtn/checks.sh
}
run() { # $1 = 커맨드 문자열 -> exit code 출력
  printf '{"tool_input":{"command":%s}}' "$(printf '%s' "$1" | jq -Rs .)" \
    | bash "$GATE" >/dev/null 2>&1
  echo $?
}
check() { # $1 설명  $2 기대  $3 실제
  if [ "$2" = "$3" ]; then echo "  ok   $1"; PASS=$((PASS+1));
  else echo "  FAIL $1 (기대 exit $2, 실제 $3)"; FAIL=$((FAIL+1)); fi
}

echo "== 게이트 1: 객관 체크는 모든 커밋에 (G-01 핵심) =="
setup_repo; mk_checks 1
check "checks 실패 + Quality Score 없음 -> 차단" 2 "$(run 'git commit -m "fix"')"
check "checks 실패 + Quality Score 있음 -> 차단" 2 "$(run 'git commit -m "fix

Quality Score: 85"')"
setup_repo; mk_checks 0
check "checks 통과 -> 허용"                     0 "$(run 'git commit -m "fix"')"
setup_repo
check "checks.sh 없음 -> 허용 (무마찰)"         0 "$(run 'git commit -m "fix"')"

echo "== 우회 시도: 메시지 조작으로 객관 체크를 끌 수 있는가 =="
setup_repo; mk_checks 1
check "Quality Score 줄 생략"        2 "$(run 'git commit -m "fix"')"
check "git commit -F msg.txt"        2 "$(run 'git commit -F msg.txt')"
check "git commit --amend --no-edit" 2 "$(run 'git commit --amend --no-edit')"
check "git -C . commit"              2 "$(run 'git -C . commit -m x')"
check "cd sub && git commit"         2 "$(run 'cd /tmp && git commit -m x')"

echo "== 게이트 2: gate-pass는 Quality Score 커밋만 =="
setup_repo; mk_checks 0
check "Quality Score 있음 + gate-pass 없음 -> 차단" 2 "$(run 'git commit -m "x

Quality Score: 85"')"
check "Quality Score 없음 + gate-pass 없음 -> 허용" 0 "$(run 'git commit -m "x"')"
touch .wigtn/gate-pass
check "Quality Score 있음 + 신선한 gate-pass -> 허용" 0 "$(run 'git commit -m "x

Quality Score: 85"')"

echo "== G-02 면제: 정상 워크플로가 막히지 않는가 =="
setup_repo; mk_checks 1; touch .git/MERGE_HEAD
check "머지 충돌 해소 중 -> 면제" 0 "$(run 'git commit -m merge')"
setup_repo; mk_checks 1; mkdir -p .git/rebase-merge
check "리베이스 진행 중 -> 면제"  0 "$(run 'git commit -m x')"
setup_repo; mk_checks 1; touch .git/CHERRY_PICK_HEAD
check "체리픽 중 -> 면제"         0 "$(run 'git commit -m x')"
setup_repo; mk_checks 1; touch .git/REVERT_HEAD
check "리버트 중 -> 면제"         0 "$(run 'git commit -m x')"

echo "== 오차단 방지: 커밋이 아닌 명령 =="
setup_repo; mk_checks 1
check 'grep -r "git commit" .' 0 "$(run 'grep -r "git commit" .')"
check 'echo "git commit 방법"' 0 "$(run 'echo "git commit 방법"')"
check 'git status'             0 "$(run 'git status')"
check 'git log --oneline'      0 "$(run 'git log --oneline')"

echo "== --no-verify는 Claude Code hook을 우회하지 못한다 =="
check "git commit --no-verify"          2 "$(run 'git commit --no-verify -m x')"
check "git commit -n"                   2 "$(run 'git commit -n -m x')"

echo "== opt-out 마커 (삭제가 아니라 존재로 opt-out) =="
setup_repo; mk_checks 1; echo "긴급 핫픽스 기간" > .wigtn-optout
check "사유 있는 .wigtn-optout -> 면제" 0 "$(run 'git commit -m x')"
setup_repo; mk_checks 1; : > .wigtn-optout
check "빈 .wigtn-optout -> 무효 (사유 필수)" 2 "$(run 'git commit -m x')"
setup_repo; mk_checks 1; mkdir -p .wigtn; touch .wigtn/checks-optout
check "구 경로(.wigtn/checks-optout) -> 무효" 2 "$(run 'git commit -m x')"

echo "== G-03: 감지 + 자동 생성 (차단이 아니라 생성) =="
mk_makefile() { # $1 = lint 타겟 exit code
  printf 'lint:\n\t@exit %s\n' "$1" > Makefile
}
if command -v make >/dev/null 2>&1; then
  setup_repo; mk_makefile 0
  rc=$(run 'git commit -m x')
  check "검사기 감지 + checks.sh 없음 -> 생성 후 통과" 0 "$rc"
  check "  실제로 생성됐는가" "yes" "$([ -x .wigtn/checks.sh ] && echo yes || echo no)"

  setup_repo; mk_makefile 1
  check "검사기 감지 + 검사 실패 -> 차단" 2 "$(run 'git commit -m x')"

  # 삭제가 더 이상 opt-out이 아니다 — hook이 다시 만든다
  setup_repo; mk_makefile 1
  run 'git commit -m x' >/dev/null
  rm -f .wigtn/checks.sh
  check "checks.sh 삭제 -> 재생성되어 여전히 차단" 2 "$(run 'git commit -m x')"

  # opt-out 마커는 감지를 이긴다
  setup_repo; mk_makefile 1; echo "이 저장소는 CI에서만 검사" > .wigtn-optout
  check "opt-out 마커 > 감지 -> 허용"     0 "$(run 'git commit -m x')"
  check "  opt-out 시 생성하지 않는다"    "no" "$([ -e .wigtn/checks.sh ] && echo yes || echo no)"
else
  echo "  skip (make 없음)"
fi

setup_repo
check "감지되는 검사기 없음 -> 무마찰" 0 "$(run 'git commit -m x')"
check "  생성하지 않는다" "no" "$([ -e .wigtn/checks.sh ] && echo yes || echo no)"

echo
echo "결과: $PASS 통과 / $FAIL 실패"
[ "$FAIL" -eq 0 ]
