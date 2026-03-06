# Multi-Account System for XNAi RAG Stack

Comprehensive multi-provider account management system with intelligent rotation, isolation, and CLI integration.

## Overview

The XNAi Multi-Account System provides:

- **Multi-Provider Support**: GitHub Copilot, Gemini, OpenCode, Antigravity, and more
- **Intelligent Account Rotation**: Quota-aware, priority-based, and task-specific selection
- **Account Isolation**: Complete separation between providers and users
- **CLI Integration**: Full command-line interface for account management
- **Agent Integration**: Seamless integration with the agent system
- **Comprehensive Testing**: Extensive test suite with isolation validation

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Account System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  │   Account       │    │   Agent         │    │   CLI           │
│  │   Manager       │    │   Integration   │    │   Interface     │
│  │                 │    │                 │    │                 │
│  │ • Account CRUD  │    │ • Context       │    │ • Account List  │
│  │ • Quota Tracking│    │   Management    │    │ • Switch Account│
│  │ • Validation    │    │ • Task Execution│    │ • Create Account│
│  │ • Rotation      │    │ • Access Control│    │ • Status Report │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  │   Configuration │    │   Testing       │    │   Validation    │
│  │   Management    │    │   Suite         │    │   Scripts       │
│  │                 │    │                 │    │                 │
│  │ • YAML Configs  │    │ • Unit Tests    │    │ • Isolation     │
│  │ • Environment   │    │ • Integration   │    │   Validation    │
│  │ • Encryption    │    │ • End-to-End    │    │ • Security      │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Features

### Core Account Management

- **Account CRUD Operations**: Create, read, update, delete accounts
- **Multi-Provider Support**: GitHub, Gemini, OpenCode, Antigravity, etc.
- **Quota Tracking**: Real-time quota monitoring and updates
- **Usage Statistics**: Detailed metrics and performance tracking
- **Account Status Management**: Active, inactive, suspended, expired states

### Intelligent Rotation

- **Quota-Aware Selection**: Prefer accounts with higher remaining quota
- **Priority-Based Rotation**: Lower priority numbers = higher priority
- **Task-Specific Routing**: Route tasks to accounts with preferred models
- **Automatic Fallback**: Switch to alternatives when primary accounts are exhausted

### Security & Isolation

- **Configuration Isolation**: Separate configs per provider/user
- **Context Isolation**: Agent contexts don't interfere with each other
- **Access Control**: Validate permissions before account access
- **Security Validation**: Prevent access to suspended/zero-quota accounts

### CLI Integration

- **Account Management**: List, create, switch, suspend accounts
- **Status Monitoring**: Real-time account status and usage
- **Recommendations**: Get best account for specific tasks
- **Reporting**: Generate comprehensive usage reports

### Agent Integration

- **Context-Aware Switching**: Preserve agent context during account switches
- **Task Execution**: Execute tasks with specific or recommended accounts
- **Access Validation**: Verify agent permissions before account access
- **Multi-Agent Support**: Multiple agents can use different accounts simultaneously

## Installation

The multi-account system is included with the XNAi RAG Stack. No additional installation required.

### Dependencies

```bash
pip install pyyaml click pytest
```

## Configuration

### Account Registry Format

Create `memory_bank/ACCOUNT-REGISTRY.yaml`:

```yaml
accounts:
  - id: "github_user_01"
    name: "GitHub User Account"
    type: "user"
    status: "active"
    created_at: "2026-03-01T10:00:00"
    last_used: null
    email: "user@example.com"
    provider: "github"
    quota_remaining: 1000
    quota_limit: 1000
    models_preferred: ["haiku-4.5", "sonnet-4.5"]
    priority: 1
    api_key: "your_github_api_key"
    usage_stats:
      total_requests: 0
      successful_requests: 0
      failed_requests: 0
      avg_response_time: 0.0

  - id: "gemini_user_01"
    name: "Gemini User Account"
    type: "user"
    status: "active"
    created_at: "2026-03-01T10:00:00"
    last_used: null
    email: "user@example.com"
    provider: "gemini"
    quota_remaining: 800
    quota_limit: 1000
    models_preferred: ["gemini-3-pro"]
    priority: 2
    api_key: "your_gemini_api_key"
    usage_stats:
      total_requests: 0
      successful_requests: 0
      failed_requests: 0
      avg_response_time: 0.0

rotation_strategy: "quota_aware"
auto_switch: true
validation_enabled: true
```

### Environment Variables

```bash
export ACCOUNT_MGMT_CONFIG_PATH="/path/to/accounts.yaml"
export ACCOUNT_MGMT_LOG_LEVEL="INFO"
export ACCOUNT_MGMT_AUTO_ROTATE="true"
```

## Usage

### CLI Commands

#### Account Management

```bash
# List all accounts
xnai account list

# List accounts by type
xnai account list --type user

# List accounts by status
xnai account list --status active

# Show detailed account information
xnai account list --verbose

# Show current account status
xnai account status

# Show specific account status
xnai account status --account github_user_01
```

#### Account Switching

```bash
# Switch to a specific account
xnai account switch github_user_01

# Get recommended account for a task
xnai account recommend --task reasoning

# Get recommended account for code tasks
xnai account recommend --task code
```

#### Account Creation

```bash
# Create a new account
xnai account create "New Account" \
  --type user \
  --email "new@example.com" \
  --provider github \
  --quota-limit 2000 \
  --models haiku-4.5 sonnet-4.5 \
  --priority 1
```

#### Account Management

```bash
# Suspend an account
xnai account suspend github_user_01 --reason "Testing suspension"

# Activate a suspended account
xnai account activate github_user_01

# Set API key for an account
xnai account set-api-key github_user_01 your_new_api_key

# Update quota information
xnai account update-quota github_user_01 --remaining 500 --limit 1000
```

#### Reporting

```bash
# Generate usage report
xnai account report

# Generate JSON report
xnai account report --format json

# Clean up expired accounts
xnai account cleanup --days 90

# Dry run cleanup
xnai account cleanup --days 90 --dry-run
```

### Programmatic Usage

#### Basic Account Management

```python
from app.XNAi_rag_app.core.account_manager import get_account_manager

async def manage_accounts():
    # Get account manager
    manager = await get_account_manager()
    
    # List all accounts
    accounts = await manager.list_accounts()
    
    # Get current account
    current = manager.get_current_account()
    
    # Switch account
    success = await manager.switch_account("github_user_01")
    
    # Get recommended account for task
    recommended = await manager.get_recommended_account("reasoning")
    
    # Create new account
    new_account_id = await manager.create_account(
        name="New Account",
        account_type="user",
        email="new@example.com",
        provider="github",
        quota_limit=2000,
        models_preferred=["haiku-4.5"],
        priority=1
    )
```

#### Agent Integration

```python
from app.XNAi_rag_app.core.agent_account_integration import AccountAwareAgent

async def agent_with_accounts():
    # Create account-aware agent
    agent = AccountAwareAgent("my_agent")
    await agent.initialize()
    
    # Get current account
    current_account = await agent.get_current_account()
    
    # Switch account
    success = await agent.switch_account("github_user_01")
    
    # Execute task with specific account
    async def my_task():
        return {"result": "success"}
    
    result = await agent.execute_with_account("github_user_01", my_task)
    
    # Execute task with recommended account
    result = await agent.execute_with_recommended_account(my_task, "reasoning")
    
    # Perform task with intelligent account selection
    result = await agent.perform_task(my_task, "code", preferred_account="github_user_01")
```

#### Context Management

```python
from app.XNAi_rag_app.core.agent_account_integration import AgentAccountContext

async def context_aware_operations():
    manager = await get_account_manager()
    
    # Use context manager to preserve account state
    async with AgentAccountContext("my_agent", manager):
        # Switch to different account
        await manager.switch_account("gemini_user_01")
        
        # Perform operations with new account
        # ... operations here ...
        
        # Account automatically restored when context exits
```

## Account Types and Providers

### Supported Providers

- **GitHub**: GitHub Copilot CLI integration
- **Gemini**: Google Gemini API integration
- **OpenCode**: OpenCode/Antigravity integration
- **Antigravity**: Multi-account rotation system
- **Custom**: Extensible provider system

### Account Types

- **User**: Regular user accounts
- **Service**: Service accounts for microservices
- **Primary**: Primary accounts with highest priority

### Task Types

- **Reasoning**: Tasks requiring deep thinking (prefers opus-4.6-thinking, raptor-mini)
- **Code**: Code generation and analysis (prefers sonnet-4.5, haiku-4.5)
- **Quick**: Fast responses (prefers haiku-4.5, raptor-mini)
- **Research**: Research and analysis (prefers gemini-3-pro, kimi-k2.5)

## Security Features

### Account Isolation

- **Configuration Isolation**: Each provider/user has separate configuration files
- **Context Isolation**: Agent contexts don't interfere with each other
- **Access Control**: Validate permissions before account access
- **Security Validation**: Prevent access to suspended/zero-quota accounts

### Validation Rules

- **Active Status**: Only active accounts can be used
- **Quota Availability**: Accounts must have remaining quota
- **Agent Permissions**: Verify agent has access to account
- **Context Preservation**: Restore original account after operations

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/test_multi_account_system.py -v

# Run specific test class
pytest tests/test_multi_account_system.py::TestAccountManager -v

# Run with coverage
pytest tests/test_multi_account_system.py --cov=app.XNAi_rag_app.core.account_manager
```

### Validation Scripts

```bash
# Run account isolation validation
python scripts/validate_account_isolation.py

# Run comprehensive validation
python scripts/validate_account_isolation.py > validation_report.txt
```

### Test Coverage

- **Unit Tests**: Core account management functionality
- **Integration Tests**: CLI and agent integration
- **End-to-End Tests**: Complete workflows
- **Isolation Tests**: Security and isolation validation

## Monitoring and Logging

### Log Levels

- **DEBUG**: Detailed operation logs
- **INFO**: General operation information
- **WARNING**: Potential issues and warnings
- **ERROR**: Errors and failures

### Metrics

- **Account Usage**: Request counts and success rates
- **Response Times**: Average response times per account
- **Quota Usage**: Real-time quota consumption
- **Switch Events**: Account switching events

### Monitoring Integration

The system integrates with existing monitoring infrastructure:

- **Prometheus Metrics**: Account usage and performance metrics
- **Health Checks**: Account availability and status
- **Alerting**: Quota exhaustion and account failures

## Troubleshooting

### Common Issues

#### Account Not Found
```bash
# Check if account exists
xnai account list --verbose

# Verify account ID
xnai account status --account your_account_id
```

#### Switch Failed
```bash
# Check account status
xnai account status --account your_account_id

# Check quota
xnai account status --account your_account_id

# Check permissions
# (Review IAM configuration)
```

#### CLI Commands Not Found
```bash
# Verify installation
python -c "import app.XNAi_rag_app.core.account_cli; print('CLI available')"

# Check PATH
which xnai
```

### Debug Mode

```bash
# Enable debug logging
export ACCOUNT_MGMT_LOG_LEVEL="DEBUG"

# Run with verbose output
xnai account list --verbose
```

### Configuration Issues

```bash
# Validate configuration
python -c "
import yaml
with open('memory_bank/ACCOUNT-REGISTRY.yaml') as f:
    config = yaml.safe_load(f)
    print('Configuration valid:', bool(config))
"

# Check file permissions
ls -la memory_bank/ACCOUNT-REGISTRY.yaml
```

## Performance Optimization

### Account Selection Optimization

- **Cache Results**: Cache account selection results for frequently used tasks
- **Batch Operations**: Batch multiple account operations when possible
- **Lazy Loading**: Load account details only when needed

### Quota Management

- **Real-time Updates**: Update quota information in real-time
- **Predictive Alerts**: Alert before quota exhaustion
- **Automatic Rotation**: Automatically rotate to accounts with higher quota

### Context Management

- **Minimal Context Switching**: Minimize context switches between accounts
- **Efficient Storage**: Use efficient storage for context data
- **Cleanup Policies**: Implement automatic cleanup of old contexts

## Integration with Existing Systems

### Agent Bus Integration

The multi-account system integrates with the Agent Bus for:

- **Task Distribution**: Distribute tasks to appropriate accounts
- **Event Publishing**: Publish account switch events
- **Coordination**: Coordinate between multiple agents

### IAM Integration

Integration with the Identity and Access Management system:

- **Permission Validation**: Validate agent permissions
- **User Management**: Manage user accounts and roles
- **Audit Logging**: Log all account access and operations

### Monitoring Integration

Integration with monitoring systems:

- **Metrics Collection**: Collect account usage metrics
- **Health Monitoring**: Monitor account health and availability
- **Alerting**: Set up alerts for quota exhaustion and failures

## Future Enhancements

### Planned Features

- **Web Dashboard**: Web-based account management interface
- **Mobile App**: Mobile application for account management
- **Advanced Analytics**: Advanced usage analytics and reporting
- **Machine Learning**: ML-based account selection optimization

### Extensibility

The system is designed to be easily extensible:

- **New Providers**: Add support for new providers
- **Custom Logic**: Implement custom account selection logic
- **Integration Points**: Add new integration points

## Contributing

### Development Setup

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd omega-stack
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Run Tests**:
   ```bash
   pytest tests/test_multi_account_system.py -v
   ```

### Code Style

- Follow existing code style and patterns
- Add comprehensive docstrings
- Include type hints for all functions
- Write tests for new functionality

### Testing Requirements

- All new features must include tests
- Tests must cover edge cases
- Integration tests required for new integrations
- Performance tests for critical paths

## Support

### Documentation

- **API Documentation**: Comprehensive API documentation
- **Usage Examples**: Real-world usage examples
- **Troubleshooting Guide**: Common issues and solutions

### Community

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Community discussions and support
- **Contributing**: Contribute to the project

### Enterprise Support

For enterprise support and custom implementations:

- **Professional Services**: Custom implementation services
- **Training**: Team training and workshops
- **Consulting**: Architecture and design consulting

## License

This system is part of the XNAi RAG Stack and follows the same licensing terms.

## Changelog

### Version 1.0.0 (2026-03-05)

- Initial release of multi-account system
- Core account management functionality
- CLI integration
- Agent integration
- Comprehensive testing suite
- Account isolation validation

---

For more information, see the [XNAi RAG Stack Documentation](./README.md).