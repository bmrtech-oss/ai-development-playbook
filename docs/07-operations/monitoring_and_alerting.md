# Monitoring & Alerting Playbook

**Last Updated:** 2026-04-18  
**Owner:** SRE / Platform Team

## Overview

All services emit metrics and structured logs. We monitor for anomalies, alert on-call, and maintain dashboards for visibility. **Every alert must have a runbook.**

---

## Metrics Stack

- **Collection:** Prometheus scrapes `localhost:9090/metrics` every 30s.
- **Storage:** 15-day retention in Prometheus; long-term in GCS.
- **Visualization:** Grafana dashboards.
- **Alerting:** Alertmanager routes to Slack, PagerDuty.

---

## Key Metrics by Service

### Backend (Python FastAPI)

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| `http_request_duration_seconds` (p95) | < 200ms | > 500ms |
| `http_requests_total` (errors) | < 0.1% | > 1% |
| `slm_inference_latency_ms` (p99) | < 150ms | > 200ms |
| `slm_token_usage_total` | Monitor spend | > $500/day increase |
| `vector_search_latency_ms` (p95) | < 200ms | > 500ms |
| `database_connection_pool_free` | Monitor exhaustion | < 2 connections |

### Frontend (VS Code Extension)

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| `extension_activation_time_ms` | < 500ms | > 1000ms |
| `ui_render_latency_ms` (LCP) | < 1200ms | > 2000ms |
| `extension_crash_count` | 0 | > 0 in production |
| `message_latency_ms` (IPC between extension & backend) | < 50ms | > 200ms |

### Infrastructure

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| `pod_cpu_usage_percent` | 50-70% (headroom) | > 85% |
| `pod_memory_usage_percent` | 50-70% | > 85% |
| `disk_free_percent` | > 20% | < 10% |
| `node_up` | 1 (healthy) | 0 (down) |

---

## Prometheus Configuration

`prometheus.yml`:

```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 15s
  external_labels:
    env: "prod"

scrape_configs:
  - job_name: "backend"
    static_configs:
      - targets: ["localhost:8000"]
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance

  - job_name: "inference"
    static_configs:
      - targets: ["inference.default.svc.cluster.local:9090"]

  - job_name: "database"
    static_configs:
      - targets: ["postgres-exporter.default.svc.cluster.local:9187"]
```

### Metrics Emission (Python)

```python
from prometheus_client import Counter, Histogram, Gauge
import time

request_latency = Histogram('http_request_duration_seconds', 'HTTP request latency')
slm_tokens = Counter('slm_token_usage_total', 'SLM tokens consumed', ['model', 'type'])
inference_latency = Histogram('slm_inference_latency_ms', 'SLM inference time')

@app.get("/api/v1/complete")
@request_latency.time()  # Automatically measure latency
async def complete(prompt: str):
    start = time.time()
    result = model.infer(prompt)
    inference_latency.observe((time.time() - start) * 1000)
    
    slm_tokens.labels(model="v2.3.1", type="input").inc(len(prompt.split()))
    slm_tokens.labels(model="v2.3.1", type="output").inc(len(result.split()))
    
    return result
```

---

## Alert Rules

`alert-rules.yml`:

```yaml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 2m
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }}"
          runbook_url: "https://playbook.example.com/runbooks/high-error-rate"

      - alert: HighInferenceLatency
        expr: histogram_quantile(0.99, slm_inference_latency_ms) > 200
        for: 5m
        annotations:
          summary: "SLM inference slow (p99 > 200ms)"
          runbook_url: "https://playbook.example.com/runbooks/slow-inference"

  - name: cost_alerts
    rules:
      - alert: UnexpectedTokenUsageSpike
        expr: |
          rate(slm_token_usage_total[1h]) > 
          avg_over_time(rate(slm_token_usage_total[1h] offset 7d)[7d:1h]) * 1.5
        for: 10m
        annotations:
          summary: "Token usage 50% above weekly average"
          runbook_url: "https://playbook.example.com/runbooks/token-spike"

  - name: infra_alerts
    rules:
      - alert: PodCrashLooping
        expr: rate(container_last_seen[15m]) < 1
        for: 5m
        annotations:
          summary: "Pod {{ $labels.pod }} is crash-looping"
          runbook_url: "https://playbook.example.com/runbooks/pod-crash-loop"
```

---

## Dashboards

### Dashboard 1: Service Health

```
┌─────────────────────────────────────────────┐
│ Service Health Overview                     │
├─────────────────────────────────────────────┤
│ API Error Rate (%)        │ 0.02% ✅        │
│ SLM Inference p99 (ms)    │ 145ms ✅        │
│ Database Pool Free        │ 12/20 ✅        │
│ Active Requests           │ 234             │
│ Uptime                    │ 99.98%          │
└─────────────────────────────────────────────┘
```

Created in Grafana using queries:
```
- `rate(http_requests_total{status=~"5.."}[5m])`
- `histogram_quantile(0.99, slm_inference_latency_ms)`
- `pg_stat_activity_idle`

Auto-refresh: 30s
Alert state indicators: Red (triggered) / Yellow (warning) / Green (ok)
```

### Dashboard 2: Cost Tracking

```
┌──────────────────────────────────────────┐
│ AI/ML Cost Dashboard                     │
├──────────────────────────────────────────┤
│ Daily Spend: $847 (↑ 12% from last week) │
│ Token Rate: 2.1M tokens/hour              │
│ GPU Utilization: 72%                     │
│ Projected Monthly: $24,890                │
│ Budget: $25,000 (99% utilization)        │
└──────────────────────────────────────────┘
```

---

## Alerting Rules (Severity & Routing)

### Severity Levels

| Level | Response Time | Escalation | Example |
|-------|---------------|------------|---------|
| **Critical** | 5 min | Page on-call | API down, data loss |
| **High** | 15 min | Slack + #incidents | 50% error rate, inference 3x slow |
| **Medium** | 1 hour | Slack only | Memory usage 85%, minor service degradation |
| **Low** | Next business day | Daily digest | Deprecated endpoint usage, minor bugs |

### Slack + PagerDuty Routing

```yaml
# alertmanager.yml
route:
  receiver: slack-default
  group_by: ['alertname', 'cluster']
  
  routes:
    - match:
        severity: critical
      receiver: pagerduty-oncall
      repeat_interval: 5m
      group_wait: 10s
    
    - match:
        severity: high
      receiver: slack-incidents
      repeat_interval: 30m
    
    - match:
        severity: medium
      receiver: slack-default
      repeat_interval: 4h
    
    - match:
        severity: low
      receiver: daily-digest
      group_wait: 12h

receivers:
  - name: slack-default
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_INCIDENTS}'
        channel: '#monitoring'

  - name: pagerduty-oncall
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
        description: '{{ .GroupLabels.alertname }}'

  - name: slack-incidents
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_INCIDENTS}'
        channel: '#incidents'
```

---

## Runbooks (Alert Response)

Every alert must link to a runbook.

### Example Runbook: High Error Rate

**Alert:** `HighErrorRate` triggered  
**On-Call:** @you

```markdown
## 1. Triage (2 min)
- Check Slack alert for affected service (API / SLM / Vector DB)
- Go to Grafana: https://grafana.example.com/d/api-health
- Check recent deployments: https://github.com/org/repo/deployments/prod

## 2. Immediate Mitigation (5 min)
- If recent deploy: `kubectl rollout undo deployment/api`
- If database issue: Check connection pool: `SELECT count(*) FROM pg_stat_activity;`
- If SLM issue: Check GPU memory: `nvidia-smi`

## 3. Investigation (10 min)
- Check logs: `kubectl logs -f deployment/api --tail=100`
- Look for patterns: Specific endpoint? User cohort? Time of day?
- Query recent errors:
  \`\`\`
  SELECT timestamp, endpoint, error_message 
  FROM error_logs 
  WHERE created_at > now() - interval '10 minutes' 
  ORDER BY created_at DESC LIMIT 100;
  \`\`\`

## 4. Communication
- Post in #incidents: "🔴 High error rate on API. Investigating. ETA 10 min."
- Update every 5 min if ongoing.

## 5. Resolution
- Apply fix (code, config, or restart)
- Verify error rate drops: `rate(http_requests_total{status=~"5.."}[5m]) < 0.001`
- Clear alert in Alertmanager

## 6. Post-Incident
- Write postmortem: https://playbook.example.com/postmortems/
- Update monitoring: Did we miss a warning sign? Add a new alert.
- PR to fix root cause.
```

---

## Log Aggregation

- **Tool:** Loki (Prometheus-compatible log storage).
- **Collection:** Fluent-Bit ships logs from containers.
- **Query interface:** Grafana Explore.

### Sample Query (Loki)

```promql
{job="api"} 
| json 
| status >= 500 
| stats count() by status
```

Returns: Count of errors by HTTP status code.

### Structured Logging (Python)

```python
import structlog

logger = structlog.get_logger()

@app.get("/api/v1/complete")
async def complete(prompt: str):
    logger.info(
        "inference_request",
        prompt_length=len(prompt),
        user_id=current_user.id,
        trace_id=request.headers.get("X-Trace-ID"),
    )
    try:
        result = model.infer(prompt)
        logger.info(
            "inference_success",
            output_length=len(result),
            latency_ms=elapsed,
        )
        return result
    except Exception as e:
        logger.error(
            "inference_failed",
            error=str(e),
            exception_type=type(e).__name__,
        )
        raise
```

---

## SLO / SLI Tracking

### Service-Level Indicator (SLI)

Example: "99.9% of API requests complete in < 500ms"

```promql
# SLI Query
histogram_quantile(0.999, 
  rate(http_request_duration_seconds_bucket[5m])
) < 0.5
```

### Service-Level Objective (SLO)

- API: 99.9% uptime, < 500ms latency p99
- SLM Inference: 99.5% uptime, < 200ms latency p99
- Vector Search: 99% uptime, < 300ms latency p95

**Error budget:** If SLI tracks below SLO, page on-call. If tracking above, team can do risky deployments.

---

## Dashboard Links (Bookmark These)

- **Grafana Home:** https://grafana.example.com
- **Service Health:** https://grafana.example.com/d/service-health
- **Cost Dashboard:** https://grafana.example.com/d/cost-tracking
- **SLM Metrics:** https://grafana.example.com/d/slm-performance
- **Loki Log Explorer:** https://grafana.example.com/d/loki-logs
- **Alertmanager:** https://alertmanager.example.com

---

## Monthly Review

On the first Tuesday of each month:
1. Review SLI performance vs. SLO.
2. Did we page on-call unnecessarily? Adjust alert thresholds.
3. Are there gaps in monitoring? Add new metrics.
4. Cost anomalies? Investigate and optimize.
5. Update this document if processes change.
