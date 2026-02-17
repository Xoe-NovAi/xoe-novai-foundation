"""
Phase 7: Semantic Search Service - Agent Bus Integration

This module integrates the semantic search knowledge base with the XNAi Agent Bus.
Registers as a microservice and responds to task assignments from the coordinator.
"""

import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

try:
    from pydantic import BaseModel, Field
except ImportError:
    print("ERROR: pydantic not installed")
    exit(1)

# Semantic search imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from ..api.semantic_search import SimpleVectorIndex

logger = logging.getLogger(__name__)

# Agent Bus constants
AGENT_NAME = "semantic-search-service"
CAPABILITIES = [
    "semantic_search",
    "knowledge_base_query",
    "documentation_lookup",
    "service_discovery"
]
INBOX_DIR = Path("/home/arcana-novai/Documents/xnai-foundation/communication_hub/inbox")
OUTBOX_DIR = Path("/home/arcana-novai/Documents/xnai-foundation/communication_hub/outbox")


# ============================================================================
# DATA MODELS FOR AGENT BUS INTEGRATION
# ============================================================================

@dataclass
class Message:
    """Agent Bus message format"""
    message_id: str
    timestamp: str
    sender: str
    target: str
    type: str  # task_assignment, task_completion, error_report, heartbeat
    priority: str  # high, medium, low
    content: Dict[str, Any]
    correlation_id: Optional[str] = None
    
    def to_json(self) -> str:
        """Serialize message to JSON"""
        return json.dumps({
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "target": self.target,
            "type": self.type,
            "priority": self.priority,
            "content": self.content,
            "correlation_id": self.correlation_id
        })
    
    @staticmethod
    def from_json(data: str) -> "Message":
        """Deserialize message from JSON"""
        obj = json.loads(data)
        return Message(**obj)


class SemanticSearchRequest(BaseModel):
    """Request format for semantic search tasks"""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=5, description="Number of results to return")
    service_filter: Optional[str] = Field(None, description="Filter by service name")
    min_score: float = Field(default=0.3, description="Minimum cosine similarity score")
    

class SemanticSearchResponse(BaseModel):
    """Response format for semantic search results"""
    query: str
    results: List[Dict[str, Any]]
    execution_time_ms: float
    total_results: int
    status: str = "success"


# ============================================================================
# SEMANTIC SEARCH SERVICE
# ============================================================================

class SemanticSearchAgentBusService:
    """
    Semantic search service integrated with XNAi Agent Bus.
    
    Responsibilities:
    - Register with Agent Bus (Consul + messaging)
    - Listen for task assignments
    - Execute semantic search queries
    - Return results to coordinator
    - Report health status
    """
    
    def __init__(self):
        self.agent_name = AGENT_NAME
        self.capabilities = CAPABILITIES
        self.index = SimpleVectorIndex()
        self.task_count = 0
        self.success_count = 0
        self.error_count = 0
        self.last_heartbeat = datetime.utcnow().isoformat()
        self.status = "initializing"
        
        # Create communication directories
        INBOX_DIR.mkdir(parents=True, exist_ok=True)
        OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized {self.agent_name} with capabilities: {self.capabilities}")
    
    async def startup(self):
        """Initialize service and register with Agent Bus"""
        logger.info("Starting semantic search service...")
        
        # Load knowledge base
        doc_dir = Path("/home/arcana-novai/Documents/xnai-foundation/knowledge/technical_manuals")
        if doc_dir.exists():
            chunk_count = self.index.add_chunks(doc_dir)
            logger.info(f"Loaded {chunk_count} chunks from knowledge base")
            self.status = "ready"
        else:
            logger.error(f"Knowledge base directory not found: {doc_dir}")
            self.status = "error"
            return False
        
        # Send registration heartbeat
        await self.send_heartbeat()
        logger.info(f"{self.agent_name} startup complete. Status: {self.status}")
        return True
    
    async def send_heartbeat(self):
        """Send heartbeat to Agent Bus"""
        message = Message(
            message_id=f"{self.agent_name}-heartbeat-{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow().isoformat(),
            sender=self.agent_name,
            target="agent_coordinator",
            type="heartbeat",
            priority="low",
            content={
                "status": self.status,
                "capabilities": self.capabilities,
                "task_count": self.task_count,
                "success_count": self.success_count,
                "error_count": self.error_count
            }
        )
        await self._write_message(message, OUTBOX_DIR)
        self.last_heartbeat = datetime.utcnow().isoformat()
    
    async def listen_for_tasks(self, poll_interval: int = 5):
        """
        Listen for incoming task assignments from Agent Bus.
        
        Args:
            poll_interval: Check for new messages every N seconds
        """
        logger.info(f"Listening for tasks in {INBOX_DIR} (poll interval: {poll_interval}s)")
        
        while True:
            try:
                # Check for new messages
                message_files = sorted(INBOX_DIR.glob(f"{self.agent_name}-*.json"))
                
                for msg_file in message_files:
                    try:
                        message_data = msg_file.read_text()
                        message = Message.from_json(message_data)
                        
                        if message.type == "task_assignment":
                            await self.handle_task(message)
                        elif message.type == "shutdown":
                            logger.info("Received shutdown signal")
                            return
                        
                        # Clean up processed message
                        msg_file.unlink()
                    except Exception as e:
                        logger.error(f"Error processing message {msg_file}: {e}")
                        msg_file.unlink()
                
                # Send periodic heartbeat
                await self.send_heartbeat()
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"Error in listen_for_tasks: {e}")
                await asyncio.sleep(poll_interval)
    
    async def handle_task(self, message: Message):
        """
        Handle incoming task assignment.
        
        Args:
            message: Task assignment message from coordinator
        """
        self.task_count += 1
        task_id = message.message_id
        
        try:
            logger.info(f"Handling task {task_id}: {message.content.get('task_type', 'unknown')}")
            
            # Extract search parameters
            query = message.content.get("query", "")
            top_k = message.content.get("top_k", 5)
            service_filter = message.content.get("service_filter")
            min_score = message.content.get("min_score", 0.3)
            
            if not query:
                raise ValueError("Query parameter required")
            
            # Execute search
            start_time = datetime.utcnow()
            results = self.index.search(query, top_k=top_k)
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Filter results if service filter specified
            if service_filter:
                results = [r for r in results if r["service"] == service_filter]
            
            # Filter by minimum score
            results = [r for r in results if r["score"] >= min_score]
            
            # Send success response
            response = Message(
                message_id=f"{self.agent_name}-response-{task_id}",
                timestamp=datetime.utcnow().isoformat(),
                sender=self.agent_name,
                target=message.sender,
                type="task_completion",
                priority="high",
                content={
                    "status": "success",
                    "query": query,
                    "results": results,
                    "result_count": len(results),
                    "execution_time_ms": execution_time
                },
                correlation_id=task_id
            )
            
            await self._write_message(response, OUTBOX_DIR)
            self.success_count += 1
            logger.info(f"Task {task_id} completed successfully. Found {len(results)} results.")
            
        except Exception as e:
            logger.error(f"Error handling task {task_id}: {e}")
            
            # Send error response
            error_response = Message(
                message_id=f"{self.agent_name}-error-{task_id}",
                timestamp=datetime.utcnow().isoformat(),
                sender=self.agent_name,
                target=message.sender,
                type="error_report",
                priority="high",
                content={
                    "error_type": "task_execution_failed",
                    "message": str(e),
                    "context": {"original_task_id": task_id}
                },
                correlation_id=task_id
            )
            
            await self._write_message(error_response, OUTBOX_DIR)
            self.error_count += 1
    
    async def _write_message(self, message: Message, output_dir: Path):
        """Write message to output directory for Agent Bus"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        msg_file = output_dir / f"{message.target}-{message.message_id}.json"
        msg_file.write_text(message.to_json())
        logger.debug(f"Wrote message to {msg_file}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "capabilities": self.capabilities,
            "task_count": self.task_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "last_heartbeat": self.last_heartbeat
        }


# ============================================================================
# STANDALONE SERVICE ENTRY POINT
# ============================================================================

async def main():
    """Run semantic search service as standalone Agent Bus agent"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    service = SemanticSearchAgentBusService()
    
    # Startup
    success = await service.startup()
    if not success:
        logger.error("Failed to startup service")
        return 1
    
    # Listen for tasks
    try:
        await service.listen_for_tasks()
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

