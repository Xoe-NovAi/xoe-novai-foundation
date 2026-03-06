#!/usr/bin/env python3
"""
CLI Abstraction Layer - Unified interface for different CLI environments
Allows the voice app to run via standalone Python, Cline, Copilot, or Claude CLI
"""

import asyncio
import json
import logging
import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, Callable, List, Tuple
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)


class CLIMode(Enum):
    """Available CLI modes"""
    STANDALONE = "standalone"  # Pure Python CLI
    CLINE = "cline"              # Cline CLI with MCP
    COPILOT = "copilot"          # GitHub Copilot CLI
    CLAUDE = "claude"            # Claude API with custom CLI
    OPENCODE = "opencode"        # OpenCode IDE extension
    BLIND_ACCESSIBLE = "blind"   # Blind-accessible voice-first mode


@dataclass
class CLIConfig:
    """Configuration for CLI mode"""
    mode: CLIMode
    verbose: bool = False
    interactive: bool = True
    headless: bool = False
    provider_api_key: Optional[str] = None
    provider_name: Optional[str] = None
    mcp_server_config: Optional[Dict[str, Any]] = None
    log_level: str = "INFO"


class CLIInterface(ABC):
    """Abstract base class for all CLI implementations"""

    def __init__(self, config: CLIConfig):
        """Initialize CLI interface"""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logging()
        self.callbacks: Dict[str, List[Callable]] = {}

    def _setup_logging(self):
        """Setup logging based on config"""
        level = getattr(logging, self.config.log_level, logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(level)

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize CLI environment and resources"""
        pass

    @abstractmethod
    async def process_command(self, command: str, args: List[str]) -> str:
        """Process a command and return response"""
        pass

    @abstractmethod
    async def start_interactive_session(self) -> None:
        """Start interactive REPL-like session"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup resources"""
        pass

    def register_callback(self, event: str, callback: Callable):
        """Register event callback"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)

    async def emit_event(self, event: str, data: Any = None):
        """Emit an event to all registered callbacks"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    self.logger.error(f"Error in callback for {event}: {e}")

    async def run_voice_turn(
        self,
        user_input: str,
        orchestrator: 'VoiceOrchestrator'
    ) -> Tuple[bool, str]:
        """Execute a single voice orchestrator turn
        
        Returns (success, response_text)
        """
        try:
            response = await orchestrator.generate_response(user_input)
            return (True, response or "No response generated")
        except Exception as e:
            self.logger.error(f"Voice turn error: {e}")
            return (False, f"Error: {str(e)}")


class StandaloneCLI(CLIInterface):
    """Standalone Python CLI implementation"""

    async def initialize(self) -> bool:
        """Initialize standalone CLI"""
        self.logger.info("Initializing Standalone CLI")
        try:
            # Import here to avoid circular imports
            from voice_orchestrator import VoiceOrchestrator
            self.orchestrator = VoiceOrchestrator()
            await self.emit_event("initialized", {"mode": "standalone"})
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            return False

    async def process_command(self, command: str, args: List[str]) -> str:
        """Process CLI command in standalone mode"""
        try:
            # Strip leading / from command (support both 'voice' and '/voice')
            cmd = command.lstrip('/')
            
            if cmd == "voice" and args:
                user_input = " ".join(args)
                success, response = await self.run_voice_turn(user_input, self.orchestrator)
                return response
            elif cmd == "status":
                status = self.orchestrator.get_status()
                return json.dumps(status, indent=2, default=str)
            elif cmd == "config":
                return json.dumps(self.orchestrator.config_dict, indent=2)
            elif cmd == "help":
                return self._get_help_text()
            else:
                return f"Unknown command: {cmd}"
        except Exception as e:
            self.logger.error(f"Command error: {e}")
            return f"Error: {str(e)}"

    async def start_interactive_session(self) -> None:
        """Start interactive REPL session"""
        self.logger.info("Starting interactive session (type 'help' for commands, 'quit' to exit)")
        
        while True:
            try:
                user_input = input("\nvice> ").strip()
                if not user_input:
                    continue
                if user_input.lower() == "quit":
                    self.logger.info("Exiting...")
                    break
                
                # Parse command (support both 'voice <text>' and '/voice <text>')
                if user_input.startswith('/'):
                    # Slash command format: /voice hello world
                    parts = user_input.lstrip('/').split(maxsplit=1)
                else:
                    # Regular format: voice hello world
                    parts = user_input.split(maxsplit=1)
                
                command = parts[0]
                args = parts[1].split() if len(parts) > 1 else []
                
                response = await self.process_command(command, args)
                print(response)
                
            except KeyboardInterrupt:
                self.logger.info("Interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Session error: {e}")

    async def shutdown(self) -> None:
        """Cleanup standalone CLI"""
        self.logger.info("Shutting down Standalone CLI")
        if hasattr(self, 'orchestrator'):
            self.orchestrator.cleanup()

    def _get_help_text(self) -> str:
        """Get help text"""
        return """
Standalone Voice CLI Commands:
  voice <text>        - Process voice input text
  /voice <text>       - Process voice input text (slash command format)
  status              - Show system status
  /status             - Show system status (slash command format)
  config              - Show current configuration
  /config             - Show current configuration (slash command format)
  help                - Show this help message
  quit                - Exit the application

Examples:
  voice What is the weather?
  /voice Tell me a joke
  status
  /status
  config
"""


class ClineCLI(CLIInterface):
    """Cline CLI implementation with MCP server"""

    async def initialize(self) -> bool:
        """Initialize Cline CLI mode"""
        self.logger.info("Initializing Cline CLI")
        try:
            # Import MCP server
            from mcp_server import get_mcp_server
            from voice_orchestrator import VoiceOrchestrator
            
            self.orchestrator = VoiceOrchestrator()
            self.mcp = get_mcp_server()
            
            # Register tools with MCP server
            self._register_mcp_tools()
            
            # Log available tools
            tools_list = self.mcp.get_tools_list()
            self.logger.info(f"Registered {len(tools_list)} tools with MCP server")
            for tool in tools_list:
                self.logger.info(f"  - {tool['name']}: {tool['description']}")
            
            await self.emit_event("initialized", {"mode": "cline", "mcp_server": "voice-assistant", "tools": len(tools_list)})
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Cline CLI: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _register_mcp_tools(self):
        """Register voice tools with MCP server"""
        
        # Tool 1: voice_input - process voice text
        async def handle_voice_input(args: dict) -> dict:
            text = args.get("text", "")
            if not text:
                return {"error": "text is required"}
            success, response = await self.run_voice_turn(text, self.orchestrator)
            return {"response": response, "success": success}
        
        self.mcp.register_tool(
            name="voice_input",
            description="Process voice input text through the voice orchestrator pipeline (STT→LLM→TTS). Returns processed response.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The voice input text to process"
                    }
                },
                "required": ["text"]
            },
            handler=handle_voice_input,
            category="voice"
        )
        
        # Tool 2: get_status - get system status
        def handle_get_status(args: dict) -> dict:
            status = self.orchestrator.get_status()
            return status
        
        self.mcp.register_tool(
            name="get_status",
            description="Get the current status of the voice orchestrator system, including service health and configuration",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=handle_get_status,
            category="status"
        )
        
        # Tool 3: list_memories - search and list stored memories
        def handle_list_memories(args: dict) -> dict:
            from src.memory.memory_bank import get_memory_bank
            mb = get_memory_bank()
            query = args.get("query", "")
            max_results = args.get("max_results", 10)
            
            memories = mb.search(query, max_results=max_results) if query else []
            return {
                "memories": [
                    {"id": m.id, "content": m.content, "type": m.memory_type, "timestamp": str(m.created_at)}
                    for m in memories
                ],
                "total": len(memories),
                "query": query
            }
        
        self.mcp.register_tool(
            name="list_memories",
            description="Search and list stored memories from the voice assistant's memory system",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for memories"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)"
                    }
                }
            },
            handler=handle_list_memories,
            category="memory"
        )

    async def process_command(self, command: str, args: List[str]) -> str:
        """Process command in Cline mode"""
        # Strip leading / from command
        cmd = command.lstrip('/')
        
        # Map to MCP tool operations
        if cmd == "voice_input" or cmd == "voice":
            text = " ".join(args) if args else ""
            success, response = await self.run_voice_turn(text, self.orchestrator)
            return response
        elif cmd == "get_status" or cmd == "status":
            status = self.orchestrator.get_status()
            return json.dumps(status, indent=2, default=str)
        elif cmd == "list_memories":
            from src.memory.memory_bank import get_memory_bank
            mb = get_memory_bank()
            query = " ".join(args) if args else ""
            memories = mb.search(query, max_results=10)
            return json.dumps([
                {"id": m.id, "content": m.content, "type": m.memory_type}
                for m in memories
            ], indent=2)
        else:
            # Return list of available tools
            tools = self.mcp.get_tools_list()
            return json.dumps({
                "error": f"Unknown tool: {cmd}",
                "available_tools": [t["name"] for t in tools]
            })

    async def start_interactive_session(self) -> None:
        """Start interactive session in Cline mode"""
        # Show help for Cline users
        tools = self.mcp.get_tools_list()
        help_text = "Cline Voice Tools ready!\n\nAvailable tools:\n"
        for tool in tools:
            help_text += f"  • {tool['name']}: {tool['description']}\n"
        
        self.logger.info(help_text)
        await self.emit_event("ready", {"mode": "cline", "tools": len(tools)})

    async def shutdown(self) -> None:
        """Cleanup Cline CLI"""
        self.logger.info("Shutting down Cline CLI")
        if hasattr(self, 'orchestrator'):
            self.orchestrator.cleanup()


class CopilotCLI(CLIInterface):
    """GitHub Copilot CLI implementation"""

    async def initialize(self) -> bool:
        """Initialize Copilot CLI mode"""
        self.logger.info("Initializing GitHub Copilot CLI")
        try:
            # Check for Copilot CLI availability
            if not self._check_copilot_available():
                self.logger.warning("GitHub Copilot CLI not found - falling back to standalone")
                return False
            
            from voice_orchestrator import VoiceOrchestrator
            self.orchestrator = VoiceOrchestrator()
            
            await self.emit_event("initialized", {"mode": "copilot"})
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Copilot CLI: {e}")
            return False

    def _check_copilot_available(self) -> bool:
        """Check if Copilot CLI is available"""
        import subprocess
        try:
            result = subprocess.run(
                ["command", "-v", "gh"],
                shell=True,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    async def process_command(self, command: str, args: List[str]) -> str:
        """Process command in Copilot mode"""
        try:
            # Strip leading / from command
            cmd = command.lstrip('/')
            
            if cmd == "voice":
                text = " ".join(args)
                success, response = await self.run_voice_turn(text, self.orchestrator)
                return response
            elif cmd == "status":
                status = self.orchestrator.get_status()
                return json.dumps(status, indent=2, default=str)
            else:
                return f"Copilot CLI command: {cmd} {' '.join(args)}"
        except Exception as e:
            return f"Error: {str(e)}"

    async def start_interactive_session(self) -> None:
        """Start interactive session in Copilot mode"""
        self.logger.info("GitHub Copilot CLI active")
        # Copilot handles the interactive loop

    async def shutdown(self) -> None:
        """Cleanup Copilot CLI"""
        self.logger.info("Shutting down Copilot CLI")
        if hasattr(self, 'orchestrator'):
            self.orchestrator.cleanup()


class ClaudeCLI(CLIInterface):
    """Claude API-based custom CLI implementation"""

    async def initialize(self) -> bool:
        """Initialize Claude CLI mode"""
        self.logger.info("Initializing Claude API CLI")
        try:
            # Check for Claude API key
            api_key = self.config.provider_api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                self.logger.error("ANTHROPIC_API_KEY not set")
                return False
            
            try:
                from anthropic import Anthropic
            except ImportError:
                self.logger.error("anthropic package not installed - run: pip install anthropic")
                return False
            
            self.client = Anthropic(api_key=api_key)
            self.conversation_history = []
            
            from voice_orchestrator import VoiceOrchestrator
            self.orchestrator = VoiceOrchestrator()
            
            await self.emit_event("initialized", {"mode": "claude"})
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Claude CLI: {e}")
            return False

    async def process_command(self, command: str, args: List[str]) -> str:
        """Process command through Claude API"""
        try:
            # Strip leading / from command
            cmd = command.lstrip('/')
            
            # Handle voice command directly
            if cmd == "voice":
                text = " ".join(args)
                success, response = await self.run_voice_turn(text, self.orchestrator)
                
                # Still add to conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": f"voice {text}"
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                return response
            
            user_message = f"{cmd} {' '.join(args)}"
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Get response from Claude
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=self._get_system_prompt(),
                messages=self.conversation_history
            )
            
            assistant_message = response.content[0].text
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            return f"Error: {str(e)}"

    async def start_interactive_session(self) -> None:
        """Start interactive Claude CLI session"""
        self.logger.info("Claude CLI ready (type 'quit' to exit, use /voice for voice commands)")
        
        while True:
            try:
                user_input = input("\nclaude> ").strip()
                if not user_input:
                    continue
                if user_input.lower() == "quit":
                    break
                
                # Handle /voice or voice commands
                if user_input.startswith('/'):
                    parts = user_input.lstrip('/').split(maxsplit=1)
                else:
                    parts = user_input.split(maxsplit=1)
                
                command = parts[0]
                args = parts[1].split() if len(parts) > 1 else []
                
                response = await self.process_command(command, args)
                print(f"\nAssistant: {response}")
                
            except KeyboardInterrupt:
                self.logger.info("Interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Session error: {e}")

    async def shutdown(self) -> None:
        """Cleanup Claude CLI"""
        self.logger.info("Shutting down Claude CLI")
        if hasattr(self, 'orchestrator'):
            self.orchestrator.cleanup()

    def _get_system_prompt(self) -> str:
        """Get system prompt for Claude"""
        return """You are a helpful AI assistant integrated with a voice orchestrator system.
You have access to voice processing capabilities and can help users with voice-related tasks.

When users ask about voice, audio, or speech-related tasks, provide helpful responses.
When appropriate, offer to process voice input or check system status.

Be concise and helpful."""


class OpenCodeCLI(CLIInterface):
    """OpenCode IDE extension implementation"""

    async def initialize(self) -> bool:
        """Initialize OpenCode CLI mode"""
        self.logger.info("Initializing OpenCode CLI")
        try:
            from voice_orchestrator import VoiceOrchestrator
            self.orchestrator = VoiceOrchestrator()
            
            # OpenCode can use either direct stdin/stdout or a simple command interface
            self._setup_opencode_interface()
            
            await self.emit_event("initialized", {"mode": "opencode"})
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenCode CLI: {e}")
            return False

    def _setup_opencode_interface(self):
        """Setup OpenCode interface - can be extended for custom protocol"""
        self.opencode_tools = {
            "voice": {
                "label": "Process Voice Input",
                "description": "Send text through voice pipeline",
                "command": "voice"
            },
            "status": {
                "label": "Get Status",
                "description": "Get system and service status",
                "command": "status"
            },
            "memories": {
                "label": "List Memories",
                "description": "Search stored memories",
                "command": "memories"
            }
        }

    async def process_command(self, command: str, args: List[str]) -> str:
        """Process command in OpenCode mode"""
        try:
            # Strip leading / from command
            cmd = command.lstrip('/')
            
            if cmd == "voice":
                text = " ".join(args)
                success, response = await self.run_voice_turn(text, self.orchestrator)
                return response
            elif cmd == "status":
                status = self.orchestrator.get_status()
                return json.dumps(status, indent=2, default=str)
            elif cmd == "memories":
                from src.memory.memory_bank import get_memory_bank
                mb = get_memory_bank()
                query = " ".join(args) if args else ""
                memories = mb.search(query, max_results=10)
                return json.dumps([
                    {"id": m.id, "content": m.content, "type": m.memory_type}
                    for m in memories
                ], indent=2)
            else:
                return json.dumps({"error": f"Unknown command: {cmd}", "available_commands": list(self.opencode_tools.keys())})
        except Exception as e:
            self.logger.error(f"OpenCode command error: {e}")
            return json.dumps({"error": str(e)})

    async def start_interactive_session(self) -> None:
        """Start interactive session in OpenCode mode"""
        self.logger.info("OpenCode CLI ready - use voice, status, memories commands")
        
        while True:
            try:
                user_input = input("\nopencode> ").strip()
                if not user_input:
                    continue
                if user_input.lower() == "quit":
                    break
                
                # Handle both /command and command formats
                if user_input.startswith('/'):
                    parts = user_input.lstrip('/').split(maxsplit=1)
                else:
                    parts = user_input.split(maxsplit=1)
                
                command = parts[0]
                args = parts[1].split() if len(parts) > 1 else []
                
                response = await self.process_command(command, args)
                print(response)
                
            except KeyboardInterrupt:
                self.logger.info("Interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"OpenCode session error: {e}")

    async def shutdown(self) -> None:
        """Cleanup OpenCode CLI"""
        self.logger.info("Shutting down OpenCode CLI")
        if hasattr(self, 'orchestrator'):
            self.orchestrator.cleanup()


class BlindAccessibleCLI(CLIInterface):
    """
    Blind-Accessible Voice-First CLI
    
    Designed for blind and visually impaired users
    - Wake word activation ("Hey Voice")
    - Natural voice-to-voice conversation
    - Audio feedback for all actions
    - No typing required
    - Continuous listening mode
    """

    async def initialize(self) -> bool:
        """Initialize blind-accessible voice mode"""
        self.logger.info("Initializing Blind-Accessible Voice Mode")
        try:
            from voice_orchestrator import VoiceOrchestrator
            from voice_activation import VoiceSessionManager, VoiceInterruptHandler
            from conversation_manager import ConversationFlowManager, BlindAccessibleResponseFormatter
            
            self.orchestrator = VoiceOrchestrator()
            self.session_manager = VoiceSessionManager(config={
                'sample_rate': 16000,
                'feedback_enabled': True,
                'sensitivity': 0.8
            })
            self.interrupt_handler = VoiceInterruptHandler()
            self.conversation_manager = ConversationFlowManager()
            self.response_formatter = BlindAccessibleResponseFormatter()
            
            # Initialize session
            success = await self.session_manager.initialize()
            if success:
                await self.emit_event("initialized", {"mode": "blind_accessible"})
                self.logger.info("✓ Voice activation ready. Say 'Hey Voice' or 'Voice' to start.")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to initialize blind-accessible mode: {e}")
            return False

    async def process_command(self, command: str, args: List[str]) -> str:
        """Process command (not typical for voice mode)"""
        # This is rarely used in voice mode, but keep for interface compliance
        return f"Command received: {command}"

    async def start_interactive_session(self) -> None:
        """Start voice-first interactive session"""
        self.logger.info("=" * 60)
        self.logger.info("VOICE-FIRST MODE ACTIVATED")
        self.logger.info("=" * 60)
        self.logger.info("Say 'Hey Voice' to start, or 'Stop listening' to exit.")
        self.logger.info("=" * 60)
        
        await self.session_manager.start_session()
        
        try:
            while True:
                # Get user speech
                audio, is_valid = await self.session_manager.get_user_speech(timeout=10.0)
                
                if not is_valid:
                    self.logger.info("No speech detected. Try again.")
                    continue
                
                # Convert speech to text (STT)
                try:
                    from stt_manager import STTManager
                    stt = STTManager()
                    user_text = await stt.transcribe_audio(audio)
                    self.logger.info(f"You said: {user_text}")
                    
                except Exception as e:
                    self.logger.error(f"Speech recognition failed: {e}")
                    await self.session_manager.audio_feedback.play_feedback('error')
                    continue
                
                # Check for wake word or interrupt commands
                if not self._is_session_started_yet:
                    if self.session_manager.wake_detector.detect_wake_word_from_text(user_text):
                        self._is_session_started_yet = True
                        await self.session_manager.audio_feedback.play_feedback('wake_word')
                        self.logger.info("Wake word detected! Ready for your request.")
                        continue
                    else:
                        continue
                
                # Check for interrupt commands
                command_type = self.interrupt_handler.classify_command(user_text)
                
                if command_type == 'stop':
                    self.logger.info("Pausing response...")
                    await self.session_manager.audio_feedback.play_feedback('processing')
                    continue
                
                elif command_type == 'repeat':
                    last_response = self.conversation_manager.context.get_last_response()
                    if last_response:
                        formatted = self.response_formatter.format_response(last_response)
                        self.logger.info(f"Repeating: {formatted}")
                        # Would play audio here
                    continue
                
                elif command_type == 'exit':
                    self.logger.info("Goodbye!")
                    break
                
                # Process normal speech input
                if command_type == 'speech':
                    try:
                        # Get response with full context
                        response, suggestions = await self.conversation_manager.process_user_input(
                            user_text,
                            self.orchestrator
                        )
                        
                        # Format for voice output
                        formatted_response = self.response_formatter.format_response(response)
                        
                        # Log the response
                        self.logger.info(f"Voice: {formatted_response}")
                        
                        # Play success feedback
                        await self.session_manager.audio_feedback.play_feedback('success')
                        
                        # Suggest follow-up actions
                        if suggestions:
                            follow_up = self.conversation_manager.context.get_follow_up_prompt()
                            self.logger.info(f"Next: {follow_up}")
                        
                    except Exception as e:
                        self.logger.error(f"Error processing input: {e}")
                        await self.session_manager.audio_feedback.play_feedback('error')
                
        except KeyboardInterrupt:
            self.logger.info("Voice session interrupted by user")
        except Exception as e:
            self.logger.error(f"Voice session error: {e}")
        finally:
            await self.session_manager.end_session()

    async def shutdown(self) -> None:
        """Cleanup voice resources"""
        self.logger.info("Shutting down blind-accessible voice mode")
        try:
            await self.session_manager.cleanup()
            if hasattr(self, 'orchestrator'):
                self.orchestrator.cleanup()
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

    def __init__(self, config: CLIConfig):
        """Initialize blind-accessible CLI"""
        super().__init__(config)
        self._is_session_started_yet = False


class CLIFactory:
    """Factory for creating CLI instances"""

    _implementations = {
        CLIMode.STANDALONE: StandaloneCLI,
        CLIMode.CLINE: ClineCLI,
        CLIMode.COPILOT: CopilotCLI,
        CLIMode.CLAUDE: ClaudeCLI,
        CLIMode.OPENCODE: OpenCodeCLI,
        CLIMode.BLIND_ACCESSIBLE: BlindAccessibleCLI,
    }

    @classmethod
    def create(cls, config: CLIConfig) -> CLIInterface:
        """Create CLI instance based on config"""
        impl_class = cls._implementations.get(config.mode)
        if not impl_class:
            raise ValueError(f"Unknown CLI mode: {config.mode}")
        return impl_class(config)

    @classmethod
    def detect_environment(cls) -> CLIMode:
        """Detect current CLI environment"""
        # Check for OpenCode
        if os.getenv("OPENCODE_AVAILABLE") or os.path.exists(os.path.expanduser("~/.opencode")):
            return CLIMode.OPENCODE
        
        # Check for Cline
        if os.getenv("CLINE_AVAILABLE") or os.path.exists(os.path.expanduser("~/.cline")):
            return CLIMode.CLINE
        
        # Check for Copilot
        if os.getenv("GITHUB_COPILOT_ENABLED"):
            return CLIMode.COPILOT
        
        # Check for Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            return CLIMode.CLAUDE
        
        # Default to standalone
        return CLIMode.STANDALONE


async def run_cli(
    mode: Optional[CLIMode] = None,
    interactive: bool = True,
    verbose: bool = False,
    api_key: Optional[str] = None
) -> int:
    """Main entry point for running the CLI
    
    Args:
        mode: CLI mode (auto-detect if None)
        interactive: Whether to start interactive session
        verbose: Enable verbose logging
        api_key: API key for providers that need it
    
    Returns:
        Exit code (0 for success)
    """
    # Detect or use provided mode
    if mode is None:
        mode = CLIFactory.detect_environment()
    
    # Create config
    config = CLIConfig(
        mode=mode,
        interactive=interactive,
        verbose=verbose,
        provider_api_key=api_key,
        log_level="DEBUG" if verbose else "INFO"
    )
    
    # Create and initialize CLI
    cli = CLIFactory.create(config)
    
    try:
        if not await cli.initialize():
            return 1
        
        if interactive and config.interactive:
            await cli.start_interactive_session()
        else:
            await cli.emit_event("ready", {"mode": str(mode.value)})
        
        return 0
        
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
        return 130
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        return 1
    finally:
        await cli.shutdown()


if __name__ == "__main__":
    exit_code = asyncio.run(run_cli(interactive=True, verbose=True))
    sys.exit(exit_code)
