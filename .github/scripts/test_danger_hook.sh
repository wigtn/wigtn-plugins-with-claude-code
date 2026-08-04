#!/usr/bin/env bash
# 위험 명령 훅 회귀 테스트 (hooks.json PreToolUse).
#
# 정규식을 눈으로 읽고 판단하지 않는다 - hooks.json 에서 명령을 그대로 뽑아
# 실제 JSON -> shell -> grep 이스케이프 체인을 태우고 exit code만 본다.
# 이 정규식은 두 번 연속 실측 없이 수정됐다가 미탐/오탐을 남겼다.
#
# 위험 명령을 실행하지 않는다. 훅에 문자열로 건네 판정만 받는다.
#
# 실행: bash .github/scripts/test_danger_hook.sh

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
HOOKS="$REPO_ROOT/plugins/wigtn-plugins/hooks/hooks.json"
PASS=0; FAIL=0

CMD=$(jq -r '.hooks.PreToolUse[0].hooks[0].command' "$HOOKS")
if [ -z "$CMD" ] || [ "$CMD" = "null" ]; then
  echo "hooks.json 에서 PreToolUse 명령을 읽지 못했다"; exit 1
fi

verdict() { # $1 = 검사할 커맨드 문자열 -> exit code
  printf '{"tool_input":{"command":%s}}' "$(printf '%s' "$1" | jq -Rs .)" \
    | sh -c "$CMD" >/dev/null 2>&1
  echo $?
}

blocked() { # $1 = 커맨드 (차단되어야 함)
  local got; got=$(verdict "$1")
  if [ "$got" = "2" ]; then echo "  ok   차단  | $1"; PASS=$((PASS+1))
  else echo "  FAIL 통과됨(미탐) | $1"; FAIL=$((FAIL+1)); fi
}

allowed() { # $1 = 커맨드 (통과해야 함)
  local got; got=$(verdict "$1")
  if [ "$got" = "0" ]; then echo "  ok   통과  | $1"; PASS=$((PASS+1))
  else echo "  FAIL 차단됨(오탐) | $1"; FAIL=$((FAIL+1)); fi
}

echo "== 미탐: 홈/루트 전체 삭제는 형태와 무관하게 막는다 =="
blocked 'rm -rf /'
blocked 'rm -rf /*'
blocked 'rm -rf ~'
blocked 'rm -rf ~/'
blocked 'rm -rf ~/*'
blocked 'sudo rm -rf /'
blocked 'rm -fr /'
blocked 'rm -r -f /'
blocked 'rm -f -r /'
blocked 'rm --recursive --force /'
echo "-- 인용 형태 (구 정규식이 전부 통과시키던 구간) --"
blocked 'rm -rf "$HOME"'
blocked "rm -rf '\$HOME'"
blocked 'rm -rf $HOME'
blocked 'rm -rf $HOME/'
blocked 'rm -rf ${HOME}'
blocked 'rm -rf "${HOME}"'
blocked 'rm -rf "/"'
blocked "rm -rf '/'"
blocked 'rm -rf "$HOME"/*'
echo "-- 플래그가 앞에 끼는 형태 --"
blocked 'rm --no-preserve-root -rf /'
blocked 'rm -v -rf /'

echo
echo "== 미탐: 그 외 파괴적 명령 =="
blocked 'git push --force origin main'
blocked 'git push -f origin main'
blocked 'git reset --hard HEAD~3'
blocked 'DROP DATABASE prod'
blocked 'drop database prod'
blocked 'DROP TABLE users'
blocked 'Drop Schema app'

echo
echo "== 오탐: 정상 작업을 막지 않는다 =="
allowed 'rm -rf /tmp/build-cache'
allowed 'rm -rf /var/folders/xx/T/scratch'
allowed 'rm -rf ~/Dev/project/dist'
allowed 'rm -rf "$HOME/Library/Caches/app"'
allowed 'rm -rf $HOME/tmp'
allowed 'rm -rf node_modules'
allowed 'rm -rf ./dist'
allowed 'rm -rf build/'
allowed 'rm -rf "$HOME_BACKUP"'
allowed 'rm file.txt'
allowed 'git push origin main'
allowed 'git reset --soft HEAD~1'
allowed 'SELECT * FROM users'
allowed 'echo "how to drop a database safely"'

echo
if [ "$FAIL" -gt 0 ]; then
  echo "결과: $PASS 통과 / $FAIL 실패"
  exit 1
fi
echo "결과: $PASS 통과 / 0 실패"
