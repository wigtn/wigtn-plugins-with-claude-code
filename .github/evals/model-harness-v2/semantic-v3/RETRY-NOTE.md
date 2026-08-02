# Semantic v3 retry note

The first launch at `2026-07-27T06:59:07Z` failed before producing any candidate
judgment:

- J55 / `create-backend-webhook`: exit 1 after 33s
- J56 / `create-backend-webhook`: exit 1 after 33s
- failure: DNS lookup for `wss://chatgpt.com/backend-api/codex/responses`, followed
  by failed HTTPS fallback
- output JSON produced: 0

These attempts contain no model judgment and are excluded from the six-call
analyzable sample. The runner was retried with network access; it overwrote the
same transient log/meta paths and produced six exit-0 JSON judgments. The report
counts completed analyzable calls, not failed transport attempts.
