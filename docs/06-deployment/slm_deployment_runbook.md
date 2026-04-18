# SLM Deployment Runbook

**Last Updated:** YYYY-MM-DD  
**Owner:** AI Infra

## Pre‑Deployment Checklist
- [ ] Model evaluated and metrics meet threshold.
- [ ] Model binary uploaded to GCS.
- [ ] Inference service Docker image built and pushed.

## Deployment Steps (via GitLab CI)
1. Merge PR with model version bump in `config/slm_version.txt`.
2. Pipeline automatically:
   - Downloads model from GCS.
   - Runs a **canary deployment** (5% traffic for 30 min).
   - Compares latency/error rate vs current production.
3. If canary passes, promote to 100% (manual approval step).

## Rollback
```bash
# Revert the version file and re‑run the deploy job
git revert <commit> && git push
```

## Monitoring
- Dashboard: [Link to Grafana SLM Dashboard]
- Alerts: #alerts-ai Slack channel
