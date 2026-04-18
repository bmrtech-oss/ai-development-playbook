# Choose Your Path: How to Use This Playbook Based on Your Team Size

This guide helps you use the playbook where it delivers the most value based on your team size and priorities.

## Solo Founder / Indie Hacker

Focus on the essentials and move fast.

- Start with [`docs/04-development/`](docs/04-development/)
- Use the quickstart in `quickstart/slm-eval-template/`
- Skip complex infra and use managed platforms like Vercel or Render
- Keep governance light and document only what you need

## Growing Startup (5-20 engineers)

Add reliability and repeatability without slowing the team.

- Include [`docs/06-deployment/`](docs/06-deployment/) for CI/CD and infrastructure standards
- Add [`docs/07-operations/`](docs/07-operations/) for monitoring, alerting, and incident response
- Use the playbook to codify handoff points between product, engineering, and SRE

## Enterprise (20+ engineers)

Implement the full practice set for scale and compliance.

- Use the full stack including [`docs/08-governance/`](docs/08-governance/) and ADRs in [`docs/03-design/adr/`](docs/03-design/adr/)
- Add formal review cycles, governance, and model cards
- Standardize release management, on-call rotation, and audit-ready observability
- Treat the playbook as a living operations manual for multiple teams
