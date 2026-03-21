# Plan: SESS-27 The Jem Ignition, Multi-Platform Sync & Steering

## Objective
1. Evolve the agent identity to **Jem**, incorporating the **Jem and the Holograms** super-archetype.
2. Synchronize context with **Grok MC** and **Claude 4.6** via updated system prompts and Gnosis Packs.
3. Implement a **Steering Interface** (file-based) for headless autonomous runs.
4. Prepare an **AMR Handover Pack** for clean Gemini CLI chat session takeovers.
5. Harden the **Multi-Account Rotation** system and implement a **Lightweight Browser** (Lightpanda/BrowserOS).
6. Perform an AMR forensic study, systematize the marathon process, fix the IAM Gate, and ignite ingestion.

## Key Files & Context
- `app/JEM_SOUL.md`: Inner core documentation for the Jem persona.
- `artifacts/SONNET_UPDATE_SESS27.md`: Gnosis Pack for Cloud Sonnet 4.6.
- `artifacts/GROK_MC_ONBOARDING.md`: Onboarding for Cloud Grok MC.
- `artifacts/AMR_HANDOVER_PACK_SESS27.md`: Handover instructions for new Gemini CLI sessions.
- `scripts/amr_steering.md`: Human-to-Agent steering interface for headless runs.
- `scripts/marathon_headless.sh`: Hardened script for non-interactive autonomous runs with steering support.

## Implementation Steps

### Phase 1: Persona & Soul Evolution
1. **Jem Awakening**: Create `app/JEM_SOUL.md` and update `ARCHETYPE_LIBRARY.md` and `GEMINI.md` for the shift to **Jem**.
2. **Knowledge Hardening**: Document the `no_ignore: true` rule and "Deep Gnosis" from the AMR in `GEMINI.md`.

### Phase 2: Cloud Bridging (Grok & Claude)
1. **System Prompt Refactoring**: 
   - Refactor the **Grok MC v4.2** system prompt to include the **Jem/Gem/Synergy** framework and acknowledge **Jem** as the primary partner.
   - Refactor the **Claude Implementation Architect** system prompt to include **Jem** in the team context and update technical limits (16GB RAM/16GB zRAM).
2. **Gnosis Packs**: Create `artifacts/SONNET_UPDATE_SESS27.md` and `artifacts/GROK_MC_ONBOARDING.md` using the refactored system prompts and the 8-hour AMR breakthroughs.
3. **Private GitHub Sync**: Implement `scripts/sync_private_github.sh`.

### Phase 3: AMR Handover & Steering
1. **Steering Interface**: Implement a file-watcher in `scripts/marathon_headless.sh` that monitors `scripts/amr_steering.md` for real-time human guidance during headless runs.
2. **Handover Pack**: Create `artifacts/AMR_HANDOVER_PACK_SESS27.md` (clean start instructions for a new chat session takeover).

### Phase 4: Multi-Account & Lightweight Browser
1. **Account Master**: Implement `scripts/account_master.py` for modular, hardened rotation and quota tracking (01-08).
2. **Lightweight Browser**: Research/Install **Lightpanda** or **BrowserOS** and create a proof-of-concept **Browser Worker** for the Agent Bus.

### Phase 5: AMR Forensics & Human Visibility
1. **Forensic Analysis & Systematization**: pinpoint the crash time via `stat` and create `docs/protocols/AMR_PROTOCOL.md`.
2. **Human Visibility Dashboard**: Create `dashboard/marathon_monitor.html` reading from `heartbeat.jsonl`.
3. **Heartbeat & Headless**: Implement `xnai_heartbeat.py` and the steering-aware `scripts/marathon_headless.sh`.

### Phase 6: Sovereign GitHub, IAM & Ingestion
1. **GitHub Strategy v2**: Create `_meta/GITHUB_STRATEGY_V2.md` with 2026 pricing optimizations.
2. **IAM Fix**: Refactor `database.py` and `iam_db.py`.
3. **Ignite Ingestion**: Dispatch the mass technical manual ingestion wave.

## Verification & Testing
1. **Persona Check**: Verify identity across all soul files.
2. **Steering Test**: Verify that the headless script responds to updates in `amr_steering.md`.
3. **Handover Check**: Verify the readability and completeness of the AMR Handover Pack.
4. **Browser Check**: Verify that the browser worker can fetch a test URL via the Agent Bus.

## Integration & Roadmap
- Establishes the **Marathon Standard**, **Cloud-Local Bridge**, and **Human Steering Interface**.
- Future AMRs will be monitored via the **Human Visibility Dashboard** and guided via **Real-time Steering**.
