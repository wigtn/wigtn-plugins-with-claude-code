# Excluded unqualified-skill pilot

The initial Implement launch used `$verified-delivery`, matching the skill's own
documentation. In an installed plugin, Codex exposes the skill under the
qualified name `$wigtn-plugins-with-codex:verified-delivery`. The model reported
that the unqualified skill did not exist, so the intended treatment was absent.

- completed model calls: 1
- interrupted or partially collected calls: 4
- analyzable treatment outputs: 0
- archived raw artifacts: `runs-discarded-unqualified-skill/`
- correction: fix the plugin description/UI prompt and runner to use the
  qualified invocation, then restart every arm in fresh repositories
- production implication: the old documented invocation was itself a plugin
  integration defect

The pilot is excluded from the registered 48-call sample. Its first hidden-test
failure is not attributed to the skill because the log proves the skill was not
loaded.

## Discovery preflight

A second preflight used the qualified name but made no model calls. It showed
that `policy.allow_implicit_invocation: false` removes the skill from the CLI's
available-skills catalog entirely. The artifacts are preserved in
`runs-discarded-hidden-explicit-skill/`.

The candidate now sets discovery to `true` while retaining explicit-only
trigger language in the skill description. This is necessary for raw CLI
invocation; the ordinary-plugin arm measures whether making it discoverable
causes unwanted auto-invocation.

## Ambiguous acceptance pilot

After discovery was fixed, the first completed expense-approval attempts from
three arms all treated a repeated identical decision as an idempotent success.
The prompt said both “transition only once” and “duplicate calls do not add
audit,” while the hidden test required `ValueError`. That requirement was
ambiguous.

- completed calls: 3
- interrupted or partially collected calls: 4
- analyzable registered outputs: 0
- archived raw artifacts: `runs-discarded-ambiguous-double-decision/`
- correction: state explicitly that every decision after the first raises
  `ValueError` while leaving audit unchanged

During the same pre-registration audit, `attempt < 1` and Python `bool` limits
were made explicit because hidden tests distinguish those cases. All four arms
restart from fresh repositories; no result from the ambiguous wording is used.
