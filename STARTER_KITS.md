# Starter Kits and Playbook Adoption

This guide helps you use the playbook where it delivers the most value based on your team size and priorities.

## Starter kit guidance

The playbook is designed as a reference base, not a finished toolkit. Use these starter paths as launch points and adapt them to your team’s stack and operating model.

- Start with [`docs/04-development/`](docs/04-development/) for architecture, code conventions, and prompt engineering.
- Use `quickstart/slm-eval-template/` for a minimal evaluation setup.
- Add your own stack-specific starter kit for .NET, Java, Node.js, or Azure if your team uses them.
- Extend the playbook with concrete examples, running scripts, and cloud-specific deployment patterns.

## Solo Founder / Indie Hacker

Focus on the essentials and move fast.

- Prioritize `docs/04-development/`, `docs/05-testing/`, and `docs/06-deployment/` for simple CI and quality checks.
- Use managed platforms like Vercel, Render, Azure App Service, or GitHub Actions.
- Keep governance light and document only what you need.
- Start with a minimal agent or retrieval pipeline and evolve the architecture as traction grows.

## Growing Startup (5-20 engineers)

Add reliability and repeatability without slowing the team.

- Use `docs/06-deployment/azure_onprem_guide.md` when you need vendor-neutral cloud or hybrid guidance.
- Add `docs/05-testing/testing_lifecycle_maturity.md` to build a more complete QA strategy.
- Use the playbook to codify handoff points between product, engineering, and SRE.
- Collect starter kit contributions from the team for preferred frontend and backend stacks.

## Enterprise (20+ engineers)

Implement the full practice set for scale and compliance.

- Use the full stack including `docs/08-governance/` and ADRs in `docs/03-design/adr/`.
- Add formal review cycles, governance, and model cards.
- Standardize release management, on-call rotation, and audit-ready observability.
- Treat the playbook as a living operations manual for multiple teams.

## Build your own starter kits

Suggested starter kit categories:

- Cloud-native AI with Azure OpenAI, AKS, and Azure Monitor
- Private inference / on-prem hybrid deployment
- Java/Spring or .NET backend integration
- Vue or mobile-first frontend AI experiences
- Industry-specific agents for retail, healthcare, finance, or legal

If your team adds a new starter kit, link it from `README.md` and `docs/CONTRIBUTING.md`.
