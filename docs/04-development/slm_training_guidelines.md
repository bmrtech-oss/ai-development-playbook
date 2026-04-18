# SLM Training Guidelines

**Last Updated:** 2026-04-18

## Data Preparation
- Dataset must be versioned (DVC or GCS bucket with timestamp).
- Include a `README` describing the source and any preprocessing.

## Fine‑Tuning
- Use **LoRA** adapters; never modify base model weights unless absolutely necessary.
- Track experiments with **MLflow** or **Weights & Biases**.
- Minimum evaluation metrics before merging a new model:
  - **Perplexity** on held‑out code corpus
  - **Exact Match** on a curated test set
  - **Latency** (p50, p99) on target hardware

## Deployment Checklist
- [ ] Model is registered in our model registry.
- [ ] Rollout plan (canary → 10% → 100%) defined.
- [ ] Monitoring dashboards updated for new model version.

See [Model Versioning & Registry](model_versioning_registry.md) for detailed deployment procedures, canary testing, and rollback criteria.
