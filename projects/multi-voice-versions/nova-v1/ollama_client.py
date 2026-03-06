#!/usr/bin/env python3
"""
Ollama Client - Local LLM integration for voice setup
Handles communication with Ollama for local model inference
"""

import asyncio
import logging
import time
import json
import os
import requests
from typing import Optional, Dict, Any, List, Union, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import aiohttp

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from health_monitor import ServiceStatus

class OllamaModel(Enum):
    """Available Ollama models"""
    LLAMA3_2 = "llama3.2"
    LLAMA3_1 = "llama3.1"
    MISTRAL = "mistral"
    GEMMA2 = "gemma2"
    PHI3 = "phi3"
    CODELLAMA = "codellama"
    QWEN2_5 = "qwen2.5"

@dataclass
class OllamaConfig:
    """Ollama configuration"""
    host: str = "localhost"
    port: int = 11434
    model: str = "llama3.2"
    timeout: int = 120
    max_tokens: int = 2000
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = True
    enable_context: bool = True
    context_size: int = 10
    fallback_models: List[str] = None
    
    def __post_init__(self):
        if self.fallback_models is None:
            self.fallback_models = ["llama3.1", "mistral", "gemma2"]

class OllamaClient:
    """Ollama client for local LLM inference"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Ollama client"""
        self.config_manager = ConfigManager()
        self.config = self._load_config(config)
        
        # Service configuration
        self.base_url = f"http://{self.config.host}:{self.config.port}"
        self.api_endpoint = f"{self.base_url}/api/generate"
        
        # State management
        self.is_initialized = False
        self.is_available = False
        self.conversation_history = []
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config: Optional[Dict[str, Any]]) -> OllamaConfig:
        """Load Ollama configuration"""
        if config:
            return OllamaConfig(**config)
        else:
            # Load from config manager or use defaults
            ollama_config = self.config_manager.get_section('ollama', {})
            return OllamaConfig(**ollama_config)
            
    async def initialize(self):
        """Initialize Ollama client"""
        self.logger.info("Initializing Ollama client...")
        
        try:
            # Check if Ollama is running
            if await self._check_service_health():
                self.is_available = True
                self.logger.info("Ollama service is available")
                
                # Check if configured model is available
                if await self._check_model_available(self.config.model):
                    self.is_initialized = True
                    self.logger.info(f"Ollama initialized with model: {self.config.model}")
                else:
                    # Try fallback models
                    fallback_model = await self._select_fallback_model()
                    if fallback_model:
                        self.config.model = fallback_model
                        self.is_initialized = True
                        self.logger.info(f"Ollama initialized with fallback model: {fallback_model}")
                    else:
                        self.logger.error("No available models found")
                        self.is_initialized = False
            else:
                self.logger.warning("Ollama service is not available")
                self.is_available = False
                self.is_initialized = False
                
        except Exception as e:
            self.logger.error(f"Ollama initialization failed: {e}")
            self.is_initialized = False
            
    async def _check_service_health(self) -> bool:
        """Check if Ollama service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
            
    async def _check_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_tags = [model.get('name', '') for model in models]
                return model_name in model_tags
            return False
        except Exception as e:
            self.logger.error(f"Error checking model availability: {e}")
            return False
            
    async def _select_fallback_model(self) -> Optional[str]:
        """Select the best available fallback model"""
        for fallback_model in self.config.fallback_models:
            if await self._check_model_available(fallback_model):
                return fallback_model
        return None
        
    async def generate_response(self, prompt: str, model: Optional[str] = None) -> Optional[str]:
        """Generate response using Ollama"""
        if not self.is_initialized:
            self.logger.error("Ollama client not initialized")
            return None
            
        target_model = model or self.config.model
        start_time = time.time()
        
        try:
            # Prepare conversation context
            messages = self._prepare_conversation_context(prompt)
            
            # Generate response
            response = await self._send_request(messages, target_model)
            
            if response:
                # Update conversation history
                self._update_conversation_history(prompt, response)
                
                latency = time.time() - start_time
                self.logger.info(f"Ollama response generated in {latency:.2f}s")
                
                return response
            else:
                self.logger.error("Ollama response generation failed")
                return None
                
        except Exception as e:
            self.logger.error(f"Ollama response generation error: {e}")
            return None
            
    def _prepare_conversation_context(self, prompt: str) -> List[Dict[str, str]]:
        """Prepare conversation context for the model"""
        messages = []
        
        # Add system message
        messages.append({
            "role": "system",
            "content": "You are a helpful AI assistant. Provide concise, accurate responses to user queries."
        })
        
        # Add conversation history if enabled
        if self.config.enable_context and self.conversation_history:
            # Limit context size
            recent_history = self.conversation_history[-self.config.context_size:]
            messages.extend(recent_history)
            
        # Add current prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return messages
        
    async def _send_request(self, messages: List[Dict[str, str]], model: str) -> Optional[str]:
        """Send request to Ollama API"""
        try:
            # Prepare request data
            data = {
                "model": model,
                "messages": messages,
                "options": {
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "num_predict": self.config.max_tokens
                },
                "stream": self.config.stream
            }
            
            # Send request
            if self.config.stream:
                return await self._send_streaming_request(data)
            else:
                return await self._send_non_streaming_request(data)
                
        except Exception as e:
            self.logger.error(f"Ollama API request error: {e}")
            return None
            
    async def _send_non_streaming_request(self, data: Dict[str, Any]) -> Optional[str]:
        """Send non-streaming request to Ollama"""
        try:
            response = requests.post(
                self.api_endpoint,
                json=data,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', '')
            else:
                self.logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Ollama non-streaming request error: {e}")
            return None
            
    async def _send_streaming_request(self, data: Dict[str, Any]) -> Optional[str]:
        """Send streaming request to Ollama"""
        try:
            full_response = ""
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_endpoint,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    
                    if response.status == 200:
                        async for line in response.content:
                            if line:
                                line_str = line.decode('utf-8').strip()
                                if line_str:
                                    try:
                                        json_data = json.loads(line_str)
                                        if 'message' in json_data:
                                            content = json_data['message'].get('content', '')
                                            if content:
                                                full_response += content
                                    except json.JSONDecodeError:
                                        continue
                    else:
                        self.logger.error(f"Ollama streaming API error: {response.status}")
                        return None
                        
            return full_response if full_response else None
            
        except Exception as e:
            self.logger.error(f"Ollama streaming request error: {e}")
            return None
            
    def _update_conversation_history(self, prompt: str, response: str):
        """Update conversation history"""
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Add assistant response
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Limit history size
        if len(self.conversation_history) > self.config.context_size * 2:
            # Keep only the most recent conversations
            self.conversation_history = self.conversation_history[-self.config.context_size * 2:]
            
    async def list_available_models(self) -> List[str]:
        """List all available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model.get('name', '') for model in models]
            return []
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []
            
    async def download_model(self, model_name: str) -> bool:
        """Download a model"""
        try:
            self.logger.info(f"Downloading model: {model_name}")
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300  # 5 minutes timeout for download
            )
            
            if response.status_code == 200:
                self.logger.info(f"Model {model_name} downloaded successfully")
                return True
            else:
                self.logger.error(f"Model download failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Model download error: {e}")
            return False
            
    def get_status(self) -> Dict[str, Any]:
        """Get Ollama client status"""
        return {
            'initialized': self.is_initialized,
            'available': self.is_available,
            'model': self.config.model,
            'conversation_history_length': len(self.conversation_history),
            'config': {
                'host': self.config.host,
                'port': self.config.port,
                'timeout': self.config.timeout,
                'max_tokens': self.config.max_tokens,
                'temperature': self.config.temperature,
                'stream': self.config.stream,
                'enable_context': self.config.enable_context
            }
        }
        
    async def update_config(self, new_config: Dict[str, Any]):
        """Update Ollama configuration"""
        self.config = OllamaConfig(**{**self.config.__dict__, **new_config})
        self.config_manager.update_section('ollama', new_config)
        
        # Update API endpoint if host/port changed
        if 'host' in new_config or 'port' in new_config:
            self.base_url = f"http://{self.config.host}:{self.config.port}"
            self.api_endpoint = f"{self.base_url}/api/generate"
            
        # Re-initialize if model changed
        if 'model' in new_config:
            await self.initialize()
            
    def cleanup(self):
        """Cleanup Ollama client resources"""
        self.logger.info("Cleaning up Ollama client resources")
        self.conversation_history.clear()