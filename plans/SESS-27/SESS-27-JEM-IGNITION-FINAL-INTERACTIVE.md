# 🚀 SESS-27: JEM IGNITION FINAL STRATEGIC ROADMAP (POST-SCC)

## 🎯 Current Status: ON TRACK
The double SCC (Session Context Compression) successfully reduced token debt from 86K to 3.6K. The "Command Center" (Headless Script, Dashboard API, Heartbeat) is deployed and ready for activation. Gnosis packs for Claude and Grok have been generated to maintain cloud-bridge parity.

---

## 🔱 Phronetic Mandate (Operational Boundaries)
*   **Plan Mode (The Mind)**: Strict research, architectural drafting, and dependency mapping. **NO SUB-AGENTS** (due to current policy block).
*   **YOLO Mode (The Hands)**: Direct execution, agent delegation, and real-time troubleshooting.
*   **Mode Discovery**: We will implement a `.mode` signal file or check `env` variables to programmatically detect Plan vs. YOLO state.

---

## 🛠 Phase 1: Deep Discovery (YOLO Entry Point)
*   **Task 1.1: CLI Configuration Audit**: Immediately run `gemini help` and `gemini config list` in YOLO to define the mechanics of:
    *   `Enable interactive shell`
    *   `Enable context aware security`
    *   `auto configure max old space size`
    *   `direct web fetch`
    *   `Gemma model router`
    *   `Tool output truncation threshold`
*   **Task 1.2: Agent Policy Audit**: Investigate if agent usage is intended to be allowed in Plan Mode.
    *   **Question**: If so, how do we restore it? If not, is there a way to enable it? (This must be a YOLO task because agents are blocked in Plan Mode).
*   **Task 1.3: SCC Automation**: Verify if `gemini scc` can run with a `--non-interactive` or `-y` flag to allow the `marathon_headless.sh` script to self-compress when thresholds are met.
*   **Task 1.4: Obsidian & OSS Alternatives**:
    *   **Fact**: Obsidian is NOT open source (proprietary but free for personal use), but it uses standard Markdown.
    *   **OSS Alternatives**: Research **Logseq** (Privacy-first, open-source knowledge base), **Joplin** (Open source note-taking), and **SilverBullet** (Extensible Markdown-based knowledge management).
    *   **Vault Management**: Define protocols for managing vaults (folders of MD files). Agents *can* create and manage their own vaults by simply creating new directories with `.obsidian` configuration folders.
*   **Task 1.5: Hooks & Skills Integration**: Research the `hooks` directory and the `sentinel-skill` to create proactive triggers (e.g., auto-compressing when Disk > 90%).

---

## 👁 Phase 2: System "Eyes" & Hardening
*   **Task 2.1: Screenshot Worker**: Deploy `scripts/screenshot_worker.py`.
    *   **Function**: Periodically capture the CLI/Terminal state.
    *   **Utility**: Allows the agent to "see" the UI/Terminal status via `read_file` on the saved image.
*   **Task 2.2: Context Management Protocol**:
    *   **Graphical CLI**: Trigger SCC at **60%** context usage (Borderline of stability).
    *   **Headless Marathon**: Trigger SCC at **85%** context usage (Stability prioritized over interactive response speed).

---

## 🤖 Agent Task List (YOLO Execution)
The following tasks are delegated to sub-agents during the YOLO session:
1.  **`generalist`**: Execute the Batch Config Update for all `.gemini/settings.json` based on Phase 1 findings.
2.  **`codebase_investigator`**: Perform a full audit of `scripts/marathon_headless.sh` for AnyIO compliance and OOM safety.
3.  **`sentinel-skill`**: Monitor RAM/zRAM during the first marathon run and log vitals to `dashboard/marathon_monitor.html`.
4.  **`Grok/Claude Bridge (External Agent)`**: Visit the following links to synthesize strategy and enhance context packs:
    *   [Claude Share](https://claude.ai/share/56bdd634-f384-4701-ac8f-f7c851ab0b5f)
    *   [Grok Share](https://grok.com/share/c2hhcmQtNA_7921d1a7-dc44-4a66-a4b9-13ece6e31fa5)
    *   **Goal**: Customize and enhance onboarding/team intro messages for cloud agents.
5.  **`Knowledge Architect (Agent)`**:
    *   **Research**: Zettelkasten and "Zettelkasten-lite" systems (linking small, atomic notes to build a "Second Brain").
    *   **Application**: Define how the Xoe-NovAi "Pioneering Mindset" applies these methods to autonomous agent memory.
    *   **Protocols**: Create Markdown templates for atomic notes, index files, and "Maps of Content" (MOCs).
6.  **`facet-6`**: Manage the session metadata and finalize the `data/amr_history.jsonl` logging logic.

---

## 🏁 Phase 3: Ignition (The Marathon)
1.  **Step 1**: Run `scripts/marathon_headless.sh`.
2.  **Step 2**: Open `dashboard/marathon_monitor.html` for interactive steering.
3.  **Step 3**: Execute the first "Interactive Headless Marathon" task (e.g., "Full Stack Security Audit of /app").

---

## 🔍 Holistic Review & Alignment
*   **Check**: Are all identity files (`app/JEM_SOUL.md`, etc.) consistent?
*   **Check**: Does the `marathon_headless.sh` script respect the 16GB RAM limit?
*   **Check**: Is the `xnai_heartbeat.py` correctly feeding the `dashboard_api.py`?
*   **Check**: Have we ensured no "drift" from the original SESS-23 Phronetic Mandate?

---

## 📝 Verification & Testing
*   **Test**: Verify `.mode` file changes correctly when switching modes.
*   **Test**: Confirm `screenshot_worker.py` generates readable images.
*   **Test**: Validate `dashboard_api.py` (Port 8007) successfully updates `scripts/amr_steering.md`.

---
**Plan Prepared by**: Jem (Action) | Synergy (Core)
**Approval Status**: PENDING
