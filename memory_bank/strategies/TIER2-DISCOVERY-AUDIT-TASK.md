# Project P-010 Phase A: Codebase-Wide Security & Quality Audit

## 🤖 Executor
- **Primary**: Gemini 3 Flash (CLI)
- **Role**: Discovery Agent
- **Budget**: 500K tokens max (per turn) / 1M total

## 📋 Objectives
Perform a comprehensive scan of the `app/` and `core/` directories to identify technical debt, security vulnerabilities, and architectural inconsistencies.

## 📂 Scope
1. `app/XNAi_rag_app/core/` (Critical infrastructure)
2. `app/XNAi_rag_app/api/` (Attack surface)
3. `core/` (Standardized modules)
4. `scripts/` (Operational risks)

## 🔍 Specific Audit Points
1. **Concurrency**: Find any usage of `asyncio.gather`, `asyncio.create_task`, or raw `threading`. These must be flagged for conversion to **AnyIO TaskGroups**.
2. **Type Safety**: Identify functions lacking type hints or using `Any` excessively.
3. **Error Handling**: Flag locations using generic `except Exception:` without logging or re-raising. Identify where custom `XNAiException` should be used.
4. **Security**: 
   - Check for hardcoded secrets/tokens.
   - Audit input validation in FastAPI endpoints.
   - Verify non-root container assumptions (file write paths).
5. **Torch-Free Compliance**: Ensure no imports of `torch`, `cuda`, or `triton` exist in the production path.
6. **Agent Bus**: Verify all components are using the unified `xnai:agent_bus` key format.

## 📝 Required Output
Return a structured audit report in `memory_bank/strategies/P-010-AUDIT-FINDINGS.md` using the following format:

### Findings Summary
| Severity | Category | Location | Issue | Fix Recommendation |
|----------|----------|----------|-------|--------------------|
| HIGH     | Async    | file:line| gather used | AnyIO TaskGroup |

### Architectural Inconsistencies
- [bullet points]

### Blockers for Tier 2 Hardening
- [bullet points]

## 🛠️ Execution Command
`gemini -p "$(cat memory_bank/strategies/TIER2-DISCOVERY-AUDIT-TASK.md)"`
