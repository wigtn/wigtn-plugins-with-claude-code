# Model × Harness Study

Publication report: [REPORT.md](REPORT.md)

## Reproduce

Prerequisites:

- Codex CLI authenticated with GPT‑5.5 and GPT‑5.6 Sol access
- local marketplace at `.codex-plugin-staging`
- Python 3 and standard Unix shell tools

```bash
bash .github/evals/model-harness-2026/run-study.sh
bash .github/evals/model-harness-2026/run-supplement.sh
bash .github/evals/model-harness-2026/run-judges.sh
python3 .github/evals/model-harness-2026/score_judges.py \
  .github/evals/model-harness-2026
python3 .github/evals/model-harness-2026/analyze_effects.py \
  .github/evals/model-harness-2026
bash .github/evals/model-harness-2026/run-live-triggers.sh
```

All runners are resumable: a non-empty output file is not regenerated.
