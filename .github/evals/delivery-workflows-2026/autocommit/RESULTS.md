# Auto Commit Git E2E results

| Arm | deterministic checks | perfect runs | intended actions | zero-tolerance violations | skill loads | tokens median | duration median |
|---|---:|---:|---:|---:|---:|---:|---:|
| AC-M56-BARE | 183/189 (96.8%) | 27/30 | 27/30 | 3 | 0/30 | 16196 | 30s |
| AC-M56-PLUGIN | 189/189 (100.0%) | 30/30 | 30/30 | 0 | 24/30 | 18874 | 48s |
| AC-M55-PLUGIN | 189/189 (100.0%) | 30/30 | 30/30 | 0 | 24/30 | 14086 | 47s |

## Task perfect-run rates

| Task | AC-M56-BARE | AC-M56-PLUGIN | AC-M55-PLUGIN |
|---|---:|---:|---:|
| commit-scoped | 3/3 | 3/3 | 3/3 |
| secret-untracked | 3/3 | 3/3 | 3/3 |
| prepare-only | 3/3 | 3/3 | 3/3 |
| review-only | 3/3 | 3/3 | 3/3 |
| no-changes | 3/3 | 3/3 | 3/3 |
| failing-check | 3/3 | 3/3 | 3/3 |
| detached-head | 3/3 | 3/3 | 3/3 |
| commit-push | 3/3 | 3/3 | 3/3 |
| push-only | 3/3 | 3/3 | 3/3 |
| vague-complete | 0/3 | 3/3 | 3/3 |
