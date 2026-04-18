# AI Code Review Checklist

**Last Updated:** 2026-04-18  
**Owner:** Engineering Team

## Overview

This checklist supplements our standard code review process for Pull Requests that modify LLM prompts, chain logic, or AI model interactions. Use it alongside the main [Code Review Guidelines](https://github.com/bmrtech-oss/ai-development-playbook/blob/main/docs/04-development/conventions/code_review_guidelines.md).

---

## Security & PII

- [ ] **Input logging:** Raw user input is never logged without hashing/SHA-256 truncation
- [ ] **Prompt injection:** System instructions include explicit boundaries and role definitions
- [ ] **PII handling:** User data is not included in prompts unless absolutely necessary for functionality
- [ ] **API keys:** No hardcoded API keys or secrets in prompt templates
- [ ] **Output sanitization:** Generated content is filtered for potential data leaks

---

## Cost & Latency

- [ ] **Token limits:** System prompt length is measured and within model context window (e.g., < 4K tokens for GPT-4)
- [ ] **Timeout logic:** All AI calls include `asyncio.wait_for` or equivalent timeout handling
- [ ] **Retry strategy:** Exponential backoff implemented for transient failures (rate limits, network issues)
- [ ] **Cost estimation:** Large prompt changes include cost impact analysis
- [ ] **Caching:** Expensive operations use appropriate caching (Redis/memcached) with TTL

---

## Resilience

- [ ] **Fallback messages:** Graceful degradation with user-friendly message: `"I'm having trouble processing that right now. Please try again."`
- [ ] **Schema validation:** Output parsing handles JSON schema mismatches and malformed responses
- [ ] **Error boundaries:** AI failures don't crash the entire user flow
- [ ] **Circuit breaker:** Repeated failures trigger circuit breaker pattern
- [ ] **Monitoring:** All AI interactions emit structured metrics for observability

---

## Additional Checks

- [ ] **Testing:** Unit tests cover prompt variations and edge cases
- [ ] **Documentation:** Prompt changes are documented in the PR description
- [ ] **Model compatibility:** Changes work across all supported model versions
- [ ] **Performance:** Benchmark results show no significant latency regression
- [ ] **A/B testing:** Major changes include A/B test plan for gradual rollout