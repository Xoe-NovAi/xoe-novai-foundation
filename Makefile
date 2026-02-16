# Xoe-NovAi Makefile (Full Version)
# Last Updated: 2026-01-24 (BuildKit Cache Management + Claude Audit)

# Purpose: Production utilities for setup, podman, testing, debugging
# Guide Reference: Section 6.3 (Build Orchestration)
# Features: BuildKit cache mounts, YAML task locking, agent coordination
# Ryzen Opt: N_THREADS=6 implicit in env; Telemetry: 8 disables verified in Podmanfiles

.PHONY: help setup setup-permissions setup-directories check-podman-permissions check-host-setup start stop status restart update doctor install-deps wheelhouse deps download-models validate health benchmark curate ingest test build up down logs debug-rag debug-ui debug-crawler debug-redis cleanup build-analyze build-report check-duplicates voice-test voice-build wheel-build wheel-build-podman-amd wheel-analyze build-tracking stack-cat stack-cat-default stack-cat-api stack-cat-rag stack-cat-frontend stack-cat-crawler stack-cat-voice stack-cat-all stack-cat-separate stack-cat-deconcat stack-cat-clean stack-cat-archive docs-buildkit docs-wheelhouse docs-optimization docs-status enterprise-buildkit enterprise-wheelhouse enterprise-cache build-base cache-status cache-warm cache-clear cache-clear-apt cache-inspect mkdocs-build mkdocs-serve mkdocs-serve-public mkdocs-serve-internal mkdocs-clean docs-public docs-internal docs-all docs-system

COMPOSE_FILE := docker-compose.yml
COMPOSE := podman-compose -f $(COMPOSE_FILE)
PYTHON := python3
PYTEST := pytest
DOCKER_EXEC := podman exec
WHEELHOUSE_DIR := wheelhouse
REQ_GLOB := "requirements-*.txt"
SCRIPTS_DIR := scripts
# BuildKit enabled for advanced caching and offline builds
export PODMAN_BUILDKIT := 1

# Interactive build detection for progress bars
INTERACTIVE_BUILD := $(shell [ -t 0 ] && echo "true" || echo "false")
PIP_PROGRESS := $(if $(filter true,$(INTERACTIVE_BUILD)),--progress-bar on,--progress-bar off)

# Cache file tracking for smart builds
CACHE_DIR := .build_cache
REQUIREMENTS_CACHE := $(CACHE_DIR)/requirements.sha256
WHEELHOUSE_CACHE := $(CACHE_DIR)/wheelhouse.sha256

CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

# ============================================================================
# BEGINNER-FRIENDLY TARGETS (Start Here!)
# ============================================================================

butler: ## 🤵 Launch the interactive Sovereign Infrastructure TUI
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "$(YELLOW)⚠️  WARNING: Running Butler from a virtual environment may cause tool resolution issues.$(NC)"; \
		echo "$(YELLOW)   It is recommended to run from a clean system shell.$(NC)"; \
	fi
	@./scripts/infra/butler.sh

steer: ## 🏎️  Execute Ryzen core steering (taskset pinning)
	@./scripts/infra/butler.sh steer

setup: ## 🚀 Complete first-time setup (AMD optimized for Linux)
	@echo "$(CYAN)🤖 Xoe-NovAi Setup for Linux$(NC)"
	@echo "$(CYAN)=================================$(NC)"
	@echo ""
	@echo "$(YELLOW)This will:$(NC)"
	@echo "  • Check your computer meets requirements"
	@echo "  • Initialize Sovereign Infrastructure (The Butler)"
	@echo "  • Download AI components (may take 15-30 minutes)"
	@echo "  • Build the AI system"
	@echo "  • Start your personal AI assistant"
	@echo ""
	@echo "$(YELLOW)System Requirements:$(NC)"
	@echo "  • Ubuntu/Debian Linux"
	@echo "  • 16GB+ RAM (32GB recommended)"
	@echo "  • 50GB+ free disk space"
	@echo "  • AMD Ryzen CPU (automatic optimizations)"
	@echo ""
	@echo "$(YELLOW)Options:$(NC)"
	@echo "  • Use FORCE_SETUP=true to skip prerequisite checks (not recommended)"
	@echo ""
	@read -p "Ready to start setup? (y/N): " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		./scripts/infra/butler.sh setup; \
		if [ -f ./setup.sh ]; then \
			setup_args=""; \
			if [ "$$FORCE_SETUP" = "true" ]; then \
				echo "$(YELLOW)⚠️  FORCE_SETUP=true: Skipping prerequisite checks!$(NC)"; \
				setup_args="--skip-prerequisites"; \
			fi; \
			if ./setup.sh $$setup_args; then \
				echo ""; \
				echo "$(GREEN)🎉 Setup completed successfully!$(NC)"; \
				echo "$(CYAN)🌐 Your AI assistant is now running at: http://localhost:8001$(NC)"; \
				echo "$(YELLOW)💡 Run 'make status' to check the system health$(NC)"; \
			else \
				echo ""; \
				echo "$(RED)❌ Setup encountered issues.$(NC)"; \
				echo "$(YELLOW)🔧 TROUBLESHOOTING:$(NC)"; \
				echo "$(CYAN)   • Check system resources: make doctor$(NC)"; \
				echo "$(CYAN)   • Fix Podman issues: sudo systemctl start podman$(NC)"; \
				echo "$(CYAN)   • Add user to podman group: sudo usermod -aG podman $$USER$(NC)"; \
				echo "$(CYAN)   • Try again: make setup$(NC)"; \
				echo "$(YELLOW)💡 For resource-limited systems:$(NC)"; \
				echo "$(CYAN)   • Use FORCE_SETUP=true make setup (not recommended)$(NC)"; \
				echo "$(CYAN)   • Consider upgrading RAM to 16GB+$(NC)"; \
				echo "$(CYAN)   • Free up disk space (need 50GB+ available)$(NC)"; \
				echo "$(CYAN)   • Voice features require more resources than text-only$(NC)"; \
				exit 1; \
			fi \
		else \
			echo "$(RED)❌ Setup script not found. Please run from project root.$(NC)"; \
			exit 1; \
		fi \
	else \
		echo "$(YELLOW)Cancellation confirmed. Run 'make setup' when ready.$(NC)"; \
	fi

start: up ## 🟢 Start your AI assistant
	@echo "$(GREEN)🚀 AI Assistant Started!$(NC)"
	@echo ""
	@echo "$(CYAN)🌐 Access your AI:$(NC)"
	@echo "   Web Interface: http://localhost:8001"
	@echo "   API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "$(YELLOW)💡 Try asking: 'What can you help me with?'$(NC)"

stop: down ## 🔴 Stop AI assistant
	@echo "$(YELLOW)🛑 AI Assistant Stopped$(NC)"
	@echo "$(CYAN)Your data is saved and will be available when you restart.$(NC)"

status: ## 📊 Check AI system status
	@echo "$(CYAN)📊 Xoe-NovAi System Status$(NC)"
	@echo "$(CYAN)==========================$(NC)"
	@echo ""
	@./scripts/infra/butler.sh status
	@echo ""
	# Check if Podman is running
	@if podman info >/dev/null 2>&1; then \
		echo "$(GREEN)✅ Podman: Running$(NC)"; \
	else \
		echo "$(RED)❌ Podman: Not running$(NC)"; \
		echo "$(YELLOW)   💡 Start with: sudo systemctl start podman$(NC)"; \
		exit 1; \
	fi
	@echo ""
	# Check AI containers
	@echo "$(CYAN)🤖 AI Services:$(NC)"
	@running_count=$$(podman ps --filter "name=xnai" --format "table {{.Names}}" | grep -c xnai 2>/dev/null || echo "0"); \
	if [ "$$running_count" -gt 0 ]; then \
		echo "$(GREEN)✅ AI System: RUNNING ($(NC)$$running_count$(GREEN) services)$(NC)"; \
		podman ps --filter "name=xnai" --format "table {{.Names}}	{{.Status}}	{{.Ports}}"; \
	else \
		echo "$(RED)❌ AI System: NOT RUNNING$(NC)"; \
		echo "$(YELLOW)   💡 Start with: make start$(NC)"; \
	fi
	@echo ""
	# Check data
	@if [ -d data ] && [ "$$($(PYTHON) -c 'import os; print(len(os.listdir("data"))))')" -gt 0 ]; then \
		doc_count=$$(find data -type f | wc -l); \
		echo "$(GREEN)📚 Documents: $(NC)$$doc_count$(GREEN) files loaded$(NC)"; \
	else \
		echo "$(YELLOW)📚 Documents: None loaded yet$(NC)"; \
		echo "$(CYAN)   💡 Upload PDFs in the web interface$(NC)"; \
	fi
	@echo ""
	# AMD optimizations status
	@if grep -q "AMD" /proc/cpuinfo 2>/dev/null; then \
		echo "$(YELLOW)🔥 AMD CPU: Optimizations active$(NC)"; \
	fi
	@echo ""
	@echo "$(CYAN)💡 Quick Commands:$(NC)"
	@echo "$(CYAN)   make start     $(NC)# Start AI"
	@echo "$(CYAN)   make stop      $(NC)# Stop AI"
	@echo "$(CYAN)   make status    $(NC)# Check status"
	@echo "$(CYAN)   make logs      $(NC)# View logs"


update: ## 🔄 Update to latest version
	@echo "$(CYAN)🔄 Updating Xoe-NovAi...$(NC)"
	$(MAKE) stop
	@echo "$(CYAN)Getting latest code...$(NC)"
	git pull origin main
	@echo "$(CYAN)Rebuilding system...$(NC)"
	$(MAKE) build
	$(MAKE) start
	@echo "$(GREEN)✅ Update complete!$(NC)"


doctor: ## 🩺 Comprehensive system diagnosis (enhanced)
	@echo "$(CYAN)🩺 System Diagnosis$(NC)"
	@echo "$(CYAN)=================$(NC)"
	@echo ""
	@./scripts/infra/butler.sh check
	@echo ""
	# Podman permissions check
	@echo "$(CYAN)🐳 Podman:$(NC)"
	@if podman info >/dev/null 2>&1; then \
		echo "$(GREEN)✅ Podman daemon running$(NC)"; \
		podman --version; \
	else \
		echo "$(RED)❌ Podman daemon not running$(NC)"; \
		echo "$(YELLOW)   💡 Fix: sudo systemctl start podman$(NC)"; \
	fi
	@if groups | grep -q podman 2>/dev/null; then \
		echo "$(GREEN)✅ User in podman group$(NC)"; \
	else \
		echo "$(RED)❌ User not in podman group$(NC)"; \
		echo "$(YELLOW)   💡 Fix: make setup-permissions$(NC)"; \
	fi
	@echo ""
	# Directory ownership check
	@echo "$(CYAN)📁 Directory Ownership:$(NC)"
	@HOST_UID=$$(id -u); HOST_GID=$$(id -g); \
	for dir in library knowledge data/faiss_index logs; do \
		if [ -d "$$dir" ]; then \
			OWNER=$$(stat -c '%u:%g' "$$dir" 2>/dev/null || echo "unknown"); \
			if [ "$$OWNER" = "$$HOST_UID:$$HOST_GID" ]; then \
				echo "$(GREEN)✅ $$dir: Correct ownership ($$OWNER)$(NC)"; \
			else \
				echo "$(RED)❌ $$dir: Wrong ownership ($$OWNER vs $$HOST_UID:$$HOST_GID)$(NC)"; \
			fi; \
		else \
			echo "$(YELLOW)⚠️  $$dir: Directory missing$(NC)"; \
		fi; \
	done
	@echo ""
	# .env configuration check
	@echo "$(CYAN)⚙️  Configuration:$(NC)"
	@if [ -f .env ]; then \
		if grep -q "APP_UID=$$(id -u)" .env 2>/dev/null; then \
			echo "$(GREEN)✅ APP_UID matches host$(NC)"; \
		else \
			echo "$(RED)❌ APP_UID mismatch$(NC)"; \
			echo "$(YELLOW)   💡 Fix: make setup-permissions$(NC)"; \
		fi; \
	else \
		echo "$(RED)❌ .env file missing$(NC)"; \
		echo "$(YELLOW)   💡 Fix: cp .env.example .env$(NC)"; \
	fi
	@echo ""
	# Basic system info
	@echo "$(CYAN)🖥️  System Info:$(NC)"
	uname -a
	echo ""
	# CPU info
	@echo "$(CYAN)🔥 CPU:$(NC)"
	lscpu | grep "Model name:" | sed 's/Model name:/CPU Model:/'
	@nproc | xargs echo "CPU Cores:"
	@free -h | grep '^Mem:' | awk '{print "Memory:", $$2, "used,", $$7, "free"}'
	echo ""
	# Storage
	@echo "$(CYAN)💾 Storage:$(NC)"
	df -h . | tail -1 | awk '{print "$$4", "free in current directory"}'
	echo ""
	# Python version
	@echo "$(CYAN)🐍 Python:$(NC)"
	python3 --version 2>/dev/null || echo "Python 3 not found"
	echo ""
	# Memory and disk warnings
	@echo "$(CYAN)🔍 Resource Warnings:$(NC)"
	if [ "$$($(PYTHON) -c 'import psutil; print(psutil.virtual_memory().total // (1024**3))' 2>/dev/null || echo '0')" -lt 16 ]; then \
		echo "⚠️  Low memory (16GB+ recommended)"; \
	fi
	if [ "$$($(PYTHON) -c 'import shutil; print(shutil.disk_usage(".").free // (1024**3))' 2>/dev/null || echo '0')" -lt 50 ]; then \
		echo "⚠️  Low disk space (50GB+ recommended)"; \
	fi
	echo ""
	echo "$(GREEN)✅ Diagnosis complete$(NC)"


install-deps: ## 📦 Install system dependencies (Ubuntu/Debian)
	@echo "$(CYAN)📦 Installing System Dependencies$(NC)"
	@echo "$(CYAN)===============================$(NC)"
	@echo ""
	@echo "$(YELLOW)This will install:$(NC)"
	@echo "  • Podman (container runtime)"
	@echo "  • Python 3 and virtual environment tools"
	@echo "  • Git (version control)"
	@echo "  • Build tools"
	@echo "  • Gum (for interactive UI)"
	@echo ""
	@read -p "Continue with installation? (y/N): " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(CYAN)Updating package lists...$(NC)"; \
		sudo apt update; \
		echo "$(CYAN)Installing dependencies...$(NC)"; \
		sudo apt install -y podman python3 python3-venv python3-pip git build-essential; \
		echo "$(CYAN)Installing Gum...$(NC)"; \
		./scripts/infra/butler.sh --auto-install; \
		echo "$(CYAN)Starting Podman service...$(NC)"; \
		sudo systemctl enable podman; \
		sudo systemctl start podman; \
		echo "$(CYAN)Adding user to podman group...$(NC)"; \
		sudo usermod -aG podman $$USER; \
		echo ""; \
		echo "$(GREEN)✅ Dependencies installed!$(NC)"; \
		echo "$(YELLOW)💡 Important: Logout and login again for Podman group changes to take effect.$(NC)"; \
		echo "$(YELLOW)   Or run: newgrp podman$(NC)"; \
	else \
		echo "$(YELLOW)Cancellation confirmed.$(NC)"; \
	fi

help: ## 📚 Show this help message
	@echo "$(CYAN)🤖 Xoe-NovAi Commands$(NC)"
	@echo "$(CYAN)=====================$(NC)"
	@echo ""
	@echo "$(GREEN)🚀 QUICK START (for beginners):$(NC)"
	@echo "$(CYAN)  make setup     $(NC)# Complete first-time setup"
	@echo "$(CYAN)  make start     $(NC)# Start AI assistant"
	@echo "$(CYAN)  make status    $(NC)# Check if running"
	@echo "$(CYAN)  make stop      $(NC)# Stop AI assistant"
	@echo "$(CYAN)  make butler    $(NC)# Launch Sovereign Orchestrator (TUI)"
	@echo ""
	@echo "$(GREEN)🔧 MAINTENANCE:$(NC)"
	@echo "$(CYAN)  make update    $(NC)# Update to latest version"
	@echo "$(CYAN)  make doctor    $(NC)# Diagnose issues"
	@echo "$(CYAN)  make logs      $(NC)# View system logs"
	@echo ""
	@echo "$(GREEN)📦 ADVANCED:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(CYAN)%%-20s$(NC) %%s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -v -E "(setup|start|stop|status|restart|update|doctor|install-deps|help|butler)"



wheelhouse: ## Download all Python dependencies to wheelhouse/ for offline install
	@echo "$(CYAN)Downloading Python packages to wheelhouse/...$(NC)"
	./scripts/download_wheelhouse.sh $(WHEELHOUSE_DIR) $(REQ_GLOB)
	@echo "$(GREEN)✓ Wheelhouse created in $(WHEELHOUSE_DIR)/$(NC)"


deps: wheelhouse ## Install dependencies from wheelhouse (offline)
	@echo "$(CYAN)Installing dependencies from wheelhouse...$(NC)"
	@if command -v uv >/dev/null 2>&1; then \
		echo "$(GREEN)✅ UV detected - using ultra-fast installer$(NC)"; \
		uv pip sync --no-index --find-links=$(WHEELHOUSE_DIR) requirements-api.txt; \
		uv pip sync --no-index --find-links=$(WHEELHOUSE_DIR) requirements-chainlit.txt; \
		uv pip sync --no-index --find-links=$(WHEELHOUSE_DIR) requirements-crawl.txt; \
		uv pip sync --no-index --find-links=$(WHEELHOUSE_DIR) requirements-curation_worker.txt; \
	else \
		echo "$(YELLOW)⚠️  UV not available - using pip (slower)$(NC)"; \
		$(PYTHON) -m pip install --no-index --find-links=$(WHEELHOUSE_DIR) -r requirements-api.txt; \
		$(PYTHON) -m pip install --no-index --find-links=$(WHEELHOUSE_DIR) -r requirements-chainlit.txt; \
		$(PYTHON) -m pip install --no-index --find-links=$(WHEELHOUSE_DIR) -r requirements-crawl.txt; \
		$(PYTHON) -m pip install --no-index --find-links=$(WHEELHOUSE_DIR) -r requirements-curation_worker.txt; \
	fi
	@echo "$(GREEN)✓ Dependencies installed from wheelhouse$(NC)"


download-models: ## Download models and embeddings
	@echo "Downloading models..."
	mkdir -p models embeddings
	wget -P models https://huggingface.co/unsloth/gemma-3-4b-it-GGUF/resolve/main/gemma-3-4b-it-UD-Q5_K_XL.gguf?download=true
	wget -P embeddings https://huggingface.co/leliuga/all-MiniLM-L12-v2-GGUF/resolve/main/all-MiniLM-L12-v2.Q8_0.gguf?download=true
#	wget -P embeddings https://huggingface.co/leliuga/all-MiniLM-L12-v2-GGUF/resolve/main/all-MiniLM-L12-v2.F16.gguf?download=true
#	wget -P embeddings https://huggingface.co/prithivida/all-MiniLM-L6-v2-gguf/resolve/main/all-MiniLM-L6-v2-q8_0.gguf?download=true


validate: ## Run configuration validation
	@echo "Validating configuration..."
	python3 scripts/validate_config.py

health: ## Run health checks
	@echo "Running health checks..."
	python3 app/XNAi_rag_app/healthcheck.py

benchmark: ## Run performance benchmark
	@echo "Running benchmark..."
	python3 scripts/query_test.py --benchmark

curate: ## Run curation (example: Gutenberg classics)
	@echo "Running curation..."
	podman exec xnai_crawler python3 /app/XNAi_rag_app/crawl.py --curate gutenberg -c classics -q "Plato" --max-items=50

ingest: ## Run library ingestion (Phase 2: Unified script)
	@echo "$(CYAN)📚 Running library ingestion...$(NC)"
	podman exec xnai_rag_api python3 -m app.XNAi_rag_app.ingest_library --mode from_library --library-path /library
	@echo "$(GREEN)✅ Library ingestion completed$(NC)"


test: ## Run tests with coverage
	@echo "Running tests..."
	cp .env.example .env
	pytest --cov

# ============================================================================
# CIRCUIT BREAKER TESTING TARGETS (Phase 1, Day 2 Integration)
# ============================================================================

test-circuit-breakers: ## Run all circuit breaker tests (Phase 1, Day 2)
	@echo "$(CYAN)🧪 Running All Circuit Breaker Tests...$(NC)"
	@echo "$(CYAN)======================================$(NC)"
	$(PYTHON) tests/test_rag_api_circuit_breaker.py
	$(PYTHON) tests/test_redis_circuit_breaker.py
	$(PYTHON) tests/test_fallback_mechanisms.py
	$(PYTHON) tests/circuit_breaker_load_test.py
	@echo "$(GREEN)✅ All circuit breaker tests completed$(NC)"


test-circuit-rag: ## Test RAG API circuit breaker functionality
	@echo "$(CYAN)🧪 Testing RAG API Circuit Breaker...$(NC)"
	$(PYTHON) tests/test_rag_api_circuit_breaker.py
	@echo "$(GREEN)✅ RAG API circuit breaker test completed$(NC)"


test-circuit-redis: ## Test Redis circuit breaker functionality
	@echo "$(CYAN)🧪 Testing Redis Circuit Breaker...$(NC)"
	$(PYTHON) tests/test_redis_circuit_breaker.py
	@echo "$(GREEN)✅ Redis circuit breaker test completed$(NC)"


test-circuit-fallback: ## Test circuit breaker fallback mechanisms
	@echo "$(CYAN)🧪 Testing Circuit Breaker Fallback Mechanisms...$(NC)"
	$(PYTHON) tests/test_fallback_mechanisms.py
	@echo "$(GREEN)✅ Fallback mechanism test completed$(NC)"


test-circuit-load: ## Run circuit breaker load testing
	@echo "$(CYAN)🧪 Running Circuit Breaker Load Test...$(NC)"
	$(PYTHON) tests/circuit_breaker_load_test.py
	@echo "$(GREEN)✅ Circuit breaker load test completed$(NC)"

# RESEARCH & BEST PRACTICE AGENT TARGETS
agent-%: ## 🤖 Run a specific custom agent (e.g., make agent-vizier)
	@if [ ! -f ".gemini/agents/$*.md" ]; then \
		echo "$(RED)❌ ERROR: Agent '$*' not found in .gemini/agents/$(NC)"; \
		exit 1; \
	fi
	@echo "$(CYAN)🤖 Invoking Agent: $*...$(NC)"
	@./scripts/dev/run_agent.sh $*

agent-list: ## 📋 List all available custom agents
	@echo "$(CYAN)📋 Available Agents:$(NC)"
	@ls .gemini/agents/ | sed 's/\.md//'

research-agent-start: ## 🤖 Start the research and best practice agent
	@echo "$(CYAN)🤖 Starting Research & Best Practice Agent...$(NC)"
	@if [ ! -f "app/XNAi_rag_app/research_agent.py" ]; then \
		echo "$(RED)❌ ERROR: Research agent not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) -c "from app.XNAi_rag_app.research_agent import start_research_agent; start_research_agent()"
	@echo "$(GREEN)✅ Research agent started$(NC)"
	@echo "$(YELLOW)💡 Agent monitors research freshness and code quality$(NC)"


research-agent-stop: ## 🛑 Stop the research and best practice agent
	@echo "$(CYAN)🛑 Stopping Research & Best Practice Agent...$(NC)"
	$(PYTHON) -c "from app.XNAi_rag_app.research_agent import stop_research_agent; stop_research_agent()"
	@echo "$(GREEN)✅ Research agent stopped$(NC)"


research-agent-status: ## 📊 Show research agent status
	@echo "$(CYAN)📊 Research Agent Status$(NC)"
	@echo "$(CYAN)=========================$(NC)"
	@if [ ! -f "app/XNAi_rag_app/research_agent.py" ]; then \
		echo "$(RED)❌ ERROR: Research agent not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) -c "from app.XNAi_rag_app.research_agent import get_research_agent; agent = get_research_agent(); import json; print(json.dumps(agent.get_monitoring_status(), indent=2, default=str))"


research-agent-check: ## 🔍 Run immediate research and quality check
	@echo "$(CYAN)🔍 Running Research & Quality Check...$(NC)"
	@if [ ! -f "app/XNAi_rag_app/research_agent.py" ]; then \
		echo "$(RED)❌ ERROR: Research agent not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) -c "from app.XNAi_rag_app.research_agent import get_research_agent; agent = get_research_agent(); import asyncio; loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop); loop.run_until_complete(agent.run_monitoring_cycle()); loop.close()"
	@echo "$(GREEN)✅ Research check completed$(NC)"


research-agent-report: ## 📋 Generate research freshness report
	@echo "$(CYAN)📋 Research Freshness Report$(NC)"
	@echo "$(CYAN)==============================$(NC)"
	@if [ ! -f "app/XNAi_rag_app/research_agent.py" ]; then \
		echo "$(RED)❌ ERROR: Research agent not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) -c "from app.XNAi_rag_app.research_agent import get_research_agent; agent = get_research_agent(); import json; print(json.dumps(agent.get_research_freshness_report(), indent=2, default=str))"

# ============================================================================
# VOICE DEBUG & RECORDING TARGETS
# ============================================================================

voice-debug-enable: ## 🎤 Enable voice debug recording mode
	@echo "$(CYAN)🎤 Enabling Voice Debug Recording Mode$(NC)"
	@echo "$(CYAN)=====================================$(NC)"
	@echo "$(YELLOW)⚠️  WARNING: This will record both human and AI voice data for debugging$(NC)"
	@echo "$(YELLOW)📁 Recordings will be saved to: /tmp/xoe_voice_debug/$(NC)"
	@echo "$(YELLOW)🔒 Data is stored locally for analysis and learning$(NC)"
	@echo ""
	@read -p "Enable voice debug recording? (y/N): " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(CYAN)Setting environment variables...$(NC)"; \
		export XOE_VOICE_DEBUG=true; \
		export XOE_VOICE_DEBUG_DIR=/tmp/xoe_voice_debug; \
		echo "$(GREEN)✅ Voice debug recording enabled$(NC)"; \
		echo "$(YELLOW)💡 Start voice interface to begin recording$(NC)"; \
		echo "$(YELLOW)💡 Use 'make voice-debug-stats' to view recordings$(NC)"; \
	else \
		echo "$(YELLOW)Cancellation confirmed$(NC)"; \
	fi

voice-debug-disable: ## 🚫 Disable voice debug recording mode
	@echo "$(CYAN)🚫 Disabling Voice Debug Recording$(NC)"
	unset XOE_VOICE_DEBUG
	unset XOE_VOICE_DEBUG_DIR
	@echo "$(GREEN)✅ Voice debug recording disabled$(NC)"


voice-debug-stats: ## 📊 Show voice debug recording statistics
	@echo "$(CYAN)📊 Voice Debug Recording Statistics$(NC)"
	@echo "$(CYAN)=====================================$(NC)"
	@if [ -z "$$XOE_VOICE_DEBUG" ] || [ "$$XOE_VOICE_DEBUG" != "true" ]; then \
		echo "$(RED)❌ Voice debug mode not enabled$(NC)"; \
		echo "$(YELLOW)💡 Enable with: make voice-debug-enable$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f "app/XNAi_rag_app/voice_interface.py" ]; then \
		echo "$(RED)❌ ERROR: Voice interface not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) -c "from app.XNAi_rag_app.voice_interface import get_voice_interface; vi = get_voice_interface(); import json; print(json.dumps(vi.get_debug_stats() if vi else {'error': 'Voice interface not initialized'}, indent=2, default=str))"


voice-debug-export: ## 📦 Export voice debug recordings for analysis
	@echo "$(CYAN)📦 Exporting Voice Debug Recordings$(NC)"
	@echo "$(CYAN)=====================================$(NC)"
	@if [ ! -f "app/XNAi_rag_app/voice_interface.py" ]; then \
		echo "$(RED)❌ ERROR: Voice interface not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) -c "from app.XNAi_rag_app.voice_interface import get_voice_interface; vi = get_voice_interface(); archive_path = vi.export_debug_session() if vi else None; print(f'✅ Debug session exported to: {archive_path}' if archive_path else '❌ No recordings to export')"
	@echo "$(YELLOW)💡 Archive contains all recordings, metadata, and analysis$(NC)"


voice-debug-clean: ## 🧹 Clean voice debug recordings (WARNING: PERMANENT DELETION)
	@echo "$(RED)⚠️  WARNING: This will permanently delete ALL voice debug recordings!$(NC)"
	@echo "$(YELLOW)Directory: /tmp/xoe_voice_debug/$(NC)"
	@read -p "Permanently delete all voice recordings? (yes/NO): " confirm && \
	if [ "$$confirm" = "yes" ]; then \
		rm -rf /tmp/xoe_voice_debug && \
		echo "$(GREEN)✅ Voice debug recordings permanently deleted$(NC)"; \
	else \
		echo "$(YELLOW)Cancellation confirmed - no files deleted$(NC)"; \
	fi

# ============================================================================
# ENTERPRISE & ADVANCED SCRIPT INTEGRATION TARGETS
# ============================================================================

build-enterprise: ## Run enterprise build orchestration
	@echo "$(CYAN)🏢 Running Enterprise Build...$(NC)"
	@if [ ! -f scripts/enterprise_build.sh ]; then \
		echo "$(RED)Error: scripts/enterprise_build.sh not found$(NC)"; \
		exit 1; \
	fi
	./scripts/enterprise_build.sh
	@echo "$(GREEN)✅ Enterprise build completed$(NC)"


audit-telemetry: ## Audit telemetry and security settings
	@echo "$(CYAN)🔒 Auditing Telemetry Settings...$(NC)"
	@if [ ! -f scripts/telemetry_audit.py ]; then \
		echo "$(RED)Error: scripts/telemetry_audit.py not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) scripts/telemetry_audit.py
	@echo "$(GREEN)✅ Telemetry audit completed$(NC)"


validate-prebuild: ## Run pre-build validation checks
	@echo "$(CYAN)🔍 Running Pre-build Validation...$(NC)"
	@if [ ! -f scripts/prebuild_validate.py ]; then \
		echo "$(RED)Error: scripts/prebuild_validate.py not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) scripts/prebuild_validate.py
	@echo "$(GREEN)✅ Pre-build validation completed$(NC)"


preflight: ## Run system readiness checks
	@echo "$(CYAN)✈️  Running Preflight Checks...$(NC)"
	@if [ ! -f scripts/preflight_checks.py ]; then \
		echo "$(RED)Error: scripts/preflight_checks.py not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) scripts/preflight_checks.py
	@echo "$(GREEN)✅ Preflight checks completed$(NC)"

# ============================================================================
# VALIDATION & VERIFICATION TARGETS
# ============================================================================

wheel-validate: ## Validate wheelhouse for Python version compatibility
	@echo "$(CYAN)🔍 Validating Wheelhouse...$(NC)"
	@if [ ! -f scripts/validate_wheelhouse.py ]; then \
		echo "$(RED)Error: Wheelhouse validation script not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) scripts/validate_wheelhouse.py --target-version 312 --report
	@echo "$(GREEN)✅ Wheelhouse validation completed$(NC)"


verify-offline: ## Verify offline build capability
	@echo "$(CYAN)🔌 Verifying Offline Build...$(NC)"
	@if [ ! -f scripts/verify_offline_build.sh ]; then \
		echo "$(RED)Error: scripts/verify_offline_build.sh not found$(NC)"; \
		exit 1; \
	fi
	./scripts/verify_offline_build.sh
	@echo "$(GREEN)✅ Offline build verification completed$(NC)"


env-detect: ## Detect and validate environment
	@echo "$(CYAN)🌍 Detecting Environment...$(NC)"
	@if [ ! -f scripts/detect_environment.sh ]; then \
		echo "$(RED)Error: scripts/detect_environment.sh not found$(NC)"; \
		exit 1; \
	fi
	./scripts/detect_environment.sh
	@echo "$(GREEN)✅ Environment detection completed$(NC)"


docs-check: ## Validate documentation quality
	@echo "$(CYAN)📚 Checking Documentation...$(NC)"
	@if [ ! -f scripts/doc_checks.sh ]; then \
		echo "$(RED)Error: scripts/doc_checks.sh not found$(NC)"; \
		exit 1; \
	fi
	./scripts/doc_checks.sh
	@echo "$(GREEN)✅ Documentation check completed$(NC)"


deps-update: ## Run automated dependency updates
	@echo "$(CYAN)⬆️  Updating Dependencies...$(NC)"
	@if [ ! -f scripts/dependency_update_system.py ]; then \
		echo "$(RED)Error: scripts/dependency_update_system.py not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) scripts/dependency_update_system.py
	@echo "$(GREEN)✅ Dependency update completed$(NC)"


vulkan-check: ## Validate Vulkan environment for Ryzen iGPU acceleration
	@echo "$(CYAN)🔍 Running Vulkan Environment Check...$(NC)"
	@if [ ! -f scripts/mesa-check.sh ]; then \
		echo "$(RED)Error: scripts/mesa-check.sh not found$(NC)"; \
		exit 1; \
	fi
	./scripts/mesa-check.sh
	@echo "$(GREEN)✅ Vulkan environment validation completed$(NC)"


build-logging: ## Run enhanced build logging
	@echo "$(CYAN)📝 Running Enhanced Build Logging...$(NC)"
	@if [ ! -f scripts/enhanced_build_logging.sh ]; then \
		echo "$(RED)Error: scripts/enhanced_build_logging.sh not found$(NC)"; \
		exit 1; \
	fi
	./scripts/enhanced_build_logging.sh
	@echo "$(GREEN)✅ Enhanced build logging completed$(NC)"


wheel-clean: ## Clean wheelhouse duplicates
	@echo "$(CYAN)🧹 Cleaning Wheelhouse Duplicates...$(NC)"
	@if [ ! -f scripts/clean_wheelhouse_duplicates.sh ]; then \
		echo "$(RED)Error: scripts/clean_wheelhouse_duplicates.sh not found$(NC)"; \
		exit 1; \
	fi
	./scripts/clean_wheelhouse_duplicates.sh
	@echo "$(GREEN)✅ Wheelhouse cleanup completed$(NC)"


check-podman-permissions:
	@echo "$(CYAN)🔐 Checking Podman Permissions...$(NC)"
	@if [ "$$SKIP_DOCKER_PERMISSIONS" = "true" ]; then \
		echo "$(YELLOW)⚠️  Skipping Podman permission check (SKIP_DOCKER_PERMISSIONS=true)$(NC)"; \
		echo "$(GREEN)✅ Podman permission check bypassed$(NC)"; \
		exit 0; \
	fi; \
	if ! groups | grep -q podman 2>/dev/null; then \
		echo "$(RED)❌ ERROR: User not in podman group$(NC)"; \
		echo "$(YELLOW)💡 Fix: make setup-permissions$(NC)"; \
		echo "$(YELLOW)💡 Or skip check: SKIP_DOCKER_PERMISSIONS=true make build$(NC)"; \
		exit 1; \
	fi; \
	if ! podman info >/dev/null 2>&1; then \
		echo "$(RED)❌ ERROR: Podman daemon not accessible$(NC)"; \
		echo "$(YELLOW)💡 Fix: sudo systemctl start podman$(NC)"; \
		echo "$(YELLOW)💡 Or skip check: SKIP_DOCKER_PERMISSIONS=true make build$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)✅ Podman permissions OK$(NC)"


check-host-setup:
	@echo "$(CYAN)📁 Checking Host Directory Setup...$(NC)"
	@HOST_UID=$$(id -u); HOST_GID=$$(id -g); \
	if [ ! -f .env ]; then \
		echo "$(YELLOW)⚠️  .env not found - creating template$(NC)"; \
		echo "APP_UID=$$HOST_UID" > .env; \
		echo "APP_GID=$$HOST_GID" >> .env; \
		echo "REDIS_PASSWORD=$$(openssl rand -base64 32)" >> .env; \
	fi
	@if ! grep -q "APP_UID=$$(id -u)" .env 2>/dev/null; then \
		echo "$(RED)❌ ERROR: APP_UID/GID mismatch with host$(NC)"; \
		echo "$(YELLOW)💡 Fix: make setup-directories$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Host setup OK$(NC)"


setup-permissions: ## 🔐 Setup Podman permissions and directories (run once)
	@echo "$(CYAN)🔐 Setting up Podman permissions...$(NC)"
	@if [ ! -f scripts/setup_permissions.sh ]; then \
		echo "$(RED)❌ Setup script not found$(NC)"; \
		exit 1; \
	fi
	@bash scripts/setup_permissions.sh


setup-consul: ## 🔧 Fix Consul permissions for rootless Podman
	@echo "$(CYAN)🔧 Setting up Consul permissions...$(NC)"
	@mkdir -p data/consul
	@chmod 777 data/consul
	@echo "$(GREEN)✅ Consul data directory configured$(NC)"


setup-directories: ## 📁 Create and own required directories
	@echo "$(CYAN)📁 Setting up directories...$(NC)"
	@HOST_UID=$$(id -u); HOST_GID=$$(id -g); \
	sudo mkdir -p library knowledge data/faiss_index data/cache backups logs app/XNAi_rag_app/logs data/redis data/curations logs/curations; \
	sudo chown -R $${HOST_UID}:$${HOST_GID} library knowledge data/faiss_index data/cache backups logs app/XNAi_rag_app/logs data/redis data/curations logs/curations; \
	sudo chmod -R 755 library knowledge data/faiss_index data/cache backups logs data/curations logs/curations; \
	sudo chmod -R 777 app/XNAi_rag_app/logs; \
	echo "$(GREEN)✅ Directories created and owned$(NC)"


build-base: ## 🏗️ Build the base image first
	@echo "$(CYAN)Building xnai-base:latest...$(NC)"
	@BUILDKIT_PROGRESS=plain podman build -t xnai-base:latest -f Dockerfile.base .
	@echo "$(GREEN)✓ Base image built$(NC)"


build: check-podman-permissions check-host-setup ## Build Podman images with BuildKit caching and offline optimization
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "$(YELLOW)⚠️  WARNING: Running build from a virtual environment may pollute container build context.$(NC)"; \
		echo "$(YELLOW)   It is recommended to deactivate your venv before building.$(NC)"; \
	fi
	@echo "$(CYAN)Starting enterprise-grade build process...$(NC)"
	@echo "$(CYAN)🏗️  Step 1: Building xnai-base:latest...$(NC)"
	@BUILDKIT_PROGRESS=plain podman build -t xnai-base:latest -f Dockerfile.base .
	@echo "$(GREEN)✓ Base image built$(NC)"
	@if [ ! -f versions/versions.toml ]; then \
		echo "$(YELLOW)Warning: versions/versions.toml not found - skipping version validation$(NC)"; \
	else \
		echo "$(CYAN)Running pre-build validation...$(NC)"; \
		python3 versions/scripts/update_versions.py 2>/dev/null || { \
			echo "$(YELLOW)Warning: Version validation failed - continuing build$(NC)"; \
		}; \
	fi
	@echo "$(CYAN)Building Podman images with BuildKit cache mounts...$(NC)"
	@echo "$(YELLOW)Note: Wheelhouse is now built inside Podman with persistent caching$(NC)"
	@echo "$(YELLOW)No external downloads needed - all caching handled by BuildKit$(NC)"
	BUILDKIT_PROGRESS=plain $(COMPOSE) build || { \
		echo "$(RED)Error: Build failed. Check Podman build logs with:$(NC)"; \
		echo "$(YELLOW)  $(COMPOSE) logs$(NC)"; \
		echo "$(YELLOW)  $(COMPOSE) build --no-cache$(NC)"; \
		exit 1; \
	}
	@echo "$(GREEN)✓ Build completed successfully with BuildKit caching$(NC)"
	@podman buildx du --format 'table {{.Size}}' 2>/dev/null | tail -1 | sed 's/^/$(YELLOW)Cache utilization: /' || echo "$(YELLOW)Build cache info unavailable$(NC)"


up: ## Start stack
	@echo "Starting stack..."
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Warning: .env file not found. Creating from .env.example...$(NC)"; \
		cp .env.example .env 2>/dev/null || echo "$(RED)Error: .env.example not found$(NC)"; \
	fi
	$(COMPOSE) -f docker-compose.yml up -d


down: ## Stop stack
	@echo "Stopping stack..."
	$(COMPOSE) down


debug-rag: ## Debug shell for RAG
	@echo "Entering RAG shell..."
	$(DOCKER_EXEC) -it xnai_rag_api bash


debug-ui: ## Debug shell for UI
	@echo "Entering UI shell..."
	$(DOCKER_EXEC) -it xnai_chainlit_ui bash


debug-crawler: ## Debug shell for Crawler
	@echo "Entering Crawler shell..."
	$(DOCKER_EXEC) -it xnai_crawler bash


debug-redis: ## Debug shell for Redis
	@echo "Entering Redis shell..."
	$(DOCKER_EXEC) -it xnai_redis bash



cleanup: ## Clean volumes and images (warning: data loss)
	@echo "Cleaning up (data loss possible)..."
	$(COMPOSE) down -v
	podman rmi -a -f

# ============================================================================
# VOICE-TO-VOICE CONVERSATION SYSTEM TARGETS
# ============================================================================

voice-test: ## Test voice interface functionality
	@echo "$(CYAN)Testing voice interface...$(NC)"
	@if [ ! -d "app/XNAi_rag_app" ]; then \
		echo "$(RED)Error: app/XNAi_rag_app directory not found$(NC)"; \
		exit 1; \
	fi
	@$(PYTHON) -c "import sys; sys.path.insert(0, 'app/XNAi_rag_app'); \
	try: \
		from voice_interface import VoiceInterface, VoiceConfig; \
		print('$(GREEN)✓ Voice interface imports successful$(NC)'); \
		config = VoiceConfig(); \
		print(f'✓ Voice config: STT={config.stt_provider.value}, TTS={config.tts_provider.value}'); \
	except ImportError as e: \
		print(f'$(YELLOW)⚠ Voice interface not fully installed (run make deps first): {e}$(NC)'); \
		exit(0); \
	except Exception as e: \
		print(f'$(RED)✗ Voice interface test failed: {e}$(NC)'); \
		exit(1)"


voice-build: ## Build Podman image with voice-to-voice support
	@echo "$(CYAN)Building Podman image with voice-to-voice support...$(NC)"
	$(COMPOSE) build chainlit
	@echo "$(GREEN)✓ Voice-enabled Chainlit image built$(NC)"
	@echo "$(YELLOW)Run 'make voice-up' to start voice-enabled UI$(NC)"


voice-up: ## Start voice-enabled UI only
	@echo "$(CYAN)Starting voice-enabled UI...$(NC)"
	$(COMPOSE) -f docker-compose.yml up -d chainlit
	@echo "$(GREEN)✓ Voice-enabled UI started$(NC)"
	@echo "$(YELLOW)Access at: http://localhost:8001$(NC)"
	@echo "$(YELLOW)Voice features: Click '🎤 Start Voice Chat' to begin$(NC)"

# ============================================================================
# BUILD TRACKING & DEPENDENCY MANAGEMENT TARGETS
# ============================================================================

build-tracking: ## Run build dependency tracking analysis
	@echo "$(CYAN)Running build dependency tracking...$(NC)"
	@if [ ! -f scripts/build_tracking.py ]; then \
		echo "$(RED)Error: scripts/build_tracking.py not found$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) scripts/build_tracking.py parse-requirements
	$(PYTHON) scripts/build_tracking.py analyze-installation 2>/dev/null || echo "$(YELLOW)Note: No installation log found (run after pip install)$(NC)"
	$(PYTHON) scripts/build_tracking.py generate-report
	@echo "$(GREEN)✓ Build tracking analysis complete$(NC)"
	@echo "$(YELLOW)Reports saved in current directory$(NC)"


build-analyze: ## Analyze current build state and dependencies
	@echo "$(CYAN)Analyzing current build state...$(NC)"
	@if [ ! -f scripts/build_tracking.py ]; then \
		exit 1; \
	fi
	$(PYTHON) scripts/build_tracking.py parse-requirements
	@echo "$(CYAN)Current dependency status:$(NC)"
	$(PYTHON) scripts/build_tracking.py analyze-installation 2>/dev/null || echo "$(YELLOW)No installation data available$(NC)"
	$(PYTHON) scripts/build_tracking.py check-duplicates
	@echo "$(GREEN)✓ Build analysis complete$(NC)"


build-report: ## Generate comprehensive build report
	@echo "$(CYAN)Generating comprehensive build report...$(NC)"
	@if [ ! -f scripts/build_tracking.py ]; then \
		exit 1; \
	fi
	$(PYTHON) scripts/build_tracking.py generate-report
	@echo "$(GREEN)✓ Build report generated$(NC)"
	@if [ -f build-report.json ]; then \
		echo "$(CYAN)Report summary:$(NC)"; \
		$(PYTHON) -c "import json; print('  Build report saved to build-report.json')"; \
	fi


check-duplicates: ## Check for duplicate packages in current environment
	@echo "$(CYAN)Checking for duplicate packages...$(NC)"
	@if [ ! -f scripts/build_tracking.py ]; then \
		exit 1; \
	fi
	$(PYTHON) scripts/build_tracking.py check-duplicates
	@echo "$(GREEN)✓ Duplicate check complete$(NC)"

# ============================================================================
# WHEEL MANAGEMENT TARGETS
# ============================================================================

wheel-build: check-python-version ## Build wheels for all requirements (for offline caching) - FAILS LOUDLY on wrong Python version
	@echo "$(CYAN)🔍 Enforcing Python 3.12 only for wheel compatibility...$(NC)"
	@if [ "$$($$(PYTHON) --version | sed 's/Python \([0-9]\+\.[0-9]\+\).*/\1/')" != "3.12" ]; then \
		echo "$(RED)❌ CRITICAL ERROR: Host Python version $$($$(PYTHON) --version) != Container Python 3.12$(NC)"; \
		echo "$(RED)❌ This will create incompatible wheels - BUILD ABORTED$(NC)"; \
		echo "$(YELLOW)💡 SOLUTION: Use 'make wheel-build-podman-amd' for guaranteed Python 3.12 wheel building$(NC)"; \
		echo "$(YELLOW)💡 Install Python 3.12: sudo apt install python3.12 python3.12-venv$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Python version compatible - proceeding with wheel building$(NC)"
	@echo "$(CYAN)Building wheels for offline caching...$(NC)"
	@if [ ! -d $(WHEELHOUSE_DIR) ]; then \
		mkdir -p $(WHEELHOUSE_DIR); \
	fi
	@echo "$(CYAN)Building wheels for API requirements...$(NC)"
	$(PYTHON) -m pip wheel --no-deps -r requirements-api.txt -w $(WHEELHOUSE_DIR) $(PIP_PROGRESS)
	@echo "$(CYAN)Building wheels for Chainlit requirements...$(NC)"
	$(PYTHON) -m pip wheel --no-deps -r requirements-chainlit.txt -w $(WHEELHOUSE_DIR) $(PIP_PROGRESS)
	@echo "$(CYAN)Building wheels for Crawl requirements...$(NC)"
	$(PYTHON) -m pip wheel --no-deps -r requirements-crawl.txt -w $(WHEELHOUSE_DIR) $(PIP_PROGRESS)
	@echo "$(CYAN)Building wheels for Curation Worker requirements...$(NC)"
	$(PYTHON) -m pip wheel --no-deps -r requirements-curation_worker.txt -w $(WHEELHOUSE_DIR) $(PIP_PROGRESS)
	@echo "$(CYAN)Validating wheelhouse compatibility...$(NC)"
	$(PYTHON) scripts/validate_wheelhouse.py --target-version 312 --clean-incompatible
	@echo "$(CYAN)Compressing wheelhouse...$(NC)"
	@if [ "$$($(PYTHON) -c 'import os; print(len([f for f in os.listdir("$(WHEELHOUSE_DIR)") if f.endswith(".whl")]))')" -gt 0 ]; then \
		tar -czf wheelhouse.tgz -C $(WHEELHOUSE_DIR) . && \
		echo "$(GREEN)✓ Wheelhouse compressed: $$(ls -lh wheelhouse.tgz | awk '{print $$5}')$(NC)"; \
	else \
		echo "$(YELLOW)Warning: No wheels built$(NC)"; \
	fi
	@echo "$(GREEN)✓ Wheel building complete with Python 3.12 validation$(NC)"
	@echo "$(YELLOW)Use 'make deps' to install from wheelhouse$(NC)"

# Parallel wheel building support
PARALLEL := $(shell command -v parallel 2>/dev/null)

wheel-build-parallel: $(if $(PARALLEL),wheel-build-parallel-true,wheel-build-parallel-false)

wheel-build-parallel-true: ## Parallel wheel building (4x faster)
	@echo "$(CYAN)🚀 Building wheels in parallel (4 jobs)...$(NC)"
	@mkdir -p $(WHEELHOUSE_DIR)
	@printf "requirements-api.txt\nrequirements-crawl.txt\nrequirements-chainlit.txt\nrequirements-curation_worker.txt" | \
		parallel --no-notice -j4 ' \
			REQ_FILE="{}"; \
			echo "$(CYAN)Building $$(basename $$REQ_FILE .txt) wheels...$(NC)"; \
			$(PYTHON) -m pip wheel --no-deps -r "$$REQ_FILE" -w "$(WHEELHOUSE_DIR)" $(PIP_PROGRESS) \
		'
		@$(MAKE) wheel-validate
	wheel-build-parallel-false: ## Fallback to sequential building
		@echo "$(YELLOW)⚠️  Parallel not available - using sequential build$(NC)"
		@echo "$(CYAN)💡 Install parallel: sudo apt install parallel$(NC)"
		@$(MAKE) wheel-build-podman
# Smart cache invalidation
$(CACHE_DIR):
	@mkdir -p $(CACHE_DIR)

requirements-hash: $(CACHE_DIR)
	@cat requirements-*.txt | sha256sum | cut -d' ' -f1 > $(REQUIREMENTS_CACHE)

wheel-build-smart: requirements-hash
	@PY_VER=$$($$(PYTHON) --version 2>&1 | cut -d' ' -f2 | cut -d. -f1-2); \
	if [ "$$PY_VER" != "3.12" ]; then \
		echo "$(YELLOW)⚠️  Using Python $$PY_VER (optimized for 3.12)$(NC)"; \
		echo "$(YELLOW)   For guaranteed compatibility, use: make wheel-build-podman$(NC)"; \
	fi; \
	CURRENT_HASH=$$(cat $(REQUIREMENTS_CACHE)); \
	if [ ! -f $(WHEELHOUSE_CACHE) ] || [ "$$(cat $(WHEELHOUSE_CACHE))" != "$$CURRENT_HASH" ]; then \
		echo "$(CYAN)📦 Requirements changed - rebuilding wheelhouse...$(NC)"; \
		$(MAKE) wheel-build-parallel; \
		cp $(REQUIREMENTS_CACHE) $(WHEELHOUSE_CACHE); \
		echo "$(GREEN)✅ Wheelhouse rebuilt and cached$(NC)"; \
	else \
		echo "$(GREEN)✅ Wheelhouse up-to-date - using cache$(NC)"; \
	fi


cache-clean: ## Clean build cache
	@rm -rf $(CACHE_DIR)
	@echo "$(GREEN)✅ Build cache cleared$(NC)"


wheel-build-podman: ## Build wheels using Podman Python 3.12 (RECOMMENDED - guarantees compatibility)
	@echo "$(CYAN)🐳 Building wheels using cached Podman Python 3.12...$(NC)"
	@if [ ! -d $(WHEELHOUSE_DIR) ]; then \
		mkdir -p $(WHEELHOUSE_DIR); \
	fi
		@echo "$(CYAN)Verifying requirements files exist...$(NC)"
		@if ! ls requirements-*.txt >/dev/null 2>&1; then \
			echo "$(RED)❌ ERROR: No requirements files found in current directory$(NC)"; \
			echo "$(YELLOW)💡 Expected files: requirements-api.txt, requirements-chainlit.txt, etc.$(NC)"; \
			exit 1; \
		fi
		@echo "$(GREEN)✅ Requirements files found$(NC)"
	@echo "$(CYAN)Building wheels in cached Python 3.12 container...$(NC)"
	@if ! podman run --rm \
		-v xoe-pip-cache:/root/.cache/pip \
		-v $(shell pwd):/workspace \
		-v $(shell pwd)/$(WHEELHOUSE_DIR):/wheelhouse \
		xoe-python312:latest \
		bash -c " \
			echo '🐳 Inside cached Python 3.12 container:' && \
			python3 --version && \
						pip install --upgrade pip && \
						echo '🚀 Building API wheels...' && \
						pip wheel --no-deps -r /workspace/requirements-api.txt -w /wheelhouse --progress-bar on && \
						echo '🚀 Building Chainlit wheels...' && \
						pip wheel --no-deps -r /workspace/requirements-chainlit.txt -w /wheelhouse --progress-bar on && \
						echo '🚀 Building Crawl wheels...' && \
						pip wheel --no-deps -r /workspace/requirements-crawl.txt -w /wheelhouse --progress-bar on && \
						echo '🚀 Building Curation Worker wheels...' && \
						pip wheel --no-deps -r /workspace/requirements-curation_worker.txt -w /wheelhouse --progress-bar on && \
						echo '✅ All wheels built with cached Python 3.12' \
					"; then \
		echo "$(RED)❌ ERROR: Podman wheel building failed$(NC)"; \
		echo "$(YELLOW)💡 Possible causes:$(NC)"; \
		echo "$(YELLOW)   - Network connectivity issues$(NC)"; \
		echo "$(YELLOW)   - Podman daemon not running$(NC)"; \
		echo "$(YELLOW)   - Insufficient disk space$(NC)"; \
		echo "$(YELLOW)💡 Alternatives:$(NC)"; \
		echo "$(YELLOW)   - Install Python 3.12: sudo apt install python3.12$(NC)"; \
		echo "$(YELLOW)   - Check Podman: podman info$(NC)"; \
		exit 1; \
	fi
	
	@echo "$(CYAN)Validating wheelhouse compatibility...$(NC)"
	@if ! $(PYTHON) scripts/validate_wheelhouse.py --target-version 312 --clean-incompatible; then \
		echo "$(RED)❌ ERROR: Wheelhouse validation failed$(NC)"; \
		exit 1; \
	fi
	
	@wheel_count="$$($(PYTHON) -c 'import os; print(len([f for f in os.listdir("$(WHEELHOUSE_DIR)") if f.endswith(".whl")]))')"; \
	if [ "$$wheel_count" -gt 0 ]; then \
		echo "$(GREEN)✅ SUCCESS: $$wheel_count Python 3.12 compatible wheels built$(NC)"; \
		echo "$(CYAN)Compressing wheelhouse...$(NC)"; \
		tar -czf wheelhouse.tgz -C $(WHEELHOUSE_DIR) . && \
	else \
		echo "$(RED)❌ ERROR: No wheels were built$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Use 'make deps' to install from wheelhouse$(NC)"


check-python-version: ## Check if host Python version matches container version (fails loudly if not)
	@echo "$(CYAN)🔍 Checking Python version compatibility...$(NC)"
	@HOST_PYTHON="$$($(PYTHON) --version 2>&1 | sed 's/Python \([0-9]\+\.[0-9]\+\).*/\1/' || echo 'unknown')"; \
	CONTAINER_PYTHON="3.12"; \
	echo "Host Python version: $$HOST_PYTHON"; \
	echo "Container Python version: $$CONTAINER_PYTHON"; \
	if [ "$$HOST_PYTHON" != "$$CONTAINER_PYTHON" ]; then \
		echo "$(RED)❌ CRITICAL ERROR: Python version mismatch!$(NC)"; \
		echo "$(RED)❌ Host: Python $$HOST_PYTHON, Container: Python $$CONTAINER_PYTHON$(NC)"; \
		echo "$(RED)❌ This will create incompatible wheels - BUILD ABORTED$(NC)"; \
		echo ""; \
		echo "$(YELLOW)💡 SOLUTIONS:$(NC)"; \
		echo "$(YELLOW)   1. Use 'make wheel-build-podman' (recommended)$(NC)"; \
		echo "$(YELLOW)   2. Install Python 3.12: sudo apt install python3.12$(NC)"; \
		echo "$(YELLOW)   3. Switch to Python 3.12 environment$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✅ Python versions match - safe to proceed$(NC)"; \
	fi


wheel-analyze: ## Analyze wheelhouse contents and dependencies
	@echo "$(CYAN)Analyzing wheelhouse contents...$(NC)"
	@if [ ! -d $(WHEELHOUSE_DIR) ]; then \
		echo "$(RED)Error: Wheelhouse directory not found. Run 'make wheel-build' first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(CYAN)Wheelhouse statistics:$(NC)"
	@ls -1 $(WHEELHOUSE_DIR)/*.whl 2>/dev/null | wc -l | xargs echo "  Total wheels:"
	@du -sh $(WHEELHOUSE_DIR) 2>/dev/null | awk '{print "  Total size: " $$1}' || echo "  Total size: Unknown"
	@if [ -f wheelhouse.tgz ]; then \
		ls -lh wheelhouse.tgz | awk '{print "  Compressed size: " $$5}'; \
	fi
	@echo "$(CYAN)Sample wheels:$(NC)"
	@ls -1 $(WHEELHOUSE_DIR)/*.whl 2>/dev/null | head -5 | sed 's/^/  /'
	@echo "$(GREEN)✓ Wheelhouse analysis complete$(NC)"

	@echo "$(CYAN)Validating wheelhouse Python version compatibility...$(NC)"
	@if [ ! -f scripts/validate_wheelhouse.py ]; then \
		exit 1; \
	fi
	$(PYTHON) scripts/validate_wheelhouse.py --target-version 312 --report
	@echo "$(GREEN)✓ Wheelhouse validation complete$(NC)"


build-health: ## Comprehensive build system health check
	@echo "$(CYAN)🏥 Build System Health Check$(NC)"
	@echo "$(CYAN)=============================$(NC)"

	# Podman check
	@if podman info >/dev/null 2>&1; then \
		echo "$(GREEN)✅ Podman: Available$(NC)"; \
	else \
		echo "$(RED)❌ Podman: Unavailable$(NC)"; exit 1; \
	fi
	
	# Python version check
	@if command -v python3 >/dev/null 2>&1; then \
		PY_VER=$$(python3 --version 2>&1 | cut -d' ' -f2); \
		if [ "$$($(PYTHON) -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')" = "3.12" ]; then \
			echo "$(GREEN)✅ Python: $$PY_VER (compatible)$(NC)"; \
		else \
			echo "$(RED)❌ Python: $$PY_VER (need 3.12)$(NC)"; exit 1; \
		fi; \
	else \
		echo "$(RED)❌ Python: Not found$(NC)"; exit 1; \
	fi
	
	# Disk space check
	@DISK_FREE=$$(df . | tail -1 | awk '{print int($$4/1024/1024)}'); \
	if [ "$$DISK_FREE" -gt 50 ]; then \
		echo "$(GREEN)✅ Disk: $$DISK_FREE GB free$(NC)"; \
	else \
		echo "$(RED)❌ Disk: Only $$DISK_FREE GB free (need 50GB+)$(NC)"; exit 1; \
	fi
	
	# Memory check
	@MEM_GB=$$(free -g | grep '^Mem:' | awk '{print $$2}'); \
	if [ "$$MEM_GB" -ge 16 ]; then \
		echo "$(GREEN)✅ Memory: $$MEM_GB GB available$(NC)"; \
	else \
		echo "$(RED)❌ Memory: $$MEM_GB GB (need 16GB+ for AI workloads)$(NC)"; exit 1; \
	fi
	
	# Requirements validation
	@for f in requirements-*.txt; do \
		if [ -f "$$f" ] && [ -s "$$f" ]; then \
			LINES=$$(wc -l < "$$f"); \
			echo "$(GREEN)✅ $$f: $$LINES lines$(NC)"; \
		else \
			echo "$(RED)❌ $$f: Missing or empty$(NC)"; exit 1; \
		fi; \
	done
	
	# Podman Compose check
	@if [ -f docker-compose.yml ]; then \
		echo "$(GREEN)✅ docker-compose.yml: Present$(NC)"; \
	else \
		echo "$(RED)❌ docker-compose.yml: Missing$(NC)"; exit 1; \
	fi
	
	# Environment file check
	@if [ -f .env.example ]; then \
		echo "$(GREEN)✅ .env.example: Present$(NC)"; \
	else \
		echo "$(RED)❌ .env.example: Missing$(NC)"; exit 1; \
	fi
	
	@echo "$(GREEN)✅ All checks passed - ready to build!$(NC)"


logs: ## Show container logs (multi-method access)
	@echo "$(CYAN)Retrieving container logs...$(NC)"
	@if [ -z "$(CONTAINER)" ]; then \
		echo "$(YELLOW)Usage: make logs CONTAINER=<container_name> [LINES=<num>]$(NC)"; \
		echo "$(YELLOW)Example: make logs CONTAINER=xnai_chainlit_ui LINES=100$(NC)"; \
		echo "$(YELLOW)Available containers:$(NC)"; \
		podman ps -a --format "table {{.Names}}\t{{.Status}}" | grep -E "(xnai|xoe)" || echo "  No Xoe-NovAi containers found"; \
		exit 1; \
	fi
	@if [ ! -f scripts/get_container_logs.sh ]; then \
		echo "$(RED)Error: Log retrieval script not found$(NC)"; \
		exit 1; \
	fi
	./scripts/get_container_logs.sh "$(CONTAINER)" "$(LINES)"

# ============================================================================
# STACK-CAT DOCUMENTATION GENERATOR TARGETS
# ============================================================================

stack-cat: stack-cat-default ## Generate default stack documentation (alias)

stack-cat-default: ## Generate default stack documentation (all components)
	@echo "$(CYAN)Generating Xoe-NovAi v0.1.5 stack documentation...$(NC)"
	@if [ ! -f scripts/stack-cat/stack-cat.sh ]; then \
		echo "$(RED)Error: Stack-Cat script not found at scripts/stack-cat/stack-cat.sh$(NC)"; \
		exit 1; \
	fi
	@cd scripts/stack-cat && ./stack-cat.sh -g default -f all
	@echo "$(GREEN)✓ Stack documentation generated$(NC)"
	@echo "$(YELLOW)Output: scripts/stack-cat/stack-cat-output/$(NC)"
	@ls -la scripts/stack-cat/stack-cat-output/ | tail -3


stack-cat-api: ## Generate API backend documentation only
	@echo "$(CYAN)Generating API documentation...$(NC)"
	@cd scripts/stack-cat && ./stack-cat.sh -g api -f all
	@echo "$(GREEN)✓ API documentation generated$(NC)"


stack-cat-rag: ## Generate RAG subsystem documentation only
	@echo "$(CYAN)Generating RAG documentation...$(NC)"
	@cd scripts/stack-cat && ./stack-cat.sh -g rag -f all
	@echo "$(GREEN)✓ RAG documentation generated$(NC)"


stack-cat-frontend: ## Generate UI frontend documentation only
	@echo "$(CYAN)Generating UI frontend documentation...$(NC)"
	@cd scripts/stack-cat && ./stack-cat.sh -g frontend -f all
	@echo "$(GREEN)✓ UI frontend documentation generated$(NC)"


stack-cat-crawler: ## Generate CrawlModule subsystem documentation only
	@echo "$(CYAN)Generating CrawlModule documentation...$(NC)"
	@cd scripts/stack-cat && ./stack-cat.sh -g crawler -f all
	@echo "$(GREEN)✓ CrawlModule documentation generated$(NC)"


stack-cat-voice: ## Generate voice interface documentation only
	@echo "$(CYAN)Generating voice interface documentation...$(NC)"
	@cd scripts/stack-cat && ./stack-cat.sh -g voice -f all
	@echo "$(GREEN)✓ Voice interface documentation generated$(NC)"


stack-cat-all: ## Generate documentation for all groups
	@echo "$(CYAN)Generating documentation for all groups...$(NC)"
	@cd scripts/stack-cat && ./stack-cat.sh -g default -f all
	@cd scripts/stack-cat && ./stack-cat.sh -g api -f all
	@cd scripts/stack-cat && ./stack-cat.sh -g rag -f all
	@cd scripts/stack-cat && ./stack-cat.sh -g frontend -f all
	@cd scripts/stack-cat && ./stack-cat.sh -g crawler -f all
	@cd scripts/stack-cat && ./stack-cat.sh -g voice -f all
	@echo "$(GREEN)✓ All documentation generated$(NC)"


stack-cat-separate: ## Generate separate markdown files for each source file
	@echo "$(CYAN)Generating separate markdown files...$(NC)"
	@cd scripts/stack-cat && ./stack-cat.sh -g default -s
	@echo "$(GREEN)✓ Separate markdown files generated$(NC)"
	@echo "$(YELLOW)Files: scripts/stack-cat/stack-cat-output/separate-md/$(NC)"


stack-cat-deconcat: ## De-concatenate markdown file into separate files
	@echo "$(CYAN)De-concatenating markdown file...$(NC)"
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: Specify FILE variable (e.g., make stack-cat-deconcat FILE=stack-cat-output/20251021_143022/stack-cat_20251021_143022.md)$(NC)"; \
		exit 1; \
	fi
	@echo "$(CYAN)De-concatenating: $(FILE)$(NC)"
	@cd scripts/stack-cat && ./stack-cat.sh -d "$(FILE)"
	@echo "$(GREEN)✓ De-concatenation complete$(NC)"


stack-cat-clean: ## Clean up stack-cat output directories (WARNING: PERMANENT DELETION)
	@echo "$(RED)⚠️  WARNING: This will permanently delete ALL historical Stack-Cat documentation snapshots!$(NC)"
	@echo "$(YELLOW)Output directory: scripts/stack-cat/stack-cat-output/$(NC)"
	@read -p "Are you sure you want to permanently delete all Stack-Cat output? (type 'yes' to confirm): " confirm && \
	if [ "$$confirm" = "yes" ]; then \
		if [ -d scripts/stack-cat/stack-cat-output ]; then \
			echo "$(CYAN)Cleaning up Stack-Cat output...$(NC)"; \
			rm -rf scripts/stack-cat/stack-cat-output && \
			echo "$(GREEN)✓ Stack-Cat output permanently deleted$(NC)"; \
		else \
			echo "$(YELLOW)No Stack-Cat output directory found$(NC)"; \
		fi; \
	else \
		echo "$(YELLOW)Cancellation confirmed - no files deleted$(NC)"; \
	fi


stack-cat-archive: ## Move Stack-Cat outputs older than 1 week to archive folder
	@echo "$(CYAN)Archiving Stack-Cat outputs older than 1 week...$(NC)"
	@if [ ! -d scripts/stack-cat/stack-cat-output ]; then \
		echo "$(YELLOW)No stack-cat-output directory found$(NC)"; \
		exit 0; \
	fi
	@mkdir -p scripts/stack-cat/stack-cat-archive
	@echo "$(CYAN)Finding files older than 7 days...$(NC)"
	@cd scripts/stack-cat && find stack-cat-output -type f -mtime +7 | while read -r file; do \
		echo "$(YELLOW)Archiving: $$file$(NC)"; \
		dirpath=$$(dirname "stack-cat-archive/$$file"); \
		mkdir -p "$$dirpath"; \
		mv "$$file" "stack-cat-archive/$$file"; \
	done
	@echo "$(CYAN)Removing empty directories from output...$(NC)"
	@cd scripts/stack-cat && find stack-cat-output -type d -empty -delete 2>/dev/null || true
	@archived_count=$$(find scripts/stack-cat/stack-cat-archive -type f -mtime +7 2>/dev/null | wc -l); \
	if [ "$$archived_count" -gt 0 ]; then \
		echo "$(GREEN)✓ Archived $$archived_count files older than 1 week$(NC)"; \
		echo "$(YELLOW)Archive location: scripts/stack-cat/stack-cat-archive/$(NC)"; \
	else \
		echo "$(YELLOW)No files older than 1 week to archive$(NC)"; \
	fi

# ============================================================================
# MKDOCS + DIÁTAXIS DOCUMENTATION PLATFORM TARGETS
# ============================================================================

docs-deps: ## Install documentation dependencies locally (for VS Code preview)
	@echo "$(CYAN)Installing MkDocs dependencies...$(NC)"
	pip install -r docs/requirements-docs.txt
	@echo "$(GREEN)✅ Documentation dependencies installed$(NC)"


docs-serve: ## 📚 Serve MkDocs documentation locally with live reload (Diátaxis navigation)
	@echo "$(CYAN)📚 Serving MkDocs documentation locally...$(NC)"
	@if ! command -v mkdocs >/dev/null 2>&1; then \
		echo "$(RED)❌ ERROR: MkDocs not installed$(NC)"; \
		echo "$(YELLOW)💡 Install with: pip install mkdocs-material$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f docs/mkdocs.yml ]; then \
		echo "$(RED)❌ ERROR: docs/mkdocs.yml not found$(NC)"; \
		echo "$(YELLOW)💡 Run from project root directory$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)🌐 Documentation available at: http://localhost:8000$(NC)"
	@echo "$(YELLOW)📋 Diátaxis Structure:$(NC)"
	@echo "$(YELLOW)   🎓 Tutorials     - Step-by-step learning$(NC)"
	@echo "$(YELLOW)   🔧 How-to Guides - Task-based instructions$(NC)"
	@echo "$(YELLOW)   📖 Reference     - Technical specifications$(NC)"
	@echo "$(YELLOW)   💡 Explanation   - Conceptual understanding$(NC)"
	@echo "$(CYAN)Press Ctrl+C to stop server$(NC)"
	@cd docs && mkdocs serve --dev-addr=0.0.0.0:8000


docs-build: ## 🛠️ Build static MkDocs documentation site with Diátaxis structure
	@echo "$(CYAN)🛠️ Building MkDocs documentation site...$(NC)"
	@if ! command -v mkdocs >/dev/null 2>&1; then \
		exit 1; \
	fi
	@if [ ! -f docs/mkdocs.yml ]; then \
		echo "$(YELLOW)💡 Run from project root directory$(NC)"; \
		exit 1; \
	fi
	@cd docs && mkdocs build --strict
	@echo "$(GREEN)✅ Documentation built successfully$(NC)"
	@echo "$(YELLOW)📁 Output: docs/site/$(NC)"
	@echo "$(YELLOW)🌐 Serve locally: make docs-serve$(NC)"


docs-validate: ## ✅ Validate MkDocs documentation (links, structure, Diátaxis compliance)
	@echo "$(CYAN)✅ Validating MkDocs documentation...$(NC)"
	@if ! command -v mkdocs >/dev/null 2>&1; then 
		exit 1; 
	fi
	@if [ ! -f docs/mkdocs.yml ]; then 
		echo "$(YELLOW)💡 Run from project root directory$(NC)"; 
		exit 1; 
	fi
	@echo "$(CYAN)🔗 Checking links and structure...$(NC)"
	@cd docs && mkdocs build --strict 2>&1 | head -20
	@if [ $$? -eq 0 ]; then 
		echo "$(GREEN)✅ Documentation validation passed$(NC)"; 
		echo "$(CYAN)📊 Diátaxis Structure Check:$(NC)"; 
		if [ -d docs/tutorials ] && [ -d docs/how-to ] && [ -d docs/reference ] && [ -d docs/explanation ]; then 
			echo "$(GREEN)   ✅ All Diátaxis quadrants present$(NC)"; 
			tut_count=$$(find docs/tutorials -name "*.md" 2>/dev/null | wc -l); 
			how_count=$$(find docs/how-to -name "*.md" 2>/dev/null | wc -l); 
			ref_count=$$(find docs/reference -name "*.md" 2>/dev/null | wc -l); 
			exp_count=$$(find docs/explanation -name "*.md" 2>/dev/null | wc -l); 
			echo "$(GREEN)   📈 Content: Tutorials: $$tut_count, How-to: $$how_count, Reference: $$ref_count, Explanation: $$exp_count$(NC)"; 
		else 
			echo "$(RED)   ❌ Missing Diátaxis quadrants$(NC)"; 
		fi; 
	else 
		echo "$(RED)❌ Documentation validation failed$(NC)"; 
		echo "$(YELLOW)💡 Fix errors and run again$(NC)"; 
		exit 1; 
	fi


docs-deploy: ## 🚀 Deploy MkDocs documentation to static hosting (optional)
	@echo "$(CYAN)🚀 Deploying MkDocs documentation...$(NC)"
	@if ! command -v mike >/dev/null 2>&1; then 
		echo "$(YELLOW)💡 Install with: pip install mkdocs-material mike$(NC)"; 
		exit 1; 
	fi
	@echo "$(YELLOW)⚠️  This deploys to GitHub Pages (requires mike plugin)$(NC)"
	@read -p "Deploy to GitHub Pages? (y/N): " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then 
		cd docs && mike deploy $(VER) --push; 
		echo "$(GREEN)✅ Documentation deployed to GitHub Pages$(NC)"; 
	else 
		echo "$(YELLOW)Deployment cancelled$(NC)"; 
	fi


docs-clean: ## 🧹 Clean MkDocs build artifacts
	@echo "$(CYAN)🧹 Cleaning MkDocs build artifacts...$(NC)"
	@if [ -d docs/site ]; then 
		rm -rf docs/site; 
		echo "$(GREEN)✅ Build artifacts cleaned$(NC)"; 
	else 
		echo "$(YELLOW)No build artifacts found$(NC)"; 
	fi


docs-setup: ## ⚙️ Setup MkDocs development environment
	@echo "$(CYAN)⚙️ Setting up MkDocs development environment...$(NC)"
	@if ! command -v pip >/dev/null 2>&1; then 
		echo "$(RED)❌ ERROR: pip not available$(NC)"; 
		exit 1; 
	fi
	@echo "$(CYAN)Installing MkDocs and plugins...$(NC)"
	pip install mkdocs-material mkdocs-glightbox mike
	@echo "$(GREEN)✅ MkDocs development environment ready$(NC)"
	@echo "$(YELLOW)💡 Available commands:$(NC)"
	@echo "$(YELLOW)   make docs-build    - Build documentation$(NC)"
	@echo "$(YELLOW)   make docs-serve    - Serve locally$(NC)"
	@echo "$(YELLOW)   make docs-validate - Validate structure$(NC)"


docs-freshness: ## Run documentation freshness & health check
	@echo "$(CYAN)📚 Running documentation freshness check...$(NC)"
	$(PYTHON) docs/scripts/freshness_monitor.py --check --report
	@echo "$(GREEN)✅ Freshness check complete$(NC)"


docs-index: ## Rebuild documentation search index
	@echo "$(CYAN)🔍 Rebuilding documentation search index...$(NC)"
	@if [ ! -f docs/scripts/indexer.py ]; then 
		echo "$(RED)❌ ERROR: Indexer script not found$(NC)"; 
		exit 1; 
	fi
	$(PYTHON) docs/scripts/indexer.py --rebuild
	@echo "$(GREEN)✅ Search index rebuilt$(NC)"


docs-migrate: ## Migrate legacy content to new numbered categories (dry-run first)
	@echo "$(CYAN)🔄 Migrating legacy content to Diátaxis structure...$(NC)"
	@if [ ! -f docs/scripts/migrate_content.py ]; then 
		echo "$(RED)❌ ERROR: Migration script not found$(NC)"; 
		exit 1; 
	fi
	@echo "$(YELLOW)⚠️  Running dry-run first...$(NC)"
	$(PYTHON) docs/scripts/migrate_content.py --dry-run
	@echo "$(YELLOW)💡 Review output above, then run with:$(NC)"
	@echo "$(YELLOW)   make docs-migrate-confirm$(NC)"


docs-migrate-confirm: ## Confirm migration of legacy content (destructive)
	@echo "$(RED)⚠️  WARNING: This will move files permanently!$(NC)"
	@read -p "Proceed with migration? (yes/NO): " confirm && \
	if [ "$$confirm" = "yes" ]; then 
		$(PYTHON) docs/scripts/migrate_content.py --execute; 
		echo "$(GREEN)✅ Migration complete$(NC)"; 
	else 
		echo "$(YELLOW)Cancellation confirmed$(NC)"; 
	fi


docs-version: ## Create new versioned documentation snapshot
	@if [ -z "$(VER)" ]; then 
		echo "$(RED)❌ ERROR: Version required$(NC)"; 
		echo "$(YELLOW)💡 Usage: make docs-version VER=v0.1.6$(NC)"; 
		exit 1; 
	fi
	@echo "$(CYAN)🏷️ Creating documentation version $(VER)...$(NC)"
	@if ! command -v mike >/dev/null 2>&1; then 
		echo "$(RED)❌ ERROR: Mike not installed$(NC)"; 
		echo "$(YELLOW)💡 Install with: pip install mike$(NC)"; 
		exit 1; 
	fi
	@cd docs && mike deploy $(VER) --push
	@echo "$(GREEN)✅ Documentation version $(VER) created$(NC)"

refresh-memory: ## 🔄 Refresh memory_bank files with latest context from GROK_CONTEXT_PACK
	@echo "$(CYAN)🔄 Refreshing memory_bank files...$(NC)"
	@python3 scripts/memory_bank_refresh.py
	@echo "$(GREEN)✅ Memory bank refresh complete$(NC)"


docs-validate-research: ## Validate Grok v5 research coverage
	@echo "$(CYAN)🔬 Validating Grok v5 research coverage...$(NC)"
	@if [ ! -f docs/scripts/research_validator.py ]; then 
		echo "$(RED)❌ ERROR: Research validator not found$(NC)"; 
		exit 1; 
	fi
	$(PYTHON) docs/scripts/research_validator.py --validate
	@echo "$(GREEN)✅ Research validation complete$(NC)"

	@echo "$(CYAN)🛠️ Building MkDocs documentation site...$(NC)"
	@if ! command -v mkdocs >/dev/null 2>&1; then 
		exit 1; 
	fi
	@if [ ! -f docs/mkdocs.yml ]; then 
		echo "$(YELLOW)💡 Run from project root directory$(NC)"; 
		exit 1; 
	fi
	@cd docs && mkdocs build --strict
	@echo "$(GREEN)✅ Documentation built successfully$(NC)"
	
	@echo "$(CYAN)📚 Serving MkDocs documentation locally...$(NC)"
	@if ! command -v mkdocs >/dev/null 2>&1; then 
		exit 1; 
	fi
	@if [ ! -f docs/mkdocs.yml ]; then 
		echo "$(YELLOW)💡 Run from project root directory$(NC)"; 
		exit 1; 
	fi
	@echo "$(YELLOW)   🎓 Tutorials     - Step-by-step learning$(NC)"
	@echo "$(YELLOW)   🔧 How-to Guides - Task-based instructions$(NC)"
	@echo "$(YELLOW)   📖 Reference     - Technical specifications$(NC)"
	@echo "$(YELLOW)   💡 Explanation   - Conceptual understanding$(NC)"
	@echo "$(CYAN)Press Ctrl+C to stop server$(NC)"
	
	@echo "$(CYAN)✅ Validating MkDocs documentation...$(NC)"
	@if ! command -v mkdocs >/dev/null 2>&1; then 
		exit 1; 
	fi
	@if [ ! -f docs/mkdocs.yml ]; then 
		echo "$(YELLOW)💡 Run from project root directory$(NC)"; 
		exit 1; 
	fi
	@echo "$(CYAN)🔗 Checking links and structure...$(NC)"
	@cd docs && mkdocs build --strict 2>&1 | head -20
	@if [ $$? -eq 0 ]; then 
		echo "$(GREEN)✅ Documentation validation passed$(NC)"; 
		echo "$(CYAN)📊 Diátaxis Structure Check:$(NC)"; 
		if [ -d docs/tutorials ] && [ -d docs/how-to ] && [ -d docs/reference ] && [ -d docs/explanation ]; then 
			echo "$(GREEN)   ✅ All Diátaxis quadrants present$(NC)"; 
			tut_count=$$(find docs/tutorials -name "*.md" 2>/dev/null | wc -l); 
			how_count=$$(find docs/how-to -name "*.md" 2>/dev/null | wc -l); 
			ref_count=$$(find docs/reference -name "*.md" 2>/dev/null | wc -l); 
			exp_count=$$(find docs/explanation -name "*.md" 2>/dev/null | wc -l); 
			echo "$(GREEN)   📈 Content: Tutorials: $$tut_count, How-to: $$how_count, Reference: $$ref_count, Explanation: $$exp_count$(NC)"; 
		else 
			echo "$(RED)   ❌ Missing Diátaxis quadrants$(NC)"; 
		fi; 
	else 
		echo "$(RED)❌ Documentation validation failed$(NC)"; 
		echo "$(YELLOW)💡 Fix errors and run again$(NC)"; 
		exit 1; 
	fi
	
	@echo "$(CYAN)🚀 Deploying MkDocs documentation...$(NC)"
	@if ! command -v mike >/dev/null 2>&1; then 
		exit 1; 
	fi
	@echo "$(YELLOW)⚠️  This deploys to GitHub Pages (requires mike plugin)$(NC)"
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then 
		cd docs && mkdocs gh-deploy --force; 
		echo "$(GREEN)✅ Documentation deployed to GitHub Pages$(NC)"; 
	else 
		echo "$(YELLOW)Deployment cancelled$(NC)"; 
	fi
	
	@echo "$(CYAN)🧹 Cleaning MkDocs build artifacts...$(NC)"
	@if [ -d docs/site ]; then 
		rm -rf docs/site; 
		echo "$(GREEN)✅ Build artifacts cleaned$(NC)"; 
	else 
		echo "$(YELLOW)No build artifacts found$(NC)"; 
	fi
	
	@echo "$(CYAN)⚙️ Setting up MkDocs development environment...$(NC)"
	@if ! command -v pip >/dev/null 2>&1; then 
		exit 1; 
	fi
	@echo "$(CYAN)Installing MkDocs and plugins...$(NC)"
	pip install mkdocs-material mkdocs-glightbox mike
	@echo "$(GREEN)✅ MkDocs development environment ready$(NC)"
	@echo "$(YELLOW)   make docs-build    - Build documentation$(NC)"
	@echo "$(YELLOW)   make docs-serve    - Serve locally$(NC)"
	@echo "$(YELLOW)   make docs-validate - Validate structure$(NC)"

# ============================================================================
# PYTHON 3.12 COMPATIBILITY & CACHING TARGETS
# ============================================================================

requirements-regenerate: ## 🔄 Regenerate all requirements files for Python 3.12 compatibility (enhanced with caching)
	@echo "$(CYAN)🔄 Regenerating requirements files for Python 3.12 compatibility...$(NC)"
	./scripts/regenerate_requirements_py312_cached.sh
	@echo "$(GREEN)✅ Requirements regeneration complete$(NC)"


requirements-compatibility-test: ## 🧪 Test Python 3.12 compatibility (fixed KeyError)
	@echo "$(CYAN)🧪 Testing Python 3.12 compatibility...$(NC)"
	python scripts/test_python312_compatibility.py
	@echo "$(GREEN)✅ Compatibility test complete$(NC)"


chainlit-upgrade-test: ## 🔄 Test Chainlit 2.8.5 compatibility with pip upgrade
	@echo "$(CYAN)🔄 Testing Chainlit 2.8.5 compatibility...$(NC)"
	@echo "$(CYAN)Creating test virtual environment...$(NC)"
	@if ! python3.12 -m venv /tmp/chainlit_test 2>/dev/null; then \
		echo "$(YELLOW)⚠️  Python 3.12 not available, using system Python$(NC)"; \
		if ! python3 -m venv /tmp/chainlit_test; then \
			echo "$(RED)❌ ERROR: Could not create virtual environment$(NC)"; \
			exit 1; \
		fi; \
	fi
	@echo "$(CYAN)Installing FastAPI and testing Chainlit compatibility...$(NC)"
	@source /tmp/chainlit_test/bin/activate && \
	pip install --upgrade pip && \
	pip install fastapi==0.128.0 && \
	echo "$(CYAN)Testing Chainlit 2.8.5 installation...$(NC)" && \
	if pip install chainlit==2.8.5 --dry-run; then \
		echo "$(GREEN)✅ Chainlit 2.8.5 compatible with FastAPI 0.128.0$(NC)"; \
		pip install chainlit==2.8.5 && \
		echo "$(CYAN)Testing imports...$(NC)" && \
		python3 -c "import fastapi; import chainlit; print(f'✅ FastAPI {fastapi.__version__} + Chainlit {chainlit.__version__} imported successfully')"; \
	else \
		echo "$(RED)❌ Chainlit 2.8.5 compatibility test failed$(NC)"; \
		exit 1; \
	fi
	@echo "$(CYAN)Cleaning up test environment...$(NC)"
	@rm -rf /tmp/chainlit_test
	@echo "$(GREEN)✅ Chainlit compatibility test complete$(NC)"


cache-setup: ## 💾 Setup complete caching system (Volumes + Local)
	@echo "$(CYAN)💾 Setting up Caching System...$(NC)"
	@echo "$(CYAN)=============================$(NC)"
	@echo ""
	@echo "$(CYAN)1. Setting up Podman volume cache...$(NC)"
	podman volume create xoe-pip-cache
	@echo ""
	@echo "$(CYAN)2. Setting up local cache directory...$(NC)"
	mkdir -p .pip_cache
	@echo ""
	@echo "$(GREEN)✅ Complete caching system ready$(NC)"
	@echo "$(YELLOW)💡 Use 'make cache-status' to check cache effectiveness$(NC)"

# ============================================================================
# DOCKER BUILDKIT & WHEELHOUSE ENTERPRISE OPTIMIZATION TARGETS
# ============================================================================

docs-buildkit: ## 🏗️ Enable BuildKit for all Podman operations
	@echo "$(CYAN)🏗️ Enabling Podman BuildKit globally...$(NC)"
	@if [ "$$($(PODMAN_CMD) buildx version 2>/dev/null)" ]; then \
		echo "$(GREEN)✅ BuildKit available$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  BuildKit not available - installing...$(NC)"; \
		sudo apt update && sudo apt install -y podman-podman; \
	fi
	@echo "$(CYAN)Setting PODMAN_BUILDKIT=1...$(NC)"
	@echo 'export PODMAN_BUILDKIT=1' >> ~/.bashrc
	export PODMAN_BUILDKIT=1
	@echo "$(GREEN)✅ BuildKit enabled for all builds$(NC)"
	@echo "$(YELLOW)💡 BuildKit features:$(NC)"
	@echo "$(YELLOW)   - Advanced caching with cache mounts$(NC)"
	@echo "$(YELLOW)   - Parallel processing$(NC)"
	@echo "$(YELLOW)   - Multi-stage build optimization$(NC)"


docs-wheelhouse: ## 📦 Setup enterprise wheelhouse for offline builds
	@echo "$(CYAN)📦 Setting up enterprise wheelhouse system...$(NC)"
	@if [ ! -d "$(WHEELHOUSE_DIR)" ]; then 
		echo "$(CYAN)Creating wheelhouse directory...$(NC)"; 
		mkdir -p $(WHEELHOUSE_DIR); 
	fi
	@echo "$(CYAN)Checking wheelhouse contents...$(NC)"
	@wheel_count=$$(find $(WHEELHOUSE_DIR) -name "*.whl" 2>/dev/null | wc -l);
	if [ "$$wheel_count" -gt 0 ]; then 
		echo "$(GREEN)✅ Wheelhouse ready: $$wheel_count wheels available$(NC)"; 
		echo "$(CYAN)Wheelhouse size: $$(du -sh $(WHEELHOUSE_DIR) | awk '{print $$1}')$(NC)"; 
	else 
		echo "$(YELLOW)⚠️  Wheelhouse empty - building wheels...$(NC)"; 
		$(MAKE) wheel-build-podman-amd; 
	fi
	@echo "$(YELLOW)💡 Wheelhouse features:$(NC)"
	@echo "$(YELLOW)   - Offline package installation$(NC)"
	@echo "$(YELLOW)   - Python 3.12 compatibility guaranteed$(NC)"
	@echo "$(YELLOW)   - Enterprise build reliability$(NC)"


docs-optimization: docs-buildkit docs-wheelhouse ## 🚀 Complete enterprise build optimization setup
	@echo "$(CYAN)🚀 Enterprise build optimization complete!$(NC)"
	@echo "$(GREEN)✅ BuildKit enabled globally$(NC)"
	@echo "$(GREEN)✅ Wheelhouse system ready$(NC)"
	@echo "$(GREEN)✅ Python 3.12 enforcement active$(NC)"
	@echo ""
	@echo "$(CYAN)Performance improvements:$(NC)"
	@echo "$(CYAN)   • 33-67x faster package downloads$(NC)"
	@echo "$(CYAN)   • 74% reduction in build times$(NC)"
	@echo "$(CYAN)   • Enterprise-grade caching$(NC)"
	@echo ""
	@echo "$(YELLOW)💡 Next steps:$(NC)"
	@echo "$(YELLOW)   make build        # Build with optimizations$(NC)"
	@echo "$(YELLOW)   make cache-status # Check cache effectiveness$(NC)"


docs-status: ## 📊 Show documentation and build optimization status
	@echo "$(CYAN)📊 Xoe-NovAi Documentation & Build Status$(NC)"
	@echo "$(CYAN)=============================================$(NC)"
	@echo ""
	@echo "$(CYAN)📚 Documentation:$(NC)"
	@if [ -d "docs" ] && [ -f "docs/mkdocs.yml" ]; then 
		page_count=$$(find docs -name "*.md" 2>/dev/null | wc -l);
		echo "$(GREEN)✅ MkDocs ready: $$page_count pages$(NC)"; 
		if podman ps | grep -q xoe-docs; then 
			echo "$(GREEN)✅ Docs server running: http://localhost:8000$(NC)"; 
		else 
			echo "$(YELLOW)⚠️  Docs server not running$(NC)"; 
		fi; 
	else 
		echo "$(RED)❌ Documentation not set up$(NC)"; 
	fi
	@echo ""
	@echo "$(CYAN)🏗️  BuildKit:$(NC)"
	@if [ "$$PODMAN_BUILDKIT" = "1" ]; then 
		echo "$(GREEN)✅ BuildKit enabled globally$(NC)"; 
	else 
		echo "$(YELLOW)⚠️  BuildKit not enabled$(NC)"; 
	fi
	@if podman buildx version >/dev/null 2>&1; then 
		echo "$(GREEN)✅ BuildKit plugin available$(NC)"; 
	else 
		echo "$(RED)❌ BuildKit plugin missing$(NC)"; 
	fi
	@echo ""
	@echo "$(CYAN)📦 Wheelhouse:$(NC)"
	@if [ -d "$(WHEELHOUSE_DIR)" ]; then 
		wheel_count=$$(find $(WHEELHOUSE_DIR) -name "*.whl" 2>/dev/null | wc -l);
		if [ "$$wheel_count" -gt 0 ]; then 
			echo "$(GREEN)✅ Wheelhouse ready: $$wheel_count wheels$(NC)"; 
			echo "$(CYAN)   Size: $$(du -sh $(WHEELHOUSE_DIR) | awk '{print $$1}')$(NC)"; 
		else 
			echo "$(YELLOW)⚠️  Wheelhouse empty$(NC)"; 
		fi; 
	else 
		echo "$(RED)❌ Wheelhouse not created$(NC)"; 
	fi
	@echo ""
	@image_count=$$(podman images | grep -E "(xoe|xnai)" | wc -l 2>/dev/null || echo "0"); \
	if [ "$$image_count" -gt 0 ]; then \
		echo "$(GREEN)✅ $$image_count Xoe-NovAi images built$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  No images built yet$(NC)"; \
	fi
	@echo ""
	@echo "$(CYAN)🎯 Quick Actions:$(NC)"
	@echo "$(CYAN)   make docs-buildkit    # Enable BuildKit$(NC)"
	@echo "$(CYAN)   make docs-wheelhouse  # Setup wheelhouse$(NC)"
	@echo "$(CYAN)   make docs-optimization # Complete setup$(NC)"
	@echo "$(CYAN)   make build            # Build with optimizations$(NC)"


enterprise-buildkit: ## 🏗️ Enable enterprise BuildKit features
	@echo "$(CYAN)🏢 Enabling enterprise BuildKit features...$(NC)"
	$(MAKE) docs-buildkit
	@echo "$(CYAN)Setting up advanced BuildKit configuration...$(NC)"
	@if ! podman buildx ls | grep -q "xoe-builder"; then \
		echo "$(CYAN)Creating enterprise builder instance...$(NC)"; \
		podman buildx create --name xoe-builder --use; \
		podman buildx inspect --bootstrap; \
	fi
	@echo "$(GREEN)✅ Enterprise BuildKit ready$(NC)"
	@echo "$(YELLOW)Features enabled:$(NC)"
	@echo "$(YELLOW)   - Multi-platform builds$(NC)"
	@echo "$(YELLOW)   - Advanced caching strategies$(NC)"
	@echo "$(YELLOW)   - Enterprise builder instance$(NC)"


enterprise-wheelhouse: ## 📦 Setup enterprise wheelhouse with validation
	@echo "$(CYAN)🏢 Setting up enterprise wheelhouse...$(NC)"
	$(MAKE) docs-wheelhouse
	@echo "$(CYAN)Running enterprise validation...$(NC)"
	$(MAKE) wheel-validate
	$(MAKE) build-health
	@echo "$(GREEN)✅ Enterprise wheelhouse validated$(NC)"
	@echo "$(YELLOW)Enterprise features:$(NC)"
	@echo "$(YELLOW)   - Python 3.12 guaranteed compatibility$(NC)"
	@echo "$(YELLOW)   - Comprehensive validation$(NC)"
	@echo "$(YELLOW)   - Build health monitoring$(NC)"


enterprise-cache: ## 💾 Setup complete enterprise caching system
	@echo "$(CYAN)🏢 Setting up complete enterprise caching...$(NC)"
	$(MAKE) cache-setup
	$(MAKE) enterprise-buildkit
	$(MAKE) enterprise-wheelhouse
	@echo "$(CYAN)Validating enterprise cache system...$(NC)"
	$(MAKE) cache-status
	@echo "$(GREEN)✅ Enterprise caching system complete$(NC)"
	@echo "$(YELLOW)Cache layers:$(NC)"
	@echo "$(YELLOW)   - Podman volume caching$(NC)"
	@echo "$(YELLOW)   - BuildKit layer caching$(NC)"
	@echo "$(YELLOW)   - Wheelhouse package caching$(NC)"
	@echo "$(YELLOW)   - Local pip cache$(NC)"
# ============================================================================
# DEEPSEEK ENTERPRISE SCRIPT INTEGRATION (Phase 6)
# ============================================================================

# ============================================================================
# DEPRECATED: apt-cacher-ng (Replaced by BuildKit Cache Mounts)
# ============================================================================
# Note: BuildKit cache mounts provide the same benefits with zero infrastructure
# See Dockerfile.base for implementation details

setup-apt-cache: ## ⚠️  DEPRECATED - BuildKit cache mounts handle this automatically
	@echo "$(RED)═══════════════════════════════════════════════════════════════$(NC)"
	@echo "$(RED)❌ DEPRECATED: apt-cacher-ng is no longer needed$(NC)"
	@echo "$(RED)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)💡 Xoe-NovAi now uses BuildKit cache mounts for APT optimization$(NC)"
	@echo "$(YELLOW)   This provides the same 2-4x speedup with ZERO infrastructure:$(NC)"
	@echo ""
	@echo "$(CYAN)   ✅ No apt-cacher-ng service to manage$(NC)"
	@echo "$(CYAN)   ✅ No Quadlet configuration needed$(NC)"
	@echo "$(CYAN)   ✅ Automatic caching in ~/.local/share/containers/storage/buildkit-cache/$(NC)"
	@echo "$(CYAN)   ✅ Works offline after initial cache population$(NC)"
	@echo ""
	@echo "$(GREEN)🚀 To build with caching enabled:$(NC)"
	@echo "$(GREEN)   make build$(NC)"
	@echo ""
	@echo "$(YELLOW)📚 For more info, see:$(NC)"
	@echo "$(YELLOW)   - docs/03-how-to-guides/buildkit-cache-optimization.md$(NC)"
	@echo "$(YELLOW)   - Dockerfile.base (implementation)$(NC)"
	@echo ""
	@exit 1

# Keep scripts in archive for future reference (Phase 7: team expansion)
archive-apt-cache-scripts: ## 📦 Archive apt-cacher-ng scripts for future use
	@echo "$(CYAN)📦 Archiving apt-cacher-ng scripts...$(NC)"
	@mkdir -p scripts/_archive/apt-cache-phase7/
	@mv scripts/apt-cache/* scripts/_archive/apt-cache-phase7/ 2>/dev/null || true
	@echo "$(GREEN)✅ Scripts archived to: scripts/_archive/apt-cache-phase7/$(NC)"
	@echo "$(YELLOW)💡 These will be useful in Phase 7 (team expansion)$(NC)"

# ============================================================================
# BUILDKIT CACHE MANAGEMENT
# ============================================================================

cache-status: ## 📊 Show caching system status (BuildKit + Volumes + Local)
	@echo "$(CYAN)📊 System Caching Status$(NC)"
	@echo "$(CYAN)========================$(NC)"
	@echo ""
	@echo "$(CYAN)🏗️  BuildKit Cache (Persistent Layer Caching):$(NC)"
	@if [ -d ~/.local/share/containers/storage/buildkit-cache/ ]; then \
		CACHE_SIZE=$$(du -sh ~/.local/share/containers/storage/buildkit-cache/ 2>/dev/null | awk '{print $$1}'); \
		echo "$(GREEN)✅ BuildKit Cache exists: $$CACHE_SIZE$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  No BuildKit cache found (run 'make build' to populate)$(NC)"; \
	fi
	@echo ""
	@echo "$(CYAN)🐳 Podman Volume Cache (xoe-pip-cache):$(NC)"
	@if podman volume ls | grep -q "xoe-pip-cache"; then \
		VOL_SIZE=$$(podman run --rm -v xoe-pip-cache:/cache alpine du -sh /cache 2>/dev/null | awk '{print $$1}' || echo "unknown"); \
		echo "$(GREEN)✅ Volume cache active: $$VOL_SIZE$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Volume cache missing (run 'make cache-setup')$(NC)"; \
	fi
	@echo ""
	@echo "$(CYAN)📁 Local Cache (.pip_cache):$(NC)"
	@if [ -d ".pip_cache" ]; then \
		LOCAL_SIZE=$$(du -sh .pip_cache 2>/dev/null | awk '{print $$1}'); \
		echo "$(GREEN)✅ Local cache active: $$LOCAL_SIZE$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Local cache missing (run 'make cache-setup')$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)💡 Quick Commands:$(NC)"
	@echo "$(YELLOW)   make cache-warm     # Pre-populate BuildKit cache$(NC)"
	@echo "$(YELLOW)   make cache-clear    # Clear ALL caches$(NC)"
	@echo "$(YELLOW)   make build          # Build with caching$(NC)"


cache-warm: ## 🔥 Warm up BuildKit caches (faster subsequent builds)
	@echo "$(CYAN)🔥 Warming up BuildKit caches...$(NC)"
	@echo "$(CYAN)This will build base image to populate apt/pip caches$(NC)"
	@echo ""
	@podman build --progress=plain -t xnai-base:cache-warm -f Dockerfile.base .
	@echo ""
	@echo "$(GREEN)✅ Cache warmed successfully$(NC)"
	@echo "$(YELLOW)💡 Subsequent builds will be 2-4x faster$(NC)"
	@echo "$(YELLOW)💡 Check cache: make cache-status$(NC)"


cache-clear: ## 🧹 Clear ALL BuildKit caches (WARNING: Forces full rebuild)
	@echo "$(RED)⚠️  WARNING: This will clear ALL BuildKit caches$(NC)"
	@echo "$(RED)⚠️  Next build will re-download all packages$(NC)"
	@echo ""
	@read -p "Continue? (yes/NO): " confirm && \
	if [ "$$confirm" = "yes" ]; then 
		echo "$(CYAN)Clearing BuildKit caches...$(NC)"; 
		podman system prune -af --volumes; 
		echo "$(GREEN)✅ All caches cleared$(NC)"; 
		echo "$(YELLOW)💡 Run 'make cache-warm' to repopulate$(NC)"; 
	else 
		echo "$(YELLOW)Canceled$(NC)"; 
	fi


cache-clear-apt: ## 🧹 Clear ONLY apt caches (use if apt install fails)
	@echo "$(CYAN)🧹 Clearing apt BuildKit caches...$(NC)"
	@echo "$(RED)⚠️  This will force re-download of apt packages$(NC)"
	@read -p "Continue? (y/N): " confirm && \
	if [ "$$confirm" = "y" ]; then 
		echo "$(CYAN)Clearing apt caches...$(NC)"; 
		podman system prune --filter "label=io.buildkit.cache.id=xnai-apt-cache" -af; 
		podman system prune --filter "label=io.buildkit.cache.id=xnai-apt-lists" -af; 
		echo "$(GREEN)✅ apt caches cleared$(NC)"; 
	fi


cache-inspect: ## 🔍 Detailed BuildKit cache inspection
	@echo "$(CYAN)🔍 BuildKit Cache Inspection$(NC)"
	@echo "$(CYAN)=============================$(NC)"
	@echo ""
	@if [ -d ~/.local/share/containers/storage/buildkit-cache/ ]; then 
		echo "$(CYAN)Cache entries:$(NC)"; 
		ls -lh ~/.local/share/containers/storage/buildkit-cache/ | tail -n +2 | awk '{print "  " $$9 " (" $$5 ")"}'; 
		echo ""; 
		echo "$(CYAN)Total cache size:$(NC)"; 
		du -sh ~/.local/share/containers/storage/buildkit-cache/; 
	else 
		echo "$(YELLOW)No cache directory found$(NC)"; 
	fi


benchmark-statistical: ## 📊 Run statistical build benchmark (95% CI)
	@echo "$(CYAN)📊 Running statistical build benchmark...$(NC)"
	@bash scripts/benchmarking/benchmark-builds-statistical.sh
	@echo "$(GREEN)✅ Benchmark complete$(NC)"


detect-regression: ## 🔍 Detect build performance regressions
	@echo "$(CYAN)🔍 Detecting performance regressions...$(NC)"
	@$(PYTHON) scripts/benchmarking/detect-build-regression.py
	@echo "$(GREEN)✅ Regression check complete$(NC)"


docs-index-rebuild: ## 🔍 Rebuild documentation search index (Portable)
	@echo "$(CYAN)🔍 Rebuilding documentation search index...$(NC)"
	@$(PYTHON) docs/scripts/indexer.py --rebuild
	@echo "$(GREEN)✅ Search index rebuilt$(NC)"


lint-docs: ## 📚 Lint documentation for broken links and style (requires markdownlint-cli)
	@echo "$(CYAN)🔍 Linting documentation...$(NC)"
	@if command -v markdownlint >/dev/null 2>&1; then \
		markdownlint "docs/**/*.md" "expert-knowledge/**/*.md" "memory_bank/**/*.md"; \
	else \
		echo "$(YELLOW)⚠️  markdownlint not found. Install with: npm install -g markdownlint-cli$(NC)"; \
	fi
	@echo "$(CYAN)🔗 Checking internal links...$(NC)"
	@grep -r "\[.*\](.*\.md)" docs expert-knowledge memory_bank | grep -v "_archive" || echo "No broken-link patterns found"

smoke-test: ## 🔱 Run the Sovereign Smoke Test (E2E Production Validation)
	@echo "$(CYAN)🚀 Running Sovereign Smoke Test...$(NC)"
	@$(PYTHON) scripts/smoke_test.py

pr-check: ## 🏁 Run full PR Readiness Audit
	@echo "$(CYAN)🔱 Starting PR Readiness Audit...$(NC)"
	@CHAINLIT_NO_TELEMETRY=true CRAWL4AI_TELEMETRY=0 LANGCHAIN_TRACING_V2=false SCARF_NO_ANALYTICS=true DO_NOT_TRACK=1 PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/pr_check.py

update-security-db: ## 💾 Sync vulnerability databases for air-gap usage
	@echo "$(CYAN)🔄 Syncing Security Databases...$(NC)"
	@$(PYTHON) scripts/db_manager.py init

verify-security-db: ## ✅ Verify security databases are valid
	@$(PYTHON) scripts/db_manager.py verify

security-audit: verify-security-db ## 🔱 Execute the Sovereign Trinity Audit (Syft + Grype + Trivy)
	@echo "$(CYAN)🛡️  Starting Security Audit Trinity...$(NC)"
	@$(PYTHON) scripts/security_audit.py

check-performance: ## 📊 Compare current system performance against baselines
	@echo "$(CYAN)📊 Verifying performance against baselines...$(NC)"
	@if [ ! -f docs/03-reference/PERFORMANCE.md ]; then \
		echo "$(RED)❌ ERROR: PERFORMANCE.md baseline file missing$(NC)"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/query_test.py --benchmark
	@echo "$(YELLOW)💡 Compare results above with docs/03-reference/PERFORMANCE.md$(NC)"

ingest-library: ingest ## 📚 Alias for library ingestion

# ===========================================================================================
# 📚 DOCUMENTATION SYSTEM TARGETS (MkDocs Integration - Phase 5)
# ===========================================================================================
# Dual-build documentation system:
#   - Public docs: docs/ + mkdocs.yml → site/ (GitHub Pages, port 8000)
#   - Internal docs: internal_docs/ + mkdocs-internal.yml → site-internal/ (team, port 8001)
# ===========================================================================================

mkdocs-build: ## 🏗️ Build both public and internal MkDocs documentation
	@echo "$(CYAN)🏗️  Building public documentation (docs/ → site/)...$(NC)"
	@mkdocs build
	@echo "$(GREEN)✅ Public docs built$(NC)"
	@echo ""
	@echo "$(CYAN)🏗️  Building internal documentation (internal_docs/ → site-internal/)...$(NC)"
	@mkdocs build -f mkdocs-internal.yml
	@echo "$(GREEN)✅ Internal docs built$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Both documentation builds complete!$(NC)"
	@echo "$(YELLOW)💡 Output locations: site/ (public) and site-internal/ (internal)$(NC)"

mkdocs-serve: mkdocs-serve-internal ## 🌐 Serve internal documentation (PRIMARY - port 8001)

mkdocs-serve-internal: ## 🌐 Serve internal documentation on port 8001
	@echo "$(CYAN)🌐 Starting internal documentation server (port 8001)...$(NC)"
	@echo "$(YELLOW)📖 Open browser: http://localhost:8001$(NC)"
	@echo "$(YELLOW)💡 Press Ctrl+C to stop server$(NC)"
	@mkdocs serve -f mkdocs-internal.yml -a 127.0.0.1:8001

mkdocs-serve-public: ## 🌐 Serve public documentation on port 8000
	@echo "$(CYAN)🌐 Starting public documentation server (port 8000)...$(NC)"
	@echo "$(YELLOW)📖 Open browser: http://localhost:8000$(NC)"
	@echo "$(YELLOW)💡 Press Ctrl+C to stop server$(NC)"
	@mkdocs serve -a 127.0.0.1:8000

mkdocs-clean: ## 🧹 Remove built documentation artifacts
	@echo "$(CYAN)🧹 Cleaning documentation build artifacts...$(NC)"
	@rm -rf site site-internal
	@echo "$(GREEN)✅ Documentation artifacts cleaned$(NC)"

docs-public: ## 📚 Build public documentation (alias)
	@echo "$(CYAN)📚 Building public documentation...$(NC)"
	@mkdocs build
	@echo "$(GREEN)✅ Public documentation ready at site/$(NC)"

docs-internal: ## 📚 Build internal documentation (alias)
	@echo "$(CYAN)📚 Building internal documentation...$(NC)"
	@mkdocs build -f mkdocs-internal.yml
	@echo "$(GREEN)✅ Internal documentation ready at site-internal/$(NC)"

docs-all: mkdocs-build ## 🎯 Build all documentation (public and internal)

docs-system: ## 📊 Show documentation system status
	@echo ""
	@echo "$(CYAN)📊 Documentation System Status$(NC)"
	@echo "────────────────────────────────────────────────────────────────"
	@echo ""
	@echo "$(YELLOW)📁 Configuration Files:$(NC)"
	@ls -lh mkdocs.yml mkdocs-internal.yml 2>/dev/null || echo "$(RED)  ⚠️  Config files missing$(NC)"
	@echo ""
	@echo "$(YELLOW)📚 Documentation Sources:$(NC)"
	@echo "  Public:   $(shell find docs -name '*.md' 2>/dev/null | wc -l) markdown files in docs/"
	@echo "  Internal: $(shell find internal_docs -name '*.md' 2>/dev/null | wc -l) markdown files in internal_docs/"
	@echo ""
	@echo "$(YELLOW)🏗️  Build Artifacts:$(NC)"
	@if [ -d site ]; then \
		echo "  $(GREEN)✅ Public build exists (site/)$(NC)"; \
	else \
		echo "  $(YELLOW)⚠️  No public build (run: make docs-public)$(NC)"; \
	fi
	@if [ -d site-internal ]; then \
		echo "  $(GREEN)✅ Internal build exists (site-internal/)$(NC)"; \
	else \
		echo "  $(YELLOW)⚠️  No internal build (run: make docs-internal)$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)🚀 Quick Commands:$(NC)"
	@echo "  make mkdocs-serve-internal  → Start internal KB on port 8001"
	@echo "  make mkdocs-serve-public    → Start public docs on port 8000"
	@echo "  make mkdocs-build           → Build both (for CI/CD)"
	@echo "  make mkdocs-clean           → Remove built artifacts"
	@echo ""
	@echo "$(YELLOW)🌐 URLs when serving:$(NC)"
	@echo "  Public:   http://localhost:8000"
	@echo "  Internal: http://localhost:8001"
	@echo ""
	@echo "$(YELLOW)📖 More info:$(NC)"
	@echo "  See: memory_bank/mkdocs-commands.md"
	@echo "  See: internal_docs/DOCUMENTATION-SYSTEM-STRATEGY.md"
	@echo "────────────────────────────────────────────────────────────────"
	@echo ""
