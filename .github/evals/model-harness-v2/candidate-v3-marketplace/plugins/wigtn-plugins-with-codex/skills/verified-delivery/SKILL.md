---
name: verified-delivery
description: Run the complete WIGTN implementation-and-verification workflow when explicitly invoked as $verified-delivery. Use only for an intentional end-to-end delivery request; never auto-invoke for ordinary coding, PRD writing, review, commit, push, or PR requests.
---

# Verified Delivery

This is an explicit-only delivery workflow. The user’s invocation authorizes implementation and proportionate local verification, not unrelated external mutations.

## Workflow

1. Establish goal, applicable requirements, constraints, repository instructions, and done criteria.
2. Inspect repository structure and adjacent code before choosing an approach.
3. For small work, implement directly. For complex work, maintain a short execution plan without creating ceremonial documents.
4. Make the minimum coherent change using existing patterns. Preserve unrelated user edits.
5. Run relevant repository-defined tests, typechecks, lint, build, and browser checks in proportion to risk.
6. When a PRD or acceptance criteria exists, apply the evidence rules from [delivery evidence](references/delivery-evidence.md).
7. Report changed files, executed verification, unresolved risk, and any requirements that remain unverified.

## Authority boundary

Do not create a commit, push, open a PR, create an issue, deploy, install dependencies, or alter remote state unless the user separately and explicitly asks for that action. Never use destructive rollback to discard a mixed dirty worktree.
