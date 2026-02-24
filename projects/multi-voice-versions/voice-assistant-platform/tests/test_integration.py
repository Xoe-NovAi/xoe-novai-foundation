"""
VoiceOS Integration Tests

Tests the live system — requires services to be running:
  - Whisper STT on :2022
  - Kokoro TTS on :8880
  - Ollama on :11434

Run: uv run pytest tests/test_integration.py -v
Or:  uv run python tests/test_integration.py
"""

from __future__ import annotations

import asyncio
import sys
import time
sys.path.insert(0, ".")


async def test_service_registry() -> None:
    """All three services should be healthy."""
    from src.registry.service_registry import ServiceRegistry

    reg = ServiceRegistry()
    health = await reg.health_check_all()

    passed = all(health.values())
    for svc, ok in health.items():
        icon = "✅" if ok else "❌"
        print(f"  {icon} {svc}")

    assert passed, f"Services unavailable: {[k for k,v in health.items() if not v]}"
    print("  → Service registry: PASS")


async def test_stt_health() -> None:
    """Whisper service should respond to health check."""
    from src.stt.stt_manager import STTManager, STTConfig

    stt = STTManager(STTConfig.from_env())
    health = await stt.health_check()
    assert health["whisper_local"], "Whisper not healthy"
    print("  ✅ STT health check: PASS")


async def test_tts_health() -> None:
    """Kokoro service should respond to health check."""
    from src.tts.tts_manager import TTSManager, TTSConfig

    tts = TTSManager(TTSConfig.from_env())
    health = await tts.health_check()
    assert health["kokoro_local"], "Kokoro not healthy"
    print("  ✅ TTS health check: PASS")


async def test_tts_speaks() -> None:
    """TTS should synthesize and play audio without error."""
    from src.tts.tts_manager import TTSManager, TTSConfig

    tts = TTSManager(TTSConfig.from_env())
    await tts.start()
    start = time.monotonic()
    await tts.speak_and_wait("VoiceOS integration test.", priority=2)
    duration = time.monotonic() - start
    await tts.stop()

    assert duration < 10.0, f"TTS took too long: {duration:.1f}s"
    print(f"  ✅ TTS speaks: PASS ({duration:.1f}s)")


async def test_ollama_chat() -> None:
    """Ollama should respond to a simple chat message."""
    from src.llm.llm_router import LLMRouter, LLMMode, Message, RequestContext, RequestType

    router = LLMRouter(mode=LLMMode.OLLAMA_ONLY)
    start = time.monotonic()

    response = await router.complete(
        messages=[
            Message(role="user", content="Reply with exactly three words: test passed successfully"),
        ],
        context=RequestContext(
            max_tokens=30,
            request_type=RequestType.QUERY,
            latency_budget_ms=30000,
        ),
    )
    duration = time.monotonic() - start

    assert not response.is_empty, "Ollama returned empty response"
    assert len(response.content) > 0
    print(f"  ✅ Ollama chat: PASS ({duration:.1f}s, model={response.model})")
    print(f"     Response: {response.content[:80]}")


async def test_intent_classification() -> None:
    """Intent classifier should correctly classify common phrases."""
    from src.orchestrator import _classify_intent
    from src.llm.llm_router import RequestType

    cases = [
        ("open Terminal", RequestType.NAVIGATION, "Terminal"),
        ("open Safari", RequestType.NAVIGATION, "Safari"),
        ("write a function to sort a list", RequestType.CODE, None),
        ("what time is it", RequestType.QUERY, None),
        ("go to Xcode", RequestType.NAVIGATION, "Xcode"),
    ]

    all_pass = True
    for text, expected_type, expected_app in cases:
        intent_type, app = _classify_intent(text)
        ok = intent_type == expected_type
        if expected_app:
            ok = ok and (app is not None) and (expected_app.lower() in app.lower())
        icon = "✅" if ok else "❌"
        print(f"  {icon} '{text}' → {intent_type.value} (app={app})")
        if not ok:
            all_pass = False

    assert all_pass, "Some intent classifications failed"
    print("  → Intent classification: PASS")


async def test_voice_event_bus() -> None:
    """VoiceEventBus should queue and deliver events in priority order."""
    from src.events.voice_event_bus import VoiceEventBus, VoiceEvent

    bus = VoiceEventBus()
    received = []

    # Publish events in mixed priority order
    await bus.publish(VoiceEvent(event_type="test", message="low priority", priority=0))
    await bus.publish(VoiceEvent(event_type="test", message="high priority", priority=2))
    await bus.publish(VoiceEvent(event_type="test", message="normal priority", priority=1))

    # Drain queue
    async def drain():
        async for event in bus.subscribe():
            received.append(event.message)
            if len(received) >= 3:
                break

    await asyncio.wait_for(drain(), timeout=2.0)

    # Highest priority should come first
    assert received[0] == "high priority", f"Got: {received}"
    print("  ✅ VoiceEventBus priority ordering: PASS")


async def test_accessibility_orchestrator_imports() -> None:
    """AccessibilityOrchestrator should initialize without PyObjC if not available."""
    from src.accessibility.accessibility_orchestrator import (
        AccessibilityOrchestrator,
        PermissionChecker,
    )

    orchestrator = AccessibilityOrchestrator()
    assert orchestrator is not None

    # Permission check should not crash even without PyObjC
    perms = orchestrator.check_permissions()
    print(f"  ✅ Accessibility orchestrator init: PASS")
    print(f"     Accessibility permission: {perms.accessibility}")
    print(f"     Microphone permission: {perms.microphone}")


async def run_all_tests() -> None:
    """Run all integration tests and report results."""
    print("\n" + "=" * 60)
    print("VoiceOS Integration Tests")
    print("=" * 60)

    tests = [
        ("Service Registry", test_service_registry),
        ("STT Health", test_stt_health),
        ("TTS Health", test_tts_health),
        ("TTS Speaks", test_tts_speaks),
        ("Ollama Chat", test_ollama_chat),
        ("Intent Classification", test_intent_classification),
        ("VoiceEventBus", test_voice_event_bus),
        ("Accessibility Orchestrator", test_accessibility_orchestrator_imports),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"\n[{name}]")
        try:
            await test_fn()
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
