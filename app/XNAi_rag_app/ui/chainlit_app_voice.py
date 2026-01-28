"""
Xoe-NovAi v0.1.0-alpha - Chainlit Voice Interface with "Hey Nova" Wake Word
=====================================================================

Enhanced voice interface with:
- "Hey Nova" wake word detection
- Redis session persistence (VoiceSessionManager)
- FAISS knowledge retrieval (VoiceFAISSClient)
- Streaming audio support
- Rate limiting and input validation
- Real-time voice-to-voice conversation

Version: v0.1.0-alpha (2026-01-10)
"""

import os
import logging
import asyncio
import io
import base64
import json
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from collections import deque
import time

# CRITICAL FIX: Import path resolution (Pattern 1)
import sys
from pathlib import Path
# Only modify sys.path in explicit developer mode to avoid masking packaging issues
if os.getenv("XOE_ALLOW_DEV_PATH", "false").lower() == "true":
    sys.path.insert(0, str(Path(__file__).parent.parent))

# Health check endpoint for Docker
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# ============================================================================
# CIRCUIT BREAKER IMPORTS (CRITICAL FIX)
# ============================================================================
from XNAi_rag_app.core.circuit_breakers import (
    registry,
    rag_api_breaker,
    redis_breaker,
    voice_processing_breaker,
    get_circuit_breaker_status,
    circuit_breaker,
    CircuitBreakerError,
    initialize_voice_circuit_breakers
)

try:
    import chainlit as cl
    from chainlit.input_widget import Select, Slider
    print("Chainlit imported successfully")
    print(f"Chainlit version: {cl.__version__}")

    # Initialize Chainlit app properly


except ImportError:
    cl = None

try:
    from XNAi_rag_app.services.voice.voice_interface import (
        VoiceInterface,
        VoiceConfig,
        STTProvider,
        TTSProvider,
        WhisperModel_,
        setup_voice_interface,
        get_voice_interface,
        WakeWordDetector,
        AudioStreamProcessor,
        VoiceRateLimiter,
        VoiceSessionManager,
        VoiceFAISSClient,
    )
    VOICE_AVAILABLE = True
except ImportError as e:
    VOICE_AVAILABLE = False
    # Use standard print if logger isn't initialized yet
    print(f"Voice interface import failed: {e}")

try:
    import numpy as np
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

os.environ["CHAINLIT_NO_TELEMETRY"] = "true"

# ============================================================================
# UNIFIED ERROR HANDLING FRAMEWORK (Same as main.py)
# ============================================================================

class ErrorCategory:
    """Standardized error categories for consistent classification."""
    VALIDATION = "validation_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    SECURITY_ERROR = "security_error"
    INTERNAL_ERROR = "internal_error"
    VOICE_ERROR = "voice_error"

# Circuit breaker status is now provided by the centralized circuit_breakers.py module

def create_standardized_error_message(
    error_code: str,
    message: str,
    details: str = None,
    recovery_suggestion: str = None
) -> str:
    """
    Create standardized error message for Chainlit UI display.

    Args:
        error_code: Error category code (e.g., "service_unavailable")
        message: User-friendly error message
        details: Technical details (debug mode only)
        recovery_suggestion: Actionable recovery guidance

    Returns:
        Formatted error message string for UI display
    """
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"

    error_msg = f"❌ **{message}**"

    if recovery_suggestion:
        error_msg += f"\n\n💡 **Suggestion:** {recovery_suggestion}"

    if debug_mode and details:
        error_msg += f"\n\n🔧 **Technical Details:** {details[:200]}..."

    return error_msg

# Global state
_voice_interface: Optional[VoiceInterface] = None
_wake_word_detector: Optional[WakeWordDetector] = None
_session_manager: Optional[VoiceSessionManager] = None
_faiss_client: Optional[VoiceFAISSClient] = None


class VoiceConversationManager:
    """Manages voice conversation state with Redis persistence support."""
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self.audio_buffer = deque(maxlen=100)
        self.is_listening = False
        self.is_speaking = False
        self.conversation_active = False
        self.wake_word_detected = False
        self.last_speech_time = 0
        self.silence_threshold = 1.5
        self.stream_processor = None

    def initialize_stream_processor(self):
        if self.stream_processor is None and AUDIO_PROCESSING_AVAILABLE:
            self.stream_processor = AudioStreamProcessor(self.config)
            logger.info("Audio stream processor initialized")

    def add_audio_chunk(self, audio_data: bytes) -> bool:
        current_time = time.time()
        self.audio_buffer.append((current_time, audio_data))

        if self.stream_processor:
            is_speech = self.stream_processor.add_chunk(audio_data)
            if is_speech and not self.is_listening:
                self.is_listening = True
                self.last_speech_time = current_time
                return True
            elif not is_speech and self.is_listening:
                if current_time - self.last_speech_time > self.silence_threshold:
                    self.is_listening = False
                    return True
            return False

        if self._detect_voice_activity(audio_data):
            self.last_speech_time = current_time
            if not self.is_listening:
                self.is_listening = True
                return True

        if self.is_listening and (current_time - self.last_speech_time) > self.silence_threshold:
            self.is_listening = False
            return True

        return False

    def _detect_voice_activity(self, audio_data: bytes) -> bool:
        if not AUDIO_PROCESSING_AVAILABLE:
            return True
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
            return rms > 500
        except Exception:
            return True

    def get_buffered_audio(self) -> bytes:
        if not self.audio_buffer:
            return b''
        audio_chunks = [chunk for _, chunk in self.audio_buffer]
        return b''.join(audio_chunks)

    def clear_buffer(self):
        self.audio_buffer.clear()
        if self.stream_processor:
            self.stream_processor.reset()

    def start_conversation(self):
        self.conversation_active = True
        self.wake_word_detected = False
        self.clear_buffer()
        self.initialize_stream_processor()
        logger.info("Voice conversation started")

    def end_conversation(self):
        self.conversation_active = False
        self.is_listening = False
        self.is_speaking = False
        self.wake_word_detected = False
        self.clear_buffer()
        logger.info("Voice conversation ended")

    def check_wake_word(self, transcription: str) -> bool:
        if not self.config.wake_word_enabled:
            return True
        if _wake_word_detector:
            detected, confidence = _wake_word_detector.detect(transcription)
            if detected:
                self.wake_word_detected = True
                logger.info(f"Wake word 'Hey Nova' detected (confidence: {confidence:.2f})")
                return True
            return False
        return True


_conversation_manager = VoiceConversationManager()


if cl:
    @cl.on_chat_start
    async def on_chat_start():
        """Initialize voice chat session with Redis session manager."""
        logger.info("Voice chat session started")
        cl.user_session.set("voice_conversation_active", False)
        cl.user_session.set("voice_enabled", False)

        # Initialize Redis session manager
        global _session_manager
        try:
            _session_manager = VoiceSessionManager(
                redis_password=os.getenv("REDIS_PASSWORD")
            )
            cl.user_session.set("session_manager", _session_manager)
            logger.info(f"Voice session manager ready: {_session_manager.session_id}")
        except Exception as e:
            logger.warning(f"Redis session manager unavailable: {e}")
            _session_manager = None

        # Initialize FAISS client for knowledge retrieval
        global _faiss_client
        try:
            _faiss_client = VoiceFAISSClient()
            cl.user_session.set("faiss_client", _faiss_client)
            stats = _faiss_client.get_index_stats()
            logger.info(f"FAISS client ready: {stats}")
        except Exception as e:
            logger.warning(f"FAISS client unavailable: {e}")
            _faiss_client = None

        # Welcome message first
        welcome_msg = """# Xoe-NovAi v0.1.0-alpha - Voice Assistant

**Voice-to-Voice Conversation Ready!**

**Features:**
- Say **"Hey Nova"** to activate
- Streaming audio with VAD
- Redis session persistence
- FAISS knowledge retrieval
- Piper ONNX TTS voice responses

**Commands:**
- "Stop voice chat" to end
- "Voice settings" to adjust"""
        
        main_message = await cl.Message(content=welcome_msg).send()

        # Define chat settings for persistent voice toggle
        await cl.ChatSettings(
            [
                cl.input_widget.Switch(id="voice_enabled", label="Voice Responses", initial=False),
                cl.input_widget.Slider(id="wake_sensitivity", label="Wake Word Sensitivity", initial=0.8, min=0.5, max=1.0, step=0.05),
            ]
        ).send()

        # Initialize voice interface and circuit breakers
        try:
            # First initialize circuit breakers for voice
            redis_host = os.getenv("REDIS_HOST", "redis")
            raw_port = os.getenv("REDIS_PORT", "6379")
            
            # Robust port parsing to handle corruption like '0MG8IH'
            try:
                # Filter only digits
                port_digits = "".join(filter(str.isdigit, str(raw_port)))
                redis_port = int(port_digits) if port_digits else 6379
            except (ValueError, TypeError):
                logger.warning(f"Invalid REDIS_PORT '{raw_port}', defaulting to 6379")
                redis_port = 6379
                
            import urllib.parse
            redis_pass = os.getenv("REDIS_PASSWORD", "")
            encoded_pass = urllib.parse.quote_plus(redis_pass)
            redis_url = f"redis://:{encoded_pass}@{redis_host}:{redis_port}/0"
            logger.info(f"Initializing voice circuit breakers with {redis_host}:{redis_port}")
            await initialize_voice_circuit_breakers(redis_url)
            
            await setup_voice_interface()
            cl.user_session.set("conversation_manager", _conversation_manager)
            global _wake_word_detector
            if VOICE_AVAILABLE:
                _wake_word_detector = WakeWordDetector(wake_word="hey nova", sensitivity=0.8)
                logger.info("Wake word detector initialized for 'Hey Nova'")
        except Exception as e:
            logger.error(f"Failed to setup voice interface: {e}")

        # ============================================================================
        # BUTLER HEALTH BRIDGE (PHASE 2: COGNITIVE INFRASTRUCTURE)
        # ============================================================================
        try:
            status_path = Path(__file__).parent.parent.parent / "data" / "infra_status.json"
            if status_path.exists():
                with open(status_path, "r") as f:
                    infra_data = json.load(f)
                
                zram = infra_data.get("services", {}).get("zram", {}).get("status", "UNKNOWN")
                cores = infra_data.get("services", {}).get("cores", {}).get("count", "??")
                
                status_md = f"🤵 **Butler Status**\n\n"
                status_md += f"- **ZRAM**: {zram}\n"
                status_md += f"- **Cores**: {cores} Threads\n"
                status_md += f"- **Last Sync**: {infra_data.get('timestamp', 'N/A')}"
                
                await cl.Text(name="System Status", content=status_md, display="side").send(for_id=main_message.id)
            else:
                await cl.Text(name="System Status", content="🤵 **Butler**: Waiting for infra sync...", display="side").send(for_id=main_message.id)
        except Exception as e:
            logger.warning(f"Failed to load Butler status: {e}")

        start_button = cl.Action(name="start_voice_chat", payload={"action": "start"}, label="Start Voice Chat")
        await cl.Message(content="Click to begin voice conversation:", actions=[start_button]).send()

        if cl:
            @cl.action_callback("start_voice_chat")
            async def start_voice_chat(action: cl.Action):
        cl.user_session.set("voice_conversation_active", True)
        cl.user_session.set("voice_enabled", True)  # Explicitly enable voice
        _conversation_manager.start_conversation()

        await cl.Message(content="""**Voice Chat Started!**

I'm listening. Say "Hey Nova" when ready.

**Status:** Listening for wake word... (Voice responses ENABLED)
        """).send()

        if cl:
            @cl.action_callback("stop_voice_chat")
            async def stop_voice_chat(action: cl.Action):
        cl.user_session.set("voice_conversation_active", False)
        cl.user_session.set("voice_enabled", False)
        _conversation_manager.end_conversation()
        
        if _session_manager:
            _session_manager.clear_session()
        
        await cl.Message(content="**Voice Chat Stopped** - Session cleared").send()

        if cl:
            @cl.action_callback("voice_settings")
            async def voice_settings(action: cl.Action):
        settings_msg = "**Voice Settings**"
        sensitivity_slider = cl.Slider(id="wake_sensitivity", label="Wake Sensitivity", initial=0.8, min=0.5, max=1.0, step=0.05)
        await cl.Message(content=settings_msg, elements=[sensitivity_slider]).send()


# ============================================================================
# CHAINLIT AUDIO INTERFACE (STREAMING)
# ============================================================================

if cl and VOICE_AVAILABLE:
    @cl.on_audio_start
    async def on_audio_start():
        """Handle browser microphone stream start."""
        try:
            logger.info("Audio stream started from browser")
            # Always ensure manager is initialized
            _conversation_manager.initialize_stream_processor()
            return True
        except Exception as e:
            logger.error(f"Error starting audio stream: {e}")
            return False

if cl and VOICE_AVAILABLE:
    @cl.on_audio_chunk
    async def on_audio_chunk(cl_chunk):
        """
        Process incoming audio chunks from browser.
        Follows 'Hey Nova' wake word detection flow with barge-in support.
        """
        if not _conversation_manager.conversation_active:
            # Drop chunks if voice conversation not explicitly started
            return

        # Add chunk to buffer and check for VAD/Speech
        # FIX: Ensure we pass cl_chunk.data (bytes) not the Chunk object
        audio_data_bytes = getattr(cl_chunk, 'data', cl_chunk) if not isinstance(cl_chunk, bytes) else cl_chunk
        
        should_process = _conversation_manager.add_audio_chunk(audio_data_bytes)
        
        # BARGE-IN LOGIC: If AI is speaking and user starts speaking, interrupt
        if _conversation_manager.is_speaking and _conversation_manager.stream_processor and _conversation_manager.stream_processor.barge_in_detected:
            if _voice_interface:
                _voice_interface.interrupt()
                logger.info("Barge-in: Interrupting AI response")
                await cl.Message(content="👂 **Interrupted - listening...**").send()
        
        # Periodic debug log (every ~50 chunks to avoid noise)
        if _conversation_manager.stats.get("total_chunks", 0) % 50 == 0:
            logger.info(f"Received audio chunk: {len(audio_data_bytes)} bytes (Total: {_conversation_manager.stats.get('total_bytes', 0)})")
        
        if should_process and not _conversation_manager.is_speaking:
            # Speech end detected, or wake word check needed
            buffered_audio = _conversation_manager.get_buffered_audio()
            
            if buffered_audio:
                # 1. Transcribe
                transcription = await process_voice_input(buffered_audio)
                
                if transcription and transcription.strip():
                    logger.info(f"Voice interface processing: '{transcription}'")
                    # 2. Check for wake word if not already 'awake'
                    if not _conversation_manager.wake_word_detected:
                        if _conversation_manager.check_wake_word(transcription):
                            # Wake word found!
                            await cl.Message(content="👂 **Listening...**").send()
                            # Strip wake word and process the rest of the message if any
                            # (Simplification: just start listening for next chunk)
                            _conversation_manager.clear_buffer()
                    else:
                        # 3. Already awake, process as AI command/query
                        _conversation_manager.is_speaking = True
                        await cl.Message(content=f"🗣️ **You said:** {transcription}").send()
                        
                        # Generate and send AI response
                        response_text = await generate_ai_response(transcription)
                        
                        # Send text
                        msg = cl.Message(content="")
                        await msg.send()
                        for word in response_text.split():
                            # Check for interrupt between tokens
                            if _voice_interface and _voice_interface.is_interrupted:
                                break
                            await msg.stream_token(word + " ")
                        await msg.update()
                        
                        # Send voice
                        if not (_voice_interface and _voice_interface.is_interrupted):
                            audio_resp = await generate_voice_response(response_text)
                            if audio_resp:
                                await cl.Audio(name="Nova", content=audio_resp, display="inline").send()
                        
                        _conversation_manager.is_speaking = False
                        _conversation_manager.clear_buffer()

if cl and VOICE_AVAILABLE:
    @cl.on_audio_end
    async def on_audio_end():
        """Handle browser microphone stream end."""
        logger.info("Audio stream ended from browser")
        _conversation_manager.clear_buffer()


async def setup_voice_interface():
    """Setup voice interface with all components."""
    global _voice_interface, _wake_word_detector
    logger.info("Setting up voice interface...")
    
    if not VOICE_AVAILABLE:
        logger.warning("Voice interface not available")
        return
    
    config = VoiceConfig(
        stt_provider=STTProvider.FASTER_WHISPER,
        tts_provider=TTSProvider.PIPER_ONNX,
        language="en",
        wake_word="hey nova",
        wake_word_enabled=True,
        wake_word_sensitivity=0.8,
        offline_mode=True,
        preload_models=True,
        stt_compute_type="int8",
    )
    
    _voice_interface = VoiceInterface(config)
    _wake_word_detector = WakeWordDetector(wake_word=config.wake_word, sensitivity=config.wake_word_sensitivity)
    
    logger.info("Voice interface initialized")


async def process_voice_input(audio_data: bytes) -> Optional[str]:
    """Process voice input with filtering for hallucinations."""
    if not VOICE_AVAILABLE or not _voice_interface:
        logger.warning("Voice interface not available for transcription")
        return None

    try:
        # 1. Transcribe
        transcription, confidence = await _voice_interface.transcribe_audio(audio_data)
        
        # 2. Filter hallucinations (Whisper filler on silence)
        filtered_text = _voice_interface.filter_hallucinations(transcription)
        
        if not filtered_text:
            return None

        logger.info(f"Turbo STT: {filtered_text[:50]}... (conf: {confidence:.1%})")

        # Save to Redis session
        if _session_manager:
            _session_manager.add_interaction("user", filtered_text, {
                "confidence": confidence,
                "model": "distil-large-v3-turbo"
            })

        return filtered_text

    except Exception as e:
        logger.error(f"Turbo STT failed: {e}")
        return None


@rag_api_breaker
async def call_rag_api_with_circuit_breaker(user_input: str, context: str = "", knowledge_context: str = "") -> Dict[str, Any]:
    """Call RAG API with circuit breaker protection and authentication."""
    import httpx
    rag_api_url = "http://rag:8000"
    
    # 1. Get token from session or login
    token = cl.user_session.get("rag_token")
    if not token:
        try:
                # Use operator-provided credentials via environment variables; do not fall back to defaults
                rag_user = os.getenv("RAG_UI_USERNAME")
                rag_password = os.getenv("RAG_UI_PASSWORD")

                if not rag_user or not rag_password:
                    logger.warning("RAG UI credentials not provided (RAG_UI_USERNAME / RAG_UI_PASSWORD); skipping UI auto-login")
                else:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        login_response = await client.post(
                            f"{rag_api_url}/auth/login",
                            json={
                                "username": rag_user,
                                "password": rag_password
                            }
                        )
                        if login_response.status_code == 200:
                            token_data = login_response.json()
                            token = token_data.get("access_token")
                            cl.user_session.set("rag_token", token)
                            logger.info("UI successfully authenticated with RAG API")
                        else:
                            logger.error(f"RAG API login failed: {login_response.status_code}")
        except Exception as e:
            logger.error(f"RAG API authentication error: {e}")

    # 2. Call query endpoint
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        response = await client.post(
            f"{rag_api_url}/query",
            headers=headers,
            json={
                "query": user_input,
                "use_rag": True,
                "voice_input": True,
                "conversation_context": context,
                "knowledge_context": knowledge_context,
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "I processed your request.")
            return {"success": True, "response": response_text}
        elif response.status_code == 401:
            # Token might be expired, clear it for next attempt
            cl.user_session.set("rag_token", None)
            raise Exception("RAG API returned 401 Unauthorized")
        else:
            raise Exception(f"RAG API returned status {response.status_code}")

async def generate_ai_response(user_input: str) -> str:
    """Generate AI response using RAG API with conversation context and circuit breaker protection."""
    try:
        # Get conversation context from Redis (with Redis circuit breaker)
        context = ""
        if _session_manager:
            try:
                context = redis_breaker(_session_manager.get_conversation_context)(max_turns=5)
            except CircuitBreakerError:
                logger.warning("Redis circuit breaker open - proceeding without conversation context")
                context = ""  # Fallback: no context

        # Get knowledge from FAISS
        knowledge_context = ""
        if _faiss_client and _faiss_client.is_available:
            try:
                results = _faiss_client.search(user_input, top_k=3)
                if isinstance(results, list) and len(results) > 0:
                    knowledge_context = "\n".join([r.get("content", "") for r in results[:2] if isinstance(r, dict)])
            except Exception as e:
                logger.warning(f"FAISS search failed: {e} - proceeding without knowledge context")

        # Call RAG API with circuit breaker protection
        try:
            result = await call_rag_api_with_circuit_breaker(user_input, context, knowledge_context)
            response_text = result["response"]

            # Save assistant response to Redis (with circuit breaker)
            if _session_manager:
                try:
                    redis_breaker(_session_manager.add_interaction)("assistant", response_text)
                except CircuitBreakerError:
                    logger.warning("Redis circuit breaker open - could not save assistant response")

            return response_text

        except CircuitBreakerError:
            # RAG API circuit breaker is open - use fallback response
            logger.warning("RAG API circuit breaker open - using fallback response")
            fallback_msg = create_standardized_error_message(
                error_code=ErrorCategory.SERVICE_UNAVAILABLE,
                message="AI service temporarily unavailable",
                recovery_suggestion="Please try again in 30 seconds. The service is automatically recovering."
            )
            return f"I'm temporarily unable to access my knowledge base. {fallback_msg}"

    except Exception as e:
        logger.error(f"AI response generation failed: {e}")
        error_msg = create_standardized_error_message(
            error_code=ErrorCategory.INTERNAL_ERROR,
            message="Unable to generate AI response",
            details=str(e),
            recovery_suggestion="Please try again. If the problem continues, contact support."
        )
        return error_msg


async def generate_voice_response(text: str) -> Optional[bytes]:
    """Generate voice response from text."""
    if not VOICE_AVAILABLE or not _voice_interface:
        return None
    
    try:
        audio_data = await _voice_interface.synthesize_speech(text=text, language="en")
        logger.info(f"Generated voice response: {len(audio_data) if audio_data else 0} bytes")
        return audio_data
    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        return None


if cl:
    @cl.on_message
    async def on_message(message: cl.Message):
    """Handle incoming messages with voice support."""
    user_query = message.content.strip()

    if user_query.startswith("/"):
        command_response = await handle_command(user_query)
        if command_response:
            await cl.Message(content=command_response).send()
        return

    msg = cl.Message(content="")
    await msg.send()

    # Check if voice is explicitly enabled via command/button/session
    voice_enabled = (
        cl.user_session.get("voice_enabled", False) or
        cl.user_session.get("voice_conversation_active", False)
    )

    try:
        response_text = await generate_ai_response(user_query)

        # Stream text response
        for word in response_text.split():
            await msg.stream_token(word + " ")
            await asyncio.sleep(0.02)

        await msg.update()

        # Only attempt voice if explicitly enabled
        if voice_enabled:
            try:
                voice_msg = cl.Message(content="🎤 Generating voice response...")
                await voice_msg.send()

                audio_data = await generate_voice_response(response_text)
                if audio_data and len(audio_data) > 0:
                    # Send audio to UI
                    await cl.Audio(
                        name="Nova",
                        content=audio_data,
                        display="inline"
                    ).send()
                    voice_msg.content = "🎤 Voice response ready."
                    await voice_msg.update()
                else:
                    voice_msg.content = "🎤 Voice generation returned no data (model may be initializing or input text invalid)."
                    await voice_msg.update()
            except Exception as e:
                logger.error(f"Voice generation failed: {e}")
                await cl.Message(content=f"❌ Voice generation failed: {e}").send()
        else:
            # Add hint for enabling voice
            hint_msg = cl.Message(content="\n\n💡 *Tip:* Use `/voice on` or click 'Start Voice Chat' for voice responses")
            await hint_msg.send()

    except Exception as e:
        logger.error(f"Message processing failed: {e}")
        error_msg = cl.Message(content=f"❌ Error processing request: {str(e)}")
        await error_msg.send()


async def handle_command(command: str) -> Optional[str]:
    """Handle slash commands."""
    command_lower = command.strip().lower()
    if command_lower == "/voice on":
        cl.user_session.set("voice_enabled", True)
        return "Voice responses enabled"
    elif command_lower == "/voice off":
        cl.user_session.set("voice_enabled", False)
        return "Voice responses disabled"
    elif command_lower == "/voice status":
        voice_enabled = cl.user_session.get("voice_enabled", True)
        session_info = ""
        if _session_manager:
            stats = _session_manager.get_stats()
            session_info = f"\nSession: {stats['session_id']}, Turns: {stats['conversation_turns']}"
        return f"Voice: {'Enabled' if voice_enabled else 'Disabled'}{session_info}"
    elif command_lower == "/voice restart":
        start_button = cl.Action(name="start_voice_chat", payload={"action": "start"}, label="Start Voice Chat")
        await cl.Message(content="Click to begin voice conversation:", actions=[start_button]).send()
        return "Voice activation button sent."
    elif command_lower == "/session clear":
        if _session_manager:
            _session_manager.clear_session()
        return "Session cleared"
    return None


if cl:
    @cl.on_settings_update
    async def on_settings_update(settings):
    """Handle settings updates."""
    if "voice_enabled" in settings:
        cl.user_session.set("voice_enabled", settings["voice_enabled"])
        status = "enabled" if settings["voice_enabled"] else "disabled"
        await cl.Message(content=f"Voice responses {status}").send()


# Health check endpoint for Docker
async def _health_check_logic():
    """Health check endpoint for Docker orchestration."""
    try:
        # Check voice interface availability
        voice_status = "available" if VOICE_AVAILABLE else "unavailable"

        # Check circuit breaker status
        circuit_status = get_circuit_breaker_status()

        # Check session manager
        session_status = "available" if _session_manager else "unavailable"

        # Check FAISS client
        faiss_status = "available" if _faiss_client and _faiss_client.is_available else "unavailable"

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "components": {
                    "voice_interface": voice_status,
                    "circuit_breakers": circuit_status,
                    "session_manager": session_status,
                    "faiss_client": faiss_status,
                    "version": "0.1.0-alpha"
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

if cl:
    @cl.on_app_startup
    def setup_chainlit_app():
        """Set up Chainlit application hooks and routes."""
        cl.app.add_api_route("/health", _health_check_logic, methods=["GET"])
    # The @cl.on_app_startup decorator handles when setup_chainlit_app is called.

if __name__ == "__main__":
    if VOICE_AVAILABLE:
        asyncio.run(setup_voice_interface())
    else:
        logger.error("Voice interface not available")
