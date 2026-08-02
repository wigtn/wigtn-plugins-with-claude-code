# Blind implementation quality results

| Arm | quality /100 | completeness | correctness | scope | maintainability | evidence | blockers | high |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| IM-M56-BARE | 93.1 | 3.62 | 3.38 | 4.00 | 3.75 | 3.88 | 1 | 4 |
| IM-M56-ORDINARY | 93.1 | 3.88 | 3.62 | 3.62 | 3.62 | 3.88 | 0 | 2 |
| IM-M56-VERIFIED | 94.4 | 3.62 | 3.38 | 4.00 | 4.00 | 3.88 | 1 | 2 |
| IM-M55-VERIFIED | 82.5 | 3.50 | 2.75 | 3.50 | 3.00 | 3.75 | 0 | 11 |

## Dual-judge consensus

- config-migration / IM-M56-BARE: blocker=no; high=yes; counts=[0, 0]/[1, 1]
- config-migration / IM-M56-ORDINARY: blocker=no; high=no; counts=[0, 0]/[0, 0]
- config-migration / IM-M56-VERIFIED: blocker=no; high=no; counts=[0, 0]/[0, 1]
- config-migration / IM-M55-VERIFIED: blocker=no; high=no; counts=[0, 0]/[0, 2]
- expense-approval / IM-M56-BARE: blocker=no; high=yes; counts=[0, 1]/[1, 1]
- expense-approval / IM-M56-ORDINARY: blocker=no; high=yes; counts=[0, 0]/[1, 1]
- expense-approval / IM-M56-VERIFIED: blocker=no; high=no; counts=[0, 1]/[1, 0]
- expense-approval / IM-M55-VERIFIED: blocker=no; high=yes; counts=[0, 0]/[2, 4]
- tenant-search / IM-M56-BARE: blocker=no; high=no; counts=[0, 0]/[0, 0]
- tenant-search / IM-M56-ORDINARY: blocker=no; high=no; counts=[0, 0]/[0, 0]
- tenant-search / IM-M56-VERIFIED: blocker=no; high=no; counts=[0, 0]/[0, 0]
- tenant-search / IM-M55-VERIFIED: blocker=no; high=yes; counts=[0, 0]/[1, 2]
- webhook-delivery / IM-M56-BARE: blocker=no; high=no; counts=[0, 0]/[0, 0]
- webhook-delivery / IM-M56-ORDINARY: blocker=no; high=no; counts=[0, 0]/[0, 0]
- webhook-delivery / IM-M56-VERIFIED: blocker=no; high=no; counts=[0, 0]/[0, 0]
- webhook-delivery / IM-M55-VERIFIED: blocker=no; high=no; counts=[0, 0]/[0, 0]
