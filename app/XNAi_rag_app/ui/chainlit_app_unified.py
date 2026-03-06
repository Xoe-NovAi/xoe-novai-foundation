#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Unified Chainlit Interface
# ============================================================================
# Purpose: Unified text + voice interface with modular components
# Version: v0.2.0 (2026-02-22)
# Features:
#   - Text chat with RAG API integration
#   - Optional voice responses (feature flag)
#   - Redis session persistence (with in-memory fallback)
#   - Qdrant + FAISS knowledge retrieval
#   - Circuit breaker protection
#   - Zero-telemetry configuration
# ============================================================================
# Architecture:
#   Uses new infrastructure layer:
#   - SessionManager (core/infrastructure/session_manager.py)
#   - KnowledgeClient (core/infrastructure/knowledge_client.py)
#   - VoiceModule (services/voice/voice_module.py)
# ============================================================================

import os
import json
import logging
import asyncio
import uuid
import re
import urllib.parse
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from subprocess import Popen, PIPE, DEVNULL
from collections import deque
from pathlib import Path
import sys

# Standardize import paths
PROJECT_ROOT = os.getenv(
    "XOE_NOVAI_ROOT", str(Path(__file__).parent.parent.parent.parent.absolute())
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURE_VOICE = os.getenv("FEATURE_VOICE", "false").lower() == "true"
FEATURE_REDIS_SESSIONS = os.getenv("FEATURE_REDIS_SESSIONS", "true").lower() == "true"
FEATURE_QDRANT = os.getenv("FEATURE_QDRANT", "true").lower() == "true"
FEATURE_LOCAL_FALLBACK = os.getenv("FEATURE_LOCAL_FALLBACK", "true").lower() == "true"

# ============================================================================
# IMPORTS
# ============================================================================

import chainlit as cl
from httpx import AsyncClient, ConnectError, TimeoutException, HTTPStatusError

# Try to import infrastructure layer
try:
    from XNAi_rag_app.core.infrastructure import (
        SessionManager,
        SessionConfig,
        KnowledgeClient,
        KnowledgeConfig,
    )

    INFRASTRUCTURE_AVAILABLE = True
except ImportError as e:
    INFRASTRUCTURE_AVAILABLE = False
    SessionManager = None
    SessionConfig = None
    KnowledgeClient = None
    KnowledgeConfig = None

# Escalation Researcher
try:
    from XNAi_rag_app.services.escalation_researcher import EscalationResearcher
    from XNAi_rag_app.core.entities.enhanced_handler import create_entity_handler
    from XNAi_rag_app.core.entities.registry import registry as entity_registry
    ESCALATION_AVAILABLE = True
except ImportError:
    ESCALATION_AVAILABLE = False
    EscalationResearcher = None
    create_entity_handler = None
    entity_registry = None

# Try to import voice module
try:
    from XNAi_rag_app.services.voice import (
        VoiceModule,
        VoiceModuleConfig,
    )

    VOICE_MODULE_AVAILABLE = True
except ImportError:
    VOICE_MODULE_AVAILABLE = False
    VoiceModule = None
    VoiceModuleConfig = None

# Try to import circuit breakers
try:
    from XNAi_rag_app.core.circuit_breakers import (
        rag_api_breaker,
        redis_breaker,
        voice_stt_breaker,
        voice_tts_breaker,
        CircuitBreakerError,
        get_circuit_breaker_status,
    )

    CIRCUIT_BREAKERS_AVAILABLE = True
except ImportError:
    CIRCUIT_BREAKERS_AVAILABLE = False
    rag_api_breaker = None
    redis_breaker = None
    CircuitBreakerError = Exception

# Try to import config and logging
try:
    from config_loader import load_config, get_config_value
    from logging_config import setup_logging, get_logger, PerformanceLogger

    CONFIG = load_config()
    setup_logging()
    logger = get_logger(__name__)
    perf_logger = PerformanceLogger(logger)
except ImportError:
    CONFIG = {"metadata": {"stack_version": "v0.2.0", "codename": "Unified"}}
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    perf_logger = None

# Try to import local LLM fallback
try:
    from dependencies import get_llm

    LOCAL_LLM_AVAILABLE = True
except ImportError:
    LOCAL_LLM_AVAILABLE = False
    get_llm = None

# ============================================================================
# CONFIGURATION
# ============================================================================

RAG_API_URL = os.getenv("RAG_API_URL", "http://rag:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT_SECONDS", 60))
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379") or "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

logger.info(f"XNAi Unified Chainlit v0.2.0 initialized")
logger.info(f"  - API: {RAG_API_URL}")
logger.info(f"  - Feature Voice: {FEATURE_VOICE}")
logger.info(f"  - Feature Redis Sessions: {FEATURE_REDIS_SESSIONS}")
logger.info(f"  - Feature Qdrant: {FEATURE_QDRANT}")
logger.info(f"  - Infrastructure: {INFRASTRUCTURE_AVAILABLE}")
logger.info(f"  - Voice Module: {VOICE_MODULE_AVAILABLE}")

# ============================================================================
# GLOBAL STATE
# ============================================================================

# Infrastructure components
_session_manager: Optional[SessionManager] = None
_knowledge_client: Optional[KnowledgeClient] = None
_voice_module: Optional[VoiceModule] = None
_escalation_researcher: Optional[EscalationResearcher] = None
_entity_handler: Any = None

# Local LLM fallback
local_llm = None

# Active curation tracking
active_curations: Dict[str, Any] = {}

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================


def init_session_state():
    """Initialize user session state."""
    if not cl.user_session.get("initialized"):
        session_id = cl.user_session.get("id", str(uuid.uuid4())[:8])

        cl.user_session.set("initialized", True)
        cl.user_session.set("session_id", session_id)
        cl.user_session.set("message_count", 0)
        cl.user_session.set("use_rag", True)
        cl.user_session.set("fallback_mode", False)
        cl.user_session.set("voice_enabled", False)
        cl.user_session.set("start_time", datetime.now())
        cl.user_session.set("last_query_time", None)
        cl.user_session.set("audio_buffer", [])

        logger.info(f"Session initialized: {session_id}")


def get_session_stats() -> Dict[str, Any]:
    """Get current session statistics."""
    start_time = cl.user_session.get("start_time", datetime.now())
    duration = (datetime.now() - start_time).total_seconds()

    return {
        "session_id": cl.user_session.get("session_id", "unknown"),
        "message_count": cl.user_session.get("message_count", 0),
        "use_rag": cl.user_session.get("use_rag", True),
        "fallback_mode": cl.user_session.get("fallback_mode", False),
        "voice_enabled": cl.user_session.get("voice_enabled", False),
        "duration_seconds": int(duration),
    }


# ============================================================================
# API INTERACTION
# ============================================================================


async def check_api_health() -> Tuple[bool, str]:
    """Check if RAG API is available."""
    try:
        async with AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{RAG_API_URL}/health")
            if response.status_code == 200:
                data = response.json()
                return True, f"API healthy: {data.get('status', 'unknown')}"
            return False, f"API returned status {response.status_code}"
    except Exception as e:
        logger.warning(f"API health check failed: {e}")
        return False, f"Cannot connect: {str(e)[:100]}"


async def stream_from_api(
    query: str,
    use_rag: bool = True,
    max_tokens: int = 512,
    context: str = "",
    knowledge_context: str = "",
):
    """Stream response from RAG API via SSE."""
    payload = {
        "query": query,
        "use_rag": use_rag,
        "max_tokens": max_tokens,
        "conversation_context": context,
        "knowledge_context": knowledge_context,
    }

    try:
        async with AsyncClient(timeout=API_TIMEOUT) as client:
            async with client.stream(
                "POST", f"{RAG_API_URL}/stream", json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            event_type = data.get("type")

                            if event_type == "token":
                                yield ("token", data.get("content", ""), {})
                            elif event_type == "sources":
                                yield (
                                    "sources",
                                    None,
                                    {"sources": data.get("sources", [])},
                                )
                            elif event_type == "done":
                                yield (
                                    "done",
                                    None,
                                    {
                                        "tokens": data.get("tokens", 0),
                                        "latency_ms": data.get("latency_ms", 0),
                                    },
                                )
                            elif event_type == "error":
                                yield (
                                    "error",
                                    None,
                                    {"error": data.get("error", "Unknown error")},
                                )
                        except json.JSONDecodeError:
                            continue

    except ConnectError as e:
        logger.error(f"Failed to connect to API: {e}")
        yield ("error", None, {"error": f"Cannot connect to RAG API"})
    except TimeoutException:
        yield ("error", None, {"error": "Request timeout"})
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield ("error", None, {"error": str(e)[:200]})


# ============================================================================
# LOCAL LLM FALLBACK
# ============================================================================


async def query_local_llm(query: str, max_tokens: int = 512) -> Optional[str]:
    """Fallback to local LLM if API unavailable."""
    global local_llm

    if not LOCAL_LLM_AVAILABLE or not FEATURE_LOCAL_FALLBACK:
        return None

    try:
        logger.info("Using local LLM fallback")
        if local_llm is None:
            local_llm = get_llm()

        prompt = f"Question: {query}\n\nAnswer:"
        response = local_llm.invoke(prompt, max_tokens=max_tokens)
        return response
    except Exception as e:
        logger.error(f"Local LLM fallback failed: {e}")
        return None


# ============================================================================
# COMMAND SYSTEM
# ============================================================================

COMMANDS = {
    "/help": "Show available commands",
    "/stats": "Display session statistics",
    "/reset": "Clear conversation history",
    "/rag on/off": "Enable/disable RAG",
    "/status": "Check API connection",
    "/voice on/off": "Enable/disable voice responses",
    "/voice status": "Show voice module status",
    "/research": "Trigger 4-level escalation research",
}


async def handle_command(command: str) -> Optional[str]:
    """Handle slash commands."""
    global _voice_module

    command_lower = command.strip().lower()
    parts = command.split()

    if command_lower == "/help":
        help_text = "**Available Commands:**\n\n"
        for cmd, desc in COMMANDS.items():
            help_text += f"`{cmd}` - {desc}\n"
        return help_text

    elif command_lower == "/stats":
        stats = get_session_stats()
        return f"""**Session Statistics:**
- **Session ID:** `{stats["session_id"]}`
- **Messages:** {stats["message_count"]}
- **RAG:** {"Enabled" if stats["use_rag"] else "Disabled"}
- **Voice:** {"Enabled" if stats["voice_enabled"] else "Disabled"}
- **Duration:** {stats["duration_seconds"]} seconds"""

    elif command_lower == "/reset":
        cl.user_session.set("message_count", 0)
        cl.user_session.set("start_time", datetime.now())
        if _session_manager:
            await _session_manager.clear_conversation()
        return "✅ Session reset"

    elif command_lower == "/rag on":
        cl.user_session.set("use_rag", True)
        return "✅ RAG enabled"

    elif command_lower == "/rag off":
        cl.user_session.set("use_rag", False)
        return "✅ RAG disabled"

    elif command_lower == "/status":
        api_healthy, api_msg = await check_api_health()
        stats = get_session_stats()

        status = f"""**Status:**
- API: {"🟢" if api_healthy else "🔴"} {api_msg}
- RAG: {"On" if stats["use_rag"] else "Off"}
- Voice: {"On" if stats["voice_enabled"] else "Off"}"""

        if _session_manager:
            status += f"\n- Session: {_session_manager.session_id}"
        if _knowledge_client:
            status += f"\n- Knowledge: Qdrant={_knowledge_client.is_qdrant_available}, FAISS={_knowledge_client.is_faiss_available}"

        return status

    elif command_lower == "/voice on":
        if not VOICE_MODULE_AVAILABLE:
            return "❌ Voice module not available"
        if _voice_module:
            _voice_module.enable()
            cl.user_session.set("voice_enabled", True)
            return "✅ Voice responses enabled"
        return "❌ Voice module not initialized"

    elif command_lower == "/voice off":
        if _voice_module:
            _voice_module.disable()
        cl.user_session.set("voice_enabled", False)
        return "✅ Voice responses disabled"

    elif command_lower == "/voice status":
        if not VOICE_MODULE_AVAILABLE:
            return "Voice module not available (import failed)"
        if _voice_module:
            status = _voice_module.get_status()
            return f"""**Voice Status:**
- Enabled: {status["enabled"]}
- Initialized: {status["initialized"]}
- Wake Word: {status["wake_word_enabled"]}
- STT: {status["stt_provider"]}
- TTS: {status["tts_provider"]}"""
        return "Voice module not initialized"

    elif command_lower.startswith("/research"):
        # This will be handled in on_message specially
        return "TRIGGER_RESEARCH"

    return None


# ============================================================================
# VOICE RESPONSE
# ============================================================================


async def generate_voice_response(text: str) -> Optional[bytes]:
    """Generate voice response from text."""
    global _voice_module

    if not _voice_module or not _voice_module.is_enabled:
        return None

    try:
        audio = await _voice_module.synthesize(text)
        return audio
    except Exception as e:
        logger.error(f"Voice synthesis failed: {e}")
        return None


# ============================================================================
# CHAINLIT HANDLERS
# ============================================================================


@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session with all available services."""
    global _session_manager, _knowledge_client, _voice_module

    # Initialize session state
    init_session_state()

    # Initialize session manager
    if INFRASTRUCTURE_AVAILABLE and FEATURE_REDIS_SESSIONS:
        try:
            redis_url = f"redis://:{urllib.parse.quote_plus(REDIS_PASSWORD)}@{REDIS_HOST}:{REDIS_PORT}/0"
            config = SessionConfig(redis_url=redis_url)
            _session_manager = SessionManager(config)
            await _session_manager.initialize()
            logger.info(f"Session manager initialized: {_session_manager.session_id}")
        except Exception as e:
            logger.warning(f"Session manager init failed: {e}")
            _session_manager = None

    # Initialize knowledge client
    if INFRASTRUCTURE_AVAILABLE and FEATURE_QDRANT:
        try:
            _knowledge_client = KnowledgeClient()
            await _knowledge_client.initialize()
            logger.info("Knowledge client initialized")
        except Exception as e:
            logger.warning(f"Knowledge client init failed: {e}")
            _knowledge_client = None

    # Initialize voice module (if feature enabled)
    if FEATURE_VOICE and VOICE_MODULE_AVAILABLE:
        try:
            config = VoiceModuleConfig(
                enabled=False,  # Start disabled, user can enable
                wake_word_enabled=True,
                offline_mode=True,
            )
            _voice_module = VoiceModule(config)
            success = await _voice_module.initialize()
            if success:
                logger.info("Voice module initialized")
            else:
                logger.warning("Voice module init failed")
                _voice_module = None
        except Exception as e:
            logger.warning(f"Voice module init failed: {e}")
            _voice_module = None

    # Initialize escalation researcher
    if ESCALATION_AVAILABLE:
        try:
            # We'll use the session_manager's redis if available
            redis_client = _session_manager.redis if _session_manager else None
            _escalation_researcher = EscalationResearcher(redis_client=redis_client)
            _entity_handler = create_entity_handler(entity_registry)
            logger.info("Escalation researcher and Entity handler initialized")
        except Exception as e:
            logger.warning(f"Escalation researcher init failed: {e}")
            _escalation_researcher = None
            _entity_handler = None

    # Check API availability
    api_healthy, api_msg = await check_api_health()
    if not api_healthy and LOCAL_LLM_AVAILABLE:
        cl.user_session.set("fallback_mode", True)

    # Build welcome message
    version = CONFIG.get("metadata", {}).get("stack_version", "v0.2.0")
    welcome = f"""# Welcome to Xoe-NovAi 🚀

**Version:** {version} - Unified Interface

**Status:**
- RAG API: {"🟢 Connected" if api_healthy else "🔴 Unavailable"}
- Voice: {"🟢 Available" if _voice_module else "⚪ Disabled"}
- Sessions: {"🟢 Redis" if _session_manager and _session_manager.is_connected else "🟡 Memory"}
- Knowledge: {"🟢 Qdrant" if _knowledge_client and _knowledge_client.is_qdrant_available else "🟡 FAISS" if _knowledge_client and _knowledge_client.is_faiss_available else "⚪ None"}

**Commands:** `/help` | `/status` | `/voice on`"""

    await cl.Message(content=welcome).send()

    # Send chat settings
    settings = [
        cl.input_widget.Switch(id="use_rag", label="Use RAG", initial=True),
    ]

    if _voice_module:
        settings.append(
            cl.input_widget.Switch(
                id="voice_enabled", label="Voice Responses", initial=False
            )
        )

    await cl.ChatSettings(settings).send()

    logger.info(f"Chat session started: {cl.user_session.get('session_id')}")


@cl.action_callback("escalate_next")
async def on_escalate_next(action):
    if _escalation_researcher:
        _escalation_researcher.interrupt(next_level=True)
        await cl.Message(content="⏩ Manual escalation to next level requested.").send()

@cl.action_callback("surgical_handoff")
async def on_surgical_handoff(action):
    specialist = json.loads(action.value)
    if _escalation_researcher:
        # Custom logic to jump to specialist model
        await cl.Message(content=f"🎯 **Surgical Handoff**: Switching to **{specialist['role']}** (Model: {specialist['model']}) for expert refinement.").send()
        # In a real impl, we'd set a specific model override in the researcher
        _escalation_researcher.interrupt(next_level=True)

async def run_escalation_research(query: str, original_msg: cl.Message):
    """Run escalation research and update UI."""
    global _escalation_researcher

    if not _escalation_researcher:
        await cl.Message(content="❌ Escalation researcher not available").send()
        return

    # Create actions
    actions = [
        cl.Action(name="escalate_next", value="next", label="⏩ Next Level"),
        cl.Action(name="escalate_cli", value="cli", label="⚡ Force CLI")
    ]

    # Initial status message
    status_msg = cl.Message(
        content="🔍 **Escalation Research Started**\n\nStarting Level 1: Tiny (150M)...",
        actions=actions
    )
    await status_msg.send()

    final_result = None
    try:
        async for result in _escalation_researcher.research_stream(query):
            final_result = result
            level = result["level"]
            model_id = result["model_id"]
            confidence = result["confidence"]
            vector = result.get("confidence_vector", {})
            dossier = result["dossier"]

            status_text = f"🔍 **Escalation Research: {model_id}**\n\n"

            # Confidence Vector Visualization
            if vector:
                v_text = " | ".join([f"{k.capitalize()}: {v:.2f}" for k, v in vector.items()])
                status_text += f"📊 **Confidence Vector:** `{v_text}`\n"

            status_text += f"**Overall Confidence:** {confidence:.2%}\n"
            status_text += f"**Answer:** {result['answer']}\n\n"

            # Specialist Handoff UI
            if "specialist_handoff" in result:
                specialist = result["specialist_handoff"]
                status_text += f"💡 **Surgical Recommendation:** The model is struggling with **{vector.get('lowest_dimension', 'one area')}**. Escalating to **{specialist['role']}** may save tokens vs. a full 8B escalation.\n"

                # Add dynamic action for the specialist
                spec_action = cl.Action(
                    name="surgical_handoff", 
                    value=json.dumps(specialist), 
                    label=f"🎯 Use {specialist['role'].replace('_', ' ').capitalize()}"
                )
                if spec_action not in actions:
                    actions.append(spec_action)
                    status_msg.actions = actions

            if level < 4:
                if confidence < 0.85:
                    next_level = level + 1
                    status_text += f"⚠️ Confidence low. Escalating to Level {next_level}...\n"
                else:
                    status_text += "✅ Target confidence reached. Finalizing dossier...\n"
            
            status_msg.content = status_text
            await status_msg.update()
            
            # Metrics Tracking (Simulation of VictoriaMetrics/Prometheus scrape)
            logger.info(f"METRIC: model={model_id} level={level} confidence={confidence} latency={result['latency_ms']}ms")

        # Final cleanup
        status_msg.content = f"✅ **Research Complete**\n\n{final_result['answer']}\n\n**Final Model:** {final_result['model_id']}\n**Final Confidence:** {final_result['confidence']:.2%}"
        status_msg.actions = []
        await status_msg.update()

    except Exception as e:
        logger.error(f"Escalation research failed: {e}")
        await cl.Message(content=f"❌ Research failed: {str(e)}").send()

async def handle_targeted_query(entity_name: str, query: str):
    """Handle follow-up queries for specific models or personas."""
    global _escalation_researcher
    
    # 1. Check Entity Registry
    from XNAi_rag_app.core.entities.registry import registry as entity_registry
    entity = entity_registry.get_entity(entity_name)
    
    if not entity.is_initialized:
        await cl.Message(content=f"⛏️  **Initializing {entity_name}...**\n\nI've summoned this expert for the first time. The Knowledge Miner is currently building its memory bank for **{entity_name}** and attached domains. One moment...").send()
        # Non-blocking wait for initial bootstrap
        for _ in range(5):
            await asyncio.sleep(1)
            if entity.is_initialized:
                break

    # 2. Get Persona-Specific Memory
    context = entity.get_relevant_context(query)
    
    # 3. Model Selection (Dynamic Handoff)
    # Check if we have history for this specific entity in the current session
    history_match = None
    if _escalation_researcher:
        for model_id, result in _escalation_researcher.history.items():
            if entity_name.lower() in model_id.lower():
                history_match = result
                break
    
    model_display = "Krikri-8B" if "authority" in entity_name.lower() or "krikri" in entity_name.lower() else "Local Stack"
    
    # Create the targeted prompt
    system_prompt = f"You are {entity_name}, an expert in your field. "
    if context:
        system_prompt += f"\n\nPAST KNOWLEDGE:\n{context}"
    if history_match:
        system_prompt += f"\n\nPREVIOUS SESSION SUMMARY:\n{history_match['answer']}"
    
    full_prompt = f"{system_prompt}\n\nUser Question: {query}\n\nExpert Response:"

    # Call the RAG API
    msg = cl.Message(content="")
    await msg.send()
    
    try:
        async with AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{RAG_API_URL}/stream",
                json={
                    "query": full_prompt,
                    "stream": True,
                    "use_rag": False, # We already injected the expert context
                }
            ) as response:
                if response.status_code == 200:
                    async for chunk in response.aiter_text():
                        # Parse SSE format if needed, but RAG API /stream returns raw text chunks usually
                        # or it might be JSON lines. Based on common patterns:
                        if chunk:
                            await msg.stream_token(chunk)
                    await msg.update()
                else:
                    await cl.Message(content=f"❌ Error from RAG API: {response.status_code}").send()
    except Exception as e:
        logger.error(f"Targeted query failed: {e}")
        await cl.Message(content=f"❌ Targeted query failed: {str(e)}").send()

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    init_session_state()

    # Update counters
    msg_count = cl.user_session.get("message_count", 0) + 1
    cl.user_session.set("message_count", msg_count)
    cl.user_session.set("last_query_time", datetime.now().isoformat())

    user_query = message.content.strip()

    # Expert Metropolis Patterns (Direct, Consult, Compare, Panel)
    if _entity_handler:
        parsed = _entity_handler.parse_query(user_query)
        if parsed:
            # Handle the parsed query (hey, ask, compare, summon panel)
            result = await _entity_handler.handle_query(parsed)
            
            if "error" not in result:
                # Custom status message for advanced patterns
                if result["type"] == "compare":
                    await cl.Message(content=f"🤝 **Expert Comparison**: {result['entity1']} vs {result['entity2']} on '{result['topic']}'").send()
                elif result["type"] == "panel":
                    await cl.Message(content=f"🏛️ **Summoning Expert Panel**: {', '.join(result['entities'])}").send()
                elif result["type"] == "cross_entity":
                    await cl.Message(content=f"🔗 **Expert Dialogue**: {result['initiator']} consulting {result['consulted']}").send()
                
                # Now handle the actual query with context injection
                # We'll use the primary entity for the targeted response
                entity_name = result.get("entity", result.get("primary_entity", result.get("initiator", result.get("entities", [""])[0])))
                await handle_targeted_query(entity_name, result.get("query", user_query))
                return

    # Handle commands
    if user_query.startswith("/"):
        response = await handle_command(user_query)
        if response == "TRIGGER_RESEARCH":
            # Extract query from /research <query>
            parts = user_query.split(None, 1)
            query = parts[1] if len(parts) > 1 else ""
            if not query:
                await cl.Message(content="Please provide a query: `/research <query>`").send()
                return
            await run_escalation_research(query, message)
            return
        elif response:
            await cl.Message(content=response).send()
        return

    # Create response message
    msg = cl.Message(content="")
    await msg.send()

    # Get session settings
    use_rag = cl.user_session.get("use_rag", True)
    voice_enabled = (
        cl.user_session.get("voice_enabled", False)
        and _voice_module
        and _voice_module.is_enabled
    )

    # Get context from session manager
    context = ""
    if _session_manager:
        try:
            context = await _session_manager.get_conversation_context(max_turns=5)
        except Exception as e:
            logger.warning(f"Failed to get context: {e}")

    # Get knowledge from knowledge client
    knowledge_context = ""
    if _knowledge_client:
        try:
            results = await _knowledge_client.search(user_query, top_k=3)
            if results:
                knowledge_context = "\n".join(
                    [r.content for r in results[:2] if r.content]
                )
        except Exception as e:
            logger.warning(f"Knowledge search failed: {e}")

    # Track timing
    start_time = datetime.now()

    try:
        response_text = ""
        sources = []

        # Stream from API
        async for event_type, content, event_metadata in stream_from_api(
            user_query,
            use_rag=use_rag,
            context=context,
            knowledge_context=knowledge_context,
        ):
            if event_type == "token":
                response_text += content
                await msg.stream_token(content)
            elif event_type == "sources":
                sources = event_metadata.get("sources", [])
            elif event_type == "done":
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                logger.info(f"Stream complete: {duration_ms:.0f}ms")
            elif event_type == "error":
                error_msg = event_metadata.get("error", "Unknown error")

                # Try local fallback
                if FEATURE_LOCAL_FALLBACK and LOCAL_LLM_AVAILABLE:
                    await msg.stream_token("\n\n_Using local fallback..._\n\n")
                    fallback = await query_local_llm(user_query)
                    if fallback:
                        await msg.stream_token(fallback)
                        response_text = fallback
                        cl.user_session.set("fallback_mode", True)
                    else:
                        await msg.stream_token(f"\n\n❌ Error: {error_msg}")
                else:
                    await msg.stream_token(f"\n\n❌ Error: {error_msg}")

                await msg.update()
                return

        await msg.update()

        # Save to session
        if _session_manager:
            await _session_manager.add_interaction("user", user_query)
            await _session_manager.add_interaction("assistant", response_text)

        # Show sources if RAG was used
        if use_rag and sources:
            sources_text = "\n\n**Sources:**\n"
            for i, source in enumerate(sources[:5], 1):
                sources_text += f"{i}. `{source}`\n"
            await cl.Message(content=sources_text).send()

        # Voice response (if enabled)
        if voice_enabled and response_text:
            try:
                audio = await generate_voice_response(response_text)
                if audio:
                    await cl.Audio(name="Nova", content=audio).send()
            except Exception as e:
                logger.warning(f"Voice response failed: {e}")

        logger.info(f"Message processed: {msg_count} total")

    except Exception as e:
        logger.error(f"Message processing failed: {e}")
        await msg.stream_token(f"\n\n❌ Error: {str(e)[:200]}")
        await msg.update()


# ============================================================================
# VOICE AUDIO HANDLERS (Conditional Registration)
# ============================================================================

if cl and VOICE_MODULE_AVAILABLE:

    @cl.on_audio_start
    async def on_audio_start():
        """Handle audio stream start."""
        if not _voice_module or not _voice_module.is_enabled:
            return False

        cl.user_session.set("audio_buffer", [])
        logger.info("Audio stream started")
        return True

    @cl.on_audio_chunk
    async def on_audio_chunk(chunk):
        """Handle audio chunk from browser."""
        if not _voice_module or not _voice_module.is_enabled:
            return

        # Get audio data
        audio_data = (
            getattr(chunk, "data", chunk) if not isinstance(chunk, bytes) else chunk
        )

        # Add to buffer
        buffer = cl.user_session.get("audio_buffer", [])
        buffer.append(audio_data)
        cl.user_session.set("audio_buffer", buffer)

        # Log periodically
        if len(buffer) % 50 == 0:
            logger.debug(f"Audio chunks: {len(buffer)}")

    @cl.on_audio_end
    async def on_audio_end():
        """Handle audio stream end - process buffered audio."""
        if not _voice_module or not _voice_module.is_enabled:
            return

        buffer = cl.user_session.get("audio_buffer", [])
        if not buffer:
            return

        try:
            # Combine chunks
            audio_data = b"".join(buffer)

            # Transcribe
            transcription, confidence = await _voice_module.transcribe(audio_data)

            if transcription and transcription.strip():
                # Check wake word
                detected, _ = _voice_module.check_wake_word(transcription)

                if detected:
                    await cl.Message(content=f"🗣️ **You said:** {transcription}").send()
                    # Process as message
                    await on_message(cl.Message(content=transcription))
                else:
                    await cl.Message(
                        content=f"🔇 Wake word not detected. Say 'Hey Nova' first."
                    ).send()

        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
        finally:
            cl.user_session.set("audio_buffer", [])


# ============================================================================
# SETTINGS UPDATE
# ============================================================================


@cl.on_settings_update
async def on_settings_update(settings: Dict[str, Any]):
    """Handle settings updates."""
    global _voice_module

    if "use_rag" in settings:
        cl.user_session.set("use_rag", settings["use_rag"])
        status = "enabled" if settings["use_rag"] else "disabled"
        await cl.Message(content=f"✓ RAG {status}").send()

    if "voice_enabled" in settings:
        voice_on = settings["voice_enabled"]
        cl.user_session.set("voice_enabled", voice_on)

        if _voice_module:
            if voice_on:
                _voice_module.enable()
            else:
                _voice_module.disable()

        status = "enabled" if voice_on else "disabled"
        await cl.Message(content=f"✓ Voice responses {status}").send()


# ============================================================================
# SESSION END
# ============================================================================


@cl.on_chat_end
async def on_chat_end():
    """Handle chat session end."""
    stats = get_session_stats()
    logger.info(f"Chat ended: {stats['session_id']}, {stats['message_count']} messages")


@cl.on_stop
async def on_stop():
    """Handle stop button."""
    logger.info("Generation stopped by user")


@cl.on_chat_resume
async def on_chat_resume():
    """Handle chat resume."""
    init_session_state()
    await cl.Message(content="🔄 Session resumed").send()


# ============================================================================
# HEALTH CHECK
# ============================================================================


async def health_check():
    """Health check for Docker."""
    return {
        "status": "healthy",
        "version": "0.2.0",
        "features": {
            "voice": FEATURE_VOICE and VOICE_MODULE_AVAILABLE,
            "redis_sessions": _session_manager is not None
            and _session_manager.is_connected,
            "qdrant": _knowledge_client is not None
            and _knowledge_client.is_qdrant_available,
        },
    }


# @cl.on_app_startup
# def setup_app():
#     """Setup Chainlit app routes."""
#     cl.app.add_api_route("/health", health_check, methods=["GET"])


# ============================================================================
# ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    import subprocess

    port = os.getenv("CHAINLIT_PORT", "8001")
    host = os.getenv("CHAINLIT_HOST", "0.0.0.0")

    subprocess.run(
        [
            "chainlit",
            "run",
            "chainlit_app_unified.py",
            "--host",
            host,
            "--port",
            port,
            "--headless",
        ]
    )
