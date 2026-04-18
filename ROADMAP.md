# Roadmap & Action Plan

This document tracks concrete initiatives to evolve our engineering practices. It moves from the abstract playbook to **who** is doing **what** and **when**.

## Q2 2026 (Current Quarter)

| Initiative | Owner | Status | Target Date |
|:-----------|:------|:-------|:------------|
| Roll out `promptfoo` evaluation pipeline for all prompts | AI Infra Team | In Progress | 2026-05-15 |
| Migrate remaining Terraform modules to OpenTofu | SRE | Done | 2026-04-01 |
| Establish weekly "Noise Reduction" grooming session | EM | Proposed | 2026-04-30 |
| Define and publish first SLM fine‑tuning baseline | ML Engineer | Not Started | 2026-06-01 |
| Implement VS Code extension automated release via GitLab CI | DX Team | In Progress | 2026-05-20 |

## Q3 2026 (Planned)

- Introduce **Playwright E2E** tests for the VS Code extension.
- Conduct a **Knowledge Graph (RDF)** proof‑of‑concept for code search.
- Formalise the **Release Manager** rotation schedule.
- Automate dependency updates with Renovate.

## Long‑Term Radar (H2 2026)

- Explore **MCP server** integrations for third‑party tools (Jira, Linear).
- Evaluate migrating SLM inference to a dedicated GPU cluster.
- Implement **feature flag** system (Flagsmith / LaunchDarkly) for frontend.

## How We Update This

- **Weekly:** Status check during the Engineering All‑Hands.
- **Monthly:** Review and reprioritise with the Kernel Team.

*This roadmap is a **forecast**, not a promise. It changes as we learn.*
