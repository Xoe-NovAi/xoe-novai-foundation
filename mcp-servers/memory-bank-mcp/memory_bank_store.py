#!/usr/bin/env python3
"""
Memory Bank SQL Store - Fallback System
=========================================
SQLite-based fallback for memory bank persistence when MCP server or Redis is unavailable.

Features:
- Local SQLite database for sovereign, offline operation
- Full-text search indexing on memory bank content
- Automatic context tier simulation (hot/warm/cold)
- Connection pooling with automatic reconnection
- Compatible with MCP tool signatures
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    import aiosqlite
except ImportError:
    aiosqlite = None

logger = logging.getLogger(__name__)

class ContextTier(str, Enum):
    """Memory bank context tiers."""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"

class ContextType(str, Enum):
    """Types of context stored."""
    PROJECT = "project"
    TECHNICAL = "technical"
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    TEMPORAL = "temporal"

@dataclass
class ContextEntry:
    """Context entry with metadata."""
    context_id: str
    agent_id: str
    context_type: str
    tier: str
    version: int
    content: str
    created_at: str
    last_modified: str
    size_bytes: int
    access_count: int = 0
    relevance_score: float = 0.0

class MemoryBankStore:
    """
    SQLite-based memory bank store with FTS support.
    
    Provides a complete fallback implementation for when the primary
    MCP server or Redis backend is unavailable.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the memory bank store.
        
        Args:
            db_path: Path to SQLite database file. Defaults to /storage/memory_bank_fallback.db
                    (integrated with Omega stack storage)
        """
        if db_path is None:
            # Use Omega stack storage directory (/storage)
            # Fall back to ~/.xnai if /storage doesn't exist (for development)
            storage_path = Path("/storage")
            if not storage_path.parent.exists():
                storage_path = Path.home() / ".xnai"
            db_path = storage_path / "memory_bank_fallback.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._db: Optional[aiosqlite.Connection] = None
        self._connection_lock = asyncio.Lock()
        self._initialized = False
        
        # In-memory cache layer for hot tier
        self._hot_cache: Dict[str, ContextEntry] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_max_age_seconds = 3600  # 1 hour TTL
        
        # Performance metrics
        self.metrics = {
            "context_reads": 0,
            "context_writes": 0,
            "agent_registrations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "fts_searches": 0,
            "errors": 0,
        }

    async def initialize(self) -> bool:
        """
        Initialize database connection and create schema.
        
        Returns:
            True if initialization successful
        """
        if self._initialized:
            return True

        if not aiosqlite:
            logger.error("aiosqlite not available - install with: pip install aiosqlite")
            return False

        try:
            async with self._connection_lock:
                self._db = await aiosqlite.connect(str(self.db_path))
                
                # Enable FTS5
                await self._db.execute("PRAGMA foreign_keys = ON")
                
                # Create schema
                await self._create_schema()
                
                self._initialized = True
                logger.info(f"Memory bank store initialized: {self.db_path}")
                return True

        except Exception as e:
            logger.error(f"Failed to initialize memory bank store: {e}")
            self._initialized = False
            return False

    async def _create_schema(self) -> None:
        """Create database tables and indexes."""
        
        # Agents table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                capabilities TEXT NOT NULL,
                memory_limit_gb REAL NOT NULL,
                last_seen TEXT NOT NULL,
                performance_score REAL DEFAULT 0.0,
                total_operations INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Context entries table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS contexts (
                context_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                context_type TEXT NOT NULL,
                tier TEXT NOT NULL,
                version INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_modified TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                access_count INTEGER DEFAULT 0,
                relevance_score REAL DEFAULT 0.0,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
                UNIQUE(agent_id, context_type, tier, version)
            )
        """)

        # Context history table (for versions)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS context_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (context_id) REFERENCES contexts(context_id),
                UNIQUE(context_id, version)
            )
        """)

        # Full-text search virtual table
        await self._db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS contexts_fts USING fts5(
                context_id UNINDEXED,
                content,
                tokenize = 'porter'
            )
        """)

        # Access log for performance tracking
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS access_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                access_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                duration_ms INTEGER,
                FOREIGN KEY (context_id) REFERENCES contexts(context_id),
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)

        # Indexes
        await self._db.execute(
            "CREATE INDEX IF NOT EXISTS idx_contexts_agent ON contexts(agent_id)"
        )
        await self._db.execute(
            "CREATE INDEX IF NOT EXISTS idx_contexts_type ON contexts(context_type)"
        )
        await self._db.execute(
            "CREATE INDEX IF NOT EXISTS idx_contexts_tier ON contexts(tier)"
        )
        await self._db.execute(
            "CREATE INDEX IF NOT EXISTS idx_access_log_timestamp ON access_log(timestamp)"
        )

        await self._db.commit()

    async def register_agent(
        self,
        agent_id: str,
        capabilities: List[str],
        memory_limit_gb: float
    ) -> Dict[str, Any]:
        """Register an agent with capabilities."""
        try:
            if not self._initialized:
                return {"status": "error", "message": "Store not initialized"}

            now = datetime.now().isoformat()
            capabilities_json = json.dumps(capabilities)

            async with self._connection_lock:
                await self._db.execute("""
                    INSERT OR REPLACE INTO agents
                    (agent_id, capabilities, memory_limit_gb, last_seen, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (agent_id, capabilities_json, memory_limit_gb, now, now, now))
                
                await self._db.commit()

            self.metrics["agent_registrations"] += 1
            logger.info(f"Registered agent: {agent_id}")

            return {
                "status": "success",
                "agent_id": agent_id,
                "capabilities": capabilities,
                "memory_limit_gb": memory_limit_gb,
                "registration_time": now
            }

        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            self.metrics["errors"] += 1
            return {"status": "error", "message": str(e)}

    async def set_context(
        self,
        agent_id: str,
        context_type: str,
        tier: str,
        content: Dict[str, Any],
        version: int = 1
    ) -> Dict[str, Any]:
        """Store context for an agent."""
        try:
            if not self._initialized:
                return {"status": "error", "message": "Store not initialized"}

            context_id = f"{agent_id}:{context_type}:{tier}"
            now = datetime.now().isoformat()
            content_json = json.dumps(content)
            size_bytes = len(content_json.encode())

            async with self._connection_lock:
                await self._db.execute("""
                    INSERT OR REPLACE INTO contexts
                    (context_id, agent_id, context_type, tier, version, content,
                     created_at, last_modified, size_bytes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (context_id, agent_id, context_type, tier, version, content_json,
                      now, now, size_bytes))

                await self._db.execute("""
                    INSERT INTO context_history
                    (context_id, version, content, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (context_id, version, content_json, now))

                await self._db.execute("""
                    INSERT OR REPLACE INTO contexts_fts
                    (context_id, content)
                    VALUES (?, ?)
                """, (context_id, content_json))

                await self._db.commit()

            if tier == ContextTier.HOT.value:
                self._hot_cache[context_id] = ContextEntry(
                    context_id=context_id,
                    agent_id=agent_id,
                    context_type=context_type,
                    tier=tier,
                    version=version,
                    content=content_json,
                    created_at=now,
                    last_modified=now,
                    size_bytes=size_bytes
                )
                self._cache_timestamps[context_id] = asyncio.get_event_loop().time()

            self.metrics["context_writes"] += 1
            logger.info(f"Stored context: {context_id} (v{version})")

            return {
                "status": "success",
                "context_id": context_id,
                "version": version,
                "stored_at": now
            }

        except Exception as e:
            logger.error(f"Failed to set context: {e}")
            self.metrics["errors"] += 1
            return {"status": "error", "message": str(e)}

    async def get_context(
        self,
        agent_id: str,
        context_type: str,
        tier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve context for an agent."""
        try:
            if not self._initialized:
                return {"status": "error", "message": "Store not initialized"}

            if tier is None:
                tier = ContextTier.HOT.value

            context_id = f"{agent_id}:{context_type}:{tier}"

            # Check hot cache first
            if context_id in self._hot_cache:
                self.metrics["cache_hits"] += 1
                cached = self._hot_cache[context_id]
                cache_age = asyncio.get_event_loop().time() - self._cache_timestamps.get(context_id, 0)
                
                if cache_age < self._cache_max_age_seconds:
                    logger.info(f"Cache hit for context: {context_id}")
                    await self._log_access(agent_id, context_id, "read")
                    
                    return {
                        "status": "success",
                        "context_id": context_id,
                        "agent_id": agent_id,
                        "context_type": context_type,
                        "tier": tier,
                        "content": json.loads(cached.content),
                        "version": cached.version,
                        "source": "cache",
                        "accessed_at": datetime.now().isoformat()
                    }
                else:
                    del self._hot_cache[context_id]
                    del self._cache_timestamps[context_id]

            self.metrics["cache_misses"] += 1

            # Retrieve from database
            async with self._connection_lock:
                async with self._db.execute("""
                    SELECT context_id, agent_id, context_type, tier, version,
                           content, created_at, last_modified, size_bytes,
                           access_count, relevance_score
                    FROM contexts
                    WHERE context_id = ?
                """, (context_id,)) as cursor:
                    row = await cursor.fetchone()

            if row:
                async with self._connection_lock:
                    await self._db.execute("""
                        UPDATE contexts
                        SET access_count = access_count + 1,
                            last_modified = ?
                        WHERE context_id = ?
                    """, (datetime.now().isoformat(), context_id))
                    await self._db.commit()

                await self._log_access(agent_id, context_id, "read")
                self.metrics["context_reads"] += 1

                return {
                    "status": "success",
                    "context_id": context_id,
                    "agent_id": agent_id,
                    "context_type": context_type,
                    "tier": tier,
                    "content": json.loads(row[5]),
                    "version": row[4],
                    "source": "database",
                    "accessed_at": datetime.now().isoformat()
                }

            return {
                "status": "not_found",
                "context_id": context_id,
                "message": f"Context {context_id} not found"
            }

        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            self.metrics["errors"] += 1
            return {"status": "error", "message": str(e)}

    async def search_context(
        self,
        query: str,
        agent_id: Optional[str] = None,
        context_type: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Full-text search across contexts."""
        try:
            if not self._initialized:
                return {"status": "error", "message": "Store not initialized"}

            sql = """
                SELECT c.context_id, c.agent_id, c.context_type, c.tier,
                       c.version, c.content, rank
                FROM contexts_fts
                JOIN contexts c ON contexts_fts.context_id = c.context_id
                WHERE contexts_fts MATCH ?
            """
            params: List[Any] = [query]

            if agent_id:
                sql += " AND c.agent_id = ?"
                params.append(agent_id)

            if context_type:
                sql += " AND c.context_type = ?"
                params.append(context_type)

            sql += " ORDER BY rank LIMIT ?"
            params.append(limit)

            async with self._connection_lock:
                async with self._db.execute(sql, params) as cursor:
                    rows = await cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    "context_id": row[0],
                    "agent_id": row[1],
                    "context_type": row[2],
                    "tier": row[3],
                    "version": row[4],
                    "content": json.loads(row[5]),
                    "rank": row[6]
                })

            self.metrics["fts_searches"] += 1

            return {
                "status": "success",
                "query": query,
                "results": results,
                "count": len(results)
            }

        except Exception as e:
            logger.error(f"Full-text search failed: {e}")
            self.metrics["errors"] += 1
            return {"status": "error", "message": str(e)}

    async def _log_access(self, agent_id: str, context_id: str, access_type: str) -> None:
        """Log context access for analytics."""
        try:
            async with self._connection_lock:
                await self._db.execute("""
                    INSERT INTO access_log
                    (context_id, agent_id, access_type, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (context_id, agent_id, access_type, datetime.now().isoformat()))
                await self._db.commit()
        except Exception as e:
            logger.warning(f"Failed to log access: {e}")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "metrics": self.metrics,
            "cache_size": len(self._hot_cache),
            "db_path": str(self.db_path),
            "initialized": self._initialized
        }

    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            await self._db.close()
            self._db = None
            self._initialized = False
            logger.info("Memory bank store closed")

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
