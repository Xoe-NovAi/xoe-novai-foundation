# Xoe-NovAi Foundation Stack

**Build your own AI. Own your data. Evolve your future.** 🔱

> **Production-Tight Local Agentic RAG System**  
> 100% local · Zero telemetry · Ryzen 5700U Optimized · Maat Ethical Overlay

---

## Metropolis Architecture (v3.5) 🏙️

The Omega Stack has evolved into a self-organizing mesh of persistent experts and high-performance retrieval patterns.

### 🧬 Pioneer RAG (Funnel 2.0)
- **Small-to-Big Retrieval**: Links high-speed 128d "Summary Chunks" to 4kb "Reasoning Blocks."
- **Speculative Drafts**: Millisecond-latency responses from 150M models, validated by 8B Authority models in the background.
- **Affinity Metrics**: VictoriaMetrics tracks the best Expert + Model pairings for ultimate efficiency.

### 🏙️ Expert Metropolis (v4.0)
- **8-Domain Expert Network**: Dedicated, persistent domain experts for Architect, API, UI, Voice, Data, Ops, Research, and Test/QA.
- **Isolated State**: Each expert maintains its own `.gemini/history` and settings via `XDG_DATA_HOME` isolation.
- **Quota-Aware Rotation**: Automated account rotation through 8 unique Gemini API keys to bypass free-tier rate limits.
- **ProxyChains Support**: Integrated support for routing key-retrieval and authentication through proxies to bypass regional blocks.

---

## 🛠️ Metropolis Operations (Makefile)

| Command | Description |
|---------|-------------|
| `make metropolis-list` | See all active experts in the mesh |
| `make metropolis-sync` | 🔄 Sync Master settings to all 8 experts |
| `make metropolis-save` | 💾 Checkpoint experts to persistent storage |
| `make metropolis-load` | 🔄 Restore experts from persistent storage |
| `make metropolis-stats` | 📊 Collect token/request metrics for dashboard |
| `make metropolis-summon NAME="Plato"` | Consult an expert directly |
| `make proxy-gemini` | 🌐 Run Gemini CLI through ProxyChains (for regional bypass) |
| `make metropolis-harden` | Definitive fix for Podman permission issues |
| `make metropolis-logs` | Monitor background knowledge mining |
| `make antigravity-login` | 🔑 Start sovereign login (bypasses CLI bugs) |
| `make antigravity-status` | 📊 Check account health and quotas |
| `make scout TASK="..."` | 🤝 Prepare token-optimized context for handoff |
| `make manage-tools` | 🛠️  View and validate all Omega tools |

---

## 🔒 Enterprise Hardening & Best Practices

- **Concurrency**: AnyIO v4.0 structured concurrency with per-level timeouts.
- **Identity**: `userns_mode: keep-id` ensures host/container file system alignment.
- **Reliability**: Non-blocking Redis health monitoring and multi-stage circuit breakers.

---

## 🧪 Validation & Testing
The Metropolis 8-Domain network is rigorously tested for isolation and performance.
*   **Core Suite**: Run `make metropolis-test` to validate instance isolation, configuration sync, and metrics collection.
*   **Live Monitoring**: Run `make dashboard` to verify the real-time telemetry pulse.
*   **Agent Bus**: Broker connectivity is verified via `scripts/metropolis-broker.py` health checks.

---

## Documentation

- **Full Docs**: http://localhost:8008
- **Memory Bank**: `memory_bank/INDEX.md`
- **Knowledge Hub**: `docs/KNOWLEDGE-HUB.md`
- **Stack Services**: `docs/03-reference/current-services.md`

---

## 🛡️ Sovereign Multi-Account Empowerment

The Omega Stack is built to mitigate the power of corporate gatekeeping. We provide pioneer-level infrastructure to bypass artificial rate limits and ensure your sovereign AI workflows are never silenced.

- **Dynamic Rotation**: Seamlessly rotate through 8+ accounts across all major providers (Gemini, SambaNova, SiliconFlow, Groq).
- **Domain Expert Isolation**: Each account maintains its own technical memory (Architect, API, Data, UI), ensuring specialized persistent context.
- **Sovereign Auth Wrappers**: Custom-built, out-of-band injection tools that bypass proprietary CLI bugs and telemetry.
- **100% Portable**: Use `make bootstrap` to deploy your sovereign environment anywhere.

---

## Architecture

```
┌─────────────────────────────────────┐
│         User Interfaces              │
│  Open WebUI │ Chainlit │ BookLore  │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│         Caddy (Reverse Proxy)        │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│         RAG Engine (FastAPI)         │
│    Qwen3-0.6B-Q6_K + Qdrant        │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│      Infrastructure Services          │
│  Redis │ PostgreSQL │ VictoriaMetrics│
└─────────────────────────────────────┘
```

---

## Key Technologies

- **LLM**: Qwen3-0.6B-Q6_K (3GB, local GGUF)
- **Vector DB**: Qdrant v1.13.1
- **Cache**: Redis 7.4.1
- **Async**: AnyIO (not asyncio)
- **Container**: Podman (rootless)
- **Hardware**: AMD Ryzen 7 5700U (Zen 2)

---

## Memory Bank

The Memory Bank is the single source of truth for project status:

| File | Purpose |
|------|---------|
| `memory_bank/INDEX.md` | Navigation |
| `memory_bank/progress.md` | Phase status |
| `memory_bank/activeContext.md` | Current work |
| `memory_bank/systemPatterns.md` | Architecture |

---

## Archive

Historical files and old sessions are archived in:

```
_archive/
└── 2026-03-01-consolidation/
    ├── by_source/
    └── by_date/
```

---

## Sovereign Principles

1. **Zero Telemetry**: No external data transmission
2. **Local-First**: All processing on your hardware
3. **Ethical AI**: Maat guardrails on all agents
4. **Self-Evolution**: Continuous learning from interactions

---

🔱 **Xoe-NovAi** — Private forge for sovereign intelligence.
