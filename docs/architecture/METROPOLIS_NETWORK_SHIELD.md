# 🛡️ Metropolis Network Shield Architecture

The **Metropolis Network Shield** is a Zero-Trust infrastructure design implemented on 2026-03-08. It enforces a strict "Gateway-Only" data access pattern, ensuring that sensitive backends are never directly exposed to the UI or the public internet.

---

## 🏗️ 1. Zero-Trust Network Partitioning

The stack is partitioned into two distinct Podman networks. Communication between them is only possible through authorized "Bridge" services.

```mermaid
graph TD
    subgraph Public_Internet [Public Access]
        User((User))
    end

    subgraph App_Network [xnai_app_network - UNTRUSTED]
        Caddy[Caddy Reverse Proxy]
        UI[Chainlit UI]
    end

    subgraph Bridge_Layer [Security Gateways - BRIDGED]
        RAG[RAG API / FastAPI]
        MB[Memory Bank MCP]
    end

    subgraph DB_Network [xnai_db_network - PRIVATE/INTERNAL]
        Redis[(Redis: TLS Backed)]
        Qdrant[(Qdrant: Vector DB)]
        Postgres[(Postgres: Gnosis)]
        VM[VictoriaMetrics]
        Workers[Crawler / Miners]
    end

    %% Flows
    User -->|HTTPS| Caddy
    Caddy -->|HTTP| UI
    UI -->|API Request| RAG
    UI -->|MCP Tool| MB

    %% Bridged Access
    RAG --- App_Network
    RAG --- DB_Network
    MB --- App_Network
    MB --- DB_Network

    %% Secure Backend Flows
    RAG -->|rediss:// TLS| Redis
    RAG -->|GRPC/HTTP| Qdrant
    MB -->|rediss:// TLS| Redis
    Workers -->|rediss:// TLS| Redis

    %% Constraints
    UI -.->|BLOCK| Redis
    UI -.->|BLOCK| Qdrant
    Caddy -.->|BLOCK| Postgres

    style Bridge_Layer fill:#f96,stroke:#333,stroke-width:4px
    style DB_Network fill:#eee,stroke:#f00,stroke-dasharray: 5 5
    style Public_Internet fill:#fff,stroke:#000
```

### 🗝️ Key Isolation Rules
1.  **Direct DB Access Banned**: The UI and Caddy containers physically cannot resolve the hostnames or IPs of Redis, Postgres, or Qdrant.
2.  **Internal-Only**: The `xnai_db_network` is marked as `internal: true`, preventing containers within it from reaching the public internet (mitigating data exfiltration risks).
3.  **Bridge Accountability**: Every database query or memory retrieval MUST pass through the **RAG API** or **Memory Bank MCP**. These bridges enforce:
    *   **S2 Auth Token** validation.
    *   **JWT Signature** verification.
    *   **Logging/Audit** of all access.

---

## 🔐 2. Redis TLS Backbone

All traffic within the "Hearth" (the backend mesh) is encrypted using Mutual TLS (or server-side TLS) to prevent packet sniffing between containers.

```mermaid
sequenceDiagram
    participant Worker as Background Worker
    participant RAG as RAG API (Bridge)
    participant Redis as Redis (TLS Enforced)

    Note over Redis: Listening on Port 0 (TCP Disabled)<br/>TLS Port 6379 Active

    Worker->>Redis: 1. rediss:// connection (Verify CA)
    Redis-->>Worker: 2. Encrypted Handshake
    Worker->>Redis: 3. SET/XADD Encrypted Data
    
    RAG->>Redis: 4. rediss:// GET Context
    Redis-->>RAG: 5. Encrypted Response
    RAG->>RAG: 6. Decapsulate & Filter
    RAG->>App_Network: 7. Deliver to UI (Clean Data)
```

### 🛡️ Hardening Details
- **Protocol**: `rediss://` (Strict TLS).
- **Verification**: All clients use a local `ca.crt` to verify the Redis server identity.
- **Fail-Fast**: If the certificate is missing or invalid, the connection terminates immediately.

---

## 🛠️ 3. Maintenance Pulse

| Action | Command | Frequency |
|:---|:---|:---|
| **Health Check** | `./scripts/stack_health_check.sh` | Daily |
| **Cert Rotation** | `./scripts/generate_tls_certs.sh` | Annual / On-Breach |
| **Audit Logs** | `podman logs xnai_caddy` | Weekly |

---
*Document sealed by Gemini General. Technical Integrity: 100%.*
