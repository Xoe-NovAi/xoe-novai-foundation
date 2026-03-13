"""
XNAi Synapse - Interactive Knowledge Synthesis Interface

This module provides the core interface for the XNAi Knowledge Synthesis Engine,
offering a NotebookLM-like experience with AI-powered analysis and synthesis.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncGenerator
from uuid import UUID, uuid4

import aiofiles
import httpx
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from ..core.llm_router import LLMRouter
from ..core.memory_bank import MemoryBank
from ..core.qdrant_manager import QdrantManager
from ..core.redis_streams import RedisStreamManager
from ..core.security.knowledge_access import KnowledgeAccessControl
from ..core.utils import sanitize_filename

logger = logging.getLogger(__name__)


class SynapseCell(BaseModel):
    """Represents a single cell in the XNAi Synapse notebook."""
    
    id: UUID
    cell_type: str  # "markdown", "code", "analysis", "visualization"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    execution_status: str = "pending"  # "pending", "running", "completed", "error"
    execution_result: Optional[Dict[str, Any]] = None
    dependencies: List[UUID] = Field(default_factory=list)


class SynapseNotebook(BaseModel):
    """Represents a complete XNAi Synapse notebook."""
    
    id: UUID
    title: str
    description: str
    tags: List[str] = Field(default_factory=list)
    cells: List[SynapseCell] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = False
    owner_id: Optional[str] = None


class ContentAnalysisRequest(BaseModel):
    """Request for AI-powered content analysis."""
    
    content: str
    analysis_type: str  # "summarization", "entity_extraction", "sentiment", "topic_modeling"
    context: Optional[Dict[str, Any]] = None
    model_preference: Optional[str] = None


class KnowledgeGraphQuery(BaseModel):
    """Query for knowledge graph operations."""
    
    query_type: str  # "entity_search", "relationship_query", "pattern_detection"
    parameters: Dict[str, Any]
    max_results: int = 100
    include_metadata: bool = True


class SynapseInterface:
    """Main interface for XNAi Synapse operations."""
    
    def __init__(
        self,
        llm_router: LLMRouter,
        memory_bank: MemoryBank,
        qdrant_manager: QdrantManager,
        redis_manager: RedisStreamManager,
        access_control: KnowledgeAccessControl
    ):
        self.llm_router = llm_router
        self.memory_bank = memory_bank
        self.qdrant_manager = qdrant_manager
        self.redis_manager = redis_manager
        self.access_control = access_control
        
        # WebSocket connections for real-time updates
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def create_notebook(self, title: str, description: str, owner_id: str) -> SynapseNotebook:
        """Create a new XNAi Synapse notebook."""
        notebook = SynapseNotebook(
            id=uuid4(),
            title=title,
            description=description,
            owner_id=owner_id
        )
        
        # Store in memory bank
        await self.memory_bank.save_to_archival(
            f"synapse_notebook_{notebook.id}",
            notebook.dict()
        )
        
        # Create collection in Qdrant for notebook embeddings
        collection_name = f"synapse_notebook_{sanitize_filename(str(notebook.id))}"
        await self.qdrant_manager.create_collection(
            collection_name=collection_name,
            vector_size=768,  # Standard embedding size
            distance="Cosine"
        )
        
        logger.info(f"Created new notebook: {notebook.id}")
        return notebook
    
    async def add_cell(
        self,
        notebook_id: UUID,
        cell_type: str,
        content: str,
        dependencies: List[UUID] = None
    ) -> SynapseCell:
        """Add a new cell to a notebook."""
        if dependencies is None:
            dependencies = []
            
        cell = SynapseCell(
            id=uuid4(),
            cell_type=cell_type,
            content=content,
            dependencies=dependencies
        )
        
        # Load notebook and add cell
        notebook_key = f"synapse_notebook_{notebook_id}"
        notebook_data = await self.memory_bank.get_from_archival(notebook_key)
        if not notebook_data:
            raise ValueError(f"Notebook {notebook_id} not found")
            
        notebook = SynapseNotebook(**notebook_data)
        notebook.cells.append(cell)
        notebook.updated_at = datetime.utcnow()
        
        # Save updated notebook
        await self.memory_bank.save_to_archival(notebook_key, notebook.dict())
        
        # Generate embeddings for the cell content
        await self._generate_cell_embeddings(notebook_id, cell)
        
        # Notify WebSocket clients
        await self._notify_notebook_update(notebook_id, "cell_added", cell.dict())
        
        return cell
    
    async def execute_cell(self, notebook_id: UUID, cell_id: UUID) -> Dict[str, Any]:
        """Execute a specific cell in a notebook."""
        notebook_key = f"synapse_notebook_{notebook_id}"
        notebook_data = await self.memory_bank.get_from_archival(notebook_key)
        if not notebook_data:
            raise ValueError(f"Notebook {notebook_id} not found")
            
        notebook = SynapseNotebook(**notebook_data)
        
        # Find the cell
        cell = next((c for c in notebook.cells if c.id == cell_id), None)
        if not cell:
            raise ValueError(f"Cell {cell_id} not found in notebook {notebook_id}")
        
        # Check dependencies
        for dep_id in cell.dependencies:
            dep_cell = next((c for c in notebook.cells if c.id == dep_id), None)
            if dep_cell and dep_cell.execution_status != "completed":
                raise ValueError(f"Dependency {dep_id} not completed")
        
        # Execute based on cell type
        cell.execution_status = "running"
        await self.memory_bank.save_to_archival(notebook_key, notebook.dict())
        
        try:
            if cell.cell_type == "analysis":
                result = await self._execute_analysis_cell(cell)
            elif cell.cell_type == "code":
                result = await self._execute_code_cell(cell)
            elif cell.cell_type == "markdown":
                result = {"type": "markdown", "content": cell.content}
            else:
                result = {"type": "unknown", "content": "Unknown cell type"}
                
            cell.execution_status = "completed"
            cell.execution_result = result
            cell.updated_at = datetime.utcnow()
            
        except Exception as e:
            cell.execution_status = "error"
            cell.execution_result = {"error": str(e)}
            logger.error(f"Error executing cell {cell_id}: {e}")
        
        # Save updated cell
        await self.memory_bank.save_to_archival(notebook_key, notebook.dict())
        
        # Notify WebSocket clients
        await self._notify_notebook_update(
            notebook_id, 
            "cell_executed", 
            {"cell_id": str(cell_id), "result": cell.execution_result}
        )
        
        return cell.execution_result
    
    async def _execute_analysis_cell(self, cell: SynapseCell) -> Dict[str, Any]:
        """Execute an analysis cell with AI-powered content analysis."""
        analysis_request = ContentAnalysisRequest(
            content=cell.content,
            analysis_type=cell.metadata.get("analysis_type", "summarization"),
            context=cell.metadata.get("context", {}),
            model_preference=cell.metadata.get("model_preference")
        )
        
        # Perform analysis using LLM router
        analysis_result = await self._analyze_content(analysis_request)
        
        # Store analysis results in Qdrant
        collection_name = f"synapse_notebook_{sanitize_filename(str(cell.id))}"
        await self.qdrant_manager.upsert_vectors(
            collection_name=collection_name,
            vectors=[analysis_result.get("embedding", [])],
            payloads=[{
                "cell_id": str(cell.id),
                "analysis_type": analysis_request.analysis_type,
                "result": analysis_result,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )
        
        return analysis_result
    
    async def _execute_code_cell(self, cell: SynapseCell) -> Dict[str, Any]:
        """Execute a code cell (sandboxed execution)."""
        # For security, we'll use a sandboxed execution environment
        # This is a simplified implementation - in production, use proper sandboxing
        
        code = cell.content
        try:
            # Basic Python code execution with restrictions
            # In production, use Docker containers or similar sandboxing
            result = await self._execute_sandboxed_code(code)
            return {"type": "code_execution", "result": result}
        except Exception as e:
            return {"type": "code_execution", "error": str(e)}
    
    async def _analyze_content(self, request: ContentAnalysisRequest) -> Dict[str, Any]:
        """Perform AI-powered content analysis."""
        prompt = self._build_analysis_prompt(request)
        
        # Use LLM router for analysis
        response = await self.llm_router.route_request(
            prompt=prompt,
            context={"analysis_type": request.analysis_type},
            model_preference=request.model_preference
        )
        
        # Parse and structure the response
        analysis_result = self._parse_analysis_response(response, request.analysis_type)
        
        return analysis_result
    
    def _build_analysis_prompt(self, request: ContentAnalysisRequest) -> str:
        """Build the prompt for content analysis."""
        analysis_prompts = {
            "summarization": f"Please provide a comprehensive summary of the following content:\n\n{request.content}\n\nSummary:",
            "entity_extraction": f"Extract all entities (people, organizations, locations, concepts) from the following content. Return in JSON format with entity type and confidence score:\n\n{request.content}\n\nEntities:",
            "sentiment": f"Analyze the sentiment of the following content. Return sentiment (positive/negative/neutral) and confidence score:\n\n{request.content}\n\nSentiment:",
            "topic_modeling": f"Identify the main topics and themes in the following content. Return topics with relevance scores:\n\n{request.content}\n\nTopics:"
        }
        
        return analysis_prompts.get(request.analysis_type, f"Analyze the following content:\n\n{request.content}")
    
    def _parse_analysis_response(self, response: str, analysis_type: str) -> Dict[str, Any]:
        """Parse and structure the LLM response."""
        try:
            # Try to parse as JSON first
            result = json.loads(response)
        except json.JSONDecodeError:
            # If not JSON, create structured response
            result = {
                "analysis_type": analysis_type,
                "content": response,
                "raw_response": response
            }
        
        # Add metadata
        result.update({
            "analysis_type": analysis_type,
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": "auto-selected"
        })
        
        return result
    
    async def search_knowledge_graph(self, query: KnowledgeGraphQuery) -> Dict[str, Any]:
        """Search the knowledge graph for entities and relationships."""
        if query.query_type == "entity_search":
            return await self._search_entities(query.parameters)
        elif query.query_type == "relationship_query":
            return await self._query_relationships(query.parameters)
        elif query.query_type == "pattern_detection":
            return await self._detect_patterns(query.parameters)
        else:
            raise ValueError(f"Unknown query type: {query.query_type}")
    
    async def _search_entities(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Search for entities in the knowledge graph."""
        query_text = parameters.get("query", "")
        entity_type = parameters.get("entity_type", None)
        limit = parameters.get("limit", 100)
        
        # Use Qdrant for semantic search
        results = await self.qdrant_manager.search_vectors(
            collection_name="knowledge_graph",
            query_text=query_text,
            limit=limit,
            filter={"entity_type": entity_type} if entity_type else None
        )
        
        return {
            "entities": results,
            "query": query_text,
            "entity_type": entity_type,
            "count": len(results)
        }
    
    async def _query_relationships(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Query relationships between entities."""
        source_entity = parameters.get("source_entity", "")
        relationship_type = parameters.get("relationship_type", None)
        target_entity = parameters.get("target_entity", "")
        
        # Query relationships from PostgreSQL
        # This would involve complex SQL queries in a real implementation
        relationships = []  # Placeholder for actual implementation
        
        return {
            "relationships": relationships,
            "source_entity": source_entity,
            "target_entity": target_entity,
            "relationship_type": relationship_type
        }
    
    async def _detect_patterns(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Detect patterns in the knowledge graph."""
        time_range = parameters.get("time_range", {})
        topics = parameters.get("topics", [])
        
        # Pattern detection logic
        # This would involve complex graph analysis algorithms
        patterns = []  # Placeholder for actual implementation
        
        return {
            "patterns": patterns,
            "time_range": time_range,
            "topics": topics,
            "count": len(patterns)
        }
    
    async def websocket_handler(self, websocket: WebSocket, notebook_id: str):
        """Handle WebSocket connections for real-time updates."""
        await websocket.accept()
        self.active_connections[notebook_id] = websocket
        
        try:
            while True:
                # Keep connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            if notebook_id in self.active_connections:
                del self.active_connections[notebook_id]
    
    async def _notify_notebook_update(
        self, 
        notebook_id: UUID, 
        update_type: str, 
        data: Dict[str, Any]
    ):
        """Notify WebSocket clients of notebook updates."""
        notebook_str = str(notebook_id)
        if notebook_str in self.active_connections:
            websocket = self.active_connections[notebook_str]
            try:
                await websocket.send_json({
                    "type": "notebook_update",
                    "notebook_id": notebook_str,
                    "update_type": update_type,
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"Error sending WebSocket update: {e}")
                # Remove broken connection
                del self.active_connections[notebook_str]
    
    async def _generate_cell_embeddings(self, notebook_id: UUID, cell: SynapseCell):
        """Generate embeddings for cell content."""
        # Use LLM router to generate embeddings
        embedding_response = await self.llm_router.route_request(
            prompt=f"Generate embedding for: {cell.content[:1000]}",  # Limit content length
            context={"operation": "embedding"},
            model_preference="embedding-model"
        )
        
        # Store in Qdrant
        collection_name = f"synapse_notebook_{sanitize_filename(str(notebook_id))}"
        await self.qdrant_manager.upsert_vectors(
            collection_name=collection_name,
            vectors=[embedding_response.get("embedding", [])],
            payloads=[{
                "cell_id": str(cell.id),
                "cell_type": cell.cell_type,
                "content_preview": cell.content[:200],
                "timestamp": datetime.utcnow().isoformat()
            }]
        )
    
    async def _execute_sandboxed_code(self, code: str) -> Dict[str, Any]:
        """Execute code in a sandboxed environment."""
        # This is a simplified implementation
        # In production, use proper sandboxing (Docker, etc.)
        
        # Basic security checks
        dangerous_imports = ["os", "sys", "subprocess", "importlib"]
        for imp in dangerous_imports:
            if f"import {imp}" in code or f"from {imp}" in code:
                raise ValueError(f"Code contains restricted import: {imp}")
        
        # Execute in isolated namespace
        namespace = {"__builtins__": {"print": print, "len": len, "str": str, "int": int}}
        
        try:
            exec(code, namespace)
            return {"status": "success", "output": "Code executed successfully"}
        except Exception as e:
            raise ValueError(f"Code execution failed: {e}")
    
    async def cleanup(self):
        """Clean up resources."""
        # Close WebSocket connections
        for websocket in self.active_connections.values():
            try:
                await websocket.close()
            except Exception:
                pass
        self.active_connections.clear()