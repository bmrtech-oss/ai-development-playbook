# AI Cost Management (FinOps)

## Overview
AI-powered features carry significant variable costs. To remain sustainable, we must treat token consumption and GPU compute as a managed resource, similar to cloud infrastructure.

## Cost Drivers
1. **Third-Party LLMs (OpenAI, Anthropic):** Charged per 1k tokens.
2. **Internal SLMs:** Charged per GPU-hour on GCP/AWS.
3. **Vector Database:** Storage and IOPS for `pgvector`.
4. **Data Pipeline:** EMR/Dataflow jobs for Knowledge Graph construction.

## Efficiency Strategies
- **Prompt Engineering:** Keep system prompts concise. Every 100 redundant tokens in a system prompt costs thousands of dollars at scale.
- **Caching Layer:** Implement a semantic cache (Redis) for common queries. If a query is >95% similar to a recent one, return the cached result.
- **Tiered Routing:**
    - **Tier 1 (Local):** Small tree-sitter tasks or local SLM. (Cost: $0)
    - **Tier 2 (Internal SLM):** Medium complexity tasks (e.g., unit test generation). (Cost: Low)
    - **Tier 3 (Frontier LLM):** High complexity reasoning (e.g., architectural refactoring). (Cost: High)

## Monitoring & Alerts
- **Budget Alerts:** Automated alerts in GCP/AWS when daily spend exceeds 120% of the moving average.
- **Token Tracking:** Every API request must be logged with `request_tokens`, `completion_tokens`, and `model_id`.
- **Cost per User:** Calculate monthly cost per active user (CPUA) to inform pricing tiers.

## Review Process
- Any feature expected to increase API spend by >$500/mo requires a "Cost Impact" section in its ADR.
- Monthly "FinOps Review" to identify and terminate underused GPU instances or optimize expensive prompts.
