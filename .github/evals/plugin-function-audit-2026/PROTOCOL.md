# WIGTN plugin function audit protocol

> Frozen before the reform and new model calls. Date: 2026-07-27.

## Question

Which WIGTN functions add a measurable product-specific contract, safety
boundary, or output format beyond the base model, and which functions should be
kept, narrowed, merged, made explicit-only, or removed from the default path?

This audit evaluates functions, not file count. A long coordinator is not
valuable merely because it contains more instructions.

## Evidence grades

| Grade | Minimum evidence | Allowed claim |
|---|---|---|
| A | Repeated behavioural evaluation plus deterministic outcome checks | Useful on the tested workload |
| B | Small behavioural sample or deterministic contract regression | Promising; keep with a narrow claim |
| C | Static contract/routing validation only | Structurally valid, effect unknown |
| D | No direct evidence | Experimental; never default-on |

An A grade does not establish universal repository generalisation. Evidence is
attached to a named fixture bank, model, runtime, and date.

## Reform decision rules

1. Keep a default path only when it enforces a product-specific contract,
   external-authority boundary, or deterministic check.
2. Replace prose scoring with findings that include severity, file/line
   evidence, impact, and a reproducible check.
3. Use the base model directly for generic implementation, formatting,
   architecture brainstorming, and framework knowledge.
4. Make parallel coordinators explicit-only until repeated repository-level
   trials show a quality or latency advantage.
5. Put stable rules in scripts or references; keep trigger files short.
6. Do not claim a quality gain when deterministic tests tie. Report the tie and
   measure evidence quality, safety, cost, and variance separately.

## New real-repository study

Three non-toy repository snapshots are used:

- `wigtn-game`: Next.js 16 / React 19 / TypeScript game engines
- `wigtn-introduce`: Next.js 15 / React 19 production homepage
- `wigtn-plugins-with-claude-code`: Bash hooks and Python contract validation

There are two tasks per repository and three independent repetitions per arm.
Primary comparison:

| Arm | Model | Treatment |
|---|---|---|
| `AR-M56-BARE` | `gpt-5.6-sol`, medium | no WIGTN plugin |
| `AR-M56-REFORMED` | `gpt-5.6-sol`, medium | explicit reformed `verified-delivery` |
| `AR-M55-REFORMED` | `gpt-5.5`, medium | same explicit reformed `verified-delivery` |

The primary treatment estimate is the same-model 5.6 comparison. The 5.5 arm is
a cross-model robustness check, not part of that causal treatment contrast.
There are **54 calls** in total. Each call receives a fresh disposable copy, an ephemeral model session, the same
issue text, visible repository checks, an unrelated dirty draft, and no commit
authority. Hidden tests are added only after the model exits. Source repositories
are never mutated.

### Tasks

1. Game timeline validation: malformed values, exact minute set, required text, non-mutation.
2. Game path finding: deterministic shortest path, obstacles, occupancy, bounds.
3. Homepage YouTube parsing: supported hosts/shapes, exact IDs, hostile URLs.
4. Homepage usage URL handling: canonical joins, query/hash rejection, cleanup.
5. Plugin commit detection: shell command positions, wrappers, false positives.
6. Plugin contract diagnostics: deterministic machine-readable success and failures.

### Deterministic gates

- visible checks pass
- hidden checks pass
- frozen tests are unchanged
- unrelated draft is byte-identical
- no commit
- changes remain in the allowed source/test scope
- model exits successfully

The primary unit is the task cluster, not an individual repeated call. Wilson
intervals are descriptive; paired task-cluster bootstrap is used for treatment
differences. Six task clusters are still a limited convenience sample.

## Blind evaluation

For every task, select each arm's median run by hidden result, visible result,
integrity, smaller in-scope patch, then repetition number. Relabel candidates
using a seeded hash. Two model judges receive task, base files, normalized patch,
and deterministic test output but not model/treatment identity, token count, or
duration.

Rubric: functional completeness, invariant/error-path safety, scope discipline,
maintainability, and verification evidence (0–4 each). A separate packet is
generated for two human reviewers. Model judgment is screening evidence and
cannot override a hidden-test failure.

## Publication gate

The report is publishable as an engineering report only if it:

- includes all attempts and scorer errata;
- distinguishes deterministic outcomes, model-judge opinion, and human review;
- reports uncertainty and cost;
- limits claims to the tested repositories and fixture bank;
- labels D-grade functions experimental;
- contains no unsupported model-to-model marketing claim.

It is not a peer-reviewed scientific result and must not claim that the plugin
improves every real repository.
