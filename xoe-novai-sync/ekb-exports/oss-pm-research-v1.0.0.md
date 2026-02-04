---
version: 1.0.0
tags: [ekb, research, pm, sovereign]
date: 2026-01-29
ma_at_mappings: [7: Truth in synthesis, 18: Balance in structure, 41: Advance through own abilities]
sync_status: initial
---

# OSS Project Management Research (v1.0.0)

## Overview
This report evaluates Open-Source Software (OSS) Project Management (PM) tools for integration into the Xoe-NovAi ecosystem. The primary objective is to identify a sovereign, local-first, zero-cost, and Podman-hostable solution that maintains functional density (boards, tasks, timelines) while ensuring offline reliability.

## Top 5 Ranked Candidates

### 1. Vikunja (Rank: 1 - Best All-Rounder)
- **Sovereignty**: 100% self-hostable; explicitly supports Podman/Docker.
- **Functional Density**: Exceptional. Supports Kanban, Gantt charts, tables, and list views.
- **Local-First/Offline**: Primarily server-based, but 1.0.0 release (Jan 2026) signals high stability and performance on local networks.
- **Ryzen Fit**: Low resource footprint; runs efficiently on Zen 2 iGPU stacks.
- **MCP Potential**: High. Structured API allows for easy MCP server creation to sync tasks with Gemini CLI.

### 2. Focalboard (Rank: 2 - Best Offline Capability)
- **Sovereignty**: Open-source alternative to Notion/Trello.
- **Functional Density**: High. Robust boards, galleries, and calendar views.
- **Local-First/Offline**: **Highest**. Offers a "Personal Desktop" app that works entirely offline with local data storage.
- **Alignment**: Strongest candidate for air-gapped scenarios.

### 3. Taiga (Rank: 3 - Best for Agile/Scrum)
- **Sovereignty**: Well-established OSS; community Podman support.
- **Functional Density**: Extreme. Full Scrum/Kanban, backlogs, and sprint planning.
- **Ryzen Fit**: Heavier resource usage (Django/RabbitMQ/Redis) but manageable on 8-core Ryzen.
- **Gaps**: Complexity in setup compared to Vikunja.

### 4. WeKan (Rank: 4 - Pure Kanban Sovereignty)
- **Sovereignty**: Strong emphasis on self-hosting and data control.
- **Functional Density**: Focused on Kanban; includes Gantt views and security-first features.
- **Ryzen Fit**: Very light (Node.js/MongoDB); excellent for low-RAM environments.
- **Alignment**: Ideal for users who want a "Trello-equivalent" without any bloat.

### 5. HedgeDoc (Rank: 5 - Documentation-Centric PM)
- **Sovereignty**: Collaborative Markdown editor; self-hostable.
- **Functional Density**: Moderate. Best for meeting notes and project documentation rather than task orchestration.
- **Gaps**: Lacks native boards/timelines; requires a database for collaborative features.

## Alignment & Gaps (Ma'at Mapping)

- **Ideal 7 (Truth in Tracking)**: Vikunja and Taiga provide the most accurate project state via robust reporting and auditing.
- **Ideal 18 (Balance in structure)**: WeKan and Focalboard offer the best balance between feature set and simplicity.
- **Ideal 41 (Sovereignty)**: Focalboard's desktop app is the gold standard for independent advancement without cloud dependencies.

## MCP Integration Strategy
The Xoe-NovAi stack will prioritize **Vikunja** for API-driven task sync. An MCP server will be developed to allow Gemini CLI to:
1. `create_task`: Add items from chat logs.
2. `get_board_status`: Report on milestone progress.
3. `sync_milestones`: Align `progress.md` with the PM board.

## Conclusion & Recommendation
**Recommendation**: Deploy **Vikunja** via Podman as the primary team PM tool. 
**Pivots**: For users requiring absolute air-gap/offline desktop flows, recommend **Focalboard Personal Desktop**.

*Research executed by Gemini CLI (v0.1.0-alpha)*