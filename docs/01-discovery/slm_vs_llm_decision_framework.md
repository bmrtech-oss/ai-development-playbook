# SLM vs. LLM Decision Framework

**Last Updated:** 2026-04-18  
**Status:** Active

When should we fine‑tune a Small Language Model (SLM) versus using a third‑party Large Language Model (LLM) API?

## Decision Tree

1. **Latency requirements?**
   - < 500ms → SLM (on‑device or edge)
   - ≥ 500ms → LLM API acceptable

2. **Data sensitivity?**
   - Code never leaves our VPC → SLM
   - Public / low sensitivity → LLM API

3. **Cost profile?**
   - High volume, predictable load → SLM (fixed GPU cost)
   - Low volume, bursty → LLM API (pay‑per‑use)

4. **Task complexity?**
   - Narrow, domain‑specific (e.g., generating docstrings) → SLM
   - Broad reasoning, planning → LLM API

## Example
_**Scenario: Docstring Generation for Python Code**_

1. **Latency?** < 500ms required (user types, sees suggestion within 500ms) → **SLM** ✓
2. **Data sensitive?** Yes (user code, never leaves VS Code extension) → **SLM** ✓
3. **Cost profile?** High volume, running on user's machine → **SLM** ✓ (cost = 0)
4. **Task complexity?** Narrow domain (Python docstrings) → **SLM** ✓

**Decision:** Use a fine-tuned SLM (e.g., Mistral-7B-LoRA trained on high-quality Python docstrings).

---

_**Counter-Example: Architectural Refactoring Recommendation**_

1. **Latency?** 5-10s acceptable (user clicks "Suggest Refactor", waits for reply) → **LLM OK**
2. **Data sensitive?** Medium (code is internal, but complex reasoning needed) → **Could be LLM**
3. **Cost profile?** Low volume (rare feature) → **LLM acceptable**
4. **Task complexity?** Broad reasoning across multiple design patterns → **LLM** ✓

**Decision:** Use OpenAI GPT-4 via API. Cost is ~$0.03/request; only used ~10x/day across user base.
