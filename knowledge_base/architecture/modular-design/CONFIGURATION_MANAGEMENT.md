# XNAi Foundation: Configuration Management System

**Version**: 1.0.0  
**Date**: 2026-02-27  
**Status**: Design Phase  
**Purpose**: Centralized configuration management for modular services

## Overview

This configuration management system leverages your existing Consul infrastructure while adding environment-specific overrides, service isolation, and development-friendly patterns.

## Current Configuration State

### Existing Infrastructure
- **Consul**: Service discovery and basic configuration
- **Environment Variables**: Runtime configuration in docker-compose.yml
- **YAML Files**: Static configuration (config.toml, mkdocs.yml)
- **Secrets**: Redis password, API keys in .env files

### Configuration Challenges
- No centralized configuration hierarchy
- Limited environment-specific overrides
- Manual configuration management
- No configuration validation

## Configuration Management Architecture

### 1. Configuration Hierarchy

```
📁 Configuration Sources (Priority Order)
├── 1. Environment Variables (Highest Priority)
├── 2. Consul KV (Service-Specific)
├── 3. Environment Overrides (dev/staging/prod)
├── 4. Service Defaults (Base Configuration)
└── 5. Global Defaults (Lowest Priority)
```

### 2. Configuration Structure

```
📁 Configuration Organization
├── configs/
│   ├── base/                    # Base configurations
│   │   ├── services.yaml        # Service definitions
│   │   ├── infrastructure.yaml  # Infrastructure config
│   │   └── defaults.yaml        # Global defaults
│   ├── environments/           # Environment-specific overrides
│   │   ├── development.yaml
│   │   ├── staging.yaml
│   │   └── production.yaml
│   ├── services/               # Service-specific configs
│   │   ├── rag-core.yaml
│   │   ├── knowledge-mgmt.yaml
│   │   ├── ui-service.yaml
│   │   └── monitoring.yaml
│   └── templates/              # Configuration templates
│       ├── docker-compose-template.yaml
│       └── kubernetes-template.yaml
└── scripts/
    ├── config-manager.py       # Configuration management tool
    └── validate-config.py      # Configuration validation
```

## Configuration Management Implementation

### 1. Configuration Manager Service

```python
# configs/scripts/config-manager.py
import os
import yaml
import consul
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ConfigSource:
    name: str
    priority: int
    loader: callable

class ConfigurationManager:
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.consul_client = consul.Consul()
        self.config_sources = self._setup_config_sources()
        
    def _setup_config_sources(self) -> list[ConfigSource]:
        """Setup configuration sources in priority order"""
        return [
            ConfigSource("environment_vars", 100, self._load_environment_vars),
            ConfigSource("consul_kv", 80, self._load_consul_kv),
            ConfigSource("environment_overrides", 60, self._load_environment_overrides),
            ConfigSource("service_defaults", 40, self._load_service_defaults),
            ConfigSource("global_defaults", 20, self._load_global_defaults),
        ]
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get merged configuration for a specific service"""
        config = {}
        
        for source in self.config_sources:
            try:
                source_config = source.loader(service_name)
                if source_config:
                    config = self._deep_merge(config, source_config)
            except Exception as e:
                print(f"Warning: Failed to load config from {source.name}: {e}")
        
        return config
    
    def _load_environment_vars(self, service_name: str) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        env_config = {}
        
        # Service-specific environment variables
        service_prefix = f"{service_name.upper().replace('-', '_')}_"
        
        for key, value in os.environ.items():
            if key.startswith(service_prefix):
                config_key = key[len(service_prefix):].lower()
                env_config = self._set_nested_value(env_config, config_key, value)
        
        return env_config
    
    def _load_consul_kv(self, service_name: str) -> Dict[str, Any]:
        """Load configuration from Consul KV store"""
        try:
            index, data = self.consul_client.kv.get(f"xnai/services/{service_name}", recurse=True)
            if data:
                config = {}
                for item in data:
                    key = item['Key'].split(f'xnai/services/{service_name}/')[1]
                    value = item['Value'].decode('utf-8') if item['Value'] else None
                    config = self._set_nested_value(config, key, value)
                return config
        except Exception as e:
            print(f"Consul KV load failed: {e}")
        return {}
    
    def _load_environment_overrides(self, service_name: str) -> Dict[str, Any]:
        """Load environment-specific overrides"""
        env_file = Path(f"configs/environments/{self.environment}.yaml")
        if env_file.exists():
            with open(env_file) as f:
                env_config = yaml.safe_load(f)
                return env_config.get('services', {}).get(service_name, {})
        return {}
    
    def _load_service_defaults(self, service_name: str) -> Dict[str, Any]:
        """Load service-specific default configuration"""
        service_file = Path(f"configs/services/{service_name}.yaml")
        if service_file.exists():
            with open(service_file) as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_global_defaults(self, service_name: str) -> Dict[str, Any]:
        """Load global default configuration"""
        defaults_file = Path("configs/base/defaults.yaml")
        if defaults_file.exists():
            with open(defaults_file) as f:
                return yaml.safe_load(f)
        return {}
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _set_nested_value(self, config: Dict[str, Any], key_path: str, value: Any) -> Dict[str, Any]:
        """Set a nested configuration value using dot notation"""
        keys = key_path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        return config
```

### 2. Configuration Validation

```python
# configs/scripts/validate-config.py
import yaml
import jsonschema
from pathlib import Path
from typing import Dict, Any

class ConfigValidator:
    def __init__(self):
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict[str, Dict]:
        """Load JSON schemas for configuration validation"""
        schemas_dir = Path("configs/schemas")
        schemas = {}
        
        for schema_file in schemas_dir.glob("*.json"):
            with open(schema_file) as f:
                schemas[schema_file.stem] = json.load(f)
        
        return schemas
    
    def validate_service_config(self, service_name: str, config: Dict[str, Any]) -> bool:
        """Validate service configuration against schema"""
        schema_name = f"{service_name}-config"
        
        if schema_name not in self.schemas:
            print(f"Warning: No schema found for {service_name}")
            return True
        
        try:
            jsonschema.validate(config, self.schemas[schema_name])
            return True
        except jsonschema.exceptions.ValidationError as e:
            print(f"Validation error for {service_name}: {e}")
            return False
    
    def validate_environment_config(self, environment: str, config: Dict[str, Any]) -> bool:
        """Validate environment configuration"""
        # Implementation for environment-specific validation
        return True
```

### 3. Service-Specific Configuration Templates

```yaml
# configs/services/rag-core.yaml
service:
  name: rag-core
  version: "1.0.0"
  environment: "${ENVIRONMENT:-development}"
  
api:
  host: "0.0.0.0"
  port: 8000
  workers: 1
  timeout: 30
  
dependencies:
  vector_db:
    host: "${QDRANT_HOST:-qdrant}"
    port: "${QDRANT_PORT:-6333}"
    collection: "xnai_vectors"
    api_key: "${QDRANT_API_KEY}"
  
  llm_providers:
    - name: "openai"
      endpoint: "${OPENAI_ENDPOINT:-https://api.openai.com}"
      model: "${OPENAI_MODEL:-gpt-4}"
      api_key: "${OPENAI_API_KEY}"
      timeout: 60
      max_tokens: 4096
  
  cache:
    host: "${REDIS_HOST:-redis}"
    port: "${REDIS_PORT:-6379}"
    db: 0
    password: "${REDIS_PASSWORD}"
    ttl: 3600
  
monitoring:
  enabled: true
  metrics_port: 8002
  health_check_interval: 30
  
security:
  jwt_secret: "${JWT_SECRET}"
  allowed_origins:
    - "http://localhost:8001"
    - "http://localhost:3000"
  
  rate_limiting:
    enabled: true
    requests_per_minute: 60
    burst_size: 10
```

```yaml
# configs/services/knowledge-mgmt.yaml
service:
  name: knowledge-mgmt
  version: "1.0.0"
  
processing:
  max_document_size: "50MB"
  supported_formats:
    - "pdf"
    - "docx"
    - "txt"
    - "md"
  
  extraction:
    chunk_size: 1000
    chunk_overlap: 100
    language: "en"
  
  quality:
    min_confidence: 0.7
    max_retries: 3
    timeout: 300
  
storage:
  documents_path: "/app/documents"
  processed_path: "/app/processed"
  backup_path: "/app/backups"
  
  database:
    host: "${POSTGRES_HOST:-postgres}"
    port: "${POSTGRES_PORT:-5432}"
    name: "${POSTGRES_DB:-xnai}"
    user: "${POSTGRES_USER:-postgres}"
    password: "${POSTGRES_PASSWORD}"
```

### 4. Environment-Specific Overrides

```yaml
# configs/environments/development.yaml
services:
  rag-core:
    api:
      debug: true
      log_level: "DEBUG"
    
    dependencies:
      vector_db:
        host: "localhost"
        port: 6333
      
      cache:
        host: "localhost"
        port: 6379
  
  knowledge-mgmt:
    processing:
      chunk_size: 500
      chunk_overlap: 50
    
    storage:
      documents_path: "./dev/documents"
      processed_path: "./dev/processed"

infrastructure:
  consul:
    host: "localhost"
    port: 8500
  
  redis:
    host: "localhost"
    port: 6379
  
  qdrant:
    host: "localhost"
    port: 6333
```

```yaml
# configs/environments/production.yaml
services:
  rag-core:
    api:
      workers: 4
      timeout: 60
      log_level: "INFO"
    
    dependencies:
      vector_db:
        host: "qdrant-prod.internal"
        port: 6333
      
      cache:
        host: "redis-prod.internal"
        port: 6379
        password: "${REDIS_PASSWORD_PROD}"
  
  knowledge-mgmt:
    processing:
      chunk_size: 2000
      chunk_overlap: 200
    
    storage:
      documents_path: "/data/documents"
      processed_path: "/data/processed"

infrastructure:
  consul:
    host: "consul-prod.internal"
    port: 8500
  
  monitoring:
    enabled: true
    metrics_retention: "30d"
    alerting_enabled: true
```

## Configuration Management Commands

### 1. Enhanced Makefile Targets

```makefile
# Configuration Management Targets
.PHONY: config-validate config-apply config-diff config-reset

config-validate: ## Validate all service configurations
	@echo "$(CYAN)Validating service configurations...$(NC)"
	@$(PYTHON) configs/scripts/validate-config.py --all

config-apply: ## Apply configuration to Consul
	@echo "$(CYAN)Applying configuration to Consul...$(NC)"
	@$(PYTHON) configs/scripts/config-manager.py --apply --environment=$(ENVIRONMENT)

config-diff: ## Show configuration differences between environments
	@echo "$(CYAN)Showing configuration differences...$(NC)"
	@$(PYTHON) configs/scripts/config-manager.py --diff --from=$(FROM_ENV) --to=$(TO_ENV)

config-reset: ## Reset configuration to defaults
	@echo "$(CYAN)Resetting configuration to defaults...$(NC)"
	@$(PYTHON) configs/scripts/config-manager.py --reset --service=$(SERVICE_NAME)
```

### 2. Configuration CLI Tool

```python
# configs/scripts/config-cli.py
import argparse
import sys
from config_manager import ConfigurationManager
from validate_config import ConfigValidator

def main():
    parser = argparse.ArgumentParser(description="XNAi Configuration Management CLI")
    subparsers = parser.add_subparsers(dest='command')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configurations')
    validate_parser.add_argument('--service', help='Service to validate')
    validate_parser.add_argument('--all', action='store_true', help='Validate all services')
    
    # Apply command
    apply_parser = subparsers.add_parser('apply', help='Apply configuration')
    apply_parser.add_argument('--environment', default='development', help='Environment to apply')
    apply_parser.add_argument('--service', help='Service to apply')
    
    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Show configuration differences')
    diff_parser.add_argument('--from', dest='from_env', help='Source environment')
    diff_parser.add_argument('--to', dest='to_env', help='Target environment')
    diff_parser.add_argument('--service', help='Service to compare')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get service configuration')
    get_parser.add_argument('service', help='Service name')
    get_parser.add_argument('--environment', default='development', help='Environment')
    get_parser.add_argument('--format', choices=['yaml', 'json'], default='yaml', help='Output format')
    
    args = parser.parse_args()
    
    if args.command == 'validate':
        validator = ConfigValidator()
        if args.all:
            # Validate all services
            pass
        elif args.service:
            config_manager = ConfigurationManager()
            config = config_manager.get_service_config(args.service)
            validator.validate_service_config(args.service, config)
    
    elif args.command == 'apply':
        config_manager = ConfigurationManager(args.environment)
        # Apply configuration logic
        pass
    
    elif args.command == 'diff':
        # Show configuration differences
        pass
    
    elif args.command == 'get':
        config_manager = ConfigurationManager(args.environment)
        config = config_manager.get_service_config(args.service)
        if args.format == 'json':
            import json
            print(json.dumps(config, indent=2))
        else:
            import yaml
            print(yaml.dump(config, default_flow_style=False))

if __name__ == '__main__':
    main()
```

## Integration with Existing Infrastructure

### 1. Consul Integration

```python
# Enhanced Consul integration
class ConsulConfigManager:
    def __init__(self):
        self.client = consul.Consul()
    
    def register_service_config(self, service_name: str, config: Dict[str, Any]):
        """Register service configuration in Consul KV"""
        config_key = f"xnai/services/{service_name}/config"
        config_data = yaml.dump(config)
        
        self.client.kv.put(config_key, config_data)
    
    def watch_service_config(self, service_name: str, callback: callable):
        """Watch for configuration changes"""
        config_key = f"xnai/services/{service_name}/config"
        
        def watch_loop():
            index = None
            while True:
                index, data = self.client.kv.get(config_key, index=index, wait='10s')
                if data:
                    config = yaml.safe_load(data['Value'])
                    callback(config)
        
        import threading
        watcher = threading.Thread(target=watch_loop, daemon=True)
        watcher.start()
```

### 2. Docker Compose Integration

```yaml
# Enhanced docker-compose.yml with configuration management
services:
  config-manager:
    build:
      context: .
      dockerfile: Dockerfile.config-manager
    image: xnai-config-manager:latest
    container_name: xnai_config_manager
    environment:
      - CONSUL_HOST=consul
      - CONSUL_PORT=8500
      - ENVIRONMENT=${ENVIRONMENT:-development}
    volumes:
      - ./configs:/app/configs:ro
    depends_on:
      - consul
    networks:
      - xnai_network
    restart: unless-stopped
    command: ["python", "configs/scripts/config-manager.py", "--watch"]
```

### 3. Environment Variable Management

```bash
# Enhanced environment setup script
#!/bin/bash
# scripts/setup-environment.sh

set -e

ENVIRONMENT=${1:-development}
echo "Setting up environment: $ENVIRONMENT"

# Load base configuration
if [ -f "configs/environments/$ENVIRONMENT.yaml" ]; then
    echo "Loading environment configuration: $ENVIRONMENT"
    python3 configs/scripts/config-manager.py --apply --environment=$ENVIRONMENT
else
    echo "Warning: Environment configuration not found: $ENVIRONMENT"
fi

# Validate configuration
echo "Validating configuration..."
python3 configs/scripts/validate-config.py --all

# Set up environment-specific secrets
case $ENVIRONMENT in
    development)
        echo "Setting up development environment..."
        export REDIS_PASSWORD="dev_password"
        export QDRANT_API_KEY="dev_key"
        ;;
    production)
        echo "Setting up production environment..."
        # Load from secure secrets management
        ;;
esac

echo "Environment setup complete!"
```

## Benefits and Features

### 1. Centralized Management
- **Single Source of Truth**: All configuration in one place
- **Version Control**: Configuration changes tracked in Git
- **Environment Isolation**: Clear separation between environments

### 2. Flexibility and Extensibility
- **Service-Specific**: Each service has its own configuration
- **Environment Overrides**: Easy environment-specific customization
- **Template Support**: Reusable configuration templates

### 3. Operational Excellence
- **Validation**: Configuration validation before deployment
- **Monitoring**: Configuration change tracking and auditing
- **Rollback**: Easy rollback to previous configurations

### 4. Developer Experience
- **Local Development**: Easy local configuration setup
- **Debugging**: Clear configuration hierarchy and overrides
- **Documentation**: Self-documenting configuration structure

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Create configuration directory structure
- [ ] Implement basic configuration manager
- [ ] Create service-specific configuration templates

### Phase 2: Integration (Week 2)
- [ ] Integrate with existing Consul infrastructure
- [ ] Add configuration validation
- [ ] Create CLI tools and Makefile targets

### Phase 3: Enhancement (Week 3)
- [ ] Add configuration watching and hot-reloading
- [ ] Implement configuration diff and rollback
- [ ] Create comprehensive documentation

### Phase 4: Production (Week 4)
- [ ] Deploy to development environment
- [ ] Test configuration management workflows
- [ ] Validate with all services

## Next Steps

1. **Review Configuration Structure**: Validate the proposed configuration hierarchy
2. **Implement Core Components**: Start with the configuration manager and validation
3. **Integrate with Services**: Update existing services to use new configuration system
4. **Test and Iterate**: Validate the system with real service configurations

This configuration management system provides a solid foundation for managing the modular architecture while leveraging your existing infrastructure investments.