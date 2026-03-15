# 🧠 Gemini Facet 6 Session Management Guide
**Version**: 1.0
**Date**: 2026-03-11
**Subject**: Comprehensive session state management for Facet 6

## 📍 Session Location & Structure

### Primary Session Directory
```
/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/storage/instances/facets/instance-6/gemini-cli/.gemini/
```

### Key Files & Their Purpose
- **`settings.json`**: Core configuration (theme, editor, model settings)
- **`mcp_config.json`**: MCP server integration (memory-bank connection)
- **`projects.json`**: Project associations and workspace mapping
- **`trustedFolders.json`**: Security permissions for file operations
- **`installation_id`**: Unique session identifier
- **`state.json`**: Current session state (tips shown, etc.)
- **`agents/facet-6.md`**: Agent definition and tool permissions
- **`expert_soul.md`**: Agent role and directives
- **`policies/facet-permissions.toml`**: Tool access permissions

## 🔄 Session State Management

### Current Active Context
Facet 6 is currently working on **"The Great Reconciliation"** - a major filesystem optimization task:

**Active Objectives:**
- [ ] Merge `storage_new/` into `data/` (11.4GB)
- [ ] Merge `knowledge_new/` into `expert-knowledge/` (1.2GB)
- [ ] Merge `docs-new/` into `docs/`
- [ ] Create symlink for models in `/media/arcana-novai/omega_library/`
- [ ] Reclaim ~15GB root space

### Session Health Monitoring

#### Memory Management
- **zRAM**: Monitor compression efficiency
- **Vulkan iGPU**: Ensure GPU acceleration is active
- **Disk Usage**: Keep root partition below 90% capacity

#### Performance Indicators
- **Agent Bus Health**: Check Redis Stream connectivity
- **MCP Integration**: Verify memory-bank server connection
- **Model Loading**: Monitor GGUF weight loading from library partition

## 🛠️ Configuration Management

### Core Settings (settings.json)
```json
{
  "theme": "dark",
  "editor": "code",
  "auto_save": true,
  "stream": true,
  "minimal_ui": true,
  "max_history_items": 100,
  "telemetry_opt_out": true,
  "model": {
    "apiKey": "AIzaSyCPRsWqa-zkX_oCjs6hSttxrnig88DbsoA"
  }
}
```

### MCP Integration (mcp_config.json)
```json
{
  "mcpServers": {
    "memory-bank": {
      "command": "podman",
      "args": [
        "run", "-i", "--rm", "--network=host",
        "--env-file", "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/.env",
        "-v", "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/storage:/storage:Z",
        "-v", "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/app:/app/app:ro",
        "-v", "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/mcp-servers/memory-bank-mcp:/app/mcp-server:ro",
        "xnai_memory_bank_mcp",
        "python", "server.py"
      ]
    }
  }
}
```

## 🚨 Session Recovery Procedures

### If Session Becomes Unresponsive
1. **Check MCP Server**: Verify the memory-bank MCP server is running
2. **Restart Agent Bus**: Restart Redis and clear any stuck streams
3. **Validate Configuration**: Check for syntax errors in JSON config files
4. **Clear State**: Reset `state.json` if tips/progress tracking is corrupted

### Filesystem Recovery
If the Great Reconciliation fails:
1. **Backup Current State**: Copy entire `.gemini/` directory
2. **Verify Parity**: Use checksums to ensure file integrity before merge
3. **Atomic Operations**: Use `rsync` with `--backup` for safe merging
4. **Rollback Plan**: Keep original folders until merge is verified

## 📊 Performance Optimization

### Hardware-Specific Tuning
- **GTT Adrenaline**: Enable `HSA_OVERRIDE_GFX_VERSION=9.0.0` for 8GB VRAM
- **Vulkan iGPU**: Ensure models use integrated GPU for inference
- **zRAM Compression**: Monitor and tune compression ratios

### Session Efficiency
- **Recursive Context Archiving (RCA)**: Implement 33:1 compression for long sessions
- **Tool Usage**: Prioritize `grep_search` over `read_file` for large codebases
- **Memory Management**: Regular cleanup of temporary files and caches

## 🔐 Security & Permissions

### File Access
- **Trusted Folders**: Only `/home/arcana-novai/Documents/Xoe-NovAi/omega-stack` is trusted
- **Tool Permissions**: Full access to file operations with priority 100
- **MCP Security**: All MCP operations run in isolated Podman containers

### API Key Management
- **Location**: Stored in `settings.json` under `model.apiKey`
- **Rotation**: Change API key and update configuration as needed
- **Backup**: Store API key securely outside the session directory

## 🔄 Session Migration

### Moving to New Environment
1. **Export Configuration**: Copy entire `.gemini/` directory
2. **Update Paths**: Modify any absolute paths in configuration files
3. **Rebuild MCP**: Ensure memory-bank MCP server is available in new environment
4. **Test Connectivity**: Verify all integrations work before full migration

### Backup Strategy
- **Daily Backups**: Automated backup of `.gemini/` directory
- **Configuration Snapshots**: Version control for configuration changes
- **Session History**: Archive conversation logs from `artifacts/`

## 📈 Monitoring & Maintenance

### Regular Health Checks
- **Daily**: Verify MCP server connectivity
- **Weekly**: Check disk usage and memory compression
- **Monthly**: Review and clean up session artifacts

### Performance Metrics
- **Response Time**: Monitor agent response latency
- **Memory Usage**: Track RAM and VRAM utilization
- **File Operations**: Monitor I/O performance for large file operations

## 🎯 Advanced Features

### Persistent Entities
Facet 6 can create and manage persistent expert personas:
- **Entity Registry**: Located in `app/XNAi_rag_app/core/entities/`
- **Knowledge Mining**: Automatic research for new entities
- **Continuous Learning**: Feedback loops for entity improvement

### Agent Collaboration
- **Agent Bus**: Redis-based communication between agents
- **Task Distribution**: Delegation of complex tasks to specialized agents
- **State Synchronization**: Shared context across agent sessions

## 📞 Support & Troubleshooting

### Common Issues
1. **MCP Connection Failures**: Check Podman container status
2. **File Access Errors**: Verify trusted folder configuration
3. **Performance Degradation**: Monitor memory usage and compression
4. **Session Crashes**: Check for syntax errors in configuration files

### Emergency Procedures
- **Complete Reset**: Delete `.gemini/` directory and restart session
- **Configuration Recovery**: Restore from backup configuration files
- **Agent Reinitialization**: Restart MCP servers and agent bus

---

**Note**: This guide is based on the current state of Facet 6 as of 2026-03-11. Regular updates should be made as the session evolves and new capabilities are added.