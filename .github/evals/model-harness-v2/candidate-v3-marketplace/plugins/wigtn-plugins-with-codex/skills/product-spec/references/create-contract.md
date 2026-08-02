# PRD Create Contract

Use the smallest implementation-ready contract. Preserve the three applicability row names and table shapes below so a deterministic validator can check them. Each conditional row is `Required` or `N/A` with a concrete reason.

```markdown
# <Feature> PRD
## Applicability
| Contract | Required / N/A | Evidence |
|---|---|---|
| Pages/routes or screen IDs |  |  |
| Empty/loading/error/success/recovery state matrix |  |  |
| Mermaid user or system flow |  |  |
## Context and problem
## Goals
## Non-goals
## Users, roles, and permissions
## Functional requirements
| ID | Requirement | Priority |
## Pages and routes              <!-- user-visible screens only -->
| Page or screen ID | Route, deep link, or explicit TBD + owner | Roles | Purpose |
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

- Pages/routes or stable screen IDs, and the state matrix: a user-visible feature. Never replace the route/screen-ID contract with prose; if routing is genuinely unknown, write `TBD`, its owner, and decision point in the table.
- Mermaid flow: a multi-step user or system lifecycle.
- Numeric NFR: only when evidence supports the target. Otherwise name the metric, owner, and decision point.

Requirements describe necessary behavior, not preferred implementation unless the constraint is real. Avoid duplicate FRs and ACs, speculative enterprise policy, exhaustive edge-case catalogs, and open decisions that do not change implementation or release.
