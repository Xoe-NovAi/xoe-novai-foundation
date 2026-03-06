# Research Expert Memory Bank

This specialized memory bank provides guidance, templates, and tracking information for agents executing research jobs from the global queue. When an agent activates this bank it gains access to:

- Standard research request/response templates
- Priority definitions and typical effort estimates
- Progress notes and status markers for each job ID
- Useful snippets such as sample search queries, crawl/analysis patterns
- Links to relevant documentation and handoff packages

Agents may automatically load this memory bank at the start of a research task to bootstrap their reasoning and update the bank with findings.  

**Activation**:
Agents can load by specifying `research_expert` as a memory bank when initializing their context (for example via the `MemoryBankAdapter` during split-test runs or within an autonomous research agent).

**Location**: `memory_bank/multi_expert/research_expert/`