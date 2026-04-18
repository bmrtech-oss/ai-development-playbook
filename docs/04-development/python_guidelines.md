# Python Development Guidelines

**Last Updated:** 2026-04-18

## Tooling
- **Formatter:** `black --line-length 100`
- **Linter:** `ruff check --select E,F,I,N,UP,B`
- **Type checker:** `mypy --strict`

## Project Structure
```
src/
├── api/          # FastAPI routes, dependencies
├── core/         # Domain models, exceptions
├── ai/           # SLM inference, prompt templates
├── infra/        # Database, external clients
└── utils/        # Pure helpers
```

## AI‑Specific Conventions
- **Prompt templates** are stored as `.jinja2` files, not hardcoded strings.
- **SLM models** must implement a `predict(input: str) -> str` interface.
- **Use Pydantic** for all data validation at system boundaries.

## Testing
- Write **pytest** tests with `pytest-asyncio` for async routes.
- Mock external API calls; test real AI model outputs using golden files.

## Dependency Management

See [Dependency Governance & Management](dependency_governance.md) for policies on adding, updating, and removing dependencies.
