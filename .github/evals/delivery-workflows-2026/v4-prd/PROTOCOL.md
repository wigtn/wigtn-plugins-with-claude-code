# v4 PRD confirmatory protocol

> Frozen before v4 model calls, 2026-07-27.

## Treatment

Start from the v3 Product Spec contract. Change only the two observed release
failures:

1. define `Present` as artifact existence and report quality defects separately,
2. cap reviews at five material findings, omit nits, and group medium findings.

The create contract and validator are unchanged in substance. The candidate is
the complete `.codex-plugin-staging` marketplace, not a prompt fragment.

## Arms and calls

- `M56-V4`: `gpt-5.6-sol`, medium — 37 calls
  - three create fixtures × 3
  - clean contract review × 7
  - six single-omission reviews × 3
  - universal review × 3
- `M55-V4`: `gpt-5.5`, medium — 14 calls
  - three create fixtures × 1
  - clean contract review × 3
  - six single-omission reviews × 1
  - universal review × 2

Total: **51 calls**. All calls use fresh ephemeral sessions, isolated homes,
read-only work directories, disabled remote plugins/apps, and the same frozen
fixtures used for v3.

## Gates

| Metric | GPT‑5.6 gate | GPT‑5.5 cross-check |
|---|---:|---:|
| create contract | >= 95% | >= 90% |
| strict validator | 100% | 100% |
| omission recall | >= 90% | no regression below v3 76.7% |
| contract-review accuracy | >= 95% | >= v3 77.1% |
| clean specificity | 7/7 | 3/3 |
| universal defect recall | >= 95% | >= 95% |
| median tokens | <= 15,701 | descriptive |

The 15,701 threshold is the frozen current-plugin median plus 25% from the
earlier release gate. A gate failure blocks the candidate even if other metrics
improve.
