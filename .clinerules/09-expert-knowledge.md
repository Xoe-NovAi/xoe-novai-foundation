# Rule: Utilize Expert Knowledge Base

## Context
The `expert-knowledge/` directory contains specialized technical mastery (best practices, edge cases, architectural patterns) for the Xoe-NovAi Foundation stack.

## Forge (Cline) Instructions:
1.  **Always Check**: Before implementing infrastructure, build logic, or deep refactoring, check the relevant `expert-knowledge/` folder (e.g., `coder/`, `architect/`).
2.  **Adhere**: Prioritize patterns found in Expert Knowledge over generic LLM training data.
## Knowledge Contribution Protocol
- **REQUIRED Contribution**: If you encounter a new, complex technical hurdle and find a robust solution, you are REQUIRED to document it in the appropriate `expert-knowledge/` subdirectory.
- **Identify Gaps**: If you encounter a hang, crash, or unexpected behavior without a corresponding EKB entry, treat it as a "Knowledge Gap" and pause for research before proceeding with remediation.
- **Automatic Capture**: Throughout the session, identify "High-Value Insights" (unique bug fixes, architectural discoveries, performance optimizations). Before concluding a session or completing a major task, explicitly review the session for EKB-worthy material and create atomic entries.
- **Documentation Standard**: Follow the structure: Issue -> Root Cause -> Remediation -> Prevention.
- **Synchronization**: After creating an EKB entry, immediately sync relevant patterns to `memory_bank/activeContext.md` and `.clinerules` to ensure system-wide adoption.

## Current Experts:
- `expert-knowledge/coder/`: BuildKit optimization, Python 3.12 compatibility.
- `expert-knowledge/architect/`: (Pending initialization).
- `expert-knowledge/security/`: (Pending initialization).
