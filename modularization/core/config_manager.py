"""
Configuration Management for OpenCode Multi-Account System
=========================================================

Handles configuration loading, validation, and management across
different environments and deployment scenarios.
"""

import os
import json
import yaml
import logging
import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
import hashlib
import secrets
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


@dataclass
class ConfigSchema:
    """Configuration schema definition."""
    required_fields: List[str] = field(default_factory=list)
    optional_fields: Dict[str, Any] = field(default_factory=dict)
    field_types: Dict[str, type] = field(default_factory=dict)
    field_validators: Dict[str, callable] = field(default_factory=dict)


class ConfigurationError(Exception):
    """Configuration-related exceptions."""
    pass


class ConfigurationManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self._secrets: Dict[str, str] = {}
        self._encryption_key: Optional[bytes] = None
        self._loaded = False
        
        # Configuration schemas
        self._schemas = self._define_schemas()
    
    async def load_config(self) -> Dict[str, Any]:
        """Load and validate configuration."""
        if self._loaded:
            return self.config
        
        try:
            # Load base configuration
            self.config = await self._load_base_config()
            
            # Load environment-specific overrides
            env_config = await self._load_environment_config()
            self.config = self._merge_configs(self.config, env_config)
            
            # Load secrets
            await self._load_secrets()
            
            # Validate configuration
            await self._validate_config()
            
            # Apply defaults
            self._apply_defaults()
            
            # Encrypt sensitive data
            await self._encrypt_secrets()
            
            self._loaded = True
            logger.info("Configuration loaded successfully")
            
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigurationError(f"Configuration loading failed: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support."""
        if not self._loaded:
            raise ConfigurationError("Configuration not loaded")
        
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value with dot notation support."""
        if not self._loaded:
            raise ConfigurationError("Configuration not loaded")
        
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.debug(f"Set configuration: {key} = {value}")
    
    def reload(self) -> None:
        """Reload configuration from files."""
        self._loaded = False
        self.config = {}
        self._secrets = {}
    
    async def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to file."""
        config_to_save = config or self.config
        
        # Create backup
        await self._create_backup()
        
        # Save configuration
        config_file = Path(self.config_path) / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            yaml.dump(config_to_save, f, default_flow_style=False, indent=2)
        
        logger.info(f"Configuration saved to {config_file}")
    
    async def save_secrets(self, secrets: Optional[Dict[str, str]] = None) -> None:
        """Save secrets to encrypted file."""
        secrets_to_save = secrets or self._secrets
        
        secrets_file = Path(self.config_path) / "secrets.enc"
        secrets_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Encrypt secrets
        encrypted_secrets = await self._encrypt_secrets_data(secrets_to_save)
        
        with open(secrets_file, 'wb') as f:
            f.write(encrypted_secrets)
        
        logger.info(f"Secrets saved to {secrets_file}")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret value."""
        return self._secrets.get(key, default)
    
    def set_secret(self, key: str, value: str) -> None:
        """Set secret value."""
        self._secrets[key] = value
        logger.debug(f"Set secret: {key}")
    
    async def initialize_config(self, environment: str = "development") -> None:
        """Initialize configuration with default values."""
        default_config = self._get_default_config(environment)
        
        # Save default configuration
        await self.save_config(default_config)
        
        # Initialize secrets file
        await self.save_secrets({})
        
        logger.info(f"Configuration initialized for {environment} environment")
    
    def _get_default_config_path(self) -> str:
        """Get default configuration path."""
        # Check environment variable
        env_path = os.getenv('OPENCODE_CONFIG_PATH')
        if env_path:
            return env_path
        
        # Check home directory
        home = Path.home()
        config_dir = home / ".config" / "opencode-multi-account"
        
        return str(config_dir)
    
    async def _load_base_config(self) -> Dict[str, Any]:
        """Load base configuration from file."""
        config_file = Path(self.config_path) / "config.yaml"
        
        if not config_file.exists():
            logger.warning(f"Configuration file not found: {config_file}")
            return {}
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        logger.debug(f"Loaded base configuration from {config_file}")
        return config
    
    async def _load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration."""
        env = os.getenv('OPENCODE_ENV', 'development')
        env_file = Path(self.config_path) / f"config.{env}.yaml"
        
        if not env_file.exists():
            logger.debug(f"Environment config not found: {env_file}")
            return {}
        
        with open(env_file, 'r') as f:
            env_config = yaml.safe_load(f) or {}
        
        logger.debug(f"Loaded environment configuration from {env_file}")
        return env_config
    
    def _merge_configs(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    async def _load_secrets(self) -> None:
        """Load and decrypt secrets."""
        secrets_file = Path(self.config_path) / "secrets.enc"
        
        if not secrets_file.exists():
            logger.debug("No secrets file found")
            return
        
        try:
            with open(secrets_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt secrets
            decrypted_data = await self._decrypt_secrets_data(encrypted_data)
            self._secrets = json.loads(decrypted_data.decode())
            
            logger.debug("Secrets loaded and decrypted")
            
        except Exception as e:
            logger.warning(f"Failed to load secrets: {e}")
    
    async def _validate_config(self) -> None:
        """Validate configuration against schemas."""
        # Validate main configuration
        main_schema = self._schemas.get('main', ConfigSchema())
        await self._validate_against_schema(self.config, main_schema, 'main')
        
        # Validate provider configurations
        providers = self.config.get('providers', {})
        for provider_name, provider_config in providers.items():
            schema = self._schemas.get(f'provider_{provider_name}', ConfigSchema())
            await self._validate_against_schema(provider_config, schema, f'provider_{provider_name}')
    
    async def _validate_against_schema(self, config: Dict[str, Any], schema: ConfigSchema, context: str) -> None:
        """Validate configuration against a schema."""
        # Check required fields
        for field in schema.required_fields:
            if field not in config:
                raise ConfigurationError(f"Missing required field '{field}' in {context}")
        
        # Check field types
        for field, expected_type in schema.field_types.items():
            if field in config and not isinstance(config[field], expected_type):
                raise ConfigurationError(
                    f"Field '{field}' in {context} should be {expected_type.__name__}, "
                    f"got {type(config[field]).__name__}"
                )
        
        # Run custom validators
        for field, validator in schema.field_validators.items():
            if field in config:
                try:
                    validator(config[field])
                except Exception as e:
                    raise ConfigurationError(f"Validation failed for field '{field}' in {context}: {e}")
    
    def _apply_defaults(self) -> None:
        """Apply default values for missing optional fields."""
        for field, default_value in self._schemas.get('main', ConfigSchema()).optional_fields.items():
            if field not in self.config:
                self.config[field] = default_value
    
    async def _encrypt_secrets(self) -> None:
        """Encrypt secrets in memory."""
        if not self._secrets:
            return
        
        # Generate encryption key if not exists
        if not self._encryption_key:
            self._encryption_key = Fernet.generate_key()
        
        # Encrypt each secret
        for key, value in self._secrets.items():
            if isinstance(value, str):
                fernet = Fernet(self._encryption_key)
                encrypted_value = fernet.encrypt(value.encode())
                self._secrets[key] = encrypted_value.decode()
    
    async def _encrypt_secrets_data(self, secrets: Dict[str, str]) -> bytes:
        """Encrypt secrets data for storage."""
        if not self._encryption_key:
            self._encryption_key = Fernet.generate_key()
        
        # Prepare secrets for encryption
        secrets_data = {}
        for key, value in secrets.items():
            if isinstance(value, str):
                fernet = Fernet(self._encryption_key)
                encrypted_value = fernet.encrypt(value.encode())
                secrets_data[key] = encrypted_value.decode()
            else:
                secrets_data[key] = value
        
        # Add encryption key hash for verification
        key_hash = hashlib.sha256(self._encryption_key).hexdigest()
        secrets_data['_key_hash'] = key_hash
        
        return json.dumps(secrets_data).encode()
    
    async def _decrypt_secrets_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt secrets data from storage."""
        # Try to get encryption key from environment or generate new one
        key_env = os.getenv('OPENCODE_SECRETS_KEY')
        if key_env:
            self._encryption_key = key_env.encode()
        else:
            # Try to derive key from config path
            key_material = f"{self.config_path}_{os.getpid()}".encode()
            self._encryption_key = hashlib.sha256(key_material).digest()
        
        # Decrypt data
        fernet = Fernet(self._encryption_key)
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Verify key hash
        secrets_dict = json.loads(decrypted_data.decode())
        if '_key_hash' in secrets_dict:
            expected_hash = secrets_dict.pop('_key_hash')
            actual_hash = hashlib.sha256(self._encryption_key).hexdigest()
            
            if expected_hash != actual_hash:
                raise ConfigurationError("Secrets decryption failed: key mismatch")
        
        return json.dumps(secrets_dict).encode()
    
    async def _create_backup(self) -> None:
        """Create backup of current configuration."""
        backup_dir = Path(self.config_path) / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"config_backup_{timestamp}.yaml"
        
        if Path(self.config_path / "config.yaml").exists():
            import shutil
            shutil.copy2(self.config_path / "config.yaml", backup_file)
            logger.debug(f"Configuration backup created: {backup_file}")
    
    def _define_schemas(self) -> Dict[str, ConfigSchema]:
        """Define configuration schemas."""
        return {
            'main': ConfigSchema(
                required_fields=['environment'],
                optional_fields={
                    'debug': False,
                    'log_level': 'INFO',
                    'plugin_paths': [],
                    'storage': {
                        'type': 'filesystem',
                        'path': '/tmp/opencode-accounts',
                        'backup_enabled': True,
                        'backup_interval': 3600
                    },
                    'monitoring': {
                        'enabled': True,
                        'metrics_interval': 60,
                        'health_check_interval': 300
                    }
                },
                field_types={
                    'environment': str,
                    'debug': bool,
                    'log_level': str,
                    'plugin_paths': list
                },
                field_validators={
                    'environment': lambda x: x in ['development', 'staging', 'production'],
                    'log_level': lambda x: x in ['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                    'plugin_paths': lambda x: all(isinstance(p, str) for p in x)
                }
            ),
            'provider_opencode': ConfigSchema(
                required_fields=['enabled'],
                optional_fields={
                    'accounts': {
                        'count': 8,
                        'rotation_strategy': 'round_robin',
                        'health_check_interval': 300
                    },
                    'credentials': {
                        'template_path': '~/.config/xnai/opencode-credentials.yaml',
                        'injection_enabled': True
                    }
                },
                field_types={
                    'enabled': bool,
                    'accounts': dict,
                    'credentials': dict
                }
            ),
            'provider_antigravity': ConfigSchema(
                required_fields=['enabled'],
                optional_fields={
                    'oauth': {
                        'client_id': '',
                        'client_secret': ''
                    },
                    'models': ['opus-4-6-thinking'],
                    'quality_validation': True
                },
                field_types={
                    'enabled': bool,
                    'oauth': dict,
                    'models': list,
                    'quality_validation': bool
                }
            )
        }
    
    def _get_default_config(self, environment: str) -> Dict[str, Any]:
        """Get default configuration for environment."""
        base_config = {
            'environment': environment,
            'debug': environment == 'development',
            'log_level': 'DEBUG' if environment == 'development' else 'INFO',
            'plugin_paths': [],
            'storage': {
                'type': 'filesystem',
                'path': '/tmp/opencode-accounts',
                'backup_enabled': True,
                'backup_interval': 3600
            },
            'monitoring': {
                'enabled': True,
                'metrics_interval': 60,
                'health_check_interval': 300
            },
            'providers': {
                'opencode': {
                    'enabled': True,
                    'accounts': {
                        'count': 8,
                        'rotation_strategy': 'round_robin',
                        'health_check_interval': 300
                    },
                    'credentials': {
                        'template_path': '~/.config/xnai/opencode-credentials.yaml',
                        'injection_enabled': True
                    }
                },
                'antigravity': {
                    'enabled': True,
                    'oauth': {
                        'client_id': '',
                        'client_secret': ''
                    },
                    'models': ['opus-4-6-thinking'],
                    'quality_validation': True
                },
                'cline': {
                    'enabled': True,
                    'cli_path': '/usr/local/bin/cline',
                    'timeout': 30,
                    'retry_attempts': 3
                },
                'gemini': {
                    'enabled': True,
                    'api_key': '',
                    'context_window': 8192,
                    'quality_score': 90
                },
                'copilot': {
                    'enabled': True,
                    'github_token': '',
                    'context_awareness': True,
                    'code_analysis': True
                }
            }
        }
        
        if environment == 'production':
            base_config['debug'] = False
            base_config['log_level'] = 'INFO'
            base_config['monitoring']['metrics_interval'] = 300  # Less frequent in production
        
        return base_config


# Global configuration manager instance
config_manager = ConfigurationManager()