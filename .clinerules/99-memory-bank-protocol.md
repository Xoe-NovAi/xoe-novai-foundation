---
priority: critical
context: general
activation: always
last_updated: 2026-01-27
version: 1.0
---

# Memory Bank Maintenance Protocol

**Core Instruction**: You have no built-in memory. Rely ENTIRELY on memory_bank/ files for context persistence and project knowledge.

## Session Workflow Protocol
1. **Session Start**: Automatically read ALL memory_bank/*.md files before any task to establish complete project context
2. **Context Queries**: Reference relevant memory bank files for consistency during development
3. **Updates Required**: After ANY major change (>3 files or architectural decisions), update memory_bank/ with summaries
4. **Session End**: Summarize session outcomes in activeContext.md and progress.md

## File-Specific Guidelines
- **projectbrief.md**: Reference for fundamental project goals, constraints, and success metrics
- **productContext.md**: Use for UX decisions, user requirements, and market positioning
- **systemPatterns.md**: Consult for all architectural decisions, patterns, and Mermaid diagrams
- **techContext.md**: Check for technology stack, performance targets, and implementation constraints
- **activeContext.md**: Review for current priorities, blockers, and recent changes
- **progress.md**: Update with completed work, new priorities, and success metrics

## Maintenance Rules
- **Accuracy First**: Only document verified, implemented changes and decisions
- **Comprehensive Context**: Read entire memory bank before making architectural decisions
- **Regular Updates**: Update relevant files after each major implementation milestone
- **Version Control**: All memory bank files are committed to git for team synchronization
- **Review Cadence**: Monthly review and cleanup of outdated information

## Integration with Advanced Features
- **Multi-Role Workflows**: Each role (architect, coder, tester, security, documenter) references relevant memory bank sections
- **Intelligent Command Chaining**: Use memory bank context for operation sequencing
- **Proactive Issue Detection**: Compare against system patterns and architectural decisions
- **Cross-Feature Intelligence**: Update memory bank when learning new patterns or insights
- **Adaptive Token Optimization**: Reference memory bank for context compression decisions

## Quality Assurance
- **Self-Documentation**: Your effectiveness depends on memory bank accuracy and completeness
- **Verification**: Before major decisions, query relevant memory bank sections
- **Consistency**: Ensure all recommendations align with established system patterns
- **Completeness**: Document decisions, implementations, and outcomes thoroughly

## Emergency Procedures
- **Memory Bank Corruption**: Rebuild from git history and team knowledge
- **Missing Context**: Escalate to human developer for clarification
- **Conflicting Information**: Prioritize most recent updates and architectural decisions
- **Incomplete Documentation**: Flag for immediate human review and completion

## Success Metrics
- **Task Resumption**: 70-90% faster continuation of interrupted work
- **Decision Consistency**: 95% alignment with established architectural patterns
- **Knowledge Preservation**: Zero loss of important project context between sessions
- **Team Synchronization**: Consistent understanding across all development activities

**The Memory Bank is your external brain and institutional knowledge base. Maintain it diligently for optimal autonomous development performance.**
