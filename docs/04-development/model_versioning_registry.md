# Model Versioning & Registry

**Last Updated:** 2026-04-18  
**Owner:** ML Engineering Team

## Overview

SLM (Small Language Model) versions must be tracked, registered, and deployable/rollbackable like code releases. Every model is versioned, tagged, and has rollback procedures.

---

## Model Registry Schema

All models are registered in the **Model Registry** (GCS bucket: `gs://models-prod/registry/`).

### Metadata (Per Version)

```yaml
# models-prod/registry/slm-code-v2/meta.yaml
name: "slm-code-v2"
version: "2.3.1"
base_model: "mistral-7b-v0.3"
training_date: "2026-04-15"
training_run_id: "mlflow-run-abc123"

# Performance metrics
metrics:
  perplexity_heldout: 4.2
  pass_rate: 0.87
  latency_p50_ms: 45
  latency_p99_ms: 120

# Hardware requirements
hardware:
  min_vram_gb: 8
  inference_framework: "vLLM"
  batch_size_max: 16

# LoRA adapter info (if using adapters)
lora_adapters:
  - name: "python-code-generation"
    size_mb: 256
    merged: false

# Deployment history
deployments:
  - env: "staging"
    deployed_at: "2026-04-16T10:00:00Z"
    status: "active"
  - env: "prod"
    deployed_at: "2026-04-18T14:30:00Z"
    status: "active"
    canary_percent: 10

# Rollback criteria (automatically triggers if exceeded)
rollback_triggers:
  perplexity_threshold: 5.0  # Alert if regression > 19%
  latency_p99_threshold_ms: 150
  error_rate_threshold: 0.05
  accuracy_drop_threshold: 0.03
```

---

## Versioning Scheme

Follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (2.0.0): Architecture change, new base model, breaking API change.
- **MINOR** (2.3.0): Improved metrics, new training data, new features.
- **PATCH** (2.3.1): Bug fix, retraining with same config, performance tuning.

### Tagging Strategy

```bash
# During training
mlflow register_model --name slm-code-candidate \
  --version-source runs/abc123

# Approved for staging (minor release)
gsutil cp gs://models-staging/slm-code-v2.2.0 \
          gs://models-prod/archive/slm-code-v2.2.0

# Tag in Git (for reproducibility)
git tag -a models/slm-code-v2.3.1 \
  -m "SLM Code v2.3.1: +2% pass rate, -5ms latency" \
  <commit-hash>
```

---

## Deployment Procedure: Canary → Gradual Rollout

All model deployments follow this sequence:

### Stage 1: Staging Environment (Day 1)

```bash
# Deploy to staging cluster
kubectl set image deployment/inference-server \
  inference=gcr.io/project/slm-code:v2.3.1 \
  --namespace=staging

# Run integration tests
pytest tests/integration/test_model_inference.py -v
# + manual smoke tests on VS Code extension
```

**Exit criteria:** All tests pass, no crashes, latency similar to previous version.

### Stage 2: Production Canary (Day 2, 10% traffic)

```bash
# Update deployment spec to route 10% to new model
kubectl patch deployment inference-server \
  --patch='{"spec":{"template":{"metadata":{"annotations":{"canary":"slm-code-v2.3.1"}}}}}'

# Traffic split via Istio:
# 90% -> slm-code-v2.3.0
# 10% -> slm-code-v2.3.1
```

**Monitor for 6+ hours:**
- Error rate stays < 0.05%
- Latency p99 < 150ms
- No spike in user-reported issues
- Metrics match staging

### Stage 3: Gradual Rollout (50% by hour 12, 100% by hour 24)

```bash
# Hour 12: Increase to 50%
kubectl patch deployment inference-server --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/metadata/annotations/canary-percent", "value":"50"}]'

# Hour 24: Full rollout
kubectl patch deployment inference-server --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/metadata/annotations/canary-percent", "value":"100"}]'

# Cleanup old deployment pod
kubectl delete rs -l app=inference-server,version=v2.3.0
```

---

## A/B Testing (Optional)

For experimental models, run parallel inference:

```python
# In inference service
if user_id % 100 < 10:  # 10% of users
    result = model_v2_3_1.infer(prompt)  # Experimental
    context["variant"] = "v2.3.1-exp"
else:
    result = model_v2_3_0.infer(prompt)  # Stable
    context["variant"] = "v2.3.0-stable"

log_inference(result, variant=context["variant"])
```

**Metrics to compare:**
- User acceptance (rating, click-through rate)
- Accuracy (automated tests)
- Latency
- Cost (tokens per user, GPU hours)

---

## Automated Rollback Triggers

The system automatically rolls back if:

1. **Perplexity regression > 19%** (e.g., 4.2 → 5.0)
2. **Latency p99 > 150ms** (increase > 25%)
3. **Error rate > 5%**
4. **Accuracy drop > 3%** (on held-out test set)

### Rollback Procedure

```bash
# Triggered by monitoring alert
# On-call engineer confirms via Slack:

# Step 1: Revert to previous version
kubectl rollout undo deployment/inference-server

# Step 2: Verify stability (1 hour)
kubectl get pods -w -l app=inference-server

# Step 3: Post-incident review
# Why did the model fail? Missing test case? Data distribution shift?
```

---

## Model Lifecycle

| Phase | Duration | Owner | Exit Criteria |
|-------|----------|-------|---------------|
| **Training** | 1-2 weeks | ML Eng | Metrics approved, code reviewed |
| **Staging** | 3-7 days | QA + ML Eng | Integration tests pass, latency acceptable |
| **Canary (10%)** | 6+ hours | SRE + On-call | Error rate < 0.05%, metrics stable |
| **Gradual Rollout** | 12-24 hours | SRE | Reach 100%, continue monitoring |
| **Production (Stable)** | Until superseded | SRE | Monitor for regressions, plan next version |

---

## Fallback: Manual Inspection

If automated monitoring detects anomalies, on-call can:

```bash
# Inspect model inference directly
kubectl exec -it deploy/inference-server -- bash
python -c "
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained('gs://models-prod/slm-code-v2.3.1')
output = model.generate('def hello')
print(output)
"

# Check inference logs
kubectl logs -f deploy/inference-server --tail=100
```

---

## Cost Tracking

Each model version tracks inference cost:

```yaml
slm-code-v2.3.1:
  gpu_hours_per_1m_requests: 2.5
  estimated_monthly_cost_at_1m_requests: $500
  total_served_requests: 150000
  total_cost_to_date: $75

slm-code-v2.3.0:
  gpu_hours_per_1m_requests: 2.7  # +8% more expensive
  reason: "Slightly larger adapter, worth the latency gain"
```

---

## Retention Policy

- **Current production version:** Retained indefinitely.
- **Previous 2 versions:** Retained for quick rollback (30 days).
- **Older versions:** Archived to cold storage (GCS Nearline) after 90 days.
- **Experimental versions:** Deleted after 14 days if not promoted.

---

## Cross-References

- Training guidelines: [SLM Training Guidelines](slm_training_guidelines.md)
- Evaluation: [SLM Evaluation Harness](../05-testing/slm_evaluation_harness.md)
- Cost: [AI Cost Management](../01-discovery/ai_cost_modeling.md)
- Deployment: [GitLab CI + OpenTofu Guide](../06-deployment/gitlab_ci_opentofu_guide.md)
