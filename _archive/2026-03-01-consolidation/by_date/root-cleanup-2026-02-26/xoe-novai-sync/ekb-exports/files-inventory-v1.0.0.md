---
version: 1.0.0
tags: [ekb, inventory, sync]
date: 2026-01-29
ma_at_mappings: [7: Truth in synthesis, 18: Balance in structure]
sync_status: initial
---

# Project File Inventory (v1.0.0)

## Overview
This document provides a comprehensive list of files within the Xoe-NovAi project root (`/home/arcana-novai/Documents/Xoe-NovAi/`). It serves as a baseline for synchronization between local environments and cloud-hosted strategy layers.

## Full Tree Inventory (Excluding .git, __pycache__)

### Root Files
- pyproject.toml
- requirements-curation_worker.in
- Dockerfile
- Dockerfile.crawl
- requirements-api.txt
- CONTRIBUTING.md
- pytest.ini
- requirements-api.in
- Dockerfile.chainlit
- chainlit_app_voice.py
- CODE_OF_CONDUCT.md
- README.md
- Makefile
- config.toml
- .env.example
- LICENSE
- Dockerfile.awq
- docker-compose.yml
- .gitignore
- mkdocs.yml
- .env
- requirements-curation_worker.txt
- Dockerfile.base
- chainlit.md
- av-16.1.0-cp313-cp313-manylinux_2_28_x86_64.whl
- requirements-chainlit.in
- Dockerfile.curation_worker
- Dockerfile.docs
- .geminiignore
- requirements-crawl.in
- requirements-crawl.txt
- .dockerignore
- .env.library_apis
- requirements-chainlit.txt

### Core Application (app/)
- app/library_api_integrations.py
- app/logging_config.py
- app/config.toml
- app/__init__.py
- app/metrics.py
- app/XNAi_rag_app/voice_interface.py
- app/XNAi_rag_app/voice_degradation.py
- app/XNAi_rag_app/__init__.py
- app/XNAi_rag_app/schemas/requests.py
- app/XNAi_rag_app/schemas/__init__.py
- app/XNAi_rag_app/schemas/responses.py
- app/XNAi_rag_app/schemas/errors.py
- app/XNAi_rag_app/workers/__init__.py
- app/XNAi_rag_app/workers/crawl.py
- app/XNAi_rag_app/workers/curation_worker.py
- app/XNAi_rag_app/core/circuit_breakers.py
- app/XNAi_rag_app/core/logging_config.py
- app/XNAi_rag_app/core/verify_imports.py
- app/XNAi_rag_app/core/dynamic_precision.py
- app/XNAi_rag_app/core/__init__.py
- app/XNAi_rag_app/core/vulkan_acceleration.py
- app/XNAi_rag_app/core/iam_service.py
- app/XNAi_rag_app/core/memory_bank_integration.py
- app/XNAi_rag_app/core/async_patterns.py
- app/XNAi_rag_app/core/services_init.py
- app/XNAi_rag_app/core/embeddings_shim.py
- app/XNAi_rag_app/core/dependencies.py
- app/XNAi_rag_app/core/maat_guardrails.py
- app/XNAi_rag_app/core/metrics.py
- app/XNAi_rag_app/core/awq_quantizer.py
- app/XNAi_rag_app/core/vectorstore_shim.py
- app/XNAi_rag_app/core/config_loader.py
- app/XNAi_rag_app/core/observability.py
- app/XNAi_rag_app/models/domain.py
- app/XNAi_rag_app/models/__init__.py
- app/XNAi_rag_app/services/library_api_integrations.py
- app/XNAi_rag_app/services/research_agent.py
- app/XNAi_rag_app/services/__init__.py
- app/XNAi_rag_app/services/ingest_library.py
- app/XNAi_rag_app/services/crawler_curation.py
- app/XNAi_rag_app/services/rag/__init__.py
- app/XNAi_rag_app/services/rag/rag_service.py
- app/XNAi_rag_app/services/rag/retrievers.py
- app/XNAi_rag_app/services/voice/voice_interface.py
- app/XNAi_rag_app/services/voice/voice_degradation.py
- app/XNAi_rag_app/services/voice/__init__.py
- app/XNAi_rag_app/services/voice/voice_recovery.py
- app/XNAi_rag_app/services/voice/voice_command_handler.py
- app/XNAi_rag_app/ui/chainlit_app_voice.py
- app/XNAi_rag_app/ui/__init__.py
- app/XNAi_rag_app/ui/chainlit_app.py
- app/XNAi_rag_app/ui/chainlit_curator_interface.py
- app/XNAi_rag_app/api/exceptions.py
- app/XNAi_rag_app/api/api_docs.py
- app/XNAi_rag_app/api/__init__.py
- app/XNAi_rag_app/api/entrypoint.py
- app/XNAi_rag_app/api/healthcheck.py
- app/XNAi_rag_app/api/main.py
- app/XNAi_rag_app/api/routers/__init__.py
- app/XNAi_rag_app/api/routers/health.py
- app/XNAi_rag_app/api/routers/query.py

### Memory Bank (memory_bank/)
- memory_bank/activeContext.md
- memory_bank/agent_capabilities_summary.md
- memory_bank/last_work_session_20260128.md
- memory_bank/contextProtocols.md
- memory_bank/productContext.md
- memory_bank/techContext.md
- memory_bank/claude.md
- memory_bank/teamProtocols.md
- memory_bank/onboardingChecklist.md
- memory_bank/systemPatterns.md
- memory_bank/environmentContext.md
- memory_bank/progress.md
- memory_bank/remediation_summary_20260128.md
- memory_bank/mcpConfiguration.md
- memory_bank/cline.md
- memory_bank/gemini.md
- memory_bank/projectbrief.md
- memory_bank/grok.md

### Documentation (docs/)
Structured via Diátaxis framework:
- **01-start/**: Quick start, onboarding.
- **02-tutorials/**: Voice setup, sovereign setup, prompt engineering.
- **03-how-to-guides/**: Dev workflow, buildtime cache, runbooks, security DB management.
- **03-reference/**: Hardware, API, Master Plan, Project History, CLI timeout guide.
- **04-explanation/**: Stack architecture, sovereign ethics, project charter, component registry.
- **05-research/**: Gemini CLI agentic report, partnership opportunities, phase 2 research.
- **06-development-log/**: strategic implementation plan, observability plans, sovereign security trinity blueprint.
- **diagrams/**: stack-mermaid.md.
- **_archive/**: Legacy and superseded documentation (high-volume).

### Expert Knowledge (expert-knowledge/)
- expert-knowledge/README.md
- expert-knowledge/url-registry.json
- expert-knowledge/infrastructure/podman_quadlet_mastery.md
- expert-knowledge/coder/buildkit_best_practices.md
- expert-knowledge/coder/claude-implementation-insights.md
- expert-knowledge/coder/uv_timeout_optimization.md
- expert-knowledge/coder/code-audit-templates.md
- expert-knowledge/research/ekb-research-master-v1.0.0.md
- expert-knowledge/environment/buildkit_cache_hardlining.md
- expert-knowledge/protocols/workflows-master-v1.0.0.md
- [Detailed domain files in coder/, architect/, environment/, esoteric/]

### Internal Documentation (internal_docs/)
- internal_docs/documentation_strategy.md
- internal_docs/branding_and_identity.md
- internal_docs/dev/ServiceOrchestrator_design.md
- internal_docs/Grok MC/Grok-MC-stack-mermaid.md

### Scripts (scripts/)
- scripts/preflight_checks.py
- scripts/regenerate_requirements_py312_cached.sh
- scripts/setup_volumes.sh
- scripts/clean_wheelhouse_duplicates.sh
- scripts/detect_environment.sh
- scripts/doc_checks.sh
- scripts/build_tracking.py
- scripts/run_tests.sh
- scripts/security_audit.py
- scripts/security_policy.py
- scripts/smoke_test.py
- scripts/enterprise_build.sh
- scripts/db_manager.py
- scripts/pr_check.py
- scripts/infra/butler.sh

### Sync & Meta (xoe-novai-sync/, _meta/)
- xoe-novai-sync/projects/
- xoe-novai-sync/ekb-exports/
- xoe-novai-sync/mc-imports/
- xoe-novai-sync/origins/
- xoe-novai-sync/_meta/
- _meta/locks/task-grok-protocol-init-complete.yaml
- _meta/locks/task-file-cleanup-lock.yaml