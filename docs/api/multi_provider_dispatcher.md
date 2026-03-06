# Multi-Provider Dispatcher (Phase 3B)

The Multi-Provider Dispatcher is the core orchestration engine that routes tasks to the most appropriate AI provider based on context size, task specialization, and quota availability.

## 🚀 Key Features

- **Dynamic Routing**: Automatically selects providers based on real-time scoring.
- **Quota Management**: Tracks usage across multiple accounts to prevent exhaustion.
- **Specialization Alignment**: Routes coding tasks to Sonnet/Raptor and reasoning tasks to Opus Thinking.
- **Automatic Fallback**: Transparently rotates to secondary providers if the primary fails or is rate-limited.
- **Tier 1 Integration**: Deep support for Antigravity's 1M context models.

---

## 🏗️ Architecture

The dispatcher follows a 5-step lifecycle for every task:

1.  **Task Analysis**: Estimates context size and identifies specialization (`CODE`, `REASONING`, `LARGE_DOCUMENT`).
2.  **Provider Scoring**: Ranks available providers based on quota, latency, and specialization fit.
3.  **Provider Selection**: Selects the highest-scoring healthy provider.
4.  **Execution**: Dispatches the task via the provider's CLI or API.
5.  **Audit & Update**: Logs the result and updates quota usage.

---

## 📋 Provider Tiers

| Tier | Providers | Best For |
|------|-----------|----------|
| **Tier 1** | Antigravity (Opus Thinking, Gemini 3 Pro) | Deep reasoning, 1M context tasks |
| **Tier 2** | Copilot CLI (Raptor-mini) | Fast coding, moderate context |
| **Tier 3** | Cline CLI, OpenCode | IDE-integrated tasks, general reasoning |
| **Tier 4** | Local GGUF (llama.cpp) | Offline, air-gap, privacy-critical |

---

## 🛠️ Usage

```python
from app.XNAi_rag_app.core.multi_provider_dispatcher import MultiProviderDispatcher

dispatcher = MultiProviderDispatcher()

result = await dispatcher.dispatch(
    task="Refactor the authentication module",
    context_size=50000,
    specialization="code"
)

if result.success:
    print(f"Task completed via {result.provider}")
```

---

## 🧩 Components

### Antigravity Dispatcher
A specialized dispatcher for the Antigravity CLI, providing access to frontier models with 1M token context windows.

### Thinking Model Router
Intelligently routes complex reasoning tasks to "Thinking" models (like Opus 4.6), managing the thinking budget and output limits.

### Token Validator
Ensures that payloads fit within provider context windows and estimates token usage for quota tracking.

---

**Last Updated**: 2026-02-28
**Owner**: MC-Overseer
