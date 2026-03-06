# Multi-Account OAuth and Domain Access User Guide

## Overview

This guide provides comprehensive instructions for using the enhanced multi-account OAuth authentication system and domain-specific expert access in the Omega Stack.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Multi-Account OAuth Setup](#multi-account-oauth-setup)
3. [Domain-Specific Expert Access](#domain-specific-expert-access)
4. [Enhanced CLI Usage](#enhanced-cli-usage)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Configuration](#advanced-configuration)

## Quick Start

### 1. Authenticate All Accounts

```bash
# Run batch authentication for all 8 accounts
python test_multi_account_oauth.py batch_auth

# Or use the OAuth manager directly
python app/XNAi_rag_app/core/oauth_manager.py batch
```

### 2. List Available Domains

```bash
# Use enhanced CLI to list domains
python app/XNAi_rag_app/cli/enhanced_cli.py --list-domains
```

### 3. Use Domain-Specific Experts

```bash
# Access Architect domain
python app/XNAi_rag_app/cli/enhanced_cli.py --domain architect --query "Design a microservices architecture"

# Access UI domain
python app/XNAi_rag_app/cli/enhanced_cli.py --domain ui --query "Create a responsive dashboard"
```

## Multi-Account OAuth Setup

### Account Configuration

The system supports 8 OAuth accounts across 3 providers:

#### Google Gemini Accounts (3 accounts)
- `gemini_oauth_01` - Primary Gemini account
- `gemini_oauth_02` - Secondary Gemini account  
- `gemini_oauth_03` - Tertiary Gemini account

**Domains Supported**: general, architect, ui, voice, data

#### OpenCode Accounts (3 accounts)
- `opencode_oauth_01` - Primary OpenCode account
- `opencode_oauth_02` - Secondary OpenCode account
- `opencode_oauth_03` - Tertiary OpenCode account

**Domains Supported**: general, architect, api, test, research

#### GitHub Copilot Accounts (2 accounts)
- `copilot_oauth_01` - Primary Copilot account
- `copilot_oauth_02` - Secondary Copilot account

**Domains Supported**: general, api, test, ops

### Authentication Process

1. **Initial Setup**: The system automatically detects available accounts from `config/cline-accounts.yaml`

2. **OAuth Flow**: Each account goes through its respective OAuth authentication:
   - Google accounts use Google OAuth 2.0
   - GitHub accounts use GitHub OAuth
   - OpenCode accounts use GitHub OAuth (via Antigravity plugin)

3. **Credential Storage**: Credentials are securely stored in `~/.xnai/oauth_credentials.json` with encryption

4. **Automatic Refresh**: The system automatically refreshes expired tokens

### Account Management

#### List All Accounts
```bash
python app/XNAi_rag_app/cli/enhanced_cli.py --list-accounts
```

#### Switch Accounts
```bash
python app/XNAi_rag_app/cli/enhanced_cli.py --switch-account gemini_oauth_02
```

#### Check Account Status
```bash
python app/XNAi_rag_app/core/oauth_manager.py list
```

## Domain-Specific Expert Access

### Available Domains

| Domain | Expert Role | Primary Models | Description |
|--------|-------------|----------------|-------------|
| `general` | General Purpose Assistant | Claude Sonnet 4.6 | Default for all queries |
| `architect` | System Blueprinting & Architecture | Claude Opus 4.6 Thinking | System design and architecture |
| `api` | Backend, AnyIO, & Redis Streams | Claude Sonnet 4.6 | API development and backend |
| `ui` | Frontend, UX, & Dashboard | Gemini 3 Pro | Frontend and user experience |
| `voice` | Audio, STT/TTS Protocols | Gemini 3 Pro | Audio processing and speech |
| `data` | RAG, Qdrant, & Gnosis Engine | Gemini 3 Pro | Data management and RAG |
| `ops` | Infra, Podman, & Caddy | Claude Sonnet 4.6 | Infrastructure and deployment |
| `research` | Scholarly Mining & Metadata | Claude Opus 4.6 Thinking | Research and academic writing |
| `test` | QA, Pytest, & Validation | Claude Sonnet 4.6 | Testing and quality assurance |

### Domain Selection

#### Automatic Domain Detection
The system can automatically detect the appropriate domain based on your query:

```bash
python app/XNAi_rag_app/cli/enhanced_cli.py --auto-detect "How do I optimize database queries?"
```

#### Manual Domain Selection
Specify the domain explicitly:

```bash
python app/XNAi_rag_app/cli/enhanced_cli.py --domain architect --query "Design a scalable system"
```

### Expert Context

Each domain has specialized expert context including:
- **Prompt Templates**: Domain-specific instructions and guidelines
- **Knowledge Base**: Relevant documentation and resources
- **Specializations**: Areas of expertise
- **Examples**: Sample queries and responses
- **Constraints**: Guidelines and limitations

## Enhanced CLI Usage

### Basic Commands

#### Dispatch with Domain
```bash
python app/XNAi_rag_app/cli/enhanced_cli.py --query "Your question here" --domain architect
```

#### List Information
```bash
# List available domains
python app/XNAi_rag_app/cli/enhanced_cli.py --list-domains

# List available accounts
python app/XNAi_rag_app/cli/enhanced_cli.py --list-accounts

# Get domain status
python app/XNAi_rag_app/cli/enhanced_cli.py --domain-status architect
```

#### Account Management
```bash
# Switch accounts
python app/XNAi_rag_app/cli/enhanced_cli.py --switch-account gemini_oauth_02

# Auto-detect domain
python app/XNAi_rag_app/cli/enhanced_cli.py --auto-detect "Your query here"
```

### Advanced Options

#### Specify Account
```bash
python app/XNAi_rag_app/cli/enhanced_cli.py --query "Question" --domain architect --account gemini_oauth_01
```

#### Session Management
```bash
python app/XNAi_rag_app/cli/enhanced_cli.py --query "Question" --domain architect --session my_session
```

### Integration with Existing CLI

The enhanced CLI can be integrated with the existing `xnai` CLI:

```bash
# Use with existing xnai CLI
xnai account dispatch "Design a system" --domain architect
```

## Troubleshooting

### Common Issues

#### No OAuth Credentials Found
```bash
# Error: No OAuth credentials found for account
# Solution: Run batch authentication
python test_multi_account_oauth.py batch_auth
```

#### Account Not Available
```bash
# Error: No valid account available for routing
# Solution: Check account configuration and credentials
python app/XNAi_rag_app/core/oauth_manager.py list
```

#### Domain Not Found
```bash
# Error: Domain 'xyz' not found
# Solution: Use auto-detection or check available domains
python app/XNAi_rag_app/cli/enhanced_cli.py --list-domains
```

#### Authentication Failed
```bash
# Error: Authentication failed for account
# Solution: Re-authenticate the specific account
python app/XNAi_rag_app/core/oauth_manager.py authenticate <account_id>
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
export XNAI_DEBUG=1
python app/XNAi_rag_app/cli/enhanced_cli.py --query "Test" --domain general
```

### Credential Issues

#### Check Credential File
```bash
# Check if credential file exists
ls -la ~/.xnai/oauth_credentials.json

# Check encryption key
ls -la ~/.xnai/.oauth_key
```

#### Manual Credential Cleanup
```bash
# Remove expired credentials
python app/XNAi_rag_app/core/oauth_manager.py cleanup

# Delete specific account credentials
python app/XNAi_rag_app/core/oauth_manager.py delete <account_id>
```

## Advanced Configuration

### Custom Domain Configuration

Add new domains by editing `config/domain-routing.yaml`:

```yaml
domains:
  my_custom_domain:
    id: 9
    role: "Custom Expert Role"
    expert_config: "expert-knowledge/my_custom_expert.yaml"
    preferred_models: ["model1", "model2"]
    description: "Description of custom domain"
```

### Custom Expert Configuration

Create custom expert configurations in `expert-knowledge/`:

```yaml
# expert-knowledge/my_custom_expert.yaml
prompt_template: |
  You are an expert in [domain]. Focus on [specific areas]...

knowledge_base:
  - "path/to/knowledge/file1.md"
  - "path/to/knowledge/file2.md"

specializations:
  - "Specialization 1"
  - "Specialization 2"

examples:
  - "Example query 1"
  - "Example query 2"

constraints:
  - "Constraint 1"
  - "Constraint 2"
```

### Account Priority Configuration

Modify account priorities in `config/cline-accounts.yaml`:

```yaml
accounts:
  - id: "gemini_oauth_01"
    priority: 1  # Lower numbers = higher priority
    # ... other config
```

### OAuth Scopes and Permissions

Configure OAuth scopes for each account:

```yaml
oauth_config:
  scopes: ["scope1", "scope2", "scope3"]
  refresh_interval: 3600  # Seconds
  credential_file: "~/.xnai/oauth_credentials.json"
```

### Environment Variables

Set environment variables for configuration:

```bash
export XNAI_OAUTH_STORAGE_PATH="~/.custom/oauth.json"
export XNAI_DOMAIN_CONFIG_PATH="config/custom-domains.yaml"
export XNAI_DEBUG=1
```

## Best Practices

### Account Management

1. **Regular Authentication**: Re-authenticate accounts periodically
2. **Monitor Usage**: Track account usage and quota
3. **Backup Credentials**: Keep backup of important credentials
4. **Security**: Use strong OAuth scopes and monitor access

### Domain Usage

1. **Choose Appropriate Domain**: Use domain-specific experts for better results
2. **Auto-Detection**: Use auto-detection for ambiguous queries
3. **Expert Context**: Leverage domain-specific knowledge and examples
4. **Constraints**: Follow domain-specific guidelines and constraints

### Performance Optimization

1. **Account Selection**: Use appropriate accounts for different domains
2. **Model Selection**: Choose models based on task requirements
3. **Caching**: Leverage expert context caching
4. **Rate Limiting**: Respect API rate limits and quotas

## Support and Resources

### Documentation
- [Architecture Overview](docs/architecture/)
- [API Reference](docs/api/)
- [Configuration Guide](docs/infrastructure/)

### Testing
- Run comprehensive tests: `python test_multi_account_oauth.py`
- Test specific components: `python test_multi_account_oauth.py --test oauth_manager`

### Logs and Monitoring
- Check application logs: `tail -f logs/app.log`
- Monitor OAuth activity: `grep "OAuth" logs/app.log`

### Community and Support
- GitHub Issues: Report bugs and feature requests
- Documentation: Contribute to documentation improvements
- Testing: Help test new features and configurations

## Conclusion

The multi-account OAuth and domain-specific expert access system provides a powerful and flexible way to access specialized AI expertise across multiple accounts and domains. By following this guide, you can effectively authenticate accounts, access domain experts, and troubleshoot any issues that arise.

For additional support or questions, refer to the troubleshooting section or consult the comprehensive documentation.