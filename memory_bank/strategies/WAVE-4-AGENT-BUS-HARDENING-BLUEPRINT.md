# Wave 4 Blueprint: Agent Bus & System Hardening

**Version**: 1.0.0
**Created**: 2026-02-23
**Owner**: Gemini MC

---

## 1. Vision & Mandate

This document outlines the strategic plan for "Wave 4," a comprehensive hardening of the XNAi development and agentic systems. The core mandate, as directed by the user, is to evolve from the current state into a platform with maximum observability, efficiency, and functionality, while holding true to the XNAi sovereignty philosophy.

This wave will address critical infrastructure gaps identified in Wave 2 and 3, particularly those related to external CLI dispatch, and will build the systems necessary for strategic resource management and advanced model utilization.

---

## 2. Strategic Pillars

The Wave 4 initiative is organized around three primary pillars:

### Pillar 1: Observability (The Usage Dashboard)
**Goal:** Achieve a unified, real-time view of resource consumption across all integrated AI services and accounts.

*   **Key Deliverable:** A web-based or terminal-based dashboard.
*   **Features:**
    *   Track message/query counts for all 8 Copilot accounts.
    *   Track token usage (input/output) for Antigravity's free-tier models.
    *   Display usage against monthly/weekly limits.
    *   Show last-used timestamps and suggest the next account for rotation.
    *   Provide estimated cost savings based on free-tier usage.
*   **Data Schema:**
    *   `account_id` (e.g., `xoe.nova.ai@gmail.com`)
    *   `service_provider` (e.g., `GitHub Copilot`, `Antigravity`)
    *   `metric_type` (e.g., `messages`, `tokens_in`, `tokens_out`)
    *   `usage_current` (integer)
    *   `usage_limit` (integer)
    *   `usage_period` (e.g., `monthly`, `weekly`)
    *   `period_reset_date` (ISO 8601)
    *   `last_updated` (ISO 8601)

### Pillar 2: Efficiency (Strategic Resource Management)
**Goal:** Maximize the value derived from limited, high-tier AI model access.

*   **Key Deliverable:** A set of protocols and automated helpers integrated into the dispatch workflow.
*   **Features:**
    *   **Account Rotation Protocol:** A system for automatically selecting the least-used Copilot account for the next dispatch.
    *   **Prompt Optimization Protocol:** A pre-flight check within the Agent Bus to analyze and refine prompts for brevity and clarity, ensuring every message to a limited model "counts."
    *   **Model Tier Routing:** An enhancement to the `model-router.yaml` to include a `cost_tier` (e.g., `free`, `limited_free`, `paid`) to allow agents to intelligently select the most appropriate model for a task's complexity vs. cost.
    *   **Completion Caching:** A simple Redis-based cache to store results for identical prompts sent to paid/limited models, reducing redundant queries.

### Pillar 3: Functionality (Agent Bus Hardening)
**Goal:** Remediate the infrastructure gaps identified during the `cline` dispatch failure and build a robust, scalable, and secure Agent Bus.

*   **Key Deliverable:** A resilient, asynchronous agent dispatch gateway.
*   **Architecture Components:**
    1.  **Credential Management Service:**
        *   **Technology:** Consul KV store.
        *   **Function:** Securely store, retrieve, and rotate API keys and auth tokens for external CLIs (`cline`, `opencode`, etc.).
        *   **Security:** Encrypt all secrets at rest within Consul.
    2.  **Asynchronous Task Gateway:**
        *   **Technology:** Redis Streams (`xnai:agent_bus`) and a dedicated Python service (`agent_gateway.py`).
        *   **Function:** Accept dispatch requests from any agent, queue them, manage the lifecycle of the external process (authentication, execution, monitoring), and publish results back to the Agent Bus. This decouples the calling agent from the external process.
    3.  **Standardized Dispatch Protocol v2:**
        *   An update to `CLI-DISPATCH-PROTOCOLS.md`.
        *   **New Step:** Pre-dispatch authentication check via the Credential Management Service.
        *   **New Field:** All dispatches must include a `timeout` parameter.
        *   **New Behavior:** All external dispatches must go through the Async Task Gateway.

---

## 3. Documentation & Legacy

*   **Origin Story:** A new document, `memory_bank/XNAI-ORIGIN-STORY.md`, will be created to chronicle the project's journey, key decisions, and the philosophy of "sovereign, local-first AI."
*   **Dispatch History:** The `CLI-DISPATCH-HISTORY-*.md` files will be maintained and used as a data source for improving protocols and analyzing agent performance.

---

## 4. Immediate Next Steps (Gemini MC)

1.  **Investigate `gh` CLI:** Research `gh` commands for querying Copilot usage and subscription status.
2.  **Refine Dashboard Schema:** Finalize the data schema for the usage dashboard based on research findings.
3.  **Monitor OpenCode Agents:** Continue monitoring the two background processes and integrate their results upon completion.
4.  **Consolidate Memory Bank:** Begin analysis of `memory_bank` for consolidation and archival, starting with the `activeContext` directory.
