"""
VoiceOS persistent configuration.

Loads ~/.voiceos/config (dotenv format) into environment variables at startup.
Environment variables always take priority over the config file.

Config file format (one per line, # for comments):
    ANTHROPIC_API_KEY=sk-ant-...
    VOICEOS_LLM_MODE=claude_only
    VOICEOS_OLLAMA_MODEL=qwen2.5:32b

Use `voiceos set-key` and `voiceos use-cloud|use-local|use-hybrid`
to modify the config file without editing it manually.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

CONFIG_DIR = Path.home() / ".voiceos"
CONFIG_FILE = CONFIG_DIR / "config"


def load_config() -> None:
    """
    Load ~/.voiceos/config dotenv file into os.environ.

    Environment variables already set take priority (they override the file).
    Call this once at CLI startup before any from_env() calls.
    """
    if not CONFIG_FILE.exists():
        return

    with open(CONFIG_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            # Strip optional surrounding quotes
            value = value.strip()
            if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            # Env vars already in environment take priority
            if key not in os.environ:
                os.environ[key] = value


def save_config_value(key: str, value: str) -> None:
    """
    Persist key=value to ~/.voiceos/config.

    Creates the config directory and file if they don't exist.
    Updates existing key or appends new one.
    Sets file permissions to 0o600 (owner read/write only) since it
    may contain API keys.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            lines = f.readlines()

    key_found = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} ="):
            lines[i] = f"{key}={value}\n"
            key_found = True
            break

    if not key_found:
        lines.append(f"{key}={value}\n")

    with open(CONFIG_FILE, "w") as f:
        f.writelines(lines)

    # Restrict permissions — config may hold API keys
    CONFIG_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)


def get_config_value(key: str) -> str | None:
    """Read a value from the config file (does not check os.environ)."""
    if not CONFIG_FILE.exists():
        return None
    with open(CONFIG_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == key:
                v = v.strip()
                if len(v) >= 2 and v[0] in ('"', "'") and v[-1] == v[0]:
                    v = v[1:-1]
                return v
    return None
