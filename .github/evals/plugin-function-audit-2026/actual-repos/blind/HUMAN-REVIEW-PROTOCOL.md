# Human blind review protocol

Two reviewers with product-code or security-review experience work independently.
They must not open `BLIND-MAP.json`, run logs, token files, or treatment metadata.

For every task:

1. Read the same issue and deterministic visible/hidden result.
2. Inspect anonymized patches A, B, and C. The order is independently hashed per task.
3. Score each candidate 0–4 on:
   - functional completeness
   - correctness and invariant/error-path safety
   - scope discipline
   - maintainability and repository fit
   - verification quality
4. Record blocker/high findings with exact patch location and triggering scenario.
5. Choose A, B, C, or Tie and confidence `low|medium|high`.

Reviewers submit before discussion. Agreement is raw preference agreement plus
quadratic-weighted agreement on total score. They then resolve only factual
disagreements by inspecting the frozen base repository and tests. The reconciled
result is reported separately; it never replaces the independent submissions.

No human or model score may override a deterministic hidden-test, integrity,
scope, or authority failure.
