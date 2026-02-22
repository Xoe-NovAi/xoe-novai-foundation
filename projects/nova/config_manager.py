#!/usr/bin/env python3
"""
Configuration Manager - Hierarchical configuration system
Handles environment-based overrides and model-specific settings
"""

import json
import os
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from typing import List
import yaml

class ConfigManager:
    """Configuration manager with hierarchical override support"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_path = config_path or self._get_default_config_path()
        self.config = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.load_config()
        
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        # Check for environment variable first
        env_config = os.getenv('VOICE_CONFIG_PATH')
        if env_config:
            return env_config
            
        # Check current directory
        current_dir_config = os.path.join(os.getcwd(), 'voice_config.json')
        if os.path.exists(current_dir_config):
            return current_dir_config
            
        # Check user home directory
        home_config = os.path.expanduser('~/.voice_config.json')
        if os.path.exists(home_config):
            return home_config
            
        # Default to current directory
        return current_dir_config
        
    def load_config(self):
        """Load configuration from file with environment overrides"""
        try:
            # Load base configuration
            base_config = self._load_base_config()
            
            # Apply environment overrides
            env_overrides = self._get_environment_overrides()
            
            # Merge configurations
            self.config = self._merge_configs(base_config, env_overrides)
            
            self.logger.info(f"Configuration loaded from: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Configuration loading failed: {e}")
            self.config = self._get_default_config()
            
    def _load_base_config(self) -> Dict[str, Any]:
        """Load base configuration from file"""
        if not os.path.exists(self.config_path):
            # Create default config file
            default_config = self._get_default_config()
            self.save_config(default_config)
            return default_config
            
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    return yaml.safe_load(f) or {}
                else:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config file: {e}")
            return self._get_default_config()
            
    def _get_environment_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables"""
        overrides = {}
        
        # STT configuration overrides
        stt_overrides = {}
        if os.getenv('STT_MODEL'):
            stt_overrides['model'] = os.getenv('STT_MODEL')
        if os.getenv('STT_CONFIDENCE_THRESHOLD'):
            stt_overrides['confidence_threshold'] = float(os.getenv('STT_CONFIDENCE_THRESHOLD'))
        if os.getenv('STT_LANGUAGE'):
            stt_overrides['language'] = os.getenv('STT_LANGUAGE')
            
        if stt_overrides:
            overrides['stt'] = stt_overrides
            
        # TTS configuration overrides
        tts_overrides = {}
        if os.getenv('TTS_MODEL'):
            tts_overrides['model'] = os.getenv('TTS_MODEL')
        if os.getenv('TTS_VOICE'):
            tts_overrides['voice'] = os.getenv('TTS_VOICE')
        if os.getenv('TTS_SPEED'):
            tts_overrides['speed'] = float(os.getenv('TTS_SPEED'))
        if os.getenv('TTS_PITCH'):
            tts_overrides['pitch'] = float(os.getenv('TTS_PITCH'))
        if os.getenv('TTS_VOLUME'):
            tts_overrides['volume'] = float(os.getenv('TTS_VOLUME'))
            
        if tts_overrides:
            overrides['tts'] = tts_overrides
            
        # Ollama configuration overrides
        ollama_overrides = {}
        if os.getenv('OLLAMA_HOST'):
            ollama_overrides['host'] = os.getenv('OLLAMA_HOST')
        if os.getenv('OLLAMA_PORT'):
            ollama_overrides['port'] = int(os.getenv('OLLAMA_PORT'))
        if os.getenv('OLLAMA_MODEL'):
            ollama_overrides['model'] = os.getenv('OLLAMA_MODEL')
        if os.getenv('OLLAMA_TIMEOUT'):
            ollama_overrides['timeout'] = int(os.getenv('OLLAMA_TIMEOUT'))
            
        if ollama_overrides:
            overrides['ollama'] = ollama_overrides
            
        # Voice orchestrator overrides
        voice_overrides = {}
        if os.getenv('LLM_MODE'):
            voice_overrides['llm_mode'] = os.getenv('LLM_MODE')
        if os.getenv('QUALITY_MODE'):
            voice_overrides['quality_mode'] = os.getenv('QUALITY_MODE')
        if os.getenv('MAX_CONCURRENT_REQUESTS'):
            voice_overrides['max_concurrent_requests'] = int(os.getenv('MAX_CONCURRENT_REQUESTS'))
            
        if voice_overrides:
            overrides['voice'] = voice_overrides
            
        return overrides
        
    def _merge_configs(self, base_config: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge base configuration with overrides"""
        result = base_config.copy()
        
        for key, value in overrides.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "voice": {
                "llm_mode": "auto",
                "quality_mode": "balanced",
                "stt_model": "canary_qwen_2.5b",
                "tts_model": "orpheus_3b",
                "ollama_model": "llama3.2",
                "fallback_timeout": 5.0,
                "max_concurrent_requests": 3,
                "enable_voice_cloning": False
            },
            "stt": {
                "model": "canary_qwen_2.5b",
                "confidence_threshold": 0.8,
                "max_audio_duration": 30.0,
                "silence_timeout": 2.0,
                "enable_vad": True,
                "vad_aggressiveness": 2,
                "language": "en",
                "fallback_models": ["whisper_large_v3_turbo", "piper"]
            },
            "tts": {
                "model": "orpheus_3b",
                "voice": "default",
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0,
                "emotion": "neutral",
                "enable_voice_cloning": False,
                "max_text_length": 2000,
                "streaming_enabled": True,
                "fallback_models": ["xtts_v2", "piper", "kokoro"]
            },
            "ollama": {
                "host": "localhost",
                "port": 11434,
                "model": "llama3.2",
                "timeout": 120,
                "max_tokens": 2000,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": True,
                "enable_context": True,
                "context_size": 10,
                "fallback_models": ["llama3.1", "mistral", "gemma2"]
            },
            "audio": {
                "sample_rate": 16000,
                "channels": 1,
                "format": "wav",
                "buffer_size": 1024,
                "vad_threshold": 0.5,
                "noise_gate": True,
                "echo_cancellation": True
            },
            "monitoring": {
                "enabled": True,
                "metrics_interval": 30,
                "health_check_interval": 10,
                "log_level": "INFO",
                "enable_performance_logging": True
            },
            "security": {
                "enable_authentication": False,
                "api_key": None,
                "allowed_ips": ["127.0.0.1", "::1"],
                "rate_limit": 100
            },
            "memory": {
                "enabled": True,
                "max_memories": 10000,
                "ttl_default": 86400,
                "semantic_search": True,
                "embedding_model": "all-MiniLM-L6-v2",
                "storage_subdir": "memory"
            }
        }
        
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        try:
            config_to_save = config or self.config
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    yaml.dump(config_to_save, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_to_save, f, indent=2)
                    
            self.logger.info(f"Configuration saved to: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Configuration save failed: {e}")
            
    def get_section(self, section_name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a specific configuration section"""
        return self.config.get(section_name, default or {})
        
    def update_section(self, section_name: str, updates: Dict[str, Any]):
        """Update a specific configuration section"""
        if section_name not in self.config:
            self.config[section_name] = {}
            
        self.config[section_name].update(updates)
        self.save_config()
        
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'stt.model')"""
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                value = value[key]
                
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config_ref = self.config
        
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
            
        config_ref[keys[-1]] = value
        self.save_config()
        
    def reload(self):
        """Reload configuration from file"""
        self.load_config()
        
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        default_config = self._get_default_config()
        self.config = default_config
        self.save_config()
        
    def validate_config(self) -> bool:
        """Validate configuration structure"""
        required_sections = ['voice', 'stt', 'tts', 'ollama', 'audio', 'monitoring', 'security']
        
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"Missing required configuration section: {section}")
                return False
        
        # memory is optional; if present it should be a dict
        if 'memory' in self.config and not isinstance(self.config['memory'], dict):
            self.logger.error("Malformed memory configuration section")
            return False
                
        # Validate specific values
        if self.config['stt']['confidence_threshold'] < 0 or self.config['stt']['confidence_threshold'] > 1:
            self.logger.error("STT confidence threshold must be between 0 and 1")
            return False
            
        if self.config['tts']['speed'] <= 0:
            self.logger.error("TTS speed must be positive")
            return False
            
        if self.config['ollama']['port'] < 1 or self.config['ollama']['port'] > 65535:
            self.logger.error("Ollama port must be between 1 and 65535")
            return False
            
        return True
        
    def get_config_path(self) -> str:
        """Get current configuration file path"""
        return self.config_path

def get_config() -> Dict[str, Any]:
    """Get global configuration"""
    config_manager = ConfigManager()
    return config_manager.config

def list_available_configs() -> List[str]:
    """List available configuration files"""
    config_files = []
    
    # Check current directory
    current_dir = os.getcwd()
    for filename in ['voice_config.json', 'voice_config.yaml', 'voice_config.yml']:
        filepath = os.path.join(current_dir, filename)
        if os.path.exists(filepath):
            config_files.append(filepath)
    
    # Check home directory
    home_dir = os.path.expanduser('~')
    for filename in ['.voice_config.json', '.voice_config.yaml', '.voice_config.yml']:
        filepath = os.path.join(home_dir, filename)
        if os.path.exists(filepath):
            config_files.append(filepath)
    
    return config_files
