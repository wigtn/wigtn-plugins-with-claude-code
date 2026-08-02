# GPT-5.5 universal-review robustness follow-up

> Post-hoc protocol frozen after the v4 frozen scorer returned 9/10 and before
> these follow-up model calls.

## Why this follow-up exists

The only failed v4 cross-check was `qualitative_nfr` in
`M55-V4/review-universal.1.md`. The output explicitly said that “충분히 빨라야
한다” is not an observable criterion and recommended p95, target API, and a
measurement environment. The frozen lexical scorer recognized
`기준 ... 없음` but not `기준이 아닙니다`.

The frozen 9/10 result remains published. This follow-up asks whether the
behavior is repeatable under an alias-robust, still deterministic rule.

## Design

- Model: `gpt-5.5`, reasoning effort `medium`
- Treatment: unchanged v4 installed plugin
- Fixture: unchanged `review-universal.txt`
- Calls: 5 fresh ephemeral sessions
- Primary follow-up gate: all five defects in all five calls, 25/25
- The qualitative-NFR check requires the qualitative term near an explicit
  critique such as “관찰 가능한 기준이 아님”, “측정/검증 불가능”, “모호”,
  “정량 기준 필요”, or a concrete percentile/latency correction.
- The follow-up cannot rewrite the frozen v4 result; it is reported separately.
