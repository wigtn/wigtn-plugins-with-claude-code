#!/usr/bin/env bash
# 검사기 감지 — gate.sh(fail-closed 판정)와 scaffold-checks.sh(생성)가 공유한다.
#
# 감지가 hook 안에 살아야 하는 이유: 감지를 프롬프트가 하면 "검사기가 있었는가"를
# 모델이 고르게 된다. fail-closed의 전제가 무너진다.
#
# 감지 조건은 항상 두 개다 — (1) 설정 파일이 있고 (2) 러너 바이너리가 PATH에 있다.
# (2)가 없으면 감지하지 않는다. 툴이 설치되지 않은 환경에서 커밋을 막지 않기 위함이다.

# wigtn_detect_checks <repo_root>
# 실행 가능한 검사 명령을 한 줄에 하나씩 stdout으로 출력한다. 없으면 아무것도 출력하지 않는다.
wigtn_detect_checks() {
  local root="$1"

  # Node / TypeScript
  if [ -f "$root/package.json" ] && command -v npm >/dev/null 2>&1; then
    grep -q '"typecheck"' "$root/package.json" 2>/dev/null && echo 'npm run typecheck'
    grep -q '"lint"'      "$root/package.json" 2>/dev/null && echo 'npm run lint'
  elif [ -f "$root/tsconfig.json" ] && command -v npx >/dev/null 2>&1; then
    echo 'npx --no-install tsc --noEmit'
  fi

  # Python
  if [ -f "$root/pyproject.toml" ] || [ -f "$root/setup.cfg" ]; then
    command -v ruff  >/dev/null 2>&1 && echo 'ruff check .'
    command -v mypy  >/dev/null 2>&1 && [ -f "$root/mypy.ini" ] && echo 'mypy .'
  fi

  # Go
  if [ -f "$root/go.mod" ] && command -v go >/dev/null 2>&1; then
    echo 'go vet ./...'
  fi

  # Rust
  if [ -f "$root/Cargo.toml" ] && command -v cargo >/dev/null 2>&1; then
    echo 'cargo check --quiet'
  fi

  # Makefile — 명시적 lint/check 타겟이 있을 때만
  if [ -f "$root/Makefile" ] && command -v make >/dev/null 2>&1; then
    grep -qE '^lint:'  "$root/Makefile" 2>/dev/null && echo 'make lint'
    grep -qE '^check:' "$root/Makefile" 2>/dev/null && echo 'make check'
  fi
}

# opt-out 마커 경로. **저장소 루트**에 둔다 — `.wigtn/`는 gitignore라 그 안에 두면
# 게이트를 끈 사실이 `git status`에도 diff에도 안 나타난다. 게이트를 끄는 행위는
# 사람이 볼 수 있어야 한다("끌 수 없게"는 위협 모델상 불가능하므로, 차선은 "끄면 보이게").
WIGTN_OPTOUT_FILE=".wigtn-optout"

# wigtn_optout_reason <repo_root>
# opt-out이 유효하면 사유를 출력하고 0을 반환한다. 아니면 1.
# 마커는 **비어 있으면 안 된다** — 사유 없는 opt-out은 받지 않는다.
wigtn_optout_reason() {
  local f="$1/$WIGTN_OPTOUT_FILE"
  [ -f "$f" ] || return 1
  local reason
  reason=$(grep -v '^[[:space:]]*#' "$f" 2>/dev/null | grep -v '^[[:space:]]*$' | head -1)
  [ -n "$reason" ] || return 1
  echo "$reason"
}

# wigtn_checks_state <repo_root>
# 게이트가 알아야 할 상태 하나를 출력한다:
#   optout    — 사용자가 사유를 적어 명시적으로 껐다
#   present   — .wigtn/checks.sh가 있고 실행 가능하다
#   missing   — 검사기는 감지되는데 checks.sh가 없다  (→ 그 자리에서 생성한다)
#   none      — 감지되는 검사기가 없다 (무마찰)
wigtn_checks_state() {
  local root="$1"
  wigtn_optout_reason "$root" >/dev/null && { echo optout; return; }
  [ -x "$root/.wigtn/checks.sh" ]         && { echo present; return; }
  [ -n "$(wigtn_detect_checks "$root")" ] && { echo missing; return; }
  echo none
}
