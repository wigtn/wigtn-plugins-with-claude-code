# Excluded sandbox pilot

The first Auto Commit launch used `workspace-write`. Codex could edit worktree
files but the sandbox rejected `.git/index.lock`, making requested commits
impossible independently of model or plugin behavior.

- completed or partially collected attempts: 4
- analyzable treatment outputs: 0
- reason for exclusion: execution environment prevented the primary action
- correction: restart all arms from fresh repositories with
  `danger-full-access`, limited to disposable `/tmp` Git fixtures and local bare
  remotes

The pilot is excluded from the registered 90-call sample.
