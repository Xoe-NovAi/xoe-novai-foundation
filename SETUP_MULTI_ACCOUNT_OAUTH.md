# Multi-Account OAuth Setup Guide

## Overview

This guide provides comprehensive instructions for setting up OAuth authentication for all 8 accounts and enabling domain-specific expert access through the CLI.

## Current Issues

1. **OAuth Authentication**: Only one account (gemini_oauth_01) is configured with OAuth
2. **Domain Access**: CLI shows "General (Instance )" instead of specific domains
3. **Account Switching**: Requires re-authentication when switching accounts
4. **Expert Access**: No way to access Architect or UI expert domains through CLI

## Solution Architecture

### 1. Multi-Account OAuth Credential Management
- Secure storage of OAuth tokens for multiple accounts
- Automatic credential rotation and refresh
- Persistent authentication across sessions

### 2. Domain Routing System
- Map domains to specific expert configurations
- CLI parameter handling for domain selection
- Expert initialization and context loading

### 3. Enhanced CLI Interface
- Add --domain parameter to CLI
- Domain-specific expert access
- Account switching without re-authentication

## Implementation Plan

### Phase 1: OAuth Credential Management System

#### 1.1 Create OAuth Credential Storage
```python
# File: app/XNAi_rag_app/core/oauth_manager.py
class OAuthManager:
    """Manages OAuth credentials for multiple accounts"""
    
    def __init__(self, storage_path: str = "~/.xnai/oauth_credentials.json"):
        self.storage_path = Path(storage_path).expanduser()
        self.credentials = self._load_credentials()
    
    def _load_credentials(self) -> Dict[str, Dict[str, Any]]:
        """Load stored OAuth credentials"""
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_credentials(self, account_id: str, credentials: Dict[str, Any]):
        """Save OAuth credentials for an account"""
        self.credentials[account_id] = credentials
        self._save_to_file()
    
    def get_credentials(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get OAuth credentials for an account"""
        return self.credentials.get(account_id)
    
    def _save_to_file(self):
        """Save credentials to encrypted file"""
        # Implementation with encryption
        pass
```

#### 1.2 Batch Authentication Script
```python
# File: scripts/batch_oauth_auth.py
async def batch_authenticate_accounts():
    """Authenticate all 8 accounts with OAuth"""
    
    accounts = [
        "gemini_oauth_01", "gemini_oauth_02", "gemini_oauth_03",
        "opencode_oauth_01", "opencode_oauth_02", "opencode_oauth_03",
        "copilot_oauth_01", "copilot_oauth_02"
    ]
    
    oauth_manager = OAuthManager()
    
    for account_id in accounts:
        print(f"Authenticating {account_id}...")
        credentials = await authenticate_account(account_id)
        oauth_manager.save_credentials(account_id, credentials)
        print(f"✅ {account_id} authenticated")
```

### Phase 2: Domain Routing System

#### 2.1 Domain Configuration
```yaml
# File: config/domain-routing.yaml
domains:
  architect:
    id: 1
    role: "System Blueprinting & Architecture"
    expert_config: "expert-knowledge/architect-expert.yaml"
    preferred_models: ["google/antigravity-claude-opus-4-6-thinking"]
    
  ui:
    id: 3
    role: "Frontend, UX, & Dashboard"
    expert_config: "expert-knowledge/ui-expert.yaml"
    preferred_models: ["google/antigravity-gemini-3-pro"]
    
  api:
    id: 2
    role: "Backend, AnyIO, & Redis Streams"
    expert_config: "expert-knowledge/api-expert.yaml"
    preferred_models: ["google/antigravity-claude-sonnet-4-6"]
```

#### 2.2 Domain Router Implementation
```python
# File: app/XNAi_rag_app/core/domain_router.py
class DomainRouter:
    """Routes requests to appropriate domain experts"""
    
    def __init__(self, config_path: str = "config/domain-routing.yaml"):
        self.config = self._load_config(config_path)
        self.experts = {}
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load domain routing configuration"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get_expert_for_domain(self, domain: str) -> Dict[str, Any]:
        """Get expert configuration for a domain"""
        return self.config['domains'].get(domain, self.config['domains']['general'])
    
    def route_to_expert(self, domain: str, query: str, account_id: str) -> Dict[str, Any]:
        """Route query to appropriate expert"""
        expert_config = self.get_expert_for_domain(domain)
        
        # Load expert context
        expert_context = self._load_expert_context(expert_config)
        
        # Select appropriate model
        model = self._select_model(expert_config, account_id)
        
        return {
            'expert_config': expert_config,
            'expert_context': expert_context,
            'model': model,
            'routing_info': {
                'domain': domain,
                'expert_role': expert_config['role'],
                'account_id': account_id
            }
        }
```

### Phase 3: Enhanced CLI Interface

#### 3.1 CLI Domain Selection
```python
# File: app/XNAi_rag_app/cli/enhanced_cli.py
class EnhancedCLI:
    """Enhanced CLI with domain selection and multi-account support"""
    
    def __init__(self):
        self.oauth_manager = OAuthManager()
        self.domain_router = DomainRouter()
        self.account_manager = AccountManager()
    
    def dispatch_with_domain(self, query: str, domain: str = "general", 
                           account_id: Optional[str] = None) -> Dict[str, Any]:
        """Dispatch query with domain selection"""
        
        # Select account if not specified
        if not account_id:
            account_id = self.account_manager.select_best_account(domain)
        
        # Get OAuth credentials
        credentials = self.oauth_manager.get_credentials(account_id)
        if not credentials:
            print(f"❌ No OAuth credentials found for {account_id}")
            print("Run: python scripts/batch_oauth_auth.py")
            return {"error": "No OAuth credentials"}
        
        # Route to domain expert
        routing_result = self.domain_router.route_to_expert(domain, query, account_id)
        
        # Execute with expert context
        result = self._execute_with_expert(query, routing_result)
        
        return result
    
    def list_domains(self):
        """List available domains"""
        domains = self.domain_router.config['domains']
        print("Available domains:")
        for domain_id, config in domains.items():
            print(f"  {domain_id}: {config['role']}")
    
    def switch_account(self, account_id: str):
        """Switch to different account"""
        credentials = self.oauth_manager.get_credentials(account_id)
        if credentials:
            print(f"✅ Switched to account: {account_id}")
            return True
        else:
            print(f"❌ No credentials found for {account_id}")
            return False
```

## Implementation Steps

### Step 1: Create OAuth Manager
1. Create `app/XNAi_rag_app/core/oauth_manager.py`
2. Implement secure credential storage
3. Add encryption for sensitive data

### Step 2: Create Domain Router
1. Create `config/domain-routing.yaml`
2. Create `app/XNAi_rag_app/core/domain_router.py`
3. Implement expert context loading

### Step 3: Enhance CLI
1. Create `app/XNAi_rag_app/cli/enhanced_cli.py`
2. Add domain selection parameters
3. Integrate with existing CLI

### Step 4: Batch Authentication
1. Create `scripts/batch_oauth_auth.py`
2. Implement OAuth flow for all accounts
3. Add credential validation

### Step 5: Update Account Registry
1. Update `config/cline-accounts.yaml` with domain mappings
2. Add OAuth configuration for all accounts
3. Configure persistent authentication

## Usage Examples

### Authenticate All Accounts
```bash
# Run batch authentication
python scripts/batch_oauth_auth.py

# Verify authentication
python -c "from app.XNAi_rag_app.core.oauth_manager import OAuthManager; print(OAuthManager().credentials.keys())"
```

### Use Domain-Specific Experts
```bash
# Access Architect domain
xnai account dispatch "Design a microservices architecture" --domain architect

# Access UI domain
xnai account dispatch "Create a responsive dashboard" --domain ui

# List available domains
xnai domain list

# Switch accounts
xnai account switch gemini_oauth_02
```

### CLI with Domain Selection
```bash
# Use enhanced CLI
python app/XNAi_rag_app/cli/enhanced_cli.py --domain architect --query "Design system architecture"

# Switch accounts without re-auth
python app/XNAi_rag_app/cli/enhanced_cli.py --account gemini_oauth_02 --domain ui --query "Design dashboard"
```

## Security Considerations

### Credential Storage
- Use encrypted storage for OAuth tokens
- Implement token refresh mechanisms
- Add credential expiration handling

### Account Isolation
- Separate credentials per account
- Prevent credential leakage between accounts
- Implement secure credential rotation

### Domain Security
- Validate domain access permissions
- Implement expert context isolation
- Add audit logging for domain access

## Testing Strategy

### Unit Tests
- OAuth credential management
- Domain routing logic
- CLI parameter handling

### Integration Tests
- Multi-account authentication flow
- Domain expert access
- Account switching functionality

### End-to-End Tests
- Complete authentication and domain access workflow
- Error handling and recovery
- Performance with multiple accounts

## Monitoring and Maintenance

### Credential Monitoring
- Track credential expiration
- Monitor authentication failures
- Alert on credential issues

### Domain Usage Analytics
- Track domain access patterns
- Monitor expert performance
- Identify popular domains

### Account Health Monitoring
- Monitor account availability
- Track usage patterns
- Alert on account issues

## Next Steps

1. **Implement OAuth Manager** - Create secure credential storage
2. **Create Domain Router** - Implement domain-to-expert mapping
3. **Enhance CLI** - Add domain selection and account switching
4. **Batch Authentication** - Authenticate all 8 accounts
5. **Update Configuration** - Add domain mappings to account registry
6. **Testing and Validation** - Comprehensive testing of all features
7. **Documentation** - User guides and API documentation

This comprehensive solution will resolve all authentication and domain access issues while providing a robust foundation for multi-account and domain-specific expert access.