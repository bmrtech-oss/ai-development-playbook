# MCP (Model Context Protocol) Design & Development Guide

**Last Updated:** 2026-04-18  
**Owner:** Platform / AI Infrastructure Team

## Overview

The **Model Context Protocol (MCP)** allows AI agents to safely interact with external tools and data sources. We use MCP servers to expose:
- **Tools:** Functions agents can call (e.g., "search code", "read file", "run test")
- **Resources:** Data sources agents can access (e.g., knowledge graphs, documentation)
- **Prompts:** Pre-built prompt templates for common tasks

This guide covers designing, implementing, and deploying MCP servers with focus on **simplicity, safety, and observability**.

---

## Philosophy: Signal Over Noise

MCP follows the same "Signal over Noise" principle as the rest of the platform:

1. **Simple interfaces:** Each tool does one thing well.
2. **Clear contracts:** Inputs/outputs are strictly typed.
3. **Fail gracefully:** Errors propagate cleanly; agents can retry or fallback.
4. **Observe everything:** Every tool call is logged and traced.

---

## Architecture: Types of MCP Servers

### Type 1: Tool Servers (Most Common)

Expose **functions** that agents can call. Examples:
- Search code by query
- Read/write files
- Run tests
- Query databases

**Complexity:** Low  
**Responsibility:** Validate input, execute, return result

```
Agent → MCP Client → Tool Server → External System
         (JSON-RPC)                (Database, Filesystem, etc.)
```

### Type 2: Resource Servers

Provide **read-only data** that agents can fetch. Examples:
- Documentation sections
- Code snippets from knowledge graph
- Architecture decision records (ADRs)
- Dependency graphs

**Complexity:** Low  
**Responsibility:** Expose data, paginate large results

```
Agent → MCP Client → Resource Server → Data Source
         (JSON-RPC)                   (pgvector, RDF store, etc.)
```

### Type 3: Sampling Servers

Provide **streaming data** or **long-running operations**. Examples:
- Live code search results (stream as they arrive)
- Model training progress updates
- Log tails for debugging

**Complexity:** Medium  
**Responsibility:** Stream results, handle client disconnect

```
Agent → MCP Client → Sampling Server → External Stream
         (JSON-RPC)                    (Log file, queue, etc.)
```

---

## Core Concepts

### 1. Tools (Function Calls)

A tool is a function the agent can invoke. Every tool has:
- **Name:** Unique identifier (snake_case, e.g., `search_code`)
- **Description:** What it does (1-2 sentences)
- **Input schema:** Pydantic model defining parameters
- **Output schema:** What the function returns

**Example: Search Code Tool**

```python
from pydantic import BaseModel, Field
from typing import Optional

class SearchCodeInput(BaseModel):
    query: str = Field(..., description="Code search query (regex or natural language)")
    limit: int = Field(default=10, description="Max results to return")
    language: Optional[str] = Field(None, description="Filter by language (py, ts, rs, etc.)")

class SearchCodeOutput(BaseModel):
    results: list[dict] = Field(..., description="Array of matches")
    total: int = Field(..., description="Total matches found")
    truncated: bool = Field(..., description="True if results were truncated")

def search_code(input: SearchCodeInput) -> SearchCodeOutput:
    """Search the codebase by query."""
    results = vector_db.search(
        query=input.query,
        top_k=input.limit,
        language_filter=input.language
    )
    return SearchCodeOutput(
        results=results,
        total=len(results),
        truncated=len(results) >= input.limit
    )
```

### 2. Resources

A resource is read-only data the agent can access. Every resource has:
- **URI:** Unique identifier (e.g., `file:///repo/main.py`)
- **Type:** MIME type (e.g., `text/markdown`, `application/json`)
- **Description:** What it contains
- **Metadata:** Creation date, size, language (for code)

**Example: ADR Resource**

```python
class ADRResource:
    uri: str = "adr://0001-trunk-based-deployment"
    name: str = "ADR 0001: Trunk-Based Deployment"
    mime_type: str = "text/markdown"
    description: str = "Architecture decision on deployment strategy"
    
    def get_contents(self) -> str:
        """Return full ADR text."""
        return open("docs/03-design/adr/0001-trunk-based.md").read()
```

### 3. Sampling (Streaming)

Some operations need to stream results (e.g., search results as they arrive, logs in real-time). Sampling lets the agent fetch data incrementally.

```python
class LogTailInput(BaseModel):
    service: str = Field(..., description="Service name (api, inference, etc.)")
    lines: int = Field(default=50, description="Number of lines to stream")

def log_tail_sampling(input: LogTailInput, callback):
    """Stream recent logs."""
    logs = fetch_logs(service=input.service)
    for line in logs[-input.lines:]:
        callback(line)  # Stream each line to agent
```

---

## Building an MCP Server: Step-by-Step

### Step 1: Define the Tool Interface

Start with Pydantic models for input/output:

```python
# tools/search.py
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(..., description="Search terms")
    limit: int = Field(default=10, ge=1, le=100)

class SearchOutput(BaseModel):
    results: list[str]
    total: int
```

### Step 2: Implement the Tool Logic

```python
# tools/search.py (continued)
from typing import Optional

async def search(input: SearchInput) -> SearchOutput:
    """Search repositories by query."""
    try:
        # Query vector DB
        results = await vector_db.search(
            query=input.query,
            top_k=input.limit
        )
        return SearchOutput(
            results=[r.text for r in results],
            total=len(results)
        )
    except Exception as e:
        logger.error("search_failed", query=input.query, error=str(e))
        # Return empty results, not an error
        # Let agent handle gracefully
        return SearchOutput(results=[], total=0)
```

### Step 3: Wrap in MCP Server

Use the `mcp` library to expose tools:

```python
# server.py
from mcp import Server
from mcp.types import TextContent
from tools.search import search, SearchInput, SearchOutput

server = Server("code-search")

@server.tool()
async def search_code(query: str, limit: int = 10) -> str:
    """Search the codebase.
    
    Args:
        query: Search terms (can be regex or natural language)
        limit: Max results (1-100)
    """
    input = SearchInput(query=query, limit=limit)
    output = await search(input)
    
    # Format for agent readability
    if not output.results:
        return f"No results found for '{query}'"
    
    formatted = "\n".join([f"- {r}" for r in output.results])
    return f"Found {output.total} matches:\n{formatted}"

if __name__ == "__main__":
    server.run()
```

### Step 4: Configure in Agent

The agent discovers and uses MCP servers via configuration:

```yaml
# agent.config.yaml
mcp_servers:
  - name: code-search
    type: tool
    url: http://localhost:3001
    tools:
      - search_code
  
  - name: knowledge-graph
    type: resource
    url: http://localhost:3002
    resources:
      - uri: adr://.*
      - uri: doc://.*
```

---

## Design Patterns

### Pattern 1: Stateless Tools (Preferred)

Each tool invocation is independent. No state between calls.

```python
@server.tool()
async def read_file(path: str) -> str:
    """Read a file's contents."""
    return open(path).read()  # Always reads current version
```

**Pros:** Simple, testable, cache-friendly  
**Cons:** Can't maintain history or sessions

### Pattern 2: Tool Chains (Implicit)

Agent calls multiple tools to accomplish a goal. MCP server doesn't know about the chain.

```
Agent logic:
1. search_code("auth handler")
2. read_file("src/auth.py")
3. run_tests("auth")
→ Generate suggestion
```

**Pros:** Flexible, agent-driven  
**Cons:** Can be slow (multiple round-trips)

### Pattern 3: Batching (Optimization)

For high-volume operations, support batch input.

```python
class RunTestsInput(BaseModel):
    test_files: list[str] = Field(..., description="Paths to test files")

@server.tool()
async def run_tests_batch(input: RunTestsInput) -> str:
    """Run multiple test files in parallel."""
    results = await asyncio.gather(*[
        run_test_async(path) for path in input.test_files
    ])
    return format_results(results)
```

**Pros:** Faster, fewer round-trips  
**Cons:** More complex input validation

### Pattern 4: Progressive Refinement

Tool allows agent to refine results incrementally.

```python
class SearchCodeInput(BaseModel):
    query: str
    language: Optional[str] = None  # Refine by language
    author: Optional[str] = None    # Refine by author
    before_date: Optional[str] = None  # Refine by recency

@server.tool()
async def search_code(input: SearchCodeInput) -> str:
    """Search with optional refinements."""
    # Agent can start broad, then call again with filters
```

**Pros:** Helps agent explore incrementally  
**Cons:** More API calls

---

## Error Handling

### Rule 1: Fail Gracefully

Tools should **not** raise exceptions. Return structured errors.

```python
# ❌ Bad: Raises exception
async def read_file(path: str) -> str:
    return open(path).read()  # Raises FileNotFoundError

# ✅ Good: Returns graceful error
class FileReadOutput(BaseModel):
    success: bool
    content: Optional[str]
    error: Optional[str]

async def read_file(path: str) -> str:
    try:
        return open(path).read()
    except FileNotFoundError:
        return f"File not found: {path}"
    except PermissionError:
        return f"Permission denied: {path}"
```

### Rule 2: Log for Observability

Every tool call should be logged with trace ID.

```python
import structlog

logger = structlog.get_logger()

@server.tool()
async def search_code(query: str) -> str:
    trace_id = request.headers.get("X-Trace-ID")
    
    logger.info(
        "tool_call_start",
        tool="search_code",
        trace_id=trace_id,
        query=query,
    )
    
    try:
        results = await vector_db.search(query)
        logger.info(
            "tool_call_success",
            trace_id=trace_id,
            result_count=len(results),
        )
        return format_results(results)
    except Exception as e:
        logger.error(
            "tool_call_failed",
            trace_id=trace_id,
            error=str(e),
        )
        return f"Error: {str(e)}"
```

### Rule 3: Timeouts

All external calls should have timeouts to prevent hanging.

```python
import asyncio

async def search_code(query: str) -> str:
    try:
        results = await asyncio.wait_for(
            vector_db.search(query),
            timeout=5.0  # 5 seconds
        )
        return format_results(results)
    except asyncio.TimeoutError:
        return f"Search timed out (>{5}s). Try a simpler query."
```

---

## Security & Isolation

### Rule 1: Validate All Inputs

Use Pydantic strictly typed inputs.

```python
from pydantic import Field

class DeleteFileInput(BaseModel):
    path: str = Field(..., description="File to delete")
    
    @validator("path")
    def validate_path(cls, v):
        # Prevent path traversal attacks
        if ".." in v or v.startswith("/"):
            raise ValueError("Relative paths only")
        return v
```

### Rule 2: Principle of Least Privilege

Tool should only access what it needs.

```python
# ❌ Bad: Tool can delete any file
def delete_file(path: str):
    os.remove(path)

# ✅ Good: Tool can only delete temp files
def delete_temp_file(filename: str):
    if not filename.startswith("tmp_"):
        raise ValueError("Can only delete temp files")
    os.remove(f"/tmp/{filename}")
```

### Rule 3: Rate Limiting

Prevent abuse by rate-limiting tool calls.

```python
from slowapi import Limiter

limiter = Limiter(key_func=lambda: request.remote_addr)

@server.tool()
@limiter.limit("10/minute")
async def search_code(query: str) -> str:
    """Rate limited to 10 calls/minute per IP."""
    return await search(query)
```

---

## Testing MCP Tools

### Unit Tests

Test each tool in isolation.

```python
import pytest

@pytest.mark.asyncio
async def test_search_code_returns_results():
    input = SearchInput(query="auth", limit=10)
    output = await search(input)
    assert output.total > 0
    assert len(output.results) <= 10

@pytest.mark.asyncio
async def test_search_code_handles_empty_query():
    input = SearchInput(query="", limit=10)
    output = await search(input)
    # Should handle gracefully, not crash
    assert isinstance(output, SearchOutput)

@pytest.mark.asyncio
async def test_search_code_respects_limit():
    input = SearchInput(query="def ", limit=5)
    output = await search(input)
    assert len(output.results) <= 5
```

### Integration Tests

Test tool in context of MCP server.

```python
import httpx

async def test_mcp_tool_via_http():
    client = httpx.AsyncClient(base_url="http://localhost:3001")
    
    response = await client.post("/tool/search_code", json={
        "query": "auth",
        "limit": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
```

### Mock Testing

Test agent behavior with mocked tools.

```python
from unittest.mock import AsyncMock

async def test_agent_uses_search_when_confused():
    # Mock the search tool to return results
    mock_search = AsyncMock(return_value=[
        "Found function in src/auth.py"
    ])
    
    # Run agent with mocked tool
    response = await agent.run_with_tools(
        prompt="How do I authenticate?",
        tools={"search_code": mock_search}
    )
    
    # Verify agent called search
    mock_search.assert_called_once()
    assert "auth" in response.lower()
```

---

## Deployment & Operations

### 1. Containerization

Each MCP server runs in a dedicated container.

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3001
CMD ["python", "-m", "mcp.server"]
```

### 2. Health Checks

Every MCP server must expose a health endpoint.

```python
@server.get("/health")
async def health_check():
    """Liveness probe for Kubernetes."""
    return {
        "status": "ok",
        "uptime_seconds": time.time() - start_time,
    }
```

### 3. Observability

See [MCP Observability Playbook](mcp_observability_playbook.md) for:
- Metrics exposure (`/metrics` endpoint)
- Structured logging with trace IDs
- Debugging failed tool calls

### 4. Scaling

MCP servers should be stateless to allow horizontal scaling.

```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-search-server
spec:
  replicas: 3  # Horizontal scaling
  template:
    spec:
      containers:
      - name: mcp-search
        image: registry.example.com/mcp-search:v1.0.0
        ports:
        - containerPort: 3001
        livenessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 5
          periodSeconds: 10
```

---

## Common MCP Server Patterns for Your Platform

### 1. Code Search Server

```
Tools:
- search_code(query, language, limit)
- search_symbols(name, type)
- search_references(symbol, file)

Resources:
- file:// → Code files in repository
- symbol:// → Function/class definitions
```

### 2. Knowledge Graph Server

```
Tools:
- query_graph(sparql_query)
- find_related_code(entity)
- trace_dependency(lib_name)

Resources:
- kg:// → RDF triples
- ontology:// → Schema definitions
```

### 3. Test & Validation Server

```
Tools:
- run_tests(test_files, language)
- check_types(files)
- lint_code(files, linter)

Resources:
- test:// → Test results
- coverage:// → Coverage reports
```

### 4. LLM Cache Server

```
Tools:
- cache_prompt_result(prompt_hash, result)
- get_cached_result(prompt_hash)
- invalidate_cache(pattern)

Resources:
- cache:// → Cache metadata
```

---

## Debugging MCP Issues

### Issue: Tool Not Found

**Symptom:** Agent says "tool_name is not registered"

**Debug:**
```bash
# Check server is running
curl http://localhost:3001/health

# List available tools
curl http://localhost:3001/tools

# Check agent config points to right URL
grep "mcp_servers" agent.config.yaml
```

### Issue: Tool Times Out

**Symptom:** Agent waits 30s then fails with timeout

**Debug:**
```bash
# Check server logs
kubectl logs mcp-search-server-xyz

# Check latency histogram
curl http://localhost:3001/metrics | grep tool_latency_seconds

# Increase timeout in agent config
mcp_servers:
  - name: code-search
    timeout_seconds: 60  # Increase from default 30
```

### Issue: Wrong Results

**Symptom:** Tool returns unexpected data

**Debug:**
```python
# Add logging to trace execution
import structlog
logger = structlog.get_logger()

logger.info("tool_input", query=query, limit=limit)
results = await search(query)
logger.info("tool_output", count=len(results), results=results[:2])
```

Then check logs:
```bash
kubectl logs mcp-search-server-xyz | jq 'select(.event == "tool_output")'
```

---

## Best Practices Summary

✅ **DO:**
- Keep tools focused and single-purpose
- Use strictly typed input/output schemas
- Log every tool call with trace ID
- Set timeouts on external calls
- Handle errors gracefully (return message, not exception)
- Test tools in isolation and integration
- Expose `/health` endpoint
- Run stateless servers (enables scaling)
- Document expected latency per tool

❌ **DON'T:**
- Create tools that are too large (agent confusion)
- Return raw exceptions to agents
- Make synchronous calls (use async/await)
- Hardcode credentials (use environment variables)
- Skip input validation
- Forget rate limiting (prevent abuse)
- Log PII or secrets
- Rely on tool execution order (agent may retry)

---

## Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Observability Playbook](mcp_observability_playbook.md)
- [API Standards & Versioning](../04-development/api_standards.md)
- [Security Scanning & Vulnerability Management](../06-deployment/security_scanning.md)
- [Monitoring & Alerting Playbook](monitoring_and_alerting.md)
