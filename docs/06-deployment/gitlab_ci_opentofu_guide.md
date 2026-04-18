# GitLab CI + OpenTofu Guide

**Last Updated:** 2026-04-18

## Overview
We use GitLab CI for continuous integration and OpenTofu (IaC) for provisioning cloud resources.

## Pipeline Stages
1. **`test`** – Lint, unit tests, AI evaluation.
2. **`build`** – Docker images, package VS Code extension.
3. **`plan`** – OpenTofu plan (for infrastructure changes).
4. **`apply`** – OpenTofu apply (manual trigger on `main` branch).
5. **`deploy`** – Helm / Cloud Run deployments.

## OpenTofu Workflow
- State stored in GCS bucket `tfstate-prod`.
- Always run `tofu fmt -recursive` before commit.
- Use **workspaces** for `dev`, `staging`, `prod` environments.

## Example MR Pipeline
```yaml
include:
  - local: '/ci/templates/.gitlab-ci.yml'
```

*Full pipeline definition lives in the main application repository.*
