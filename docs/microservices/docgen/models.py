"""
Pydantic models for Documentation Generation Service

Defines request/response schemas and data models for all API endpoints.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class TemplateGenerationRequest(BaseModel):
    """Request model for template-based documentation generation."""
    
    template_name: str = Field(..., description="Name of the Jinja2 template to use")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context variables for template rendering")
    output_path: str = Field(..., description="Output file path for generated documentation")
    git_commit: bool = Field(default=False, description="Whether to commit changes to git")
    
    @validator('template_name')
    def validate_template_name(cls, v):
        if not v.endswith(('.md', '.html', '.rst')):
            raise ValueError('Template name must have a valid extension (.md, .html, .rst)')
        return v
    
    @validator('output_path')
    def validate_output_path(cls, v):
        if not v.startswith(('docs/', 'documentation/')):
            raise ValueError('Output path must be in docs/ or documentation/ directory')
        return v


class CodeExtractionRequest(BaseModel):
    """Request model for code comment extraction."""
    
    source_path: str = Field(..., description="Path to source code file or directory")
    output_path: str = Field(..., description="Output file path for extracted documentation")
    language: Optional[str] = Field(None, description="Programming language (auto-detected if not provided)")
    include_private: bool = Field(default=False, description="Whether to include private methods/functions")
    git_commit: bool = Field(default=False, description="Whether to commit changes to git")
    
    @validator('source_path')
    def validate_source_path(cls, v):
        if not any(v.endswith(ext) for ext in ['.py', '.js', '.ts', '.java', '.go', '.rust', '.c', '.cpp']):
            raise ValueError('Source path must point to a valid source code file or directory')
        return v


class AIGenerationRequest(BaseModel):
    """Request model for AI-assisted documentation generation."""
    
    topic: str = Field(..., description="Topic or subject for documentation generation")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for AI generation")
    output_path: str = Field(..., description="Output file path for generated documentation")
    max_tokens: int = Field(default=2000, ge=100, le=8000, description="Maximum tokens for AI generation")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="AI generation temperature")
    git_commit: bool = Field(default=False, description="Whether to commit changes to git")
    
    @validator('topic')
    def validate_topic(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Topic must be at least 3 characters long')
        return v.strip()


class GenerationResponse(BaseModel):
    """Response model for all generation endpoints."""
    
    success: bool = Field(..., description="Whether the generation was successful")
    message: str = Field(..., description="Detailed message about the operation")
    output_path: str = Field(..., description="Path to the generated documentation file")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation results for the generated content")
    processing_time: Optional[float] = Field(None, description="Time taken for generation in seconds")
    ai_model_used: Optional[str] = Field(None, description="AI model used for generation")


class TemplateMetadata(BaseModel):
    """Metadata for available templates."""
    
    name: str = Field(..., description="Template name")
    path: str = Field(..., description="Template file path")
    description: Optional[str] = Field(None, description="Template description")
    category: str = Field(..., description="Template category (tutorial, api, howto, etc.)")
    created_at: datetime = Field(..., description="Template creation timestamp")
    updated_at: datetime = Field(..., description="Template last update timestamp")
    variables: List[str] = Field(default_factory=list, description="Required template variables")


class ValidationResult(BaseModel):
    """Validation result for generated content."""
    
    passed: bool = Field(..., description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")
    score: float = Field(..., ge=0.0, le=100.0, description="Quality score (0-100)")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")


class GitCommitResult(BaseModel):
    """Result of git commit operation."""
    
    success: bool = Field(..., description="Whether the commit was successful")
    commit_hash: Optional[str] = Field(None, description="Commit hash if successful")
    message: str = Field(..., description="Commit message")
    files_changed: List[str] = Field(default_factory=list, description="List of changed files")


class ServiceHealth(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status (healthy, degraded, unhealthy)")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    ai_initialized: bool = Field(..., description="Whether AI generator is initialized")
    template_dir: str = Field(..., description="Template directory path")
    git_repo: str = Field(..., description="Git repository path")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")
    memory_usage: Optional[Dict[str, Any]] = Field(None, description="Memory usage statistics")


class DocumentationMetrics(BaseModel):
    """Metrics for documentation quality and usage."""
    
    total_documents: int = Field(..., description="Total number of documentation files")
    generated_today: int = Field(..., description="Number of documents generated today")
    validation_pass_rate: float = Field(..., ge=0.0, le=100.0, description="Validation pass rate percentage")
    average_quality_score: float = Field(..., ge=0.0, le=100.0, description="Average quality score")
    ai_usage_count: int = Field(..., description="Number of AI-assisted generations")
    template_usage: Dict[str, int] = Field(default_factory=dict, description="Template usage statistics")
    last_updated: datetime = Field(..., description="Last metrics update timestamp")