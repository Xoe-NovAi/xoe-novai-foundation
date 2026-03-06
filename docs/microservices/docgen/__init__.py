"""
Documentation Generation Microservice

Automated content generation from code comments, templates, and AI assistance.
Integrates with existing MkDocs pipeline and provides enterprise-grade documentation
management capabilities.

Architecture:
- FastAPI service for REST endpoints
- Template-based generation with Jinja2
- AI-assisted content creation using local models
- Git integration for version control
- Quality validation pipeline

Usage:
    python -m docs.microservices.docgen.app

Environment Variables:
    DOCGEN_PORT: Service port (default: 8002)
    DOCGEN_MODEL_PATH: Path to local model for AI generation
    DOCGEN_TEMPLATE_DIR: Directory containing Jinja2 templates
    DOCGEN_GIT_REPO: Git repository path for version control
"""