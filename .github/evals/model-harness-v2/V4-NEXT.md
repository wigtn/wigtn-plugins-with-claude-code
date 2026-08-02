# v4 next-change contract

> Status: recommendation from v3 failures; **not implemented or validated**.

## Required changes

### Review audit semantics

- `Present`: the required artifact/section exists in recognizable form.
- `Missing`: the artifact/section does not exist.
- `N/A`: the contract does not apply and the PRD gives evidence.
- A present but incomplete artifact stays `Present`; report incompleteness as a
  semantic finding. Never use `Missing` as a quality score.

### Review output budget

- Report all blockers and highs.
- Merge findings with the same root cause.
- Report at most the five implementation-changing medium findings; summarize the
  remainder in one sentence.
- Do not restate evidence already present in the contract audit.

### Create consistency sweep

- Before completion, compare `Must`/P0 FRs and ACs with assumptions and open
  decisions.
- An unresolved choice cannot coexist with an FR/AC that selects one branch.
- Either resolve it with evidence, or mark the behavior `TBD` with owner,
  decision point, and blocked requirement IDs.

## Minimum confirmation

1. Freeze this file and the candidate hash before calls.
2. GPT‑5.6 clean review: 10 repetitions; specificity lower Wilson bound should be
   reported, not only the point estimate.
3. GPT‑5.6 complete 11-fixture regression: 5 repetitions.
4. Token median must be at most `15,701` on the same workload.
5. Blind semantic comparison of v3/v4 on all three create fixtures with GPT‑5.5
   and GPT‑5.6 judges.
6. Human review of the duplicate-expense policy conflict and other consensus
   highs.
7. Canary on real team PRDs before default promotion.
