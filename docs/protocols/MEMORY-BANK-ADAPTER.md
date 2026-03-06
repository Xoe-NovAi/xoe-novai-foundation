# Memory Bank Adapter Protocol

**Purpose:**
Define how the split-test framework can evaluate a memory bank as if it were a model, enabling systematic comparison and benchmarking of knowledge bases.

## Overview

A *MemoryBankAdapter* is a subclass of `ModelAdapter` located in `scripts/split_test/__init__.py`. It wraps the memory retrieval API so that the core runner can query a bank with a prompt and receive a text response. This allows the existing metrics, result storage, and evaluation logic to operate unchanged.

Memory banks are simple directory structures containing markdown/text documents. Embeddings are generated and stored in a vector index (Qdrant/FAISS). During evaluation the adapter performs a semantic search against the bank and formats the top results as the "response".

## Usage

```python
from split_test import MemoryBankAdapter, SplitTestRunner, SplitTestConfig

config = SplitTestConfig(id="philosophy-bank", provider="memorybank")
adapter = MemoryBankAdapter(bank_dir="/path/to/memory_bank/multi_expert/philosophy")

runner = SplitTestRunner(configs=[config])
runner.run_prompt("Explain Plato's allegory of the cave.")
```

When running as part of a split test the adapter is selected automatically if a config has `provider: memorybank` or the CLI flag `--memory-bank-dir` is supplied.

## Research Expert Bank

A companion memory bank called `research_expert` provides agents with templates and progress-tracking guidance. Agents can load this bank to bootstrap research jobs or update status as they complete tasks. The adapter handles activation transparently.

## Integration Points

- **KnowledgeClient**: Results from bank evaluations are indexed using `KnowledgeClient` so they can later be queried by other agents.
- **SessionManager**: Stores session metadata for reproducibility of bank tests.
- **MetricsCollector**: Captures specialized metrics such as recall scores and style adherence when comparing banks.
- **CLI**: The `split-test` CLI exposes flags: `--memory-bank-dir` and `--list-banks` for introspection.

## Applying to New Banks

To add a new memory bank:
1. Create a directory under `memory_bank/multi_expert/` with a `README.md` describing its domain.
2. Populate documents and run the ingestion script (`scripts/memory_bank/ingest.py` soon to be added).
3. Add a corresponding `SplitTestConfig` entry or invoke via CLI with `--memory-bank-dir`.

## Future Work

- Automation of bank ingestion from external corpora
- Dashboard visualizations comparing bank responses
- Parallel bank testing and vector cache integration

---

*Last updated February 26, 2026.*