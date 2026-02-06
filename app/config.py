"""Xoe-NovAi Configuration Module"""
import os
import toml
from pathlib import Path
from typing import Any, Dict, Optional

class Config:
    """Configuration class that loads settings from config.toml"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.toml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        self._config = toml.load(config_path)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'models.llm_path')"""
        parts = key.split('.')
        value = self._config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self._config.get(section, {})
    
    def __getitem__(self, key: str) -> Any:
        return self.get(key)
    
    def __getattr__(self, key: str) -> Any:
        return self.get(key)

# Global config instance
config = Config()

# Convenience functions for common settings
def get_llm_path() -> str:
    return config.get('models.llm_path', '/models/local/all/ruvltra-claude-code-0.5b-q4_k_m.gguf')

def get_embedding_path() -> str:
    return config.get('models.embedding_path', '/embeddings/all-MiniLM-L12-v2.Q8_0.gguf')

def get_redis_config() -> Dict[str, Any]:
    return config.get_section('redis')

def get_server_config() -> Dict[str, Any]:
    return config.get_section('server')

def get_voice_config() -> Dict[str, Any]:
    return config.get_section('voice')