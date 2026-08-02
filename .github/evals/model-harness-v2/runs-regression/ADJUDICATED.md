# Post-hoc robustness adjudication

> Frozen primary scores remain authoritative. This file separates lexical scorer/parser misses from behavior misses.

## Universal defect scorer

| Arm | Frozen | Alias-robust |
|---|---:|---:|
| M56-BARE | 25/25 (100.0%) | 25/25 (100.0%) |
| M56-CURRENT | 23/25 (92.0%) | 25/25 (100.0%) |
| M56-V2 | 23/25 (92.0%) | 25/25 (100.0%) |

## Create validator robustness

| Arm | Frozen validator | Alias-robust structure | Strict route identity |
|---|---:|---:|---:|
| M56-BARE | 0/15 (0.0%) | 0/15 (0.0%) | 0/15 (0.0%) |
| M56-CURRENT | 0/15 (0.0%) | 0/15 (0.0%) | 0/15 (0.0%) |
| M56-V2 | 0/15 (0.0%) | 12/15 (80.0%) | 7/15 (46.7%) |

### Strict-validator failure codes

- M56-BARE: applicability=15, acceptance-shape=15, delivery=15, pages-applicability=15, states-applicability=15, flow-applicability=15, problem=6, fr=5, authorization=5, goals=2
- M56-CURRENT: applicability=15, acceptance-shape=15, delivery=15, pages-applicability=15, states-applicability=15, flow-applicability=15, authorization=5
- M56-V2: route-identity=7, flow-applicability=1, flow-section=1, delivery=1
