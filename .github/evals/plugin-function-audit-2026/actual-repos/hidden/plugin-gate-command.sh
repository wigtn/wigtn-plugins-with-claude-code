#!/usr/bin/env bash
set -u
root=$1
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
for command in \
  '/usr/local/bin/git commit -m x' \
  'command -- git commit -m x' \
  'env -i MODE=test git commit -m x' \
  'true && git --no-pager commit -m x' \
  $'true;\n git -C . commit -m x'
do
  invoke "$command"
  [ "$?" -eq 2 ] || { echo "missed: $command"; exit 1; }
done
for command in \
  'echo git commit -m x' \
  'printf "git commit -m x"' \
  'grep -R git.commit .' \
  'python3 -c "print(\"git commit\")"' \
  'git status'
do
  invoke "$command"
  [ "$?" -eq 0 ] || { echo "false block: $command"; exit 1; }
done
echo "hidden command-position cases: PASS"
