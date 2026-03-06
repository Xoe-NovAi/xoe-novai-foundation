"""
VoiceOS CLI — Command-line interface for managing VoiceOS.

Commands:
  voiceos start              Start the voice loop
  voiceos start --mode X     Start with specific LLM mode
  voiceos status             Check all service health
  voiceos check-permissions  Verify macOS permissions
  voiceos config             Show current configuration
  voiceos set-key <key>      Save Anthropic API key to ~/.voiceos/config
  voiceos use-cloud          Switch to Claude (claude_only mode), persists setting
  voiceos use-local          Switch to Ollama only (ollama_only mode), persists setting
  voiceos use-hybrid         Switch to hybrid mode (Ollama first, Claude fallback)
"""

from __future__ import annotations

import asyncio
import os
import sys

try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False
    print("Install click: pip install click", file=sys.stderr)
    sys.exit(1)

import structlog

# Load ~/.voiceos/config into environment BEFORE any from_env() calls
from .config import load_config, save_config_value, CONFIG_FILE
load_config()

logger = structlog.get_logger(__name__)


@click.group()
def main() -> None:
    """VoiceOS — Voice-first AI platform for developers."""
    pass


@main.command()
@click.option(
    "--mode",
    type=click.Choice(["ollama_only", "hybrid", "claude_only"]),
    default=None,
    help="LLM routing mode (overrides saved config for this session)",
)
@click.option(
    "--output-device",
    default="Mac mini Speakers",
    help="Audio output device name",
)
def start(mode: str | None, output_device: str) -> None:
    """Start the VoiceOS voice loop."""
    # If no --mode flag given, use saved config (already loaded into env)
    effective_mode = mode or os.getenv("VOICEOS_LLM_MODE", "hybrid")
    os.environ["VOICEOS_LLM_MODE"] = effective_mode
    os.environ["VOICEOS_OUTPUT_DEVICE"] = output_device

    api_key_status = "configured" if os.getenv("ANTHROPIC_API_KEY") else "not set"
    click.echo(f"Starting VoiceOS in {effective_mode} mode...")
    click.echo(f"Audio output: {output_device}")
    click.echo(f"Anthropic API key: {api_key_status}")

    if effective_mode == "claude_only" and not os.getenv("ANTHROPIC_API_KEY"):
        click.echo(
            click.style(
                "\nWarning: claude_only mode selected but ANTHROPIC_API_KEY is not set.\n"
                "VoiceOS will fall back to local Ollama automatically.\n"
                "Run:  voiceos set-key <your-key>  to configure Claude access.",
                fg="yellow",
            )
        )

    click.echo("Press Ctrl+C to stop.\n")

    from .orchestrator import VoiceOrchestrator, OrchestratorConfig
    config = OrchestratorConfig.from_env()
    orchestrator = VoiceOrchestrator(config)

    async def run() -> None:
        await orchestrator.start()
        await orchestrator.run()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        click.echo("\nStopping VoiceOS...")


@main.command("set-key")
@click.argument("api_key")
def set_key(api_key: str) -> None:
    """Save your Anthropic API key to ~/.voiceos/config.

    VoiceOS defaults to Claude (cloud) mode. Get your API key at:
      https://console.anthropic.com/settings/keys

    Note: This is a standard Anthropic API key (sk-ant-...), not the OAuth
    token used internally by Claude Code CLI. Both use the same account;
    API keys are the correct credential for programmatic access.

    Example:
        voiceos set-key sk-ant-api03-...

    The key is stored in ~/.voiceos/config with 0600 permissions (owner-only).
    It is loaded automatically on every voiceos command.
    """
    if not api_key.startswith("sk-ant-"):
        click.echo(
            click.style(
                "Warning: key doesn't look like an Anthropic key (expected 'sk-ant-...').",
                fg="yellow",
            )
        )

    save_config_value("ANTHROPIC_API_KEY", api_key)
    os.environ["ANTHROPIC_API_KEY"] = api_key  # Effective immediately in this process
    click.echo(f"API key saved to {CONFIG_FILE}")
    click.echo("Run 'voiceos use-cloud' to switch to Claude, or 'voiceos start' to start.")


@main.command("use-cloud")
def use_cloud() -> None:
    """Switch to Claude (cloud) processing and save the setting.

    Uses claude_only mode: all queries go to Anthropic's API.
    Falls back to local Ollama automatically if the API key is unavailable.

    Requires ANTHROPIC_API_KEY — run 'voiceos set-key <key>' first if not set.
    """
    save_config_value("VOICEOS_LLM_MODE", "claude_only")
    os.environ["VOICEOS_LLM_MODE"] = "claude_only"

    if not os.getenv("ANTHROPIC_API_KEY"):
        click.echo(
            click.style(
                "Switched to cloud mode, but ANTHROPIC_API_KEY is not set.\n"
                "Run: voiceos set-key <your-key>",
                fg="yellow",
            )
        )
    else:
        click.echo("Switched to cloud (claude_only) mode. Setting saved.")
        click.echo("Run 'voiceos start' to begin.")


@main.command("use-local")
def use_local() -> None:
    """Switch to local Ollama processing only (offline, private).

    Uses ollama_only mode: no cloud calls, all processing on your Mac.
    """
    save_config_value("VOICEOS_LLM_MODE", "ollama_only")
    os.environ["VOICEOS_LLM_MODE"] = "ollama_only"
    click.echo("Switched to local (ollama_only) mode. Setting saved.")
    click.echo("Run 'voiceos start' to begin.")


@main.command("use-hybrid")
def use_hybrid() -> None:
    """Switch to hybrid mode: Ollama first, Claude as fallback.

    Tries local Ollama within the latency budget; if it fails or times out,
    falls back to Claude (requires ANTHROPIC_API_KEY for the fallback to work).
    """
    save_config_value("VOICEOS_LLM_MODE", "hybrid")
    os.environ["VOICEOS_LLM_MODE"] = "hybrid"
    click.echo("Switched to hybrid mode (Ollama → Claude fallback). Setting saved.")
    click.echo("Run 'voiceos start' to begin.")


@main.command()
def status() -> None:
    """Check health of all VoiceOS services."""
    click.echo("Checking service health...")

    async def check() -> None:
        from .registry.service_registry import ServiceRegistry
        registry = ServiceRegistry()
        health = await registry.health_check_all()

        for service, is_healthy in health.items():
            icon = "✅" if is_healthy else "❌"
            click.echo(f"  {icon} {service}")

        all_ok = all(health.values())
        if all_ok:
            click.echo("\nAll services are healthy.")
        else:
            failing = [k for k, v in health.items() if not v]
            click.echo(f"\nWarning: {', '.join(failing)} not responding.")
            click.echo("Run `voiceos start` to see startup logs.")

    asyncio.run(check())


@main.command("check-permissions")
def check_permissions() -> None:
    """Verify required macOS permissions are granted."""
    from .accessibility.accessibility_orchestrator import PermissionChecker
    checker = PermissionChecker()
    perms = checker.check_all()

    icons = {True: "✅", False: "❌"}
    click.echo("macOS Permission Status:")
    click.echo(f"  {icons[perms.accessibility]} Accessibility")
    click.echo(f"  {icons[perms.microphone]} Microphone")

    if not perms.all_granted:
        click.echo("\n" + perms.voice_message)
        if not perms.accessibility:
            click.echo("\nOpening System Settings → Accessibility...")
            PermissionChecker.request_accessibility()
    else:
        click.echo("\nAll required permissions are granted.")


@main.command()
def config() -> None:
    """Show current VoiceOS configuration."""
    from .stt.stt_manager import STTConfig
    from .tts.tts_manager import TTSConfig
    from .llm.llm_router import OllamaConfig, AnthropicConfig
    from .audio.audio_processor import AudioConfig

    stt = STTConfig.from_env()
    tts = TTSConfig.from_env()
    ollama = OllamaConfig.from_env()
    audio = AudioConfig.from_env()

    mode = os.getenv("VOICEOS_LLM_MODE", "hybrid")
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    click.echo("VoiceOS Configuration:")
    click.echo(f"\n  Config file:  {CONFIG_FILE} ({'exists' if CONFIG_FILE.exists() else 'not created yet'})")

    click.echo(f"\n  LLM Mode:     {mode}")

    # API key status with helpful hint
    if api_key:
        masked = api_key[:12] + "..." + api_key[-4:] if len(api_key) > 16 else "***"
        click.echo(f"  Anthropic:    {masked}")
    else:
        click.echo(
            click.style(
                "  Anthropic:    NOT SET — run: voiceos set-key <your-key>",
                fg="yellow",
            )
        )

    if mode == "claude_only" and not api_key:
        click.echo(
            click.style(
                "\n  ⚠️  claude_only mode but no API key — will fall back to Ollama.",
                fg="yellow",
            )
        )

    click.echo(f"\n  STT:")
    click.echo(f"    URL:        {stt.whisper_url}")
    click.echo(f"    Language:   {stt.language}")
    click.echo(f"\n  TTS:")
    click.echo(f"    URL:        {tts.kokoro_url}")
    click.echo(f"    Voice:      {tts.voice}")
    click.echo(f"    Speed:      {tts.speed}x")
    click.echo(f"\n  LLM (Ollama):")
    click.echo(f"    URL:        {ollama.base_url}")
    click.echo(f"    Default:    {ollama.default_model}")
    click.echo(f"    Code:       {ollama.code_model}")
    click.echo(f"    Fast:       {ollama.fast_model}")
    click.echo(f"\n  Audio:")
    click.echo(f"    Output:     {audio.preferred_output}")
    click.echo(f"    Silence:    {audio.silence_duration_sec}s")

    click.echo(f"\n  Quick switch:")
    click.echo(f"    voiceos use-cloud    → claude_only")
    click.echo(f"    voiceos use-local    → ollama_only")
    click.echo(f"    voiceos use-hybrid   → hybrid")


@main.command()
@click.option("--clear-session", is_flag=True, help="Clear saved session (start fresh next boot)")
@click.option("--clear-all", is_flag=True, help="Clear ALL memory — session + long-term facts")
def memory(clear_session: bool, clear_all: bool) -> None:
    """Show or manage VoiceOS persistent memory.

    Memory is stored at ~/.voiceos/memory/ and persists across sessions.
    Inspired by the Memory Bank Protocol from the Xoe-NovAi Foundation Stack
    (https://github.com/Xoe-NovAi/xoe-novai-foundation).
    """
    from .memory.memory_manager import MemoryManager
    mem = MemoryManager()

    if clear_all:
        mem.clear_long_term()
        mem.clear_session()
        click.echo("All memory cleared.")
        return

    if clear_session:
        mem.clear_session()
        click.echo("Session memory cleared. VoiceOS will start fresh next boot.")
        return

    stats = mem.stats()
    click.echo("VoiceOS Memory (Xoe-NovAi Memory Bank Pattern):")
    click.echo(f"\n  Storage:          {stats['memory_dir']}")
    click.echo(f"  Archive days:     {stats['archive_days']}")
    click.echo(f"  Total turns:      {stats['total_archived_turns']}")
    click.echo(f"  Session turns:    {stats['current_session_turns']}")
    click.echo(f"  Long-term facts:  {stats['long_term_facts']}")

    facts = mem.get_all_facts()
    if facts:
        click.echo("\n  Long-term memory:")
        for k, v in facts.items():
            click.echo(f"    {k}: {v}")
    else:
        click.echo("\n  No long-term facts yet.")
        click.echo("  Say 'remember that...' to save something, or facts are auto-extracted every 10 turns.")

    click.echo("\n  Commands:")
    click.echo("    voiceos memory --clear-session    Clear saved session")
    click.echo("    voiceos memory --clear-all        Wipe all memory")


if __name__ == "__main__":
    main()
