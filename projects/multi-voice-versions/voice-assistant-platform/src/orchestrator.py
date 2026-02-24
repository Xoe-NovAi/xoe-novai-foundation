"""
VoiceOrchestrator — Main voice loop for VoiceOS.

Connects all modules into a working voice pipeline:

  Microphone → VAD → STT → Intent → Handler → LLM → TTS → Speaker

This is the entry point for the voice session.
Run directly: python -m src.orchestrator
Or via CLI:   voiceos start
"""

from __future__ import annotations

import asyncio
import os
import signal
from dataclasses import dataclass
from enum import Enum

import structlog

from .config import load_config, save_config_value
from .audio.audio_processor import AudioProcessor, AudioConfig
from .stt.stt_manager import STTManager, STTConfig, STTError
from .tts.tts_manager import TTSManager, TTSConfig
from .llm.llm_router import LLMRouter, LLMMode, RequestContext, RequestType, Message, _format_duration
from .memory.memory_manager import MemoryManager
from .registry.service_registry import ServiceRegistry
from .accessibility.accessibility_orchestrator import AccessibilityOrchestrator
from .events.voice_event_bus import VoiceEventBus, VoiceEvent, get_bus

# Load persisted config before anything reads from env
load_config()

logger = structlog.get_logger(__name__)


class SessionState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


# Provider-switch phrases → (LLMMode, short_label)
_PROVIDER_SWITCH_PHRASES: list[tuple[list[str], LLMMode, str]] = [
    (
        ["switch to cloud", "use claude", "use cloud", "switch to claude", "go online",
         "enable cloud", "cloud mode"],
        LLMMode.CLAUDE_ONLY,
        "cloud",
    ),
    (
        ["switch to local", "go offline", "use local", "use ollama", "offline mode",
         "local mode", "go local"],
        LLMMode.OLLAMA_ONLY,
        "local",
    ),
    (
        ["switch to hybrid", "use hybrid", "hybrid mode"],
        LLMMode.HYBRID,
        "hybrid",
    ),
]


def _detect_provider_switch(text_lower: str) -> tuple[LLMMode, str] | None:
    """Return (LLMMode, label) if text is a provider-switch command, else None."""
    for phrases, mode, label in _PROVIDER_SWITCH_PHRASES:
        if any(phrase in text_lower for phrase in phrases):
            return mode, label
    return None


def _classify_intent(text: str) -> tuple[RequestType, str | None]:
    """
    Simple keyword-based intent classification.

    Returns:
        (RequestType, app_name_if_nav)
    """
    text_lower = text.lower().strip()

    # Navigation: "open X", "switch to X", "focus X" — must start the sentence
    # Note: "switch to cloud/local/hybrid" is handled before nav in _handle_intent
    nav_triggers = ["open ", "go to ", "focus ", "launch "]
    for trigger in nav_triggers:
        if text_lower.startswith(trigger):
            app = text_lower[len(trigger):].strip().rstrip(".?!")
            app = " ".join(w.capitalize() for w in app.split())
            return RequestType.NAVIGATION, app

    # "switch to <app>" — but only if not a provider switch
    if text_lower.startswith("switch to ") and not _detect_provider_switch(text_lower):
        app = text_lower[len("switch to "):].strip().rstrip(".?!")
        app = " ".join(w.capitalize() for w in app.split())
        return RequestType.NAVIGATION, app

    # Voice control
    voice_triggers = ["stop", "be quiet", "shut up", "repeat that", "say that again"]
    if any(t in text_lower for t in voice_triggers):
        return RequestType.SYSTEM, None

    # Code
    code_triggers = ["write", "code", "function", "debug", "fix", "implement", "class", "script"]
    if any(t in text_lower for t in code_triggers):
        return RequestType.CODE, None

    # System queries
    system_triggers = ["what time", "status", "check", "what is", "what's the"]
    if any(t in text_lower for t in system_triggers):
        return RequestType.QUERY, None

    return RequestType.QUERY, None


@dataclass
class OrchestratorConfig:
    """Configuration for the VoiceOrchestrator."""
    llm_mode: LLMMode = LLMMode.CLAUDE_ONLY   # Default: Anthropic API
    announce_listening: bool = True
    announce_processing: bool = True
    max_conversation_turns: int = 20
    output_device: str = "Mac mini Speakers"

    @classmethod
    def from_env(cls) -> "OrchestratorConfig":
        mode_str = os.getenv("VOICEOS_LLM_MODE", "claude_only")
        mode_map = {
            "ollama_only": LLMMode.OLLAMA_ONLY,
            "hybrid": LLMMode.HYBRID,
            "claude_only": LLMMode.CLAUDE_ONLY,
        }
        return cls(
            llm_mode=mode_map.get(mode_str, LLMMode.HYBRID),
            output_device=os.getenv("VOICEOS_OUTPUT_DEVICE", "Mac mini Speakers"),
        )


class VoiceOrchestrator:
    """
    Main orchestrator: connects all VoiceOS modules into the voice loop.

    Lifecycle:
        orchestrator = VoiceOrchestrator()
        await orchestrator.start()    # Initialize, check permissions, speak greeting
        await orchestrator.run()      # Voice loop (blocks until stopped)
        await orchestrator.stop()     # Graceful shutdown

    Voice loop (one iteration):
        1. Wait for speech (VAD)
        2. Transcribe audio (STT)
        3. Classify intent
        4. Route to handler
        5. Speak response (TTS)
        6. Repeat
    """

    def __init__(self, config: OrchestratorConfig | None = None) -> None:
        self.config = config or OrchestratorConfig.from_env()
        self.state = SessionState.IDLE

        # Memory system (persistent across sessions)
        self.memory = MemoryManager()

        # Initialize modules
        self.audio = AudioProcessor(AudioConfig(
            preferred_output=self.config.output_device
        ))
        self.stt = STTManager(STTConfig.from_env())
        self.tts = TTSManager(TTSConfig.from_env())
        self.llm = LLMRouter(
            mode=self.config.llm_mode,
            on_rate_limit_recovered=self._on_cloud_recovered(),
        )
        self.registry = ServiceRegistry()
        self.accessibility = AccessibilityOrchestrator()
        self.bus = get_bus()

        self._conversation: list[Message] = []
        self._running = False
        self._stop_event = asyncio.Event()

    def _on_cloud_recovered(self):
        """Callback factory passed to LLMRouter; called when rate-limit window clears."""
        async def _announce():
            await self.tts.speak(
                "Claude is available again. Switching back to cloud mode.",
                priority=2,
            )
        # Return the function itself (not a coroutine object) so it can be
        # called multiple times — one fresh coroutine per rate-limit recovery.
        return _announce

    async def start(self) -> None:
        """Initialize all services and speak startup greeting."""
        logger.info("voiceos_starting", mode=self.config.llm_mode.value)

        # Start audio output watcher (keeps Mac mini Speakers as output)
        self.audio.start_watcher()

        # Start TTS worker
        await self.tts.start()

        # Check service health
        await self.registry.start()
        health = await self.registry.health_check_all()
        logger.info("service_health", **health)

        # Check accessibility permissions
        perms = self.accessibility.check_permissions()
        if not perms.accessibility:
            logger.warning("accessibility_permission_missing")

        # Load previous session from memory
        # (Xoe-NovAi memory bank pattern — https://github.com/Xoe-NovAi/xoe-novai-foundation
        # activeContext.md → session.json for cross-session continuity)
        prior_turns = self.memory.load_recent_turns(n=6)
        if prior_turns:
            for t in prior_turns:
                self._conversation.append(
                    Message(role=t["role"], content=t["content"])
                )
            logger.info("session_resumed", prior_turns=len(prior_turns))

        # Speak greeting with active provider and memory status
        healthy_count = sum(1 for v in health.values() if v)
        total = len(health)
        mode = self.config.llm_mode
        cloud_ready = self.llm.cloud_available

        mode_label = {
            LLMMode.CLAUDE_ONLY: "Claude" if cloud_ready else "local AI (no API key set)",
            LLMMode.OLLAMA_ONLY: "local AI only",
            LLMMode.HYBRID: "hybrid" if cloud_ready else "local only",
        }[mode]

        if healthy_count == total:
            base = f"VoiceOS ready. Using {mode_label}."
        elif healthy_count > 0:
            base = f"VoiceOS ready with limited services. Using {mode_label}."
        else:
            base = "VoiceOS started but no services are running."

        if prior_turns:
            greeting = f"{base} Resuming from last session. Listening."
        else:
            greeting = f"{base} Listening."

        await self.tts.speak_and_wait(greeting, priority=2)
        await asyncio.sleep(0.3)
        self._running = True

    async def run(self) -> None:
        """
        Main voice loop. Runs until stop() is called or Ctrl+C.

        Each iteration:
          1. Capture one utterance
          2. Transcribe it
          3. Handle it
          4. Speak the response
        """
        logger.info("voice_loop_started")

        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._handle_signal)

        while self._running and not self._stop_event.is_set():
            try:
                await self._one_turn()
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error("voice_loop_error", error=str(e))
                self.state = SessionState.ERROR
                await self.tts.speak(
                    "Something went wrong. Please try again.",
                    priority=2,
                )
                await asyncio.sleep(1.0)

    async def _one_turn(self) -> None:
        """Execute one complete voice interaction turn."""
        # 1. Capture audio
        self.state = SessionState.LISTENING
        if self.config.announce_listening:
            logger.debug("listening")

        try:
            audio_bytes = await self.audio.capture_utterance()
        except Exception as e:
            logger.error("audio_capture_failed", error=str(e))
            await self.tts.speak("Microphone error. Please check your audio setup.")
            return

        # 2. Transcribe
        self.state = SessionState.PROCESSING
        if self.config.announce_processing:
            # Brief processing indicator for long transcriptions
            pass

        try:
            transcript = await self.stt.transcribe(audio_bytes)
        except STTError as e:
            await self.tts.speak(e.voice_message, priority=2)
            return

        if transcript.is_empty or not transcript.text.strip():
            logger.debug("empty_transcript_ignored")
            return

        user_text = transcript.text.strip()
        logger.info("user_said", text=user_text)

        # 3. Classify intent
        intent, nav_target = _classify_intent(user_text)
        logger.debug("intent_classified", intent=intent.value, nav_target=nav_target)

        # 4. Route to handler
        response_text = await self._handle_intent(user_text, intent, nav_target)

        # 5. Speak response and wait for playback to finish
        if response_text:
            self.state = SessionState.SPEAKING
            await self.tts.speak(response_text, priority=1)
            await self.tts.wait_until_idle()
            # Brief pause so the mic doesn't catch reverb from speakers
            await asyncio.sleep(0.3)

        # 6. Update conversation history + persist to memory bank
        provider = (
            f"anthropic:{self.llm._anthropic.config.quality_model}"
            if self.llm.mode == LLMMode.CLAUDE_ONLY and self.llm.cloud_available
            else f"ollama:{self.llm._ollama.config.default_model}"
        )
        self._conversation.append(Message(role="user", content=user_text))
        self.memory.save_turn("user", user_text, provider=provider)

        if response_text:
            self._conversation.append(Message(role="assistant", content=response_text))
            self.memory.save_turn("assistant", response_text, provider=provider)

        # Persist session state for next-boot continuity (activeContext.md pattern)
        self.memory.flush_session(self._conversation)

        # Keep in-memory history bounded
        if len(self._conversation) > self.config.max_conversation_turns * 2:
            self._conversation = self._conversation[-self.config.max_conversation_turns * 2:]

        # Periodic memory extraction (every 10 user turns — memory_bank_refresh pattern)
        asyncio.get_running_loop().create_task(
            self.memory.maybe_extract_memory(self._conversation, self.llm)
        )

        self.state = SessionState.IDLE

    async def _handle_provider_switch(self, text_lower: str) -> str | None:
        """
        Handle "switch to cloud/local/hybrid" voice commands.

        Returns a response string if a switch was performed, None otherwise.
        Persists the new mode to ~/.voiceos/config so it survives restarts.
        """
        result = _detect_provider_switch(text_lower)
        if result is None:
            return None

        new_mode, label = result
        old_mode = self.config.llm_mode

        if new_mode == old_mode:
            return f"Already in {label} mode."

        # Reload API key before switching to cloud
        if new_mode in (LLMMode.CLAUDE_ONLY, LLMMode.HYBRID):
            self.llm.reload_api_key()

        self.llm.set_mode(new_mode)
        self.config.llm_mode = new_mode

        # Persist the change so it survives restarts
        save_config_value("VOICEOS_LLM_MODE", new_mode.value)

        cloud_ready = self.llm.cloud_available
        if new_mode == LLMMode.CLAUDE_ONLY:
            if cloud_ready:
                return "Switched to cloud mode. Using Claude."
            else:
                return (
                    "Switched to cloud mode, but your API key is not set. "
                    "I'll use local Ollama as a fallback. "
                    "Run voiceos set-key to configure Claude."
                )
        elif new_mode == LLMMode.OLLAMA_ONLY:
            return "Switched to local mode. All processing is now on your Mac."
        else:
            if cloud_ready:
                return "Switched to hybrid mode. I'll use local first, then cloud as backup."
            else:
                return "Switched to hybrid mode. Local only for now — no cloud key is set."

    async def _handle_intent(
        self,
        user_text: str,
        intent: RequestType,
        nav_target: str | None,
    ) -> str:
        """
        Route intent to the appropriate handler.

        Returns:
            Response text to speak, or empty string if handled silently
        """
        text_lower = user_text.lower()

        # Voice control commands (no LLM needed)
        if any(t in text_lower for t in ["stop", "be quiet", "shut up"]):
            self.tts.interrupt()
            return ""

        if any(t in text_lower for t in ["repeat that", "say that again"]):
            if self._conversation:
                last_assistant = next(
                    (m.content for m in reversed(self._conversation) if m.role == "assistant"),
                    None,
                )
                if last_assistant:
                    return last_assistant
            return "Nothing to repeat."

        if "what can i say" in text_lower or "what can you do" in text_lower:
            return (
                "You can ask me anything, say open followed by an app name to open it, "
                "ask me to write code, say switch to cloud or switch to local to change AI, "
                "or say status to check services."
            )

        if "status" == text_lower.strip().rstrip("?.!"):
            base = self.registry.get_voice_status_message()
            if self.llm.rate_limited:
                secs = self.llm.rate_limit_seconds_remaining
                base += f" Claude rate limit clears in {_format_duration(secs)}."
            return base

        # Current mode / AI status query
        if any(p in text_lower for p in ["what mode", "which mode", "what ai", "which ai",
                                          "using cloud", "using local", "which model"]):
            mode = self.config.llm_mode
            cloud = self.llm.cloud_available
            rate_limited = self.llm.rate_limited
            if rate_limited:
                secs = self.llm.rate_limit_seconds_remaining
                return (
                    f"Claude is rate limited for {_format_duration(secs)}. "
                    "Using local Ollama as fallback right now."
                )
            if mode == LLMMode.CLAUDE_ONLY:
                return "I'm using Claude via the Anthropic API." if cloud else "I'm set to cloud mode but no API key is configured — falling back to local."
            elif mode == LLMMode.OLLAMA_ONLY:
                return f"I'm in local-only mode using {self.llm._ollama.config.default_model} on your Mac."
            else:
                return "I'm in hybrid mode — local Ollama first, Claude as fallback." if cloud else "I'm in hybrid mode using local only — no cloud key set."

        # Memory commands
        if text_lower.startswith("remember ") or text_lower.startswith("remember that "):
            fact_text = user_text.split(" ", 2)[-1].strip()
            await self.memory.maybe_extract_memory(
                self._conversation + [Message(role="user", content=fact_text)],
                self.llm,
                force=True,
            )
            return "Got it, I've saved that to memory."

        if any(p in text_lower for p in ["forget everything", "clear my memory",
                                          "wipe my memory", "forget all"]):
            self.memory.clear_long_term()
            self.memory.clear_session()
            self._conversation.clear()
            return "Memory cleared. Starting fresh."

        if any(p in text_lower for p in ["what do you remember", "what do you know about me",
                                          "show my memory", "recall memory"]):
            facts = self.memory.get_all_facts()
            if not facts:
                return "I don't have anything saved in long-term memory yet."
            items = "; ".join(f"{k}: {v}" for k, v in list(facts.items())[:6])
            return f"I remember: {items}."

        # Provider switch commands
        switch_response = await self._handle_provider_switch(text_lower)
        if switch_response is not None:
            return switch_response

        # Navigation
        if intent == RequestType.NAVIGATION and nav_target:
            result = await self.accessibility.focus_app(nav_target)
            return result

        # Everything else → LLM
        context = RequestContext(
            request_type=intent,
            max_tokens=150,
            latency_budget_ms=8000,
        )
        messages = self.llm.build_voice_messages(
            user_text,
            history=self._conversation[-6:] if self._conversation else None,
            request_type=intent,
        )

        try:
            response = await self.llm.complete(messages, context)
            return response.content
        except Exception as e:
            logger.error("llm_failed", error=str(e))
            return "I'm having trouble thinking right now. Please try again."

    async def stop(self) -> None:
        """Graceful shutdown — flush memory bank before exit."""
        self._running = False
        self._stop_event.set()

        # Persist final session state (memory bank closure protocol)
        self.memory.flush_session(self._conversation)
        logger.info("session_state_persisted", turns=len(self._conversation))

        await self.tts.speak("VoiceOS stopping. Goodbye.", priority=2)
        await asyncio.sleep(2.0)  # Let TTS finish
        await self.tts.stop()
        await self.registry.stop()
        self.audio.stop_watcher()
        logger.info("voiceos_stopped")

    def _handle_signal(self) -> None:
        """Handle SIGINT/SIGTERM for graceful shutdown."""
        logger.info("shutdown_signal_received")
        self._stop_event.set()


async def main() -> None:
    """Entry point for running VoiceOS from command line."""
    config = OrchestratorConfig.from_env()
    orchestrator = VoiceOrchestrator(config)
    await orchestrator.start()
    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())
