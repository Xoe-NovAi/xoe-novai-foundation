"""
Memory Bank System for Voice Assistant Platform
Central memory management system for conversation context and knowledge storage
"""

import os
import json
import sqlite3
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config_manager import ConfigManager

def get_storage_path(subdir: str) -> str:
    """Get storage path for memory data"""
    base_path = os.path.expanduser("~/.voice_assistant")
    return os.path.join(base_path, subdir)

logger = logging.getLogger(__name__)

class MemoryItem:
    """Represents a single memory item in the memory bank"""
    
    def __init__(self, 
                 content: str,
                 memory_type: str = "conversation",
                 context: Optional[Dict[str, Any]] = None,
                 priority: int = 0,
                 ttl: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.id = hashlib.sha256(content.encode()).hexdigest()[:16]
        self.content = content
        self.memory_type = memory_type
        self.context = context or {}
        self.priority = priority
        self.timestamp = time.time()
        self.ttl = ttl
        self.metadata = metadata or {}
        self.embedding = None  # Will be populated by embedding model
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory item to dictionary for storage"""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "context": json.dumps(self.context),
            "priority": self.priority,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "metadata": json.dumps(self.metadata),
            "embedding": self.embedding.tobytes() if self.embedding is not None else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create memory item from dictionary"""
        item = cls(
            content=data["content"],
            memory_type=data["memory_type"],
            context=json.loads(data["context"]),
            priority=data["priority"],
            ttl=data["ttl"],
            metadata=json.loads(data["metadata"])
        )
        item.id = data["id"]
        item.timestamp = data["timestamp"]
        if data["embedding"] is not None:
            item.embedding = data["embedding"]
        return item
    
    def is_expired(self) -> bool:
        """Check if memory item has expired"""
        if self.ttl is None:
            return False
        return time.time() > self.timestamp + self.ttl
    
    def __repr__(self) -> str:
        return f"MemoryItem(id={self.id[:8]}, type={self.memory_type}, priority={self.priority})"


class MemoryBank:
    """Central memory management system for voice assistant
    
    Features:
    - SQLite-based persistent storage
    - Semantic search with sentence embeddings
    - Context management for conversations
    - Automatic expiration of old memories
    - Thread-safe operations
    """
    
    def __init__(self, storage_path: Optional[str] = None, max_memories: Optional[int] = None):
        # load configuration from ConfigManager if available
        self.config_manager = ConfigManager()
        mem_conf = self.config_manager.get_section('memory', {})
        # memory subsystem enabled/disabled flag
        self.enabled = mem_conf.get('enabled', True)
        # maximum number of memories to store
        self.max_memories = max_memories or mem_conf.get('max_memories', 10000)
        # default TTL for new memories
        self.ttl_default = mem_conf.get('ttl_default')
        # semantic search configuration
        self.semantic_search_enabled = mem_conf.get('semantic_search', True)
        self.embedding_model_name = mem_conf.get('embedding_model', 'all-MiniLM-L6-v2')
        # directory under base storage for memory data
        subdir = mem_conf.get('storage_subdir', 'memory')
        self.storage_path = storage_path or get_storage_path(subdir)

        # threading lock for database operations
        import threading
        self._lock = threading.Lock()

        self._initialize_storage()
        self.context_manager = ContextManager()
        self.retrieval_engine = RetrievalEngine()
        self._load_embeddings_model()
        self._start_cleanup_thread()
    
    def _initialize_storage(self):
        """Initialize SQLite database for memory storage"""
        os.makedirs(self.storage_path, exist_ok=True)
        self.db_path = os.path.join(self.storage_path, "memory.db")
        
        # allow use from multiple threads
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                context TEXT,
                priority INTEGER DEFAULT 0,
                timestamp REAL NOT NULL,
                ttl INTEGER,
                metadata TEXT,
                embedding BLOB
            )
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_type ON memories(memory_type)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_priority ON memories(priority)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expiry ON memories(timestamp, ttl)
        """)
        
        self.conn.commit()
    
    def _load_embeddings_model(self):
        """Load embedding model for semantic search"""
        if not self.semantic_search_enabled:
            logger.info("Semantic search disabled by configuration")
            self.embedding_model = None
            return

        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"Loaded sentence transformer model '{self.embedding_model_name}' for semantic search")
        except ImportError:
            logger.warning("sentence-transformers not available, semantic search disabled")
            self.embedding_model = None
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self.embedding_model = None
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread for expired memories"""
        import threading
        import time
        
        def cleanup_loop():
            while True:
                try:
                    time.sleep(3600)  # Run every hour
                    deleted = self.cleanup_expired()
                    if deleted > 0:
                        logger.info(f"Cleaned up {deleted} expired memories")
                except Exception as e:
                    logger.error(f"Cleanup thread error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        logger.info("Started memory cleanup background thread")
    
    def store(self, memory_item: MemoryItem) -> None:
        """Store a memory item in the database
        
        Automatically enforces memory limits by removing oldest, lowest-priority
        items when max_memories is exceeded.
        """
        if not self.enabled:
            logger.debug("Memory store called while memory subsystem is disabled")
            return

        # apply default ttl if not provided
        if memory_item.ttl is None and self.ttl_default is not None:
            memory_item.ttl = self.ttl_default

        if self.embedding_model and memory_item.embedding is None:
            memory_item.embedding = self.embedding_model.encode([memory_item.content])[0]

        with self._lock:
            self.cursor.execute("""
                INSERT OR REPLACE INTO memories 
                (id, content, memory_type, context, priority, timestamp, ttl, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory_item.id,
                memory_item.content,
                memory_item.memory_type,
                json.dumps(memory_item.context),
                memory_item.priority,
                memory_item.timestamp,
                memory_item.ttl,
                json.dumps(memory_item.metadata),
                memory_item.embedding.tobytes() if memory_item.embedding is not None else None
            ))
            self.conn.commit()
        
        # Enforce memory limit
        self._enforce_memory_limit()
    
    def _enforce_memory_limit(self) -> None:
        """Enforce maximum memory limit by removing old, low-priority items"""
        with self._lock:
            self.cursor.execute("SELECT COUNT(*) as count FROM memories")
            count = self.cursor.fetchone()["count"]
        
        if count > self.max_memories:
            # Remove oldest, lowest-priority memories
            excess = count - self.max_memories
            with self._lock:
                self.cursor.execute("""
                    DELETE FROM memories 
                    WHERE id IN (
                        SELECT id FROM memories 
                        ORDER BY priority ASC, timestamp ASC 
                        LIMIT ?
                    )
                """, (excess,))
                self.conn.commit()
            logger.info(f"Removed {excess} memories to enforce limit")
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        self.cursor.execute("""
            SELECT content, context, timestamp FROM memories 
            WHERE memory_type = 'conversation'
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = self.cursor.fetchall()
        return [dict(row) for row in reversed(rows)]
    
    def summarize_context(self, query: str, memory_types: Optional[List[str]] = None) -> str:
        """Generate a summary of relevant context for a query

        The optional ``memory_types`` list can restrict the search to a subset of
        memories (e.g. ['knowledge'] or ['conversation']).
        """
        memories = self.search(query, max_results=5, memory_types=memory_types)
        if not memories:
            return ""
        
        summary_parts = []
        for memory in memories:
            role = memory.context.get("role", "unknown")
            summary_parts.append(f"[{role}]: {memory.content[:200]}")
        
        return "\n".join(summary_parts)
    
    def retrieve(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a specific memory item by ID"""
        self.cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = self.cursor.fetchone()
        if row:
            return MemoryItem.from_dict(dict(row))
        return None
    
    def search(self, query: str, max_results: int = 5, 
               memory_types: Optional[List[str]] = None) -> List[MemoryItem]:
        """Search memories using semantic search"""
        if not query.strip():
            return []
        
        # First try exact match
        if memory_types:
            placeholders = ','.join('?' for _ in memory_types)
            q = f"SELECT * FROM memories WHERE content LIKE ? AND memory_type IN ({placeholders}) ORDER BY priority DESC, timestamp DESC LIMIT ?"
            params = [f"%{query}%", *memory_types, max_results]
        else:
            q = "SELECT * FROM memories WHERE content LIKE ? ORDER BY priority DESC, timestamp DESC LIMIT ?"
            params = [f"%{query}%", max_results]

        self.cursor.execute(q, params)
        exact_matches = self.cursor.fetchall()
        if exact_matches:
            return [MemoryItem.from_dict(dict(row)) for row in exact_matches]
        
        # If no exact match and embedding model available, use semantic search
        if self.embedding_model:
            query_embedding = self.embedding_model.encode([query])[0]
            
            self.cursor.execute("SELECT * FROM memories WHERE embedding IS NOT NULL")
            all_memories = self.cursor.fetchall()
            
            similarities = []
            for row in all_memories:
                memory = MemoryItem.from_dict(dict(row))
                if memory.embedding is not None:
                    similarity = self._calculate_similarity(query_embedding, memory.embedding)
                    similarities.append((memory, similarity))
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            results = [result[0] for result in similarities[:max_results]]
            
            # Filter by memory types if specified (already performed above for exact)
            if memory_types:
                results = [r for r in results if r.memory_type in memory_types]
            
            return results
        
        # Fallback to simple text search
        self.cursor.execute("""
            SELECT * FROM memories 
            WHERE content LIKE ?
            ORDER BY priority DESC, timestamp DESC
            LIMIT ?
        """, (f"%{query}%", max_results))
        rows = self.cursor.fetchall()
        return [MemoryItem.from_dict(dict(row)) for row in rows]
    
    def get_relevant_context(self, query: str) -> Dict[str, Any]:
        """Get most relevant context for a given query"""
        memories = self.search(query, max_results=3)
        
        context = {}
        for memory in memories:
            context.update(memory.context)
        
        return context
    
    def store_interaction(self, input_text: str, output_text: str) -> None:
        """Store a complete interaction (input and output)"""
        # Store input as conversation memory
        input_memory = MemoryItem(
            content=input_text,
            memory_type="conversation",
            context={"role": "user"},
            priority=1
        )
        self.store(input_memory)
        
        # Store output as conversation memory
        output_memory = MemoryItem(
            content=output_text,
            memory_type="conversation",
            context={"role": "assistant"},
            priority=1
        )
        self.store(output_memory)
    
    def cleanup_expired(self) -> int:
        """Remove expired memory items"""
        with self._lock:
            self.cursor.execute("""
                DELETE FROM memories 
                WHERE ttl IS NOT NULL AND timestamp + ttl < ?
            """, (time.time(),))
            deleted_count = self.cursor.rowcount
            self.conn.commit()
        return deleted_count
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage"""
        with self._lock:
            self.cursor.execute("SELECT COUNT(*) as count FROM memories")
            total_count = self.cursor.fetchone()["count"]
        
        with self._lock:
            self.cursor.execute("SELECT COUNT(*) as count FROM memories WHERE ttl IS NOT NULL")
            expiring_count = self.cursor.fetchone()["count"]
        
        with self._lock:
            self.cursor.execute("SELECT COUNT(*) as count FROM memories WHERE timestamp > ?", 
                              (time.time() - 86400,))
            recent_count = self.cursor.fetchone()["count"]
        
        return {
            "total_items": total_count,
            "expiring_items": expiring_count,
            "recent_items_24h": recent_count,
            "storage_path": self.storage_path
        }
    
    def close(self) -> None:
        """Close database connection"""
        self.conn.close()
        logger.info("Memory bank connection closed")

    def reload_config(self) -> None:
        """Reload memory configuration from the ConfigManager."""
        # reload configuration from disk in case another component changed it
        self.config_manager.reload()
        mem_conf = self.config_manager.get_section('memory', {})
        self.enabled = mem_conf.get('enabled', self.enabled)
        self.max_memories = mem_conf.get('max_memories', self.max_memories)
        self.ttl_default = mem_conf.get('ttl_default', self.ttl_default)
        self.semantic_search_enabled = mem_conf.get('semantic_search', self.semantic_search_enabled)
        new_model = mem_conf.get('embedding_model', self.embedding_model_name)
        logger.debug(f"Memory config values after reload: enabled={self.enabled}, max_memories={self.max_memories}, ttl_default={self.ttl_default}, semantic_search={self.semantic_search_enabled}, embedding_model={new_model}")
        if new_model != self.embedding_model_name:
            self.embedding_model_name = new_model
            self._load_embeddings_model()
        logger.info("Memory bank configuration reloaded")

    def clear_memory(self) -> None:
        """Remove all stored memories from the database"""
        with self._lock:
            self.cursor.execute("DELETE FROM memories")
            self.conn.commit()
        logger.info("All memories cleared")

    def clear_memory(self) -> None:
        """Remove all stored memories from the database"""
        with self._lock:
            self.cursor.execute("DELETE FROM memories")
            self.conn.commit()
        logger.info("All memories cleared")
    
    def _calculate_similarity(self, embedding1, embedding2) -> float:
        """Calculate cosine similarity between two embeddings"""
        import numpy as np
        dot_product = np.dot(embedding1, embedding2)
        norm_product = np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        if norm_product == 0:
            return 0.0
        return dot_product / norm_product


class ContextManager:
    """Manages conversation context and state"""
    
    def __init__(self):
        self.current_context = {}
        self.context_history = []
        self.context_priority = {}
        self.context_ttl = 3600  # 1 hour default
    
    def update_context(self, new_context: Dict[str, Any]) -> None:
        """Update current context with new information"""
        self.current_context.update(new_context)
        self.context_history.append({
            "context": new_context,
            "timestamp": time.time()
        })
        
        # Keep only recent context history
        self.context_history = [
            ctx for ctx in self.context_history 
            if time.time() - ctx["timestamp"] < self.context_ttl
        ]
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context"""
        return self.current_context
    
    def get_context_history(self) -> List[Dict[str, Any]]:
        """Get context history"""
        return self.context_history
    
    def clear_context(self) -> None:
        """Clear current context"""
        self.current_context = {}
        self.context_history = []


class RetrievalEngine:
    """Fast lookup and retrieval of relevant information
    
    Placeholder for future advanced search/indexing logic (e.g. FAISS)
    """
    
    def __init__(self):
        self.index = {}
        self.vector_store = None
    
    def search(self, query: str, max_results: int = 5) -> List[MemoryItem]:
        """Search for relevant memories (stubbed)
        """
        return []


# Global memory bank instance
_memory_bank = None


def get_memory_bank() -> MemoryBank:
    """Get global memory bank instance (singleton)

    The instance will read configuration on first access and honor memory.enabled.
    """
    global _memory_bank
    if _memory_bank is None:
        _memory_bank = MemoryBank()
    return _memory_bank


def initialize_memory_bank(storage_path: Optional[str] = None, max_memories: Optional[int] = None) -> MemoryBank:
    """Initialize global memory bank with custom settings"""
    global _memory_bank
    _memory_bank = MemoryBank(storage_path=storage_path, max_memories=max_memories)
    return _memory_bank


# Convenience functions
def store_memory(content: str, 
                 memory_type: str = "conversation",
                 context: Optional[Dict[str, Any]] = None,
                 priority: int = 0,
                 ttl: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> str:
    """Store a memory item"""
    memory_item = MemoryItem(
        content=content,
        memory_type=memory_type,
        context=context,
        priority=priority,
        ttl=ttl,
        metadata=metadata
    )
    get_memory_bank().store(memory_item)
    return memory_item.id


def retrieve_memory(memory_id: str) -> Optional[MemoryItem]:
    """Retrieve a specific memory item"""
    return get_memory_bank().retrieve(memory_id)


def search_memory(query: str, max_results: int = 5, memory_types: Optional[List[str]] = None) -> List[MemoryItem]:
    """Search for relevant memories with optional type filtering"""
    return get_memory_bank().search(query, max_results, memory_types)


def get_relevant_context(query: str) -> Dict[str, Any]:
    """Get most relevant context for a query"""
    return get_memory_bank().get_relevant_context(query)


def store_interaction(input_text: str, output_text: str) -> None:
    """Store a complete interaction"""
    get_memory_bank().store_interaction(input_text, output_text)


def cleanup_expired_memory() -> int:
    """Remove expired memory items"""
    return get_memory_bank().cleanup_expired()


def get_memory_stats() -> Dict[str, Any]:
    """Get memory statistics"""
    return get_memory_bank().get_memory_stats()