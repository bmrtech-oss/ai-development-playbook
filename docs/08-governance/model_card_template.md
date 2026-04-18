# Model Card Template

**Last Updated:** 2026-04-18  
**Owner:** ML Team / AI Governance

## Overview

This template documents AI models used in our platform. Fill out all sections before deploying to production. Store completed cards in the `docs/08-governance/model-cards/` directory.

---

## Model Details

- **Owner:** [Your Name / Team]
- **Version:** [e.g., v1.2.3]
- **Date:** [YYYY-MM-DD]
- **Framework:** [e.g., Llama 3.2, vLLM, transformers]

---

## Intended Use

[Describe the primary use case within the AI Platform tools. Be specific about what tasks this model performs and in what context.]

---

## Out-of-Scope Use

[Explicitly state what the model SHOULD NOT be used for. Examples: Medical advice, Financial decisions, Legal judgments, Personal data analysis beyond what's necessary for the intended use case.]

---

## Training Data & Provenance

[Brief summary of dataset source and any filtering applied. Include: data source (e.g., public datasets, proprietary), size, domain, preprocessing steps, and any known limitations of the training data.]

---

## Performance Metrics

[Link to `promptfoo` eval run ID and key scores. Include: accuracy metrics, toxicity scores, latency benchmarks, and any A/B test results against previous versions.]

---

## Ethical Considerations & Bias

[Document known limitations identified during Red Teaming. Include: bias patterns observed, edge cases that fail, cultural context considerations, and mitigation strategies implemented.]

---

## Deployment Artifact

[Container image SHA or model registry path. Include: registry URL, image tag, model file checksum, and deployment environment requirements.]