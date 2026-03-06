# Expert Knowledge System

## Overview
The `expert-knowledge/` directory serves as a high-fidelity, specialized knowledge base for the various AI "Stack Experts" working on the Xoe-NovAi project. Unlike the `memory_bank/`, which tracks the *current project state*, the Expert Knowledge base captures *hard-earned technical mastery*, including best practices, edge cases, and architectural patterns.

## Directory Structure
The system is organized by expert domain:

- **`expert-knowledge/coder/`**: Programming standards, BuildKit optimizations, refactoring patterns.
- **`expert-knowledge/architect/`**: System design, IPC patterns, security hardening.
- **`expert-knowledge/documenter/`**: Diátaxis compliance, tone guides, MkDocs optimizations.
- **`expert-knowledge/security/`**: Zero-trust protocols, rootless Podman hardening.
- **`expert-knowledge/tester/`**: Circuit breaker load testing, benchmarking suites.

## Integration with AI Agents

### 1. Context Loading
Agents are directed to check the relevant `expert-knowledge/` subdirectory at the start of a session (Phase 1 or 2) when working on tasks within that domain.

### 2. Knowledge Capture Directive
All AI team members (Cline, Grok, Gemini CLI, Claude) are mandated to:
1.  **Identify** hard-earned knowledge (e.g., discovering a Podman-specific bug).
2.  **Synthesize** the lesson into a concise Markdown file in the appropriate `expert-knowledge/` folder.
3.  **Link** the new knowledge back to the `memory_bank/` and project documentation.

## Best Practices for Contributing
- **Case-Study Driven**: Focus on real issues encountered in the Xoe-NovAi Foundation stack.
- **Action-Oriented**: Provide clear "BEFORE/AFTER" code blocks or terminal commands.
- **Edge-Case Aware**: Explicitly document what *didn't* work and why.
- **Versioned**: Note the software versions (e.g., Podman 5.x) to ensure relevance.
