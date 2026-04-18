# Jira ↔ GitHub Workflow

**Last Updated:** 2026-04-18

We use Jira for epic tracking and roadmap visibility; GitHub for all code and day‑to‑day work.

## The Flow

1. **Epic** created in Jira (e.g., "Improve SLM Inference Speed").
2. **Stories/Tasks** are broken down in Jira.
3. For each story:
   - Create a **GitHub Issue** using the `jira-integration` bot.
   - Link the issue to the story (automated via commit message or manual link).
4. Development happens in GitHub:
   - Branch named `feature/ABC-123-short-description`
   - PR references the issue (`Closes #42`)
5. When PR merges, **Jira status moves to "Done"** automatically.

## Noise Reduction
- **Do not** duplicate conversations. Comment on GitHub, not Jira.
- **Do** keep Jira fields (fixVersion, assignee) updated for reporting.
