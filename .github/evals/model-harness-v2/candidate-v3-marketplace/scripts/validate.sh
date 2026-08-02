#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
plugin="$repo_root/plugins/wigtn-plugins-with-codex"
codex_home="${CODEX_HOME:-$HOME/.codex}"
plugin_validator="$codex_home/skills/.system/plugin-creator/scripts/validate_plugin.py"
skill_validator="$codex_home/skills/.system/skill-creator/scripts/quick_validate.py"

test -f "$plugin_validator" || { echo "Missing plugin validator: $plugin_validator"; exit 2; }
test -f "$skill_validator" || { echo "Missing skill validator: $skill_validator"; exit 2; }

python3 "$plugin_validator" "$plugin"

skill_count=0
for skill in "$plugin"/skills/*; do
  test -d "$skill" || continue
  python3 "$skill_validator" "$skill"
  skill_count=$((skill_count + 1))
done

test "$skill_count" -eq 8 || { echo "Expected 8 skills, found $skill_count"; exit 1; }
grep -q 'allow_implicit_invocation: false' "$plugin/skills/verified-delivery/agents/openai.yaml"
grep -q '커밋해줘' "$plugin/skills/release-readiness/SKILL.md"
grep -q 'PRD 디깅해줘' "$plugin/skills/product-spec/SKILL.md"

"$repo_root/scripts/run-evals.sh"
echo "Repository validation: PASS"
