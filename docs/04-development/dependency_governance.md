# Dependency Governance & Management

**Last Updated:** 2026-04-18  
**Owner:** Platform / Kernel Team

## Overview

Dependencies are managed by language. We have clear policies for upgrades, security patches, and deprecation cycles.

---

## Python Dependency Policy

### Tools

- **Package manager:** Poetry (manages `poetry.lock` for reproducible builds)
- **Vulnerability scanning:** `safety` (runs in CI)
- **Dependency updates:** Renovate bot (automated PRs)

### Approval Workflow

| Type | Policy | Example |
|------|--------|---------|
| **Patch** (1.2.3 → 1.2.4) | Auto-merge if CI passes | `pydantic==2.0.1` |
| **Minor** (1.2.0 → 1.3.0) | Review required; full test suite | `fastapi==0.108.0` → `0.109.0` |
| **Major** (1.0.0 → 2.0.0) | Feature branch; manual testing | `langchain==0.1.0` → `0.2.0` (breaking) |

### Adding a New Dependency

1. **Evaluate:** Is this library well-maintained? Does it have heavy dependencies?
2. **Add to `pyproject.toml`:**
   ```toml
   [tool.poetry.dependencies]
   requests = "^2.31.0"  # Caret: minor/patch updates allowed
   ```
3. **Lock:** `poetry lock --no-update`
4. **Test:** `pytest` runs with new dependency.
5. **Review:** Kernel Team reviews for unnecessary bloat.

### Python Version Support

- **Minimum:** Python 3.11 (current LTS at project start)
- **Tested:** Python 3.11, 3.12
- **CI matrix:** Tests run on all supported versions

### High-Risk Dependencies (Watch These)

| Package | Reason | Policy |
|---------|--------|--------|
| `langchain` | Large transitive deps, frequent breaking changes | Pin to minor version; review major updates |
| `torch` | Large size, GPU-specific; hard to downgrade | Dedicated review; notify ops team |
| `tree-sitter` | Native bindings; may require rebuild | Test on all platforms |

---

## Node.js / TypeScript Dependency Policy

### Tools

- **Package manager:** npm 10+ (lockfile: `package-lock.json`)
- **Node version:** 18 LTS minimum (managed via `.nvmrc`)
- **Vulnerability scanning:** `npm audit` (runs in CI)
- **Linting:** Renovate (auto-PRs for patches)

### LTS Policy

| Node Version | Support Window | Max Patch |
|--------------|----------------|-----------|
| 18 LTS | Until 2025-04 | 18.x |
| 20 LTS | Until 2026-04 | 20.x |
| 22 LTS | Until 2027-10 | 22.x |

**Update rule:** Keep on active LTS. Upgrade 1 minor version per quarter.

### Approval Workflow

Same as Python:
- **Patch:** Auto-merge
- **Minor:** Review + test
- **Major:** Feature branch + manual testing

### High-Risk Dependencies (Node.js)

| Package | Risk | Policy |
|---------|------|--------|
| `@vscode/vsce` | Extension publishing; affects release pipeline | Dedicated review |
| `electron` | Desktop app; OS compatibility issues | Test on Mac, Windows, Linux |
| `react` | Major version = rewrite; breaking JSX changes | 2-week feature branch before merge |
| `@playwright/test` | Test framework; CI-critical | Patch auto-merge; minor/major reviewed |

---

## Docker Base Image Policy

### Image Selection

- **Python backend:** `python:3.11-slim` (official, regularly patched)
- **Node.js services:** `node:20-alpine` (minimal size, security-focused)
- **Avoid:** `latest` tags. Always pin to specific version.

### Update Cycle

- **Monthly:** Check for new patch versions of base images.
- **Renovate:** Auto-creates PRs for patch updates.
- **Process:**
  ```bash
  docker pull python:3.11-slim  # Get latest 3.11 patch
  docker scan python:3.11-slim  # Check vulnerabilities
  # If clean, merge the Renovate PR
  ```

---

## Renovate Configuration

`.renovaterc.json`:

```json
{
  "extends": ["config:base"],
  "schedule": ["before 3am on Monday"],
  "python": {
    "supportPolicy": ["lts-active"],
    "rangeStrategy": "auto"
  },
  "npm": {
    "rangeStrategy": "auto"
  },
  "vulnerabilityAlerts": {
    "enabled": true,
    "automerge": true
  },
  "major": {
    "enabled": false  # Require manual review for major updates
  },
  "patch": {
    "enabled": true,
    "automerge": true
  },
  "minor": {
    "enabled": true,
    "automerge": false  # Require review
  },
  "packageRules": [
    {
      "packageNames": ["langchain"],
      "extends": ["schedule:weekly"]  # Less frequent
    },
    {
      "packageNames": ["pytest"],
      "automerge": true
    }
  ]
}
```

---

## Dependency Conflict Resolution

If two dependencies require incompatible versions of a shared transitive dependency:

### Decision Tree

1. **Can you upgrade the lower requirement?**
   - E.g., if `lib-a` requires `shared-lib>=2.0` and `lib-b` requires `shared-lib>=1.0`, upgrade `lib-b`.
   - Try: `pip install lib-b --upgrade` or check for a newer version.

2. **Can you use an intermediate version?**
   - E.g., pin `shared-lib==2.1` if both `lib-a` (needs ≥2.0) and `lib-b` (needs <3.0) accept it.

3. **Must you vendor or fork?**
   - Copy the dependency into your repo under `vendor/` (rare).
   - Or, contribute a fix upstream and wait for release.

4. **Can you replace one dependency?**
   - E.g., switch from `lib-b` to an alternative that's compatible.

### Example: Python

```bash
# Poetry's resolution algorithm is quite good.
poetry update --dry-run  # See what versions Poetry would install
poetry add lib-a@latest  # Add the new lib
poetry lock  # Resolve conflicts
```

If Poetry can't resolve: Check `poetry.lock` for comments on why; open an issue.

---

## Deprecation Cycle

When deprecating a library or feature:

1. **Announce (1 sprint):** Add deprecation warning.
   ```python
   import warnings
   warnings.warn("lib-x is deprecated, use lib-y instead", DeprecationWarning)
   ```

2. **Support (1 quarter):** Accept both old and new; log warnings.

3. **Remove (next major):** Delete old code in a major version bump.

### Example Timeline

| Sprint | Action |
|--------|--------|
| S1 | Decide to replace Jinja2 with Mako |
| S2 | Add `DeprecationWarning` when Jinja2 templates are used |
| S3-S5 | Support both; document migration path |
| S6 | Remove Jinja2 from `pyproject.toml`; bump major version |

---

## Security Patch Process

### If a CVE Affects Your Dependencies

1. **Immediately:** `safety check` or `npm audit` reports it.
2. **Triage:** Is it in your runtime code or dev-only? (Dev deps are lower risk.)
3. **Patch:** Update to fixed version; test.
4. **Deploy:** Expedite to production same day (if possible).

### Example

```bash
# Safety reports: Jinja2 < 3.1.2 has RCE vulnerability
# 1. Update
poetry add jinja2@^3.1.2
poetry lock

# 2. Test
pytest

# 3. Deploy
# Create urgent PR, merge to main, deploy to prod
```

---

## Lock File Strategy

- **Always commit `poetry.lock` and `package-lock.json`** to version control.
- Never run `pip install -r requirements.txt` without pinning versions.
- Reproducible builds require locked dependencies.

### When to Update Lock Files

- Weekly: `poetry update` (let Renovate handle it via automated PRs)
- Before release: Ensure no conflicts, all tests pass
- After security advisory: Immediate patch

---

## Testing Dependency Changes

When Renovate opens a PR for a dependency update:

1. **CI runs automatically:** Linters, unit tests, security scans.
2. **If CI passes:** Minor/patch updates auto-merge; major updates wait for review.
3. **If CI fails:** Investigate. Dependency may have breaking change.
4. **Manual testing (for major updates):** Smoke test in staging.

---

## Monitoring & Reporting

### Monthly Dependency Audit

First Tuesday of month:

```bash
# Python
poetry show --outdated
safety check

# Node.js
npm outdated
npm audit

# Docker
trivy image $CI_REGISTRY_IMAGE:latest
```

**Report findings:** Create issues for outdated libraries, security updates.

### Metrics to Track

- Number of outdated packages
- Days since last update (per package)
- Security vulnerabilities (by severity)
- Dependency tree depth (too deep = fragile)

---

## Resources

- [Semantic Versioning](https://semver.org/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [npm Audit](https://docs.npmjs.com/cli/v10/commands/npm-audit)
- [Renovate Bot](https://www.whitesourcesoftware.com/free-developer-tools/renovate/)
- [Trivy Container Scanning](https://aquasecurity.github.io/trivy/)
