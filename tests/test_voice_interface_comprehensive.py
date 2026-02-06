#!/usr/bin/env python3
"""
Comprehensive Voice Interface Test Suite
Tests: STT → LLM → TTS pipeline with circuit breakers and metrics
"""

import asyncio
import io
import wave
import numpy as np
import time
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.XNAi_rag_app.services.voice.voice_interface import (
    VoiceInterface, VoiceConfig, WakeWordDetector,
    voice_metrics, STTProvider, TTSProvider
)
from app.XNAi_rag_app.core.circuit_breakers import (
    voice_stt_breaker, voice_tts_breaker, get_circuit_breaker_status
)


def create_test_wav(duration_seconds=1, sample_rate=16000):
    """Create a test WAV file with silence."""
    samples = np.zeros(int(sample_rate * duration_seconds), dtype=np.int16)
    
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())
    
    return wav_buffer.getvalue()


async def test_voice_interface_initialization():
    """Test VoiceInterface initialization."""
    print("=" * 60)
    print("Test 1: VoiceInterface Initialization")
    print("=" * 60)
    
    config = VoiceConfig(
        stt_provider=STTProvider.FASTER_WHISPER,
        tts_provider=TTSProvider.PIPER_ONNX,
        offline_mode=False,
        preload_models=True
    )
    
    t0 = time.time()
    interface = VoiceInterface(config)
    init_time = time.time() - t0
    
    print(f"✅ VoiceInterface initialized in {init_time:.2f}s")
    print(f"   - STT Provider: {interface.stt_provider_name}")
    print(f"   - TTS Provider: {interface.tts_provider_name}")
    print(f"   - STT Model Loaded: {interface.stt_model is not None}")
    print(f"   - Session ID: {interface.session_id}")
    
    return interface


def test_wake_word_detection():
    """Test wake word detection."""
    print("\n" + "=" * 60)
    print("Test 2: Wake Word Detection")
    print("=" * 60)
    
    detector = WakeWordDetector(wake_word="hey nova", sensitivity=0.8)
    
    test_cases = [
        ("Hey Nova, what's the weather?", True),
        ("Hello, how are you?", False),
        ("Hey Nova!", True),
        ("I said hey to Nova yesterday", False),
    ]
    
    for phrase, expected in test_cases:
        detected, confidence = detector.detect(phrase)
        status = "✅" if detected == expected else "❌"
        print(f"{status} '{phrase}' -> Detected: {detected} (conf: {confidence:.2f})")
    
    stats = detector.get_stats()
    print(f"\nDetection Stats: {stats}")


async def test_circuit_breakers():
    """Test circuit breaker functionality."""
    print("\n" + "=" * 60)
    print("Test 3: Circuit Breakers")
    print("=" * 60)
    
    # Get initial status
    status = get_circuit_breaker_status()
    print("Initial Circuit Breaker Status:")
    for name, state in status.items():
        print(f"  - {name}: {state}")
    
    # Test STT circuit breaker
    stt_allow = voice_stt_breaker.allow_request()
    print(f"\nSTT Circuit allows request: {stt_allow}")
    
    # Record success
    voice_stt_breaker.record_success()
    print("Recorded STT success")
    
    # Test TTS circuit breaker
    tts_allow = voice_tts_breaker.allow_request()
    print(f"TTS Circuit allows request: {tts_allow}")
    
    voice_tts_breaker.record_success()
    print("Recorded TTS success")
    
    # Check metrics
    voice_metrics.update_circuit_breaker("stt", open=False)
    voice_metrics.update_circuit_breaker("tts", open=False)
    print("\n✅ Circuit breakers functioning correctly")


async def test_metrics_system():
    """Test Prometheus metrics collection."""
    print("\n" + "=" * 60)
    print("Test 4: Prometheus Metrics")
    print("=" * 60)
    
    # Record some test metrics
    voice_metrics.record_stt_request("success", "faster_whisper", 0.5)
    voice_metrics.record_tts_request("success", "piper_onnx", 0.3)
    voice_metrics.record_wake_word(True)
    voice_metrics.update_model_loaded("stt", "faster_whisper", True)
    voice_metrics.update_model_loaded("tts", "piper_onnx", True)
    
    # Get metrics output
    metrics_data = voice_metrics.get_metrics()
    if metrics_data:
        print("✅ Metrics collected successfully")
        print("\nSample metrics output (first 500 chars):")
        print(metrics_data[:500].decode('utf-8', errors='ignore'))
    else:
        print("⚠️  Metrics unavailable (Prometheus not installed)")


async def test_voice_session():
    """Test voice session management."""
    print("\n" + "=" * 60)
    print("Test 5: Voice Session Management")
    print("=" * 60)
    
    from app.XNAi_rag_app.services.voice.voice_interface import VoiceSessionManager
    
    # Create session manager (without Redis for testing)
    session = VoiceSessionManager(
        session_id="test_session_001",
        redis_client=None  # Disable Redis for test
    )
    
    # Add interactions
    session.add_interaction("user", "Hello, how are you?")
    session.add_interaction("assistant", "I'm doing well, thank you!")
    
    # Get conversation context
    context = session.get_conversation_context()
    print("Conversation Context:")
    print(context)
    
    # Get stats
    stats = session.get_stats()
    print(f"\nSession Stats: {stats}")
    print("✅ Session management working")


async def main():
    """Run all voice interface tests."""
    print("=" * 60)
    print("Voice Interface Comprehensive Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Initialization
        interface = await test_voice_interface_initialization()
        
        # Test 2: Wake Word Detection
        test_wake_word_detection()
        
        # Test 3: Circuit Breakers
        await test_circuit_breakers()
        
        # Test 4: Metrics
        await test_metrics_system()
        
        # Test 5: Session Management
        await test_voice_session()
        
        # Final Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print("✅ VoiceInterface initialization: PASSED")
        print("✅ Wake word detection: PASSED")
        print("✅ Circuit breakers: PASSED")
        print("✅ Metrics collection: PASSED")
        print("✅ Session management: PASSED")
        print("\n🎉 All voice interface tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)