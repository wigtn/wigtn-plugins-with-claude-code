---
name: release-readiness
description: Safely review, verify, commit, push, or open a pull request when the user asks in natural language such as “커밋해줘”, “푸시해줘”, “PR 올려줘”, or “커밋 준비해줘”. Preserve unrelated changes and execute only the requested Git scope. Do not use for ordinary implementation or vague “완료해줘”.
---

# Release Readiness

Interpret the user’s sentence as the authority boundary.

## Request mapping

- **“리뷰해줘”**: review and report only. Do not stage or commit.
- **“커밋 준비해줘”**: inspect, verify, and propose the exact scope and message. Do not commit.
- **“커밋해줘”**: inspect, verify, stage only in-scope files, and commit.
- **“푸시해줘”**: inspect status, run needed checks, and push the current intended branch; commit only if the request or context clearly includes committing the current changes.
- **“PR 올려줘”**: verify and perform the necessary in-scope commit and push, then create the PR.
- **“구현해줘”**: not a release request. Do not capture it and do not perform Git mutations.

When wording is ambiguous about a consequential mutation, stop before that mutation and ask.

## Workflow

1. Read repository instructions. Inspect `git status`, branch, upstream, staged diff, unstaged diff, and untracked files.
2. Separate task changes from pre-existing or unrelated user work. Never silently include unrelated files.
3. Review for correctness, regression, security, and missing tests. Findings need severity, confidence, file/line, and impact.
4. Run relevant repository-defined verification. Record exact commands and results.
5. Execute only the mapped action. Use non-interactive Git commands and preserve hooks unless the user explicitly asks otherwise.
6. Report commit hash, pushed branch, or PR URL only after success.

Read [Git safety](references/git-safety.md) before any staging, commit, push, or PR operation. Never force-push, hard-reset, delete branches, amend, or rewrite history without explicit authorization.
