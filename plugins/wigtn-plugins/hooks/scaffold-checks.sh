#!/usr/bin/env bash
# .wigtn/checks.sh 스캐폴딩 — /auto-commit Step 3.5가 1줄로 호출한다.
#
# 생성기가 번들 스크립트인 이유: 프롬프트 안의 heredoc이면 모델이 매번 그 내용을
# 다시 쓰게 되고, 자기를 심판할 스크립트를 자기가 쓰는 구조가 된다.
#
# 사용: bash "${CLAUDE_PLUGIN_ROOT}/hooks/scaffold-checks.sh"
# 멱등: 이미 존재하면 덮어쓰지 않는다.

set -u
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=./checks-lib.sh
. "$DIR/checks-lib.sh"

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "not a git repo"; exit 0; }

if wigtn_optout_reason "$ROOT" >/dev/null; then
  echo "skip: $WIGTN_OPTOUT_FILE 존재 (객관 체크 opt-out)"
  exit 0
fi
if [ -e "$ROOT/.wigtn/checks.sh" ]; then
  echo "skip: .wigtn/checks.sh 이미 존재 (덮어쓰지 않음)"
  exit 0
fi

CHECKS=$(wigtn_detect_checks "$ROOT")
if [ -z "$CHECKS" ]; then
  echo "skip: 감지된 검사기 없음 (무마찰)"
  exit 0
fi

mkdir -p "$ROOT/.wigtn"
{
  echo '#!/usr/bin/env bash'
  echo '# WIGTN 객관 게이트 (자동 생성). 커밋 직전 hook이 직접 실행하고, non-zero면 차단한다.'
  echo '#'
  echo '# 여기 있는 것은 "모델이 못 꾸미는 것"이어야 한다 — exit code로 말하는 검사만 넣는다.'
  echo '# 전체 테스트를 강제하려면 아래에 추가한다 (단 커밋이 그만큼 느려진다).'
  echo '# 이 게이트를 끄려면: 저장소 루트 .wigtn-optout 에 사유를 한 줄 적는다 (이 파일 삭제가 아니라).'
  echo 'set -e'
  printf '%s\n' "$CHECKS"
} > "$ROOT/.wigtn/checks.sh"
chmod +x "$ROOT/.wigtn/checks.sh"

echo "생성: $ROOT/.wigtn/checks.sh"
printf '%s\n' "$CHECKS" | sed 's/^/  - /'
