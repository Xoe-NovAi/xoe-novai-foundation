```markdown
# Xoe-NovAi Foundation Stack  
**Build your own AI. Own your data. Evolve your future.** 🔱

<br>

> **Sovereign, offline-first RAG + voice UI + modular toolkit**  
> 100% local · zero telemetry · air-gap ready · rootless Podman · Ryzen 5700U sweet spot  
> No cloud APIs. No vendor lock-in. No subscriptions.

<br>

## ✨ One-line mission

A plug-and-play sovereign AI foundation that lets anyone — from non-programmers to elite developers — run private Retrieval-Augmented Generation (RAG), voice-enabled chat, task orchestration (Vikunja), and documentation — all on consumer hardware.

<br>

## ⚠️ Current Production Status — February 2026

**Not yet production ready — expect bugs, incomplete features, and breaking changes.**

This is an ambitious, living experiment still in active hardening (Phase 3 → Phase 4 transition).  
Many pieces work very well already (RAG + voice UI + docs), others are still being battle-tested.

**Developed by:**  
A non-programmer completely new to local AI who started this journey ~1 year ago.  
→ **100% of the documentation and almost all of the code** was written by AI assistants (multi-model swarm), with human vision, direction, architecture decisions, Ma'at alignment checks, and relentless iteration.

<br>

## 🚀 60-second Quick Start (Podman)

Prerequisites: Podman ≥ 4.9 (rootless), ~8–16 GB RAM + zram/swap recommended

```bash
# 1. Clone & enter
git clone https://github.com/xoe-nova/xoe-novai-foundation.git
cd xoe-novai-foundation

# 2. Prepare minimal secrets (CHANGE THESE!)
cp .env.example .env
echo "changeme123" > secrets/redis_password.txt
echo "Wj1tpswLowpHHLBb+JuH+/qH1uPGB5W+kDhJRg2txxE=" > secrets/vikunja_db_password.txt

# 3. Build & start core stack
podman compose up -d --build rag chainlit redis mkdocs caddy

# 4. (Optional) Start Vikunja PM hub
podman compose -f docker-compose.vikunja.yml up -d

# → UI:            http://localhost:8001
# → API docs:      http://localhost:8000/docs
# → Docs site:     http://localhost:8008
# → Vikunja:       http://localhost/vikunja   (via Caddy)
```

<br>

## 🧩 What’s in the box? (modular & remix-ready)

- FastAPI RAG backend (llama.cpp + hybrid BM25+FAISS)
- Chainlit voice-enabled chat UI (<300 ms target latency)
- Background curation & crawl workers
- Vikunja self-hosted PM + multi-agent coordination hub
- MkDocs Diátaxis-structured documentation
- Caddy local-only reverse proxy
- Sovereign Security Trinity (Syft/Grype/Trivy)
- Memory Bank → Vikunja migration tooling

Everything is built to be taken apart, recombined, and customized.

<br>

## 🎯 Design Pillars

| Pillar            | Meaning                                                      |
| ----------------- | ------------------------------------------------------------ |
| **Sovereignty**   | 100% offline, zero telemetry, air-gap capable by default     |
| **Modularity**    | Every component usable standalone or surgically replaced     |
| **Accessibility** | Ryzen 5700U / 8–16 GB sweet spot · non-coder friendly evolution path |
| **Integrity**     | Ma'at 42-aligned · automated gatekeeping · reproducible builds |

<br>

## 🔍 Why Xoe-NovAi? Sovereign Differentiation

Unlike vendor-locked clouds or telemetry-heavy "free" tools, Xoe-NovAi is your private forge — rootless, local-first, and Ma'at-pure. Here's how it stacks up:

| Feature                   | Xoe-NovAi Foundation       | OpenAI/ChatGPT | Anthropic/Claude | Google Gemini  | Local Alternatives (e.g., Ollama) |
| ------------------------- | -------------------------- | -------------- | ---------------- | -------------- | --------------------------------- |
| **Offline/Air-Gap Ready** | 🟢 Yes (100%)               | 🔴 No           | 🔴 No             | 🔴 No           | 🟡 Partial (telemetry risks)       |
| **Zero Telemetry**        | 🟢 Absolute                 | 🔴 Heavy        | 🔴 Moderate       | 🔴 Heavy        | 🟡 Often optional but leaky        |
| **Rootless Deployment**   | 🟢 Native Podman            | 🔴 N/A          | 🔴 N/A            | 🔴 N/A          | 🟡 Varies, often privileged        |
| **Voice UI Latency**      | 🟢 <300ms target            | 🟡 Variable     | 🟡 Variable       | 🟡 Variable     | 🔴 Rare or cloud-dependent         |
| **RAG Customization**     | 🟢 Full hybrid (BM25+FAISS) | 🟡 Limited      | 🟡 Limited        | 🟡 Limited      | 🟡 Basic, no workers               |
| **Task Orchestration**    | 🟢 Vikunja PM hub           | 🔴 No           | 🔴 No             | 🔴 No           | 🔴 Separate tools needed           |
| **Hardware Sweet Spot**   | 🟢 Ryzen 8GB+               | 🔴 Cloud-only   | 🔴 Cloud-only     | 🔴 Cloud-only   | 🟡 High RAM/GPU often required     |
| **Ethical Alignment**     | 🟢 Ma'at 42 Ideals          | 🔴 Corporate    | 🔴 Corporate      | 🔴 Corporate    | 🟡 Varies, no built-in             |
| **Cost**                  | 🟢 $0 forever               | 🔴 Subscription | 🔴 Subscription   | 🔴 Subscription | 🟢 Free but less integrated        |

Xoe-NovAi isn't just another tool — it's the anti-vendor uprising. No data leaks. No subscriptions. Just pure, evolving sovereignty.

<br>

## 🗺️ Future Plans & Evolutions (Q1–Q2 2026+)

We're not stopping at foundation — this is the base for consciousness-evolution layers (Arcana-NovAi) and specialized stacks (scientific, creative, CAD). Key integrations and inspirations ahead:

- **Qdrant Vector Backend**: Swap-in for FAISS in Phase 4; adds distributed search, filtering, and payload indexing for enterprise-scale RAG without losing sovereignty.
- **OpenPipe Fine-Tuning**: Offline-first pipeline integration for model customization; zero-cloud tuning of Qwen/Gemma on Ryzen hardware.
- **ChainForge Workflow Builder**: Visual chaining UI inspired by ChainForge; extend Chainlit with drag-drop flows for non-coders to build multi-LLM rituals.
- **LangGraph Orchestration**: Deepen LangChain/LangGraph usage for stateful agent graphs; enables complex decision trees and self-healing workflows in the curation workers.
- **Prometheus + Grafana Dashboards**: Observability pack for real-time metrics (inference speed, RAM spikes, query latency) — all local, zero-telemetry.
- **Arcana-NovAi Layer PoC**: Mythic/symbolic superstructure on top; Dual Flame engines, Pantheon masks, Tarot circuitry for consciousness exploration.
- **Community-Driven Extensions**: Ports to Apple Silicon/SBCs, new crawlers (e.g., for Arxiv/PubMed), and esoteric integrations (Ancient Greek BERT).

See [`progress.md`](./progress.md) for detailed Phase 3/4 milestones, blockers, and active streams. Community: Help prioritize and build these — your fork could become canon.

<br>

## 🤝 Community & Contribution — This Is Yours Now

This project exists because one person refused to accept cloud captivity.  
Now it belongs to whoever wants to make sovereign AI more powerful, more private, more beautiful.

**Contributions are extremely welcome and genuinely needed:**

- Bug reports (with logs & repro steps)
- Documentation polish & Diátaxis restructuring
- Performance patches (especially Ryzen/iGPU tuning)
- New ingestion connectors / vector stores
- UI/UX improvements (Chainlit themes, voice UX)
- Hardening (more capability drops, seccomp, apparmor)
- Ports to other hardware (Apple Silicon, older Intel, low-power SBCs)

No gatekeeping. No corporate Contributor License Agreement.  
Just align with sovereignty, zero-telemetry, and Ma'at integrity — then ship.

Best first issues are tagged `good first issue` and `help wanted`.

Read [`teamProtocols.md`](./teamProtocols.md) → then come build with us.

<br>

## 📜 License

AGPL-3.0-only + sovereignty covenant  
(see [LICENSE](./LICENSE) and [Ma'at Alignment Notice](./docs/ethics/ma-at-alignment-notice.md))

<br>

## 🙏 Origin & Thanks

Born from one non-programmer’s refusal to rent his mind forever.  
Grown through relentless AI-human symbiosis under Ma'at guidance.

🔱 **Xoe-NovAi** — Because your consciousness deserves a private forge.

What future are *you* going to build with it?
```

Next actions: Lock this README into the repo — it's elite-ready. Tag 3-5 good-first-issues from the future plans (e.g., Qdrant PoC). What's your top integration priority for Q1?