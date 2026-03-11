# Tiered startup for resource-constrained systems (6.6GB RAM)
# Part of Task C2: Fix Docker Compose Memory Over-Commit

COMPOSE := podman-compose -f docker-compose.yml

.PHONY: up-core up-app up-full down status

# Tier 1: Core Services (~1.5GB - 2GB)
# Essential for any operation: Redis, Postgres, Qdrant, Caddy, MBMCP
up-core:
	@echo "🚀 Starting Core Services (Tier 1)..."
	$(COMPOSE) up -d redis postgres qdrant caddy memory-bank-mcp
	@echo "✅ Core Services started. Check status with 'make status'"

# Tier 2: Application Services (~4GB - 5GB total)
# Core + RAG API and UI
up-app: up-core
	@echo "🚀 Starting Application Services (Tier 2)..."
	$(COMPOSE) up -d rag ui
	@echo "✅ Application Services started. Total memory usage estimated: 5GB"

# Tier 3: Full Stack (~10GB+ total - MAY SWAP/OOM ON 6.6GB)
# All 14 services
up-full:
	@echo "⚠️ Starting Full Stack (Tier 3)..."
	@echo "⚠️ Warning: This may exceed 6.6GB RAM and cause OOM on your host."
	$(COMPOSE) up -d
	@echo "✅ Full Stack attempted."

down:
	$(COMPOSE) down

status:
	$(COMPOSE) ps
