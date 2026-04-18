# Data Privacy & "Code Zero" Protocol

## Overview
As a AI Platform, our most valuable asset is the **trust** of our users. The "Code Zero" Protocol defines how we handle, process, and protect user source code. We operate on the principle of **Least Privilege and Zero Retention** for raw source code unless explicitly opted-in by the user.

## Core Principles
1. **Never Train on Private Code by Default:** No user-provided code should ever enter a training set for a global model without explicit, verifiable consent.
2. **Ephemeral Processing:** Code sent for analysis (embeddings, LLM context) should be processed in memory and purged immediately after the session or request.
3. **Local-First Analysis:** Wherever possible, perform static analysis and tree-sitter parsing on the user's local machine (VS Code extension/Electron app).
4. **Anonymization at the Edge:** Strip PII, secrets, and sensitive identifiers from code snippets before sending them to remote SLMs/LLMs.

## Handling User Data
| Data Type | Retention Policy | Storage Location | Encryption |
|-----------|------------------|------------------|------------|
| Raw Source Code | Ephemeral (Session only) | Memory / Secure Temp | TLS 1.3 / AES-256 |
| Embeddings (pgvector) | Account Lifetime | Isolated Tenant DB | AES-256 at rest |
| Search Queries | 30 Days (for CX) | Audit Logs | Anonymized |
| Model Feedback | Permanent (if opted-in) | Training Lake | De-identified |

## The "Code Zero" Checklist for Developers
- [ ] **Secrets Detection:** Does the feature include a pre-flight check to ensure no `.env` or secrets are sent to the backend?
- [ ] **Tenant Isolation:** Are all `pgvector` queries scoped by `tenant_id` at the database level?
- [ ] **Opt-Out Visibility:** Is the "Do not use my data for improvement" toggle easily accessible in the UI?
- [ ] **Log Scrubbing:** Have you verified that `structlog` or standard loggers are not printing code snippets in production?

## Compliance & Auditing

### SOC 2 Type II
- All infrastructure changes affecting data flow must be documented via ADR.
- Security scanning logs retained for 2 years (CloudTrail, GitLab audit logs).
- Access controls enforced via MFA + CloudTrail audit trails.

### GDPR Compliance

We process personal data (source code, which may contain identifiers) under the lawful basis of **Legitimate Interest** (improving developer tools) or **Explicit Consent** (if user opts into model training).

**Key GDPR Obligations:**

| Obligation | Implementation | Response Time |
|-----------|-----------------|----------------|
| **Right to Access** | API endpoint `/user/{id}/data` returns all user data in JSON | Within 30 days |
| **Right to Erasure** | "Delete All My Data" button triggers pgvector cleanup + log purge | Within 72 hours |
| **Right to Portability** | `/user/{id}/export` returns embeddings + metadata in portable format | Within 30 days |
| **Data Processing Agreement (DPA)** | Signed with all sub-processors (GCP, AWS, OpenAI) | Annual review |
| **Privacy Impact Assessment (PIA)** | Completed for any new feature using personal data | Before launch |

**Data Residency:** 
- EU users' data is stored in `eu-central1` (GCP Frankfurt).
- US users in `us-central1`.
- Users can request data export or deletion at any time.

### SOC 2 Control Mapping

| SOC 2 Principle | Control | Evidence |
|-----------------|---------|----------|
| **CC6.1** (Logical Separation) | User data isolated by `tenant_id` in database | Database schema review, tests |
| **CC7.2** (Access Control) | MFA required for production access | AWS CloudTrail logs, access logs |
| **A1.2** (Incident Management) | Postmortem process, blameless culture | Incident database, postmortem docs |
| **CC9.2** (Encryption) | TLS 1.3 for transit; AES-256 at rest | TLS certificates, KMS key audit |

---

## Data Breach Notification

If a data breach occurs:
1. **Assess impact:** Which users? What data? How long was it exposed?
2. **Notify affected users within 72 hours** (GDPR requirement).
3. **Notify regulators** (Data Protection Authority in user's country).
4. **Public statement:** Transparency about what happened and what we're doing.
5. **Post-incident review:** Why? How do we prevent it?
6. **Compensation / credit monitoring** (if applicable).

## Incident Response
Any suspected leak of user code is a **P0 Incident**. Follow the `incident_response_runbook.md` immediately.
