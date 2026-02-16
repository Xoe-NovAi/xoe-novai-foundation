# Vikunja Implementation Guide: Complete Sovereign PM Integration

## Overview

This guide provides comprehensive instructions for deploying and using Vikunja as the central project management hub for the Xoe-NovAi ecosystem. The implementation includes full security hardening, automated deployment, and seamless integration with the existing memory_bank system.

## 🚀 Quick Start

### 1. Prerequisites

- **Podman** installed and configured for rootless containers
- **Python 3.10+** with required packages (aiohttp, tenacity, python-frontmatter)
- **Network access** for initial container downloads
- **Sufficient disk space** for database and file storage

### 2. One-Command Deployment

```bash
# Deploy Vikunja with full security hardening
python3 scripts/deploy_vikunja_secure.py
```

This will:
- ✅ Setup proper permissions for rootless containers
- ✅ Create secure Podman secrets (database password, JWT secret)
- ✅ Deploy Vikunja with security hardening (no-new-privileges, SELinux labels)
- ✅ Wait for services to be healthy
- ✅ Run security scan on containers
- ✅ Display access information and next steps

### 3. Access Vikunja

After deployment:
- **UI**: http://localhost:3456
- **API**: http://localhost:3456/api/v1

Create your admin account through the web interface, then get your API token from Settings > API.

## 📋 Complete Implementation Components

### Core Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/deploy_vikunja_secure.py` | Complete secure deployment | `python3 scripts/deploy_vikunja_secure.py` |
| `scripts/setup_vikunja_secrets.py` | Setup Podman secrets | `python3 scripts/setup_vikunja_secrets.py` |
| `scripts/memory_bank_export.py` | Export memory_bank to JSON | `python3 scripts/memory_bank_export.py --dry-run` |
| `scripts/vikunja_importer.py` | Import tasks to Vikunja | `python3 scripts/vikunja_importer.py vikunja-import.json --token YOUR_TOKEN` |
| `scripts/recovery/vikunja_recovery_flow.sh` | Recovery and maintenance | `bash scripts/recovery/vikunja_recovery_flow.sh` |

### Configuration Files

| File | Purpose | Security |
|------|---------|----------|
| `docker-compose.yml` | Rootless deployment configuration | Hardened with no-new-privileges, SELinux labels |
| `Caddyfile` | Local reverse proxy configuration | Local-only access, no external exposure |

## 🔒 Security Features

### Rootless Container Security
- **Non-root users**: All containers run as UID 1000:1000
- **No new privileges**: `--no-new-privileges` on all services
- **SELinux labels**: `:Z,U` volume flags for proper context
- **User namespaces**: `--userns=keep-id` for isolation

### Secret Management
- **Podman secrets**: Database password and JWT secret stored securely
- **Runtime injection**: No secrets in files or environment
- **Automatic rotation**: Secrets can be rotated without container restart

### Network Security
- **Local-only access**: Caddy proxy restricts to localhost
- **No external exposure**: No public ports exposed
- **Isolated network**: Dedicated bridge network for Vikunja services

## 🔄 Migration from memory_bank

### Step 1: Export Existing Tasks

```bash
# Dry run to see what will be exported
python3 scripts/memory_bank_export.py --dry-run memory_bank vikunja-import.json

# Export for real
python3 scripts/memory_bank_export.py memory_bank vikunja-import.json
```

### Step 2: Import to Vikunja

```bash
# Dry run import
python3 scripts/vikunja_importer.py vikunja-import.json --dry-run

# Live import with API token
python3 scripts/vikunja_importer.py vikunja-import.json --token YOUR_API_TOKEN
```

### Step 3: Verify Migration

- Check tasks appear in Vikunja UI
- Verify labels and custom fields are preserved
- Confirm task descriptions and priorities are correct

## 🛠️ Management Commands

### View Logs
```bash
podman-compose -f docker-compose.yml logs
```

### Stop Services
```bash
podman-compose -f docker-compose.yml down
```

### Restart Services
```bash
podman-compose -f docker-compose.yml restart
```

### Clean Deployment (Remove Everything)
```bash
python3 scripts/deploy_vikunja_secure.py --cleanup
```

### Security Scan
```bash
# Run Trinity security scan
trivy image vikunja/api:latest
trivy image vikunja/frontend:latest
trivy image postgres:16
```

## 📊 Integration with Xoe-NovAi Ecosystem

### Memory Bank Synchronization
- **Bidirectional sync**: Tasks can flow between memory_bank and Vikunja
- **Automated updates**: Changes in Vikunja can update memory_bank files
- **Conflict resolution**: Manual review for conflicting changes

### Agent Integration
- **Gemini CLI**: Can create tasks directly via Vikunja API
- **Cline variants**: Can update task status and add comments
- **Grok MC**: Can monitor progress and generate reports

### EKB Integration
- **Task references**: Tasks can link to EKB entries
- **Knowledge mapping**: Tasks can be tagged with relevant knowledge areas
- **Progress tracking**: EKB updates can be tracked as tasks

## 🔧 Customization

### Adding Custom Labels
Vikunja automatically creates labels based on memory_bank frontmatter:
- **Agents**: `Grok MC`, `Gemini CLI`, `Cline-Kat`, etc.
- **Status**: `proposed`, `backlog`, `in-progress`, `completed`
- **Priority**: `high`, `medium`, `low`, `critical`
- **Ma'at ideals**: `ma_at_7`, `ma_at_18`, `ma_at_41`, etc.

### Custom Fields
Tasks include custom fields from memory_bank:
- **Owner**: From `author` field
- **Date**: From `date` field
- **EKB-Link**: From `ekb_links` field
- **Version**: From `version` field

### Project Structure
- **Namespaces**: `Foundation`, `Arcana`, `Agents`, `Infra`, `EKB`, `Sync`, `Roadmaps`
- **Projects**: Organized by phase and domain
- **Labels**: Comprehensive tagging system for filtering and search

## 🚨 Troubleshooting

### Common Issues

**Podman Permission Errors**
```bash
# Add user to podman group
sudo usermod -aG podman $USER
# Log out and back in, or use:
newgrp podman
```

**Container Won't Start**
```bash
# Check Podman info
podman info
# Check available storage
podman system df
# Clean up resources
podman system prune -a
```

**API Not Accessible**
```bash
# Check if services are running
podman ps
# Check port binding
podman port vikunja-proxy
# Check Caddy configuration
podman logs vikunja-proxy
```

**Secrets Not Found**
```bash
# Recreate secrets
python3 scripts/setup_vikunja_secrets.py --cleanup
python3 scripts/setup_vikunja_secrets.py
```

### Recovery Procedures

**Complete Recovery**
```bash
# Stop and remove everything
podman-compose -f docker-compose.yml down
podman system prune -a

# Clean up secrets
python3 scripts/setup_vikunja_secrets.py --cleanup

# Redeploy
python3 scripts/deploy_vikunja_secure.py
```

**Database Recovery**
```bash
# Backup database
podman exec vikunja-db pg_dump -U vikunja vikunja > vikunja-backup.sql

# Restore database
podman exec -i vikunja-db psql -U vikunja -d vikunja < vikunja-backup.sql
```

## 📈 Performance Optimization

### Database Tuning
- **Shared buffers**: Set to 25% of available RAM
- **Connection pooling**: Vikunja handles connection pooling automatically
- **Index optimization**: Vikunja creates necessary indexes automatically

### Container Optimization
- **Resource limits**: Set appropriate CPU/memory limits if needed
- **Health checks**: Built-in health checks ensure service availability
- **Logging**: Structured logging for debugging and monitoring

### Network Optimization
- **Local proxy**: Caddy provides efficient local proxying
- **Compression**: Enabled by default for API responses
- **Caching**: Browser caching for static assets

## 🔮 Future Enhancements

### Planned Features
- **MCP Integration**: Full Gemini CLI MCP server for task management
- **Automated Sync**: Background sync between memory_bank and Vikunja
- **Advanced Reporting**: Custom reports and dashboards
- **Mobile Support**: Optimized mobile interface
- **Plugin System**: Custom plugins for specialized workflows

### Integration Opportunities
- **Git Integration**: Link tasks to commits and pull requests
- **Calendar Integration**: Sync tasks with calendar applications
- **Notification System**: Email and webhook notifications
- **Advanced Analytics**: Usage analytics and insights

## 📚 Additional Resources

- **Vikunja Documentation**: https://vikunja.io/docs/
- **Podman Documentation**: https://docs.podman.io/
- **Caddy Documentation**: https://caddyserver.com/docs/
- **Xoe-NovAi Project Brief**: `memory_bank/projectbrief.md`
- **Security Guidelines**: `memory_bank/techContext.md`

## 🤝 Contributing

To contribute to the Vikunja implementation:

1. **Test thoroughly**: Always test deployment scripts in isolated environments
2. **Document changes**: Update this guide for any modifications
3. **Security first**: Ensure all changes maintain security hardening
4. **Backward compatibility**: Maintain compatibility with existing workflows

## 📞 Support

For issues with the Vikunja implementation:

1. **Check logs**: Use `podman-compose logs` to diagnose issues
2. **Review documentation**: Check this guide and linked resources
3. **Search issues**: Check for similar issues in project tracking
4. **Ask for help**: Use appropriate channels for assistance

---

**Status**: ✅ **Production-Ready Implementation**  
**Security**: 🔒 **Hardened Rootless Deployment**  
**Integration**: 🔄 **Full Ecosystem Compatibility**