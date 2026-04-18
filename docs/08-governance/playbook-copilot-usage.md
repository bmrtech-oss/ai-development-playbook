# Playbook Copilot Usage

**Last Updated:** 2026-04-18  
**Owner:** Platform Team

## Overview

The Playbook Copilot is an AI-powered assistant that answers questions about the AI Development Playbook using Retrieval-Augmented Generation (RAG). It searches the documentation and provides contextual answers with source citations.

## How to Use

1. Open an issue in this repository.
2. In a comment, type `/ask` followed by your question.
3. The Copilot will respond with an answer based on the playbook content.

Example:
```
/ask How do I set up a promptfoo evaluation pipeline?
```

## Features

- **Contextual Answers:** Retrieves relevant sections from the playbook.
- **Source Citations:** Links to the original documentation files.
- **Privacy Considerations:** Questions and answers are public (GitHub issues are public).

## Rate Limits

- Limited to 10 queries per hour per user to manage API costs.
- If rate limited, the action will comment with a retry suggestion.

## Troubleshooting

- Ensure your question is clear and specific.
- If the answer seems incomplete, try rephrasing or ask for more details.
- For complex questions, consider opening a discussion instead.