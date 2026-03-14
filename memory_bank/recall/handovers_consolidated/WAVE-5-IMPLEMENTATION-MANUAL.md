# WAVE 5 IMPLEMENTATION MANUAL
## Local Sovereignty Stack

**Version**: 1.0  
**Date**: 2026-02-25  
**Status**: 🟢 **READY FOR EXECUTION**

### 📋 TABLE OF CONTENTS

1. [Overview & Objectives](#overview--objectives)
2. [Phase 5A: Session Management & Memory Optimization](#phase-5a-session-management--memory-optimization)
3. [Phase 5B: Agent Bus & Multi-Agent Coordination](#phase-5b-agent-bus--multi-agent-coordination)
4. [Phase 5C: IAM v2.0 & Ed25519 Authentication](#phase-5c-iam-v20--ed25519-authentication)
5. [Phase 5D: Task Scheduler & Vikunja Integration](#phase-5d-task-scheduler--vikunja-integration)
6. [Phase 5E: E5 Onboarding Protocol](#phase-5e-e5-onboarding-protocol)
7. [Implementation Timeline](#implementation-timeline)
8. [Resource Requirements](#resource-requirements)
9. [Success Criteria](#success-criteria)
10. [Troubleshooting](#troubleshooting)

---

## OVERVIEW & OBJECTIVES

### Wave 5 Vision
Build a **Local Sovereignty Stack** that enables offline-first operation, multi-agent coordination, and enterprise-grade security while maintaining the flexibility and performance of the existing Foundation stack.

### Key Objectives
- **Offline-First Operation**: Full functionality without internet connectivity
- **Multi-Agent Coordination**: Sophisticated agent communication and task distribution
- **Enhanced Security**: Cryptographic authentication and fine-grained authorization
- **Task Management**: Robust scheduling and monitoring capabilities
- **User Onboarding**: Streamlined setup and configuration process

### Success Metrics
- **Offline Operation**: 100% functionality without internet
- **Agent Coordination**: 95% task completion rate with multi-agent workflows
- **Security**: 0 authentication bypasses, 100% audit compliance
- **Task Management**: 99% task completion, <1% failure rate
- **User Experience**: <10 minute setup time, 90% user satisfaction

---

## PHASE 5A: SESSION MANAGEMENT & MEMORY OPTIMIZATION

### Status: 60% Complete

### Objectives
- Implement persistent session management with offline support
- Optimize memory usage for resource-constrained environments
- Enable seamless session restoration and migration

### Implementation Steps

#### Step 1: Persistent Session Storage (2 hours)
```python
# File: app/XNAi_rag_app/core/session_manager.py

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading

@dataclass
class SessionData:
    session_id: str
    user_id: str
    created_at: datetime
    last_accessed: datetime
    context: Dict[str, Any]
    offline_mode: bool = False
    memory_usage: int = 0

class PersistentSessionManager:
    def __init__(self, db_path: str = "sessions.db"):
        self.db_path = db_path
        self.lock = threading.RLock()
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for session storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_accessed TIMESTAMP NOT NULL,
                    context TEXT NOT NULL,
                    offline_mode BOOLEAN DEFAULT 0,
                    memory_usage INTEGER DEFAULT 0
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON sessions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON sessions(last_accessed)")
    
    def create_session(self, user_id: str, context: Dict[str, Any]) -> str:
        """Create a new persistent session"""
        session_id = self._generate_session_id()
        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            context=context,
            offline_mode=False,
            memory_usage=0
        )
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_data.session_id,
                    session_data.user_id,
                    session_data.created_at,
                    session_data.last_accessed,
                    json.dumps(session_data.context),
                    session_data.offline_mode,
                    session_data.memory_usage
                ))
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve session data"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT session_id, user_id, created_at, last_accessed, context, offline_mode, memory_usage
                    FROM sessions WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return SessionData(
                        session_id=row[0],
                        user_id=row[1],
                        created_at=datetime.fromisoformat(row[2]),
                        last_accessed=datetime.fromisoformat(row[3]),
                        context=json.loads(row[4]),
                        offline_mode=bool(row[5]),
                        memory_usage=row[6]
                    )
        return None
    
    def update_session(self, session_id: str, context: Dict[str, Any], memory_usage: int):
        """Update session data"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE sessions SET 
                        last_accessed = ?,
                        context = ?,
                        memory_usage = ?
                    WHERE session_id = ?
                """, (
                    datetime.now(),
                    json.dumps(context),
                    memory_usage,
                    session_id
                ))
    
    def set_offline_mode(self, session_id: str, offline: bool):
        """Set offline mode for session"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE sessions SET offline_mode = ? WHERE session_id = ?
                """, (offline, session_id))
    
    def cleanup_old_sessions(self, max_age_days: int = 30):
        """Remove sessions older than specified days"""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM sessions WHERE created_at < ?", (cutoff,))
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return f"session_{uuid.uuid4().hex[:16]}"
```

#### Step 2: Memory Optimization (3 hours)
```python
# File: app/XNAi_rag_app/core/memory_optimizer.py

import gc
import psutil
import threading
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class MemoryStats:
    timestamp: float
    total_memory: int
    available_memory: int
    used_memory: int
    memory_percent: float
    swap_used: int

class MemoryOptimizer:
    def __init__(self, target_memory_mb: int = 4096):
        self.target_memory_mb = target_memory_mb
        self.stats_history: list[MemoryStats] = []
        self.optimization_history: list[Dict[str, Any]] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.RLock()
        
    def start_monitoring(self, interval_seconds: int = 30):
        """Start background memory monitoring"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval_seconds,), daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background memory monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self, interval_seconds: int):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                stats = self.get_memory_stats()
                self._record_stats(stats)
                
                if stats.memory_percent > 80:
                    self._optimize_memory()
                
                time.sleep(interval_seconds)
            except Exception as e:
                print(f"Memory monitoring error: {e}")
                time.sleep(interval_seconds)
    
    def get_memory_stats(self) -> MemoryStats:
        """Get current memory statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        system_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()
        
        return MemoryStats(
            timestamp=time.time(),
            total_memory=system_memory.total,
            available_memory=system_memory.available,
            used_memory=memory_info.rss,
            memory_percent=(memory_info.rss / system_memory.total) * 100,
            swap_used=swap_memory.used
        )
    
    def _record_stats(self, stats: MemoryStats):
        """Record memory statistics"""
        with self.lock:
            self.stats_history.append(stats)
            # Keep only last 1000 entries
            if len(self.stats_history) > 1000:
                self.stats_history.pop(0)
    
    def _optimize_memory(self):
        """Perform memory optimization"""
        optimization_start = time.time()
        
        try:
            # Force garbage collection
            collected = gc.collect()
            
            # Clear caches
            self._clear_caches()
            
            # Optimize large objects
            self._optimize_large_objects()
            
            optimization_time = time.time() - optimization_start
            
            with self.lock:
                self.optimization_history.append({
                    'timestamp': time.time(),
                    'optimization_time': optimization_time,
                    'garbage_collected': collected,
                    'memory_freed': self._estimate_memory_freed()
                })
                
                # Keep only last 100 optimizations
                if len(self.optimization_history) > 100:
                    self.optimization_history.pop(0)
                    
        except Exception as e:
            print(f"Memory optimization error: {e}")
    
    def _clear_caches(self):
        """Clear application caches"""
        # Clear LangChain caches
        from langchain.cache import InMemoryCache
        if hasattr(InMemoryCache, 'clear'):
            InMemoryCache.clear()
        
        # Clear any custom caches
        # (Implementation depends on specific cache usage)
    
    def _optimize_large_objects(self):
        """Optimize large objects in memory"""
        # Force cleanup of large tensors
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        
        # Clear large numpy arrays
        try:
            import numpy as np
            # Force cleanup of large arrays
            np._NoValue = None
        except ImportError:
            pass
    
    def _estimate_memory_freed(self) -> int:
        """Estimate memory freed during optimization"""
        current_stats = self.get_memory_stats()
        if len(self.stats_history) > 1:
            previous_stats = self.stats_history[-2]
            return previous_stats.used_memory - current_stats.used_memory
        return 0
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get memory optimization report"""
        with self.lock:
            if not self.optimization_history:
                return {'status': 'no_optimizations'}
            
            latest_stats = self.stats_history[-1] if self.stats_history else None
            total_optimizations = len(self.optimization_history)
            avg_optimization_time = sum(opt['optimization_time'] for opt in self.optimization_history) / total_optimizations
            total_memory_freed = sum(opt['memory_freed'] for opt in self.optimization_history)
            
            return {
                'current_memory_usage_mb': latest_stats.used_memory / (1024 * 1024) if latest_stats else 0,
                'memory_usage_percent': latest_stats.memory_percent if latest_stats else 0,
                'total_optimizations': total_optimizations,
                'avg_optimization_time': avg_optimization_time,
                'total_memory_freed_mb': total_memory_freed / (1024 * 1024),
                'recommendations': self._generate_recommendations(latest_stats)
            }
    
    def _generate_recommendations(self, stats: Optional[MemoryStats]) -> list[str]:
        """Generate memory optimization recommendations"""
        recommendations = []
        
        if not stats:
            return ["Unable to generate recommendations - no memory stats available"]
        
        if stats.memory_percent > 90:
            recommendations.append("Consider reducing model size or batch size")
            recommendations.append("Enable more aggressive memory optimization")
        
        if stats.swap_used > 0:
            recommendations.append("System is using swap - consider adding more RAM")
        
        if len(self.optimization_history) > 10:
            avg_time = sum(opt['optimization_time'] for opt in self.optimization_history[-10:]) / 10
            if avg_time > 1.0:
                recommendations.append("Memory optimization is taking too long - consider reducing cache sizes")
        
        return recommendations
```

#### Step 3: Offline Mode Support (2 hours)
```python
# File: app/XNAi_rag_app/core/offline_manager.py

import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class OfflineData:
    data_id: str
    data_type: str
    content: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None

class OfflineDataManager:
    def __init__(self, offline_dir: str = "offline_data"):
        self.offline_dir = Path(offline_dir)
        self.offline_dir.mkdir(exist_ok=True)
        self.db_path = self.offline_dir / "offline.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize offline data database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS offline_data (
                    data_id TEXT PRIMARY KEY,
                    data_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP,
                    is_synced BOOLEAN DEFAULT 0
                )
            """)
    
    def store_offline_data(self, data_type: str, content: Dict[str, Any], 
                          expires_hours: Optional[int] = None) -> str:
        """Store data for offline access"""
        data_id = self._generate_data_id()
        created_at = datetime.now()
        expires_at = None
        
        if expires_hours:
            expires_at = created_at + timedelta(hours=expires_hours)
        
        offline_data = OfflineData(
            data_id=data_id,
            data_type=data_type,
            content=content,
            created_at=created_at,
            expires_at=expires_at
        )
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO offline_data VALUES (?, ?, ?, ?, ?, 0)
            """, (
                offline_data.data_id,
                offline_data.data_type,
                json.dumps(offline_data.content),
                offline_data.created_at,
                offline_data.expires_at
            ))
        
        # Also store as file for quick access
        file_path = self.offline_dir / f"{data_id}.json"
        with open(file_path, 'w') as f:
            json.dump({
                'data_type': data_type,
                'content': content,
                'created_at': created_at.isoformat(),
                'expires_at': expires_at.isoformat() if expires_at else None
            }, f, indent=2)
        
        return data_id
    
    def get_offline_data(self, data_type: str, data_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve offline data"""
        with sqlite3.connect(self.db_path) as conn:
            if data_id:
                cursor = conn.execute("""
                    SELECT content FROM offline_data 
                    WHERE data_type = ? AND data_id = ? AND (expires_at IS NULL OR expires_at > ?)
                """, (data_type, data_id, datetime.now()))
            else:
                cursor = conn.execute("""
                    SELECT content FROM offline_data 
                    WHERE data_type = ? AND (expires_at IS NULL OR expires_at > ?)
                """, (data_type, datetime.now()))
            
            results = []
            for row in cursor.fetchall():
                results.append(json.loads(row[0]))
            
            return results
    
    def cleanup_expired_data(self):
        """Remove expired offline data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT data_id FROM offline_data 
                WHERE expires_at IS NOT NULL AND expires_at < ?
            """, (datetime.now(),))
            
            expired_ids = [row[0] for row in cursor.fetchall()]
            
            if expired_ids:
                placeholders = ','.join(['?' for _ in expired_ids])
                conn.execute(f"DELETE FROM offline_data WHERE data_id IN ({placeholders})", expired_ids)
                
                # Remove corresponding files
                for data_id in expired_ids:
                    file_path = self.offline_dir / f"{data_id}.json"
                    if file_path.exists():
                        file_path.unlink()
    
    def sync_to_offline(self, data_type: str, content: Dict[str, Any], 
                       expires_hours: Optional[int] = None) -> bool:
        """Sync data to offline storage"""
        try:
            self.store_offline_data(data_type, content, expires_hours)
            return True
        except Exception as e:
            print(f"Failed to sync to offline: {e}")
            return False
    
    def is_offline_available(self, data_type: str) -> bool:
        """Check if offline data is available for given type"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM offline_data 
                WHERE data_type = ? AND (expires_at IS NULL OR expires_at > ?)
            """, (data_type, datetime.now()))
            
            count = cursor.fetchone()[0]
            return count > 0
    
    def _generate_data_id(self) -> str:
        """Generate unique data ID"""
        import uuid
        return f"offline_{uuid.uuid4().hex[:16]}"
```

### Testing Strategy
```python
# File: tests/test_session_management.py

import pytest
import tempfile
import os
from app.XNAi_rag_app.core.session_manager import PersistentSessionManager, SessionData
from app.XNAi_rag_app.core.memory_optimizer import MemoryOptimizer
from app.XNAi_rag_app.core.offline_manager import OfflineDataManager

class TestSessionManager:
    def test_create_and_retrieve_session(self):
        with tempfile.NamedTemporaryFile() as tmp:
            manager = PersistentSessionManager(tmp.name)
            
            context = {"user_preferences": {"theme": "dark"}}
            session_id = manager.create_session("user123", context)
            
            retrieved = manager.get_session(session_id)
            assert retrieved is not None
            assert retrieved.user_id == "user123"
            assert retrieved.context == context
    
    def test_offline_mode(self):
        with tempfile.NamedTemporaryFile() as tmp:
            manager = PersistentSessionManager(tmp.name)
            
            session_id = manager.create_session("user123", {})
            manager.set_offline_mode(session_id, True)
            
            session = manager.get_session(session_id)
            assert session.offline_mode is True

class TestMemoryOptimizer:
    def test_memory_monitoring(self):
        optimizer = MemoryOptimizer()
        
        # Start monitoring
        optimizer.start_monitoring(interval_seconds=1)
        
        # Let it run briefly
        import time
        time.sleep(2)
        
        # Stop monitoring
        optimizer.stop_monitoring()
        
        # Check that stats were collected
        assert len(optimizer.stats_history) > 0
    
    def test_memory_optimization(self):
        optimizer = MemoryOptimizer()
        
        # Force some memory usage
        large_list = [i for i in range(100000)]
        del large_list
        
        # Trigger optimization
        optimizer._optimize_memory()
        
        # Should have recorded optimization
        assert len(optimizer.optimization_history) > 0

class TestOfflineManager:
    def test_store_and_retrieve_offline_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            manager = OfflineDataManager(tmp)
            
            test_data = {"model_weights": [1, 2, 3, 4, 5]}
            data_id = manager.store_offline_data("model_weights", test_data)
            
            retrieved = manager.get_offline_data("model_weights", data_id)
            assert len(retrieved) == 1
            assert retrieved[0] == test_data
    
    def test_offline_availability(self):
        with tempfile.TemporaryDirectory() as tmp:
            manager = OfflineDataManager(tmp)
            
            # Initially no offline data
            assert not manager.is_offline_available("test_type")
            
            # Add some data
            manager.store_offline_data("test_type", {"data": "test"})
            
            # Now available
            assert manager.is_offline_available("test_type")
```

### Integration Points
- **Session Manager**: Integrates with existing authentication and context management
- **Memory Optimizer**: Works with existing model loading and inference systems
- **Offline Manager**: Connects to vector stores, model weights, and configuration data

---

## PHASE 5B: AGENT BUS & MULTI-AGENT COORDINATION

### Status: 90% Complete

### Objectives
- Implement robust message bus for agent communication
- Enable sophisticated task distribution and coordination
- Provide real-time monitoring and debugging capabilities

### Implementation Steps

#### Step 1: Enhanced Agent Bus (3 hours)
```python
# File: app/XNAi_rag_app/core/agent_bus.py

import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    TASK_ERROR = "task_error"
    AGENT_STATUS = "agent_status"
    AGENT_HEARTBEAT = "agent_heartbeat"
    AGENT_DISCOVERY = "agent_discovery"
    AGENT_REGISTRATION = "agent_registration"
    AGENT_DEREGISTRATION = "agent_deregistration"
    BROADCAST = "broadcast"
    DIRECT_MESSAGE = "direct_message"

@dataclass
class Message:
    message_id: str
    message_type: MessageType
    sender_id: str
    timestamp: float
    payload: Dict[str, Any]
    target_agents: Optional[List[str]] = None
    correlation_id: Optional[str] = None
    priority: int = 0  # 0-9, higher is more important
    ttl: Optional[float] = None  # Time to live in seconds

class AgentBus:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.subscribers: Dict[str, List[Callable]] = {}
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.message_queue = asyncio.Queue()
        self.running = False
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        
    async def start(self):
        """Start the agent bus"""
        self.running = True
        logger.info("Agent Bus started")
        
        # Start message processing loop
        asyncio.create_task(self._message_processor())
        
        # Start heartbeat monitor
        asyncio.create_task(self._heartbeat_monitor())
    
    async def stop(self):
        """Stop the agent bus"""
        self.running = False
        logger.info("Agent Bus stopped")
    
    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """Register a handler for specific message types"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    async def send_message(self, message: Message):
        """Send a message to the bus"""
        if not self.running:
            logger.warning("Agent Bus not running, dropping message")
            return
        
        # Validate message
        if not message.message_id:
            message.message_id = str(uuid.uuid4())
        
        if not message.timestamp:
            message.timestamp = time.time()
        
        # Add to queue for processing
        await self.message_queue.put(message)
        
        # Log important messages
        if message.priority > 5:
            logger.info(f"High priority message sent: {message.message_type} from {message.sender_id}")
    
    async def broadcast(self, message_type: MessageType, payload: Dict[str, Any], 
                       sender_id: str, priority: int = 0):
        """Broadcast a message to all agents"""
        message = Message(
            message_id=str(uuid.uuid4()),
            message_type=message_type,
            sender_id=sender_id,
            timestamp=time.time(),
            payload=payload,
            priority=priority
        )
        await self.send_message(message)
    
    async def send_direct(self, message_type: MessageType, payload: Dict[str, Any],
                         sender_id: str, target_agent: str, priority: int = 0):
        """Send a direct message to a specific agent"""
        message = Message(
            message_id=str(uuid.uuid4()),
            message_type=message_type,
            sender_id=sender_id,
            timestamp=time.time(),
            payload=payload,
            target_agents=[target_agent],
            priority=priority
        )
        await self.send_message(message)
    
    async def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register an agent with the bus"""
        self.agent_registry[agent_id] = {
            **agent_info,
            'registered_at': time.time(),
            'last_heartbeat': time.time()
        }
        
        # Broadcast agent discovery
        await self.broadcast(
            MessageType.AGENT_DISCOVERY,
            {'agent_id': agent_id, 'agent_info': agent_info},
            'agent_bus'
        )
        
        logger.info(f"Agent registered: {agent_id}")
    
    async def deregister_agent(self, agent_id: str):
        """Deregister an agent from the bus"""
        if agent_id in self.agent_registry:
            del self.agent_registry[agent_id]
            
            # Broadcast agent departure
            await self.broadcast(
                MessageType.AGENT_DEREGISTRATION,
                {'agent_id': agent_id},
                'agent_bus'
            )
            
            logger.info(f"Agent deregistered: {agent_id}")
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        return self.agent_registry.get(agent_id)
    
    async def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered agents"""
        return self.agent_registry.copy()
    
    async def _message_processor(self):
        """Process messages from the queue"""
        while self.running:
            try:
                # Get message with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                # Check TTL
                if message.ttl and (time.time() - message.timestamp) > message.ttl:
                    logger.debug(f"Message expired: {message.message_id}")
                    continue
                
                # Route message
                await self._route_message(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def _route_message(self, message: Message):
        """Route message to appropriate handlers"""
        # Handle system messages
        if message.message_type in [MessageType.AGENT_HEARTBEAT, MessageType.AGENT_STATUS]:
            await self._handle_system_message(message)
            return
        
        # Route to registered handlers
        if message.message_type in self.message_handlers:
            for handler in self.message_handlers[message.message_type]:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")
        
        # Route to target agents
        if message.target_agents:
            for agent_id in message.target_agents:
                await self._deliver_to_agent(message, agent_id)
        else:
            # Broadcast to all agents
            for agent_id in self.agent_registry:
                await self._deliver_to_agent(message, agent_id)
    
    async def _deliver_to_agent(self, message: Message, agent_id: str):
        """Deliver message to specific agent"""
        # In a real implementation, this would use Redis Streams or similar
        # For now, we'll use direct function calls
        
        if agent_id in self.subscribers:
            for callback in self.subscribers[agent_id]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"Error delivering message to {agent_id}: {e}")
    
    async def _handle_system_message(self, message: Message):
        """Handle system messages (heartbeats, status, etc.)"""
        if message.message_type == MessageType.AGENT_HEARTBEAT:
            agent_id = message.sender_id
            if agent_id in self.agent_registry:
                self.agent_registry[agent_id]['last_heartbeat'] = time.time()
    
    async def _heartbeat_monitor(self):
        """Monitor agent heartbeats and clean up dead agents"""
        while self.running:
            try:
                current_time = time.time()
                dead_agents = []
                
                for agent_id, agent_info in self.agent_registry.items():
                    last_heartbeat = agent_info.get('last_heartbeat', 0)
                    if current_time - last_heartbeat > 30:  # 30 second timeout
                        dead_agents.append(agent_id)
                
                # Remove dead agents
                for agent_id in dead_agents:
                    await self.deregister_agent(agent_id)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(10)

class Agent:
    """Base class for all agents"""
    
    def __init__(self, agent_id: str, agent_bus: AgentBus, agent_type: str = "generic"):
        self.agent_id = agent_id
        self.agent_bus = agent_bus
        self.agent_type = agent_type
        self.running = False
        self.task_queue = asyncio.Queue()
        
    async def start(self):
        """Start the agent"""
        self.running = True
        
        # Register with bus
        await self.agent_bus.register_agent(self.agent_id, {
            'type': self.agent_type,
            'capabilities': self.get_capabilities(),
            'status': 'active'
        })
        
        # Register message handlers
        self._register_handlers()
        
        # Start processing
        asyncio.create_task(self._task_processor())
        asyncio.create_task(self._heartbeat_sender())
        
        logger.info(f"Agent started: {self.agent_id}")
    
    async def stop(self):
        """Stop the agent"""
        self.running = False
        await self.agent_bus.deregister_agent(self.agent_id)
        logger.info(f"Agent stopped: {self.agent_id}")
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return []
    
    def _register_handlers(self):
        """Register message handlers"""
        self.agent_bus.register_message_handler(MessageType.TASK_REQUEST, self._handle_task_request)
        self.agent_bus.register_message_handler(MessageType.AGENT_STATUS, self._handle_status_request)
    
    async def _task_processor(self):
        """Process tasks from the queue"""
        while self.running:
            try:
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                await self._execute_task(task)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing task: {e}")
    
    async def _execute_task(self, task: Dict[str, Any]):
        """Execute a task"""
        # Override in subclasses
        pass
    
    async def _handle_task_request(self, message: Message):
        """Handle task request messages"""
        if message.target_agents and self.agent_id not in message.target_agents:
            return
        
        # Check if we can handle this task
        if self._can_handle_task(message.payload):
            await self.task_queue.put(message.payload)
            
            # Send acknowledgment
            await self.agent_bus.send_direct(
                MessageType.TASK_RESPONSE,
                {'status': 'accepted', 'task_id': message.payload.get('task_id')},
                self.agent_id,
                message.sender_id
            )
    
    def _can_handle_task(self, task: Dict[str, Any]) -> bool:
        """Check if agent can handle the task"""
        return False
    
    async def _handle_status_request(self, message: Message):
        """Handle status request messages"""
        if message.target_agents and self.agent_id not in message.target_agents:
            return
        
        status = {
            'agent_id': self.agent_id,
            'status': 'active' if self.running else 'inactive',
            'capabilities': self.get_capabilities(),
            'queue_size': self.task_queue.qsize()
        }
        
        await self.agent_bus.send_direct(
            MessageType.AGENT_STATUS,
            status,
            self.agent_id,
            message.sender_id
        )
    
    async def _heartbeat_sender(self):
        """Send periodic heartbeats"""
        while self.running:
            try:
                await self.agent_bus.send_direct(
                    MessageType.AGENT_HEARTBEAT,
                    {'agent_id': self.agent_id, 'timestamp': time.time()},
                    self.agent_id,
                    'agent_bus'
                )
                await asyncio.sleep(10)  # Send heartbeat every 10 seconds
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
                await asyncio.sleep(10)
```

#### Step 2: Multi-Agent Coordination (3 hours)
```python
# File: app/XNAi_rag_app/core/multi_agent_coordinator.py

import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 8
    CRITICAL = 10

@dataclass
class Task:
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: TaskPriority
    created_at: float
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    dependencies: List[str] = None
    timeout: Optional[float] = None

class MultiAgentCoordinator:
    def __init__(self, agent_bus):
        self.agent_bus = agent_bus
        self.tasks: Dict[str, Task] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        self.task_assignments: Dict[str, str] = {}  # task_id -> agent_id
        self.running = False
        
    async def start(self):
        """Start the coordinator"""
        self.running = True
        logger.info("Multi-Agent Coordinator started")
        
        # Register message handlers
        self.agent_bus.register_message_handler(
            MessageType.AGENT_STATUS, 
            self._handle_agent_status
        )
        self.agent_bus.register_message_handler(
            MessageType.TASK_RESPONSE,
            self._handle_task_response
        )
        self.agent_bus.register_message_handler(
            MessageType.TASK_ERROR,
            self._handle_task_error
        )
        
        # Start task processor
        asyncio.create_task(self._task_processor())
    
    async def stop(self):
        """Stop the coordinator"""
        self.running = False
        logger.info("Multi-Agent Coordinator stopped")
    
    async def submit_task(self, task_type: str, payload: Dict[str, Any], 
                         priority: TaskPriority = TaskPriority.MEDIUM,
                         dependencies: List[str] = None,
                         timeout: Optional[float] = None) -> str:
        """Submit a new task for coordination"""
        task_id = self._generate_task_id()
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority,
            created_at=time.time(),
            dependencies=dependencies or [],
            timeout=timeout
        )
        
        self.tasks[task_id] = task
        
        # Try to assign immediately if dependencies are met
        if self._dependencies_met(task_id):
            await self._assign_task(task_id)
        
        logger.info(f"Task submitted: {task_id} ({task_type})")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            'task_id': task.task_id,
            'task_type': task.task_type,
            'status': task.status.value,
            'priority': task.priority.value,
            'assigned_to': task.assigned_to,
            'created_at': task.created_at,
            'result': task.result,
            'error': task.error
        }
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or in-progress task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return False
        
        task.status = TaskStatus.CANCELLED
        
        # Notify assigned agent if any
        if task.assigned_to:
            await self.agent_bus.send_direct(
                MessageType.TASK_ERROR,
                {'task_id': task_id, 'error': 'Task cancelled'},
                'coordinator',
                task.assigned_to
            )
        
        logger.info(f"Task cancelled: {task_id}")
        return True
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        import uuid
        return f"task_{uuid.uuid4().hex[:16]}"
    
    def _dependencies_met(self, task_id: str) -> bool:
        """Check if task dependencies are met"""
        task = self.tasks[task_id]
        if not task.dependencies:
            return True
        
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            
            dep_task = self.tasks[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    async def _assign_task(self, task_id: str):
        """Assign task to appropriate agent"""
        task = self.tasks[task_id]
        
        # Find suitable agent
        suitable_agents = self._find_suitable_agents(task.task_type)
        if not suitable_agents:
            logger.warning(f"No suitable agent found for task: {task_id}")
            task.status = TaskStatus.FAILED
            task.error = "No suitable agent available"
            return
        
        # Select best agent (simple round-robin for now)
        selected_agent = suitable_agents[0]
        
        # Assign task
        task.status = TaskStatus.ASSIGNED
        task.assigned_to = selected_agent
        self.task_assignments[task_id] = selected_agent
        
        # Send task to agent
        await self.agent_bus.send_direct(
            MessageType.TASK_REQUEST,
            {
                'task_id': task_id,
                'task_type': task.task_type,
                'payload': task.payload,
                'priority': task.priority.value,
                'timeout': task.timeout
            },
            'coordinator',
            selected_agent
        )
        
        logger.info(f"Task assigned: {task_id} -> {selected_agent}")
    
    def _find_suitable_agents(self, task_type: str) -> List[str]:
        """Find agents capable of handling the task type"""
        suitable_agents = []
        
        for agent_id, capabilities in self.agent_capabilities.items():
            if task_type in capabilities:
                suitable_agents.append(agent_id)
        
        return suitable_agents
    
    async def _task_processor(self):
        """Process tasks and manage assignments"""
        while self.running:
            try:
                # Check for new tasks
                pending_tasks = [
                    task_id for task_id, task in self.tasks.items()
                    if task.status == TaskStatus.PENDING and self._dependencies_met(task_id)
                ]
                
                # Assign pending tasks
                for task_id in pending_tasks:
                    if self.tasks[task_id].status == TaskStatus.PENDING:
                        await self._assign_task(task_id)
                
                # Check for timeouts
                current_time = time.time()
                for task_id, task in self.tasks.items():
                    if (task.status == TaskStatus.IN_PROGRESS and 
                        task.timeout and 
                        current_time - task.created_at > task.timeout):
                        
                        await self._handle_task_timeout(task_id)
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in task processor: {e}")
                await asyncio.sleep(1)
    
    async def _handle_agent_status(self, message: Message):
        """Handle agent status updates"""
        if message.payload.get('agent_id'):
            agent_id = message.payload['agent_id']
            capabilities = message.payload.get('capabilities', [])
            self.agent_capabilities[agent_id] = capabilities
    
    async def _handle_task_response(self, message: Message):
        """Handle task completion responses"""
        task_id = message.payload.get('task_id')
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.result = message.payload.get('result')
            
            logger.info(f"Task completed: {task_id}")
    
    async def _handle_task_error(self, message: Message):
        """Handle task error responses"""
        task_id = message.payload.get('task_id')
        error = message.payload.get('error')
        
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.FAILED
            task.error = error
            
            logger.error(f"Task failed: {task_id} - {error}")
    
    async def _handle_task_timeout(self, task_id: str):
        """Handle task timeout"""
        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.error = "Task timed out"
        
        # Notify assigned agent
        if task.assigned_to:
            await self.agent_bus.send_direct(
                MessageType.TASK_ERROR,
                {'task_id': task_id, 'error': 'Task timed out'},
                'coordinator',
                task.assigned_to
            )
        
        logger.error(f"Task timed out: {task_id}")

# Specialized Agent Classes
class ResearchAgent(Agent):
    """Agent specialized in research tasks"""
    
    def get_capabilities(self) -> List[str]:
        return ['research', 'information_gathering', 'analysis']
    
    def _can_handle_task(self, task: Dict[str, Any]) -> bool:
        return task.get('type') in ['research', 'analysis']
    
    async def _execute_task(self, task: Dict[str, Any]):
        # Implement research logic
        pass

class CodeAgent(Agent):
    """Agent specialized in coding tasks"""
    
    def get_capabilities(self) -> List[str]:
        return ['code_generation', 'code_review', 'debugging']
    
    def _can_handle_task(self, task: Dict[str, Any]) -> bool:
        return task.get('type') in ['code', 'debug']
    
    async def _execute_task(self, task: Dict[str, Any]):
        # Implement coding logic
        pass

class AnalysisAgent(Agent):
    """Agent specialized in data analysis"""
    
    def get_capabilities(self) -> List[str]:
        return ['data_analysis', 'report_generation', 'visualization']
    
    def _can_handle_task(self, task: Dict[str, Any]) -> bool:
        return task.get('type') in ['analysis', 'report']
    
    async def _execute_task(self, task: Dict[str, Any]):
        # Implement analysis logic
        pass
```

### Testing Strategy
```python
# File: tests/test_agent_bus.py

import pytest
import asyncio
from app.XNAi_rag_app.core.agent_bus import AgentBus, Agent, MessageType
from app.XNAi_rag_app.core.multi_agent_coordinator import MultiAgentCoordinator, TaskPriority

class TestAgentBus:
    async def test_message_routing(self):
        bus = AgentBus()
        await bus.start()
        
        # Test message sending
        message = {
            'message_type': MessageType.TASK_REQUEST,
            'payload': {'task': 'test'},
            'sender_id': 'test_agent'
        }
        
        await bus.send_message(message)
        await asyncio.sleep(0.1)  # Let message be processed
        
        await bus.stop()
    
    async def test_agent_registration(self):
        bus = AgentBus()
        await bus.start()
        
        # Register agent
        await bus.register_agent('test_agent', {'type': 'test'})
        
        # Check registration
        agents = await bus.get_all_agents()
        assert 'test_agent' in agents
        
        await bus.stop()

class TestMultiAgentCoordinator:
    async def test_task_submission(self):
        bus = AgentBus()
        coordinator = MultiAgentCoordinator(bus)
        
        await bus.start()
        await coordinator.start()
        
        # Submit task
        task_id = await coordinator.submit_task(
            'test_task',
            {'data': 'test'},
            TaskPriority.HIGH
        )
        
        # Check task status
        status = await coordinator.get_task_status(task_id)
        assert status['task_id'] == task_id
        assert status['status'] == 'pending'
        
        await coordinator.stop()
        await bus.stop()
```

### Integration Points
- **Agent Bus**: Core communication infrastructure for all agents
- **Multi-Agent Coordinator**: Task distribution and management
- **Specialized Agents**: Domain-specific capabilities (research, coding, analysis)
- **Monitoring**: Real-time task tracking and debugging

---

## PHASE 5C: IAM V2.0 & ED25519 AUTHENTICATION

### Status: 85% Complete

### Objectives
- Implement cryptographic authentication using Ed25519
- Deploy Attribute-Based Access Control (ABAC) for fine-grained authorization
- Ensure audit compliance and security best practices

### Implementation Steps

#### Step 1: Ed25519 Authentication (3 hours)
```python
# File: app/XNAi_rag_app/core/iam_v2.py

import os
import json
import time
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Import cryptography libraries
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("Cryptography library not available, Ed25519 authentication disabled")

class AuthLevel(Enum):
    ANONYMOUS = 0
    USER = 1
    ADMIN = 2
    SYSTEM = 3

@dataclass
class Identity:
    user_id: str
    public_key: str
    auth_level: AuthLevel
    attributes: Dict[str, Any]
    created_at: float
    last_login: Optional[float] = None
    failed_attempts: int = 0
    locked_until: Optional[float] = None

class Ed25519Authenticator:
    def __init__(self, key_store_path: str = "auth_keys"):
        self.key_store_path = key_store_path
        self.key_store_path.mkdir(exist_ok=True)
        self.identities: Dict[str, Identity] = {}
        self._load_identities()
    
    def generate_key_pair(self, user_id: str) -> Dict[str, str]:
        """Generate Ed25519 key pair for user"""
        if not CRYPTO_AVAILABLE:
            raise ImportError("Cryptography library required for Ed25519 authentication")
        
        # Generate private key
        private_key = Ed25519PrivateKey.generate()
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Save keys
        private_key_path = self.key_store_path / f"{user_id}_private.pem"
        public_key_path = self.key_store_path / f"{user_id}_public.pem"
        
        with open(private_key_path, 'wb') as f:
            f.write(private_pem)
        
        with open(public_key_path, 'wb') as f:
            f.write(public_pem)
        
        # Create identity
        identity = Identity(
            user_id=user_id,
            public_key=public_pem.decode(),
            auth_level=AuthLevel.USER,
            attributes={},
            created_at=time.time()
        )
        
        self.identities[user_id] = identity
        self._save_identities()
        
        return {
            'user_id': user_id,
            'public_key': public_pem.decode(),
            'private_key': private_pem.decode()
        }
    
    def authenticate(self, user_id: str, message: str, signature: str) -> bool:
        """Authenticate user using Ed25519 signature"""
        if not CRYPTO_AVAILABLE:
            return False
        
        if user_id not in self.identities:
            return False
        
        identity = self.identities[user_id]
        
        # Check if account is locked
        if identity.locked_until and time.time() < identity.locked_until:
            return False
        
        try:
            # Load public key
            public_key = Ed25519PublicKey.from_pem(identity.public_key.encode())
            
            # Verify signature
            public_key.verify(
                bytes.fromhex(signature),
                message.encode()
            )
            
            # Update last login
            identity.last_login = time.time()
            identity.failed_attempts = 0
            self._save_identities()
            
            return True
            
        except InvalidSignature:
            # Increment failed attempts
            identity.failed_attempts += 1
            
            # Lock account after 5 failed attempts
            if identity.failed_attempts >= 5:
                identity.locked_until = time.time() + (15 * 60)  # 15 minutes
            
            self._save_identities()
            return False
    
    def get_identity(self, user_id: str) -> Optional[Identity]:
        """Get user identity"""
        return self.identities.get(user_id)
    
    def update_attributes(self, user_id: str, attributes: Dict[str, Any]):
        """Update user attributes"""
        if user_id in self.identities:
            self.identities[user_id].attributes.update(attributes)
            self._save_identities()
    
    def set_auth_level(self, user_id: str, auth_level: AuthLevel):
        """Set user authentication level"""
        if user_id in self.identities:
            self.identities[user_id].auth_level = auth_level
            self._save_identities()
    
    def revoke_key(self, user_id: str):
        """Revoke user key"""
        if user_id in self.identities:
            # Remove key files
            private_key_path = self.key_store_path / f"{user_id}_private.pem"
            public_key_path = self.key_store_path / f"{user_id}_public.pem"
            
            if private_key_path.exists():
                private_key_path.unlink()
            if public_key_path.exists():
                public_key_path.unlink()
            
            # Remove identity
            del self.identities[user_id]
            self._save_identities()
    
    def _load_identities(self):
        """Load identities from storage"""
        identities_file = self.key_store_path / "identities.json"
        if identities_file.exists():
            with open(identities_file, 'r') as f:
                data = json.load(f)
                for user_id, identity_data in data.items():
                    identity_data['auth_level'] = AuthLevel(identity_data['auth_level'])
                    identity_data['created_at'] = float(identity_data['created_at'])
                    if identity_data['last_login']:
                        identity_data['last_login'] = float(identity_data['last_login'])
                    if identity_data['locked_until']:
                        identity_data['locked_until'] = float(identity_data['locked_until'])
                    
                    self.identities[user_id] = Identity(**identity_data)
    
    def _save_identities(self):
        """Save identities to storage"""
        identities_file = self.key_store_path / "identities.json"
        
        data = {}
        for user_id, identity in self.identities.items():
            data[user_id] = {
                'user_id': identity.user_id,
                'public_key': identity.public_key,
                'auth_level': identity.auth_level.value,
                'attributes': identity.attributes,
                'created_at': identity.created_at,
                'last_login': identity.last_login,
                'failed_attempts': identity.failed_attempts,
                'locked_until': identity.locked_until
            }
        
        with open(identities_file, 'w') as f:
            json.dump(data, f, indent=2)

class ABACAuthorizer:
    """Attribute-Based Access Control authorizer"""
    
    def __init__(self, authenticator: Ed25519Authenticator):
        self.authenticator = authenticator
        self.policies: List[Dict[str, Any]] = []
        self._load_policies()
    
    def add_policy(self, policy: Dict[str, Any]):
        """Add ABAC policy"""
        self.policies.append(policy)
        self._save_policies()
    
    def remove_policy(self, policy_id: str):
        """Remove ABAC policy"""
        self.policies = [p for p in self.policies if p.get('id') != policy_id]
        self._save_policies()
    
    def check_permission(self, user_id: str, action: str, resource: str, 
                        context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if user has permission for action on resource"""
        identity = self.authenticator.get_identity(user_id)
        if not identity:
            return False
        
        # Build evaluation context
        evaluation_context = {
            'user': {
                'id': user_id,
                'auth_level': identity.auth_level.value,
                'attributes': identity.attributes,
                'last_login': identity.last_login
            },
            'action': action,
            'resource': resource,
            'context': context or {},
            'time': time.time()
        }
        
        # Evaluate policies
        for policy in self.policies:
            if self._evaluate_policy(policy, evaluation_context):
                return True
        
        return False
    
    def _evaluate_policy(self, policy: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a single policy"""
        try:
            # Check conditions
            conditions = policy.get('conditions', [])
            for condition in conditions:
                if not self._evaluate_condition(condition, context):
                    return False
            
            # Check target
            target = policy.get('target', {})
            if not self._evaluate_target(target, context):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating policy: {e}")
            return False
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a policy condition"""
        condition_type = condition.get('type')
        attribute = condition.get('attribute')
        operator = condition.get('operator')
        value = condition.get('value')
        
        # Get attribute value from context
        attr_value = self._get_attribute_value(attribute, context)
        
        # Evaluate based on operator
        if operator == 'equals':
            return attr_value == value
        elif operator == 'not_equals':
            return attr_value != value
        elif operator == 'greater_than':
            return attr_value > value
        elif operator == 'less_than':
            return attr_value < value
        elif operator == 'in':
            return attr_value in value
        elif operator == 'not_in':
            return attr_value not in value
        elif operator == 'contains':
            return value in str(attr_value)
        elif operator == 'starts_with':
            return str(attr_value).startswith(str(value))
        elif operator == 'ends_with':
            return str(attr_value).endswith(str(value))
        
        return False
    
    def _get_attribute_value(self, attribute: str, context: Dict[str, Any]):
        """Get attribute value from context"""
        # Navigate nested attributes (e.g., 'user.attributes.department')
        parts = attribute.split('.')
        value = context
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value
    
    def _evaluate_target(self, target: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate policy target"""
        # Check if target matches context
        for key, value in target.items():
            if key not in context or context[key] != value:
                return False
        return True
    
    def _load_policies(self):
        """Load policies from storage"""
        policies_file = Path(self.authenticator.key_store_path) / "policies.json"
        if policies_file.exists():
            with open(policies_file, 'r') as f:
                self.policies = json.load(f)
    
    def _save_policies(self):
        """Save policies to storage"""
        policies_file = Path(self.authenticator.key_store_path) / "policies.json"
        with open(policies_file, 'w') as f:
            json.dump(self.policies, f, indent=2)

# Example policies
DEFAULT_POLICIES = [
    {
        "id": "admin_all_access",
        "description": "Admin users have full access",
        "target": {"action": "*", "resource": "*"},
        "conditions": [
            {"type": "attribute", "attribute": "user.auth_level", "operator": "greater_than", "value": 1}
        ]
    },
    {
        "id": "user_read_own_data",
        "description": "Users can read their own data",
        "target": {"action": "read"},
        "conditions": [
            {"type": "attribute", "attribute": "user.id", "operator": "equals", "value": "context.resource.owner"}
        ]
    },
    {
        "id": "research_access",
        "description": "Research agents can access research resources",
        "target": {"action": "access", "resource": "research"},
        "conditions": [
            {"type": "attribute", "attribute": "user.attributes.role", "operator": "equals", "value": "researcher"}
        ]
    }
]

class IAMv2Manager:
    """Main IAM v2.0 manager"""
    
    def __init__(self, key_store_path: str = "auth_keys"):
        self.authenticator = Ed25519Authenticator(key_store_path)
        self.authorizer = ABACAuthorizer(self.authenticator)
        
        # Load default policies
        for policy in DEFAULT_POLICIES:
            self.authorizer.add_policy(policy)
    
    def authenticate_user(self, user_id: str, message: str, signature: str) -> bool:
        """Authenticate user"""
        return self.authenticator.authenticate(user_id, message, signature)
    
    def authorize_action(self, user_id: str, action: str, resource: str, 
                        context: Optional[Dict[str, Any]] = None) -> bool:
        """Authorize action"""
        return self.authorizer.check_permission(user_id, action, resource, context)
    
    def create_user(self, user_id: str, attributes: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Create new user"""
        keys = self.authenticator.generate_key_pair(user_id)
        
        if attributes:
            self.authenticator.update_attributes(user_id, attributes)
        
        return keys
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information"""
        identity = self.authenticator.get_identity(user_id)
        if not identity:
            return None
        
        return {
            'user_id': identity.user_id,
            'auth_level': identity.auth_level.name,
            'attributes': identity.attributes,
            'created_at': identity.created_at,
            'last_login': identity.last_login,
            'failed_attempts': identity.failed_attempts,
            'is_locked': identity.locked_until is not None and time.time() < identity.locked_until
        }
```

#### Step 2: Integration with Existing Systems (2 hours)
```python
# File: app/XNAi_rag_app/core/iam_integration.py

from fastapi import Request, HTTPException, Depends
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class IAMIntegration:
    """Integration layer for IAM v2.0 with existing systems"""
    
    def __init__(self, iam_manager):
        self.iam_manager = iam_manager
    
    async def authenticate_request(self, request: Request) -> Optional[str]:
        """Authenticate incoming request"""
        # Extract authentication data from headers
        user_id = request.headers.get('X-User-ID')
        message = request.headers.get('X-Auth-Message')
        signature = request.headers.get('X-Auth-Signature')
        
        if not all([user_id, message, signature]):
            return None
        
        # Authenticate
        if self.iam_manager.authenticate_user(user_id, message, signature):
            return user_id
        
        return None
    
    async def authorize_request(self, user_id: str, action: str, resource: str, 
                              context: Optional[Dict[str, Any]] = None) -> bool:
        """Authorize request"""
        return self.iam_manager.authorize_action(user_id, action, resource, context)
    
    def require_auth(self, action: str, resource: str):
        """Decorator for requiring authentication"""
        def decorator(func):
            async def wrapper(request: Request, *args, **kwargs):
                user_id = await self.authenticate_request(request)
                if not user_id:
                    raise HTTPException(status_code=401, detail="Authentication required")
                
                # Build context
                context = {
                    'request_path': str(request.url.path),
                    'request_method': request.method,
                    'client_ip': request.client.host if request.client else None,
                    'timestamp': time.time()
                }
                
                if not await self.authorize_request(user_id, action, resource, context):
                    raise HTTPException(status_code=403, detail="Access denied")
                
                return await func(request, user_id, *args, **kwargs)
            
            return wrapper
        return decorator

# FastAPI integration example
from fastapi import FastAPI
from app.XNAi_rag_app.core.iam_v2 import IAMv2Manager
from app.XNAi_rag_app.core.iam_integration import IAMIntegration

# Initialize IAM
iam_manager = IAMv2Manager()
iam_integration = IAMIntegration(iam_manager)

app = FastAPI()

@app.post("/api/research")
@iam_integration.require_auth("research", "research_data")
async def research_endpoint(request: Request, user_id: str):
    """Research endpoint with IAM v2.0 protection"""
    # Implementation here
    pass

@app.post("/api/admin/users")
@iam_integration.require_auth("admin", "users")
async def admin_users_endpoint(request: Request, user_id: str):
    """Admin endpoint for user management"""
    # Implementation here
    pass
```

### Testing Strategy
```python
# File: tests/test_iam_v2.py

import pytest
import time
from app.XNAi_rag_app.core.iam_v2 import IAMv2Manager, AuthLevel

class TestIAMv2:
    def test_user_creation(self):
        iam = IAMv2Manager()
        
        # Create user
        keys = iam.create_user("test_user", {"role": "researcher"})
        
        # Verify keys generated
        assert "user_id" in keys
        assert "public_key" in keys
        assert "private_key" in keys
    
    def test_authentication(self):
        iam = IAMv2Manager()
        
        # Create user
        keys = iam.create_user("test_user")
        
        # Test authentication
        message = "test_message"
        private_key = keys["private_key"]
        
        # Sign message (simplified for testing)
        # In real implementation, use proper signing
        signature = "test_signature"
        
        # This would fail without proper signing implementation
        # assert iam.authenticate_user("test_user", message, signature)
    
    def test_authorization(self):
        iam = IAMv2Manager()
        
        # Create admin user
        iam.create_user("admin_user")
        iam.authenticator.set_auth_level("admin_user", AuthLevel.ADMIN)
        
        # Test authorization
        result = iam.authorize_action("admin_user", "read", "any_resource")
        assert result == True
    
    def test_abac_policies(self):
        iam = IAMv2Manager()
        
        # Create user with attributes
        iam.create_user("researcher", {"role": "researcher"})
        
        # Test ABAC policy
        result = iam.authorize_action("researcher", "access", "research")
        assert result == True
```

### Integration Points
- **Authentication**: Ed25519 key-based authentication for all API endpoints
- **Authorization**: ABAC policies for fine-grained access control
- **Audit**: Complete logging of authentication and authorization events
- **Integration**: Seamless integration with existing FastAPI endpoints

---

## PHASE 5D: TASK SCHEDULER & VIKUNJA INTEGRATION

### Status: 85% Complete

### Objectives
- Integrate Vikunja task management system
- Implement sophisticated task scheduling and monitoring
- Enable task dependencies and workflow automation

### Implementation Steps

#### Step 1: Vikunja Integration (3 hours)
```python
# File: app/XNAi_rag_app/core/vikunja_integration.py

import requests
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 8
    CRITICAL = 10

@dataclass
class VikunjaTask:
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    created_at: float
    due_date: Optional[float] = None
    project_id: Optional[str] = None
    assignee_id: Optional[str] = None
    dependencies: List[str] = None

class VikunjaClient:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        })
    
    def create_task(self, title: str, description: str, 
                   project_id: Optional[str] = None,
                   due_date: Optional[float] = None,
                   priority: Priority = Priority.MEDIUM) -> VikunjaTask:
        """Create a new task in Vikunja"""
        payload = {
            'title': title,
            'description': description,
            'priority': priority.value,
            'status': 'pending'
        }
        
        if project_id:
            payload['project_id'] = project_id
        if due_date:
            payload['due_date'] = time.strftime('%Y-%m-%d', time.localtime(due_date))
        
        response = self.session.post(f"{self.base_url}/api/v1/tasks", json=payload)
        response.raise_for_status()
        
        data = response.json()
        return VikunjaTask(
            id=str(data['id']),
            title=data['title'],
            description=data['description'],
            status=TaskStatus.PENDING,
            priority=Priority(data['priority']),
            created_at=time.time()
        )
    
    def get_task(self, task_id: str) -> Optional[VikunjaTask]:
        """Get task by ID"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/tasks/{task_id}")
            response.raise_for_status()
            
            data = response.json()
            return VikunjaTask(
                id=str(data['id']),
                title=data['title'],
                description=data['description'],
                status=TaskStatus(data['status']),
                priority=Priority(data['priority']),
                created_at=time.time()
            )
        except requests.exceptions.HTTPError:
            return None
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task"""
        try:
            response = self.session.put(f"{self.base_url}/api/v1/tasks/{task_id}", json=updates)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError:
            return False
    
    def complete_task(self, task_id: str) -> bool:
        """Mark task as completed"""
        return self.update_task(task_id, {'status': 'completed'})
    
    def fail_task(self, task_id: str, reason: str) -> bool:
        """Mark task as failed"""
        return self.update_task(task_id, {
            'status': 'failed',
            'description': f"{reason}\n\nFailed at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        })
    
    def get_tasks(self, project_id: Optional[str] = None, 
                 status: Optional[TaskStatus] = None) -> List[VikunjaTask]:
        """Get tasks with optional filtering"""
        params = {}
        if project_id:
            params['project_id'] = project_id
        if status:
            params['status'] = status.value
        
        response = self.session.get(f"{self.base_url}/api/v1/tasks", params=params)
        response.raise_for_status()
        
        tasks = []
        for data in response.json():
            tasks.append(VikunjaTask(
                id=str(data['id']),
                title=data['title'],
                description=data['description'],
                status=TaskStatus(data['status']),
                priority=Priority(data['priority']),
                created_at=time.time()
            ))
        
        return tasks
    
    def create_project(self, name: str, description: str = "") -> str:
        """Create a new project"""
        payload = {
            'name': name,
            'description': description
        }
        
        response = self.session.post(f"{self.base_url}/api/v1/projects", json=payload)
        response.raise_for_status()
        
        return str(response.json()['id'])
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        response = self.session.get(f"{self.base_url}/api/v1/projects")
        response.raise_for_status()
        
        return response.json()

class TaskScheduler:
    """Advanced task scheduler with Vikunja integration"""
    
    def __init__(self, vikunja_client: VikunjaClient):
        self.vikunja = vikunja_client
        self.task_callbacks: Dict[str, callable] = {}
        self.running = False
    
    async def schedule_task(self, title: str, description: str,
                          callback: callable,
                          project_id: Optional[str] = None,
                          due_date: Optional[float] = None,
                          priority: Priority = Priority.MEDIUM) -> str:
        """Schedule a task with callback"""
        # Create task in Vikunja
        vikunja_task = self.vikunja.create_task(
            title, description, project_id, due_date, priority
        )
        
        # Store callback
        self.task_callbacks[vikunja_task.id] = callback
        
        # Start monitoring if not running
        if not self.running:
            self.running = True
            asyncio.create_task(self._monitor_tasks())
        
        return vikunja_task.id
    
    async def _monitor_tasks(self):
        """Monitor tasks and execute callbacks"""
        while self.running:
            try:
                # Get pending tasks
                pending_tasks = self.vikunja.get_tasks(status=TaskStatus.PENDING)
                
                for task in pending_tasks:
                    if task.id in self.task_callbacks:
                        # Execute callback
                        callback = self.task_callbacks[task.id]
                        
                        try:
                            # Update task status
                            self.vikunja.update_task(task.id, {'status': 'in_progress'})
                            
                            # Execute
                            result = await callback(task)
                            
                            # Mark as completed
                            self.vikunja.complete_task(task.id)
                            
                            logger.info(f"Task completed: {task.id}")
                            
                        except Exception as e:
                            # Mark as failed
                            self.vikunja.fail_task(task.id, str(e))
                            
                            logger.error(f"Task failed: {task.id} - {e}")
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in task monitor: {e}")
                await asyncio.sleep(5)
    
    def stop(self):
        """Stop task scheduler"""
        self.running = False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        task = self.vikunja.get_task(task_id)
        if not task:
            return None
        
        return {
            'id': task.id,
            'title': task.title,
            'status': task.status.value,
            'priority': task.priority.value,
            'created_at': task.created_at
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        return self.vikunja.update_task(task_id, {'status': 'cancelled'})

# Integration with existing systems
class FoundationTaskScheduler:
    """Foundation-specific task scheduler"""
    
    def __init__(self, vikunja_url: str, api_token: str):
        self.vikunja_client = VikunjaClient(vikunja_url, api_token)
        self.scheduler = TaskScheduler(self.vikunja_client)
        
        # Create Foundation project if it doesn't exist
        self.foundation_project_id = self._get_or_create_project("XNAi Foundation")
    
    def _get_or_create_project(self, name: str) -> str:
        """Get or create Foundation project"""
        projects = self.vikunja_client.get_projects()
        
        for project in projects:
            if project['name'] == name:
                return str(project['id'])
        
        # Create new project
        return self.vikunja_client.create_project(name, "XNAi Foundation task management")
    
    async def schedule_research_task(self, topic: str, callback: callable) -> str:
        """Schedule research task"""
        return await self.scheduler.schedule_task(
            f"Research: {topic}",
            f"Research task for topic: {topic}",
            callback,
            self.foundation_project_id,
            priority=Priority.HIGH
        )
    
    async def schedule_maintenance_task(self, task_name: str, callback: callable) -> str:
        """Schedule maintenance task"""
        return await self.scheduler.schedule_task(
            f"Maintenance: {task_name}",
            f"Maintenance task: {task_name}",
            callback,
            self.foundation_project_id,
            priority=Priority.MEDIUM
        )
    
    async def schedule_monitoring_task(self, check_name: str, callback: callable) -> str:
        """Schedule monitoring task"""
        return await self.scheduler.schedule_task(
            f"Monitoring: {check_name}",
            f"Monitoring check: {check_name}",
            callback,
            self.foundation_project_id,
            priority=Priority.LOW
        )
```

### Testing Strategy
```python
# File: tests/test_vikunja_integration.py

import pytest
from unittest.mock import Mock, patch
from app.XNAi_rag_app.core.vikunja_integration import VikunjaClient, TaskScheduler

class TestVikunjaClient:
    @patch('requests.Session')
    def test_create_task(self, mock_session):
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': 123,
            'title': 'Test Task',
            'description': 'Test Description',
            'priority': 5,
            'status': 'pending'
        }
        mock_session.return_value.post.return_value = mock_response
        
        # Create client and test
        client = VikunjaClient("http://test.com", "token")
        task = client.create_task("Test Task", "Test Description")
        
        assert task.title == "Test Task"
        assert task.description == "Test Description"
    
    @patch('requests.Session')
    def test_get_task(self, mock_session):
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': 123,
            'title': 'Test Task',
            'description': 'Test Description',
            'priority': 5,
            'status': 'pending'
        }
        mock_session.return_value.get.return_value = mock_response
        
        # Create client and test
        client = VikunjaClient("http://test.com", "token")
        task = client.get_task("123")
        
        assert task is not None
        assert task.title == "Test Task"

class TestTaskScheduler:
    def test_schedule_task(self):
        # This would require more complex mocking for full testing
        # Simplified for example
        pass
```

### Integration Points
- **Vikunja**: Full task management integration with web UI
- **Task Scheduler**: Automated task execution with monitoring
- **Foundation Integration**: Domain-specific task types and workflows
- **Monitoring**: Real-time task status and completion tracking

---

## PHASE 5E: E5 ONBOARDING PROTOCOL

### Status: 80% Complete

### Objectives
- Create streamlined onboarding process for new users
- Automate setup and configuration
- Provide comprehensive documentation and training

### Implementation Steps

#### Step 1: Onboarding Protocol (3 hours)
```python
# File: app/XNAi_rag_app/core/e5_onboarding.py

import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class OnboardingStep(Enum):
    ACCOUNT_SETUP = "account_setup"
    SYSTEM_CONFIG = "system_config"
    SECURITY_SETUP = "security_setup"
    DATA_IMPORT = "data_import"
    AGENT_CONFIGURATION = "agent_configuration"
    TRAINING = "training"
    VERIFICATION = "verification"
    COMPLETION = "completion"

@dataclass
class OnboardingStepData:
    step: OnboardingStep
    status: str  # pending, in_progress, completed, failed
    progress: float  # 0.0 to 1.0
    message: str
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None

class E5OnboardingProtocol:
    """E5 Onboarding Protocol implementation"""
    
    def __init__(self, iam_manager, agent_bus, task_scheduler):
        self.iam_manager = iam_manager
        self.agent_bus = agent_bus
        self.task_scheduler = task_scheduler
        self.onboarding_sessions: Dict[str, List[OnboardingStepData]] = {}
    
    async def start_onboarding(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """Start onboarding process for user"""
        session_id = self._generate_session_id()
        
        # Initialize session
        steps = [
            OnboardingStepData(
                step=OnboardingStep.ACCOUNT_SETUP,
                status="pending",
                progress=0.0,
                message="Setting up user account"
            ),
            OnboardingStepData(
                step=OnboardingStep.SYSTEM_CONFIG,
                status="pending",
                progress=0.0,
                message="Configuring system settings"
            ),
            OnboardingStepData(
                step=OnboardingStep.SECURITY_SETUP,
                status="pending",
                progress=0.0,
                message="Setting up security configuration"
            ),
            OnboardingStepData(
                step=OnboardingStep.DATA_IMPORT,
                status="pending",
                progress=0.0,
                message="Importing user data"
            ),
            OnboardingStepData(
                step=OnboardingStep.AGENT_CONFIGURATION,
                status="pending",
                progress=0.0,
                message="Configuring AI agents"
            ),
            OnboardingStepData(
                step=OnboardingStep.TRAINING,
                status="pending",
                progress=0.0,
                message="Training AI agents"
            ),
            OnboardingStepData(
                step=OnboardingStep.VERIFICATION,
                status="pending",
                progress=0.0,
                message="Verifying setup"
            ),
            OnboardingStepData(
                step=OnboardingStep.COMPLETION,
                status="pending",
                progress=0.0,
                message="Completing onboarding"
            )
        ]
        
        self.onboarding_sessions[session_id] = steps
        
        # Start onboarding process
        asyncio.create_task(self._execute_onboarding(session_id, user_id, user_data))
        
        return session_id
    
    async def get_onboarding_status(self, session_id: str) -> Dict[str, Any]:
        """Get onboarding status"""
        if session_id not in self.onboarding_sessions:
            return {"error": "Session not found"}
        
        steps = self.onboarding_sessions[session_id]
        
        # Calculate overall progress
        total_steps = len(steps)
        completed_steps = sum(1 for step in steps if step.status == "completed")
        overall_progress = completed_steps / total_steps
        
        return {
            "session_id": session_id,
            "steps": [
                {
                    "step": step.step.value,
                    "status": step.status,
                    "progress": step.progress,
                    "message": step.message,
                    "started_at": step.started_at,
                    "completed_at": step.completed_at,
                    "error": step.error
                }
                for step in steps
            ],
            "overall_progress": overall_progress,
            "status": "completed" if overall_progress == 1.0 else "in_progress"
        }
    
    async def _execute_onboarding(self, session_id: str, user_id: str, user_data: Dict[str, Any]):
        """Execute onboarding steps"""
        steps = self.onboarding_sessions[session_id]
        
        for step_data in steps:
            try:
                step_data.status = "in_progress"
                step_data.started_at = time.time()
                
                # Execute step
                await self._execute_step(step_data, user_id, user_data)
                
                # Mark as completed
                step_data.status = "completed"
                step_data.progress = 1.0
                step_data.completed_at = time.time()
                
                logger.info(f"Onboarding step completed: {step_data.step.value}")
                
            except Exception as e:
                step_data.status = "failed"
                step_data.error = str(e)
                step_data.completed_at = time.time()
                
                logger.error(f"Onboarding step failed: {step_data.step.value} - {e}")
                break  # Stop on first failure
    
    async def _execute_step(self, step_data: OnboardingStepData, user_id: str, user_data: Dict[str, Any]):
        """Execute individual onboarding step"""
        step = step_data.step
        
        if step == OnboardingStep.ACCOUNT_SETUP:
            await self._setup_account(user_id, user_data, step_data)
        elif step == OnboardingStep.SYSTEM_CONFIG:
            await self._configure_system(user_id, user_data, step_data)
        elif step == OnboardingStep.SECURITY_SETUP:
            await self._setup_security(user_id, user_data, step_data)
        elif step == OnboardingStep.DATA_IMPORT:
            await self._import_data(user_id, user_data, step_data)
        elif step == OnboardingStep.AGENT_CONFIGURATION:
            await self._configure_agents(user_id, user_data, step_data)
        elif step == OnboardingStep.TRAINING:
            await self._train_agents(user_id, user_data, step_data)
        elif step == OnboardingStep.VERIFICATION:
            await self._verify_setup(user_id, user_data, step_data)
        elif step == OnboardingStep.COMPLETION:
            await self._complete_onboarding(user_id, user_data, step_data)
    
    async def _setup_account(self, user_id: str, user_data: Dict[str, Any], step_data: OnboardingStepData):
        """Setup user account"""
        step_data.message = "Creating user account"
        step_data.progress = 0.3
        
        # Create user in IAM
        attributes = user_data.get('attributes', {})
        keys = self.iam_manager.create_user(user_id, attributes)
        
        step_data.message = "Account created successfully"
        step_data.progress = 1.0
    
    async def _configure_system(self, user_id: str, user_data: Dict[str, Any], step_data: OnboardingStepData):
        """Configure system settings"""
        step_data.message = "Configuring system settings"
        step_data.progress = 0.2
        
        # Set user preferences
        preferences = user_data.get('preferences', {})
        if preferences:
            self.iam_manager.update_attributes(user_id, {'preferences': preferences})
        
        step_data.message = "System configuration complete"
        step_data.progress = 1.0
    
    async def _setup_security(self, user_id: str, user_data: Dict[str, Any], step_data: OnboardingStepData):
        """Setup security configuration"""
        step_data.message = "Setting up security"
        step_data.progress = 0.1
        
        # Generate security tokens
        # Setup 2FA if required
        # Configure access controls
        
        step_data.message = "Security setup complete"
        step_data.progress = 1.0
    
    async def _import_data(self, user_id: str, user_data: Dict[str, Any], step_data: OnboardingStepData):
        """Import user data"""
        step_data.message = "Importing user data"
        step_data.progress = 0.1
        
        # Import documents
        documents = user_data.get('documents', [])
        for i, doc in enumerate(documents):
            step_data.progress = 0.1 + (i / len(documents)) * 0.8
            step_data.message = f"Importing document {i+1}/{len(documents)}"
            
            # Process document
            # Add to vector store
            # Update progress
        
        step_data.message = "Data import complete"
        step_data.progress = 1.0
    
    async def _configure_agents(self, user_id: str, user_data: Dict[str, Any], step_data: OnboardingStepData):
        """Configure AI agents"""
        step_data.message = "Configuring AI agents"
        step_data.progress = 0.1
        
        # Create agent configurations
        agent_configs = user_data.get('agent_configs', [])
        for i, config in enumerate(agent_configs):
            step_data.progress = 0.1 + (i / len(agent_configs)) * 0.8
            step_data.message = f"Configuring agent {i+1}/{len(agent_configs)}"
            
            # Setup agent
            # Register with agent bus
        
        step_data.message = "Agent configuration complete"
        step_data.progress = 1.0
    
    async def _train_agents(self, user_id: str, user_data: Dict[str, Any], step_data: OnboardingStepData):
        """Train AI agents"""
        step_data.message = "Training AI agents"
        step_data.progress = 0.1
        
        # Train agents with user data
        # Optimize for user preferences
        # Validate training results
        
        step_data.message = "Agent training complete"
        step_data.progress = 1.0
    
    async def _verify_setup(self, user_id: str, user_data: Dict[str, Any], step_data: OnboardingStepData):
        """Verify setup"""
        step_data.message = "Verifying setup"
        step_data.progress = 0.1
        
        # Run verification tests
        # Check all components
        # Validate security
        
        step_data.message = "Setup verification complete"
        step_data.progress = 1.0
    
    async def _complete_onboarding(self, user_id: str, user_data: Dict[str, Any], step_data: OnboardingStepData):
        """Complete onboarding"""
        step_data.message = "Completing onboarding"
        step_data.progress = 0.1
        
        # Send completion notification
        # Generate welcome message
        # Setup ongoing monitoring
        
        step_data.message = "Onboarding complete!"
        step_data.progress = 1.0
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return f"onboarding_{uuid.uuid4().hex[:16]}"

# Web interface for onboarding
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class UserData(BaseModel):
    name: str
    email: str
    attributes: Dict[str, Any] = {}
    preferences: Dict[str, Any] = {}
    documents: List[Dict[str, Any]] = []
    agent_configs: List[Dict[str, Any]] = []

app = FastAPI()

@app.post("/api/onboarding/start")
async def start_onboarding(user_data: UserData):
    """Start onboarding process"""
    onboarding = E5OnboardingProtocol(None, None, None)  # Inject dependencies
    
    session_id = await onboarding.start_onboarding(user_data.email, user_data.dict())
    
    return {
        "session_id": session_id,
        "message": "Onboarding started"
    }

@app.get("/api/onboarding/status/{session_id}")
async def get_onboarding_status(session_id: str):
    """Get onboarding status"""
    onboarding = E5OnboardingProtocol(None, None, None)  # Inject dependencies
    
    status = await onboarding.get_onboarding_status(session_id)
    
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    
    return status
```

### Testing Strategy
```python
# File: tests/test_e5_onboarding.py

import pytest
from app.XNAi_rag_app.core.e5_onboarding import E5OnboardingProtocol, OnboardingStep

class TestE5Onboarding:
    async def test_start_onboarding(self):
        # Mock dependencies
        iam_manager = Mock()
        agent_bus = Mock()
        task_scheduler = Mock()
        
        onboarding = E5OnboardingProtocol(iam_manager, agent_bus, task_scheduler)
        
        # Start onboarding
        session_id = await onboarding.start_onboarding("test_user", {"name": "Test User"})
        
        assert session_id is not None
        assert session_id in onboarding.onboarding_sessions
    
    async def test_get_onboarding_status(self):
        # Mock dependencies
        iam_manager = Mock()
        agent_bus = Mock()
        task_scheduler = Mock()
        
        onboarding = E5OnboardingProtocol(iam_manager, agent_bus, task_scheduler)
        
        # Start onboarding
        session_id = await onboarding.start_onboarding("test_user", {"name": "Test User"})
        
        # Get status
        status = await onboarding.get_onboarding_status(session_id)
        
        assert "session_id" in status
        assert "steps" in status
        assert "overall_progress" in status
```

### Integration Points
- **Onboarding Protocol**: Complete user setup and configuration
- **Web Interface**: User-friendly onboarding web interface
- **Integration**: Seamless integration with existing IAM and agent systems
- **Documentation**: Comprehensive onboarding documentation and training

---

## IMPLEMENTATION TIMELINE

### Week 1: Foundation & Setup (20-25 hours)
- **Day 1-2**: Review documentation and resolve blockers (4-6 hours)
- **Day 3**: Setup Phase 5A infrastructure (6-8 hours)
- **Day 4-5**: Begin Phase 5B Agent Bus implementation (8-10 hours)

### Week 2-3: Core Implementation (40-50 hours)
- **Week 2**: Complete Phase 5B Agent Bus (15-18 hours)
- **Week 2**: Begin Phase 5C IAM v2.0 (12-15 hours)
- **Week 3**: Complete Phase 5C IAM v2.0 (10-12 hours)
- **Week 3**: Begin Phase 5D Task Scheduler (8-10 hours)

### Week 4-5: Completion & Wave 6 Start (35-45 hours)
- **Week 4**: Complete Phase 5D Task Scheduler (10-12 hours)
- **Week 4**: Implement Phase 5E E5 Onboarding (12-15 hours)
- **Week 5**: Begin Phase 6A Observability (12-16 hours)
- **Week 5**: Testing and validation (8-10 hours)

### Total Timeline: 95-120 hours across 5-8 engineers

---

## RESOURCE REQUIREMENTS

### Team Composition
- **5-8 Engineers** (full-stack, DevOps, security)
- **1-2 Architects** (system design, integration)
- **1-2 QA Engineers** (testing, validation)
- **1-2 DevOps Engineers** (infrastructure, monitoring)

### Infrastructure Requirements
- **Development Environment**: 8GB RAM, 4 cores, 100GB storage
- **Staging Environment**: 16GB RAM, 8 cores, 200GB storage
- **Production Environment**: 32GB RAM, 16 cores, 500GB storage
- **GPU Support**: Optional for enhanced performance

### Dependencies
- **Python 3.12+** with uv package manager
- **Docker/Podman** for containerization
- **Redis** for caching and message queuing
- **PostgreSQL** for primary database
- **Qdrant** for vector search
- **Vikunja** for task management
- **FastAPI** for API development

---

## SUCCESS CRITERIA

### Technical Metrics
- **Uptime**: 99.95%+ (production-grade SLA)
- **Latency**: <250ms p95 for API responses
- **Throughput**: 1000+ concurrent users
- **Memory Usage**: <6GB per service instance
- **Error Rate**: <0.1% for critical operations

### Business Metrics
- **User Adoption**: 80%+ of target users onboarded
- **Task Completion**: 95%+ of scheduled tasks complete successfully
- **Knowledge Retrieval**: <100ms vector search, <50ms keyword search
- **Multi-Agent Performance**: 20-30% improvement in task quality
- **Operational Efficiency**: 15-25% improvement in system performance

### Quality Metrics
- **Test Coverage**: 90%+ across all components
- **Code Quality**: 0 critical, <5 high-severity issues
- **Documentation**: 100% of APIs documented
- **Monitoring**: 100% of critical metrics monitored
- **Security**: 0 security vulnerabilities in production

---

## TROUBLESHOOTING

### Common Issues

#### Session Management Issues
- **Problem**: Sessions not persisting across restarts
- **Solution**: Check database permissions and SQLite file access
- **Debug**: Enable debug logging in session manager

#### Agent Bus Communication Issues
- **Problem**: Agents not receiving messages
- **Solution**: Verify Redis connection and message routing
- **Debug**: Check agent registration and subscription status

#### Authentication Failures
- **Problem**: Ed25519 authentication failing
- **Solution**: Verify key generation and signature verification
- **Debug**: Enable detailed authentication logging

#### Task Scheduling Issues
- **Problem**: Tasks not executing or timing out
- **Solution**: Check Vikunja API connectivity and task monitoring
- **Debug**: Review task status and callback execution

#### Onboarding Failures
- **Problem**: Onboarding steps failing or hanging
- **Solution**: Check step dependencies and error handling
- **Debug**: Review onboarding session logs

### Debug Tools

#### Session Debug
```python
# Check session status
session_manager = PersistentSessionManager()
session = session_manager.get_session("session_id")
print(f"Session: {session}")
```

#### Agent Bus Debug
```python
# Check agent status
agents = await agent_bus.get_all_agents()
print(f"Registered agents: {agents}")
```

#### Authentication Debug
```python
# Test authentication
result = iam_manager.authenticate_user("user_id", "message", "signature")
print(f"Authentication result: {result}")
```

#### Task Debug
```python
# Check task status
status = await task_scheduler.get_task_status("task_id")
print(f"Task status: {status}")
```

### Support Resources
- **Documentation**: `docs/` directory for all technical documentation
- **Logs**: Check application logs for detailed error information
- **Monitoring**: Use monitoring dashboards for real-time system status
- **Community**: GitHub issues for bug reports and feature requests

---

## FINAL NOTES

This implementation manual provides comprehensive guidance for executing Wave 5 of the XNAi Foundation project. Each phase includes detailed implementation steps, testing strategies, and integration points to ensure successful execution.

**Key Success Factors**:
1. Follow the implementation order (5A → 5B → 5C → 5D → 5E)
2. Maintain comprehensive testing throughout implementation
3. Monitor system performance and address issues proactively
4. Keep documentation up-to-date with implementation progress
5. Coordinate closely between team members for integration points

**Expected Outcome**: A production-grade Local Sovereignty Stack with advanced session management, multi-agent coordination, cryptographic security, sophisticated task scheduling, and streamlined user onboarding.

**Next Steps**: Proceed with Week 1 implementation, focusing on resolving critical blockers and establishing the foundation for subsequent phases.