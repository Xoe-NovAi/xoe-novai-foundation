"""
Model Card Schema for XNAi Knowledge Base

Pydantic v2 schema for structured model metadata including specifications,
benchmarks, ecosystem compatibility, and research status.
"""

from datetime import datetime
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class SpecsModel(BaseModel):
    """Model specifications (parameters, context, quantization, performance)"""
    parameters: str = Field(..., description="Model size (e.g., '6.7B', '13B')")
    context_window: int = Field(..., description="Context window size in tokens")
    quantizations: List[str] = Field(
        default=["q4_k_m"],
        description="Available quantization formats"
    )
    inference_speed_ryzen7: str = Field(
        ...,
        description="Inference speed on Ryzen 7 5700U (e.g., '1.2 tok/s')"
    )
    memory_required: str = Field(
        ...,
        description="Memory required for primary quantization (e.g., '4.5 GB')"
    )
    vram_optional: Optional[str] = Field(
        default=None,
        description="Optional VRAM acceleration memory"
    )


class BenchmarkModel(BaseModel):
    """Benchmark result with metadata"""
    score: float = Field(..., description="Benchmark score/metric value")
    source: str = Field(..., description="Source of benchmark (HuggingFace, Papers, etc.)")
    source_url: Optional[str] = Field(default=None, description="URL to source")
    date: Optional[str] = Field(default=None, description="Date of benchmark")


class EcosystemModel(BaseModel):
    """Ecosystem compatibility and integration information"""
    frameworks: List[str] = Field(
        ...,
        description="Supported frameworks (ollama, vLLM, llama.cpp, etc.)"
    )
    verified_integrations: List[str] = Field(
        default=[],
        description="Verified integrations with XNAi stack (xnai_crawl, chainlit, langchain)"
    )
    dependencies: List[str] = Field(
        default=[],
        description="Required dependencies (transformers==4.x, peft==0.x, etc.)"
    )


class CompetitiveAnalysisModel(BaseModel):
    """Competitive analysis vs. alternative models"""
    strengths: List[str] = Field(
        ...,
        description="Key strengths of this model"
    )
    weaknesses: List[str] = Field(
        ...,
        description="Known weaknesses or limitations"
    )
    alternatives: List[str] = Field(
        default=[],
        description="Alternative models to consider (with brief comparison)"
    )


class MetadataModel(BaseModel):
    """Model card metadata and provenance"""
    created_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date when model card was created"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date when model card was last updated"
    )
    researcher_notes: Optional[str] = Field(
        default=None,
        description="Notes from researcher conducting the review"
    )
    source_links: List[str] = Field(
        default=[],
        description="Links to model sources (HuggingFace, GitHub, Papers, etc.)"
    )


class VectorMetadataModel(BaseModel):
    """Vector embedding metadata"""
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model used for vector representation"
    )
    vector_index_location: str = Field(
        default="knowledge/vectors/model_cards.faiss",
        description="Path to FAISS vector index file"
    )
    embedding_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When vectors were last updated"
    )


class ModelCardSchema(BaseModel):
    """
    Complete Model Card schema for XNAi Foundation knowledge base
    
    Example:
    ```python
    card = ModelCardSchema(
        model_id="deepseek-coder-6.7b",
        task_category="code_generation",
        specs=SpecsModel(...),
        ...
    )
    ```
    """
    
    model_id: str = Field(
        ...,
        description="Unique model identifier (e.g., 'deepseek-coder-6.7b')"
    )
    
    task_category: Literal[
        "code_generation",
        "research_synthesis",
        "data_curation",
        "other"
    ] = Field(
        ...,
        description="Primary task category for this model"
    )
    
    specs: SpecsModel = Field(
        ...,
        description="Model specifications"
    )
    
    benchmarks: Dict[str, BenchmarkModel] = Field(
        default={},
        description="Benchmark results with sources"
    )
    
    ecosystem: EcosystemModel = Field(
        ...,
        description="Ecosystem compatibility information"
    )
    
    competitive_analysis: CompetitiveAnalysisModel = Field(
        ...,
        description="Competitive analysis vs. alternatives"
    )
    
    research_status: Literal[
        "verified",
        "pending_verification",
        "deprecated"
    ] = Field(
        default="verified",
        description="Research status of this model card"
    )
    
    vectors: VectorMetadataModel = Field(
        default_factory=VectorMetadataModel,
        description="Vector embedding metadata"
    )
    
    metadata: MetadataModel = Field(
        default_factory=MetadataModel,
        description="Card metadata and provenance"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "model_id": "deepseek-coder-6.7b",
                "task_category": "code_generation",
                "specs": {
                    "parameters": "6.7B",
                    "context_window": 4096,
                    "quantizations": ["q4_k_m", "q5_k_m"],
                    "inference_speed_ryzen7": "1.2 tok/s",
                    "memory_required": "4.5 GB",
                    "vram_optional": "2 GB"
                },
                "benchmarks": {
                    "humaneval": {
                        "score": 73.2,
                        "source": "BigCode Leaderboard",
                        "source_url": "https://huggingface.co/spaces/bigcode/bigcode-models-leaderboard"
                    }
                },
                "ecosystem": {
                    "frameworks": ["ollama", "vLLM", "llama.cpp"],
                    "verified_integrations": ["xnai_crawl"],
                    "dependencies": ["transformers==4.37"]
                },
                "competitive_analysis": {
                    "strengths": ["Best code benchmark for 6B"],
                    "weaknesses": ["Memory footprint on tight budgets"],
                    "alternatives": ["Mistral 7B"]
                },
                "research_status": "verified"
            }
        }
    
    def to_dict_for_vectorization(self) -> Dict:
        """Extract text content for vectorization"""
        text_parts = [
            f"Model: {self.model_id}",
            f"Category: {self.task_category}",
            f"Description: {self.specs.parameters} parameters",
            f"Strengths: {', '.join(self.competitive_analysis.strengths)}",
            f"Weaknesses: {', '.join(self.competitive_analysis.weaknesses)}",
            f"Frameworks: {', '.join(self.ecosystem.frameworks)}",
            f"Research notes: {self.metadata.researcher_notes or 'None provided'}",
        ]
        return {"content": " | ".join(text_parts)}
