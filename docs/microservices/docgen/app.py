"""
Documentation Generation Service

FastAPI application for automated documentation generation with AI assistance.
Provides endpoints for template-based content generation, code comment extraction,
and AI-assisted documentation creation.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import jinja2
import git
import uvicorn

from .models import (
    TemplateGenerationRequest, 
    CodeExtractionRequest, 
    AIGenerationRequest,
    GenerationResponse,
    TemplateMetadata
)
from .template_engine import TemplateEngine
from .code_extractor import CodeExtractor
from .ai_generator import AIGenerator
from .git_integration import GitIntegration
from .validators import ContentValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
DOCGEN_PORT = int(os.getenv("DOCGEN_PORT", "8002"))
DOCGEN_TEMPLATE_DIR = os.getenv("DOCGEN_TEMPLATE_DIR", "docs/templates")
DOCGEN_GIT_REPO = os.getenv("DOCGEN_GIT_REPO", ".")
DOCGEN_MODEL_PATH = os.getenv("DOCGEN_MODEL_PATH", "/models/Qwen3-0.6B-Q6_K.gguf")

app = FastAPI(
    title="Documentation Generation Service",
    description="Enterprise-grade automated documentation generation with AI assistance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
template_engine = TemplateEngine(DOCGEN_TEMPLATE_DIR)
code_extractor = CodeExtractor()
ai_generator = AIGenerator(DOCGEN_MODEL_PATH)
git_integration = GitIntegration(DOCGEN_GIT_REPO)
content_validator = ContentValidator()

@app.on_event("startup")
async def startup_event():
    """Initialize service components on startup."""
    logger.info("Starting Documentation Generation Service...")
    
    # Ensure template directory exists
    Path(DOCGEN_TEMPLATE_DIR).mkdir(parents=True, exist_ok=True)
    
    # Initialize AI model if path provided
    if DOCGEN_MODEL_PATH and Path(DOCGEN_MODEL_PATH).exists():
        await ai_generator.initialize()
        logger.info(f"AI Generator initialized with model: {DOCGEN_MODEL_PATH}")
    else:
        logger.warning("No AI model path provided or model not found")
    
    logger.info("Documentation Generation Service ready")

@app.post("/generate/template", response_model=GenerationResponse)
async def generate_from_template(
    request: TemplateGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate documentation from a Jinja2 template.
    
    Supports dynamic content generation with context variables and includes.
    """
    try:
        logger.info(f"Generating documentation from template: {request.template_name}")
        
        # Generate content using template engine
        result = await template_engine.generate(
            template_name=request.template_name,
            context=request.context,
            output_path=request.output_path
        )
        
        # Validate generated content
        validation_result = content_validator.validate_file(result.output_path)
        
        # Add to git if requested
        if request.git_commit:
            background_tasks.add_task(
                git_integration.commit_changes,
                file_paths=[result.output_path],
                commit_message=f"Auto-generate: {request.template_name}"
            )
        
        return GenerationResponse(
            success=True,
            message="Template generation completed successfully",
            output_path=result.output_path,
            validation=validation_result
        )
        
    except Exception as e:
        logger.error(f"Template generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/code", response_model=GenerationResponse)
async def extract_from_code(
    request: CodeExtractionRequest,
    background_tasks: BackgroundTasks
):
    """
    Extract documentation from code comments and docstrings.
    
    Supports Python, JavaScript, TypeScript, and other major languages.
    """
    try:
        logger.info(f"Extracting documentation from: {request.source_path}")
        
        # Extract documentation from code
        result = await code_extractor.extract(
            source_path=request.source_path,
            output_path=request.output_path,
            language=request.language
        )
        
        # Validate generated content
        validation_result = content_validator.validate_file(result.output_path)
        
        # Add to git if requested
        if request.git_commit:
            background_tasks.add_task(
                git_integration.commit_changes,
                file_paths=[result.output_path],
                commit_message=f"Extract docs from: {request.source_path}"
            )
        
        return GenerationResponse(
            success=True,
            message="Code extraction completed successfully",
            output_path=result.output_path,
            validation=validation_result
        )
        
    except Exception as e:
        logger.error(f"Code extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/ai", response_model=GenerationResponse)
async def generate_with_ai(
    request: AIGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate documentation using AI assistance.
    
    Leverages local models for content generation with context awareness.
    """
    try:
        logger.info(f"Generating AI-assisted documentation for: {request.topic}")
        
        # Check if AI generator is available
        if not ai_generator.is_initialized():
            raise HTTPException(
                status_code=503, 
                detail="AI generator not initialized. Please provide a valid model path."
            )
        
        # Generate content using AI
        result = await ai_generator.generate(
            topic=request.topic,
            context=request.context,
            output_path=request.output_path,
            max_tokens=request.max_tokens
        )
        
        # Validate generated content
        validation_result = content_validator.validate_file(result.output_path)
        
        # Add to git if requested
        if request.git_commit:
            background_tasks.add_task(
                git_integration.commit_changes,
                file_paths=[result.output_path],
                commit_message=f"AI-generated docs: {request.topic}"
            )
        
        return GenerationResponse(
            success=True,
            message="AI generation completed successfully",
            output_path=result.output_path,
            validation=validation_result
        )
        
    except Exception as e:
        logger.error(f"AI generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/templates", response_model=List[TemplateMetadata])
async def list_templates():
    """List available documentation templates."""
    try:
        templates = template_engine.list_templates()
        return templates
    except Exception as e:
        logger.error(f"Failed to list templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Service health check endpoint."""
    return {
        "status": "healthy",
        "service": "docgen",
        "version": "1.0.0",
        "ai_initialized": ai_generator.is_initialized(),
        "template_dir": DOCGEN_TEMPLATE_DIR,
        "git_repo": DOCGEN_GIT_REPO
    }

if __name__ == "__main__":
    uvicorn.run(
        "docs.microservices.docgen.app:app",
        host="0.0.0.0",
        port=DOCGEN_PORT,
        reload=True,
        log_level="info"
    )