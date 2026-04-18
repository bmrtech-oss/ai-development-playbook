# SLM Evaluation Harness

**Last Updated:** 2026-04-18

Our custom harness for benchmarking fine‑tuned SLMs.

## Usage
```bash
python -m ai.evaluate \
  --model-path gs://models/slm-code-v2 \
  --test-suite code-generation \
  --output results.json
```

## Metrics Collected
| Metric | Description |
|:-------|:------------|
| `pass@1` | Functional correctness (unit test passes) |
| `BLEU` | Surface similarity (for refactoring tasks) |
| `CodeBLEU` | Domain‑specific variant |
| `latency_p99_ms` | Tail latency under load |

## Adding a New Test Suite
1. Add `.jsonl` file to `tests/fixtures/ai/`.
2. Implement an evaluator in `ai/evaluators.py`.
3. Update this document.

## Results Dashboard

All evaluation results are logged to Weights & Biases. View the live dashboard:

**Dashboard:** https://wandb.ai/your-org/slm-evaluation/overview

Metrics are also pushed to Prometheus for alerting:
- `slm_pass_rate` (alert if < 0.85)
- `slm_perplexity` (alert if > 5.0)
- `slm_latency_p99_ms` (alert if > 200)
