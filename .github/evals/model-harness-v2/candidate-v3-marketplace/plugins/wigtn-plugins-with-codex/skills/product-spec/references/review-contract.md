# PRD Review Contract

Before semantic findings, emit this table. Use only `Present`, `N/A`, or `Missing`. `N/A` requires evidence from the PRD.

| Contract | Status | Evidence |
|---|---|---|
| Applicability ledger |  |  |
| Pages and routes |  |  |
| Empty/loading/error/success/recovery state matrix |  |  |
| Mermaid user or system flow |  |  |
| Acceptance precondition/action/result mapped to requirement IDs |  |  |
| Delivery phases mapped to requirement IDs and exit conditions |  |  |

Rules:

- A user-visible feature makes pages/routes and state matrix applicable.
- A multi-step user or system lifecycle makes Mermaid flow applicable.
- Backend-only work must not invent screens.
- `Missing` on an applicable WIGTN contract is a finding even when the rest of the PRD is sound.
- Then review universal quality: contradictions, authorization/data boundaries, state transitions, failure/recovery, unverifiable acceptance, unsupported scope, migration, operations, privacy, and security only where relevant.
- Report findings by `blocker`, `high`, `medium`, `low`; cite exact sections or IDs. Do not use numeric quality scores.
