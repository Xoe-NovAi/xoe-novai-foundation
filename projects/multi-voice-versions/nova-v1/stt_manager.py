#!/usr/bin/env python3
"""
STT Manager - Speech-to-Text service manager
Handles Canary Qwen 2.5B and Whisper Large V3 Turbo integration
"""

import asyncio
import logging
import time
import json
import os
import subprocess
import requests
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

class STTModel(Enum):
    """Available STT models"""
    CANARY_QWEN_2_5B = "canary_qwen_2.5b"
    WHISPER_LARGE_V3_TURBO = "whisper_large_v3_turbo"
    WHISPER_LARGE_V3 = "whisper_large_v3"
    PIPER = "piper"

@dataclass
class STTConfig:
    """STT configuration"""
    model: str = "canary_qwen_2.5b"
    confidence_threshold: float = 0.8
    max_audio_duration: float = 30.0
    silence_timeout: float = 2.0
    enable_vad: bool = True
    vad_aggressiveness: int = 2
    language: str = "en"
    fallback_models: List[str] = None
    
    def __post_init__(self):
        if self.fallback_models is None:
            self.fallback_models = ["whisper_large_v3_turbo", "piper"]

class STTManager:
    """Speech-to-Text service manager"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize STT manager"""
        self.config_manager = ConfigManager()
        self.config = self._load_config(config)
        
        # Service endpoints
        self.services = {
            STTModel.CANARY_QWEN_2_5B: {
                'url': 'http://localhost:2022/v1/audio/transcriptions',
                'port': 2022,
                'model': 'canary-qwen-2.5b'
            },
            STTModel.WHISPER_LARGE_V3_TURBO: {
                'url': 'http://localhost:2023/v1/audio/transcriptions',
                'port': 2023,
                'model': 'whisper-large-v3-turbo'
            },
            STTModel.WHISPER_LARGE_V3: {
                'url': 'http://localhost:2024/v1/audio/transcriptions',
                'port': 2024,
                'model': 'whisper-large-v3'
            },
            STTModel.PIPER: {
                'url': 'http://localhost:2025/v1/audio/transcriptions',
                'port': 2025,
                'model': 'piper'
            }
        }
        
        # State management
        self.is_initialized = False
        self.active_model = None
        self.service_health = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config: Optional[Dict[str, Any]]) -> STTConfig:
        """Load STT configuration"""
        if config:
            return STTConfig(**config)
        else:
            # Load from config manager or use defaults
            stt_config = self.config_manager.get_section('stt', {})
            return STTConfig(**stt_config)
            
    async def initialize(self):
        """Initialize STT services"""
        self.logger.info("Initializing STT services...")
        
        try:
            # Check service availability
            for model_name, service_info in self.services.items():
                if await self._check_service_health(service_info['url']):
                    self.service_health[model_name] = ServiceStatus.HEALTHY
                    self.logger.info(f"STT service {model_name} is available")
                else:
                    self.service_health[model_name] = ServiceStatus.UNHEALTHY
                    self.logger.warning(f"STT service {model_name} is not available")
            
            # Set active model
            self.active_model = self._select_best_model()
            self.is_initialized = True
            
            self.logger.info(f"STT manager initialized with active model: {self.active_model}")
            
        except Exception as e:
            self.logger.error(f"STT initialization failed: {e}")
            self.is_initialized = False
            
    def _select_best_model(self) -> Optional[STTModel]:
        """Select the best available model based on configuration"""
        preferred_model = STTModel(self.config.model)
        
        # Check if preferred model is available
        if self.service_health.get(preferred_model) == ServiceStatus.HEALTHY:
            return preferred_model
            
        # Try fallback models
        for fallback_model_name in self.config.fallback_models:
            try:
                fallback_model = STTModel(fallback_model_name)
            except ValueError:
                self.logger.warning(f"Unknown fallback STT model '{fallback_model_name}' - skipping")
                continue
            if self.service_health.get(fallback_model) == ServiceStatus.HEALTHY:
                self.logger.info(f"Using fallback model: {fallback_model}")
                return fallback_model
                
        self.logger.error("No STT models are available")
        return None
        
    async def _check_service_health(self, url: str) -> bool:
        """Check if STT service is healthy"""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
            
    async def transcribe(self, audio_data: Union[bytes, np.ndarray, str]) -> Optional[str]:
        """Transcribe audio to text"""
        if not self.is_initialized or not self.active_model:
            self.logger.error("STT manager not initialized or no active model")
            return None
            
        start_time = time.time()
        
        try:
            # Prepare audio data
            audio_file_path = await self._prepare_audio_data(audio_data)
            if not audio_file_path:
                return None
                
            # Transcribe using active model
            transcript = await self._transcribe_with_model(self.active_model, audio_file_path)
            
            if transcript:
                # Validate confidence if available
                if self._validate_confidence(transcript):
                    latency = time.time() - start_time
                    self.logger.info(f"STT transcription successful in {latency:.2f}s")
                    return transcript
                else:
                    self.logger.warning("STT confidence below threshold, trying fallback")
                    
            # Try fallback models
            return await self._try_fallback_transcription(audio_file_path, start_time)
            
        except Exception as e:
            self.logger.error(f"STT transcription error: {e}")
            return None
        finally:
            # Cleanup temporary audio file
            if isinstance(audio_data, str) and audio_data.startswith('/tmp/'):
                try:
                    os.unlink(audio_data)
                except:
                    pass
                    
    async def _prepare_audio_data(self, audio_data: Union[bytes, np.ndarray, str]) -> Optional[str]:
        """Prepare audio data for transcription"""
        try:
            if isinstance(audio_data, str):
                # Already a file path
                return audio_data
            elif isinstance(audio_data, bytes):
                # Raw audio bytes
                return await self._save_audio_bytes(audio_data)
            elif isinstance(audio_data, np.ndarray):
                # NumPy array
                return await self._save_audio_array(audio_data)
            else:
                self.logger.error("Unsupported audio data type")
                return None
        except Exception as e:
            self.logger.error(f"Audio preparation error: {e}")
            return None
            
    async def _save_audio_bytes(self, audio_bytes: bytes) -> str:
        """Save audio bytes to temporary file"""
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file.write(audio_bytes)
        temp_file.close()
        return temp_file.name
        
    async def _save_audio_array(self, audio_array: np.ndarray) -> str:
        """Save audio array to temporary file"""
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        sf.write(temp_file.name, audio_array, 16000)
        temp_file.close()
        return temp_file.name
        
    async def _transcribe_with_model(self, model: STTModel, audio_file: str) -> Optional[str]:
        """Transcribe audio using specific model"""
        service_info = self.services[model]
        
        try:
            # Prepare request
            files = {'file': open(audio_file, 'rb')}
            data = {
                'model': service_info['model'],
                'language': self.config.language,
                'response_format': 'json'
            }
            
            # Send request
            response = requests.post(
                service_info['url'],
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('text', '')
            else:
                self.logger.error(f"STT service error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"STT model {model} error: {e}")
            return None
        finally:
            if 'files' in locals():
                files['file'].close()
                
    def _validate_confidence(self, transcript: str) -> bool:
        """Validate transcription confidence"""
        # Simple length-based validation for now
        # In a real implementation, this would check model-specific confidence scores
        if len(transcript.strip()) < 3:
            return False
        return True
        
    async def _try_fallback_transcription(self, audio_file: str, start_time: float) -> Optional[str]:
        """Try transcription with fallback models"""
        for fallback_model_name in self.config.fallback_models:
            try:
                fallback_model = STTModel(fallback_model_name)
            except ValueError:
                self.logger.warning(f"Skipping invalid fallback model '{fallback_model_name}'")
                continue
            
            if self.service_health.get(fallback_model) != ServiceStatus.HEALTHY:
                continue
            
            try:
                transcript = await self._transcribe_with_model(fallback_model, audio_file)
                if transcript and self._validate_confidence(transcript):
                    latency = time.time() - start_time
                    self.logger.info(f"STT fallback successful with {fallback_model} in {latency:.2f}s")
                    return transcript
            except Exception as e:
                self.logger.error(f"Fallback STT model {fallback_model} error: {e}")
                
        self.logger.error("All STT models failed")
        return None
        
    def get_status(self) -> Dict[str, Any]:
        """Get STT service status"""
        return {
            'initialized': self.is_initialized,
            'active_model': self.active_model.value if self.active_model else None,
            'service_health': {k.value: v.value for k, v in self.service_health.items()},
            'config': {
                'model': self.config.model,
                'confidence_threshold': self.config.confidence_threshold,
                'max_audio_duration': self.config.max_audio_duration,
                'language': self.config.language
            }
        }
        
    async def update_config(self, new_config: Dict[str, Any]):
        """Update STT configuration"""
        self.config = STTConfig(**{**self.config.__dict__, **new_config})
        self.config_manager.update_section('stt', new_config)
        
        # Re-select best model if configuration changed
        if 'model' in new_config or 'fallback_models' in new_config:
            old_model = self.active_model
            self.active_model = self._select_best_model()
            if self.active_model != old_model:
                self.logger.info(f"STT model changed from {old_model} to {self.active_model}")
                
    def cleanup(self):
        """Cleanup STT resources"""
        self.logger.info("Cleaning up STT manager resources")
        # Cleanup any temporary files or connections