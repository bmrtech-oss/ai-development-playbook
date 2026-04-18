# Incident Response Runbook

**Last Updated:** 2026-04-18  
**Owner:** On-Call Engineer (rotating)

## On-Call Rotation

The **On-Call Engineer** is responsible for responding to SEV1 & SEV2 incidents.

### Rotation Schedule

- **Weekly rotation:** Mondays 9 AM — Sundays 11 PM (PST)
- **Coverage:** 1 primary on-call, 1 backup
- **Calendar:** [Google Calendar Link](https://calendar.google.com/calendar/u/0?cid=) (internal)

**Current on-call:** Check [#oncall Slack channel](https://slack.com/app_redirect?channel=oncall)

### Escalation Matrix

| Escalation Level | Contact | Response Time | Authority |
|------------------|---------|----------------|-----------|
| **L1 (On-Call)** | @oncall | 5 min | Implement fixes, page on L2 if needed |
| **L2 (Tech Lead)** | @tech-lead | 15 min | Approve risky fixes, coordinate teams |
| **L3 (VP Eng)** | @vp-eng | 30 min | Authorization for rollbacks, resource escalation |

---

## Severity Levels & SLAs

| Level | Impact | Page On-Call? | Response SLA | Resolution Target |
|-------|--------|---------------|--------------|-------------------|
| **SEV1** | Platform down or data loss | ✅ Immediately | 5 min | 1 hour |
| **SEV2** | Major feature broken, no workaround | ✅ Within 15 min | 15 min | 4 hours |
| **SEV3** | Minor bug, workaround available | ❌ Next business day | 1 hour | 1 day |

**Response SLA:** Time until on-call engineer acknowledges and begins investigation.  
**Resolution Target:** Time to restore service (temporary fix acceptable; permanent fix can be later).

## Response Process
1. **Acknowledge** alert in #incidents Slack channel.
2. **Mitigate** – restore service, even if temporary.
3. **Communicate** – update status page and stakeholders.
4. **Resolve** – implement permanent fix.
5. **Postmortem** – blameless document within 48h.

---

## Monitoring & Alerts

See [Monitoring & Alerting Playbook](monitoring_and_alerting.md) for:
- Metric definitions and alerts
- Runbook links for each alert
- SLI/SLO tracking

## Postmortem Template
```markdown
# Incident Postmortem: [Title]

**Date:** YYYY-MM-DD  
**Duration:** X minutes  
**Impact:** ...

## Timeline
...

## Root Cause
...

## Action Items
- [ ] ...
```
