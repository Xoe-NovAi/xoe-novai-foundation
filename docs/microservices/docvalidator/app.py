"""
Documentation Validation Service

FastAPI application for comprehensive content quality validation.
Provides multi-layered validation including formatting, accessibility,
content quality, and compliance checking.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from .models import (
    ValidationRequest, 
    ValidationResult,
    QualityReport,
    AccessibilityReport,
    ComplianceReport
)
from .validators import (
    ContentValidator,
    FormatValidator, 
    AccessibilityValidator,
    ComplianceValidator
)
from .quality_checker import QualityChecker
from .report_generator import ReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
DOCVALIDATOR_PORT = int(os.getenv("DOCVALIDATOR_PORT", "8003"))
DOCVALIDATOR_STRICT_MODE = os.getenv("DOCVALIDATOR_STRICT_MODE", "false").lower() == "true"
DOCVALIDATOR_ACCESSIBILITY_CHECKS = os.getenv("DOCVALIDATOR_ACCESSIBILITY_CHECKS", "true").lower() == "true"

app = FastAPI(
    title="Documentation Validation Service",
    description="Enterprise-grade content quality validation with accessibility and compliance checking",
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

# Initialize validators
content_validator = ContentValidator()
format_validator = FormatValidator()
accessibility_validator = AccessibilityValidator() if DOCVALIDATOR_ACCESSIBILITY_CHECKS else None
compliance_validator = ComplianceValidator()
quality_checker = QualityChecker()
report_generator = ReportGenerator()

@app.on_event("startup")
async def startup_event():
    """Initialize service components on startup."""
    logger.info("Starting Documentation Validation Service...")
    
    # Load validation rules and style guides
    await content_validator.initialize()
    await format_validator.initialize()
    
    if accessibility_validator:
        await accessibility_validator.initialize()
    
    await compliance_validator.initialize()
    
    logger.info("Documentation Validation Service ready")

@app.post("/validate/file", response_model=ValidationResult)
async def validate_file(
    request: ValidationRequest,
    background_tasks: BackgroundTasks
):
    """
    Validate a single documentation file.
    
    Performs comprehensive validation including content quality, formatting,
    accessibility, and compliance checks.
    """
    try:
        logger.info(f"Validating file: {request.file_path}")
        
        # Perform validation pipeline
        validation_result = await content_validator.validate_file(request.file_path)
        format_result = await format_validator.validate_file(request.file_path)
        
        accessibility_result = None
        if accessibility_validator and request.include_accessibility:
            accessibility_result = await accessibility_validator.validate_file(request.file_path)
        
        compliance_result = await compliance_validator.validate_file(request.file_path)
        
        # Generate quality report
        quality_report = await quality_checker.analyze_file(
            file_path=request.file_path,
            content=validation_result.content if validation_result.success else None
        )
        
        # Combine results
        combined_result = ValidationResult(
            file_path=request.file_path,
            passed=all([
                validation_result.success,
                format_result.success,
                accessibility_result.success if accessibility_result else True,
                compliance_result.success
            ]),
            validation=validation_result,
            format=format_result,
            accessibility=accessibility_result,
            compliance=compliance_result,
            quality=quality_report,
            overall_score=quality_report.overall_score if quality_report else 0.0
        )
        
        # Generate detailed report if requested
        if request.generate_report:
            background_tasks.add_task(
                report_generator.generate_detailed_report,
                combined_result,
                output_dir=request.report_output_dir
            )
        
        return combined_result
        
    except Exception as e:
        logger.error(f"File validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate/batch", response_model=List[ValidationResult])
async def validate_batch(
    request: ValidationRequest,
    background_tasks: BackgroundTasks
):
    """
    Validate multiple documentation files.
    
    Processes a batch of files and returns validation results for each.
    """
    try:
        logger.info(f"Validating batch: {request.file_path}")
        
        # Get all files in directory
        file_path = Path(request.file_path)
        if file_path.is_dir():
            files = list(file_path.rglob("*.md"))
        else:
            files = [file_path]
        
        results = []
        for file in files:
            single_request = ValidationRequest(
                file_path=str(file),
                include_accessibility=request.include_accessibility,
                generate_report=False,  # Don't generate individual reports for batch
                report_output_dir=request.report_output_dir
            )
            
            result = await validate_file(single_request, background_tasks)
            results.append(result)
        
        # Generate batch summary report
        if request.generate_report and results:
            background_tasks.add_task(
                report_generator.generate_batch_report,
                results,
                output_dir=request.report_output_dir
            )
        
        return results
        
    except Exception as e:
        logger.error(f"Batch validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate/content", response_model=ValidationResult)
async def validate_content(
    request: ValidationRequest,
    background_tasks: BackgroundTasks
):
    """
    Validate content directly without file I/O.
    
    Useful for validating generated content before writing to file.
    """
    try:
        logger.info("Validating content")
        
        # Perform validation pipeline on content
        validation_result = await content_validator.validate_content(request.content or "")
        format_result = await format_validator.validate_content(request.content or "")
        
        accessibility_result = None
        if accessibility_validator and request.include_accessibility:
            accessibility_result = await accessibility_validator.validate_content(request.content or "")
        
        compliance_result = await compliance_validator.validate_content(request.content or "")
        
        # Generate quality report
        quality_report = await quality_checker.analyze_content(request.content or "")
        
        # Combine results
        combined_result = ValidationResult(
            file_path="content",
            passed=all([
                validation_result.success,
                format_result.success,
                accessibility_result.success if accessibility_result else True,
                compliance_result.success
            ]),
            validation=validation_result,
            format=format_result,
            accessibility=accessibility_result,
            compliance=compliance_result,
            quality=quality_report,
            overall_score=quality_report.overall_score if quality_report else 0.0
        )
        
        return combined_result
        
    except Exception as e:
        logger.error(f"Content validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quality/report/{file_path:path}")
async def get_quality_report(file_path: str):
    """
    Get detailed quality report for a file.
    
    Returns comprehensive analysis including suggestions for improvement.
    """
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Generate detailed report
        report = await report_generator.generate_detailed_report(
            file_path=str(file_path_obj),
            output_dir=None
        )
        
        return report
        
    except Exception as e:
        logger.error(f"Quality report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Service health check endpoint."""
    return {
        "status": "healthy",
        "service": "docvalidator",
        "version": "1.0.0",
        "strict_mode": DOCVALIDATOR_STRICT_MODE,
        "accessibility_checks": DOCVALIDATOR_ACCESSIBILITY_CHECKS,
        "validators_initialized": {
            "content": content_validator.is_initialized(),
            "format": format_validator.is_initialized(),
            "accessibility": accessibility_validator.is_initialized() if accessibility_validator else False,
            "compliance": compliance_validator.is_initialized()
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "docs.microservices.docvalidator.app:app",
        host="0.0.0.0",
        port=DOCVALIDATOR_PORT,
        reload=True,
        log_level="info"
    )