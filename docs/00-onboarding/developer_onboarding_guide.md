# Developer Onboarding Guide

**Last Updated:** 2026-04-18  
**Owner:** Platform Team

## Welcome!

This guide will get you from zero to productive on the AI Platform.

> Note: This playbook is a reference framework, not a finished product. Expect to adapt the guidance to your team’s workflows, compliance controls, and tech stack.

---

## Reading Roadmap (By Day)

### **Day 1: Foundations**
- [ ] Read [README.md](/README.md) — Understand our mission, tech stack, and core tenets.
- [ ] Review [AGENTS.md](/AGENTS.md) — Context for AI assistants (Copilot, Cursor).
- [ ] Skim [Lean Team Design](../team/lean_team_design.md) — How the team operates.
- [ ] Skim [Communication Bandwidth Management](../team/communication_bandwidth_management.md) — How we minimize interrupts.

### **Day 2: Setup & First Run**
- [ ] Follow [Local Environment Setup](../04-development/setup.md) — Get your machine ready.
- [ ] Run `make test-smoke` to verify everything works.
- [ ] Join **#engineering** Slack and introduce yourself.
- [ ] Schedule a pair programming session with your buddy on a small task.

### **Week 1: Deep Dive by Role**

**If you're a Backend Engineer:**
- [ ] Read [Python Development Guidelines](../04-development/python_guidelines.md)
- [ ] Read [API Standards & Versioning](../04-development/api_standards.md)
- [ ] Read [SLM Training Guidelines](../04-development/slm_training_guidelines.md)
- [ ] Complete your first PR (add a unit test or fix a small bug)

**If you're a Frontend Engineer:**
- [ ] Read [Frontend & VS Code Extension Guidelines](../04-development/frontend_vscode_guidelines.md)
- [ ] Read [End-to-End Testing Strategy](../05-testing/e2e_testing_strategy.md)
- [ ] Familiarize yourself with Electron and VS Code Extension APIs
- [ ] Complete your first PR (UI improvement or test)

**If you're an ML/AI Engineer:**
- [ ] Read [SLM vs. LLM Decision Framework](../01-discovery/slm_vs_llm_decision_framework.md)
- [ ] Read [SLM Training Guidelines](../04-development/slm_training_guidelines.md)
- [ ] Read [Model Versioning & Registry](../04-development/model_versioning_registry.md)
- [ ] Review the model evaluation setup

**If you're an SRE/DevOps Engineer:**
- [ ] Read [GitLab CI + OpenTofu Guide](../06-deployment/gitlab_ci_opentofu_guide.md)
- [ ] Read [Security Scanning & Vulnerability Management](../06-deployment/security_scanning.md)
- [ ] Read [Monitoring & Alerting Playbook](../07-operations/monitoring_and_alerting.md)
- [ ] Review on-call rotation and get added to the schedule

### **Week 2-3: Cross-Functional**
- [ ] Attend the weekly engineering all-hands (Friday, 2 PM PST).
- [ ] Read an Architecture Decision Record (ADR) from [03-design/adr/](../03-design/adr/).
- [ ] Join a code review and provide feedback on one PR.
- [ ] Review [QA Strategy: Signal over Noise](../05-testing/qa_strategy_noise_vs_signal.md) — testing philosophy.

### **Month 1: Operations & Culture**
- [ ] Read [Incident Response Runbook](../07-operations/incident_response_runbook.md).
- [ ] Read [Data Privacy & Code Zero Protocol](../07-operations/data_privacy_and_security.md).
- [ ] Read [AI Cost Management (FinOps)](../01-discovery/ai_cost_modeling.md).
- [ ] Attend a tech lead meeting or architecture forum.

---

## Getting Help

- **General questions?** Ask in **#engineering** Slack.
- **Setup issues?** See [Troubleshooting Guide](../04-development/troubleshooting.md).
- **Process questions?** See [CONTRIBUTING.md](../CONTRIBUTING.md).
- **Stuck on a task?** Pair with your buddy or raise in standup.
