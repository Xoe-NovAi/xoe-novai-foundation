# 🌊 Skill: State Hydrator (Metropolis Standard)

Expert guidance for agents performing Memory Bank state hydration beats. Use this when you need to finalize a session or mark a major milestone.

## 📜 Procedural Guidance

1.  **Preparation**:
    - Synthesize the session's accomplishments into three tiers: **Status**, **Key Changes**, and **Artifacts**.
    - Generate a unique **Coordination Key** using the pattern: `METROPOLIS-[STATUS]-[YYYYMMDD]`.

2.  **Execution (The Atomic Beat)**:
    - You MUST update `INDEX.md`, `activeContext.md`, and `progress.md` in a **SINGLE TURN**.
    - Ensure `INDEX.md` reflects the global status and new additions.
    - Ensure `activeContext.md` contains the `hydration` YAML metadata block.
    - Ensure `progress.md` marks tasks as `[DONE]` and updates milestones.

3.  **Verification**:
    - After writing, perform a `grep_search` across `memory_bank/` for the **Coordination Key**.
    - If the key is missing from any of the three files, you MUST fix it immediately.

4.  **Logging**:
    - Create a log in `memory_bank/recall/handovers/HYDRATION_[YYYYMMDD_HHMMSS].md`.

## 🛠️ Validation Pattern
Before finishing, the agent should state:
`"Hydration Beat Complete. Coordination Key [KEY] verified across 3 core files. Status: [STATUS]."`

---
*Skill Version: 1.0.0*
