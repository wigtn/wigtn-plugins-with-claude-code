---
name: acceptance-verifier
description: Verify whether an implementation satisfies PRD requirements or acceptance criteria using code and executed-test evidence. Use for “요구사항 반영됐는지 검증”, “PRD 충족 확인”, requirement coverage, or acceptance verification. Do not use for a general code review or when no requirements can be identified.
---

# Acceptance Verifier

Produce an evidence-backed requirement matrix. This is read-only unless the user also asks to fix gaps.

## Workflow

1. Locate the authoritative PRD, acceptance criteria, issue, or user-provided requirements.
2. Identify the requested implementation scope: working tree, commit, branch comparison, PR, or named files.
3. Extract stable requirement IDs. If none exist, create temporary `AC-01` IDs and say they are local to the report.
4. Inspect implementation and tests. Run the smallest meaningful repository-defined checks when authorized and feasible.
5. Assign exactly one status per requirement:
   - `Satisfied`
   - `Partially satisfied`
   - `Not satisfied`
   - `Not verifiable`
6. Cite code evidence as clickable file and line references. Record commands, exit codes, and relevant test names. Never infer that unexecuted tests passed.
7. Separate issues outside the requirement set under `Out-of-scope findings`.

Use the matrix and decision rules in [evidence matrix](references/evidence-matrix.md).

## Output

| Requirement | Status | Code evidence | Test evidence | Gap |
|---|---|---|---|---|

Follow with executed commands, limitations, and prioritized gaps. A missing test is not automatically a failed requirement; distinguish implementation evidence from verification confidence.
