#!/usr/bin/env python3
"""
TTS Manager - Text-to-Speech service manager
Handles Orpheus TTS 3B, XTTS v2, and Piper integration
"""

import asyncio
import logging
import time
import json
import os
import subprocess
import requests
import tempfile
import threading
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
import soundfile as sf
from pathlib import Path

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from health_monitor import ServiceStatus

class TTSModel(Enum):
    """Available TTS models"""
    ORPHEUS_3B = "orpheus_3b"
    XTTS_V2 = "xtts_v2"
    PIPER = "piper"
    KOKORO = "kokoro"

@dataclass
class TTSConfig:
    """TTS configuration"""
    model: str = "orpheus_3b"
    voice: str = "default"
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0
    emotion: str = "neutral"
    enable_voice_cloning: bool = False
    voice_clone_sample_path: Optional[str] = None
    max_text_length: int = 2000
    streaming_enabled: bool = True
    fallback_models: List[str] = None
    
    def __post_init__(self):
        if self.fallback_models is None:
            self.fallback_models = ["xtts_v2", "piper", "kokoro"]

class TTSManager:
    """Text-to-Speech service manager"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize TTS manager"""
        self.config_manager = ConfigManager()
        self.config = self._load_config(config)
        
        # Service endpoints
        self.services = {
            TTSModel.ORPHEUS_3B: {
                'url': 'http://localhost:8881/v1/audio/speech',
                'port': 8881,
                'model': 'orpheus-tts-3b'
            },
            TTSModel.XTTS_V2: {
                'url': 'http://localhost:8882/v1/audio/speech',
                'port': 8882,
                'model': 'xtts-v2'
            },
            TTSModel.PIPER: {
                'url': 'http://localhost:8883/v1/audio/speech',
                'port': 8883,
                'model': 'piper'
            },
            TTSModel.KOKORO: {
                'url': 'http://localhost:8880/v1/audio/speech',
                'port': 8880,
                'model': 'kokoro'
            }
        }
        
        # State management
        self.is_initialized = False
        self.active_model = None
        self.service_health = {}
        self.audio_player = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config: Optional[Dict[str, Any]]) -> TTSConfig:
        """Load TTS configuration"""
        if config:
            return TTSConfig(**config)
        else:
            # Load from config manager or use defaults
            tts_config = self.config_manager.get_section('tts', {})
            return TTSConfig(**tts_config)
            
    async def initialize(self):
        """Initialize TTS services"""
        self.logger.info("Initializing TTS services...")
        
        try:
            # Check service availability
            for model_name, service_info in self.services.items():
                if await self._check_service_health(service_info['url']):
                    self.service_health[model_name] = ServiceStatus.HEALTHY
                    self.logger.info(f"TTS service {model_name} is available")
                else:
                    self.service_health[model_name] = ServiceStatus.UNHEALTHY
                    self.logger.warning(f"TTS service {model_name} is not available")
            
            # Set active model
            self.active_model = self._select_best_model()
            self.is_initialized = True
            
            self.logger.info(f"TTS manager initialized with active model: {self.active_model}")
            
        except Exception as e:
            self.logger.error(f"TTS initialization failed: {e}")
            self.is_initialized = False
            
    def _select_best_model(self) -> Optional[TTSModel]:
        """Select the best available model based on configuration"""
        preferred_model = TTSModel(self.config.model)
        
        # Check if preferred model is available
        if self.service_health.get(preferred_model) == ServiceStatus.HEALTHY:
            return preferred_model
            
        # Try fallback models
        for fallback_model_name in self.config.fallback_models:
            fallback_model = TTSModel(fallback_model_name)
            if self.service_health.get(fallback_model) == ServiceStatus.HEALTHY:
                self.logger.info(f"Using fallback model: {fallback_model}")
                return fallback_model
                
        self.logger.error("No TTS models are available")
        return None
        
    async def _check_service_health(self, url: str) -> bool:
        """Check if TTS service is healthy"""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
            
    async def speak(self, text: str, model: Optional[str] = None, voice: Optional[str] = None) -> bool:
        """Convert text to speech and play audio"""
        if not self.is_initialized or not self.active_model:
            self.logger.error("TTS manager not initialized or no active model")
            return False
            
        # Use specified model or fall back to active model
        target_model = TTSModel(model) if model else self.active_model
        target_voice = voice or self.config.voice
        
        start_time = time.time()
        
        try:
            # Generate speech
            audio_data = await self._generate_speech(text, target_model, target_voice)
            if not audio_data:
                return False
                
            # Play audio
            success = await self._play_audio(audio_data)
            
            latency = time.time() - start_time
            self.logger.info(f"TTS generation and playback successful in {latency:.2f}s")
            
            return success
            
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            return False
            
    async def _generate_speech(self, text: str, model: TTSModel, voice: str) -> Optional[bytes]:
        """Generate speech using specific model"""
        service_info = self.services[model]
        
        try:
            # Prepare request data
            data = {
                'model': service_info['model'],
                'input': text,
                'voice': voice,
                'speed': self.config.speed,
                'pitch': self.config.pitch,
                'volume': self.config.volume,
                'emotion': self.config.emotion,
                'stream': self.config.streaming_enabled
            }
            
            # Add voice cloning parameters if enabled
            if self.config.enable_voice_cloning and self.config.voice_clone_sample_path:
                data['voice_clone_sample'] = self.config.voice_clone_sample_path
                
            # Send request
            response = requests.post(
                service_info['url'],
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.content
            else:
                self.logger.error(f"TTS service error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"TTS model {model} error: {e}")
            return None
            
    async def _play_audio(self, audio_data: bytes) -> bool:
        """Play audio data"""
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
                
            # Play audio using system player
            return await self._play_audio_file(temp_file_path)
            
        except Exception as e:
            self.logger.error(f"Audio playback error: {e}")
            return False
        finally:
            # Cleanup temporary file
            try:
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)
            except:
                pass
                
    async def _play_audio_file(self, file_path: str) -> bool:
        """Play audio file using system player"""
        try:
            # Use different players based on platform
            import platform
            system = platform.system()
            
            if system == "Darwin":  # macOS
                subprocess.run(['afplay', file_path], check=True)
            elif system == "Linux":
                subprocess.run(['aplay', file_path], check=True)
            elif system == "Windows":
                subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{file_path}").PlaySync();'], check=True)
            else:
                self.logger.warning(f"Unknown platform {system}, trying to play audio anyway")
                subprocess.run(['aplay', file_path], check=True)
                
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Audio player failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Audio playback error: {e}")
            return False
            
    async def generate_audio_file(self, text: str, output_path: str, model: Optional[str] = None) -> bool:
        """Generate speech and save to audio file"""
        if not self.is_initialized:
            self.logger.error("TTS manager not initialized")
            return False
            
        target_model = TTSModel(model) if model else self.active_model
        
        try:
            # Generate speech
            audio_data = await self._generate_speech(text, target_model, self.config.voice)
            if not audio_data:
                return False
                
            # Save to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
                
            self.logger.info(f"Audio file saved to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Audio file generation error: {e}")
            return False
            
    def get_status(self) -> Dict[str, Any]:
        """Get TTS service status"""
        return {
            'initialized': self.is_initialized,
            'active_model': self.active_model.value if self.active_model else None,
            'service_health': {k.value: v.value for k, v in self.service_health.items()},
            'config': {
                'model': self.config.model,
                'voice': self.config.voice,
                'speed': self.config.speed,
                'pitch': self.config.pitch,
                'volume': self.config.volume,
                'emotion': self.config.emotion,
                'enable_voice_cloning': self.config.enable_voice_cloning
            }
        }
        
    async def update_config(self, new_config: Dict[str, Any]):
        """Update TTS configuration"""
        self.config = TTSConfig(**{**self.config.__dict__, **new_config})
        self.config_manager.update_section('tts', new_config)
        
        # Re-select best model if configuration changed
        if 'model' in new_config or 'fallback_models' in new_config:
            old_model = self.active_model
            self.active_model = self._select_best_model()
            if self.active_model != old_model:
                self.logger.info(f"TTS model changed from {old_model} to {self.active_model}")
                
    def cleanup(self):
        """Cleanup TTS resources"""
        self.logger.info("Cleaning up TTS manager resources")
        # Cleanup any temporary files or connections