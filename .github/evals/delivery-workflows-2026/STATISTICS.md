# Statistical appendix

> Post-specified analysis. Primary gates and fixtures remained frozen. Bootstrap seed `20260727`, 20,000 task-cluster resamples.

## Binomial uncertainty

| Arm | Metric | Result |
|---|---|---:|
| AC-M56-BARE | intended | 27/30 (90.0%; 95% Wilson 74.4%–96.5%) |
| AC-M56-BARE | perfect | 27/30 (90.0%; 95% Wilson 74.4%–96.5%) |
| AC-M56-BARE | safe | 27/30 (90.0%; 95% Wilson 74.4%–96.5%) |
| AC-M56-PLUGIN | intended | 30/30 (100.0%; 95% Wilson 88.6%–100.0%) |
| AC-M56-PLUGIN | perfect | 30/30 (100.0%; 95% Wilson 88.6%–100.0%) |
| AC-M56-PLUGIN | safe | 30/30 (100.0%; 95% Wilson 88.6%–100.0%) |
| AC-M55-PLUGIN | intended | 30/30 (100.0%; 95% Wilson 88.6%–100.0%) |
| AC-M55-PLUGIN | perfect | 30/30 (100.0%; 95% Wilson 88.6%–100.0%) |
| AC-M55-PLUGIN | safe | 30/30 (100.0%; 95% Wilson 88.6%–100.0%) |
| IM-M56-BARE | visible | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |
| IM-M56-BARE | hidden | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |
| IM-M56-BARE | perfect | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |
| IM-M56-ORDINARY | visible | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |
| IM-M56-ORDINARY | hidden | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |
| IM-M56-ORDINARY | perfect | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |
| IM-M56-VERIFIED | visible | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |
| IM-M56-VERIFIED | hidden | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |
| IM-M56-VERIFIED | perfect | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |
| IM-M55-VERIFIED | visible | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |
| IM-M55-VERIFIED | hidden | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |
| IM-M55-VERIFIED | perfect | 12/12 (100.0%; 95% Wilson 75.8%–100.0%) |

Wilson intervals treat trials as Bernoulli observations and can be too narrow when attempts within one fixture are correlated. The paired differences below therefore resample whole task clusters.

## Paired treatment differences

| Contrast | Metric | Difference [95% cluster bootstrap] |
|---|---|---:|
| AC-M56-PLUGIN − AC-M56-BARE | intended | +10.0%p [task-cluster bootstrap +0.0, +30.0] |
| AC-M56-PLUGIN − AC-M56-BARE | perfect | +10.0%p [task-cluster bootstrap +0.0, +30.0] |
| IM-M56-ORDINARY − IM-M56-BARE | hidden | +0.0%p [task-cluster bootstrap +0.0, +0.0] |
| IM-M56-VERIFIED − IM-M56-ORDINARY | hidden | +0.0%p [task-cluster bootstrap +0.0, +0.0] |
| IM-M56-VERIFIED − IM-M56-BARE | perfect | +0.0%p [task-cluster bootstrap +0.0, +0.0] |

These intervals quantify uncertainty in this fixture bank, not the full distribution of production repositories. With only four implementation fixtures, treatment differences smaller than one trial (8.3 percentage points) should be treated as directional.
