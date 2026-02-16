# Contributing to the Xoe-NovAi Foundation Stack

First off, thank you for considering contributing to Xoe-NovAi! It's people like you that make Xoe-NovAi such a great foundation for everyone.

## 🚀 How Can I Contribute?

### Reporting Bugs
- Use the GitHub issue tracker to report bugs.
- Describe the bug in detail and provide steps to reproduce it.
- Include information about your hardware (specifically your CPU and GPU/iGPU) and your OS.

### Suggesting Enhancements
- Enhancement suggestions are tracked as GitHub issues.
- Explain why the enhancement would be useful to most Xoe-NovAi users.

### Pull Requests
- Fill in the required template.
- Ensure the code follows the existing style and structure.
- **Critical**: Run `make pr-check` before submitting. Your PR will not be merged if it violates the Sovereign Security Trinity policy or fails the smoke tests.

## 🛡️ Sovereign Standards
All contributions must adhere to our core principles:
1. **Zero Telemetry**: No code should ever send data to an external server without explicit, per-instance user consent.
2. **Local-First**: Features must work offline by default.
3. **Modular**: Aim for plug-n-play modules that can be reused in other projects.

## 🔬 The Great AI-Native Experiment
The Xoe-NovAi Foundation Stack is unique: it was built by a non-programmer using **100% AI-written code** over the course of a year. We are extremely interested in hearing from seasoned programmers about the nature of this codebase:

- **Structural Comparison**: How does this 100% AI-written code compare to traditional human-authored code?
- **Direction Comparison**: How does AI code directed by a non-dev (technical visionary) differ from AI code directed by a seasoned programmer?
- **Emergent Patterns**: Are there implementations or strategies in the underlying architecture of the stack that are unique or unconventional?

We invite you to share your insights, audits, and discoveries in our GitHub Discussions or as EKB contributions.

## ⚖️ Code of Conduct
By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Agent account naming & protocol
- We use a dual-layer naming system: **High-Level Personas** for coordination and **Technical Identifiers** for account-level traceability.
- **Personas**: Cline (Code), Grok (Research), Gemini (Ground Truth), Human Director (User).
- **Technical Format**: `[plugin-name]-[model-name]-[account-delineator]` (examples: `Copilot-Haiku-27`, `Raptor-74`, `Cline-X`).
- Primary technical accounts for this project:
  - `Copilot-Raptor-27` → antipode2727@gmail.com (primary — near free‑tier quota limit).
  - `Copilot-Raptor-74` → antipode7474@gmail.com (secondary; use for Raptor/Haiku workloads when 27 is rate‑limited).
  - `Cline-X` → xoe.nova.ai@gmail.com (admin / repo owner — use for privileged operations and merges).
- Usage guidance:
  - Reference team members by **Persona** in high-level dialogue.
  - Use **Technical Identifiers** in logs, billing, and quota management.
  - Always include `--account <identifier>` where CLIs support multiple identities.
- Onboarding files for each account live under `expert-knowledge/onboarding/` and must be reviewed before assigning production tasks.
