#!/usr/bin/env python3
"""Dependency-free smoke test for voice_codex_cli.

This stubs audio/ML modules so we can validate command routing logic without
installing faster-whisper/kokoro.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "voice_codex_cli.py"


def install_fake_modules() -> None:
    np_mod = types.ModuleType("numpy")
    np_mod.float32 = float
    np_mod.int16 = int
    np_mod.ndarray = object
    np_mod.array = lambda *args, **kwargs: []
    np_mod.frombuffer = lambda *args, **kwargs: []
    np_mod.clip = lambda arr, _low, _high: arr
    np_mod.asarray = lambda arr, dtype=None: arr
    sys.modules["numpy"] = np_mod

    class DummyRawInputStream:
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            return None

        def stop(self):
            return None

        def close(self):
            return None

    sd_mod = types.ModuleType("sounddevice")
    sd_mod.RawInputStream = DummyRawInputStream
    sd_mod.play = lambda *args, **kwargs: None
    sys.modules["sounddevice"] = sd_mod

    class DummyVad:
        def __init__(self, *args, **kwargs):
            pass

        def is_speech(self, _frame, _rate):
            return True

    vad_mod = types.ModuleType("webrtcvad")
    vad_mod.Vad = DummyVad
    sys.modules["webrtcvad"] = vad_mod

    class DummyWhisperModel:
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, *args, **kwargs):
            segment = types.SimpleNamespace(text="dummy")
            return [segment], {}

    fw_mod = types.ModuleType("faster_whisper")
    fw_mod.WhisperModel = DummyWhisperModel
    sys.modules["faster_whisper"] = fw_mod

    class DummyPipeline:
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            return []

    kokoro_mod = types.ModuleType("kokoro")
    kokoro_mod.KPipeline = DummyPipeline
    sys.modules["kokoro"] = kokoro_mod


def load_target_module():
    spec = importlib.util.spec_from_file_location("voice_codex_cli", TARGET)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {TARGET}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["voice_codex_cli"] = module
    spec.loader.exec_module(module)
    return module


class FakeProcess:
    def __init__(self):
        self._done = False

    def poll(self):
        return 0 if self._done else None

    def terminate(self):
        self._done = True

    def wait(self, timeout=None):
        self._done = True

    def kill(self):
        self._done = True


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_smoke_test() -> None:
    install_fake_modules()
    vc = load_target_module()

    cfg = vc.Config(require_wake_word=True, wake_word="hey codex")
    controller = vc.VoiceCodexController(cfg=cfg, cwd=ROOT)

    controller._run_codex = lambda prompt, confirmed=False: f"MOCK_CODEX:{prompt}"
    controller._run_shell = lambda command, confirmed=False: f"MOCK_SHELL:{command}"

    reply, _ = controller._handle_utterance("hello there")
    assert_true(reply == "", "Non-wake utterance should be ignored")

    reply, _ = controller._handle_utterance("hey codex help")
    assert_true("Available commands" in reply, "Wake-word help routing failed")

    reply, _ = controller._handle_utterance("hey codex fix failing tests")
    assert_true(
        reply == "MOCK_CODEX:fix failing tests",
        "Wake-word Codex fallback routing failed",
    )

    reply, _ = controller._handle_utterance("hey codex run shell echo hi")
    assert_true(reply == "MOCK_SHELL:echo hi", "Wake-word shell routing failed")

    running = vc.RunningTask(
        kind="codex",
        description="long task",
        process=FakeProcess(),
    )
    controller.current_task = running

    reply, _ = controller._handle_utterance("hey codex stop running task")
    assert_true(reply == "Stopping running codex task.", "Stop command did not trigger")
    assert_true(running.stop_requested, "Stop command should set stop_requested")

    reply, _ = controller._handle_utterance("hey codex task status")
    assert_true("Running codex task:" in reply, "Task status should report running task")

    controller.current_task = None
    reply, _ = controller._handle_utterance("hey codex task status")
    assert_true(reply == "No task is currently running.", "Idle task status incorrect")

    print("Smoke test passed: wake-word and stop-task flows are working.")


if __name__ == "__main__":
    run_smoke_test()
