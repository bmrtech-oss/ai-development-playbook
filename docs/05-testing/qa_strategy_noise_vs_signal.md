# QA Strategy: Signal over Noise

**Last Updated:** 2026-04-18

## Guiding Principle
We test what matters, and we automate the boring stuff.

## Test Pyramid (Adapted for AI)
```
       /\
      /E2E\        Playwright (critical user flows)
     /------\
    /  Int.  \     API + AI eval harness
   /----------\
  /   Unit     \   pytest + vitest (fast feedback)
 /--------------\
```

## AI‑Specific Testing
- **Prompt Regression Tests:** Run `promptfoo` on every PR that touches prompts.
- **SLM Accuracy:** Weekly benchmark run against the `code-eval` dataset.
- **MCP Tools:** Mock server responses to test tool‑calling logic.

## Noise Management
- **Flaky tests are killed immediately.** (Slack alert → fix or delete within 24h)
- **Nightly builds** run the full suite; PRs only run relevant affected tests.
