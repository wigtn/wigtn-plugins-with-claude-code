# PRD Deep-dive Guide

Deep diving challenges the PRD; it does not merely proofread it.

1. **Repository fit** — compare proposed routes, data, APIs, components, tests, deployment, and conventions to the actual repository.
2. **Opposing hypotheses** — identify plausible reasons the problem statement, chosen scope, or proposed solution may be wrong.
3. **Boundary and abuse cases** — permissions, tenancy, privacy, injection, replay, rate limits, idempotency, destructive actions, and recovery where applicable.
4. **Lifecycle** — migration, backward compatibility, rollout, rollback, observability, support, and data retention.
5. **State space** — concurrency, partial failure, latency, empty data, stale data, offline behavior, retries, duplicates, and cancellation.
6. **Verification** — ensure each important claim can be proven by a test, metric, artifact, or manual check.

Label each statement as `Fact`, `Inference`, or `Open question`. Finish with a prioritized change proposal, not an automatic rewrite.
