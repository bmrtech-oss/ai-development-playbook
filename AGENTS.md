# AI Assistant Context

This file provides essential context for AI coding assistants (Cursor, Copilot, etc.) working within this repository.

## Project Overview
We are building a **AI Platform** — an AI‑powered developer tool that combines static analysis, semantic search, and SLMs to accelerate software development.

## Technology Stack
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, LangChain, tree‑sitter (also extendable to Node.js, Java, .NET, and hybrid API stacks)
- **Frontend:** TypeScript, React 18, Vite, Tailwind, Radix UI / Shadcn (also applicable to Next.js, Vue, mobile, and embedded web experiences)
- **AI/ML:** PyTorch (SLM fine‑tuning), Hugging Face Transformers, pgvector, RDFlib
- **Infra:** GCP (primary), AWS (secondary), Azure, on-prem hybrid patterns, OpenTofu, GitLab CI, Docker

## Code Conventions
- **Python:** Follow `black` formatting, `ruff` linting, type hints required.
- **TypeScript:** Prettier + ESLint (strict mode), prefer functional components.
- **Commit Messages:** Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`).
- **PR Size:** Keep changes under 400 lines; use feature flags for large features.

## Important Directories
- `docs/` – This playbook. All process and architecture decisions live here.
- `.cursor/rules/` – Additional AI‑specific rules (if any).

## Testing Philosophy
- **Unit tests:** `pytest` (backend), `vitest` (frontend).
- **AI evaluation:** `promptfoo` for prompt regression, custom harness for SLM metrics.
- **E2E:** Playwright for critical user journeys.

When generating code, adhere to the guidelines in `docs/04-development/` and always consider the "Signal over Noise" principle: **simplicity and clarity first**.
