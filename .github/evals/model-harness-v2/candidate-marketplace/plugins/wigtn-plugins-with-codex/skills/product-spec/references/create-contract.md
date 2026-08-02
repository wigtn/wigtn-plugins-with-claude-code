# PRD Create Contract

Use a compact applicability ledger. Each conditional row is `Required` or `N/A` with a concrete reason.

```markdown
# <Feature> PRD
## Applicability
| Contract | Required / N/A | Evidence |
## Context and problem
## Goals
## Non-goals
## Users, roles, and permissions
## Functional requirements
| ID | Requirement | Priority |
## Pages and routes              <!-- user-visible screens only -->
## State matrix                 <!-- user-visible state only -->
| Surface | Empty | Loading | Error | Success | Recovery |
## User or system flow          <!-- multi-step lifecycle only -->
```mermaid
flowchart TD
```
## Authorization and data boundaries
## Non-functional requirements
## Acceptance criteria
| ID | Requirement | Given | When | Then | Verification |
## Assumptions and open decisions
## Risks and mitigations
## Delivery
| Phase | Requirement IDs | Verifiable exit condition |
```

Always required: problem, goals/non-goals, roles, stable FR IDs, authorization/data boundary, acceptance mapping, risks, open decisions, and FR-mapped delivery.

Conditional:

- Pages/routes and state matrix: a user-visible feature.
- Mermaid flow: a multi-step user or system lifecycle.
- Numeric NFR: only when evidence supports the target. Otherwise name the metric, owner, and decision point.

Requirements describe necessary behavior, not preferred implementation unless the constraint is real.
