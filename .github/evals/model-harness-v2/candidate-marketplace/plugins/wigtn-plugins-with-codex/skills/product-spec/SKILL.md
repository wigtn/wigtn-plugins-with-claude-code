---
name: product-spec
description: Create, review, or deeply analyze implementation-ready PRDs. Use for “PRD 뽑아줘”, “PRD 검토해줘”, “PRD 디깅해줘”, product requirements, specs, acceptance criteria, feasibility, security, edge-case, or contradiction review. Do not use for ordinary implementation, minor fixes, or general code review.
---

# Product Spec

Turn product intent into a traceable implementation contract. Do not make PRD work a gate for ordinary coding.

## Mode

- **Create:** read [create contract](references/create-contract.md). Draft only applicable sections. Mark every conditional contract `Required` or `N/A` with evidence.
- **Review:** read [review contract](references/review-contract.md). Emit its contract-audit table before semantic findings. Do not rewrite the PRD unless asked.
- **Deep dive:** read the review contract and [deep-dive guide](references/deep-dive.md). Inspect repository evidence when available and label facts, inferences, and open questions.

## Rules

- Use stable requirement IDs and observable acceptance criteria.
- Treat server authorization, ownership, and tenancy as product behavior where applicable. UI hiding is not authorization.
- Do not invent scale, SLA numbers, architecture, analytics, or compliance requirements without evidence.
- Ask only about decisions that materially change the result and cannot be safely inferred. Record reversible assumptions and continue.
- Preserve source documents unless the user asks to edit them.
- Order review findings by impact and cite exact sections or requirement IDs. More findings are not inherently better.
- When a PRD is saved, run `python3 scripts/validate-prd.py <path>` from this skill directory. Report validator failures; do not silently weaken the contract.

## Completion

Return the artifact or findings, important assumptions, unresolved decisions, and validator result when run. Do not claim validation beyond inspected evidence.
