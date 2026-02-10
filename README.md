```markdown
# Xoe-NovAi Foundation Stack  
**Build your own AI. Own your data. Evolve your future.** 🔱

<br>

> Sovereign, offline-first RAG + voice UI + modular orchestration toolkit  
> 100% local · zero telemetry · air-gap ready · rootless Podman-first  
> Ryzen 5700U / 8–16 GB sweet spot · no cloud APIs · no vendor lock-in

<br>

## Mission

A modular, self-hosted foundation for private Retrieval-Augmented Generation (RAG), voice-enabled interfaces, background content pipelines, task orchestration, and living documentation — designed from the ground up for sovereignty and remixability.

<br>

## ⚠️ Production Readiness — February 2026

**Early Release**  
This is an early release. Bugs, incomplete features, and breaking changes should be expected.

Core flows (RAG retrieval, voice UI, basic ingestion) are stable and performant on target hardware.  
Higher-order features (Redis reconnection, full worker fault tolerance, observability) are still maturing.

We are actively hardening the stack and welcome community help to make it production-ready.

<br>

## 🚀 Quick Start (Podman Rootless)

```bash
# 1. Clone
git clone https://github.com/xoe-nova/xoe-novai-foundation.git
cd xoe-novai-foundation

# 2. Secrets (change these!)
cp .env.example .env
echo "changeme123" > secrets/redis_password.txt
echo "Wj1tpswLowpHHLBb+JuH+/qH1uPGB5W+kDhJRg2txxE=" > secrets/vikunja_db_password.txt

# 3. Launch core stack
podman compose up -d --build rag chainlit redis mkdocs caddy

# 4. (Optional) Vikunja PM hub
podman compose -f docker-compose.vikunja.yml up -d

# Access points:
# • Voice UI          http://localhost:8001
# • API /docs         http://localhost:8000/docs
# • Documentation     http://localhost:8008
# • Vikunja (proxied) http://localhost/vikunja
```

<br>

## Core Components

- **RAG Engine** — FastAPI + llama.cpp inference + hybrid BM25 + FAISS retrieval  
- **Voice Interface** — Chainlit + WebRTC voice I/O (<300 ms target E2E latency)  
- **Workers** — Background curation, crawl4ai ingestion, content cleaning  
- **PM & Coordination Hub** — Vikunja 0.24.1 (self-hosted task & agent sync)  
- **Docs Platform** — MkDocs Material + Diátaxis structure  
- **Proxy & Hardening** — Caddy 2.8 local-only reverse proxy  
- **Security Pipeline** — Sovereign Trinity (Syft SBOM + Grype CVE + Trivy secret scan)  
- **Migration Bridge** — Memory Bank markdown → Vikunja structured tasks

All pieces are designed for surgical replacement or standalone use.

<br>

## Sovereign Differentiation

| Feature                        | Xoe-NovAi Foundation          | OpenAI / Claude / Gemini | Typical Local Stacks (Ollama / LM Studio) |
|--------------------------------|-------------------------------|---------------------------|--------------------------------------------|
| Offline / Air-Gap by Default   | Yes                           | No                        | Partial (often leaky)                      |
| Zero Telemetry Guarantee       | Absolute                      | No                        | Usually optional, rarely enforced          |
| Rootless Podman Native         | Yes                           | N/A                       | Rare                                       |
| Built-in Voice UI (<300 ms)    | Yes                           | Cloud-dependent           | Rare / cloud-only                          |
| Hybrid BM25 + Vector RAG       | Yes (FAISS default)           | Limited customization     | Usually basic vector-only                  |
| Integrated PM / Agent Hub      | Yes (Vikunja)                 | No                        | No                                         |
| Ma'at-aligned Ethical Gatekeeping | Yes                        | No                        | No                                         |
| Hardware Target                | Ryzen 5700U 8–16 GB           | Cloud-only                | Often 24+ GB + discrete GPU                |
| Cost Forever                   | $0                            | Subscription              | Free but fragmented                        |

Xoe-NovAi is built for people who refuse rent-seeking intelligence.

<br>

## Roadmap — Near & Mid-Term (2026 Q1–Q3)

- Re-enable & harden Vikunja + Redis reconnection logic  
- **Qdrant** optional vector backend (payload filtering, distributed mode)  
- **OpenPipe**-style offline fine-tuning pipeline (Qwen/Gemma on consumer hardware)  
- **ChainForge**-inspired visual workflow builder layered on Chainlit  
- **LangGraph** deep integration for stateful, self-healing agent graphs  
- Prometheus + Grafana local observability pack (inference metrics, RAM/thermal)  
- Arcana-NovAi PoC: symbolic/mythic routing layer (Pantheon masks, Tarot circuitry)  
- Community ports: Apple Silicon, low-power SBCs, new domain crawlers

Detailed status, blockers, and owners live in [`progress.md`](./progress.md).

<br>

## Contributing

We welcome contributions that preserve sovereignty, zero-telemetry, and modular integrity.

**Your help is needed to turn this early release into a powerful, production-ready sovereign AI stack.**

High-impact starters:

- Bug reports + repro steps
- Diátaxis docs restructuring & link validation
- Ryzen/iGPU performance tuning
- New ingestion connectors (Arxiv, PubMed, custom APIs)
- Chainlit theme / voice UX polish
- Additional hardening (seccomp, apparmor, capability drops)

Tagged `good first issue` and `help wanted` labels for entry points.  
See [`teamProtocols.md`](./teamProtocols.md) before large PRs.

<br>

## License

AGPL-3.0-only + explicit sovereignty covenant  
([LICENSE](./LICENSE) · [Ma'at Alignment Notice](./docs/ethics/ma-at-alignment-notice.md))

<br>

🔱 Xoe-NovAi — Private forge for sovereign intelligence.

What piece do you want to harden, extend, or remix first?
```

### What changed
- Explicit **“Early Release”** header with your exact wording in the Production Readiness section
- Clear call-to-action: “We welcome community help to make it production-ready”
- Strengthened Contributing section to directly echo your request: “Your help is needed to turn this early release into a powerful, production-ready sovereign AI stack”
- Kept everything else tech-focused and polished

Ready to commit as the new `README.md`.  

Next: Shall we create the first batch of `good first issue` tickets based on the roadmap (Qdrant, Redis hardening, docs restructure, etc.)? Or lock this in and move to something else?