# ADR 0001: Record Architecture Decisions

## Status
Accepted

## Context
As the Xoe-NovAi project grows in complexity and the number of AI agents increases, the "Why" behind critical architectural choices is becoming harder to track. Decisions made in one turn are often forgotten or regressed in later turns because the rationale was only captured in transient chat history or scratchpads.

## Decision
We will use Architectural Decision Records (ADRs) to capture significant architectural choices.
- **Location**: `docs/03-reference/architecture/ADR/`
- **Naming**: `NNNN-descriptive-name.md`
- **Format**: Based on Michael Nygard's template (Title, Status, Context, Decision, Consequences).
- **Triggers**: Any change that affects performance targets, security boundaries, choice of third-party libraries, or core data flow patterns.

## Consequences
- **Positive**: Improved long-term maintainability, easier onboarding for new agents/developers, and reduced risk of architectural regressions.
- **Negative**: Slight increase in documentation overhead for major changes.
