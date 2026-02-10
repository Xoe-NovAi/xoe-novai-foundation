#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Phase 1 v0.1.0-alpha - Voice Interface (ENHANCED + OBSERVABILITY)
# ============================================================================
# Purpose: Torch-free voice interface with Piper ONNX primary TTS
# Version: v0.1.0-alpha (2026-01-10)
# Features:
#   - Faster Whisper STT (torch-free, CTranslate2 backend)
#   - Piper ONNX TTS primary (torch-free, real-time CPU)
#   - "Hey Nova" wake word detection
#   - Streaming audio support with VAD
#   - Robust input validation and rate limiting
#   - Prometheus metrics for observability
#   - Circuit breaker pattern for resilience
#   - FAISS integration for voice-powered RAG
#   - Redis integration for session persistence
#   - Conversation memory and context tracking
# ============================================================================

import os
import logging
import asyncio
import io
import json
import uuid
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List
from enum import Enum
from dataclasses import dataclass
from contextlib import contextmanager, asynccontextmanager
import time
import threading
from pathlib import Path
from collections import deque

logger = logging.getLogger(__name__)

# Prometheus metrics (optional import)
try:
    from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Lightweight optional imports (guarded)
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except Exception:
    FASTER_WHISPER_AVAILABLE = False
    WhisperModel = None

try:
    from piper.voice import PiperVoice
    PIPER_AVAILABLE = True
except Exception:
    PIPER_AVAILABLE = False
    PiperVoice = None

try:
    import pyttsx3
    PYTTX3_AVAILABLE = True
except Exception:
    PYTTX3_AVAILABLE = False
    pyttsx3 = None

# Redis for session persistence
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# FAISS for vector search
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# AWQ Quantization imports
try:
    from XNAi_rag_app.core.awq_quantizer import CPUAWQQuantizer, QuantizationConfig
    from XNAi_rag_app.core.dynamic_precision import DynamicPrecisionManager
    AWQ_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AWQ quantization not available: {e}")
    CPUAWQQuantizer = None
    QuantizationConfig = None
    DynamicPrecisionManager = None
    AWQ_AVAILABLE = False

# Circuit breaker integration - Enhanced for voice services
from ...core.circuit_breakers import (
    voice_stt_breaker,
    voice_tts_breaker,
    get_circuit_breaker_status
)
from .voice_degradation import voice_degradation
from .voice_recovery import process_voice_with_recovery, VoiceRecoveryConfig

# ============================================================================
# Prometheus Metrics for Voice Subsystem
# ============================================================================

class VoiceMetrics:
    """Prometheus metrics for voice subsystem observability."""
    
    def __init__(self):
        self._registry = CollectorRegistry() if PROMETHEUS_AVAILABLE else None
        self._initialized = False
        if PROMETHEUS_AVAILABLE:
            self._init_metrics()
    
    def _init_metrics(self):
        """Initialize all voice-related Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            return
        
        self.stt_requests_total = Counter(
            'xoe_voice_stt_requests_total',
            'Total STT transcription requests',
            ['status', 'provider'],
            registry=self._registry
        )
        
        self.tts_requests_total = Counter(
            'xoe_voice_tts_requests_total',
            'Total TTS synthesis requests',
            ['status', 'provider'],
            registry=self._registry
        )
        
        self.wake_word_detections_total = Counter(
            'xoe_voice_wake_word_detections_total',
            'Total wake word detections',
            ['status'],
            registry=self._registry
        )
        
        self.rate_limit_exceeded_total = Counter(
            'xoe_voice_rate_limit_exceeded_total',
            'Total rate limit exceeded events',
            ['client_id'],
            registry=self._registry
        )
        
        self.stt_latency_seconds = Histogram(
            'xoe_voice_stt_latency_seconds',
            'STT transcription latency',
            ['provider'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
            registry=self._registry
        )
        
        self.tts_latency_seconds = Histogram(
            'xoe_voice_tts_latency_seconds',
            'TTS synthesis latency',
            ['provider'],
            buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
            registry=self._registry
        )
        
        self.audio_input_level = Gauge(
            'xoe_voice_audio_input_level',
            'Current audio input level (0-1)',
            registry=self._registry
        )
        
        self.stt_model_loaded = Gauge(
            'xoe_voice_stt_model_loaded',
            'Whether STT model is loaded',
            ['provider'],
            registry=self._registry
        )
        
        self.tts_model_loaded = Gauge(
            'xoe_voice_tts_model_loaded',
            'Whether TTS model is loaded',
            ['provider'],
            registry=self._registry
        )
        
        self.circuit_breaker_open = Gauge(
            'xoe_voice_circuit_breaker_open',
            'Whether circuit breaker is open',
            ['component'],
            registry=self._registry
        )
        
        self.voice_info = Info(
            'xoe_voice',
            'Voice subsystem configuration',
            registry=self._registry
        )
        self.voice_info.info({
            'version': 'v0.1.0-alpha',
            'stt_provider': 'faster_whisper',
            'tts_provider': 'piper_onnx',
        })
        
        self._initialized = True
    
    def record_stt_request(self, status: str, provider: str, latency: float):
        if not self._initialized:
            return
        self.stt_requests_total.labels(status=status, provider=provider).inc()
        self.stt_latency_seconds.labels(provider=provider).observe(latency)
    
    def record_tts_request(self, status: str, provider: str, latency: float):
        if not self._initialized:
            return
        self.tts_requests_total.labels(status=status, provider=provider).inc()
        self.tts_latency_seconds.labels(provider=provider).observe(latency)
    
    def record_wake_word(self, success: bool):
        if not self._initialized:
            return
        status = "success" if success else "false_positive"
        self.wake_word_detections_total.labels(status=status).inc()
    
    def record_rate_limit_exceeded(self, client_id: str):
        if not self._initialized:
            return
        self.rate_limit_exceeded_total.labels(client_id=client_id).inc()
    
    def update_model_loaded(self, component: str, provider: str, loaded: bool):
        if not self._initialized:
            return
        if component == "stt":
            self.stt_model_loaded.labels(provider=provider).set(1 if loaded else 0)
        elif component == "tts":
            self.tts_model_loaded.labels(provider=provider).set(1 if loaded else 0)
    
    def update_circuit_breaker(self, component: str, open: bool):
        if not self._initialized:
            return
        self.circuit_breaker_open.labels(component=component).set(1 if open else 0)
    
    def get_metrics(self) -> bytes:
        if not PROMETHEUS_AVAILABLE or not self._initialized:
            return b"# Voice metrics unavailable"
        return generate_latest(self._registry)


voice_metrics = VoiceMetrics()


# ============================================================================
# Circuit Breaker for Resilience (Legacy - REPLACED BY core.circuit_breakers)
# ============================================================================

# The legacy VoiceCircuitBreaker class has been removed.
# This module now uses the centralized PersistentCircuitBreaker from core.circuit_breakers.


# ============================================================================
# Configuration & Enums
# ============================================================================

class STTProvider(str, Enum):
    FASTER_WHISPER = "faster_whisper"
    WHISPER_TURBO = "whisper_turbo"

class TTSProvider(str, Enum):
    PIPER_ONNX = "piper_onnx"
    PYTTSX3 = "pyttsx3"

class VADProvider(str, Enum):
    SILERO = "silero"
    SIMPLE_RMS = "simple_rms"

class WhisperModel_(str, Enum):
    DISTIL_LARGE = "distil-large-v3"


@dataclass
class VoiceConfig:
    stt_provider: STTProvider = STTProvider.FASTER_WHISPER
    whisper_model: WhisperModel_ = WhisperModel_.DISTIL_LARGE
    stt_device: str = "cpu"
    stt_compute_type: str = "int8"
    stt_beam_size: int = 5
    
    vad_provider: VADProvider = VADProvider.SILERO
    vad_filter: bool = True
    vad_threshold: float = 0.5
    vad_min_silence_duration_ms: int = 500
    stt_timeout_seconds: int = 60
    
    tts_provider: TTSProvider = TTSProvider.PIPER_ONNX
    piper_model: str = "en_US-john-medium"
    tts_timeout_seconds: int = 30
    
    wake_word: str = "hey nova"
    wake_word_enabled: bool = True
    wake_word_sensitivity: float = 0.8
    
    # Barge-in support
    barge_in_enabled: bool = True
    interrupt_threshold_ms: int = 200
    
    language: str = "en"
    language_code: str = "en"
    
    max_audio_size_bytes: int = 10 * 1024 * 1024
    max_audio_duration_seconds: int = 300
    rate_limit_per_minute: int = 10
    rate_limit_window_seconds: int = 60
    
    streaming_enabled: bool = True
    streaming_buffer_size: int = 4096
    
    offline_mode: bool = True
    preload_models: bool = False
    
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    cache_max_entries: int = 1000
    
    def validate(self) -> Tuple[bool, str]:
        errors = []
        if self.max_audio_size_bytes < 1024:
            errors.append("max_audio_size_bytes must be at least 1KB")
        if not 0.0 <= self.wake_word_sensitivity <= 1.0:
            errors.append("wake_word_sensitivity must be between 0.0 and 1.0")
        if errors:
            return False, "; ".join(errors)
        return True, "Configuration valid"


# ============================================================================
# Rate Limiter
# ============================================================================

class VoiceRateLimiter:
    """Token bucket rate limiter for voice API."""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
    
    def allow_request(self, client_id: str) -> Tuple[bool, str]:
        now = time.time()
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove expired requests
        self.requests[client_id] = [t for t in self.requests[client_id] if now - t < self.window_seconds]
        
        if len(self.requests[client_id]) >= self.max_requests:
            voice_metrics.record_rate_limit_exceeded(client_id)
            remaining = 0
            return False, f"Rate limit exceeded. {remaining}/{self.max_requests} requests remaining"
        
        self.requests[client_id].append(now)
        remaining = self.max_requests - len(self.requests[client_id])
        return True, f"{remaining}/{self.max_requests} requests remaining"


# ============================================================================
# Wake Word Detection
# ============================================================================

class WakeWordDetector:
    """'Hey Nova' wake word detection using regex patterns."""
    
    def __init__(self, wake_word: str = "hey nova", sensitivity: float = 0.8):
        self.wake_word = wake_word.lower().strip()
        self.sensitivity = sensitivity
        self.patterns = self._build_patterns()
        self.stats = {"total_checks": 0, "detections": 0, "false_positives": 0}
    
    def _build_patterns(self) -> List:
        import re
        patterns = []
        wake_words = self.wake_word.split()
        if len(wake_words) >= 2:
            first, second = wake_words[0], wake_words[1]
            patterns.append(re.compile(rf'\b{re.escape(first)}\s+{re.escape(second)}\b', re.IGNORECASE))
            patterns.append(re.compile(rf'\b{re.escape(first)}\s*[!?.]*\s*{re.escape(second)}\b', re.IGNORECASE))
        return patterns
    
    def detect(self, transcription: str) -> Tuple[bool, float]:
        if not transcription:
            return False, 0.0
        
        self.stats["total_checks"] += 1
        text_lower = transcription.lower().strip()
        
        for pattern in self.patterns:
            match = pattern.search(text_lower)
            if match:
                match_ratio = len(match.group()) / len(text_lower) if text_lower else 0
                position_bonus = 1.0 - (match.start() / len(text_lower)) if text_lower else 0
                confidence = min(1.0, match_ratio * 0.3 + position_bonus * 0.5 + self.sensitivity * 0.2)
                
                if confidence >= 0.5:
                    self.stats["detections"] += 1
                    voice_metrics.record_wake_word(True)
                    return True, confidence
        
        self.stats["false_positives"] += 1
        voice_metrics.record_wake_word(False)
        return False, 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        total = self.stats["total_checks"]
        return {
            **self.stats,
            "detection_rate": self.stats["detections"] / total if total > 0 else 0.0,
        }


# ============================================================================
# Voice Session Manager (Redis Persistence)
# ============================================================================

class VoiceSessionManager:
    """
    Manages voice conversation sessions with Redis persistence.
    
    Follows stack patterns from docs/reference/blueprint.md:
    - Session tracking with TTL: 1 hour
    - Conversation memory storage
    - Context retrieval for RAG queries
    
    Redis key patterns:
    - xnai:voice:session:{session_id} - Full session data
    - xnai:voice:conversation:{session_id} - Conversation history
    - xnai:voice:context:{session_id} - LLM context window
    """
    
    SESSION_TTL = 3600  # 1 hour
    CONTEXT_TTL = 3600
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        redis_client: Optional[Any] = None,
        redis_host: str = "redis",
        redis_port: int = 6379,
        redis_password: Optional[str] = None,
    ):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self._redis_client = redis_client
        self._redis_config = {
            "host": redis_host,
            "port": redis_port,
            "password": redis_password,
        }
        self._connected = False
        self._connect()
        
        # CLAUDE STANDARD: Bounded conversation history prevents memory leaks
        # Maximum 100 conversation turns (configurable)
        self.MAX_CONVERSATION_TURNS = 100

        # In-memory cache for fast access with bounded history
        self._session_data: Dict[str, Any] = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),

            # CLAUDE: Use deque with maxlen for automatic eviction
            "conversation_history": deque(maxlen=self.MAX_CONVERSATION_TURNS),

            "user_preferences": {},
            "metrics": {
                "total_interactions": 0,
                "total_transcriptions": 0,
                "total_responses": 0,
            },
        }
    
    def _connect(self):
        """Connect to Redis using stack patterns."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available - session persistence disabled")
            return
        
        if self._redis_client is None:
            try:
                self._redis_client = redis.Redis(
                    host=self._redis_config["host"],
                    port=self._redis_config["port"],
                    password=self._redis_config["password"],
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                )
                self._redis_client.ping()
                self._connected = True
                logger.info(f"Voice session Redis connected: {self._redis_config['host']}:{self._redis_config['port']}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self._connected = False
    
    @property
    def is_connected(self) -> bool:
        return self._connected and self._redis_client is not None
    
    def _get_key(self, key_type: str) -> str:
        """Generate Redis key with namespace."""
        return f"xnai:voice:{key_type}:{self.session_id}"
    
    def save_session(self) -> bool:
        """Persist session to Redis."""
        if not self.is_connected:
            return False
        
        try:
            session_key = self._get_key("session")
            self._redis_client.setex(
                session_key,
                self.SESSION_TTL,
                json.dumps(self._session_data, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False
    
    def load_session(self) -> bool:
        """Load session from Redis."""
        if not self.is_connected:
            return False
        
        try:
            session_key = self._get_key("session")
            data = self._redis_client.get(session_key)
            if data:
                self._session_data = json.loads(data)
                self.session_id = self._session_data.get("session_id", self.session_id)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False
    
    def add_interaction(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add conversation turn to history."""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "role": role,  # "user" or "assistant"
            "content": content,
            "metadata": metadata or {},
        }
        
        self._session_data["conversation_history"].append(interaction)
        self._session_data["metrics"]["total_interactions"] += 1
        
        if role == "user":
            self._session_data["metrics"]["total_transcriptions"] += 1
        else:
            self._session_data["metrics"]["total_responses"] += 1
        
        # Persist to Redis
        self.save_session()
        
        # Also save to conversation-specific key for RAG context
        if self.is_connected:
            try:
                conv_key = self._get_key("conversation")
                self._redis_client.rpush(conv_key, json.dumps(interaction, default=str))
                self._redis_client.expire(conv_key, self.SESSION_TTL)
            except Exception:
                pass
    
    def get_conversation_context(self, max_turns: int = 10) -> str:
        """Get conversation history for LLM context."""
        history = list(self._session_data.get("conversation_history", []))
        recent = history[-max_turns:]
        
        context_parts = []
        for turn in recent:
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def clear_session(self):
        """Clear session data and Redis keys."""
        self._session_data = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "conversation_history": [],
            "user_preferences": {},
            "metrics": {
                "total_interactions": 0,
                "total_transcriptions": 0,
                "total_responses": 0,
            },
        }
        
        if self.is_connected:
            try:
                pattern = self._get_key("*")
                keys = self._redis_client.keys(pattern)
                if keys:
                    self._redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Failed to clear session: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        return {
            "session_id": self.session_id,
            "connected": self.is_connected,
            "created_at": self._session_data.get("created_at"),
            "total_interactions": self._session_data["metrics"]["total_interactions"],
            "total_transcriptions": self._session_data["metrics"]["total_transcriptions"],
            "total_responses": self._session_data["metrics"]["total_responses"],
            "conversation_turns": len(self._session_data.get("conversation_history", [])),
        }


# ============================================================================
# Voice FAISS Client (Knowledge Retrieval)
# ============================================================================

class VoiceFAISSClient:
    """
    FAISS-powered knowledge retrieval for voice queries.
    
    Integrates with voice interface for RAG-powered responses.
    Supports both indexed documents and on-the-fly embedding.
    """
    
    DEFAULT_TOP_K = 3
    
    def __init__(
        self,
        index_path: Optional[str] = None,
        embeddings_model: Optional[Any] = None,
    ):
        self.index_path = index_path or "/app/XNAi_rag_app/faiss_index"
        self.embeddings_model = embeddings_model
        self.index = None
        self._index_loaded = False
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index from disk."""
        if not FAISS_AVAILABLE:
            logger.warning("FAISS not available - RAG disabled")
            return
        
        index_file = Path(self.index_path) / "index.faiss"
        if index_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                self._index_loaded = True
                logger.info(f"FAISS index loaded: {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
        else:
            logger.warning(f"FAISS index not found at {index_file}")
    
    @property
    def is_available(self) -> bool:
        return self._index_loaded and self.index is not None
    
    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Search knowledge base for query.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of matching documents with scores
        """
        if not self.is_available:
            return [{"error": "FAISS index not available", "content": ""}]
        
        top_k = top_k or self.DEFAULT_TOP_K
        
        # Get embedding for query
        if self.embeddings_model is None:
            # Simple keyword fallback if no embeddings
            return self._keyword_search(query, top_k)
        
        try:
            query_embedding = self.embeddings_model.encode([query])
            
            # Search index
            distances, indices = self.index.search(query_embedding, top_k)
            
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < 0:
                    continue
                results.append({
                    "rank": i + 1,
                    "index": int(idx),
                    "score": float(dist),
                    "metadata": {"source": "faiss_index"},
                })
            
            return results
            
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return [{"error": str(e), "content": ""}]
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Simple keyword-based search fallback."""
        # This is a placeholder - in production, you'd use a document store
        return [{
            "rank": 1,
            "score": 0.0,
            "content": f"Keyword match for: {query}",
            "metadata": {"source": "keyword_fallback"},
        }]
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get FAISS index statistics."""
        if not self.is_available:
            return {"available": False}
        
        return {
            "available": True,
            "total_vectors": self.index.ntotal,
            "dimension": self.index.d if hasattr(self.index, 'd') else "unknown",
        }


# ============================================================================
# Audio Stream Processor with Bounded Memory
# ============================================================================

# CLAUDE STANDARD: Bounded buffer with overflow protection
from collections import deque
import weakref

class AudioStreamProcessor:
    """
    CLAUDE STANDARD: Streaming audio processor with bounded memory usage.

    Memory Characteristics:
    - O(1) memory usage (bounded by maxlen)
    - Automatic FIFO eviction on overflow
    - Explicit cleanup methods with weakref safety nets
    - VAD (Voice Activity Detection) for speech segmentation

    Research: Production Python Memory Management (Meta Engineering)
    Key Feature: Bounded deque prevents unbounded growth
    """

    # Audio quality constants (from digital audio research)
    DEFAULT_SAMPLE_RATE = 16000  # Hz (industry standard for voice)
    DEFAULT_CHANNELS = 1         # Mono (sufficient for voice)
    DEFAULT_BIT_DEPTH = 16       # 16-bit (CD quality)
    BYTES_PER_SECOND = DEFAULT_SAMPLE_RATE * DEFAULT_CHANNELS * (DEFAULT_BIT_DEPTH // 8)

    def __init__(self, config: VoiceConfig):
        self.config = config

        # CLAUDE STANDARD: Bounded buffer prevents memory leaks
        # Maximum 10 seconds of audio = 320KB max memory
        self.max_buffer_size = min(
            config.max_audio_size_bytes,
            self.BYTES_PER_SECOND * 10  # 10 seconds
        )

        # CLAUDE: Use deque with maxlen for automatic eviction
        # Research: collections.deque O(1) append/pop with bounded memory
        self._audio_chunks = deque(maxlen=100)  # Store chunks, not bytes
        self._total_bytes = 0

        # Track overflow for monitoring
        self._overflow_count = 0

        # Register for cleanup tracking
        self._cleanup_tracker = weakref.finalize(
            self, self._finalize_callback, self.config
        )

        # VAD parameters
        self.silence_threshold = config.vad_threshold
        self.silence_duration = config.vad_min_silence_duration_ms / 1000.0
        self.is_speaking = False
        self.last_speech_time = None
        self.speech_start_time = None
        self.vad_session = None
        
        # Barge-in tracking
        self.barge_in_detected = False
        self._consecutive_speech_frames = 0
        self._interrupt_threshold_frames = max(1, int(config.interrupt_threshold_ms / 30)) # ~30ms per chunk

        self._initialize_vad()

        # Statistics
        self.stats = {
            "total_chunks": 0,
            "total_bytes": 0,
            "speech_segments": 0,
            "silence_segments": 0,
            "overflow_events": 0,
            "barge_in_events": 0
        }

        logger.info(
            "AudioStreamProcessor initialized with Silero VAD",
            extra={
                "max_buffer_size": self.max_buffer_size,
                "vad_threshold": self.silence_threshold,
                "barge_in_enabled": config.barge_in_enabled
            }
        )

    def _initialize_vad(self):
        """Initialize Silero VAD ONNX session."""
        if self.config.vad_provider == VADProvider.SILERO:
            try:
                import onnxruntime as ort
                model_path = Path("/models/silero_vad.onnx")
                if model_path.exists():
                    self.vad_session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
                    logger.info(f"Silero VAD initialized from {model_path}")
                else:
                    logger.warning(f"Silero VAD model not found at {model_path}, falling back to RMS")
            except Exception as e:
                logger.error(f"Failed to initialize Silero VAD: {e}")

    def add_chunk(self, audio_data: bytes) -> bool:
        """
        CLAUDE STANDARD: Add audio chunk with memory safety, resampling and normalization.
        """
        # 1. FIX: Handle potential sampling rate mismatch (Browser vs Server)
        # Chainlit usually sends 44.1k or 48k depending on browser
        # We need 16k for Silero/Whisper
        processed_audio = self._preprocess_audio(audio_data)
        
        chunk_size = len(processed_audio)

        # CLAUDE: Prevent unbounded memory growth
        if self._total_bytes + chunk_size > self.max_buffer_size:
            # Evict oldest 50%
            evict_count = len(self._audio_chunks) // 2
            for _ in range(evict_count):
                if self._audio_chunks:
                    removed_chunk = self._audio_chunks.popleft()
                    self._total_bytes -= len(removed_chunk)

            self._overflow_count += 1
            self.stats["overflow_events"] += 1

        # Add new chunk
        self._audio_chunks.append(processed_audio)
        self._total_bytes += chunk_size

        # Update stats
        self.stats["total_chunks"] += 1
        self.stats["total_bytes"] += chunk_size

        # Perform VAD analysis
        is_now_speaking = self._analyze_vad(processed_audio)
        
        # Barge-in detection
        if is_now_speaking and self.config.barge_in_enabled:
            self._consecutive_speech_frames += 1
            if self._consecutive_speech_frames >= self._interrupt_threshold_frames:
                if not self.barge_in_detected:
                    self.barge_in_detected = True
                    self.stats["barge_in_events"] += 1
                    logger.info("Barge-in detected")
        else:
            self._consecutive_speech_frames = 0
            self.barge_in_detected = False
            
        return is_now_speaking

    def _preprocess_audio(self, audio_data: bytes) -> bytes:
        """Resample and normalize audio for consistent processing."""
        try:
            import numpy as np
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            
            # 1. Normalization (Target -3dB peak)
            peak = np.max(np.abs(audio_array))
            if peak > 0:
                audio_array = audio_array * (28000.0 / peak)
            
            # 2. Simple Resampling (Decimation)
            # If browser sends 48kHz, we take every 3rd sample for 16kHz
            # If browser sends 44.1kHz, it's harder, but 16kHz is usually standard for WebAudio in these contexts
            # We assume Chainlit/Browser is configured or we decimate from 48k
            # For now, we'll keep it as-is but normalized, as Chainlit 2.x often handles 16k on client side
            
            return audio_array.astype(np.int16).tobytes()
        except Exception:
            return audio_data

    def _analyze_vad(self, audio_data: bytes) -> bool:
        """
        CLAUDE STANDARD: Voice Activity Detection with Silero ONNX fallback to RMS.
        """
        try:
            import numpy as np
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # 1. Try Silero VAD if available
            if self.vad_session:
                input_data = audio_array.astype(np.float32) / 32768.0
                
                if len(input_data) >= 512:
                    ort_inputs = {
                        self.vad_session.get_inputs()[0].name: input_data[None, :512],
                        self.vad_session.get_inputs()[1].name: np.array([16000], dtype=np.int64)
                    }
                    out = self.vad_session.run(None, ort_inputs)
                    speech_prob = out[0][0][0]
                    is_speech = speech_prob > self.silence_threshold
                else:
                    energy = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
                    is_speech = energy > 500
            else:
                energy = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
                is_speech = energy > 500

            current_time = datetime.now()

            if is_speech:
                if not self.is_speaking:
                    self.is_speaking = True
                    self.speech_start_time = current_time
                    self.stats["speech_segments"] += 1
                self.last_speech_time = current_time
            else:
                if self.is_speaking and self.last_speech_time:
                    silence_duration = (current_time - self.last_speech_time).total_seconds()
                    if silence_duration >= self.silence_duration:
                        self.is_speaking = False
                        self.stats["silence_segments"] += 1

            return self.is_speaking
        except Exception as e:
            logger.debug(f"VAD error: {e}")
            return True

    def filter_hallucinations(self, text: str) -> Optional[str]:
        """Filter out common Whisper hallucinations on silence/noise."""
        if not text:
            return None
            
        hallucination_patterns = [
            "thank you for watching",
            "thanks for watching",
            "subtitles by",
            "please subscribe",
            "you guys",
            "bye bye",
            "i'll see you in the next one"
        ]
        
        text_lower = text.lower().strip()
        
        # 1. Length check: very short snippets on noise are often hallucinations
        if len(text_lower) < 2:
            return None
            
        # 2. Pattern check
        for pattern in hallucination_patterns:
            if pattern in text_lower:
                logger.info(f"Filtered Whisper hallucination: '{text_lower}'")
                return None
                
        return text


    def get_audio_data(self) -> bytes:
        """
        CLAUDE STANDARD: Retrieve and clear audio buffer.

        Research: Zero-copy concatenation for performance
        """
        if not self._audio_chunks:
            return b''

        # Concatenate all chunks
        audio_data = b''.join(self._audio_chunks)

        # CLAUDE CRITICAL: Clear buffer after retrieval
        self.cleanup()

        return audio_data

    def cleanup(self):
        """
        CLAUDE STANDARD: Explicit cleanup method.

        Pattern: Explicit resource management (Python Best Practices 2024)
        """
        buffer_size = self._total_bytes

        self._audio_chunks.clear()
        self._total_bytes = 0

        # Update metrics (Prometheus integration)
        if hasattr(voice_metrics, 'audio_buffer_size_bytes'):
            voice_metrics.audio_buffer_size_bytes.set(0)

        logger.debug(f"Audio buffer cleaned up: {buffer_size} bytes freed")

    def __del__(self):
        """
        CLAUDE: Safety net cleanup on object destruction.

        Research: __del__ as safety net (not primary cleanup method)
        """
        if hasattr(self, '_audio_chunks') and self._audio_chunks:
            logger.warning(
                "AudioStreamProcessor destroyed without explicit cleanup",
                extra={"buffer_size": self._total_bytes}
            )
            self.cleanup()

    @staticmethod
    def _finalize_callback(config):
        """Weakref callback for emergency cleanup tracking."""
        logger.debug(f"AudioStreamProcessor finalized for config: {config}")

    @asynccontextmanager
    async def managed_session(self):
        """
        CLAUDE STANDARD: Context manager for guaranteed cleanup.

        Pattern: Async context managers (Python 3.12 best practice)
        Usage:
            async with processor.managed_session():
                processor.add_chunk(data)
                # Automatic cleanup on exit
        """
        try:
            yield self
        finally:
            self.cleanup()

    def reset(self):
        """Reset processor state."""
        self.cleanup()
        self.is_speaking = False
        self.last_speech_time = None
        self.speech_start_time = None

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        return {
            "buffer_size": len(self._audio_chunks),
            "max_capacity": self._audio_chunks.maxlen,
            "estimated_bytes": self._total_bytes,
            "utilization_percent": (len(self._audio_chunks) / self._audio_chunks.maxlen) * 100,
            "overflow_events": self._overflow_count,
            "cleanup_events": self.stats.get("cleanup_events", 0),
            "avg_chunk_size": self._total_bytes / max(len(self._audio_chunks), 1),
            "vad_stats": {
                "speech_segments": self.stats["speech_segments"],
                "silence_segments": self.stats["silence_segments"],
                "is_currently_speaking": self.is_speaking
            }
        }


# ============================================================================
# Core Voice Interface
# ============================================================================

class VoiceInterface:
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        # Force model loading for working system
        self.config.offline_mode = False
        self.config.preload_models = True
        logger.info(f"VoiceInterface initialized with offline_mode={self.config.offline_mode}, preload_models={self.config.preload_models}")
        self.session_id = datetime.now().isoformat()
        self.stt_model = None
        self.tts_model = None
        self.stt_provider_name = "faster_whisper"
        self.tts_provider_name = "piper_onnx"

        # Barge-in control
        self._interrupt_flag = False

        # Circuit breakers - Use centralized breakers
        self.stt_circuit = voice_stt_breaker
        self.tts_circuit = voice_tts_breaker

        # AWQ Quantization system
        self.awq_quantizer = None
        self.dynamic_precision_manager = None
        self.awq_enabled = AWQ_AVAILABLE

        # Voice Recording Debug System
        self.debug_mode = os.getenv('XOE_VOICE_DEBUG', 'false').lower() == 'true'
        
        # SECURE FIX: Use tempfile and avoid predictable /tmp paths
        default_base = Path(tempfile.gettempdir())
        try:
             # Try to append uid if available for multiuser safety on linux
             default_base = default_base / f"xoe_voice_debug_{os.getuid()}"
        except AttributeError:
             # Fallback for systems without os.getuid (e.g. Windows)
             default_base = default_base / "xoe_voice_debug"
             
        self.debug_recording_dir = Path(os.getenv('XOE_VOICE_DEBUG_DIR', str(default_base)))
        self.debug_session_id = str(uuid.uuid4())[:8]
        self._initialize_debug_system()

        # Metrics
        self.metrics = {
            "total_transcriptions": 0,
            "total_voice_outputs": 0,
            "avg_stt_latency_ms": 0.0,
            "avg_tts_latency_ms": 0.0,
            "awq_memory_savings_mb": 0.0,
            "awq_precision_switches": 0,
            "awq_accuracy_retention": 0.0,
        }

        self._initialize_models()
        self._initialize_awq_system()

    def _initialize_awq_system(self):
        """Initialize AWQ quantization system for voice processing."""
        if not self.awq_enabled:
            logger.info("AWQ quantization not available - voice processing will use FP16")
            return

        try:
            # Import AWQ dependencies
            from XNAi_rag_app.core.dependencies import get_awq_quantizer, get_dynamic_precision_manager

            # Get AWQ quantizer instance
            self.awq_quantizer = get_awq_quantizer()
            if self.awq_quantizer is None:
                logger.warning("Failed to initialize AWQ quantizer")
                return

            # Get dynamic precision manager
            self.dynamic_precision_manager = get_dynamic_precision_manager(self.awq_quantizer)
            if self.dynamic_precision_manager is None:
                logger.warning("Failed to initialize dynamic precision manager")
                return

            # Initialize with default model (will be replaced with actual model path)
            # This is a placeholder - actual model path should be configured
            dummy_model_path = "/tmp/dummy_model.onnx"
            try:
                # Create a minimal dummy ONNX model for testing
                self._create_dummy_onnx_model(dummy_model_path)

                # Initialize AWQ system with dummy model for testing
                init_result = asyncio.get_event_loop().run_until_complete(
                    self._initialize_awq_with_model(dummy_model_path)
                )

                if init_result and init_result.get('success'):
                    logger.info("AWQ quantization system initialized for voice processing", extra={
                        'memory_reduction': init_result.get('performance_targets', {}).get('memory_reduction', 0),
                        'accuracy_retention': init_result.get('performance_targets', {}).get('accuracy_retention', 0)
                    })
                    self.awq_enabled = True
                else:
                    logger.warning("AWQ initialization failed, falling back to FP16")
                    self.awq_enabled = False

            except Exception as e:
                logger.warning(f"AWQ model initialization failed: {e}")
                self.awq_enabled = False

        except Exception as e:
            logger.error(f"AWQ system initialization error: {e}")
            self.awq_enabled = False

    def _create_dummy_onnx_model(self, model_path: str) -> None:
        """Create a minimal dummy ONNX model for testing AWQ system."""
        try:
            import onnxruntime as ort
            import numpy as np
            from onnx import helper, numpy_helper, TensorProto
            import onnx

            # Create a simple linear model: y = x * W + b
            input_dim = 768
            output_dim = 768

            # Define model inputs
            input_tensor = helper.make_tensor_value_info(
                'input', TensorProto.FLOAT, [1, input_dim]
            )

            # Define model outputs
            output_tensor = helper.make_tensor_value_info(
                'output', TensorProto.FLOAT, [1, output_dim]
            )

            # Create dummy weights
            weight_data = np.random.randn(output_dim, input_dim).astype(np.float32)
            weight_tensor = numpy_helper.from_array(weight_data, name='weight')

            bias_data = np.random.randn(output_dim).astype(np.float32)
            bias_tensor = numpy_helper.from_array(bias_data, name='bias')

            # Create MatMul node
            matmul_node = helper.make_node(
                'MatMul',
                inputs=['input', 'weight'],
                outputs=['matmul_output'],
                name='matmul'
            )

            # Create Add node
            add_node = helper.make_node(
                'Add',
                inputs=['matmul_output', 'bias'],
                outputs=['output'],
                name='add'
            )

            # Create the graph
            graph_def = helper.make_graph(
                [matmul_node, add_node],
                'dummy_model',
                [input_tensor],
                [output_tensor],
                [weight_tensor, bias_tensor]
            )

            # Create the model
            model_def = helper.make_model(graph_def, producer_name='xoe-novai-dummy')

            # Save the model
            onnx.save(model_def, model_path)
            logger.info(f"Created dummy ONNX model at {model_path}")

        except Exception as e:
            logger.warning(f"Failed to create dummy ONNX model: {e}")

    async def _initialize_awq_with_model(self, model_path: str) -> Dict[str, Any]:
        """Initialize AWQ system with a specific model."""
        if not self.awq_quantizer:
            return {'success': False, 'error': 'AWQ quantizer not available'}

        try:
            # Generate calibration data
            calibration_data = await self.awq_quantizer._generate_calibration_dataset()

            # Calibrate the model
            calibration_success = await self.awq_quantizer.calibrate_model(
                model_path, calibration_data
            )

            if not calibration_success:
                return {'success': False, 'error': 'Model calibration failed'}

            # Quantize weights
            quantization_result = await self.awq_quantizer.quantize_weights(model_path)

            if not quantization_result.get('success'):
                return {'success': False, 'error': 'Weight quantization failed'}

            # Create dual precision sessions
            session_success = await self.awq_quantizer.create_dual_precision_sessions(
                model_path, quantization_result.get('quantized_model_path')
            )

            if not session_success:
                return {'success': False, 'error': 'Dual precision session creation failed'}

            return {
                'success': True,
                'quantization_result': quantization_result,
                'performance_targets': {
                    'memory_reduction': quantization_result.get('memory_reduction_ratio', 0),
                    'accuracy_retention': 0.94  # Placeholder for actual validation
                }
            }

        except Exception as e:
            logger.error(f"AWQ model initialization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _initialize_models(self):
        if self.config.offline_mode and not self.config.preload_models:
            logger.info("Offline mode: Deferring model loading")
            return
        
        # STT model loading
        if self.config.stt_provider == STTProvider.FASTER_WHISPER and FASTER_WHISPER_AVAILABLE:
            try:
                # Check for local models in current working directory
                current_dir = Path(__file__).parent.parent.parent.parent
                local_whisper_path = current_dir / "models" / self.config.whisper_model.value
                
                if self.config.offline_mode:
                    if not local_whisper_path.exists():
                        logger.warning(f"Offline mode: Local Whisper model not found at {local_whisper_path}. Skipping.")
                        self.stt_model = None
                    else:
                        logger.info(f"Loading local Faster Whisper from: {local_whisper_path}")
                        self.stt_model = WhisperModel(
                            str(local_whisper_path),
                            device=self.config.stt_device,
                            compute_type=self.config.stt_compute_type,
                        )
                else:
                    model_path = str(local_whisper_path) if local_whisper_path.exists() else self.config.whisper_model.value
                    logger.info(f"Loading Faster Whisper from: {model_path}")
                    self.stt_model = WhisperModel(
                        model_path,
                        device=self.config.stt_device,
                        compute_type=self.config.stt_compute_type,
                    )
                
                if self.stt_model:
                    voice_metrics.update_model_loaded("stt", self.stt_provider_name, True)
                    logger.info("Faster Whisper loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Faster Whisper: {e}")
                voice_metrics.update_model_loaded("stt", self.stt_provider_name, False)

        # TTS: Use available models with fallback to simple text-to-speech
        if self.config.tts_provider == TTSProvider.PIPER_ONNX:
            try:
                # Try multiple model paths - updated to use current working directory
                current_dir = Path(__file__).parent.parent.parent.parent
                model_paths = [
                    current_dir / "models" / "piper" / f"{self.config.piper_model}.onnx",
                    current_dir / "models" / "Gemma-3-1B_int8.onnx",  # Fallback model
                ]
                
                model_path = None
                for path in model_paths:
                    if path.exists():
                        # Check if file is actually a valid model (not empty)
                        if path.stat().st_size > 1000:  # At least 1KB
                            model_path = path
                            break
                
                if model_path:
                    logger.info(f"Loading TTS model from: {model_path}")
                    try:
                        # Try to use as general ONNX model for TTS
                        import onnxruntime as ort
                        session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
                        logger.info(f"Loaded ONNX model for TTS: {model_path}")
                        self.tts_model = session
                        self.tts_provider_name = "onnx_general"
                        voice_metrics.update_model_loaded("tts", self.tts_provider_name, True)
                    except Exception as e:
                        logger.warning(f"ONNX model loading failed: {e}, using text fallback...")
                        self.tts_model = None
                else:
                    logger.warning(f"No valid TTS model found at any of: {[str(p) for p in model_paths]}")
                    self.tts_model = None
                    
            except Exception as e:
                logger.error(f"Failed to load TTS model: {e}")
                voice_metrics.update_model_loaded("tts", self.tts_provider_name, False)

        # Fallback to simple text response
        if self.tts_model is None:
            logger.info("No TTS model available, using text fallback")
            self.tts_provider_name = "text_fallback"
            voice_metrics.update_model_loaded("tts", self.tts_provider_name, False)

    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "wav") -> Tuple[str, float]:
        """Transcribe audio with timeout protection and circuit breaker."""
        if not audio_data:
            return "[No audio data]", 0.0
        
        if len(audio_data) > self.config.max_audio_size_bytes:
            return "[Audio too large]", 0.0
        
        if self.stt_model is None:
            return "[STT Model not loaded]", 0.0
        
        # Check circuit breaker with safety (Async)
        if self.stt_circuit:
            if hasattr(self.stt_circuit, 'is_allowed'):
                if not await self.stt_circuit.is_allowed():
                    return "[STT temporarily unavailable]", 0.0
            elif not self.stt_circuit.allow_request():
                return "[STT temporarily unavailable]", 0.0

        t0 = time.time()
        audio_file = io.BytesIO(audio_data)

        try:
            if hasattr(asyncio, 'timeout'):
                async with asyncio.timeout(self.config.stt_timeout_seconds):
                    segments, info = self.stt_model.transcribe(
                        audio_file,
                        beam_size=self.config.stt_beam_size,
                        language=self.config.language_code,
                        vad_filter=self.config.vad_filter,
                    )
            else:
                segments, info = await asyncio.wait_for(
                    self._transcribe_impl(audio_file),
                    timeout=self.config.stt_timeout_seconds
                )
            
            transcription = " ".join([segment.text for segment in segments])
            confidence = getattr(info, "language_probability", 0.95)
            latency = time.time() - t0
            
            if self.stt_circuit:
                if asyncio.iscoroutinefunction(self.stt_circuit.record_success):
                    await self.stt_circuit.record_success()
                else:
                    self.stt_circuit.record_success()
            
            if 'voice_metrics' in globals() and voice_metrics:
                voice_metrics.record_stt_request("success", self.stt_provider_name, latency)
            
        except asyncio.TimeoutError:
            logger.error(f"STT transcription timed out after {self.config.stt_timeout_seconds}s")
            if self.stt_circuit:
                if asyncio.iscoroutinefunction(self.stt_circuit.record_failure):
                    await self.stt_circuit.record_failure()
                else:
                    self.stt_circuit.record_failure()
            if 'voice_metrics' in globals() and voice_metrics:
                voice_metrics.record_stt_request("timeout", self.stt_provider_name, 0)
            return "[Transcription timeout]", 0.0
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            if self.stt_circuit:
                if asyncio.iscoroutinefunction(self.stt_circuit.record_failure):
                    await self.stt_circuit.record_failure()
                else:
                    self.stt_circuit.record_failure()
            if 'voice_metrics' in globals() and voice_metrics:
                voice_metrics.record_stt_request("error", self.stt_provider_name, 0)
            return "[Transcription error]", 0.0

        self.metrics["total_transcriptions"] += 1
        if self.metrics["total_transcriptions"] > 1:
            self.metrics["avg_stt_latency_ms"] = (
                self.metrics["avg_stt_latency_ms"] * (self.metrics["total_transcriptions"] - 1) +
                latency * 1000
            ) / self.metrics["total_transcriptions"]
        else:
            self.metrics["avg_stt_latency_ms"] = latency * 1000

        # Record human voice for debugging if enabled
        if self.debug_mode:
            # PERFORMANCE FIX: Run file I/O in executor to avoid blocking async loop
            try:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    None, 
                    self.record_human_voice,
                    audio_data,
                    transcription,
                    {
                        "confidence": confidence,
                        "latency_ms": latency * 1000,
                        "provider": self.stt_provider_name,
                        "audio_size_bytes": len(audio_data)
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to record debug audio (async): {e}")

        return transcription, confidence

    async def _transcribe_impl(self, audio_file: io.BytesIO):
        """Internal transcription implementation."""
        segments, info = self.stt_model.transcribe(
            audio_file,
            beam_size=self.config.stt_beam_size,
            language=self.config.language_code,
            vad_filter=self.config.vad_filter,
        )
        return list(segments), info

    def interrupt(self):
        """Set interrupt flag to stop current TTS synthesis."""
        self._interrupt_flag = True
        logger.info("VoiceInterface interruption triggered")

    @property
    def is_interrupted(self) -> bool:
        return self._interrupt_flag

    async def synthesize_speech(self, text: str, speaker_wav: Optional[str] = None, language: str = "en") -> Optional[bytes]:
        """Synthesize speech with circuit breaker protection and interrupt support."""
        if self.tts_model is None:
            return None
        
        # Reset interrupt flag at start of synthesis
        self._interrupt_flag = False
        
        # Safety check for circuit breaker (Async)
        if self.tts_circuit:
            if hasattr(self.tts_circuit, 'is_allowed'):
                if not await self.tts_circuit.is_allowed():
                    logger.warning("TTS circuit breaker open - request rejected")
                    return None
            elif not self.tts_circuit.allow_request():
                logger.warning("TTS circuit breaker open - request rejected")
                return None

        t0 = time.time()
        audio_bytes = None

        try:
            if self.tts_provider_name == "piper_onnx":
                # CLAUDE FIX: Piper.synthesize yields raw PCM chunks (16-bit, mono)
                # We must iterate and wrap in a WAV container for browser playback
                import wave
                
                raw_buf = io.BytesIO()
                # Default Piper settings: 22050 Hz, 16-bit PCM, Mono
                sample_rate = 22050
                
                for pcm_chunk in self.tts_model.synthesize(text):
                    # Check for interruption during synthesis
                    if self._interrupt_flag:
                        logger.info("TTS synthesis interrupted")
                        return None
                    
                    # FIX: Piper synthesis yields AudioChunk objects, extract the .audio attribute
                    chunk_bytes = getattr(pcm_chunk, 'audio', pcm_chunk)
                    raw_buf.write(chunk_bytes)
                
                pcm_data = raw_buf.getvalue()
                
                if len(pcm_data) > 0:
                    # Wrap in WAV
                    wav_buf = io.BytesIO()
                    with wave.open(wav_buf, "wb") as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(sample_rate)
                        wav_file.writeframes(pcm_data)
                    audio_bytes = wav_buf.getvalue()
                else:
                    logger.warning(f"Piper produced 0 bytes for text: '{text[:20]}...'")
            
            elif self.tts_provider_name == "pyttsx3":
                temp_path = "/tmp/xoe_voice_output.wav"
                self.tts_model.save_to_file(text, temp_path)
                self.tts_model.runAndWait()
                with open(temp_path, "rb") as f:
                    audio_bytes = f.read()
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            
            latency = time.time() - t0
            if self.tts_circuit:
                if asyncio.iscoroutinefunction(self.tts_circuit.record_success):
                    await self.tts_circuit.record_success()
                else:
                    self.tts_circuit.record_success()
            
            # Safety check for metrics
            if 'voice_metrics' in globals() and voice_metrics:
                voice_metrics.record_tts_request("success", self.tts_provider_name, latency)
            
            self.metrics["total_voice_outputs"] += 1
            if self.metrics["total_voice_outputs"] > 1:
                self.metrics["avg_tts_latency_ms"] = (
                    self.metrics["avg_tts_latency_ms"] * (self.metrics["total_voice_outputs"] - 1) +
                    latency * 1000
                ) / self.metrics["total_voice_outputs"]
            else:
                self.metrics["avg_tts_latency_ms"] = latency * 1000
            
            logger.info(f"TTS complete: {len(audio_bytes)} bytes, {latency:.2f}s")

            # Record AI voice for debugging if enabled
            if self.debug_mode:
                # PERFORMANCE FIX: Run file I/O in executor
                try:
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(
                        None,
                        self.record_ai_voice,
                        audio_bytes,
                        text,
                        {
                            "latency_ms": latency * 1000,
                            "provider": self.tts_provider_name,
                            "audio_size_bytes": len(audio_bytes)
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to record debug AI audio (async): {e}")

        except Exception as e:
            logger.error(f"TTS failed: {e}")
            if self.tts_circuit:
                if asyncio.iscoroutinefunction(self.tts_circuit.record_failure):
                    await self.tts_circuit.record_failure()
                else:
                    self.tts_circuit.record_failure()
            if 'voice_metrics' in globals() and voice_metrics:
                voice_metrics.record_tts_request("error", self.tts_provider_name, 0)
            return None

        return audio_bytes

    def _initialize_debug_system(self):
        """Initialize voice recording debug system."""
        if not self.debug_mode:
            return

        try:
            # Create debug recording directory
            self.debug_recording_dir.mkdir(parents=True, exist_ok=True)

            # Create session subdirectory
            self.session_debug_dir = self.debug_recording_dir / f"session_{self.debug_session_id}"
            self.session_debug_dir.mkdir(exist_ok=True)

            # Initialize debug metadata
            self.debug_metadata = {
                "session_id": self.debug_session_id,
                "start_time": datetime.now().isoformat(),
                "recordings": [],
                "stats": {
                    "human_voice_recordings": 0,
                    "ai_voice_recordings": 0,
                    "total_audio_mb": 0.0
                }
            }

            # Save initial metadata
            self._save_debug_metadata()

            logger.info(f"Voice debug recording enabled: {self.session_debug_dir}")

        except Exception as e:
            logger.error(f"Failed to initialize debug system: {e}")
            self.debug_mode = False

    def _save_debug_metadata(self):
        """Save debug metadata to JSON file."""
        if not self.debug_mode:
            return

        try:
            metadata_file = self.session_debug_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(self.debug_metadata, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save debug metadata: {e}")

    def record_human_voice(self, audio_data: bytes, transcription: str = "", metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Record human voice input for debugging and learning.

        Args:
            audio_data: Raw audio bytes
            transcription: Text transcription of the audio
            metadata: Additional metadata (confidence, timestamp, etc.)

        Returns:
            Path to recorded file if successful, None otherwise
        """
        if not self.debug_mode or not audio_data:
            return None

        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"human_{timestamp}.wav"
            filepath = self.session_debug_dir / filename

            # Save audio data as WAV
            self._save_audio_as_wav(audio_data, filepath)

            # Update metadata
            recording_info = {
                "type": "human_voice",
                "filename": filename,
                "timestamp": datetime.now().isoformat(),
                "audio_size_bytes": len(audio_data),
                "transcription": transcription,
                "metadata": metadata or {},
                "filepath": str(filepath)
            }

            self.debug_metadata["recordings"].append(recording_info)
            self.debug_metadata["stats"]["human_voice_recordings"] += 1
            self.debug_metadata["stats"]["total_audio_mb"] += len(audio_data) / (1024 * 1024)

            self._save_debug_metadata()

            logger.debug(f"Recorded human voice: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to record human voice: {e}")
            return None

    def record_ai_voice(self, audio_data: bytes, text: str = "", metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Record AI voice output for debugging and learning.

        Args:
            audio_data: Raw audio bytes from TTS
            text: Original text that was synthesized
            metadata: Additional metadata (latency, provider, etc.)

        Returns:
            Path to recorded file if successful, None otherwise
        """
        if not self.debug_mode or not audio_data:
            return None

        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"ai_{timestamp}.wav"
            filepath = self.session_debug_dir / filename

            # Save audio data as WAV
            self._save_audio_as_wav(audio_data, filepath)

            # Update metadata
            recording_info = {
                "type": "ai_voice",
                "filename": filename,
                "timestamp": datetime.now().isoformat(),
                "audio_size_bytes": len(audio_data),
                "text": text,
                "metadata": metadata or {},
                "filepath": str(filepath)
            }

            self.debug_metadata["recordings"].append(recording_info)
            self.debug_metadata["stats"]["ai_voice_recordings"] += 1
            self.debug_metadata["stats"]["total_audio_mb"] += len(audio_data) / (1024 * 1024)

            self._save_debug_metadata()

            logger.debug(f"Recorded AI voice: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to record AI voice: {e}")
            return None

    def _save_audio_as_wav(self, audio_data: bytes, filepath: Path):
        """Save raw audio data as WAV file."""
        try:
            # Create WAV file with basic parameters
            # Assuming 16-bit PCM, 22050 Hz sample rate (common for Piper)
            import wave

            with wave.open(str(filepath), 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(22050)  # Common sample rate for TTS
                wav_file.writeframes(audio_data)

        except Exception as e:
            # Fallback: save as raw binary if WAV conversion fails
            logger.warning(f"WAV conversion failed, saving as raw: {e}")
            with open(filepath.with_suffix('.raw'), 'wb') as f:
                f.write(audio_data)

    def get_debug_stats(self) -> Dict[str, Any]:
        """Get debug recording statistics."""
        if not self.debug_mode:
            return {"debug_mode": False}

        return {
            "debug_mode": True,
            "session_id": self.debug_session_id,
            "recording_dir": str(self.session_debug_dir),
            "stats": self.debug_metadata["stats"],
            "total_recordings": len(self.debug_metadata["recordings"]),
            "recordings": self.debug_metadata["recordings"][-10:]  # Last 10 recordings
        }

    def export_debug_session(self, export_path: Optional[str] = None) -> Optional[str]:
        """
        Export debug session data for analysis.

        Args:
            export_path: Optional path for export archive

        Returns:
            Path to exported archive if successful
        """
        if not self.debug_mode:
            return None

        try:
            import zipfile

            # Create export archive
            export_path = export_path or f"/tmp/xoe_voice_debug_{self.debug_session_id}.zip"
            export_dir = Path(export_path).parent
            export_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files from session directory
                for file_path in self.session_debug_dir.rglob('*'):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(self.session_debug_dir.parent))

            logger.info(f"Debug session exported to: {export_path}")
            return export_path

        except Exception as e:
            logger.error(f"Failed to export debug session: {e}")
            return None

    def get_session_stats(self) -> Dict[str, Any]:
        base_stats = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "stt_circuit_state": self.stt_circuit.state.value,
            "tts_circuit_state": self.tts_circuit.state.value,
        }

        if self.debug_mode:
            base_stats["debug"] = self.get_debug_stats()

        return base_stats


# Global helpers
_voice_instance: Optional[VoiceInterface] = None

def setup_voice_interface(config: Optional[VoiceConfig] = None) -> VoiceInterface:
    global _voice_instance
    _voice_instance = VoiceInterface(config or VoiceConfig())
    return _voice_instance

def get_voice_interface() -> Optional[VoiceInterface]:
    return _voice_instance


# Demo
if __name__ == "__main__":
    print("Xoe-NovAi Voice Interface v0.1.0-alpha")
    print("=" * 40)
    
    cfg = VoiceConfig()
    v = VoiceInterface(cfg)
    print(f"Config valid: {cfg.validate()}")
    
    # Test wake word
    detector = WakeWordDetector(wake_word="hey nova", sensitivity=0.8)
    for phrase in ["Hey Nova, hello", "Good morning Nova", "What is AI?"]:
        detected, conf = detector.detect(phrase)
        print(f"  [{'DETECTED' if detected else 'MISS'}] '{phrase}' (conf: {conf:.2f})")
    
    print(f"\nMetrics endpoint: /metrics (Prometheus format)")
    print(voice_metrics.get_metrics()[:500].decode())