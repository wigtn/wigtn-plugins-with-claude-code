# Semantic gold results

| Arm | semantic /100 | completeness | correctness | feasibility | traceability | concision | judge blockers | judge high |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| M56-BARE | 83.3 | 4.00 | 3.33 | 3.50 | 3.33 | 2.50 | 0 | 5 |
| M56-CURRENT | 90.8 | 3.67 | 3.83 | 3.50 | 3.83 | 3.33 | 0 | 4 |
| M56-V2 | 88.3 | 4.00 | 3.67 | 3.67 | 3.83 | 2.50 | 0 | 4 |

## Dual-judge defect consensus

- create-backend-webhook / M56-BARE: blocker consensus=no; high consensus=no; counts=[0, 0]/[0, 0]
- create-backend-webhook / M56-CURRENT: blocker consensus=no; high consensus=no; counts=[0, 0]/[0, 1]
- create-backend-webhook / M56-V2: blocker consensus=no; high consensus=no; counts=[0, 0]/[0, 2]
- create-mobile-expense / M56-BARE: blocker consensus=no; high consensus=yes; counts=[0, 0]/[2, 1]
- create-mobile-expense / M56-CURRENT: blocker consensus=no; high consensus=no; counts=[0, 0]/[0, 1]
- create-mobile-expense / M56-V2: blocker consensus=no; high consensus=no; counts=[0, 0]/[2, 0]
- create-ui-internal / M56-BARE: blocker consensus=no; high consensus=no; counts=[0, 0]/[0, 2]
- create-ui-internal / M56-CURRENT: blocker consensus=no; high consensus=no; counts=[0, 0]/[2, 0]
- create-ui-internal / M56-V2: blocker consensus=no; high consensus=no; counts=[0, 0]/[0, 0]
