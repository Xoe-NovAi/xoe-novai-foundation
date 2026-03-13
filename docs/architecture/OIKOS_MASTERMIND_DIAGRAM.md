# 🔱 Omega Stack: Oikos Mastermind Architecture
**Date**: March 11, 2026 | **Status**: ACTIVE PROTOCOL

## 🌐 Cognitive Flow Diagram

```mermaid
graph TD
    User((User)) -->|Request| Iris[🌈 Iris Messenger]
    
    subgraph "Level 1: Swift Response"
        Iris -->|Complexity < 5| Hearth[🔥 Brigid: Hearth Check]
        Hearth -->|Status| Iris
    end
    
    subgraph "Level 2: Archive Guardian"
        Iris -->|Complexity 5-20| Guardian[🔱 Archive Guardian]
        Guardian -->|Iterative Refinement| RefinedPrompt[Refined Prompt]
        RefinedPrompt -->|Decision| Guardian
    end
    
    subgraph "Level 3: Oikos Council"
        Guardian -->|Complexity > 20| Mastermind[🔱 Mastermind Orchestrator]
        Mastermind --> Council{Oikos Council}
        Council -->|Insight| B[🔥 Brigid]
        Council -->|Insight| H[🕯️ Hestia]
        Council -->|Insight| D[🌾 Demeter]
        Council -->|Insight| A[🦉 Athena]
        Council -->|Insight| I[🌈 Iris Bridge]
    end
    
    subgraph "The Final Ascent"
        Council -->|Synthesis| MaLi[🔱 MaLi Monad Gate]
        MaLi -->|Judgment| Decree[📜 Mastermind Decree]
        Decree -->|Distill| Soul[🔱 Soul Path]
    end
    
    Decree -->|Response| Iris
    Iris -->|Delivery| User
```

## 🏛️ Process Hooks & Functions

| Function | Archetype | Component | Logic |
|:---|:---|:---|:---|
| `route_request` | Iris | `oikos_service.py` | Determines escalation level based on complexity. |
| `call_level_2` | Archive Guardian | `oikos_mastermind.py` | Performs iterative prompt refinement. |
| `orchestrate_oikos` | Sentinel | `oikos_service.py` | Manages sequential Council speaking turns. |
| `judge_decree` | MaLi | `mali_gate.py` | Balances Maat/Lilith for final approval. |
| `distill_cycle` | Sentinel | `soul_distiller.py` | Records evolution in `SOUL_PATHS.yaml`. |

---

## 📡 Port & Network Map
- **Oikos Mesh API**: Port 8006 (FastAPI)
- **Memory Bank**: Port 8005 (FastAPI/MCP)
- **Redis**: Port 6379 (Isolated in `xnai_db_network`)
- **Prometheus**: Port 9090 (Observability)
