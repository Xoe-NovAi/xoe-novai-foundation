#!/usr/bin/env python3
"""
Voice Setup - Main entry point for the voice orchestrator application
Supports multiple CLI modes: standalone, Cline, Copilot, Claude
Auto-manages services (Ollama, STT, TTS)
"""

import asyncio
import sys
import logging
import argparse
import json
import os
from typing import Optional

from cli_abstraction import CLIMode, CLIFactory, CLIConfig, run_cli
from service_manager import get_service_manager, ensure_services_ready


# Setup root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VoiceApp:
    """Main application class"""

    def __init__(self, args):
        """Initialize voice app"""
        self.args = args
        self.service_manager = get_service_manager()
        self.cli_mode = self._determine_cli_mode()

    def _determine_cli_mode(self) -> CLIMode:
        """Determine which CLI mode to use"""
        if self.args.cli_mode:
            mode_map = {
                "standalone": CLIMode.STANDALONE,
                "cline": CLIMode.CLINE,
                "copilot": CLIMode.COPILOT,
                "claude": CLIMode.CLAUDE,
                "opencode": CLIMode.OPENCODE,
                "blind": CLIMode.BLIND_ACCESSIBLE,
                "auto": None,
            }
            mode = mode_map.get(self.args.cli_mode)
            if mode is None and self.args.cli_mode != "auto":
                logger.warning(f"Unknown CLI mode: {self.args.cli_mode}, using auto-detection")
                mode = CLIFactory.detect_environment()
            elif mode is None:
                mode = CLIFactory.detect_environment()
            return mode
        else:
            return CLIFactory.detect_environment()

    async def setup_services(self) -> bool:
        """Setup and verify all required services"""
        logger.info("Setting up services...")

        # Start monitoring
        monitor_task = asyncio.create_task(self.service_manager.start_monitoring())

        try:
            # Ensure required services are running
            services_to_start = ["ollama"] if not self.args.no_ollama else []

            if services_to_start and not self.args.no_auto_start:
                if not await ensure_services_ready(services_to_start):
                    logger.warning("Some services failed to start")
                    if self.args.fail_on_service_error:
                        return False

            # Show service status
            status = await self.service_manager.get_all_services_status()
            logger.info(f"Service status: {json.dumps(status, indent=2)}")

            return True

        except Exception as e:
            logger.error(f"Service setup error: {e}")
            return False

    async def run(self) -> int:
        """Run the application
        
        Returns:
            Exit code
        """
        try:
            # Setup logging level
            if self.args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)
                logger.info("Verbose mode enabled")

            logger.info(f"Starting Voice Assistant ({self.cli_mode.value} mode)")

            # Setup services if not disabled
            if not self.args.skip_services:
                if not await self.setup_services():
                    if self.args.fail_on_service_error:
                        logger.error("Failed to setup services")
                        return 1

            # Create CLI config
            cli_config = CLIConfig(
                mode=self.cli_mode,
                verbose=self.args.verbose,
                interactive=self.args.interactive,
                headless=self.args.headless,
                provider_api_key=self.args.api_key,
                log_level="DEBUG" if self.args.verbose else "INFO",
            )

            # Create and run CLI
            cli = CLIFactory.create(cli_config)

            if not await cli.initialize():
                logger.error("Failed to initialize CLI")
                return 1

            # Start interactive session if requested
            if self.args.interactive and not self.args.headless:
                await cli.start_interactive_session()
            elif self.args.command:
                # Process single command and exit
                parts = self.args.command.split(maxsplit=1)
                command = parts[0]
                args = parts[1].split() if len(parts) > 1 else []
                response = await cli.process_command(command, args)
                print(response)
            else:
                # Ready for external input (e.g., from Cline MCP server)
                logger.info("Voice Assistant ready for input")
                await asyncio.sleep(1000)  # Keep running

            await cli.shutdown()
            return 0

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            return 130
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return 1
        finally:
            await self.service_manager.shutdown()

    async def show_status(self) -> None:
        """Show application status"""
        logger.info("=== Voice Assistant Status ===")
        
        # Service status
        service_status = await self.service_manager.get_all_services_status()
        logger.info(f"Services: {json.dumps(service_status, indent=2)}")
        
        # CLI mode
        logger.info(f"CLI Mode: {self.cli_mode.value}")
        
        # Memory status
        try:
            from src.memory.memory_bank import get_memory_bank
            mb = get_memory_bank()
            mem_stats = mb.get_memory_stats()
            logger.info(f"Memory: {json.dumps(mem_stats, indent=2)}")
        except Exception as e:
            logger.warning(f"Could not get memory stats: {e}")

    async def show_config(self) -> None:
        """Show configuration"""
        try:
            from config_manager import ConfigManager
            cm = ConfigManager()
            logger.info("Configuration:")
            logger.info(json.dumps(cm.config, indent=2))
        except Exception as e:
            logger.error(f"Could not load configuration: {e}")


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Voice Assistant - Multi-mode voice orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start interactive standalone CLI
  python main.py --interactive

  # Use Cline CLI interface
  python main.py --cli-mode cline

  # Use blind-accessible voice-first mode for blind users
  python main.py --cli-mode blind --interactive

  # Use OpenCode IDE extension
  python main.py --cli-mode opencode --interactive

  # Use Claude API with custom CLI
  python main.py --cli-mode claude --api-key <key>

  # Run single command
  python main.py --command "voice What is the weather?"

  # Show status
  python main.py --status

  # Headless mode (useful for MCP servers)
  python main.py --headless --cli-mode cline
        """
    )

    # CLI mode selection
    parser.add_argument(
        "--cli-mode",
        choices=["standalone", "cline", "copilot", "claude", "opencode", "blind", "auto"],
        default="auto",
        help="CLI mode to use (default: auto-detect)"
    )

    # Interaction modes
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive session"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (no interactive session)"
    )

    parser.add_argument(
        "-c", "--command",
        type=str,
        help="Execute a single command and exit"
    )

    # Service management
    parser.add_argument(
        "--no-auto-start",
        action="store_true",
        help="Don't auto-start services"
    )

    parser.add_argument(
        "--no-ollama",
        action="store_true",
        help="Don't require Ollama service"
    )

    parser.add_argument(
        "--skip-services",
        action="store_true",
        help="Skip service setup entirely"
    )

    parser.add_argument(
        "--fail-on-service-error",
        action="store_true",
        help="Exit if any service fails to start"
    )

    # API keys and credentials
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for providers (Claude, OpenAI, etc.)"
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=["claude", "openai", "openrouter", "ollama"],
        help="LLM provider to use"
    )

    # Logging and debugging
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Reduce output verbosity"
    )

    # Status and configuration
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show application status and exit"
    )

    parser.add_argument(
        "--config",
        action="store_true",
        help="Show configuration and exit"
    )

    # Version
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit"
    )

    return parser


def main() -> int:
    """Main entry point
    
    Returns:
        Exit code
    """
    parser = create_argument_parser()
    args = parser.parse_args()

    # Handle flags that exit immediately
    if args.version:
        print("Voice Assistant v1.0.0")
        return 0

    # Create and run app
    app = VoiceApp(args)

    # Handle status/config requests
    if args.status:
        asyncio.run(app.show_status())
        return 0

    if args.config:
        asyncio.run(app.show_config())
        return 0

    # Default: interactive unless specified otherwise
    if not args.command and not args.headless:
        args.interactive = True

    # Run the application
    return asyncio.run(app.run())


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
