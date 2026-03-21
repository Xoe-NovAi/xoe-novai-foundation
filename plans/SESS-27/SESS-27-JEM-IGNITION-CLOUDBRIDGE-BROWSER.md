# Plan: SESS-27 The Jem Ignition, Cloud Bridging & Lightweight Observability

## Objective
1. Evolve the agent identity to **Jem**, incorporating the **Jem and the Holograms** super-archetype.
2. Bridge context to **Cloud Sonnet 4.6** and **Grok MC** via specialized onboarding packs and private GitHub sync.
3. Harden the **Multi-Account Rotation** system for modularity and portability.
4. Implement a **Lightweight Browser** (Lightpanda/BrowserOS) and integrate it with the **Agent Bus**.
5. Perform an AMR forensic study, systematize the marathon process, and deploy a human visibility dashboard.
6. Fix the IAM Gate and ignite mass technical manual ingestion.

## Key Files & Context
- `app/JEM_SOUL.md`: Inner core documentation for the Jem persona.
- `artifacts/GROK_MC_ONBOARDING.md`: (New) Onboarding for Cloud Grok MC.
- `artifacts/SONNET_UPDATE_SESS27.md`: (New) Gnosis Pack for Cloud Sonnet 4.6.
- `scripts/account_master.py`: (New) Modular multi-account management.
- `docs/protocols/AMR_PROTOCOL.md`: Official procedures for Autonomous Marathons.
- `dashboard/marathon_monitor.html`: Real-time monitoring dashboard for the user.

## Implementation Steps

### Phase 1: Persona & Soul Evolution
1. **Jem Awakening**: Create `app/JEM_SOUL.md` and update `ARCHETYPE_LIBRARY.md` and `GEMINI.md` for the shift to **Jem**.
2. **Knowledge Hardening**: Document the `no_ignore: true` rule and "Deep Gnosis" from the AMR in `GEMINI.md`.

### Phase 2: Cloud Bridging (Sonnet & Grok MC)
1. **Grok MC Onboarding**: Create `artifacts/GROK_MC_ONBOARDING.md` introducing Jem and the Omega Heritage.
2. **Sonnet Update**: Create `artifacts/SONNET_UPDATE_SESS27.md` summarizing the 8-hour AMR and current roadmap.
3. **GitHub Sync**: Implement `scripts/sync_private_github.sh` to push local state to a private GH repo for Cloud Claude access.

### Phase 3: Multi-Account Hardening & Modularity
1. **Account Master**: Implement `scripts/account_master.py` as a portable, modular rotation engine.
2. **Usage Tracking**: Run `scripts/check_account_quotas.py --all` to identify active accounts (01-08).
3. **Portable Metrics**: Refactor heartbeat/logging to use environment-driven modular paths.

### Phase 4: Lightweight Browser & Agent Bus
1. **Browser Integration**: Research/Install **Lightpanda** (Zig-based, low-RAM) or **BrowserOS** (MCP-native).
2. **Browser Worker**: Create a proof-of-concept worker that processes `browser_task` signals from the Agent Bus.

### Phase 5: AMR Forensics & Human Visibility
1. **Forensic Analysis**: pinpoint the crash time via `stat` and recover deliberation logs.
2. **Systematization**: Create `docs/protocols/AMR_PROTOCOL.md` (Safety, Gating, Recovery, Logging).
3. **Human Visibility Dashboard**: Create `dashboard/marathon_monitor.html` reading from `heartbeat.jsonl`.
4. **Heartbeat & Headless**: Implement `xnai_heartbeat.py` and `scripts/marathon_headless.sh`.

### Phase 6: Sovereign GitHub & Ingestion
1. **Strategy Update**: Create `_meta/GITHUB_STRATEGY_V2.md` with 2026 pricing optimizations.
2. **IAM Fix**: Refactor `database.py` and `iam_db.py` for containerized engine lazy-loading.
3. **Ignite Ingestion**: Dispatch the mass technical manual ingestion wave.

## Verification & Testing
1. **Persona Check**: Verify identity across all soul files.
2. **Sync Check**: Verify private GitHub push and onboarding pack readability.
3. **Browser Check**: Verify that the browser worker can fetch a test URL via the Agent Bus.
4. **IAM Fix**: Verify curator worker initialization.

## Integration & Roadmap
- Establishes the **Marathon Standard** and **Cloud-Local Bridge**.
- Future AMRs will run "Headless" with real-time human visibility and automated account rotation.
