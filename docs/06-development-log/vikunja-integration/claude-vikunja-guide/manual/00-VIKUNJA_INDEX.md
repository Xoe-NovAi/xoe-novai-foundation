# Vikunja Implementation Manual - Master Index & Quick Reference

**Version**: 1.0 Complete Suite  
**Updated**: 2026-02-07  
**Target**: Cline (Local Developer Assistant)  
**Status**: ✅ Ready for Implementation

---

## 📚 Documentation Suite

This manual consists of **5 comprehensive guides** totaling ~50,000 words and covering all aspects of Vikunja integration into Xoe-NovAi.

### Quick Navigation

| Part | Title | Purpose | Time | Status |
|------|-------|---------|------|--------|
| **Part 1** | [Architecture & Knowledge Gaps](01-VIKUNJA_ARCHITECTURE_GAPS.md) | Understanding Vikunja design + Podman rootless | 30 min | 📖 Read First |
| **Part 2** | [Pre-Deployment Setup](02-VIKUNJA_PREDEPLOYMENT.md) | Environment validation + config file creation | 1 hour | 🔧 Setup |
| **Part 3** | [Docker Compose & Deployment](03-VIKUNJA_DEPLOYMENT.md) | Multi-file Compose + actual stack startup | 2 hours | 🚀 Deploy |
| **Part 4** | [Testing, Validation & Troubleshooting](04-VIKUNJA_TESTING.md) | Verify functionality + fix common issues | 1 hour | ✅ Validate |
| **Part 5** | [Voice Integration & Advanced Features](05-VIKUNJA_ADVANCED.md) | REST API + webhook + voice commands (Phase 2) | 1 hour | 🎤 Integration |

**Total estimated time: 5-6 hours from zero to production-ready**

---

## 🎯 Getting Started (5-Minute Overview)

### What is Vikunja?

Vikunja is an open-source, self-hosted task management system designed for teams and individuals. It provides:
- **Project Management**: Organize tasks into projects
- **REST API**: Programmatic task creation/modification
- **Webhooks**: Event-driven automation (v0.22+)
- **Air-Gappable**: No cloud dependencies, full local control

### Why Integrate with Xoe-NovAi?

| Benefit | Use Case |
|---------|----------|
| **Voice Commands** | "Create task: Deploy Vikunja" → automatic task creation |
| **Knowledge Integration** | Tasks auto-log to RAG knowledge base |
| **Project Coordination** | Multi-agent systems manage shared task lists |
| **Autonomous Workflows** | Voice → FastAPI → Vikunja → task completion tracking |

### What's Actually Being Deployed?

```
Your System (8GB RAM, Ryzen 5700U)
├── Foundation Stack (unchanged)
│   ├── Redis (cache)
│   ├── RAG API (FastAPI)
│   ├── Chainlit UI (voice interface)
│   └── Caddy (reverse proxy) ← NOW UNIFIED ENTRYPOINT
│
└── Vikunja Stack (NEW - optional overlay)
    ├── PostgreSQL 16 (database)
    ├── Vikunja API (bundled Go binary)
    └── (Shares: Redis, Caddy, Network)

Total footprint: ~1.3GB RAM
All access: http://localhost (port 80 via Caddy)
```

---

## 🚀 Quick Start Path

### If you're familiar with Docker/Podman:

```bash
# Step 1: Read Part 1 (30 min understanding)
cat 01-VIKUNJA_ARCHITECTURE_GAPS.md | less

# Step 2: Run Part 2 setup (45 min preparation)
bash 02-VIKUNJA_PREDEPLOYMENT.md  # Contains executable blocks

# Step 3: Deploy via Part 3 (1 hour deployment)
# Copy docker-compose.vikunja.yml + Caddyfile + configs
# Then: make up-vikunja

# Step 4: Test via Part 4 (30 min validation)
./test-full-stack.sh

# Step 5: Integrate via Part 5 (optional, future)
# Implement voice commands when ready
```

### If you're new to containerization:

**⚠️ Recommended**: Read all 5 parts sequentially (don't skip)
- Part 1 builds your mental model
- Part 2 ensures environment is correct
- Part 3 provides detailed copy-paste instructions
- Part 4 teaches troubleshooting
- Part 5 shows future possibilities

---

## 🔍 Finding Specific Information

### "I need to..."

| Goal | Go To | Section |
|------|-------|---------|
| Understand Vikunja architecture | Part 1 | "Vikunja Architecture Deep Dive" |
| Set up my system | Part 2 | "Directory Structure Preparation" |
| Create config files | Part 2 | "Configuration Files" |
| Deploy the stack | Part 3 | "Deployment Steps" |
| Test if it's working | Part 4 | "Functionality Testing" |
| Fix a specific error | Part 4 | "Troubleshooting Guide" |
| Enable voice commands | Part 5 | "Voice-to-Vikunja Integration" |
| See the REST API | Part 5 | "Vikunja REST API Quick Reference" |
| Plan future features | Part 5 | "Advanced Features & Roadmap" |

---

## ⚠️ Critical Knowledge Gaps Fixed

### Gap 1: "Vikunja is multiple containers"
**Reality**: Vikunja is a **single bundled binary** (API + Frontend together)
**Impact**: Simpler deployment, but no independent scaling

### Gap 2: "Docker permission solutions work for Podman"
**Reality**: Rootless Podman uses different userns mapping
**Solution**: Use `:Z,U` flags + `podman unshare chown` (see Part 2)

### Gap 3: "PostgreSQL default settings work for <6GB systems"
**Reality**: Default shared_buffers (25% RAM) causes memory issues
**Solution**: Tune to 128MB shared_buffers (see Part 2 config)

### Gap 4: "Vikunja needs manual proxy configuration"
**Reality**: Environment variables override config files (VIKUNJA_ prefix)
**Solution**: Use env-only approach in docker-compose.vikunja.yml

### Gap 5: "Secrets go in docker-compose.yml"
**Reality**: Plaintext secrets in compose is a security risk
**Solution**: Use Podman native secrets (external: true in compose)

---

## 📋 Pre-Implementation Checklist

Before starting, verify:

- [ ] **Podman**: `podman --version` returns ≥ 4.0.0
- [ ] **Subuid/subgid**: `grep "^$(whoami):" /etc/subuid` shows ≥65536 range
- [ ] **SELinux**: `getenforce` returns Enforcing/Permissive/Disabled (all OK)
- [ ] **Disk Space**: `df -h $(pwd)` shows ≥10GB free
- [ ] **Git Status**: `git status` is clean (no uncommitted changes)
- [ ] **Docker Compose**: `podman compose --version` works
- [ ] **Read Part 1**: You understand how Vikunja architecture differs from your assumptions

---

## 🔐 Security Principles

**All deployments follow Ma'at ethical guidelines**:

| Law | Implementation |
|-----|-----------------|
| **18: Balance** | Modular Compose (toggle Vikunja on/off independently) |
| **35: Security** | Rootless containers, zero elevated privileges, secret management |
| **41: Progress** | Single bundled binary (~100MB), lean memory footprint |
| **42: Simplicity** | Environment variables only, no complex scripts |

**Result**: Grade A sovereignty compliance ✅

---

## 📊 Implementation Timeline

```
Week 1:
├── Day 1: Read Parts 1-2 (90 min learning)
├── Day 2: Run Part 2 setup (45 min preparation)
├── Day 3: Deploy via Part 3 (120 min deployment)
└── Day 4: Validate via Part 4 (60 min testing)

Week 2:
├── Day 5-7: Run in production, monitor, fix issues
└── Day 8+: Plan Phase 2 features (voice integration)

Total: ~5-6 hours hands-on + 1 week validation
```

---

## 🛠️ Essential Commands Reference

### Lifecycle Management

```bash
# Start Foundation only (without Vikunja)
make up
make down
make restart

# Start Foundation + Vikunja
make up-vikunja       # Start both
make down-vikunja     # Stop Vikunja (keep Foundation)
make restart-vikunja  # Restart Vikunja

# Monitoring
make health           # Check Foundation health
make health-vikunja   # Check Vikunja health
make logs             # Tail Foundation logs
make logs-vikunja     # Tail Vikunja logs
```

### Configuration & Secrets

```bash
# View secrets (from files)
cat secrets/redis_password.txt
cat secrets/vikunja_db_password.txt

# Create Podman secrets
podman secret create redis_password < secrets/redis_password.txt
podman secret create vikunja_db_password < secrets/vikunja_db_password.txt

# Fix permissions
podman unshare chown 1000:1000 -R data/vikunja/
```

### Database Access

```bash
# Connect to Vikunja database
podman exec xnai_vikunja_db psql -U vikunja -d vikunja

# Useful PostgreSQL queries:
SELECT COUNT(*) FROM pg_stat_activity;  # Check connections
SELECT * FROM tasks;                    # View all tasks
VACUUM ANALYZE;                         # Optimize database
```

### API Testing

```bash
# Get JWT token
TOKEN=$(curl -s -X POST http://localhost/vikunja/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' | jq -r '.token')

# Create task
curl -X POST http://localhost/vikunja/api/v1/projects/1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task"}'

# List tasks
curl http://localhost/vikunja/api/v1/tasks/all \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### Container Inspection

```bash
# View all containers
podman ps

# View container logs
podman logs xnai_vikunja_api

# Execute command inside container
podman exec xnai_vikunja_api curl http://localhost:3456/api/v1/info

# Inspect container resources
podman stats --no-stream xnai_vikunja_api
```

---

## 📞 Troubleshooting Quick Links

**Problem**: Docker Compose syntax errors
→ See Part 3: "Validate Docker Compose Syntax"

**Problem**: "Permission denied" on data/ directory
→ See Part 2: "Set Correct Permissions" + Part 4: "Troubleshooting Guide"

**Problem**: PostgreSQL won't start
→ See Part 4: "PostgreSQL fails to start"

**Problem**: Vikunja API returns 500 error
→ See Part 4: "Vikunja API returns 500 Error"

**Problem**: Can't access Vikunja from browser
→ See Part 4: "Caddy 'bad gateway' for Vikunja"

**All other issues**: Jump to Part 4 "Troubleshooting Guide" (comprehensive solutions for 15+ common problems)

---

## 🎯 Success Criteria

When complete, you will have:

✅ **Functional Vikunja System**
- Web UI at `http://localhost/vikunja/`
- REST API at `http://localhost/vikunja/api/v1/`
- Database persisting across restarts

✅ **Integrated Architecture**
- Foundation Stack unchanged, still operational
- Caddy unified reverse proxy (single port 80 entrypoint)
- All services on shared xnai_network

✅ **Security Hardened**
- All containers rootless, non-root users
- Secrets managed via Podman (not plaintext)
- No elevated capabilities, read-only filesystems

✅ **Performance Optimized**
- Total memory <2GB for Vikunja (PostgreSQL + API)
- API response time <300ms
- Database connections pooled (<20 max)

✅ **Future-Ready**
- Foundation for Phase 2 voice integration
- REST API fully functional and documented
- Webhook receiver framework implemented

---

## 📖 Documentation Conventions

### Code Blocks

**Bash commands**:
```bash
# Cline: Execute this command
echo "This is what to run"
```

**Python code**:
```python
# Cline: Add this to your application
import requests
```

**YAML configuration**:
```yaml
# Add this section to config files
key: value
```

### Callout Boxes

- ✅ **Success/verified**: Something works as expected
- ❌ **Failure/not supported**: Something doesn't work
- ⚠️ **Warning**: Pay attention to this
- ℹ️ **Information**: Note for reference
- 🔶 **Caution**: Proceed carefully
- 📖 **Read**: This is important

### Progress Indicators

- 📖 **Read**: Read through this guide
- 🔧 **Setup**: Execute setup commands
- 🚀 **Deploy**: Run deployment
- ✅ **Validate**: Test that it works
- 🎤 **Integration**: Connect features together

---

## 🤝 Getting Help

### Within This Documentation

1. Use "Finding Specific Information" table (above) to find relevant section
2. Search for your error message in Part 4 "Troubleshooting Guide"
3. Check "Critical Knowledge Gaps" section for conceptual understanding

### Within Your Project

- Check project documentation: `/mnt/project/docs/`
- Review existing Docker/Podman configurations for patterns
- Check git history for similar implementations

### Online Resources

- **Vikunja Docs**: https://vikunja.io/docs/
- **Vikunja API**: `http://localhost/vikunja/api/v1/docs` (when running)
- **Podman Docs**: https://podman.io/docs/
- **Caddy Docs**: https://caddyserver.com/docs/

---

## 📊 Implementation Stats

**What You're Deploying**:
- **1** PostgreSQL container (database)
- **1** Vikunja container (API + Frontend bundled)
- **1** Caddy service (unified proxy)
- **3** Shared services (Redis, RAG, Chainlit)
- **~1 hour** of configuration files created
- **~50,000 words** of documentation provided

**What This Enables**:
- ✅ Full task management via UI and REST API
- ✅ Voice-driven task creation (framework ready)
- ✅ Knowledge base synchronization (Phase 2)
- ✅ Autonomous agent coordination (Phase 2+)
- ✅ Future scaling to team collaboration

---

## 🎓 Learning Outcomes

After completing this implementation, you will understand:

1. **Vikunja Architecture**: How bundled binaries work, API design, database schema
2. **Rootless Podman**: User namespaces, volume mounting, SELinux integration
3. **Container Networking**: Service-to-service communication, reverse proxies, port mapping
4. **Database Tuning**: PostgreSQL memory management for constrained environments
5. **REST API Integration**: Authentication, webhooks, event-driven architectures
6. **Secret Management**: Secure credential handling in containerized systems
7. **Multi-Service Orchestration**: Docker Compose overlays, modular stacks, health checks

**Skills Practiced**:
- Infrastructure as Code (docker-compose)
- Configuration Management (YAML, environment variables)
- Troubleshooting (logs, health checks, debugging)
- Security Hardening (rootless, capabilities, secrets)
- API Integration (REST, webhooks, authentication)

---

## 📋 Final Checklist

Before declaring "Done":

- [ ] All 5 documentation parts reviewed
- [ ] Pre-deployment checklist ✅ passed
- [ ] Part 2 setup completed
- [ ] Part 3 deployment successful
- [ ] Part 4 tests all passing
- [ ] Data persists across restarts
- [ ] Memory usage within budget
- [ ] All services healthy (`make health`)
- [ ] Can create/edit/delete tasks via UI and API
- [ ] Secrets not exposed in containers
- [ ] Changes committed to git

---

## 🎉 Congratulations!

You have successfully integrated **Vikunja task management** into your **Xoe-NovAi Foundation Stack**.

**Your next milestone**: Phase 2 voice integration (Part 5 provides the framework).

---

## 📞 Document Maintenance

**This manual is version 1.0** (2026-02-07)

**Future updates** should document:
- Vikunja version upgrades
- PostgreSQL optimization learnings
- Voice command feature additions
- Performance tuning insights
- Community integrations

---

## 🚀 Ready to Begin?

**Start here**: Open Part 1 and read the first section carefully.

**Then**: Follow the 5-part sequence in order (don't skip ahead).

**Finally**: Deploy, test, and enjoy your new task management system!

---

**Happy deploying!** 🎉

*For questions or clarifications, refer to the relevant part above, or consult the project lead.*

**Last Updated**: 2026-02-07  
**Maintainer**: Implementation Architecture Team  
**Status**: Production-Ready ✅
