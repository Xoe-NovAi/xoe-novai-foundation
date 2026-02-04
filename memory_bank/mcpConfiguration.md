# MCP Configuration Matrix: Multi-Environment Tool Integration

**Last Updated**: January 27, 2026
**Purpose**: Comprehensive mapping of Community MCP servers and tools across all environments
**Audience**: All AI team members (Cline, Grok, Gemini CLI, Claude) and system administrators

## Executive Summary

Xoe-NovAi utilizes **Community-Sourced MCP Servers** to extend AI capabilities while ensuring maximum security, reliability, and architectural simplicity. By leveraging hardened, community-vetted servers (e.g., Anthropic, ModelContextProtocol), we avoid the "Confused Deputy" vulnerabilities and maintenance overhead associated with custom-built implementations.

## MCP Architecture Overview

### Core MCP Principles
- **Community-First**: Prioritize official and high-reputation community servers (e.g., Filesystem, Git, Podman).
- **Sovereignty-Aware**: All MCP configurations respect offline/online preferences and run in rootless environments.
- **Environment-Specific**: MCP usage varies by environment (Codium/Cline vs. Gemini CLI).
- **The User/Architect (Human) Control**: Mandatory "Human-in-the-Loop" (HITL) gates for all write/commit/delete operations.

## Current MCP Strategy (Release Hardening Phase)

### 1. Filesystem MCP (Community)
**Source**: `modelcontextprotocol/servers/src/filesystem`
**Purpose**: Secure, local file access for documentation and codebase analysis.
**Xoe-NovAi Tweaks**:
- Bind-mount `/memory_bank` as **Read-Only** by default.
- The User/Architect's approval required for any file modifications via tool calls.
- Chroot isolation to prevent path traversal.

### 2. Git MCP (Community)
**Source**: Anthropic (Official Fork)
**Purpose**: Automated repo management, diffing, and commits.
**Xoe-NovAi Tweaks**:
- Hardened against 2026 prompt-injection vulnerabilities.
- Mandatory The User/Architect approval for all `git commit` and `git push` operations.

### 3. Podman MCP (Community)
**Source**: `yok-tottii-mcp-podman-devcon`
**Purpose**: Infrastructure monitoring and container management.
**Xoe-NovAi Tweaks**:
- Communicates with the rootless Podman socket (`/run/user/1001/podman/podman.sock`).
- Requires `podman system service` to be active.

## Environment-Specific MCP Usage

### Codium + Cline Environment
**Primary Interface**: Codium IDE with Cline Extension (Claude-based).
**Usage**: Real-time coding, refactoring, and local repository management.
**Security**: HITL gates enforced by the Cline extension settings.

### Gemini CLI Environment
**Primary Interface**: Linux Terminal.
**Usage**: System monitoring, health checks, and rapid file-system lookups.
**Security**: Gemini CLI enforces Ma'at-aligned validation before executing tool-suggested commands.

## Security & Sovereignty Guardrails

### 🛡️ The "Confused Deputy" Mitigation
AI agents cannot chain tools to gain unauthorized access. Each tool call is an atomic unit requiring validation against the 42 Laws of Ma'at.

### 🛂 Human-in-the-Loop (HITL)
- **Status**: MANDATORY
- **Application**: Any tool that can modify the state of the system (Write, Delete, Commit, Push, Execute).
- **Gatekeeper**: The User/Architect (Human Director).

## Conclusion

By standardizing on community MCPs, Xoe-NovAi ensures an "Elite" security posture with minimal code bloat. We focus on **configuration and hardening** rather than custom server development.

## 🤖 AI Partnership with Claude (NEW)

**Current Collaboration:**
- **Hybrid Path Research Initiative**: Partnering with Claude to provide comprehensive stack-specific context for advanced refactoring guidance
- **10 Knowledge Gap Research**: Claude is conducting research on critical areas including BuildKit optimization, Security Trinity integration, Performance benchmarking, Memory Bank synchronization, and Ryzen core steering
- **Production-Grade Implementation Manual**: Target delivery of 50-60 page manual with code examples, configuration templates, and validation procedures

**Partnership Benefits:**
- **Stack-Specific Context**: Providing Claude with comprehensive Xoe-NovAi Foundation stack knowledge including Ma'at Guardrails, Sovereign Security Trinity, Memory Bank Protocol, and hardware optimization patterns
- **Enhanced Research Quality**: Ensuring research is 85-90% specific to Xoe-NovAi constraints rather than generic best practices
- **Production-Ready Deliverables**: Focus on immediately actionable guidance with copy-paste code examples and configuration templates

**Research Timeline:**
- **Day 1-3**: Parallel data gathering and research initiation
- **Day 3**: Checkpoint 1 - Data delivery and direction refinement
- **Day 6**: Checkpoint 2 - Mid-research status review
- **Day 9**: Checkpoint 3 - Draft manual review
- **Day 10**: Final delivery of implementation manual

**Integration with Refactoring:**
- Research findings will be integrated with the v0.1.0-alpha modular refactoring plan
- Focus on practical implementation patterns that align with Xoe-NovAi's sovereign, offline-first architecture
- Emphasis on production-grade solutions that maintain the stack's core principles
