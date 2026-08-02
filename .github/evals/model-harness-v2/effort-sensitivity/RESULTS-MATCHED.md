# GPT-5.6 v2 effort sensitivity — matched metrics

> Post-hoc mechanical correction: the frozen scorer filtered quality to repeats 1–3
> but calculated the medium token/time medians over repeats 1–5. This table uses
> the same first three repeats for every quality and resource metric. Quality
> values are unchanged.

| Effort | create | contract review | universal review | tokens median | duration median |
|---|---:|---:|---:|---:|---:|
| medium | 93/117 (79.5%) | 125/126 (99.2%) | 13/15 (86.7%) | 12,180 | 123s |
| low | 95/117 (81.2%) | 125/126 (99.2%) | 14/15 (93.3%) | 14,564 | 117s |

Low effort was not inferior on these deterministic checks, but it did not reduce
token use in this sample. The study was not powered as a formal non-inferiority
test and does not justify replacing medium for all tasks.
