# API Standards & Versioning

**Last Updated:** 2026-04-18

## Philosophy
Our API serves both our internal VS Code extension and external integrations. It must be **predictable, versioned, and documented**.

## Standards
- **Framework:** FastAPI (Python 3.11+).
- **Serialization:** Pydantic v2 for request/response validation.
- **Communication:** REST for standard CRUD; WebSockets or SSE for streaming AI responses.

## Versioning Strategy
- **URL Versioning:** `/v1/...`, `/v2/...`.
- **Breaking Changes:** A change is breaking if it removes a field, changes a type, or alters the semantic behavior of an endpoint.
- **Sunset Policy:** Old versions are supported for 6 months after a new version is released. Users (and the extension) will receive a `Warning` header in responses for deprecated endpoints.

## Extension Compatibility
The VS Code extension must bundle its "Target API Version." The backend must support the `N-1` version of the extension to ensure that users who haven't updated their VS Code yet still have a working experience.

## Documentation
- **Auto-generated:** Swagger/OpenAPI docs must be available at `/docs` in non-production environments.
- **Examples:** Every endpoint must have a documented example request and response in the Pydantic model `Config`.
- **MCP Servers:** If building MCP tool servers, follow [MCP Design & Development Guide](mcp_design_and_development.md) for JSON-RPC communication patterns.

## Error Handling
Use standard HTTP status codes:
- `400 Bad Request`: Validation errors.
- `401 Unauthorized`: Missing or invalid API key.
- `402 Payment Required`: LLM quota exceeded.
- `429 Too Many Requests`: Rate limiting.
- `500 Internal Server Error`: For unhandled exceptions (aim for zero).

All errors must return a JSON body:
```json
{
  "error": "error_code",
  "message": "Human readable message",
  "details": {}
}
```
