#!/usr/bin/env python3
"""
Multi-Agent Coordination System for Xoe-NovAi Foundation Stack
Implements the Agent Bus Protocol for filesystem-based communication.
"""

import os
import json
import time
import uuid
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import threading
# Optional infra helpers
try:
    from scripts.agent_state_redis import RedisAgentStateAdapter
    _redis_adapter = RedisAgentStateAdapter()
except Exception:
    _redis_adapter = None

try:
    from scripts.consul_registration import ConsulRegistrar
    _consul_registrar = ConsulRegistrar()
except Exception:
    _consul_registrar = None

try:
    from scripts.identity_ed25519 import generate_keypair_hex
    _identity_available = True
except Exception:
    _identity_available = False

import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent_coordinator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AgentState:
    """Agent state data structure"""
    agent_name: str
    status: str  # active, inactive, busy, error, offline
    current_task: Optional[str] = None
    progress: float = 0.0
    last_heartbeat: str = ""
    capabilities: List[str] = None
    memory_usage: str = ""
    error_count: int = 0
    success_count: int = 0
    total_tasks: int = 0
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if not self.last_heartbeat:
            self.last_heartbeat = datetime.utcnow().isoformat()

@dataclass
class Message:
    """Message data structure"""
    message_id: str
    timestamp: str
    sender: str
    target: str
    type: str
    priority: str  # high, medium, low
    content: Dict[str, Any]
    correlation_id: Optional[str] = None

class AgentCoordinator:
    """Main coordinator for multi-agent communication"""
    
    def __init__(self, hub_dir: str = "internal_docs/communication_hub"):
        self.hub_dir = Path(hub_dir)
        self.inbox_dir = self.hub_dir / "inbox"
        self.outbox_dir = self.hub_dir / "outbox"
        self.state_dir = self.hub_dir / "state"
        
        # Ensure directories exist
        for dir_path in [self.inbox_dir, self.outbox_dir, self.state_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Agent registry
        self.agents: Dict[str, AgentState] = {}
        self.message_handlers: Dict[str, Callable] = {}
        
        # Threading
        self.running = False
        self.watchers: Dict[str, threading.Thread] = {}
        
        # Message processing queue
        self.message_queue = []
        self.queue_lock = threading.Lock()
        
        logger.info(f"Agent Coordinator initialized with hub: {self.hub_dir}")
    
    def register_agent(self, agent_name: str, capabilities: List[str]):
        """Register a new agent"""
        state = AgentState(
            agent_name=agent_name,
            status="active",
            capabilities=capabilities
        )
        self.agents[agent_name] = state
        self._save_state(agent_name, state)
        # Generate Ed25519 identity and persist (if available)
        if _identity_available:
            try:
                priv_hex, pub_hex = generate_keypair_hex()
                iam_path = self.hub_dir.parent / "data" / "iam_agents.db"
                iam_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    existing = json.loads(iam_path.read_text()) if iam_path.exists() else {}
                except Exception:
                    existing = {}
                existing[agent_name] = {"public_key": pub_hex}
                iam_path.write_text(json.dumps(existing, indent=2))
                logger.info(f"Generated identity for agent {agent_name}")
            except Exception as e:
                logger.warning(f"Failed to generate identity for {agent_name}: {e}")
        # Consul registration (best-effort)
        if _consul_registrar:
            try:
                _consul_registrar.register_service(name=agent_name, service_id=agent_name, tags=capabilities)
                logger.info(f"Registered {agent_name} with Consul")
            except Exception as e:
                logger.warning(f"Consul registration failed for {agent_name}: {e}")
        logger.info(f"Registered agent: {agent_name} with capabilities: {capabilities}")
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types"""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")
    
    def send_message(self, target_agent: str, message_type: str, content: Dict[str, Any], 
                    priority: str = "medium", sender: str = "agent_coordinator", 
                    correlation_id: Optional[str] = None):
        """Send message to target agent"""
        message = Message(
            message_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            sender=sender,
            target=target_agent,
            type=message_type,
            priority=priority,
            content=content,
            correlation_id=correlation_id
        )
        
        # Validate target agent exists
        if target_agent not in self.agents:
            logger.warning(f"Target agent {target_agent} not registered")
            return False
        
        # Write message to outbox
        message_file = self.outbox_dir / f"{target_agent}_{int(time.time())}.json"
        try:
            with open(message_file, 'w') as f:
                json.dump(asdict(message), f, indent=2)
            logger.info(f"Message sent to {target_agent}: {message_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {target_agent}: {e}")
            return False
    
    def get_messages(self, agent_name: str) -> List[Message]:
        """Get messages for specific agent"""
        messages = []
        message_files = list(self.inbox_dir.glob(f"{agent_name}_*.json"))
        
        for msg_file in message_files:
            try:
                with open(msg_file, 'r') as f:
                    message_data = json.load(f)
                    message = Message(**message_data)
                    messages.append(message)
                    
                    # Archive message
                    msg_file.unlink()
            except Exception as e:
                logger.error(f"Failed to read message {msg_file}: {e}")
        
        # Sort by priority and timestamp
        messages.sort(key=lambda m: (
            {"high": 0, "medium": 1, "low": 2}[m.priority],
            m.timestamp
        ))
        
        return messages
    
    def update_agent_state(self, agent_name: str, updates: Dict[str, Any]):
        """Update agent state"""
        if agent_name not in self.agents:
            logger.warning(f"Agent {agent_name} not registered")
            return
        
        state = self.agents[agent_name]
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        state.last_heartbeat = datetime.utcnow().isoformat()
        self.agents[agent_name] = state
        self._save_state(agent_name, state)
    
    def get_agent_state(self, agent_name: str) -> Optional[AgentState]:
        """Get agent state"""
        return self.agents.get(agent_name)
    
    def _save_state(self, agent_name: str, state: AgentState):
        """Save agent state to file"""
        # Try Redis adapter first
        try:
            if _redis_adapter:
                _redis_adapter.save_state(agent_name, asdict(state))
                return
        except Exception as e:
            logger.warning(f"Redis adapter save failed for {agent_name}: {e}")
        state_file = self.state_dir / f"{agent_name}.json"
        try:
            with open(state_file, 'w') as f:
                json.dump(asdict(state), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state for {agent_name}: {e}")
    
    def _load_state(self, agent_name: str) -> Optional[AgentState]:
        """Load agent state from file"""
        # Try Redis adapter first
        try:
            if _redis_adapter:
                data = _redis_adapter.load_state(agent_name)
                if data:
                    return AgentState(**data)
        except Exception as e:
            logger.warning(f"Redis adapter load failed for {agent_name}: {e}")
        state_file = self.state_dir / f"{agent_name}.json"
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, 'r') as f:
                state_data = json.load(f)
                return AgentState(**state_data)
        except Exception as e:
            logger.error(f"Failed to load state for {agent_name}: {e}")
            return None
    
    def process_messages(self, agent_name: str):
        """Process messages for specific agent"""
        messages = self.get_messages(agent_name)
        
        for message in messages:
            logger.info(f"Processing message for {agent_name}: {message.type}")
            
            # Handle message based on type
            if message.type in self.message_handlers:
                try:
                    handler = self.message_handlers[message.type]
                    handler(message)
                except Exception as e:
                    logger.error(f"Handler failed for message {message.message_id}: {e}")
                    self.send_error_report(agent_name, message, str(e))
            else:
                logger.warning(f"No handler for message type: {message.type}")
    
    def send_error_report(self, agent_name: str, original_message: Message, error_message: str):
        """Send error report to message sender"""
        error_content = {
            "error_type": "message_processing_failed",
            "message": error_message,
            "context": {
                "agent": agent_name,
                "original_message_id": original_message.message_id,
                "original_message_type": original_message.type,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        self.send_message(
            target_agent=original_message.sender,
            message_type="error_report",
            content=error_content,
            priority="high",
            correlation_id=original_message.message_id
        )
    
    def start_watcher(self, agent_name: str, interval: int = 30):
        """Start watcher thread for agent"""
        if agent_name in self.watchers:
            logger.warning(f"Watcher already running for {agent_name}")
            return
        
        def watcher_loop():
            while self.running:
                try:
                    # Check for new messages
                    messages = self.get_messages(agent_name)
                    if messages:
                        logger.info(f"Watcher: {len(messages)} new messages for {agent_name}")
                        for message in messages:
                            self.process_messages(agent_name)
                    
                    # Update heartbeat
                    self.update_agent_state(agent_name, {"status": "active"})
                    
                except Exception as e:
                    logger.error(f"Watcher error for {agent_name}: {e}")
                
                time.sleep(interval)
        
        watcher = threading.Thread(target=watcher_loop, daemon=True)
        self.watchers[agent_name] = watcher
        watcher.start()
        logger.info(f"Started watcher for {agent_name} with interval {interval}s")
    
    def stop_watcher(self, agent_name: str):
        """Stop watcher thread for agent"""
        if agent_name in self.watchers:
            del self.watchers[agent_name]
            logger.info(f"Stopped watcher for {agent_name}")
    
    def start_health_monitor(self, check_interval: int = 60):
        """Start health monitoring thread"""
        def health_loop():
            while self.running:
                try:
                    self.check_health()
                except Exception as e:
                    logger.error(f"Health monitor error: {e}")
                time.sleep(check_interval)
        
        health_thread = threading.Thread(target=health_loop, daemon=True)
        health_thread.start()
        logger.info(f"Started health monitor with interval {check_interval}s")
    
    def check_health(self):
        """Check health of all agents"""
        for agent_name, state in self.agents.items():
            last_heartbeat = datetime.fromisoformat(state.last_heartbeat)
            if datetime.utcnow() - last_heartbeat > timedelta(minutes=10):
                logger.warning(f"Agent {agent_name} heartbeat stale: {state.last_heartbeat}")
                self.update_agent_state(agent_name, {"status": "error"})
    
    def start(self):
        """Start the coordinator"""
        self.running = True
        logger.info("Agent Coordinator started")
        
        # Start health monitor
        self.start_health_monitor()
        
        # Start watchers for all registered agents
        for agent_name in self.agents:
            self.start_watcher(agent_name)
    
    def stop(self):
        """Stop the coordinator"""
        self.running = False
        logger.info("Agent Coordinator stopping")
        
        # Stop all watchers
        for agent_name in list(self.watchers.keys()):
            self.stop_watcher(agent_name)
    
    def get_status(self) -> Dict[str, Any]:
        """Get coordinator status"""
        return {
            "running": self.running,
            "registered_agents": list(self.agents.keys()),
            "active_watchers": list(self.watchers.keys()),
            "inbox_count": len(list(self.inbox_dir.glob("*.json"))),
            "outbox_count": len(list(self.outbox_dir.glob("*.json"))),
            "agent_states": {name: asdict(state) for name, state in self.agents.items()}
        }

# Default message handlers
def handle_task_assignment(message: Message):
    """Handle task assignment messages"""
    logger.info(f"Task assignment: {message.content.get('task')} for {message.target}")

def handle_task_completion(message: Message):
    """Handle task completion messages"""
    logger.info(f"Task completion: {message.content.get('task')} from {message.sender}")

def handle_state_update(message: Message):
    """Handle state update messages"""
    logger.info(f"State update from {message.sender}")

def handle_error_report(message: Message):
    """Handle error report messages"""
    logger.error(f"Error report from {message.sender}: {message.content.get('message')}")

def handle_assistance_request(message: Message):
    """Handle assistance request messages"""
    logger.info(f"Assistance request from {message.sender}: {message.content.get('description')}")

# Example usage and initialization
def main():
    """Example usage of the Agent Coordinator"""
    coordinator = AgentCoordinator()
    
    # Register message handlers
    coordinator.register_message_handler("task_assignment", handle_task_assignment)
    coordinator.register_message_handler("task_completion", handle_task_completion)
    coordinator.register_message_handler("state_update", handle_state_update)
    coordinator.register_message_handler("error_report", handle_error_report)
    coordinator.register_message_handler("assistance_request", handle_assistance_request)
    
    # Register agents
    coordinator.register_agent("cline-cli", ["code_generation", "refactoring", "testing"])
    coordinator.register_agent("gemini-cli", ["execution", "filesystem", "sync"])
    coordinator.register_agent("opencode", ["research", "model_access", "analysis"])
    coordinator.register_agent("grok-mc", ["strategy", "oversight", "coordination"])
    
    # Send test messages
    coordinator.send_message(
        target_agent="cline-cli",
        message_type="task_assignment",
        content={
            "task": "implement_circuit_breakers",
            "priority": "high",
            "deadline": "2026-02-21",
            "description": "Implement Redis-backed circuit breakers",
            "requirements": ["redis_connection", "graceful_degradation"],
            "deliverables": ["circuit_breaker_module", "tests", "documentation"]
        },
        priority="high"
    )
    
    # Start coordinator
    coordinator.start()
    
    # Handle shutdown
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received")
        coordinator.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep running
    try:
        while coordinator.running:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        coordinator.stop()

if __name__ == "__main__":
    main()