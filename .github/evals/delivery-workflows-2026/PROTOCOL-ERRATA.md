# Protocol errata

> Recorded 2026-07-27, before any Implement or blind-judge model call.

`PROTOCOL.md` §C says candidates are relabeled “A/B/C” in one sentence. There are
four Implement arms, so the intended and implemented labels are **A/B/C/D**, as
the following sentence, `make_prompts.py`, and the human protocol all specify.

This is an editorial correction only. It does not change an arm, fixture,
selection rule, metric, or gate. The frozen original is left untouched so its
manifest hash remains reproducible.

## Installed-plugin skill name

`PROTOCOL.md` uses the short label `$verified-delivery`. Before the registered
Implement sample, a pilot showed that an installed plugin requires the
qualified invocation `$wigtn-plugins-with-codex:verified-delivery`. The
unqualified pilot was stopped and excluded because no skill treatment was
delivered. The plugin's own description/UI prompt and runner were corrected,
and all four arms restart from fresh repositories. See
`implement/PILOT-NOTE.md`.

The next no-model preflight found that `allow_implicit_invocation: false`
removed the explicit-only skill from the CLI catalog. The candidate changes
this to `true` so it can be selected, while its description remains
explicit-only. The ordinary-plugin arm is the registered non-interference test
for accidental invocation.

## Hidden-test wording

An expense pilot exposed ambiguity between “transition once” and “duplicate
calls do not add audit.” Three independent attempts chose idempotent repeated
decisions, while the hidden test expected `ValueError`. Those runs were
excluded. The prompt now explicitly requires `ValueError` after any prior
decision and unchanged audit. It also explicitly states two type/range
boundaries already enforced by hidden tests: `attempt < 1` is invalid and
`limit` excludes `bool`. No hidden implementation or expected output was added
to the model-visible repository.
# v4 PRD preflight

The first v4 PRD command stopped before any model call because its no-model
preflight expected the complete skill body inside `debug prompt-input`.
Implicitly invokable skills expose their catalog description there and are read
after routing, so that assertion could never hold. The repaired preflight checks
the qualified catalog entry in prompt input and separately checks the installed
cached `SKILL.md` for the two v4 contract markers. A fresh temporary plugin home
is used. No analysis result was excluded because no model call had started.

The v4 runner later completed all 14 GPT-5.5 calls but hit Bash `set -u` while
expanding an empty final batch (14 is exactly divisible by the batch size of
two). The GPT-5.6 arm continued. The runner now guards the final loop with a
non-empty length check. Completed output and metadata are reused by filename;
no completed model call is repeated and no treatment or score changes.
