# Git Hooks & CI/CD Setup Guide

This guide helps you set up and configure Git hooks, GitHub Actions, and GitLab CI to enforce the branching strategy outlined in [docs/04-development/branching-strategy.md](../docs/04-development/branching-strategy.md).

## Overview

The AI development playbook uses automated enforcement to maintain code quality and consistency:

1. **Pre-commit Hooks** – Local validation before commits
2. **GitHub Actions** – Cloud-based CI/CD and branch protection
3. **GitLab CI** – Additional pipeline for comprehensive testing and deployment
4. **Custom Scripts** – Specialized checks for branch names and feature flags

## Installation & Setup

### 1. Pre-commit Hooks (Local)

Pre-commit hooks run on your machine before you commit code. This catches issues early.

#### Install pre-commit framework

```bash
# macOS / Linux
pip install pre-commit

# Windows (PowerShell)
pip install pre-commit
```

#### Install hooks for this repository

```bash
cd ai-development-playbook
pre-commit install
pre-commit install --hook-type commit-msg
```

This creates hooks in `.git/hooks/` that run automatically before each commit.

#### Run hooks manually (before committing)

```bash
# Check all files
pre-commit run --all-files

# Check specific files
pre-commit run --files src/my_file.py docs/my_doc.md

# Bypass hooks (only when necessary!)
git commit --no-verify
```

#### What hooks check:

- **File formatting**: Remove trailing whitespace, fix EOF
- **Python**: Black formatting, Ruff linting, type hints
- **TypeScript**: ESLint, Prettier
- **Markdown**: Linting for consistency
- **YAML**: Validate syntax and formatting
- **Branch name**: Enforce `feature/*`, `release/*`, `hotfix/*` patterns
- **Commit messages**: Validate conventional format (`feat:`, `fix:`, etc.)
- **Feature flags**: Detect orphaned or undefined flags

### 2. GitHub Actions (Cloud CI/CD)

GitHub Actions runs automated checks when you push code or create pull requests.

#### Configuration Files

- `.github/workflows/branching-strategy-enforcement.yml` – Main enforcement workflow

#### What it validates:

1. **Branch Name** – Checks PR/push branch follows naming conventions
2. **Commit Messages** – Ensures conventional commit format
3. **PR Structure** – Verifies PR has description and checklist
4. **Feature Flags** – Scans for orphaned flags
5. **Tests** – Runs relevant tests based on changed files

#### Enabled for:

- All PRs to `main`, `release/*`, and `develop`
- All pushes to feature, hotfix, and release branches

### 3. GitLab CI (Pipeline)

GitLab CI provides extended testing and deployment capabilities.

#### Configuration File

- `quickstart/gitlab-ci-pipeline.yml` – Complete CI/CD pipeline

#### Stages:

1. **Validate** – Branch names, commit format, feature flags, hotfixes
2. **Test** – Run pytest, linting
3. **Build** – Create artifacts and containers
4. **Deploy Staging** – Test deployment to staging (feature flag gated)
5. **E2E** – End-to-end testing
6. **Deploy Prod** – Production deployment (tag-gated)

#### Key Environment Variables:

- `FEATURE_FLAG_DEPLOY` – Control staging/prod deployments (default: `false`)
- `STAGING_ENV` – Staging environment identifier

#### Usage:

```yaml
# Enable staging deployment
FEATURE_FLAG_DEPLOY=true

# Run production deployment on tag
git tag v1.2.0
git push origin v1.2.0
```

## Validation Scripts

Custom Python scripts perform specialized checks:

### validate_branch_name.py

Ensures branch names follow conventions.

```bash
# Validate current branch
python scripts/validate_branch_name.py

# Allowed patterns:
# ✓ feature/add-auth
# ✓ release/v1.2.0
# ✓ hotfix/fix-bug
# ✗ Feature/add-auth (capitalized)
# ✗ feature_add_auth (underscores)
```

### check_feature_flags.py

Detects orphaned, undefined, or misconfigured feature flags.

```bash
# Check files for flag issues
python scripts/check_feature_flags.py src/api.py src/ui.ts

# Warnings:
# - Flags used but not defined
# - Flags defined but not used
# - Deprecated flag markers
```

## Configuration Examples

### Example 1: Local Development

```bash
# Setup hooks
pre-commit install

# Create feature branch
git checkout -b feature/add-auth

# Make changes with feature flags
# Edit config/featureFlags.ts: FEATURE_NEW_AUTH_ENABLED

# Commit
git add .
git commit -m "feat(auth): add JWT validation"
# ✓ Hooks validate branch, commit message, flags

# Push and create PR
git push -u origin feature/add-auth
# GitHub Actions validates PR
```

### Example 2: Hotfix Workflow

```bash
# Branch from main
git checkout main
git checkout -b hotfix/fix-session-timeout

# Fix the issue
git add .
git commit -m "fix(session): increase timeout threshold"

# Push
git push -u origin hotfix/fix-session-timeout

# GitLab CI flags this as urgent
# GitHub Actions routes to fast review
```

### Example 3: Release Process

```bash
# Create release branch
git checkout -b release/v1.2.0

# Bug fixes and docs only
git commit -m "docs(release): update changelog"
git commit -m "fix(api): patch response parsing"

# Merge back to main
git checkout main
git merge release/v1.2.0
git tag v1.2.0
git push origin main
git push origin v1.2.0

# GitLab CI detects version tag and auto-deploys to production
```

## Troubleshooting

### Hook Installation Failed

```bash
# Ensure pre-commit is installed
pip install --upgrade pre-commit

# Reinstall hooks
pre-commit uninstall
pre-commit install --install-hooks

# Verify installation
ls .git/hooks/ | grep pre-commit
```

### Commit Blocked by Hook

```bash
# See which hook failed
git commit -m "message"
# Output shows failing hook

# Fix the issue (e.g., format Python)
black src/my_file.py
git add src/my_file.py

# Retry commit
git commit -m "message"
```

### Skip Hooks (Use Cautiously!)

```bash
# Skip all hooks
git commit --no-verify -m "message"

# Skip only pre-commit
SKIP=some-hook git commit -m "message"
```

### Feature Flag Warning

```bash
# If hook complains about undefined flags:
1. Check config file for flag definition
2. Ensure flag is in featureFlags.ts / config.py
3. Add flag definition if missing
4. Retry commit
```

### GitHub Actions Fails on Branch Name

```bash
# GitHub Actions rejects branch name
# Example: Branch "feature/my feature" (spaces)

# Fix: Rename branch
git branch -m feature/my-feature
git push origin feature/my-feature

# Or: Create PR from correct branch
```

## Best Practices

1. **Run hooks before pushing** – Catch issues locally, faster feedback
2. **Use meaningful commit messages** – Helps future debugging
3. **Keep feature branches short-lived** – Max 3 days per team policy
4. **Test locally** – Run `pre-commit run --all-files` before force push
5. **Use feature flags for unfinished work** – Merge early with flags disabled
6. **Monitor CI/CD logs** – Understand why deployments succeed/fail

## References

- [Branching Strategy Guide](../docs/04-development/branching-strategy.md)
- [Contributing Guidelines](../docs/CONTRIBUTING.md)
- [Quickstart Examples](./BRANCHING_WORKFLOW_EXAMPLES.md)
- [Pre-commit Documentation](https://pre-commit.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI Documentation](https://docs.gitlab.com/ee/ci/)

## Support

For issues with hooks or CI/CD:

1. Check the troubleshooting section above
2. Review workflow output in GitHub Actions tab
3. Check GitLab CI pipeline logs
4. Refer to [Branching Strategy FAQ](../docs/04-development/branching-strategy.md#rationale)
