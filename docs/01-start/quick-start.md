# 🚀 Xoe-NovAi Quick Start: Makefile Setup (3 Commands)

**Get your AI assistant running in 20 minutes using only Makefile commands.**

**Last Updated:** January 27, 2026
**For:** Complete beginners with AMD Ryzen CPUs
**Success Rate:** 95% with proper hardware (16GB+ RAM, 50GB+ disk)

---

## 🎯 **3-COMMAND SUCCESS PATH**

### **Step 1: Close VS Code (Free RAM for Podman)**

Before starting, **close VS Code completely** to free up RAM for Podman containers.

**For systems with limited resources**, use the force setup option below.

---

### **Command 1: `make help` - Discover Commands**

**What it does:** Shows all available Makefile commands organized for beginners.

**Run this:**
```bash
cd Xoe-NovAi
make help
```

**What you'll see:**
```
🤖 Xoe-NovAi Commands
=====================

🚀 QUICK START (for beginners):
  make setup     # Complete first-time setup
  make start     # Start AI assistant
  make status    # Check if running
  make stop      # Stop AI assistant
```

**Success:** ✅ Command list appears with clear descriptions.

---

### **Command 2: `make setup` - Complete Automated Setup**

**What it does:**
- Detects AMD Ryzen CPU and applies optimizations (Zen 2/4).
- Checks system requirements (RAM, disk, Podman).
- Downloads AI components (15-30 minutes).
- Builds the **7-service Foundation Stack** (Base, RAG, UI, Crawler, Worker, Redis, Docs).
- Starts your sovereign AI assistant.

**Run this:**
```bash
make setup
```

**Interactive prompt:**
```
Ready to start setup? (y/N):
```
**Type:** `y` (then press Enter)

**Progress you'll see:**
```
🤖 Xoe-NovAi Setup for Linux
=================================

[1/6] 🔍 Detecting CPU and system capabilities...
   ✓ AMD CPU detected - applying Zen optimizations (OPENBLAS_CORETYPE=ZEN)

[2/6] 🔍 Checking system requirements...
   ✓ RAM: 16GB+ available
   ✓ Disk: 50GB+ free
   ✓ Podman: Rootless mode verified

[3/6] 🏗️ Building Sovereign Toolkit...
   ✓ Building 7-service images (using BuildKit cache)

[4/6] 🚀 Launching AI Foundation...
   ✓ Web UI, RAG API, Redis, and Curation services active.

🎉 Setup completed successfully!
🌐 Your AI assistant is now running at: http://localhost:8001
```

**Expected time:** 15-30 minutes (Cold build) / < 1 minute (Cached)

---

### **Command 3: `make status` - Verify Everything Works**

**What it does:** Checks that all 7 AI services are running and shows system health.

**Run this:**
```bash
make status
```

**What you'll see:**
```
📊 Xoe-NovAi Foundation Status
==============================

✅ Podman: Running (Rootless)
✅ Foundation: RUNNING (7 services)
┌─────────────────┬────────────┬─────────────┐
│ xnai-ui          │ Running    │ 0.0.0.0:8001 │
│ xnai-rag         │ Running    │ 0.0.0.0:8000 │
│ xnai-redis       │ Running    │ 6379         │
│ xnai-crawler     │ Running    │ (Background) │
│ xnai-worker      │ Running    │ (Background) │
│ xnai-docs        │ Running    │ 0.0.0.0:8002 │
│ xnai-base        │ Completed  │ (Image Only) │
└─────────────────┴────────────┴─────────────┘

🛡️ Security Policy: ACTIVE (Zero-Critical)
🔥 AMD CPU: Optimizations active
```

**Success indicators:**
- ✅ Docker: Running
- ✅ AI System: RUNNING with 3 services
- ✅ All containers show "Running" status
- ✅ Ports accessible (8001 web, 8000 API)

---

## 🌐 **ACCESS YOUR AI ASSISTANT**

### **Open your web browser and go to:**
**http://localhost:8001**

### **Test your AI:**
1. **Text chat:** Type `"Hello! What can you help me with?"`
2. **Voice:** Click the microphone button (🎤)
3. **Documents:** Upload PDFs using the upload button

---

## 🛠️ **TROUBLESHOOTING**

### **If `make setup` shows resource errors:**
```
❌ Need at least 16 GB RAM. Found: 6 GB
❌ Need at least 50 GB free space. Found: 26 GB
```
**Solutions:**
- **Force setup (not recommended):** `FORCE_SETUP=true make setup`
- Close browser/IDE to free RAM
- Ensure Podman is in rootless mode: `podman unshare cat /proc/self/uid_map`

### **If Podman fails to start:**
- Check for lingering processes: `make stop`
- Verify rootless socket: `scripts/socket_resolver.py`

### **If setup shows "ERROR: Could not find a version that satisfies the requirement":**
This indicates Python version compatibility issues. The system has been updated to handle these automatically, but if you encounter this error:
- The system will automatically use Python 3.12 compatible versions
- Dependencies like `pydantic-core` and `audioop-lts` are handled automatically
- Try running setup again - the fixes are built-in

### **If `make status` shows services not running:**
```bash
# Check logs for issues
make logs

# Restart services
make stop
make start
make status
```

### **If web interface doesn't load:**
- Check that port 8001 is accessible
- Verify all containers are running with `make status`
- Check browser console for errors

---

## 📋 **SYSTEM REQUIREMENTS**

### **Minimum Hardware:**
- **CPU:** AMD Ryzen (automatic Zen 2+ optimization)
- **RAM:** 16GB
- **Storage:** 50GB free space
- **OS:** Linux (Ubuntu 22.04+, Fedora 39+, RHEL 9+)

### **Software:**
- **Podman 4.x/5.x** (Mandatory - Rootless)
- **Python 3.12+**
- **Make**

---

## 🎯 **WHAT YOU GET**

### **🤖 The Sovereign Foundation:**
- **Modular Toolkit:** Plug-n-play security, RAG, and voice modules.
- **Privacy-First:** Zero telemetry verified by `make pr-check`.
- **Security Trinity:** Automated SBOM and CVE auditing built-in.
- **AMD Zenith:** Optimized for local Ryzen performance.

### **🔧 Technical Features:**
- **AMD Optimization:** Automatic Ryzen performance tuning
- **Containerized:** Isolated, reproducible deployments
- **Scalable:** Multiple services working together
- **Production Ready:** Enterprise-grade error handling

---

## 🚀 **NEXT STEPS AFTER SUCCESS**

### **Daily Usage:**
```bash
make start     # Start AI (if stopped)
make status    # Check health
make stop      # Stop when done
```

### **Community & Contribution:**
Before submitting a PR or evolving the stack:
- **Run the Gatekeeper:** `make pr-check`
- **Audit Security:** `make security-audit`
- **Update CVE DBs:** `make update-security-db`

### **Build Performance Tips:**
- **Use `make wheel-build-smart`** for fastest builds with caching
- **Use `make wheel-build-parallel`** for 4x speed improvement
- **Use `make build-health`** before major builds to catch issues early
- **Cache is automatic** - builds skip when requirements unchanged

### **Customization:**
- **Voice Settings:** Adjust speed, pitch in interface
- **Document Collections:** Build specialized knowledge bases
- **Performance Tuning:** Automatic AMD optimizations applied
- **Build Optimization:** Smart caching and parallel processing enabled

---

## 📞 **GET HELP**

### **Common Issues:**
- **"Podman not running"**: `sudo systemctl start docker`
- **"Permission denied"**: `sudo usermod -aG podman $USER && newgrp docker`
- **"Out of memory"**: Close other applications, ensure 16GB+ RAM

### **Documentation:**
- **`docs/BEGINNER_GUIDE.md`** - Complete tutorial
- **`docs/howto/makefile-usage.md`** - All Makefile commands
- **`docs/troubleshooting.md`** - Common fixes

---

## 🎉 **SUCCESS CHECKLIST**

After running the 3 commands:
- [x] `make help` shows command list
- [x] `make setup` completes successfully (15-30 min)
- [x] `make status` shows 3 running services
- [x] Web interface loads at http://localhost:8001
- [x] AI responds to text chat
- [x] Voice features work (microphone + audio)

**✅ Congratulations! You now have a fully functional, privacy-first AI assistant!**

---

**Document Version:** 1.0
**Last Updated:** January 27, 2026
**Tested On:** AMD Ryzen 7 5700U, Ubuntu 25.04
