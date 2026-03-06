"""
Pydantic models for Documentation Validation Service

Defines request/response schemas and data models for validation endpoints.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class ValidationRequest(BaseModel):
    """Request model for file validation."""
    
    file_path: str = Field(..., description="Path to file or directory to validate")
    include_accessibility: bool = Field(default=True, description="Whether to include accessibility validation")
    generate_report: bool = Field(default=False, description="Whether to generate detailed report")
    report_output_dir: Optional[str] = Field(None, description="Directory to save reports")
    content: Optional[str] = Field(None, description="Content to validate (for content validation)")
    
    @validator('file_path')
    def validate_file_path(cls, v):
        if not v:
            raise ValueError('File path cannot be empty')
        return v


class ValidationResult(BaseModel):
    """Combined validation result for a file."""
    
    file_path: str = Field(..., description="Path to validated file")
    passed: bool = Field(..., description="Whether all validations passed")
    validation: Optional['ContentValidationResult'] = Field(None, description="Content validation result")
    format: Optional['FormatValidationResult'] = Field(None, description="Format validation result")
    accessibility: Optional['AccessibilityValidationResult'] = Field(None, description="Accessibility validation result")
    compliance: Optional['ComplianceValidationResult'] = Field(None, description="Compliance validation result")
    quality: Optional['QualityReport'] = Field(None, description="Quality analysis report")
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall quality score")
    timestamp: datetime = Field(default_factory=datetime.now, description="Validation timestamp")


class ContentValidationResult(BaseModel):
    """Result of content validation."""
    
    success: bool = Field(..., description="Whether content validation passed")
    errors: List[str] = Field(default_factory=list, description="Content validation errors")
    warnings: List[str] = Field(default_factory=list, description="Content validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Content improvement suggestions")
    content: Optional[str] = Field(None, description="File content (for further analysis)")


class FormatValidationResult(BaseModel):
    """Result of format validation."""
    
    success: bool = Field(..., description="Whether format validation passed")
    errors: List[str] = Field(default_factory=list, description="Format validation errors")
    warnings: List[str] = Field(default_factory=list, description="Format validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Format improvement suggestions")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="Detailed format issues")


class AccessibilityValidationResult(BaseModel):
    """Result of accessibility validation."""
    
    success: bool = Field(..., description="Whether accessibility validation passed")
    errors: List[str] = Field(default_factory=list, description="Accessibility validation errors")
    warnings: List[str] = Field(default_factory=list, description="Accessibility validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Accessibility improvement suggestions")
    wcag_compliance: Dict[str, Any] = Field(default_factory=dict, description="WCAG compliance details")
    score: float = Field(..., ge=0.0, le=100.0, description="Accessibility score")


class ComplianceValidationResult(BaseModel):
    """Result of compliance validation."""
    
    success: bool = Field(..., description="Whether compliance validation passed")
    errors: List[str] = Field(default_factory=list, description="Compliance validation errors")
    warnings: List[str] = Field(default_factory=list, description="Compliance validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Compliance improvement suggestions")
    compliance_standards: List[str] = Field(default_factory=list, description="Compliance standards checked")
    violations: List[Dict[str, Any]] = Field(default_factory=list, description="Compliance violations")


class QualityReport(BaseModel):
    """Quality analysis report for documentation."""
    
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall quality score")
    readability_score: float = Field(..., ge=0.0, le=100.0, description="Readability score")
    technical_accuracy: float = Field(..., ge=0.0, le=100.0, description="Technical accuracy score")
    completeness: float = Field(..., ge=0.0, le=100.0, description="Content completeness score")
    clarity: float = Field(..., ge=0.0, le=100.0, description="Content clarity score")
    
    strengths: List[str] = Field(default_factory=list, description="Content strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Content weaknesses")
    suggestions: List[str] = Field(default_factory=list, description="Quality improvement suggestions")
    
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Detailed quality metrics")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="Quality issues found")


class AccessibilityReport(BaseModel):
    """Detailed accessibility compliance report."""
    
    wcag_level: str = Field(..., description="WCAG compliance level (A, AA, AAA)")
    color_contrast_score: float = Field(..., ge=0.0, le=100.0, description="Color contrast compliance score")
    alt_text_compliance: float = Field(..., ge=0.0, le=100.0, description="Alternative text compliance score")
    heading_structure_score: float = Field(..., ge=0.0, le=100.0, description="Heading structure compliance score")
    link_compliance: float = Field(..., ge=0.0, le=100.0, description="Link accessibility compliance score")
    
    violations: List[Dict[str, Any]] = Field(default_factory=list, description="Accessibility violations")
    recommendations: List[str] = Field(default_factory=list, description="Accessibility recommendations")
    manual_review_needed: bool = Field(default=False, description="Whether manual review is needed")


class ComplianceReport(BaseModel):
    """Detailed compliance validation report."""
    
    standards_checked: List[str] = Field(default_factory=list, description="Compliance standards checked")
    violations: List[Dict[str, Any]] = Field(default_factory=list, description="Compliance violations")
    recommendations: List[str] = Field(default_factory=list, description="Compliance recommendations")
    risk_level: str = Field(..., description="Overall compliance risk level")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last compliance check timestamp")


class ValidationMetrics(BaseModel):
    """Metrics for validation service performance."""
    
    total_validations: int = Field(..., description="Total number of validations performed")
    success_rate: float = Field(..., ge=0.0, le=100.0, description="Validation success rate")
    average_score: float = Field(..., ge=0.0, le=100.0, description="Average validation score")
    validation_times: Dict[str, float] = Field(default_factory=dict, description="Validation timing metrics")
    error_breakdown: Dict[str, int] = Field(default_factory=dict, description="Error type breakdown")


class BatchValidationResult(BaseModel):
    """Result of batch validation operation."""
    
    total_files: int = Field(..., description="Total number of files validated")
    passed_files: int = Field(..., description="Number of files that passed validation")
    failed_files: int = Field(..., description="Number of files that failed validation")
    average_score: float = Field(..., ge=0.0, le=100.0, description="Average validation score")
    results: List[ValidationResult] = Field(default_factory=list, description="Individual validation results")
    summary_report: Optional[str] = Field(None, description="Path to summary report file")


class ReportTemplate(BaseModel):
    """Template for generating validation reports."""
    
    name: str = Field(..., description="Report template name")
    format: str = Field(..., description="Report format (html, pdf, json, markdown)")
    sections: List[str] = Field(default_factory=list, description="Report sections to include")
    styling: Dict[str, Any] = Field(default_factory=dict, description="Report styling options")
    include_details: bool = Field(default=True, description="Whether to include detailed analysis")


class ValidationRule(BaseModel):
    """Individual validation rule."""
    
    rule_id: str = Field(..., description="Unique rule identifier")
    rule_name: str = Field(..., description="Human-readable rule name")
    rule_description: str = Field(..., description="Detailed rule description")
    severity: str = Field(..., description="Rule severity (error, warning, info)")
    category: str = Field(..., description="Rule category (formatting, content, accessibility)")
    enabled: bool = Field(default=True, description="Whether rule is enabled")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Rule-specific parameters")


class StyleGuide(BaseModel):
    """Documentation style guide configuration."""
    
    name: str = Field(..., description="Style guide name")
    version: str = Field(..., description="Style guide version")
    rules: List[ValidationRule] = Field(default_factory=list, description="Style guide rules")
    exceptions: List[str] = Field(default_factory=list, description="Files/directories to exclude")
    auto_fix: bool = Field(default=False, description="Whether to auto-fix issues when possible")