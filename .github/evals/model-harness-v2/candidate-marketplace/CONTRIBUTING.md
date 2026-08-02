# Contributing

Keep this plugin thin. Add a workflow only when it carries WIGTN-specific knowledge or repeatable evidence rules that ordinary Codex behavior does not already provide.

## Before submitting changes

1. Keep each `SKILL.md` focused and move detailed templates into `references/` or `assets/`.
2. Put positive triggers and negative boundaries in the skill description.
3. Add positive and negative cases to `tests/trigger-cases.tsv` when invocation behavior changes.
4. Preserve explicit authority boundaries for Git and other external mutations.
5. Run `./scripts/validate.sh`.

Do not add model routing, hooks, MCP servers, or apps without an evaluated product need and the required companion files.
