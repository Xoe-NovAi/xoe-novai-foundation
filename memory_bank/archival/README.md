# Archival Memory Tier

**Purpose**: Semantic memory - research, benchmarks, model cards, and reference material.

## Structure

```
archival/
├── research/         # Research findings and deep dives
├── benchmarks/       # Benchmark results and analysis
├── strategies/       # Strategic planning documents (symlink to ../strategies/)
└── model_cards/      # LLM model documentation
```

## Usage

- **Retrieved via semantic search** when needed
- **Max Size**: 200MB total
- **Indexing**: Semantic search enabled

## Content Sources

| Directory | Source | Sync |
|-----------|--------|------|
| research/ | `expert-knowledge/` | Manual |
| benchmarks/ | `benchmarks/` | Auto |
| strategies/ | `memory_bank/strategies/` | Symlink |

## Search

Use semantic search via `localhost:8000/search` or the `search_archival` memory tool.

## Related

- `BLOCKS.yaml` - Configuration
- `recall/` - Session history
- `expert-knowledge/` - Source directory
