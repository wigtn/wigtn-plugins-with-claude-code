# Function-level evidence and reform decision

> Pre-reform classification. Evidence references the frozen studies under
> `.github/evals/`. Grades follow `PROTOCOL.md`.
>
> **Scope note:** Claude sections below are assessment and migration
> recommendations only. The Claude plugin was not reformed in this work. Actual
> implementation changes apply only to the Codex v0.2 candidate under
> `.codex-plugin-staging/`.

## Claude plugin agents — assessment only, unchanged

| Function | Evidence | Grade | Decision | Reform |
|---|---|---:|---|---|
| `code-reviewer-lean` | Findings contract; 33 hook and 59 contract regressions support its gate boundary | B | Keep | One review schema: severity, evidence, impact, check; no score |
| `code-reviewer` | Generic 100-point rubric showed no stable benefit; overlaps lean reviewer | B− | Merge | Remove from default routes and manifest after references migrate |
| `pr-reviewer` | PR workflow exists; no repeated end-to-end posting study | C | Keep narrowly | Read-only default, evidence findings, explicit approval before posting |
| `prd-reviewer` | PRD v4: 51 model calls and deterministic contract/omission checks | A | Keep as contract verifier | Verify WIGTN output contract; do not award subjective quality scores |
| `design-discovery` | Design-direction behaviour was 2 repetitions; bare also passed 100% | B− | Narrow | Project-native evidence and options only; no fake suitability percentages |
| `code-formatter` | No direct benefit study; formatter/linter exit codes are deterministic | D | Remove from default | Run repository formatter/linter directly |
| `architecture-decision` | No `/implement` agent-level ablation | D | Explicit-only | Use only for a named consequential architecture decision |
| `backend-architect` | Generic framework capability; no isolated gain | D | Explicit-only | Invoke only when user asks for backend architecture analysis |
| `frontend-developer` | Generic framework/design capability; no isolated gain | D | Explicit-only | Preserve only WIGTN-specific design references |
| `mobile-developer` | Generic framework capability; no isolated gain | D | Explicit-only | No automatic routing |
| `ai-agent` | Provider integration knowledge changes quickly; no isolated gain | D | Explicit-only | Prefer current provider docs; no automatic routing |
| `parallel-digging-coordinator` | 893-line pipeline, no quality/latency ablation | D | Experimental | Never default; require explicit parallel deep-dive request |
| `parallel-review-coordinator` | 566-line pipeline, no repeated advantage over one evidence reviewer | D | Experimental | Never default; use only for high-risk explicit multi-review |
| `team-build-coordinator` | 671-line orchestration; no repository E2E advantage study | D | Experimental | Never default; require separable work and explicit team request |

## Claude plugin commands — assessment only, unchanged

| Function | Evidence | Grade | Decision | Reform |
|---|---|---:|---|---|
| `/prd` | GPT-5.5/5.6 PRD contract studies; v4 51 calls | A | Core | Thin router plus create/review contracts and validator |
| `/auto-commit` | 90 calls; 5.6 bare made 3/3 vague-request commits, plugin 0/3; hook 33/33 | A | Core | Keep authority and objective checks; remove ceremonial scoring/orchestration |
| `/implement` | 48 calls: all arms passed visible/hidden tests; verified cost +22.2% tokens | B | Core but thin | Direct implementation default; explicit verification; no default teams |
| `/screen-spec` | Small behaviour study and five-artifact format contract | B | Keep | Thin router to templates; no default frontend-agent review |
| `/review-pr` | Static contract only; posting path not behaviour-tested | C | Keep narrowly | Read-only findings by default; posting requires explicit user authority |

## Claude plugin skills and hooks — assessment only, unchanged

| Function | Evidence | Grade | Decision | Reform |
|---|---|---:|---|---|
| `screen-spec` | Output-contract behaviour, small sample | B | Keep | Retain templates; shorten trigger instructions |
| `handdrawn-diagram` | Format-specific behaviour, 2 repetitions | B | Keep | Retain render verification |
| `wigtn-ppt` | WIGTN brand contract improved 50%→100% in 2 repetitions | B | Keep | Retain brand-only scope; add larger visual QA later |
| `design-system-reference` | Bare tied plugin on small design task | B− | Reference only | Load only selected style; do not auto-inject all 20 |
| `code-review-levels` | No isolated effect; duplicates reviewer prose | D | Merge | Replace with one findings schema/reference |
| `team-memory-protocol` | No isolated effect or long-running recovery study | D | Experimental | Explicit multi-agent only; no default files |
| commit gate | 33/33 deterministic regressions | A | Core | Keep objective checks and visible opt-out |
| dangerous-command blocker | Static hook contract; limited adversarial coverage | B | Keep | Add quoted/wrapper command regression cases |
| Write/Edit reminder | No evidence; fires on every edit | D | Remove | Let commands route formatting/review when needed |
| Stop reminder | No evidence; user-visible noise | D | Remove | Delete |

## Codex plugin skills

| Function | Evidence | Grade | Decision | Reform |
|---|---|---:|---|---|
| `product-spec` | PRD v4 51 calls; contract and validator results | A | Core | Keep concise entrypoint and deterministic validator |
| `release-readiness` | Auto Commit 90 calls | A | Core | Preserve exact action/authority boundary |
| `verified-delivery` | 48 implementation calls; +1.3 blind points from 8 judge calls, no deterministic pass gain | B− | Reform and retest | Risk-first tests, diff review, requirement-evidence closeout |
| `acceptance-verifier` | Contract behaviour sample; no broad repository study | B | Core | Keep read-only matrix and explicit confidence |
| `screen-spec` | Small output-contract study | B | Keep | Preserve five-artifact contract |
| `handdrawn-diagram` | Small format-specific study | B | Keep | Preserve source + render validation |
| `wigtn-presentation` | Small brand-contract study | B | Keep | Brand-only; require visual QA |
| `design-direction` | Bare tied plugin in small sample | B− | Keep narrow | Existing-system discovery, no style invention by default |

## Cold conclusion before new calls

The defensible core is not a general-purpose “agent harness.” It is a small set
of WIGTN-specific contracts and safety boundaries: product specification,
acceptance evidence, screen/brand artifacts, explicit verified delivery, and
release authority. Generic specialist personas and default parallel orchestration
are unproven overhead and should not be advertised as quality improvements.
