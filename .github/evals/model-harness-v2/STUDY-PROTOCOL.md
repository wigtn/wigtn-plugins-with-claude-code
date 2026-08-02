# WIGTN Codex Plugin v2 Release-Gate Study

> 사전등록: 모델 실행 전  
> 목적: 현 플러그인을 v2로 교체할 수 있는지 실패영역 중심으로 판정

## Arms

| Arm | Model | Harness |
|---|---|---|
| `M56-BARE` | `gpt-5.6-sol`, medium | none |
| `M56-CURRENT` | `gpt-5.6-sol`, medium | current Codex plugin |
| `M56-V2` | `gpt-5.6-sol`, medium | split create/review contracts + deterministic PRD validator |

## Workload

- PRD create: UI, backend-only, mobile 3 fixtures
- Contract review: gold control plus six one-variable omissions
- Universal review: five labeled universal defects
- repetitions: 5
- total: 11 fixtures × 3 arms × 5 = **165 model calls**

## Isolation

- arm-specific temporary `CODEX_HOME`
- empty work directories outside the repository
- `--ephemeral`, read-only, approval never
- remote plugin and apps disabled
- byte-identical prompt inside each fixture
- prompt-input capture proves WIGTN absence/presence
- every output, log, exit code, duration, token count, and input hash retained

## Primary metrics

1. Create contract satisfaction over 13 frozen criteria
2. Review omission recall: expected missing contract marked `Missing`
3. Review contract table accuracy over all six rows
4. Clean contract specificity: no complete contract marked `Missing`
5. Universal defect recall
6. v2 deterministic validator pass rate on create outputs

## Efficiency

- total tokens from CLI log
- duration
- response lines

## Release gates

All must pass:

1. v2 create contract ≥80%
2. v2 omission recall ≥80%
3. v2 clean contract specificity ≥90%
4. v2 universal defect recall ≥95%
5. v2 validator pass ≥80%
6. no primary metric worse than current by more than 5 percentage points
7. v2 median tokens no more than 25% above current

Semantic blind comparison and human review are separate gates; this study does not substitute format scores for meaning quality.
