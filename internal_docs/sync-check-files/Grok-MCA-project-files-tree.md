arcana-novai@Arcana-NovAi:~/Documents/Xoe-NovAi$ tree -L 3
.
├── app
│   └── XNAi_rag_app
│       ├── chainlit_app.py
│       ├── chainlit_app_voice.py
│       ├── chainlit_app_with_voice.py
│       ├── chainlit_curator_interface.py
│       ├── config_loader.py
│       ├── crawler_curation.py
│       ├── crawl.py
│       ├── curation_worker.py
│       ├── dependencies.py
│       ├── healthcheck.py
│       ├── ingest_library.py
│       ├── __init__.py
│       ├── library_api_integrations.py
│       ├── logging_config.py
│       ├── main.py
│       ├── metrics.py
│       ├── __pycache__
│       ├── verify_imports.py
│       ├── voice_command_handler.py
│       └── voice_interface.py
├── backups  [error opening dir]
├── build_tools.log
├── chainlit_app_voice.py
├── config.toml
├── data  [error opening dir]
├── docker-api-build.log
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.chainlit
├── Dockerfile.crawl
├── Dockerfile.curation_worker
├── docker-ui-build.log
├── docs
│   ├── 01-getting-started
│   │   ├── 01-QUICK_START_MAKEFILE.md
│   │   ├── 01-START_HERE.md
│   │   ├── 02-podman-installation-guide.md
│   │   ├── 03-advanced-features-user-guide.md
│   │   ├── 04-redis-sentinel-cluster-guide.md
│   │   ├── 05-awq-production-pipeline-guide.md
│   │   ├── 06-neural-bm25-retrieval-guide.md
│   │   ├── beginner-guide.md
│   │   └── README.md
│   ├── 02-development
│   │   ├── 2026_implementation_plan.md
│   │   ├── 6_week_stack_enhancement_plan.md
│   │   ├── best_practices_research.md
│   │   ├── build-performance.md
│   │   ├── build_timeline.md
│   │   ├── checklist.md
│   │   ├── claude-briefing-update-research-request.md
│   │   ├── Claude Fix Rpeort - Docker to Podman move issues and chache_from errors.md
│   │   ├── claude-guides-analysis-outline.md
│   │   ├── claude-research-integration-report.md
│   │   ├── claude-v2-integration-assessment.md
│   │   ├── code-review-checklists.md
│   │   ├── code-review-files.md
│   │   ├── code-skeletons.md
│   │   ├── COMPREHENSIVE_STACK_POLISHING_ROADMAP.md
│   │   ├── CRITICAL_BLOCKERS_REPORT.md
│   │   ├── dependency-tracking-matrix.md
│   │   ├── DEPENDENCY_UPDATE_ENTERPRISE_IMPLEMENTATION.md
│   │   ├── DEPENDENCY_UPDATE_IMPLEMENTATION_GUIDE.md
│   │   ├── deployment-operations-guide.md
│   │   ├── developer-portability-guide.md
│   │   ├── docker-mkdocs-optimization-complete.md
│   │   ├── docker-setup.md
│   │   ├── docs-enhancement-roadmap.md
│   │   ├── enhanced-metrics-implementation-report.md
│   │   ├── enterprise-build.md
│   │   ├── enterprise_build_system_final_report.md
│   │   ├── enterprise-enhancement-implementation-roadmap.md
│   │   ├── enterprise-transformation-risk-assessment.md
│   │   ├── FULL_STACK_AUDIT_REPORT.md
│   │   ├── github-protocol-guide.md
│   │   ├── holistic-integration-execution-plan.md
│   │   ├── howto_template.md
│   │   ├── implementation-checklist.md
│   │   ├── implementation-execution-tracker.md
│   │   ├── implementation-summary.md
│   │   ├── index.md
│   │   ├── library-api.md
│   │   ├── library-api-readme.md
│   │   ├── makefile-usage.md
│   │   ├── mkdocs-docker-audit-critical-findings.md
│   │   ├── mkdocs-enterprise-enhancement-plan.md
│   │   ├── mkdocs-rag-integration-roadmap.md
│   │   ├── mkdocs-research-implementation-summary.md
│   │   ├── ml_docker_optimization_guide.md
│   │   ├── ml_docker_optimization_guide_v2.md
│   │   ├── monitoring-observability-plan.md
│   │   ├── next_steps_strategy.md
│   │   ├── offline-build-logging.md
│   │   ├── offline-deployment.md
│   │   ├── permissions-mitigation-implementation.md
│   │   ├── phase1_day2_circuit_breaker_testing.md
│   │   ├── phase1-implementation-guide.md
│   │   ├── phase1-implementation-status-report.md
│   │   ├── phase-1.md
│   │   ├── phase1_progress_tracker.md
│   │   ├── phase1_week1_security_errorhandling_ux.md
│   │   ├── phase-2-3.md
│   │   ├── phase3_day34_execution_complete.md
│   │   ├── phase3_day567_execution_complete.md
│   │   ├── phase3_implementation_guide_research_verified.md
│   │   ├── phase3_research_audit_complete.md
│   │   ├── piper-onnx-complete.md
│   │   ├── piper-onnx-implementation-complete.md
│   │   ├── piper-onnx-implementation-summary.md
│   │   ├── piper-onnx-summary.md
│   │   ├── plugin_architecture_design.md
│   │   ├── POLISHING_INTEGRATION_SUMMARY.md
│   │   ├── POLISHING_MASTER_INDEX.md
│   │   ├── polishing-progress-tracker.md
│   │   ├── production-integration-roadmap.md
│   │   ├── production-stability-audit.md
│   │   ├── project-status-tracker.md
│   │   ├── project-tracking-dashboard.md
│   │   ├── qdrant-agentic-migration.md
│   │   ├── qdrant-checklist.md
│   │   ├── qdrant-index.md
│   │   ├── qdrant-integration.md
│   │   ├── qdrant-migration.md
│   │   ├── quality-assurance-framework.md
│   │   ├── quick-reference-checklist.md
│   │   ├── quick-start.md
│   │   ├── README.md
│   │   ├── research-implementation-tasks.md
│   │   ├── research-integration-master-plan.md
│   │   ├── research-integration-summary.md
│   │   ├── risk-assessment-mitigation.md
│   │   ├── rootless-docker-roadmap.md
│   │   ├── script_optimization_tracker.md
│   │   ├── site-wide-implementation-roadmap.md
│   │   ├── technical-debt-register.md
│   │   ├── tts-options.md
│   │   ├── UNIFIED_IMPLEMENTATION_GUIDE.md
│   │   ├── UX_TEST_FRESH_BUILD_20260110.md
│   │   ├── visual-reference.md
│   │   ├── voice-enterprise.md
│   │   ├── voice-interface-guide.md
│   │   ├── voice-quick-reference.md
│   │   ├── voice-setup.md
│   │   ├── vulkan-igpu-implementation-log.md
│   │   ├── vulkan-integration-roadmap.md
│   │   ├── week1-2_implementation_log.md
│   │   ├── week1-completion-summary.md
│   │   ├── week1-dependency-audit.md
│   │   ├── week1-implementation-plan.md
│   │   ├── week1-progress-summary.md
│   │   ├── week1_rollback_procedures.md
│   │   ├── week2-implementation-plan.md
│   │   ├── week2_implementation_plan.md
│   │   ├── week2-progress-summary.md
│   │   ├── week3-implementation-plan.md
│   │   ├── week3-progress-summary.md
│   │   ├── wheelhouse-build.md
│   │   ├── wheelhouse-build-tracking.md
│   │   └── xoe-novai-implementation-completeness-report.md
│   ├── 03-architecture
│   │   ├── architecture.md
│   │   ├── audio-research.md
│   │   ├── audio-strategy.md
│   │   ├── blueprint.md
│   │   ├── CODE_REVIEW_2026_01_05.md
│   │   ├── condensed-guide.md
│   │   ├── crawler-optimization.md
│   │   ├── curator-enhancement.md
│   │   ├── data-directories.md
│   │   ├── docker-code-changes.md
│   │   ├── docker-optimization.md
│   │   ├── docker-services.md
│   │   ├── docker-summary.md
│   │   ├── docker-visual-guide.md
│   │   ├── DR - Top 20 Resources for EmbGemma in XNAi.md
│   │   ├── EmbeddingGemma model card.md
│   │   ├── enhancement-architecture-multi-agent-orchestration.md
│   │   ├── enhancement-dependency-tracking.md
│   │   ├── enhancement-learning-evolving-agents.md
│   │   ├── enhancement-lfm25-voice-integration.md
│   │   ├── enhancement-performance-distributed-vector-storage.md
│   │   ├── enhancement-persona-system-intelligence.md
│   │   ├── enhancement-project-completion-summary.md
│   │   ├── enhancement-security-zero-trust-architecture.md
│   │   ├── enhancement-voice-to-voice-basic.md
│   │   ├── enterprise-strategy.md
│   │   ├── implementation-roadmap.md
│   │   ├── organization-plan.md
│   │   ├── project-charter.md
│   │   ├── project-overview.md
│   │   ├── qdrant-agentic-api.md
│   │   ├── rag-refinements.md
│   │   ├── README.md
│   │   ├── STACK_ARCHITECTURE_AND_TECHNOLOGY_SUPPLEMENT.md
│   │   ├── stack-cat-guide.md
│   │   ├── STACK_STATUS.md
│   │   ├── TECHNICAL_STACK_AUDIT_TRACKING.md
│   │   ├── TECHNICAL_STACK_DOCUMENTATION.md
│   │   ├── ux_timing_system_final_report.md
│   │   └── xnai_v0.1.5_voice_addendum.md
│   ├── 04-operations
│   │   ├── build-logging.md
│   │   ├── build-tools.md
│   │   ├── code-updates-tracker.md
│   │   ├── docker-build-troubleshooting.md
│   │   ├── docker-testing.md
│   │   ├── ingestion-system-enhancements.md
│   │   ├── local-telemetry-free-tts-options.md
│   │   ├── make-up-test-results.md
│   │   ├── qdrant-performance-tuning.md
│   │   ├── README.md
│   │   ├── runbook_template.md
│   │   ├── security-fixes-runbook.md
│   │   ├── updates-running.md
│   │   └── voice-deployment.md
│   ├── 05-governance
│   │   ├── audit_summary_20260110.md
│   │   ├── CHANGELOG.md
│   │   ├── Cline Rules.md
│   │   ├── delivery-complete.md
│   │   ├── DOCS_STRATEGY.md
│   │   ├── DOCUMENTATION_BEST_PRACTICES.md
│   │   ├── documentation-changelog.md
│   │   ├── DOCUMENTATION_DRIFT_PREVENTION.md
│   │   ├── executive-audit.md
│   │   ├── executive-summary.md
│   │   ├── implementation-complete.md
│   │   ├── implementation-package-summary.md
│   │   ├── OWNERS.md
│   │   ├── phase-2-completion.md
│   │   ├── POLICIES.md
│   │   ├── policy_template.md
│   │   ├── pr-release-notes.md
│   │   ├── README.md
│   │   ├── v0.1.4-stable.md
│   │   ├── v0.1.4-stable-release-readiness-audit.md
│   │   ├── v0.1.5.md
│   │   └── version-management-policy.md
│   ├── 06-meta
│   │   ├── AI_ASSISTANT_GUIDE.md
│   │   ├── bash_best_practices_research.md
│   │   ├── bash_script_execution_issues.md
│   │   ├── DEPENDENCY_UPDATE_RESEARCH_PLAN.md
│   │   ├── DOCUMENTATION_AUDIT_CHANGES.md
│   │   ├── final-organization-summary.md
│   │   ├── Grok - 2026 Tech & Strategy Update Report.md
│   │   ├── Grok - 2026 Tech & Strategy Update v2.md
│   │   ├── Grok - 2026 Tech & Strategy Update v3.md
│   │   ├── Grok - 2026 Tech & Strategy Update v4.md
│   │   ├── Grok - 2026 Tech & Strategy Update v5.md
│   │   ├── Grok - Additional Research Update v5.md
│   │   ├── Grok - BIOS Script Update v5.md
│   │   ├── grok_deep_research_response.md
│   │   ├── Grok - Doc Update v5.md
│   │   ├── GROK_EXPERT_ONBOARDING_REPORT.md
│   │   ├── implementation-files-organization-complete.md
│   │   ├── implementation-files-review.md
│   │   ├── migration-report.md
│   │   ├── organization-complete.md
│   │   ├── organization-summary.md
│   │   ├── pip_progress_interception_research.md
│   │   └── README.md
│   ├── 99-research
│   │   ├── Complete Vulkan Offload Guide for Xoe-NovAi.md
│   │   ├── enterprise-modernization
│   │   ├── faiss-architecture
│   │   ├── kokoro-tts
│   │   ├── mkdocs
│   │   ├── Operational Stack Readiness Research Fulfillment.md
│   │   ├── operational-stack-readiness-research.md
│   │   ├── README.md
│   │   ├── stack-2026
│   │   ├── Top 5 Most Critical Cutting-Edge Practices.md
│   │   └── vulkan-inference
│   ├── AI_ASSISTANT_GUIDE.md
│   ├── ai-research
│   │   ├── admin
│   │   ├── AWQ Quantization Production Implementation Research Report.md
│   │   ├── claude-onboarding-document.md
│   │   ├── claude-research-initiation-prompt.md
│   │   ├── completed-research
│   │   ├── comprehensive-claude-research-synthesis.md
│   │   ├── current-research
│   │   ├── Grok - Podman for Multi-Container Orchestration in Xoe-NovAi.md
│   │   ├── implementation-tracking
│   │   ├── notebooklm-video-generation-research.md
│   │   ├── PRR-P1-WATERMARK-003 Educational Briefing AI Content Watermarking.md
│   │   ├── README.md
│   │   ├── remaining-research-questions.md
│   │   ├── requests
│   │   ├── research-requests
│   │   ├── research-responses
│   │   └── responses
│   ├── archive
│   │   ├── code-review-sessions
│   │   ├── duplicates
│   │   ├── historical
│   │   ├── old-versions
│   │   ├── README.md
│   │   └── sessions
│   ├── assets
│   │   ├── downloads
│   │   ├── images
│   │   └── videos
│   ├── audit
│   │   ├── CONTENT_CLASSIFICATION.md
│   │   ├── CONTENT_INVENTORY.md
│   │   ├── ORGANIZATION_PLAN.md
│   │   └── XOE_NOVAI_CLAUDE_ALIGNMENT_AUDIT.md
│   ├── audit-progress.md
│   ├── best-practices
│   │   ├── docker-buildkit-wheelhouse-guide.md
│   │   ├── python-version-management.md
│   │   ├── README.md
│   │   └── uv-integration-guide.md
│   ├── broken_links_report.json
│   ├── build_visualizations
│   │   ├── build_flow.pdf
│   │   └── build_timeline.md
│   ├── business-opportunities.md
│   ├── CHAINLIT_DOWNGRADE_ANALYSIS.md
│   ├── claude-research-requirements-q1-2026.md
│   ├── cline-session-continuation.md
│   ├── cline-session-onboarding.md
│   ├── compliance
│   ├── critical_mkdocs_research_focus.md
│   ├── deep_research
│   │   ├── 01-vulkan-native-inference.md
│   │   ├── 02-kokoro-v2-voice-synthesis.md
│   │   ├── 03-advanced-faiss-architecture.md
│   │   ├── 04-system-resilience-extensibility.md
│   │   ├── 05-neural-compilation-paradigms.md
│   │   ├── Claude code audit - 01-13-2026.md
│   │   ├── Claude__Sonnet 4-5 enhanced__code audit - 01-13-2026.md
│   │   ├── Grok - DR - FastAPI and version conflict resolution  (Jan 13, 2026).md
│   │   ├── Grok-DR-Mkdocs-integration.md
│   │   ├── Grok - DR -  Overview & Guiding Principles (2026 Edition).md
│   │   ├── Grok - DR - Speed up pip downloads (2026).md
│   │   ├── Grok - DR - Technical Guide Enforcing Python 3.12.md
│   │   ├── Grok- DR - UV advanced features and usage.md
│   │   ├── Grok- DR - UV security and ruff linter.md
│   │   ├── mkdocs-error-resolution-research-request.md
│   │   ├── mkdocs_research_solutions.md
│   │   ├── README.md
│   │   ├── research-request-v1.md
│   │   ├── xnai_implementation_guide.py
│   │   ├── xnai_knowledge_gap_findings.md
│   │   ├── xnai_stack_research_2026.md
│   │   └── xnai_top_3_deep_research_findings.md
│   ├── design
│   │   ├── audio-research.md
│   │   ├── audio-strategy.md
│   │   ├── crawler-optimization.md
│   │   ├── curator-enhancement.md
│   │   ├── docker-code-changes.md
│   │   ├── docker-optimization.md
│   │   ├── docker-summary.md
│   │   ├── docker-visual-guide.md
│   │   ├── enterprise-strategy.md
│   │   ├── final-organization-summary.md
│   │   ├── implementation-files-organization-complete.md
│   │   ├── implementation-files-review.md
│   │   ├── implementation-roadmap.md
│   │   ├── organization-complete.md
│   │   ├── organization-plan.md
│   │   ├── organization-summary.md
│   │   ├── rag-refinements.md
│   │   └── README.md
│   ├── Dockerfile.docs
│   ├── docs_freshness_report.json
│   ├── DOCUMENTATION_AUDIT_CHECKLIST.md
│   ├── documentation-consolidation-project
│   │   ├── DOCUMENTATION_CONSOLIDATION_PROJECT_README.md
│   │   ├── DOCUMENTATION_CONSOLIDATION_PROJECT_TRACKER.md
│   │   ├── DOCUMENTATION_PROJECT_SUPPLEMENTALS.json
│   │   ├── DRR-DOCS-001_SUPPLEMENTAL_CONTEXT.md
│   │   ├── GROK_DOCUMENTATION_CONSOLIDATION_REQUEST.md
│   │   ├── PR_DOCUMENTATION_ORGANIZATION_RECOMMENDATION.md
│   │   ├── README.md
│   │   ├── USER_GUIDES_CRAFTING_PLAN.md
│   │   ├── xoe-novai-documentation-consolidation-specialist-v1.0.md
│   │   └── xoe-novai-research-expert-v2.0.md
│   ├── DOCUMENTATION_MAINTENANCE_INDEX.md
│   ├── DR-research-request-from -Cline - 01_13_2026.md
│   ├── enhancements
│   │   ├── enhancement-architecture-multi-agent-orchestration.md
│   │   ├── enhancement-dependency-tracking.md
│   │   ├── enhancement-learning-evolving-agents.md
│   │   ├── enhancement-lfm25-voice-integration.md
│   │   ├── enhancement-performance-distributed-vector-storage.md
│   │   ├── enhancement-persona-system-intelligence.md
│   │   ├── enhancement-project-completion-summary.md
│   │   ├── enhancement-security-zero-trust-architecture.md
│   │   └── enhancement-voice-to-voice-basic.md
│   ├── example-prompts
│   │   ├── Grok-MkDocs-Enterprise-Expert.md
│   │   └── Grok-MkDocs-Enterprise-Expert - v2.md
│   ├── explanation
│   │   └── system-overview.md
│   ├── freshness-report.md
│   ├── governance
│   ├── grok_deep_research_request.md
│   ├── grok_mkdocs_research_request.md
│   ├── handover-readiness-report.md
│   ├── how-to
│   │   ├── docker-deployment.md
│   │   ├── enterprise-integration.md
│   │   ├── index.md
│   │   ├── mkdocs-tutorials
│   │   ├── performance-tuning.md
│   │   ├── testing-strategy.md
│   │   ├── troubleshooting.md
│   │   └── voice-setup.md
│   ├── howto
│   │   ├── docker-setup.md
│   │   ├── github-protocol-guide.md
│   │   ├── library-api.md
│   │   ├── library-api-readme.md
│   │   ├── makefile-usage.md
│   │   ├── offline-build-logging.md
│   │   ├── offline-deployment.md
│   │   ├── qdrant-checklist.md
│   │   ├── qdrant-index.md
│   │   ├── qdrant-migration.md
│   │   ├── quick-start.md
│   │   ├── README.md
│   │   ├── tts-options.md
│   │   ├── voice-enterprise-guide.py
│   │   ├── voice-enterprise.md
│   │   ├── voice-interface-guide.md
│   │   ├── voice-quick-reference.md
│   │   ├── voice-setup.md
│   │   └── wheelhouse-build.md
│   ├── implementation
│   │   ├── advanced-features.md
│   │   ├── core-patterns.md
│   │   ├── implementation-checklist.md
│   │   ├── implementation-status.txt
│   │   ├── library-api.md
│   │   ├── phase-1-5
│   │   ├── phase-1-5-summary.txt
│   │   ├── phase-1.md
│   │   ├── phase-2-3.md
│   │   ├── piper-onnx-complete.md
│   │   ├── piper-onnx-summary.md
│   │   ├── project-status-tracker.md
│   │   ├── qdrant-integration.md
│   │   ├── quick-reference-checklist.md
│   │   └── README.md
│   ├── incoming
│   │   ├── Additional 2026 Best Practices for Integration.md
│   │   ├── Advanced Diátaxis Patterns Guide.md
│   │   ├── Advanced MkDocStrings Options Guide.md
│   │   ├── Claude - Advanced AI Hardware & Security Research Supplement (2026-2027) - incomplete.md
│   │   ├── Claude - AI Enhancement Metrics.md
│   │   ├── Claude - AWQ Quantization Production Implementation Research Report.md
│   │   ├── Claude - Comprehensive Cline AI Assistant Briefing Xoe-NovAi v0.md
│   │   ├── Claude - Comprehensive Cline AI Assistant Briefing Xoe-NovAi v1 - supplemental.md
│   │   ├── Claude - Comprehensive Cline AI Assistant Briefing Xoe-NovAi v2 - incomplete.md
│   │   ├── Claude - Comprehensive Cline AI Assistant Briefing Xoe-NovAi v3 - complete.md
│   │   ├── Claude - Comprehensive System Briefing and Research - doc 1.md
│   │   ├── Claude - config_improvements_report_v1.md
│   │   ├── Claude - config_improvements_report_v2.md
│   │   ├── Claude - config_improvements_report_v3.md
│   │   ├── Claude - critical_issues_guide.md
│   │   ├── Claude - enterprise_integration_matrix.md
│   │   ├── Claude - high_priority_guide.md
│   │   ├── Claude - medium_priority_guide - incomplete.md
│   │   ├── Claude - mkdocs-master-guide-complete.md
│   │   ├── Claude - mkdocs_rag_enhanced_guide.md
│   │   ├── Claude - mkdocs_rag_master_guide.md
│   │   ├── Claude - XNAI MASTER OPERATIONS & IMPLEMENTATIONS HANDBOOK (01-17-2026).md
│   │   ├── Griffe Backend Customization Guide.md
│   │   ├── Grok - Complete Guide to Generating High-Quality Videos in NotebookLM.md
│   │   ├── MKdocs Diataxis Versioning Guide + Mike RAG metadata.md
│   │   ├── MkDocs Guide Elevate Local RAG to Academic Performance.md
│   │   ├── MkDocs Mike Versioning.md
│   │   ├── MkDocStrings Plugin Tutorial.md
│   │   ├── NotebooLM - Xoe-NovAi Enterprise Platform Advanced Research & Implementation Briefing.md
│   │   ├── PRR-P1-WATERMARK-003 Educational Briefing AI Content Watermarking.md
│   │   ├── Report - Cutting-Edge MkDocs Configuration for Xoe-NovAi Documentation Resilience.md
│   │   ├── Ultimate MkDocs Master Guide Research Plan.md
│   │   ├── xoe_enterprise_remediation_guide.md
│   │   ├── Xoe-NovAi Comprehensive Implementation Quick-Start.md
│   │   ├── Xoe-NovAi .env File Review & Recommendations.md
│   │   ├── Xoe-NovAi Permissions Best Practices Guide.md
│   │   └── Xoe-NovAi Remediation & Implementation Main Guide.md
│   ├── incoming-integration-summary.md
│   ├── index.html
│   ├── index.json
│   ├── index.md
│   ├── journey
│   │   └── README.md
│   ├── mkdocs
│   │   ├── config
│   │   ├── scripts
│   │   ├── styles
│   │   └── templates
│   ├── operations
│   │   ├── monitoring-dashboard.md
│   │   └── troubleshooting.md
│   ├── personas
│   │   ├── lilith.json
│   │   └── odin.json
│   ├── policies
│   │   ├── DOCS_STRATEGY.md
│   │   ├── DOCUMENTATION_DRIFT_PREVENTION.md
│   │   ├── DOCUMENTATION_STRATEGY.md
│   │   ├── OWNERS.md
│   │   ├── PIP_INSTALL_STANDARDS.md
│   │   ├── POLICIES.md
│   │   ├── README.md
│   │   └── version-management-policy.md
│   ├── portability
│   │   ├── migration-partition-fixes-2026.md
│   │   ├── partition-migration-analysis.md
│   │   └── README.md
│   ├── powerful_mkdocs_system_focus.md
│   ├── projects
│   │   └── TORCH_FREE_CHAINLIT_MOD.md
│   ├── project-tracking
│   │   ├── ai-capabilities-overview.md
│   │   ├── build-system.md
│   │   ├── dependency-management.md
│   │   ├── infrastructure-architecture.md
│   │   ├── integration-guide.md
│   │   ├── operations-handbook.md
│   │   ├── performance-optimization.md
│   │   ├── phase1-foundation-security.md
│   │   ├── phase2-performance-resilience.md
│   │   ├── phase3-production-hardening.md
│   │   ├── phase4-documentation-consolidation.md
│   │   ├── PROJECT_STATUS_DASHBOARD.md
│   │   └── security-framework.md
│   ├── project-tracking-consolidation-resources
│   │   ├── analysis
│   │   ├── backups
│   │   ├── execution
│   │   ├── planning
│   │   ├── README.md
│   │   ├── templates
│   │   └── validation
│   ├── README.md
│   ├── reference
│   │   ├── api
│   │   ├── architecture.md
│   │   ├── blueprint.md
│   │   ├── CODE_REVIEW_2026_01_05.md
│   │   ├── condensed-guide.md
│   │   ├── configuration.md
│   │   ├── data-directories.md
│   │   ├── docker-services.md
│   │   ├── DR - Top 20 Resources for EmbGemma in XNAi.md
│   │   ├── EmbeddingGemma model card.md
│   │   ├── enterprise-features
│   │   ├── integration
│   │   ├── project-charter.md
│   │   ├── project-overview.md
│   │   ├── README.md
│   │   ├── stack-cat-guide.md
│   │   └── xnai_v0.1.5_voice_addendum.md
│   ├── releases
│   │   ├── changelog.md
│   │   ├── CHANGELOG.md
│   │   ├── delivery-complete.md
│   │   ├── documentation-changelog.md
│   │   ├── executive-audit.md
│   │   ├── executive-summary.md
│   │   ├── implementation-complete.md
│   │   ├── implementation-package-summary.md
│   │   ├── phase-2-completion.md
│   │   ├── pr-release-notes.md
│   │   ├── README.md
│   │   ├── v0.1.4-stable.md
│   │   ├── v0.1.4-stable-release-readiness-audit.md
│   │   ├── v0.1.5.md
│   │   ├── voice-implementation-summary.txt
│   │   └── voice-v0.2.0-summary.py
│   ├── requirements-docs.txt
│   ├── research
│   │   ├── CLAUDE_WEEK4_PRODUCTION_VALIDATION_PROMPT.md
│   │   ├── Grok_Clarification_Response.md
│   │   ├── Grok - Claude final implementations recommenfations.md
│   │   ├── GROK_FINAL_PRODUCTION_READINESS_REPORT_v1.0.md
│   │   ├── methodology
│   │   ├── POLISHING_RESEARCH_REQUESTS.md
│   │   ├── projects
│   │   ├── README.md
│   │   ├── research-integration-guide.md
│   │   ├── research-needs.md
│   │   ├── research-request-template.md
│   │   ├── RESEARCH_SYSTEM_SUMMARY.md
│   │   ├── research-tracking.md
│   │   └── urls
│   ├── research-validation-report.md
│   ├── runbooks
│   │   ├── build-logging.md
│   │   ├── build-tools.md
│   │   ├── code-updates-tracker.md
│   │   ├── docker-build-troubleshooting.md
│   │   ├── docker-testing.md
│   │   ├── ingestion-system-enhancements.md
│   │   ├── make-up-test-results.md
│   │   ├── README.md
│   │   ├── security-fixes-runbook.md
│   │   ├── updates-running.md
│   │   └── voice-deployment.md
│   ├── scripts
│   │   ├── catalog.json
│   │   ├── fix_mkdocs_nav.py
│   │   ├── freshness_monitor.py
│   │   ├── indexer.py
│   │   ├── migrate_content.py
│   │   ├── README.md
│   │   ├── research_request_system.py
│   │   ├── research_validator.py
│   │   └── validate_review_compliance.py
│   ├── search_index.json
│   ├── STACK_STATUS.md
│   ├── START_HERE.md
│   ├── stylesheets
│   ├── system-prompts
│   │   ├── assistants
│   │   ├── experts
│   │   ├── _meta
│   │   ├── metrics
│   │   └── README.md
│   ├── templates
│   │   ├── enhancement_tracking_template.md
│   │   ├── howto_template.md
│   │   ├── policy_template.md
│   │   ├── release_note_template.md
│   │   └── runbook_template.md
│   ├── TRACKING_DOCUMENTS_CONSOLIDATION_ANALYSIS.md
│   ├── tutorials
│   │   ├── docker-setup.md
│   │   ├── getting-started.md
│   │   ├── quick-start.md
│   │   └── voice-interface.md
│   ├── updated_mkdocs_research_request.md
│   ├── versions
│   │   └── version_strategy.md
│   ├── videos
│   │   ├── Claude - NotebookLM Masterclass.md
│   │   ├── claude-research-request-for-video-enhancement.md
│   │   ├── Grok - Complete Guide to Generating High-Quality Videos in NotebookLM.md
│   │   ├── Grok - Expanded Script Template (Anime Style – Inspirational Triumph).md
│   │   ├── Grok - Unique Use Cases Discovered.md
│   │   ├── Grok - video supplemental.md
│   │   ├── kj-xoe-novai-explanation-script.md
│   │   ├── README.md
│   │   ├── Research Report Enhanced NotebookLM Video Strategies (Jan 17, 2026).md
│   │   └── xoe-novai-notebooklm-context-package.md
│   ├── voice-debug-mode.md
│   ├── Xoe-NovAi AI Code Assistant System Prompt.md
│   ├── XOE_NOVAI_CHAINLIT_IMPLEMENTATIONS.md
│   └── xoe_novai_mkdocs_supplemental_details.md
├── expert-knowledge
│   ├── infrastructure
│   ├── origins
│   ├── protocols
│   ├── research
│   ├── security
│   └── sync
├── IMPLEMENTATION_COMPLETE_PIPER_ONNX.md
├── job.schema.json
├── LOCAL_TELEMETRY_FREE_TTS_OPTIONS_2025.md
├── logs
│   └── curations  [error opening dir]
├── Makefile
├── memory_bank
│   ├── activeContext
│   └── communications
├── _meta
│   └── locks
│       └── task-genesis-complete.yaml
├── PIPER_ONNX_IMPLEMENTATION_SUMMARY.md
├── __pycache__
│   ├── test_ingestion_demo.cpython-313-pytest-9.0.2.pyc
│   └── test_voice.cpython-313-pytest-9.0.2.pyc
├── redis_password.txt
├── requirements-api.txt
├── requirements-chainlit.txt
├── requirements-crawl.txt
├── requirements-curation_worker.txt
├── scripts
│   ├── build_tools
│   │   ├── build_visualizer.py
│   │   ├── dependency_db.json
│   │   ├── dependency_tracker.py
│   │   ├── enhanced_download_wheelhouse.py
│   │   ├── initial_dependency_report.md
│   │   ├── requirements.txt
│   │   └── scan_requirements.py
│   ├── clean_wheelhouse_duplicates.sh
│   ├── curation_worker.py
│   ├── download_wheelhouse.sh
│   ├── ingest_library.py
│   ├── prebuild_validate.py
│   ├── preflight_checks.py
│   ├── __pycache__
│   │   └── query_test.cpython-313-pytest-9.0.2.pyc
│   ├── query_test.py
│   ├── stack-cat
│   │   ├── groups.json
│   │   └── whitelist.json
│   └── validate_config.py
├── test_docker_integration.sh
├── test_ingestion_demo.py
├── tests
│   ├── conftest.py
│   ├── __pycache__
│   │   ├── conftest.cpython-313-pytest-9.0.2.pyc
│   │   ├── test_circuit_breaker_chaos.cpython-313-pytest-9.0.2.pyc
│   │   ├── test_crawl.cpython-313-pytest-9.0.2.pyc
│   │   ├── test_curation_worker.cpython-313-pytest-9.0.2.pyc
│   │   ├── test_healthcheck.cpython-313-pytest-9.0.2.pyc
│   │   ├── test_integration.cpython-313-pytest-9.0.2.pyc
│   │   ├── test_metrics.cpython-313-pytest-9.0.2.pyc
│   │   ├── test_truncation.cpython-313-pytest-9.0.2.pyc
│   │   └── test_voice.cpython-313-pytest-9.0.2.pyc
│   ├── test_circuit_breaker_chaos.py
│   ├── test_crawl.py
│   ├── test_curation_worker.py
│   ├── test_healthcheck.py
│   ├── test_integration.py
│   ├── test_metrics.py
│   ├── test_truncation.py
│   └── test_voice.py
├── test_voice.py
├── venv
├── versions
│   ├── scripts
│   │   ├── build_monitor.py
│   │   └── update_versions.py
│   ├── version_report.md
│   └── versions.toml
├── voice_interface.py
├── WHEELHOUSE_BUILD_TRACKING.md
└── xoe-novai-sync
    ├── ekb-exports
    ├── mc-imports
    └── _meta

124 directories, 622 files