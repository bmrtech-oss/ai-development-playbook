# Frontend & VS Code Extension Guidelines

## Philosophy
Our frontend is the primary interface for developer intelligence. It must be **fast, non-intrusive, and accessible**. We prioritize the "Inner Loop" speed—UI latency should never hinder a developer's flow.

## Tech Stack
- **VS Code Extension:** TypeScript, VS Code API.
- **Desktop App:** Electron, React, Vite.
- **Web Dashboard:** React, Tailwind CSS, Radix UI.
- **State Management:** Zustand (for simplicity) or XState (for complex AI agent flows).

## VS Code Extension Best Practices
1. **Performance First:** Never block the Extension Host. Perform heavy computations (like tree-sitter parsing) in a Worker Thread or the Backend.
2. **Webviews vs. Native UI:** Use native VS Code UI components (QuickPick, TreeView) for standard interactions. Use Webviews only for complex visualizations (e.g., Knowledge Graph exploration).
3. **Graceful Degradation:** The extension should still provide basic syntax highlighting and navigation even if the Backend or SLM is unreachable.

## Frontend Development Standards
- **Component Design:** Use Shadcn/UI primitives. Keep components small and functional.
- **Streaming UI:** AI responses (LLM completions) must be streamed. Use `ReadableStream` to update the UI incrementally to reduce perceived latency.
- **Error Boundaries:** Wrap AI-generated content in Error Boundaries. If a model generates malformed markdown or code, the UI should handle it without crashing.

## Communication (Extension <-> Backend)
- **JSON-RPC / MCP:** Follow the Model Context Protocol for communication where applicable. See [MCP Design & Development Guide](mcp_design_and_development.md) for tool design patterns.
- **Telemetry:** Use the internal telemetry wrapper to log UI interactions (anonymized) to understand feature adoption.

## Performance Budgets
- **LCP (Largest Contentful Paint):** < 1.2s for the Desktop App.
- **Extension Activation Time:** < 500ms.
- **Input Latency (Ghost Text):** < 50ms for local SLM completions.

## Testing
- **Vitest:** For unit and logic tests.
- **Playwright:** For E2E tests of the Electron app and VS Code webview interactions.
- **Manual Smoke Test:** Verify extension performance on a "Large Repository" (e.g., Linux kernel or React) before every release.

See [End-to-End Testing Strategy](../../05-testing/e2e_testing_strategy.md) for detailed test setup and fixtures.

## Dependencies

Keep Node.js and Electron dependencies current. See [Dependency Governance & Management](dependency_governance.md) for update policies and approval workflows.
