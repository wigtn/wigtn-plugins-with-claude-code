# V3 semantic confirmation results

| Arm | semantic /100 | completeness | correctness | feasibility | traceability | concision | judge blockers | judge high |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| M56-CURRENT | 89.2 | 4.00 | 3.50 | 3.50 | 4.00 | 2.83 | 0 | 5 |
| M56-V2 | 89.2 | 3.83 | 3.83 | 3.83 | 3.83 | 2.50 | 0 | 3 |
| M56-V3 | 90.8 | 3.83 | 3.33 | 3.67 | 4.00 | 3.33 | 0 | 6 |

## Frozen gates

| Gate | Result |
|---|---|
| semantic_noninferiority_vs_current_minus_5 | PASS |
| concision_not_below_v2 | PASS |

## Dual-judge defect consensus

- create-backend-webhook / M56-CURRENT: blocker consensus=no; high consensus=no; counts=[0, 0]/[0, 0]
- create-backend-webhook / M56-V2: blocker consensus=no; high consensus=no; counts=[0, 0]/[0, 0]
- create-backend-webhook / M56-V3: blocker consensus=no; high consensus=no; counts=[0, 0]/[0, 2]
- create-mobile-expense / M56-CURRENT: blocker consensus=no; high consensus=no; counts=[0, 0]/[0, 1]
- create-mobile-expense / M56-V2: blocker consensus=no; high consensus=no; counts=[0, 0]/[3, 0]
- create-mobile-expense / M56-V3: blocker consensus=no; high consensus=yes; counts=[0, 0]/[1, 2]
- create-ui-internal / M56-CURRENT: blocker consensus=no; high consensus=yes; counts=[0, 0]/[2, 2]
- create-ui-internal / M56-V2: blocker consensus=no; high consensus=no; counts=[0, 0]/[0, 0]
- create-ui-internal / M56-V3: blocker consensus=no; high consensus=no; counts=[0, 0]/[1, 0]

- no V3 consensus blocker: PASS
