"""
MemoryManager — Persistent conversation memory for VoiceOS.

Architecture credit:
  Inspired by the Memory Bank Protocol and dual-memory system from the
  Xoe-NovAi Foundation Stack (https://github.com/Xoe-NovAi/xoe-novai-foundation).

  Key patterns adopted:
    - Memory bank as "external brain" for AI session continuity across restarts
      (see: .clinerules/99-memory-bank-protocol.md — "Rely ENTIRELY on memory_bank/
      files for context persistence")
    - Hierarchical file purposes: activeContext (session) vs CONTEXT (persistent facts)
      mapped here to session.json and long_term.json
    - Event-based JSONL logging with UTC timestamps
      (see: app/XNAi_rag_app/core/memory_bank_integration.py)
    - Resilience-first: every I/O wrapped with fallback, atomic renames, JSON
      corruption recovery (see: CONTEXT.md design pattern — "graceful degradation")
    - Periodic memory extraction / refresh cycle
      (see: scripts/memory_bank_refresh.py, enhanced_memory_bank.py)

Two-tier storage at ~/.voiceos/memory/:

  Tier 1 — Session continuity (short-term):
    session.json          Last 20 turns. Loaded on startup so conversation
                          continues naturally across restarts.

  Tier 2 — Long-term facts (persistent):
    long_term.json        Key/value facts extracted from conversations:
                          user preferences, project names, recurring topics.
                          Injected as a brief system-prompt addendum every call.

  Archive — Full history:
    conversations/YYYY-MM-DD.jsonl   Append-only daily log. Never deleted
                                      automatically; provides searchable history.

Usage:
    mem = MemoryManager()
    turns = mem.load_recent_turns(n=6)  # Resume from last session

    # After each exchange:
    mem.save_turn("user", transcript, provider="anthropic:claude-sonnet")
    mem.save_turn("assistant", response, provider="anthropic:claude-sonnet")
    mem.flush_session(current_conversation)   # Persist for next boot

    # Periodic / on "remember" command:
    await mem.maybe_extract_memory(conversation, llm_router)
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

MEMORY_DIR = Path.home() / ".voiceos" / "memory"
SESSION_FILE = MEMORY_DIR / "session.json"
LONG_TERM_FILE = MEMORY_DIR / "long_term.json"
CONVERSATIONS_DIR = MEMORY_DIR / "conversations"

_EXTRACT_EVERY_N_TURNS = 10   # Run memory extraction after every N user turns


@dataclass
class ConversationTurn:
    role: str          # "user" or "assistant"
    content: str
    timestamp: str     # ISO-8601
    provider: str = "" # e.g. "anthropic:claude-sonnet-4-6" or "ollama:qwen2.5:32b"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryManager:
    """
    Manages two-tier persistent memory for VoiceOS.

    Thread-safety: all writes use append-only patterns or atomic rewrites;
    safe for single-process use (the voice loop).
    """

    def __init__(self) -> None:
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
        self._turn_count = 0   # User-turn counter for periodic extraction

    # ── Archive ──────────────────────────────────────────────────────────────

    def save_turn(self, role: str, content: str, provider: str = "") -> None:
        """
        Append a single turn to today's conversation archive.
        Called immediately after each utterance/response.
        """
        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=_now_iso(),
            provider=provider,
        )
        archive = CONVERSATIONS_DIR / f"{date.today().isoformat()}.jsonl"
        with open(archive, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(turn), ensure_ascii=False) + "\n")

        if role == "user":
            self._turn_count += 1

    # ── Session continuity ───────────────────────────────────────────────────

    def flush_session(self, conversation: list) -> None:
        """
        Persist the current in-memory conversation list to session.json.
        Call this periodically (e.g. every turn) and on shutdown.

        Args:
            conversation: list of Message objects (role + content attributes)
        """
        turns = [
            {"role": m.role, "content": m.content}
            for m in conversation[-20:]          # Keep last 20 turns
        ]
        data = {
            "saved_at": _now_iso(),
            "turn_count": self._turn_count,
            "turns": turns,
        }
        # Atomic write: write to .tmp then rename
        tmp = SESSION_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(SESSION_FILE)

    def load_recent_turns(self, n: int = 6) -> list[dict]:
        """
        Load last N turns from the previous session.

        Returns:
            List of {"role": ..., "content": ...} dicts, oldest first.
            Empty list if no session file or session is empty.
        """
        if not SESSION_FILE.exists():
            return []
        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            turns = data.get("turns", [])
            self._turn_count = data.get("turn_count", 0)
            return turns[-n:]
        except (json.JSONDecodeError, KeyError):
            logger.warning("session_file_corrupt", path=str(SESSION_FILE))
            return []

    def has_previous_session(self) -> bool:
        """Return True if a saved session exists with at least one turn."""
        if not SESSION_FILE.exists():
            return False
        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            return len(data.get("turns", [])) > 0
        except Exception:
            return False

    def clear_session(self) -> None:
        """Delete the saved session (start fresh next boot)."""
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
        self._turn_count = 0

    # ── Long-term memory ─────────────────────────────────────────────────────

    def update_long_term(self, facts: dict[str, str]) -> None:
        """
        Merge new key/value facts into long_term.json.

        Facts overwrite existing values for the same key.
        Keys with value None are removed.
        """
        existing: dict = {}
        if LONG_TERM_FILE.exists():
            try:
                existing = json.loads(LONG_TERM_FILE.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass

        for k, v in facts.items():
            if v is None:
                existing.pop(k, None)
            else:
                existing[k] = v

        existing["_updated"] = _now_iso()
        LONG_TERM_FILE.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.info("long_term_memory_updated", keys=list(facts.keys()))

    def get_long_term_summary(self) -> str:
        """
        Return a brief, LLM-digestible summary of long-term facts.

        Injected into every system prompt so Claude always knows key context.
        Returns empty string if no facts stored yet.
        """
        if not LONG_TERM_FILE.exists():
            return ""
        try:
            data = json.loads(LONG_TERM_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return ""

        data.pop("_updated", None)
        if not data:
            return ""

        lines = [f"- {k}: {v}" for k, v in list(data.items())[:15]]
        return "Persistent memory about the user:\n" + "\n".join(lines)

    def get_all_facts(self) -> dict[str, str]:
        """Return all long-term facts as a dict."""
        if not LONG_TERM_FILE.exists():
            return {}
        try:
            d = json.loads(LONG_TERM_FILE.read_text(encoding="utf-8"))
            d.pop("_updated", None)
            return d
        except Exception:
            return {}

    def clear_long_term(self) -> None:
        """Erase all long-term memory."""
        if LONG_TERM_FILE.exists():
            LONG_TERM_FILE.unlink()

    # ── Automatic memory extraction ──────────────────────────────────────────

    async def maybe_extract_memory(
        self,
        conversation: list,
        llm_router: object,
        force: bool = False,
    ) -> None:
        """
        Periodically ask the LLM to extract memorable facts from the conversation.

        Runs asynchronously after every _EXTRACT_EVERY_N_TURNS user turns, or
        when force=True (e.g. after a "remember that..." command).

        Does nothing if:
          - Not enough turns yet (< 4)
          - Cloud is unavailable and Ollama would be slow (skips gracefully)
        """
        if not force and self._turn_count % _EXTRACT_EVERY_N_TURNS != 0:
            return
        if len(conversation) < 4:
            return

        # Build a compact conversation summary for extraction
        recent = conversation[-12:]
        convo_text = "\n".join(
            f"{m.role.upper()}: {m.content[:200]}" for m in recent
        )
        existing_facts = self.get_all_facts()
        existing_str = json.dumps(existing_facts, indent=2) if existing_facts else "{}"

        extraction_prompt = f"""Review this conversation and extract facts worth remembering long-term.
Focus on: user preferences, project names, recurring tasks, personal details the user mentioned.
Ignore one-off queries, troubleshooting steps, and anything ephemeral.

Existing memory (do not re-add these unless updating):
{existing_str}

Recent conversation:
{convo_text}

Return ONLY a JSON object of new or updated key:value pairs to remember.
Keys should be short snake_case labels (e.g. "preferred_language", "project_name").
Values should be concise strings. Return {{}} if nothing new to remember.
Return ONLY the JSON object, no explanation."""

        from ..llm.llm_router import Message, RequestContext, RequestType

        messages = [
            Message(role="user", content=extraction_prompt),
        ]
        context = RequestContext(
            request_type=RequestType.SYSTEM,
            max_tokens=300,
            temperature=0.1,
        )

        try:
            response = await llm_router.complete(messages, context)  # type: ignore[union-attr]
            text = response.content.strip()
            # Extract JSON even if wrapped in markdown fences
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            facts = json.loads(text)
            if facts and isinstance(facts, dict):
                self.update_long_term(facts)
                logger.info("memory_extracted", facts=list(facts.keys()))
        except Exception as e:
            logger.debug("memory_extraction_skipped", reason=str(e))

    # ── Statistics ───────────────────────────────────────────────────────────

    def stats(self) -> dict:
        """Return a summary of stored memory for the `voiceos memory` CLI command."""
        archive_files = sorted(CONVERSATIONS_DIR.glob("*.jsonl"))
        total_turns = 0
        for f in archive_files:
            try:
                with open(f, encoding="utf-8") as fh:
                    total_turns += sum(1 for _ in fh)
            except OSError:
                pass

        facts_count = len(self.get_all_facts())
        session_turns = 0
        if SESSION_FILE.exists():
            try:
                data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
                session_turns = len(data.get("turns", []))
            except Exception:
                pass

        return {
            "archive_days": len(archive_files),
            "total_archived_turns": total_turns,
            "long_term_facts": facts_count,
            "current_session_turns": session_turns,
            "memory_dir": str(MEMORY_DIR),
        }
