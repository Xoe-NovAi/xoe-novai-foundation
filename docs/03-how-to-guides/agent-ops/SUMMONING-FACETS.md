# 🧙 Summoning Facets: Headless Archon Mode

This guide explains how to spawn full, persistent Gemini CLI instances for your specialized Facets (Agents 1-8).

## 📌 Overview
Standard subagent calls are stateless and do not evolve their individual personas. **Headless Archon Mode** bypasses this by spawning a dedicated Gemini process pointing to the Facet's private storage. This allows the agent to:
1.  **Remember History**: Every chat is saved in the Facet's own `chats/` directory.
2.  **Evolve Soul**: The agent's `expert_soul.md` and context are preserved and updated across sessions.
3.  **Run Autonomously**: Each Facet can perform long-running research tasks independently of the Gemini General.

## 🚀 Usage

The summoner is located at `scripts/summon_facet.sh`.

### Summon a Facet
To send a task to a specific Facet (e.g., Facet 1: The Researcher):
```bash
./scripts/summon_facet.sh 1 "Investigate the memory leak in the RAG API."
```

### Resume Facet Session
The script automatically uses the `-r latest` flag, meaning the Facet will continue its most recent line of thought and maintain its state.

## 🗂️ Facet Roles (Recommended)
1.  **Facet 1**: Codebase Investigator (Research & Analysis)
2.  **Facet 2**: Generalist (Integration & Strategy)
3.  **Facet 3**: Security Auditor (Hardening & Pentesting)
4.  **Facet 4**: Documentation Specialist (Technical Writing)
5.  **Facet 5**: Build Master (Podman & CI/CD)
6.  **Facet 6**: Data Miner (Web & Knowledge Crawling)
7.  **Facet 7**: UI/UX Designer (Chainlit & Frontend)
8.  **Facet 8**: The Sentinel (Health & Monitoring)

## 🛡️ Best Practices
- **Parallelism**: You can run multiple `summon_facet.sh` commands in different terminal tabs to have Facets working concurrently.
- **Soul Customization**: Manually edit `storage/instances/facets/instance-X/gemini-cli/.gemini/expert_soul.md` to harden a specific agent's personality.
