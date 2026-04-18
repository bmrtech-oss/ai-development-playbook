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

---

## Incident Response Drills

We conduct **quarterly incident response drills** to ensure our processes work under pressure and team members stay familiar with the runbook.

### Drill Schedule

- **Frequency:** Quarterly (Q1, Q4, Q7, Q10)
- **Duration:** 2 hours
- **Format:** Simulated incident with real-time response
- **Participants:** Full on-call rotation + observers

### Drill Scenarios

We rotate through these scenarios to cover different failure modes:

1. **Database Outage** (Q1)
   - Simulate PostgreSQL primary failure
   - Test failover to read replica
   - Verify data consistency

2. **SLM Inference Failure** (Q4)
   - Simulate model loading errors
   - Test fallback to baseline model
   - Verify graceful degradation

3. **VS Code Extension Crash** (Q7)
   - Simulate extension runtime errors
   - Test auto-restart mechanisms
   - Verify user experience continuity

4. **CI/CD Pipeline Break** (Q10)
   - Simulate GitLab CI failures
   - Test rollback procedures
   - Verify deployment safety nets

### Drill Process

1. **Preparation (30 min)**
   - On-call engineer briefed on scenario
   - Observers assigned monitoring roles
   - Chat channels set up for communication

2. **Execution (60 min)**
   - Scenario triggered at random time
   - On-call responds per runbook
   - Observers note process gaps

3. **Debrief (30 min)**
   - Timeline review
   - Process improvements identified
   - Action items assigned

### Success Criteria

- **Response SLA met:** Alert acknowledged within 5 min
- **Communication clear:** Stakeholders updated every 15 min
- **Mitigation effective:** Service restored within target time
- **Postmortem complete:** Documented within 48 hours

### Drill Results

| Quarter | Scenario | Response Time | Issues Found | Status |
|---------|----------|---------------|--------------|--------|
| Q1 2026 | Database Outage | 4 min | 2 minor | ✅ Passed |
| Q4 2025 | SLM Inference | 6 min | 1 major | ⚠️ Passed w/ issues |
| Q3 2025 | Extension Crash | 3 min | 0 | ✅ Passed |

**Next drill:** Q4 2026 (Database Outage) - Scheduled for 2026-10-15
