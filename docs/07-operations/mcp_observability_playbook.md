# MCP Observability Playbook

**Last Updated:** 2026-04-18

Our AI agents use the **Model Context Protocol (MCP)** to call tools (search, file read, etc.). Observability is critical.

---

## Quick Start

**New to MCP?** Start with [MCP Design & Development Guide](../04-development/mcp_design_and_development.md).

---

## What to Monitor
- **Tool call success rate** (errors/timeouts)
- **Latency per tool** (p95, p99)
- **Rate of tool usage** (to detect abuse or cost spikes)

## Implementation
- All MCP servers expose a `/metrics` endpoint (Prometheus format).
- Structured logs include `trace_id`, `tool_name`, `user_id`.

## Debugging a Failed Tool Call
1. Grab `trace_id` from the user-reported error.
2. Query Loki: `{trace_id="xxx"}`
3. Check tool server logs and the agent's decision log.

### Example Query

```logql
{job="mcp-server"} 
| json 
| trace_id="abc123def456" 
| line_format "{{.timestamp}} [{{.level}}] {{.message}}"
```

This returns a timeline of all logs for that tool call, including:
- Tool selection decision
- Input parameters
- Tool execution latency
- Output (or error)
- Agent's interpretation

### Common Issues & Fixes

| Problem | Query to Debug | Fix |
|---------|----------------|-----|
| Tool timeout | `{job="mcp-server"} \| latency_ms > 30000` | Increase timeout in agent config, or optimize tool server |
| Tool crashed | `{job="mcp-server"} \| "error" or "panic"` | Check tool server logs; restart if memory leak |
| Wrong tool selected | `{trace_id="xxx"} \| "selected_tool"` | Review prompt; add more examples to agent |
