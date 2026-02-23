# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- VERSION HISTORY -->

## [0.2.0] - 2026-02-22

### Added
- **Infrastructure Layer**: SessionManager with Redis + in-memory fallback
- **Infrastructure Layer**: KnowledgeClient with Qdrant + FAISS abstraction
- **Voice Module**: VoiceModule adapter for Chainlit integration
- **Knowledge Distillation**: LangGraph StateGraph pipeline for knowledge absorption
- **Knowledge Distillation**: Quality scoring with 5 factors (Relevance, Novelty, Actionability, Completeness, Accuracy)
- **Automation**: Ruff linter replacing flake8 + isort + black
- **Automation**: MyPy type checking in CI
- **Automation**: Dependabot for dependency updates
- **Automation**: PR automation (labeler, CODEOWNERS, size checker)
- **Automation**: EditorConfig for IDE consistency
- **Automation**: Semantic versioning with python-semantic-release
- **Documentation**: Infrastructure layer API reference
- **Documentation**: Voice module API reference
- **Documentation**: Voice interface documentation
- **Documentation**: Chainlit migration guide
- **Documentation**: Feature flags reference
- **Documentation**: Shared CLI configuration
- **Gemini CLI**: MC agent session templates
- **Gemini CLI**: Operational commands (status, dispatch, handoff, audit, torch-free)

### Changed
- **Chainlit**: Consolidated 2 apps into 1 unified app (65% code reduction)
- **Chainlit**: Replaced `chainlit_app.py` (721 lines) and `chainlit_app_voice.py` (964 lines) with `chainlit_app_unified.py` (580 lines)
- **START-HERE.md**: Updated with current state and coordination key
- **Automation Maturity**: Improved from 6.7/10 to 8.5/10

### Fixed
- Root shim import pointing to unified Chainlit app

## [0.1.0] - 2026-02-15

### Added
- Initial project structure
- Basic RAG functionality
- Voice interface prototype
- Agent Bus integration
- Redis state management
- Qdrant vector storage
- Consul service discovery

---

[0.2.0]: https://github.com/arcana-novai/xnai-foundation/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/arcana-novai/xnai-foundation/releases/tag/v0.1.0
