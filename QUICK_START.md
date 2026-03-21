# 🚀 Quick Start: Metropolis Foundation v4.1.2

## Current Status: ✅ Infrastructure Hardened & Hydrated

The Omega Stack is now operating under the **Metropolis Foundation v4.1.2-HARDENED-INFRA** standard.

---

## 🎯 1. Tiered Infrastructure Startup
The stack is optimized for **6.6GB RAM + 16GB zRAM**. Use the tiered approach to prevent OOM.

### Phase 1: Core Mesh
Starts Redis (Cache/Bus), PostgreSQL (IAM), Qdrant (Vector DB), and Memory Bank MCP.
```bash
make metropolis-up
```

### Phase 2: RAG & Inference
Starts the FastAPI backend and Llama-cpp-python server.
```bash
# Verify RAM availability first (free -h)
podman-compose -f infra/docker/docker-compose.yml up -d rag llama_server
```

---

## 🔑 2. Agent Authentication & Secrets
All internal mesh communication requires `auth_token` validation.

1.  **Configure .env**: Ensure your `.env` contains `REDIS_PASSWORD` and `API_KEY`.
2.  **Gemini Access**:
    ```bash
    # Setup OAuth and API Keys for account rotation
    ./scripts/quick_gemini_setup.sh
    ```

---

## 📊 3. Observability & Monitoring
Track the pulse of the Metropolis mesh.

- **Master Dashboard**: [http://localhost:3000](http://localhost:3000) (Grafana)
- **zRAM Monitor**: [http://localhost:9101/metrics](http://localhost:9101/metrics)
- **RAG Metrics**: [http://localhost:8002/metrics](http://localhost:8002/metrics)

---

## 🏛️ 4. Governance & Protocols
Every session MUST adhere to the following:

1.  **State Hydration**: Perform an atomic beat after major changes (`docs/protocols/STATE_HYDRATION_PROTOCOL.md`).
2.  **GitHub Sync**: Follow the 7-stage CI/CD parity loop (`docs/protocols/GITHUB_SYNC_PROTOCOL.md`).
3.  **The Librarian**: Monitor `session_bloat` events on the Agent Bus for automated archival.

---
*For deep strategy, refer to the [METROPOLIS MASTER INDEX](docs/METROPOLIS_MASTER_INDEX.md).*
