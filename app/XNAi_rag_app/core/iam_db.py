#!/usr/bin/env python3
"""
IAM Database Module - Agent Identity Persistence
================================================
SQLite persistent storage for agent identities (DIDs, public keys).
Supports Ed25519 key management for sovereign handshakes.

Pattern: Sovereign Identity Management (Phase 4.2.6)
Version: 1.0.0
"""

import os
import sqlite3
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Agent types in the system"""
    COPILOT = "copilot"
    GEMINI = "gemini"
    CLAUDE = "claude"
    CLINE = "cline"
    SERVICE = "service"


@dataclass
class AgentIdentity:
    """Agent identity model with DID and public keys"""
    did: str
    agent_name: str
    agent_type: AgentType
    public_key_ed25519: str
    metadata: Dict[str, Any]
    created_at: str
    last_seen: Optional[str] = None
    verified: bool = False
    controller_did: Optional[str] = None
    relationship_type: str = "owner"
    auth_key_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "did": self.did,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type.value,
            "public_key_ed25519": self.public_key_ed25519,
            "metadata": json.dumps(self.metadata),
            "created_at": self.created_at,
            "last_seen": self.last_seen,
            "verified": int(self.verified),
            "controller_did": self.controller_did,
            "relationship_type": self.relationship_type,
            "auth_key_id": self.auth_key_id
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> 'AgentIdentity':
        """Create from database row"""
        return cls(
            did=row["did"],
            agent_name=row["agent_name"],
            agent_type=AgentType(row["agent_type"]),
            public_key_ed25519=row["public_key_ed25519"],
            metadata=json.loads(row["metadata"]),
            created_at=row["created_at"],
            last_seen=row.get("last_seen"),
            verified=bool(row["verified"]),
            controller_did=row.get("controller_did"),
            relationship_type=row.get("relationship_type", "owner"),
            auth_key_id=row.get("auth_key_id")
        )


class IAMDatabase:
    """
    SQLite persistent storage for agent identities.
    Alignment: Sovereign, Zero-Telemetry, Low-Memory.
    """

    def __init__(self, db_path: str = None):
        """Initialize IAM database"""
        self.db_path = db_path or os.getenv("IAM_AGENTS_DB_PATH", "data/iam_agents.db")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        
        # Initialize database with WAL mode
        self.conn = sqlite3.connect(
            self.db_path,
            isolation_level=None,
            check_same_thread=False
        )
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.execute("PRAGMA mmap_size=268435456;")  # 256MB MMAP for Ryzen
        
        self._initialize_schema()
        logger.info(f"IAM database initialized at {self.db_path}")

    def _initialize_schema(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()
        
        # Agent identities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_identities (
                did TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                public_key_ed25519 TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_seen TEXT,
                verified INTEGER DEFAULT 0,
                controller_did TEXT,
                relationship_type TEXT DEFAULT 'owner',
                auth_key_id TEXT
            )
        """)

        # Add columns if they don't exist (for existing DBs)
        try:
            cursor.execute("ALTER TABLE agent_identities ADD COLUMN controller_did TEXT")
        except sqlite3.OperationalError: pass
        try:
            cursor.execute("ALTER TABLE agent_identities ADD COLUMN relationship_type TEXT DEFAULT 'owner'")
        except sqlite3.OperationalError: pass
        try:
            cursor.execute("ALTER TABLE agent_identities ADD COLUMN auth_key_id TEXT")
        except sqlite3.OperationalError: pass
        
        # Create indices for efficient queries
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_name_type
            ON agent_identities(agent_name, agent_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_type
            ON agent_identities(agent_type)
        """)
        
        self.conn.commit()
        logger.debug("Agent identities schema initialized")

    def register_agent(self, identity: AgentIdentity) -> bool:
        """Register a new agent identity"""
        try:
            cursor = self.conn.cursor()
            data = identity.to_dict()
            
            cursor.execute("""
                INSERT INTO agent_identities
                (did, agent_name, agent_type, public_key_ed25519, metadata, created_at, last_seen, verified,
                 controller_did, relationship_type, auth_key_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["did"],
                data["agent_name"],
                data["agent_type"],
                data["public_key_ed25519"],
                data["metadata"],
                data["created_at"],
                data["last_seen"],
                data["verified"],
                data["controller_did"],
                data["relationship_type"],
                data["auth_key_id"]
            ))
            
            self.conn.commit()
            logger.info(f"Agent registered: {identity.did} ({identity.agent_name})")
            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to register agent {identity.did}: {e}")
            return False

    def get_agent(self, did: str) -> Optional[AgentIdentity]:
        """Retrieve agent by DID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT did, agent_name, agent_type, public_key_ed25519, metadata, created_at, last_seen, verified,
                   controller_did, relationship_type, auth_key_id
            FROM agent_identities
            WHERE did = ?
        """, (did,))
        
        row = cursor.fetchone()
        if row:
            return AgentIdentity.from_row({
                "did": row[0],
                "agent_name": row[1],
                "agent_type": row[2],
                "public_key_ed25519": row[3],
                "metadata": row[4],
                "created_at": row[5],
                "last_seen": row[6],
                "verified": row[7],
                "controller_did": row[8],
                "relationship_type": row[9],
                "auth_key_id": row[10]
            })
        return None

    def get_agent_by_name(self, agent_name: str, agent_type: AgentType) -> Optional[AgentIdentity]:
        """Retrieve agent by name and type"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT did, agent_name, agent_type, public_key_ed25519, metadata, created_at, last_seen, verified,
                   controller_did, relationship_type, auth_key_id
            FROM agent_identities
            WHERE agent_name = ? AND agent_type = ?
        """, (agent_name, agent_type.value))
        
        row = cursor.fetchone()
        if row:
            return AgentIdentity.from_row({
                "did": row[0],
                "agent_name": row[1],
                "agent_type": row[2],
                "public_key_ed25519": row[3],
                "metadata": row[4],
                "created_at": row[5],
                "last_seen": row[6],
                "verified": row[7],
                "controller_did": row[8],
                "relationship_type": row[9],
                "auth_key_id": row[10]
            })
        return None

    def list_agents(self, agent_type: Optional[AgentType] = None) -> List[AgentIdentity]:
        """List all agents, optionally filtered by type"""
        cursor = self.conn.cursor()
        
        if agent_type:
            cursor.execute("""
                SELECT did, agent_name, agent_type, public_key_ed25519, metadata, created_at, last_seen, verified,
                       controller_did, relationship_type, auth_key_id
                FROM agent_identities
                WHERE agent_type = ?
                ORDER BY created_at DESC
            """, (agent_type.value,))
        else:
            cursor.execute("""
                SELECT did, agent_name, agent_type, public_key_ed25519, metadata, created_at, last_seen, verified,
                       controller_did, relationship_type, auth_key_id
                FROM agent_identities
                ORDER BY created_at DESC
            """)
        
        agents = []
        for row in cursor.fetchall():
            agents.append(AgentIdentity.from_row({
                "did": row[0],
                "agent_name": row[1],
                "agent_type": row[2],
                "public_key_ed25519": row[3],
                "metadata": row[4],
                "created_at": row[5],
                "last_seen": row[6],
                "verified": row[7],
                "controller_did": row[8],
                "relationship_type": row[9],
                "auth_key_id": row[10]
            }))
        return agents

    def update_agent_verification(self, did: str, verified: bool) -> bool:
        """Update agent verification status"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE agent_identities
                SET verified = ?, last_seen = ?
                WHERE did = ?
            """, (int(verified), datetime.now(timezone.utc).isoformat(), did))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update verification for {did}: {e}")
            return False

    def update_agent_last_seen(self, did: str) -> bool:
        """Update last seen timestamp"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE agent_identities
                SET last_seen = ?
                WHERE did = ?
            """, (datetime.now(timezone.utc).isoformat(), did))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update last_seen for {did}: {e}")
            return False

    def delete_agent(self, did: str) -> bool:
        """Delete an agent identity"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM agent_identities WHERE did = ?", (did,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete agent {did}: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Global instance for easy access
_iam_db: Optional[IAMDatabase] = None

def get_iam_database(db_path: str = None) -> IAMDatabase:
    """Get or create global IAM database instance"""
    global _iam_db
    if _iam_db is None:
        _iam_db = IAMDatabase(db_path)
    return _iam_db
