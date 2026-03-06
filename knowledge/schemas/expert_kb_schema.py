"""
Expert Knowledge Base Schema for XNAi Agent Bus

Pydantic v2 schema for agent-specific knowledge bases including documents,
tool registries, and vector index metadata.
"""

from datetime import datetime
from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field


class DocumentMetadataModel(BaseModel):
    """Metadata for KB documents"""
    document_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    document_type: Literal[
        "sop",
        "example",
        "system_instruction",
        "reference",
        "decision_log",
        "runbook"
    ] = Field(..., description="Type of document")
    version: str = Field(default="1.0", description="Document version")
    created_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Document creation date"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update date"
    )
    author: Optional[str] = Field(default=None, description="Document author")
    tags: List[str] = Field(default=[], description="Searchable tags/categories")


class DocumentModel(BaseModel):
    """Individual KB document with content and metadata"""
    metadata: DocumentMetadataModel = Field(..., description="Document metadata")
    content: str = Field(..., description="Full document content")
    cross_references: List[str] = Field(
        default=[],
        description="Links to related documents in other agent KBs"
    )


class ToolRegistryModel(BaseModel):
    """Tool/integration available to the agent"""
    tool_name: str = Field(..., description="Tool name (e.g., 'Consul', 'Redis')")
    tool_type: Literal[
        "service_discovery",
        "state_management",
        "vector_search",
        "task_queue",
        "monitoring",
        "other"
    ] = Field(..., description="Type of tool")
    integration_pattern: str = Field(
        ...,
        description="How to integrate this tool (code pattern or reference)"
    )
    documentation_link: Optional[str] = Field(
        default=None,
        description="Link to tool documentation"
    )


class VectorIndexModel(BaseModel):
    """Vector index configuration and metadata"""
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model used"
    )
    vector_dimension: int = Field(default=384, description="Vector dimension size")
    index_type: Literal["flat", "hnsw", "ivf"] = Field(
        default="flat",
        description="FAISS index type"
    )
    index_path: str = Field(
        ...,
        description="Path to vector index file"
    )
    document_count: int = Field(
        default=0,
        description="Number of documents indexed"
    )
    search_latency_sla_ms: int = Field(
        default=500,
        description="Target search latency in milliseconds"
    )
    last_indexed: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last time vectors were indexed"
    )


class AgentKBMetadataModel(BaseModel):
    """Metadata about the knowledge base itself"""
    agent_name: str = Field(
        ...,
        description="Agent name (copilot, gemini, cline, crawler)"
    )
    kb_version: str = Field(default="1.0", description="KB version")
    created_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="KB creation date"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update date"
    )
    total_documents: int = Field(default=0, description="Total documents in KB")
    kb_size_mb: float = Field(default=0.0, description="Total KB size in MB")
    description: str = Field(
        ...,
        description="Description of what this KB covers"
    )


class ExpertKBSchema(BaseModel):
    """
    Complete Expert Knowledge Base schema for agent-specific knowledge storage
    
    Example:
    ```python
    kb = ExpertKBSchema(
        metadata=AgentKBMetadataModel(...),
        documents=[DocumentModel(...), ...],
        tools=[ToolRegistryModel(...), ...],
        vectors=VectorIndexModel(...),
    )
    ```
    """
    
    metadata: AgentKBMetadataModel = Field(
        ...,
        description="KB metadata and provenance"
    )
    
    documents: List[DocumentModel] = Field(
        default=[],
        description="Collection of KB documents"
    )
    
    tools: List[ToolRegistryModel] = Field(
        default=[],
        description="Tool registry for this agent"
    )
    
    vectors: VectorIndexModel = Field(
        ...,
        description="Vector index configuration"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "metadata": {
                    "agent_name": "copilot",
                    "kb_version": "1.0",
                    "description": "Knowledge base for Copilot CLI (Haiku 4.5)"
                },
                "documents": [
                    {
                        "metadata": {
                            "document_id": "copilot-system-instructions-001",
                            "title": "Copilot Haiku 4.5 System Instructions",
                            "document_type": "system_instruction"
                        },
                        "content": "You are Copilot CLI with Haiku 4.5 model..."
                    }
                ],
                "tools": [
                    {
                        "tool_name": "Consul",
                        "tool_type": "service_discovery",
                        "integration_pattern": "from consul import Consul..."
                    }
                ],
                "vectors": {
                    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                    "index_path": "expert-knowledge/copilot/vectors.index"
                }
            }
        }
    
    def add_document(self, doc: DocumentModel) -> None:
        """Add a document to the KB and increment count"""
        self.documents.append(doc)
        self.metadata.total_documents = len(self.documents)
        self.metadata.last_updated = datetime.utcnow()
    
    def search_documents_by_tag(self, tag: str) -> List[DocumentModel]:
        """Find documents by tag"""
        return [doc for doc in self.documents if tag in doc.metadata.tags]
    
    def get_documents_by_type(
        self, 
        doc_type: str
    ) -> List[DocumentModel]:
        """Get all documents of a specific type"""
        return [doc for doc in self.documents if doc.metadata.document_type == doc_type]
    
    def to_vector_input(self) -> List[Dict[str, Any]]:
        """Convert all documents to format suitable for vectorization"""
        return [
            {
                "doc_id": doc.metadata.document_id,
                "title": doc.metadata.title,
                "content": doc.content,
                "tags": doc.metadata.tags,
            }
            for doc in self.documents
        ]


class SharedSOPSchema(BaseModel):
    """
    Shared SOP (Standard Operating Procedure) section across all agent KBs
    
    Contains universal tooling docs (Consul, Redis, Vikunja) to prevent drift
    """
    
    name: str = Field(default="common-sop", description="Shared SOP section name")
    documents: List[DocumentModel] = Field(
        default=[],
        description="Universal SOP documents"
    )
    created_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation date"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update date"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "common-sop",
                "documents": [
                    {
                        "metadata": {
                            "document_id": "common-sop-consul-001",
                            "title": "Consul Integration Pattern",
                            "document_type": "sop"
                        },
                        "content": "All agents must register with Consul..."
                    },
                    {
                        "metadata": {
                            "document_id": "common-sop-redis-001",
                            "title": "Redis State Management",
                            "document_type": "sop"
                        },
                        "content": "All persistent state goes in Redis..."
                    }
                ]
            }
        }
    
    def add_sop(self, doc: DocumentModel) -> None:
        """Add a shared SOP document"""
        self.documents.append(doc)
        self.last_updated = datetime.utcnow()
