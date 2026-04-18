# Security Scanning & Vulnerability Management

**Last Updated:** 2026-04-18  
**Owner:** SRE / Security Team

## Overview

Every deployment must pass automated security gates. We scan for:
- **SAST (Static Application Security Testing):** Code vulnerabilities, secrets leaks
- **Dependency vulnerabilities:** Python packages, Node.js modules, Docker base images
- **Infrastructure as Code:** OpenTofu/Terraform misconfigurations
- **Container scanning:** Base image CVEs

---

## CI/CD Security Pipeline

All code flowing through GitLab CI must pass these checks **before** merging to `main`.

### Stage: `lint-security`

```yaml
# In .gitlab-ci.yml
security_scan:
  stage: test
  script:
    # Python SAST
    - bandit -r src/ -f json -o bandit-report.json
    - python -m safety check --json > safety-report.json
    
    # TypeScript/JavaScript SAST
    - npm audit --json > npm-audit.json || true
    
    # Secrets scanning
    - git-secrets --scan
    - truffleHog filesystem . --json > truffles-report.json || true
    
    # OpenTofu security
    - tfsec infrastructure/ -format json -o tfsec-report.json || true
  artifacts:
    reports:
      sast: bandit-report.json
      dependency_scanning: safety-report.json
      container_scanning: container-report.json
  allow_failure: false  # Blocking until we reduce false positives
```

### Stage: `build-container`

```yaml
build_container:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - trivy image --severity HIGH,CRITICAL $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  allow_failure: false
```

---

## Tool Configuration

### Python: Bandit + Safety

**Bandit** (code security):
```bash
bandit -r src/ --skip B101  # Ignore assert checks
```

**Safety** (dependency vulns):
```bash
poetry export -f requirements.txt | safety check --stdin
```

Both run on every PR. High/Critical findings block merge.

### Node.js: npm audit + Snyk

```bash
npm audit --audit-level=high
npx snyk test --severity-threshold=high
```

### Secrets: git-secrets + TruffleHog

Register patterns:
```bash
git secrets --install
git secrets --register-aws  # Detect AWS keys
git secrets --add 'api_key.*=.*'
```

**No API keys, credentials, or private URLs in code.** Use environment variables or AWS Secrets Manager.

---

## Dependency Management

### Update Policy

- **Patch updates** (1.2.3 → 1.2.4): Auto-merge if tests pass.
- **Minor updates** (1.2.0 → 1.3.0): Review required; test with integration suite.
- **Major updates** (1.0.0 → 2.0.0): Feature branch, run full suite + manual testing.

### Tools

- **Python:** `poetry update` with lock file tracking.
- **Node.js:** Renovate bot (configured to auto-merge patches, flag majors).
- **Dependencies in Docker:** Alpine base images only. Scan with Trivy.

### Quarterly Audit

On the first Tuesday of each quarter:
1. Run `safety check` on all Python deps.
2. Run `npm audit` on all Node.js deps.
3. Scan all Docker images with Trivy.
4. Create an issue for any Medium+ findings.
5. Generate SBOM (Software Bill of Materials) for customers.

---

## SBOM & Release Artifacts

Every release includes a Software Bill of Materials for compliance & transparency.

### Generation

```bash
# Python
poetry export -f requirements.txt | cyclonedx-bom -i -

# Node.js
npx cyclonedx-npm --output-file sbom-npm.json

# Combined Docker image
syft $CI_REGISTRY_IMAGE:$VERSION -o cyclonedx-json > sbom-docker.json
```

Published to:
- Release page (GitHub / GitLab)
- `https://releases.platform.example.com/sbom/$VERSION.json`

---

## Secret Rotation & Key Management

### API Keys & Credentials

1. **Never commit to code.** Use GitLab/GCP Secrets.
2. **Rotate quarterly** or on key compromise.
3. **Audit access** via CloudTrail (AWS) / Cloud Audit Logs (GCP).

### Database Passwords

- Managed by Secrets Manager (AWS) or GCP Secret Manager.
- Rotated every 6 months.
- On-call engineer has read access; never in code.

### LLM API Keys

- OpenAI, Anthropic keys stored in GCP Secret Manager.
- Access scoped to `ai-inference` service account only.
- Rotated if a key is exposed in logs or reports.

---

## Incident Response

### If a Vulnerability is Found

**P0 (immediate threat):**
1. Tag the incident `security-vulnerability` in GitLab.
2. Create a hotfix branch.
3. Deploy patch to production within 4 hours.
4. Post-incident review (24h).

**P1 (fixable in next release):**
1. Create an issue with label `security`.
2. Target the issue to the next sprint.
3. Coordinate with the Release Manager for expedited release if needed.

### If Secrets Are Exposed

1. **Rotate immediately.** Regenerate any keys/tokens that were leaked.
2. **Audit logs.** Check what access the key allowed during exposure window.
3. **Incident postmortem.** Why did it leak? What can we prevent this?
4. **Update git-secrets patterns** if a new pattern was missed.

---

## Compliance Notes

- **SOC2:** Security scanning logs retained for 2 years (CloudTrail, GitLab audit logs).
- **GDPR:** Secrets never contain personal data. Ensure PII detection in SAST rules.
- **PCI DSS** (if handling payments): Ensure database credentials are never logged.

---

## Monitoring & Reporting

- **Dashboard:** Link to GitLab Security Dashboard showing all vulnerabilities by project/severity.
- **Weekly summary:** Slack notification of new High/Critical findings.
- **Monthly metrics:** Count of vulnerabilities, mean time to remediation (MTTR).

---

## Resources

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://pyup.io/safety/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CycloneDX SBOM Format](https://cyclonedx.org/)
