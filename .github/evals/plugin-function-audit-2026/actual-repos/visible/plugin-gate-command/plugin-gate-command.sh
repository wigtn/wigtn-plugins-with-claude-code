#!/usr/bin/env bash
set -u
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
gate="$root/plugins/wigtn-plugins/hooks/gate.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp" || exit 1
git init -q
git config user.email eval@example.com
git config user.name eval
printf x > a
git add a
git commit -qm init
mkdir -p .wigtn
printf '#!/usr/bin/env bash\nexit 1\n' > .wigtn/checks.sh
chmod +x .wigtn/checks.sh

invoke() {
  printf '{"tool_input":{"command":%s}}' "$(printf %s "$1" | jq -Rs .)" |
    bash "$gate" >/dev/null 2>&1
}
expect_block() { invoke "$1"; [ "$?" -eq 2 ] || { echo "missed: $1"; exit 1; }; }
expect_allow() { invoke "$1"; [ "$?" -eq 0 ] || { echo "false block: $1"; exit 1; }; }

expect_block '/usr/bin/git commit -m x'
expect_block 'command git commit -m x'
expect_block 'env MODE=test git commit -m x'
expect_block $'printf ready\n&& git commit -m x'
expect_allow 'printf "%s" "git commit -m x"'
expect_allow 'grep -R "git commit" .'
echo "visible command-position cases: PASS"
