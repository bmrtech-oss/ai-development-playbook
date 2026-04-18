# ADR 0001: Record Architecture Decisions

**Date:** 2026-04-01  
**Status:** Accepted

## Context
We need a lightweight, discoverable way to document significant technical choices.

## Decision
We will use **Architecture Decision Records (ADRs)** as described by Michael Nygard.

- Format: Markdown files in `docs/03-design/adr/`
- Naming: `NNNN-title-with-dashes.md`
- Template: See below.

## Consequences
- ADRs become part of the codebase, reviewed in PRs.
- Historical context is preserved alongside code changes.
- The team is expected to read relevant ADRs before proposing changes.

## Template
```markdown
# ADR NNNN: Short Title

**Date:** YYYY-MM-DD
**Status:** [Proposed | Accepted | Deprecated | Superseded]

## Context
...

## Decision
...

## Consequences
...
```
