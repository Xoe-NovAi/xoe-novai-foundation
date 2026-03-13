# 🔱 Sovereign Tool-Use Protocol (STUP)
**Version**: 1.0.0 (SESS-23)
**Mandate**: Maximum Efficiency / Phronetic Autonomy / Context Density

## 1. Golden Tool-Use Chains
Agents must prioritize parallel, surgical tool-calls to minimize turns and context bloat.

*   **Discovery Chain**: `glob` + `grep_search` + `read_file` (specific lines) in a single turn.
*   **Implementation Chain**: `read_file` (AST verification) + `replace` + `run_shell_command` (verification) in a single turn.
*   **Verification Chain**: `gnostic-audit` + `pytest` + `metron-push` in a single turn.

## 2. Delegation Thresholds
*   **Direct Execution**: Use for single-file edits, direct inquiries, or surgical fixes.
*   **Sub-Agent (Generalist)**: Use for batch tasks (3+ files), exhaustive research, or speculative investigations.
*   **Deep Council Summons**: Use for architectural refactoring or core Gnostic logic changes.

## 3. Context-Aware Reads (Surgicality)
*   **NEVER** read a file > 500 lines in full unless absolutely necessary.
*   **ALWAYS** use `start_line` and `end_line` for targeted analysis.
*   **ALWAYS** verify the **Crystal Hash (ZLV)** of a core file before modification.

## 4. MAX_TURNS & Autonomy
*   **MAX_TURNS: 250** is authorized for high-phronesis architectural tasks.
*   **Auto-Flush Context**: Every 50 turns, agents MUST perform a **State-Seal** and re-initialize context to prevent 1GB RAM collapse.
*   **Turn-Backpressure**: If turn count > 100 without 0.8 resonance, trigger an immediate Octave Council review.

## 5. Alethia-Anchoring (AP)
Every technical claim MUST include an **Alethia-Pointer** `[AP:file#line]` to its Ground Truth. Any claim without an AP is classified as **Speculative Logos**.
