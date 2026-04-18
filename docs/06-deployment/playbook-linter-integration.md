# Playbook Linter Integration

**Last Updated:** 2026-04-18  
**Owner:** Platform Team

## Overview

The Playbook Linter is a reusable GitHub Action that validates your repository's compliance with the AI Development Playbook standards. Use it to ensure your team follows best practices.

## Quick Start

Add this to your `.github/workflows/lint.yml`:

```yaml
name: Lint Playbook Compliance

on: [push, pull_request]

jobs:
  lint:
    uses: bmrtech-oss/ai-development-playbook/.github/workflows/playbook-linter.yml@main
    with:
      strict_mode: true
      report_format: 'markdown'
      fail_on_warning: true
```

## Configuration

Create a `.playbook-linter.yaml` in your repository root:

```yaml
strict_mode: true
report_format: markdown
fail_on_warning: false
```

## What It Checks

- **File Existence:** Required playbook files (model cards, promptfoo configs, etc.)
- **Content Patterns:** Specific practices like feature flags in CI, pgvector queries
- **Structure:** Proper directory organization

## Reports

- **Markdown:** Human-readable summary with ✅/❌ status
- **JSON:** Machine-readable for automation

## Troubleshooting

- Ensure your repository has the expected file structure.
- Check the artifact upload for detailed reports.
- For custom checks, fork and modify the action.