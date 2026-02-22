---
priority: low
context: meta
activation: manual
last_updated: 2026-02-17
version: 1.0
---

# Rule Effectiveness Metrics

## Purpose
Track which rules are actually useful vs. noise. Update after each significant task.

## Metrics Tracking

| Rule File | Uses | Effective | Issues | Notes |
|-----------|------|-----------|--------|-------|
| 00-core-context.md | 0 | - | - | NEW |
| 01-security.md | 0 | - | - | NEW |
| 02-memory-bank.md | 0 | - | - | NEW |
| 03-coding-standards.md | 0 | - | - | NEW |
| 04-documentation.md | 0 | - | - | NEW |
| 05-dependencies.md | 0 | - | - | NEW |
| 06-agents-coordination.md | 0 | - | - | NEW |

## Archived Rules (2026-02-17)
The following 12 files were archived due to low utility or pseudocode bloat:

| File | Lines | Reason |
|------|-------|--------|
| 07-command-chaining.md | 18130 | Verbose, rarely used |
| 07-error-handling.md | 8805 | Duplicate numbering |
| 08-documentation-maintenance.md | 11506 | Consolidated into 04 |
| 09-expert-knowledge.md | 1715 | Vague, low utility |
| 10-spec-listener.md | 1006 | Niche use case |
| 12-research-mastery.md | 8389 | Condensed |
| 13-thought-recording.md | 10374 | Verbose |
| 14-coding-expert-persona.md | 29340 | Persona-heavy, bloated |
| rules/08-workflow-adapters.md | 10742 | Pseudocode |
| rules/09-performance-analytics.md | 12157 | Pseudocode |
| rules/10-rule-evolution.md | 13959 | Pseudocode |
| rules/11-intelligent-orchestrator.md | 16398 | Pseudocode |

**Total archived**: ~122,000 lines of bloat removed

## Update Protocol
After completing tasks, increment:
- **Uses**: How often rule was referenced
- **Effective**: Did rule help? (Y/N/partial)
- **Issues**: Any conflicts or problems

## Review Schedule
- Weekly: Quick scan of usage
- Monthly: Effectiveness assessment
- Quarterly: Archive ineffective rules

## Success Criteria
- Average uses per active rule > 2/week
- Effectiveness rate > 80%
- Total rule lines < 1000

## Total Line Count
**Before**: 5,909 lines (24 files)
**After**: ~800 lines (8 files)
**Reduction**: 86%
