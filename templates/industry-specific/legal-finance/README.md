# Legal / Finance AI Recipe

This recipe captures a precision-first approach for legal and finance workflows using deterministic logic, auditability, and fact-checking.

## Core capabilities

- Evidence-backed fact verification using deterministic Datalog-style rules.
- High-precision extraction of contract clauses, regulatory references, and financial assertions.
- Structured output for compliance reporting and risk review.
- Token-economic design that minimizes over-generation and encourages verified reasoning.

## Architecture pattern

1. Normalize source documents and reference datasets into a machine-readable store.
2. Execute deterministic logic or Datalog rules to validate claims and extract facts.
3. Enforce output schema contracts and maintain a traceable audit of all inference decisions.
4. Use semantic caching for repeatable legal lookups while ensuring provenance and versioning.

## Why this matters

Legal and finance automation cannot rely on fuzzy language alone. This recipe is designed to make every conclusion auditable, repeatable, and consistent with enterprise risk policies.
