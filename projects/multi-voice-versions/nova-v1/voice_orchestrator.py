#!/usr/bin/env python3
"""
Voice Orchestrator - Main service orchestrator for local voice setup
Manages routing between Claude Code and Ollama LLMs with STT/TTS integration
"""

import asyncio
import logging
import sys
sys.path.append('src')
import time
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stt_manager import STTManager
from tts_manager import TTSManager
from ollama_client import OllamaClient
from config_manager import ConfigManager
from health_monitor import HealthMonitor
from audio_processor import AudioProcessor
from memory.memory_integration import MemoryAwareVoiceOrchestrator
from src.memory.memory_bank import get_memory_bank

class LLMMode(Enum):
    """LLM operation modes"""
    CLAUDE_ONLY = "claude_only"
    OLLAMA_ONLY = "ollama_only"
    HYBRID = "hybrid"
    AUTO = "auto"

class QualityMode(Enum):
    """Quality vs Speed modes"""
    HIGH_QUALITY = "high_quality"
    BALANCED = "balanced"
    HIGH_SPEED = "high_speed"
    ULTRA_FAST = "ultra_fast"

@dataclass
class VoiceConfig:
    """Voice setup configuration"""
    llm_mode: LLMMode = LLMMode.AUTO
    quality_mode: QualityMode = QualityMode.BALANCED
    stt_model: str = "canary_qwen_2.5b"
    tts_model: str = "orpheus_3b"
    ollama_model: str = "llama3.2"
    fallback_timeout: float = 5.0
    max_concurrent_requests: int = 3
    enable_voice_cloning: bool = False
    voice_clone_sample_path: Optional[str] = None

class VoiceOrchestrator:
    """Main orchestrator for voice conversation system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the voice orchestrator"""
        self.config_manager = ConfigManager(config_path)
        self.config_dict = self.config_manager.config  # Dictionary config
        self.config = self._create_voice_config(self.config_dict)  # Dataclass config
        
        # Initialize components with their specific config sections
        self.stt_manager = STTManager(self.config_dict.get('stt', {}))
        self.tts_manager = TTSManager(self.config_dict.get('tts', {}))
        self.ollama_client = OllamaClient(self.config_dict.get('ollama', {}))
        self.health_monitor = HealthMonitor(self.config_dict.get('monitoring', {}))
        self.audio_processor = AudioProcessor(self.config_dict.get('audio', {}))

        # memory subsystem
        mem_conf = self.config_dict.get('memory', {})
        self.memory_enabled = mem_conf.get('enabled', False)
        self.memory_bank = get_memory_bank() if self.memory_enabled else None
        # helper object kept for backwards compatibility
        self.memory_integration = MemoryAwareVoiceOrchestrator(self)
        
        # State management
        self.is_listening = False
        self.is_processing = False
        self.conversation_active = False
        self.last_activity_time = time.time()
        
        # Performance metrics
        self.metrics = {
            'stt_latency': [],
            'tts_latency': [],
            'llm_latency': [],
            'total_latency': [],
            'error_count': 0,
            'success_count': 0
        }
        
        # Setup logging
        self._setup_logging()
        
    def _create_voice_config(self, config_dict: Dict[str, Any]) -> VoiceConfig:
        """Create VoiceConfig dataclass from dictionary"""
        voice_section = config_dict.get('voice', {})
        return VoiceConfig(
            llm_mode=LLMMode(voice_section.get('llm_mode', 'auto')),
            quality_mode=QualityMode(voice_section.get('quality_mode', 'balanced')),
            stt_model=voice_section.get('stt_model', 'canary_qwen_2.5b'),
            tts_model=voice_section.get('tts_model', 'orpheus_3b'),
            ollama_model=voice_section.get('ollama_model', 'llama3.2'),
            fallback_timeout=voice_section.get('fallback_timeout', 5.0),
            max_concurrent_requests=voice_section.get('max_concurrent_requests', 3),
            enable_voice_cloning=voice_section.get('enable_voice_cloning', False),
            voice_clone_sample_path=voice_section.get('voice_clone_sample_path')
        )
        
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('voice_orchestrator.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def start_conversation(self):
        """Start a voice conversation session"""
        self.logger.info("Starting voice conversation session")
        self.conversation_active = True
        self.is_listening = True

        # make sure all underlying services are initialized before loop
        await self.stt_manager.initialize()
        await self.tts_manager.initialize()
        await self.ollama_client.initialize()

        try:
            while self.conversation_active:
                # Listen for user input
                audio_data = await self._listen_for_audio()
                if not audio_data:
                    continue

                # Process audio and transcribe
                start_time = time.time()
                transcript = await self._process_audio_to_text(audio_data)
                if not transcript:
                    self.logger.warning("Failed to transcribe audio")
                    continue

                stt_latency = time.time() - start_time
                self.metrics['stt_latency'].append(stt_latency)

                self.logger.info(f"Transcribed: {transcript}")

                # Generate response (memory integration happens inside)
                response_text = await self.generate_response(transcript)
                if not response_text:
                    continue

                llm_latency = time.time() - start_time - stt_latency
                self.metrics['llm_latency'].append(llm_latency)

                # Convert to speech
                total_start = time.time()
                await self._speak_response(response_text)

                tts_latency = time.time() - total_start - stt_latency - llm_latency
                self.metrics['tts_latency'].append(tts_latency)

                total_latency = time.time() - start_time
                self.metrics['total_latency'].append(total_latency)

                self.logger.info(f"Response generated in {total_latency:.2f}s")
                self.metrics['success_count'] += 1

        except Exception as e:
            self.logger.error(f"Conversation error: {e}")
            self.metrics['error_count'] += 1
        finally:
            await self.stop_conversation()
            
    async def _listen_for_audio(self) -> Optional[bytes]:
        """Listen for audio input with VAD"""
        try:
            audio_data = await self.audio_processor.record_audio_with_vad()
            return audio_data
        except Exception as e:
            self.logger.error(f"Audio recording error: {e}")
            return None
            
    async def _process_audio_to_text(self, audio_data: bytes) -> Optional[str]:
        """Convert audio to text using STT manager"""
        try:
            # Preprocess audio
            processed_audio = self.audio_processor.preprocess_audio(audio_data)
            
            # Transcribe using selected STT model
            transcript = await self.stt_manager.transcribe(processed_audio)
            return transcript
        except Exception as e:
            self.logger.error(f"STT processing error: {e}")
            return None
            
    async def _generate_response(self, user_input: str) -> Optional[str]:
        """Low level LLM call.  The public ``generate_response`` method handles
        context injection and memory storage.
        """
        try:
            # Determine which LLM to use based on mode and availability
            llm_choice = self._select_llm()

            if llm_choice == "ollama":
                response = await self.ollama_client.generate_response(
                    user_input,
                    model=self.config.ollama_model
                )
            else:  # Claude Code
                response = await self._generate_claude_response(user_input)

            return response
        except Exception as e:
            self.logger.error(f"LLM generation error: {e}")
            return None
            
    def _select_llm(self) -> str:
        """Select which LLM to use based on mode and availability"""

    async def generate_response(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Public method that adds memory/context and stores interactions.

        - If a context dict is provided it will be appended to the prompt.
        - If the memory subsystem is enabled and no context is passed, a
          relevant context will be fetched automatically.
        - After generating an answer the user input and response are recorded
          when memory is active.
        """
        original_input = user_input

        # fetch context automatically when appropriate
        if self.memory_enabled and context is None and self.memory_bank:
            try:
                context = self.memory_bank.get_relevant_context(user_input)
            except Exception as e:
                self.logger.warning(f"Memory retrieval error: {e}")
                context = {}

        # update transient context manager (always available when memory bank exists)
        if self.memory_bank:
            try:
                self.memory_bank.context_manager.update_context({
                    'role': 'user',
                    'text': original_input
                })
            except Exception:
                pass

        # if we have a context dict from memory retrieval, append it
        if context:
            ctx_lines = [f"{k}: {v}" for k, v in (context.items() if isinstance(context, dict) else [])]
            if ctx_lines:
                context_prompt = "\n".join(ctx_lines)
                user_input = f"{user_input}\n\nContext:\n{context_prompt}"

        # add ephemeral/transient context (short-term conversation state)
        if self.memory_bank:
            try:
                ephemeral = self.memory_bank.context_manager.get_context()
                if ephemeral:
                    ep_lines = [f"{k}: {v}" for k, v in ephemeral.items()]
                    if ep_lines:
                        ep_prompt = "\n".join(ep_lines)
                        user_input = f"{user_input}\n\nEphemeralContext:\n{ep_prompt}"
            except Exception as e:
                self.logger.debug(f"Failed to append ephemeral context: {e}")

        # also include recent conversation history at top if memory is enabled
        if self.memory_enabled and self.memory_bank:
            try:
                history = self.memory_bank.get_conversation_history(limit=5)
                if history:
                    hist_lines = []
                    for entry in history:
                        role = entry.get('context', {}).get('role', 'unknown') if isinstance(entry.get('context'), dict) else entry.get('context', {}).get('role', 'unknown')
                        hist_lines.append(f"[{role}] {entry.get('content')}" )
                    if hist_lines:
                        hist_prompt = "\n".join(hist_lines)
                        user_input = f"{hist_prompt}\n\n{user_input}"
            except Exception as e:
                self.logger.debug(f"Unable to prepend conversation history: {e}")

        response = await self._generate_response(user_input)

        # record the exchange if memory is active
        if self.memory_enabled and response:
            try:
                self.memory_bank.store_interaction(original_input, response)
                # update ephemeral context with assistant answer as well
                self.memory_bank.context_manager.update_context({
                    'role': 'assistant',
                    'text': response
                })
            except Exception as e:
                self.logger.warning(f"Failed to store interaction: {e}")

        return response

    def _select_llm(self) -> str:
        """Select which LLM to use based on mode and availability"""
        if self.config.llm_mode == LLMMode.CLAUDE_ONLY:
            return "claude"
        elif self.config.llm_mode == LLMMode.OLLAMA_ONLY:
            return "ollama"
        elif self.config.llm_mode == LLMMode.HYBRID:
            # Check availability and select based on quality mode
            if self.ollama_client.is_available:  # attribute not method
                return "ollama"
            else:
                return "claude"
        else:  # AUTO mode
            # Smart selection based on content and performance
            return self._smart_llm_selection()
            
    def _smart_llm_selection(self) -> str:
        """Smart LLM selection based on content analysis and performance"""
        # For now, simple fallback logic
        if self.ollama_client.is_available:
            return "ollama"
        return "claude"
        
    async def _generate_claude_response(self, user_input: str) -> Optional[str]:
        """Generate response using Claude Code via MCP"""
        try:
            # This would integrate with the existing Claude Code MCP setup
            # For now, return a placeholder
            return f"Claude response to: {user_input}"
        except Exception as e:
            self.logger.error(f"Claude response generation error: {e}")
            return None
            
    async def _speak_response(self, text: str):
        """Convert text to speech using TTS manager"""
        try:
            # Select TTS model based on quality mode
            tts_model = self._select_tts_model()
            
            # Generate speech
            await self.tts_manager.speak(text, model=tts_model)
        except Exception as e:
            self.logger.error(f"TTS generation error: {e}")
            
    def _select_tts_model(self) -> str:
        """Select TTS model based on quality mode"""
        if self.config.quality_mode == QualityMode.HIGH_QUALITY:
            return "orpheus_3b"
        elif self.config.quality_mode == QualityMode.BALANCED:
            return "orpheus_3b"
        elif self.config.quality_mode == QualityMode.HIGH_SPEED:
            return "piper"
        else:  # ULTRA_FAST
            return "piper"
            
    async def stop_conversation(self):
        """Stop the voice conversation session"""
        self.logger.info("Stopping voice conversation session")
        self.conversation_active = False
        self.is_listening = False
        
        # Save metrics
        await self._save_metrics()
        
    async def _save_metrics(self):
        """Save performance metrics to file"""
        metrics_data = {
            'timestamp': time.time(),
            'config': asdict(self.config),
            'metrics': self.metrics
        }
        
        with open('voice_metrics.json', 'w') as f:
            json.dump(metrics_data, f, indent=2)
            
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'conversation_active': self.conversation_active,
            'is_listening': self.is_listening,
            'is_processing': self.is_processing,
            'stt_status': self.stt_manager.get_status(),
            'tts_status': self.tts_manager.get_status(),
            'ollama_status': self.ollama_client.get_status(),
            'health_status': self.health_monitor.get_status(),
            'metrics': {
                'avg_stt_latency': sum(self.metrics['stt_latency']) / len(self.metrics['stt_latency']) if self.metrics['stt_latency'] else 0,
                'avg_tts_latency': sum(self.metrics['tts_latency']) / len(self.metrics['tts_latency']) if self.metrics['tts_latency'] else 0,
                'avg_llm_latency': sum(self.metrics['llm_latency']) / len(self.metrics['llm_latency']) if self.metrics['llm_latency'] else 0,
                'avg_total_latency': sum(self.metrics['total_latency']) / len(self.metrics['total_latency']) if self.metrics['total_latency'] else 0,
                'success_rate': self.metrics['success_count'] / (self.metrics['success_count'] + self.metrics['error_count']) if (self.metrics['success_count'] + self.metrics['error_count']) > 0 else 0
            }
        }
        
    async def update_config(self, new_config: Dict[str, Any]):
        """Update configuration dynamically.

        The incoming dictionary may contain any top‑level sections ("voice",
        "stt", "memory" etc).  We merge it with the existing configuration and
        then propagate changes to each subsystem.
        """
        # merge into existing configuration
        merged = self.config_manager._merge_configs(self.config_manager.config, new_config)
        self.config_manager.config = merged
        self.config_manager.save_config()

        # refresh local views of the configuration
        self.config_dict = self.config_manager.config
        self.config = self._create_voice_config(self.config_dict)

        # propagate to subsystems
        await self.stt_manager.update_config(self.config_dict.get('stt', {}))
        await self.tts_manager.update_config(self.config_dict.get('tts', {}))
        await self.ollama_client.update_config(self.config_dict.get('ollama', {}))

        # memory configuration (update based on merged settings)
        if 'memory' in new_config:
            mem_section = self.config_dict.get('memory', {})
            if self.memory_bank:
                # apply any updated parameters locally
                # reload_config may still be useful for external changes
                self.memory_bank.reload_config()
                self.memory_bank.max_memories = mem_section.get('max_memories', self.memory_bank.max_memories)
                self.memory_bank.ttl_default = mem_section.get('ttl_default', self.memory_bank.ttl_default)
                self.memory_bank.semantic_search_enabled = mem_section.get('semantic_search', self.memory_bank.semantic_search_enabled)
                new_model = mem_section.get('embedding_model')
                if new_model and new_model != self.memory_bank.embedding_model_name:
                    self.memory_bank.embedding_model_name = new_model
                    self.memory_bank._load_embeddings_model()
                # toggle enabled flag
                self.memory_bank.enabled = mem_section.get('enabled', self.memory_bank.enabled)
                self.logger.debug(f"memory_bank.enabled after update = {self.memory_bank.enabled}")
                if not self.memory_bank.enabled:
                    self.memory_bank = None
                    self.memory_enabled = False
            else:
                if mem_section.get('enabled'):
                    self.memory_bank = get_memory_bank()
                    self.memory_enabled = True
        
    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up voice orchestrator resources")
        self.stt_manager.cleanup()
        self.tts_manager.cleanup()
        self.ollama_client.cleanup()
        self.health_monitor.cleanup()
        # NOTE: Do not close memory_bank here - it's a global singleton shared across processes
        # Individual memory operations will close their connections; the global instance remains available

async def main():
    """Main entry point for voice orchestrator"""
    orchestrator = VoiceOrchestrator()
    
    try:
        # Start health monitoring
        await orchestrator.health_monitor.start_monitoring()
        
        # Start conversation
        await orchestrator.start_conversation()
        
    except KeyboardInterrupt:
        print("\nShutting down voice orchestrator...")
    finally:
        orchestrator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())