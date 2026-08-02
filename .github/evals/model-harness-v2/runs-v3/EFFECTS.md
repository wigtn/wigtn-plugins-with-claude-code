# v3 descriptive effects

> Alias-robust scorer; confirmatory gates remain in `V3-PROTOCOL.md`.

## Arm rates with Wilson intervals

| Family | Arm | Passed | Rate [95% Wilson] |
|---|---|---:|---:|
| create | M56-BARE | 87/195 | 44.6% [37.8%, 51.6%] |
| create | M56-CURRENT | 121/195 | 62.1% [55.1%, 68.6%] |
| create | M56-V2 | 156/195 | 80.0% [73.8%, 85.0%] |
| create | M56-V3 | 194/195 | 99.5% [97.2%, 99.9%] |
| omission-recall | M56-BARE | 2/30 | 6.7% [1.8%, 21.3%] |
| omission-recall | M56-CURRENT | 1/30 | 3.3% [0.6%, 16.7%] |
| omission-recall | M56-V2 | 29/30 | 96.7% [83.3%, 99.4%] |
| omission-recall | M56-V3 | 29/30 | 96.7% [83.3%, 99.4%] |
| contract-review | M56-BARE | 11/210 | 5.2% [2.9%, 9.1%] |
| contract-review | M56-CURRENT | 19/210 | 9.0% [5.9%, 13.7%] |
| contract-review | M56-V2 | 203/210 | 96.7% [93.3%, 98.4%] |
| contract-review | M56-V3 | 207/210 | 98.6% [95.9%, 99.5%] |
| clean-specificity | M56-BARE | 0/5 | 0.0% [0.0%, 43.4%] |
| clean-specificity | M56-CURRENT | 0/5 | 0.0% [0.0%, 43.4%] |
| clean-specificity | M56-V2 | 5/5 | 100.0% [56.6%, 100.0%] |
| clean-specificity | M56-V3 | 4/5 | 80.0% [37.6%, 96.4%] |
| universal | M56-BARE | 25/25 | 100.0% [86.7%, 100.0%] |
| universal | M56-CURRENT | 25/25 | 100.0% [86.7%, 100.0%] |
| universal | M56-V2 | 25/25 | 100.0% [86.7%, 100.0%] |
| universal | M56-V3 | 25/25 | 100.0% [86.7%, 100.0%] |

## Paired fixture-cluster bootstrap

| Family | Comparison | Δ percentage points [95% cluster bootstrap] | Fixture clusters |
|---|---|---:|---:|
| create | v3 − current | +37.4 [+35.4, +38.5] | 3 |
| create | v3 − v2 | +19.5 [+13.8, +24.6] | 3 |
| create | v3 − bare | +54.9 [+46.2, +67.7] | 3 |
| omission-recall | v3 − current | +93.3 [+80.0, +100.0] | 6 |
| omission-recall | v3 − v2 | +0.0 [-10.0, +10.0] | 6 |
| omission-recall | v3 − bare | +90.0 [+76.7, +100.0] | 6 |
| contract-review | v3 − current | +89.5 [+84.8, +94.8] | 7 |
| contract-review | v3 − v2 | +1.9 [-1.9, +8.1] | 7 |
| contract-review | v3 − bare | +93.3 [+88.6, +97.1] | 7 |
| clean-specificity | v3 − current | +80.0 [not estimated: one fixture] | 1 |
| clean-specificity | v3 − v2 | -20.0 [not estimated: one fixture] | 1 |
| clean-specificity | v3 − bare | +80.0 [not estimated: one fixture] | 1 |
| universal | v3 − current | +0.0 [not estimated: one fixture] | 1 |
| universal | v3 − v2 | +0.0 [not estimated: one fixture] | 1 |
| universal | v3 − bare | +0.0 [not estimated: one fixture] | 1 |
