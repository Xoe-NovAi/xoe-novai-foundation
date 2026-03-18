# 🐼 OMEGA BROWSER MCP SPECIFICATION (Lightpanda Integration)
**Status**: DRAFT | **Target**: Opus 4.6 Implementation
**Role**: Autonomous Web Research & Interaction

## 1. Overview
The **Browser MCP** allows agents to browse the web safely and efficiently using **Lightpanda** (or a similar headless browser). Unlike simple `curl`, this supports JS rendering, navigation, and interaction, essential for "Deep Research" tasks.

## 2. Architecture
-   **Core Binary**: `lightpanda` (Go-based headless browser) or `playwright`.
-   **Interface**: MCP Tool (`browse_web`, `click_element`, `extract_text`).
-   **Security**: Runs in a sandboxed container (`xnai_browser`).

## 3. Tool Definitions

### `browse(url: str, query: str = None)`
-   **Description**: Navigates to a URL. If `query` is provided, it performs a search on the page or summarizes content relevant to the query.
-   **Output**: Markdown-formatted text of the page content.

### `screenshot(url: str, path: str)`
-   **Description**: Takes a screenshot for visual debugging or Vision model analysis.

## 4. Implementation Steps
1.  **Containerize**: Create `infra/docker/Dockerfile.browser` with Lightpanda/Playwright dependencies.
2.  **MCP Server**: Create `mcp-servers/xnai-browser/server.py`.
3.  **Agent Integration**: Add to `OMEGA_TOOLS.yaml` for Research Agents.
