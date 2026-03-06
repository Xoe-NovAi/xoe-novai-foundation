#!/usr/bin/env python3
"""
Architecture Diagram Generator for XNAi Foundation

This script generates comprehensive architecture diagrams showing current and target states,
including multi-agent coordination, FAISS integration, and system components.

Author: XNAi Foundation
License: AGPL-3.0-only
"""

import json
import logging
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Component:
    """System component"""
    id: str
    name: str
    type: str  # service, database, cache, queue, etc.
    description: str
    technologies: List[str]
    connections: List[str]  # List of component IDs this component connects to
    status: str  # current, target, planned
    priority: int


@dataclass
class AgentAccount:
    """Agent account information"""
    account_id: str
    name: str
    type: str  # primary, subagent, coordinator, validator
    capabilities: List[str]
    status: str  # active, inactive, suspended
    priority: int


@dataclass
class ArchitectureState:
    """Complete architecture state"""
    name: str
    description: str
    components: List[Component]
    agent_accounts: List[AgentAccount]
    relationships: List[Dict[str, str]]
    created_at: str


class ArchitectureDiagramGenerator:
    """Generates architecture diagrams using Mermaid"""
    
    def __init__(self, output_dir: str = "architecture/diagrams"):
        """
        Initialize the diagram generator
        
        Args:
            output_dir: Directory to save generated diagrams
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.config_path = Path("configs/multi-agent-config.yaml")
        self.config: Optional[Dict] = None
        
        # Architecture states
        self.current_state: Optional[ArchitectureState] = None
        self.target_state: Optional[ArchitectureState] = None
    
    async def load_config(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            self.config = config_data.get('multi_agent', {})
            logger.info("Loaded architecture configuration")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def build_current_architecture(self) -> ArchitectureState:
        """Build current architecture state"""
        components = [
            # Core Services
            Component(
                id="chainlit_app",
                name="Chainlit App",
                type="web_service",
                description="Main web interface for RAG application",
                technologies=["Python", "Chainlit", "FastAPI"],
                connections=["api_server", "qdrant", "faiss"],
                status="current",
                priority=1
            ),
            Component(
                id="api_server",
                name="API Server",
                type="web_service",
                description="FastAPI backend server",
                technologies=["Python", "FastAPI", "uvicorn"],
                connections=["postgres", "redis", "qdrant", "faiss"],
                status="current",
                priority=1
            ),
            
            # Databases
            Component(
                id="postgres",
                name="PostgreSQL",
                type="database",
                description="Primary relational database",
                technologies=["PostgreSQL", "Alembic"],
                connections=["api_server"],
                status="current",
                priority=1
            ),
            Component(
                id="qdrant",
                name="Qdrant",
                type="vector_database",
                description="Vector database for embeddings",
                technologies=["Qdrant", "Docker"],
                connections=["api_server", "faiss"],
                status="current",
                priority=1
            ),
            
            # Caching & Queues
            Component(
                id="redis",
                name="Redis",
                type="cache",
                description="Caching and session storage",
                technologies=["Redis"],
                connections=["api_server", "celery"],
                status="current",
                priority=2
            ),
            Component(
                id="celery",
                name="Celery",
                type="queue",
                description="Task queue for background jobs",
                technologies=["Celery", "Redis"],
                connections=["api_server", "redis"],
                status="current",
                priority=2
            ),
            
            # Storage
            Component(
                id="faiss",
                name="FAISS",
                type="vector_database",
                description="Local vector database for Ryzen optimization",
                technologies=["FAISS", "NumPy"],
                connections=["api_server", "qdrant"],
                status="current",
                priority=1
            ),
            Component(
                id="minio",
                name="MinIO",
                type="storage",
                description="Object storage for documents and models",
                technologies=["MinIO", "S3 API"],
                connections=["api_server"],
                status="current",
                priority=2
            ),
            
            # Monitoring
            Component(
                id="prometheus",
                name="Prometheus",
                type="monitoring",
                description="Metrics collection and monitoring",
                technologies=["Prometheus", "Grafana"],
                connections=["api_server", "chainlit_app"],
                status="current",
                priority=3
            ),
            Component(
                id="grafana",
                name="Grafana",
                type="monitoring",
                description="Visualization and dashboards",
                technologies=["Grafana", "Prometheus"],
                connections=["prometheus"],
                status="current",
                priority=3
            ),
            
            # Infrastructure
            Component(
                id="nginx",
                name="Nginx",
                type="proxy",
                description="Reverse proxy and load balancer",
                technologies=["Nginx", "SSL/TLS"],
                connections=["chainlit_app", "api_server"],
                status="current",
                priority=2
            ),
            Component(
                id="docker",
                name="Docker",
                type="containerization",
                description="Container runtime and orchestration",
                technologies=["Docker", "Docker Compose"],
                connections=["all_services"],
                status="current",
                priority=2
            )
        ]
        
        agent_accounts = [
            AgentAccount(
                account_id="primary_account",
                name="Primary Account",
                type="primary",
                capabilities=["full_access", "admin"],
                status="active",
                priority=1
            )
        ]
        
        relationships = [
            {"source": "chainlit_app", "target": "api_server", "type": "http"},
            {"source": "api_server", "target": "postgres", "type": "database"},
            {"source": "api_server", "target": "qdrant", "type": "vector"},
            {"source": "api_server", "target": "faiss", "type": "vector"},
            {"source": "api_server", "target": "redis", "type": "cache"},
            {"source": "api_server", "target": "celery", "type": "queue"},
            {"source": "qdrant", "target": "faiss", "type": "sync"},
            {"source": "api_server", "target": "minio", "type": "storage"},
            {"source": "api_server", "target": "prometheus", "type": "metrics"},
            {"source": "chainlit_app", "target": "prometheus", "type": "metrics"},
            {"source": "prometheus", "target": "grafana", "type": "visualization"},
            {"source": "nginx", "target": "chainlit_app", "type": "proxy"},
            {"source": "nginx", "target": "api_server", "type": "proxy"}
        ]
        
        return ArchitectureState(
            name="Current Architecture",
            description="Current state of XNAi Foundation architecture",
            components=components,
            agent_accounts=agent_accounts,
            relationships=relationships,
            created_at=datetime.now().isoformat()
        )
    
    def build_target_architecture(self) -> ArchitectureState:
        """Build target architecture state with multi-agent coordination"""
        components = [
            # Core Services
            Component(
                id="chainlit_app",
                name="Chainlit App",
                type="web_service",
                description="Main web interface for RAG application",
                technologies=["Python", "Chainlit", "FastAPI"],
                connections=["api_server", "qdrant", "faiss", "agent_coordinator"],
                status="target",
                priority=1
            ),
            Component(
                id="api_server",
                name="API Server",
                type="web_service",
                description="FastAPI backend server with multi-agent integration",
                technologies=["Python", "FastAPI", "uvicorn", "Redis Streams"],
                connections=["postgres", "redis", "qdrant", "faiss", "agent_coordinator", "health_monitor"],
                status="target",
                priority=1
            ),
            
            # Multi-Agent Coordination
            Component(
                id="agent_coordinator",
                name="Agent Coordinator",
                type="service",
                description="Coordinates multiple CLI agent accounts",
                technologies=["Python", "Redis Streams", "AsyncIO"],
                connections=["redis", "agent_accounts", "task_coordinator", "health_monitor"],
                status="target",
                priority=1
            ),
            Component(
                id="task_coordinator",
                name="Task Coordinator",
                type="service",
                description="Manages complex multi-step tasks across agents",
                technologies=["Python", "Redis", "Workflow Engine"],
                connections=["agent_coordinator", "agent_accounts"],
                status="target",
                priority=1
            ),
            Component(
                id="health_monitor",
                name="Health Monitor",
                type="service",
                description="Monitors agent health and performance",
                technologies=["Python", "Redis", "Metrics"],
                connections=["agent_coordinator", "agent_accounts", "prometheus"],
                status="target",
                priority=1
            ),
            Component(
                id="agent_account_manager",
                name="Account Manager",
                type="service",
                description="Manages multiple agent account configurations",
                technologies=["Python", "Encryption", "YAML"],
                connections=["agent_coordinator", "agent_accounts"],
                status="target",
                priority=1
            ),
            
            # Agent Accounts (External)
            Component(
                id="agent_accounts",
                name="CLI Agent Accounts",
                type="external_service",
                description="Multiple CLI agent accounts (Cline, Copilot, OpenCode, Gemini)",
                technologies=["CLI Tools", "API Keys", "Rate Limiting"],
                connections=["agent_coordinator", "task_coordinator"],
                status="target",
                priority=1
            ),
            
            # Databases
            Component(
                id="postgres",
                name="PostgreSQL",
                type="database",
                description="Primary relational database",
                technologies=["PostgreSQL", "Alembic"],
                connections=["api_server", "agent_coordinator"],
                status="target",
                priority=1
            ),
            Component(
                id="qdrant",
                name="Qdrant",
                type="vector_database",
                description="Vector database for embeddings with FAISS integration",
                technologies=["Qdrant", "Docker", "FAISS"],
                connections=["api_server", "faiss", "agent_coordinator"],
                status="target",
                priority=1
            ),
            
            # Enhanced FAISS Integration
            Component(
                id="faiss",
                name="FAISS (Ryzen Optimized)",
                type="vector_database",
                description="Local vector database optimized for Ryzen processors",
                technologies=["FAISS", "NumPy", "Vulkan", "Ryzen Optimizations"],
                connections=["api_server", "qdrant", "agent_coordinator"],
                status="target",
                priority=1
            ),
            
            # Caching & Queues
            Component(
                id="redis",
                name="Redis (Enhanced)",
                type="cache",
                description="Enhanced caching with Streams for agent coordination",
                technologies=["Redis", "Streams", "Pub/Sub"],
                connections=["api_server", "agent_coordinator", "task_coordinator", "health_monitor"],
                status="target",
                priority=1
            ),
            Component(
                id="celery",
                name="Celery (Enhanced)",
                type="queue",
                description="Enhanced task queue with agent task support",
                technologies=["Celery", "Redis", "Agent Tasks"],
                connections=["api_server", "redis", "agent_coordinator"],
                status="target",
                priority=2
            ),
            
            # Storage
            Component(
                id="minio",
                name="MinIO",
                type="storage",
                description="Object storage for documents and models",
                technologies=["MinIO", "S3 API"],
                connections=["api_server", "agent_coordinator"],
                status="target",
                priority=2
            ),
            
            # Enhanced Monitoring
            Component(
                id="prometheus",
                name="Prometheus (Enhanced)",
                type="monitoring",
                description="Enhanced metrics collection including agent metrics",
                technologies=["Prometheus", "Grafana", "Agent Metrics"],
                connections=["api_server", "chainlit_app", "agent_coordinator", "health_monitor"],
                status="target",
                priority=1
            ),
            Component(
                id="grafana",
                name="Grafana (Enhanced)",
                type="monitoring",
                description="Enhanced visualization with agent performance dashboards",
                technologies=["Grafana", "Prometheus", "Agent Dashboards"],
                connections=["prometheus"],
                status="target",
                priority=1
            ),
            
            # Infrastructure
            Component(
                id="nginx",
                name="Nginx (Enhanced)",
                type="proxy",
                description="Enhanced reverse proxy with agent traffic routing",
                technologies=["Nginx", "SSL/TLS", "Load Balancing"],
                connections=["chainlit_app", "api_server", "agent_coordinator"],
                status="target",
                priority=2
            ),
            Component(
                id="docker",
                name="Docker (Enhanced)",
                type="containerization",
                description="Enhanced containerization with agent coordination support",
                technologies=["Docker", "Docker Compose", "Multi-Agent"],
                connections=["all_services"],
                status="target",
                priority=2
            )
        ]
        
        agent_accounts = [
            AgentAccount(
                account_id="primary_account",
                name="Primary Account",
                type="primary",
                capabilities=["full_access", "admin", "coordination"],
                status="active",
                priority=1
            ),
            AgentAccount(
                account_id="subagent_1",
                name="Subagent 1",
                type="subagent",
                capabilities=["code_generation", "documentation"],
                status="active",
                priority=2
            ),
            AgentAccount(
                account_id="subagent_2",
                name="Subagent 2",
                type="subagent",
                capabilities=["testing", "analysis"],
                status="active",
                priority=2
            ),
            AgentAccount(
                account_id="coordinator_agent",
                name="Coordinator Agent",
                type="coordinator",
                capabilities=["task_coordination", "workflow_management"],
                status="active",
                priority=1
            ),
            AgentAccount(
                account_id="validator_agent",
                name="Validator Agent",
                type="validator",
                capabilities=["validation", "quality_assurance"],
                status="active",
                priority=1
            )
        ]
        
        relationships = [
            # Core service relationships
            {"source": "chainlit_app", "target": "api_server", "type": "http"},
            {"source": "api_server", "target": "postgres", "type": "database"},
            {"source": "api_server", "target": "qdrant", "type": "vector"},
            {"source": "api_server", "target": "faiss", "type": "vector"},
            {"source": "api_server", "target": "redis", "type": "cache"},
            {"source": "api_server", "target": "celery", "type": "queue"},
            {"source": "api_server", "target": "agent_coordinator", "type": "coordination"},
            
            # Multi-agent relationships
            {"source": "agent_coordinator", "target": "redis", "type": "streams"},
            {"source": "agent_coordinator", "target": "agent_accounts", "type": "api"},
            {"source": "agent_coordinator", "target": "task_coordinator", "type": "coordination"},
            {"source": "agent_coordinator", "target": "health_monitor", "type": "monitoring"},
            {"source": "agent_coordinator", "target": "account_manager", "type": "management"},
            
            {"source": "task_coordinator", "target": "agent_coordinator", "type": "workflow"},
            {"source": "task_coordinator", "target": "agent_accounts", "type": "task_assignment"},
            
            {"source": "health_monitor", "target": "agent_coordinator", "type": "metrics"},
            {"source": "health_monitor", "target": "agent_accounts", "type": "monitoring"},
            {"source": "health_monitor", "target": "prometheus", "type": "metrics"},
            
            {"source": "account_manager", "target": "agent_coordinator", "type": "management"},
            {"source": "account_manager", "target": "agent_accounts", "type": "configuration"},
            
            # Enhanced database relationships
            {"source": "qdrant", "target": "faiss", "type": "sync"},
            {"source": "postgres", "target": "agent_coordinator", "type": "metadata"},
            
            # Enhanced storage relationships
            {"source": "api_server", "target": "minio", "type": "storage"},
            {"source": "agent_coordinator", "target": "minio", "type": "storage"},
            
            # Enhanced monitoring relationships
            {"source": "api_server", "target": "prometheus", "type": "metrics"},
            {"source": "chainlit_app", "target": "prometheus", "type": "metrics"},
            {"source": "agent_coordinator", "target": "prometheus", "type": "agent_metrics"},
            {"source": "health_monitor", "target": "prometheus", "type": "health_metrics"},
            {"source": "prometheus", "target": "grafana", "type": "visualization"},
            
            # Enhanced infrastructure relationships
            {"source": "nginx", "target": "chainlit_app", "type": "proxy"},
            {"source": "nginx", "target": "api_server", "type": "proxy"},
            {"source": "nginx", "target": "agent_coordinator", "type": "proxy"}
        ]
        
        return ArchitectureState(
            name="Target Architecture",
            description="Target state with multi-agent coordination and enhanced FAISS integration",
            components=components,
            agent_accounts=agent_accounts,
            relationships=relationships,
            created_at=datetime.now().isoformat()
        )
    
    def generate_mermaid_diagram(self, architecture: ArchitectureState, diagram_type: str = "overview") -> str:
        """
        Generate Mermaid diagram for architecture
        
        Args:
            architecture: Architecture state to visualize
            diagram_type: Type of diagram (overview, components, agents)
            
        Returns:
            Mermaid diagram string
        """
        if diagram_type == "overview":
            return self._generate_overview_diagram(architecture)
        elif diagram_type == "components":
            return self._generate_components_diagram(architecture)
        elif diagram_type == "agents":
            return self._generate_agents_diagram(architecture)
        else:
            return self._generate_overview_diagram(architecture)
    
    def _generate_overview_diagram(self, architecture: ArchitectureState) -> str:
        """Generate overview diagram showing all components and relationships"""
        mermaid = ["graph TB"]
        mermaid.append(f"    subgraph {architecture.name.replace(' ', '_')}")
        mermaid.append(f"        title[{architecture.name}]")
        mermaid.append(f"        description[{architecture.description}]")
        
        # Group components by type
        component_groups = {}
        for component in architecture.components:
            if component.type not in component_groups:
                component_groups[component.type] = []
            component_groups[component.type].append(component)
        
        # Add component groups
        for group_type, components in component_groups.items():
            group_name = group_type.replace('_', ' ').title()
            mermaid.append(f"        subgraph {group_type}_group[📁 {group_name}]")
            
            for component in components:
                status_icon = "🟢" if component.status == "current" else "🔵"
                component_label = f"{status_icon} {component.name}"
                mermaid.append(f"            {component.id}[{component_label}]")
            
            mermaid.append("        end")
        
        # Add agent accounts
        if architecture.agent_accounts:
            mermaid.append("        subgraph agents_group[🤖 Agent Accounts]")
            for agent in architecture.agent_accounts:
                status_icon = "🟢" if agent.status == "active" else "🔴"
                agent_label = f"{status_icon} {agent.name} ({agent.type})"
                mermaid.append(f"            agent_{agent.account_id}[{agent_label}]")
            mermaid.append("        end")
        
        # Add relationships
        for relationship in architecture.relationships:
            source = relationship['source']
            target = relationship['target']
            rel_type = relationship['type']
            
            # Map relationship types to styles
            style = ""
            if rel_type == "http":
                style = "--"
            elif rel_type == "database":
                style = "=="
            elif rel_type == "vector":
                style = "..>"
            elif rel_type == "coordination":
                style = "==>"
            elif rel_type == "monitoring":
                style = "-.-"
            else:
                style = "-->"
            
            mermaid.append(f"        {source} {style} {target}")
        
        mermaid.append("    end")
        
        return "\n".join(mermaid)
    
    def _generate_components_diagram(self, architecture: ArchitectureState) -> str:
        """Generate detailed components diagram"""
        mermaid = ["graph TB"]
        mermaid.append(f"    subgraph {architecture.name.replace(' ', '_')}_components")
        
        # Group by priority
        for priority in range(1, 4):
            priority_components = [c for c in architecture.components if c.priority == priority]
            if priority_components:
                mermaid.append(f"        subgraph priority_{priority}[Priority {priority}]")
                for component in priority_components:
                    tech_list = ", ".join(component.technologies[:3])  # Show first 3 technologies
                    component_label = f"{component.name}<br/>[{tech_list}]"
                    mermaid.append(f"            {component.id}[{component_label}]")
                mermaid.append("        end")
        
        # Add relationships
        for relationship in architecture.relationships:
            source = relationship['source']
            target = relationship['target']
            mermaid.append(f"        {source} --> {target}")
        
        mermaid.append("    end")
        
        return "\n".join(mermaid)
    
    def _generate_agents_diagram(self, architecture: ArchitectureState) -> str:
        """Generate agent coordination diagram"""
        mermaid = ["graph TB"]
        mermaid.append(f"    subgraph {architecture.name.replace(' ', '_')}_agents")
        
        # Agent coordination services
        mermaid.append("        subgraph coordination_services[🤖 Coordination Services]")
        mermaid.append("            coordinator[Agent Coordinator]")
        mermaid.append("            task_coord[Task Coordinator]")
        mermaid.append("            health_mon[Health Monitor]")
        mermaid.append("            account_mgr[Account Manager]")
        mermaid.append("        end")
        
        # Agent accounts
        mermaid.append("        subgraph agent_accounts[👤 Agent Accounts]")
        for agent in architecture.agent_accounts:
            agent_label = f"{agent.name}<br/>({agent.type})"
            mermaid.append(f"            agent_{agent.account_id}[{agent_label}]")
        mermaid.append("        end")
        
        # Relationships
        mermaid.append("        coordinator --> task_coord")
        mermaid.append("        coordinator --> health_mon")
        mermaid.append("        coordinator --> account_mgr")
        
        for agent in architecture.agent_accounts:
            mermaid.append(f"        coordinator --> agent_{agent.account_id}")
            mermaid.append(f"        task_coord --> agent_{agent.account_id}")
            mermaid.append(f"        health_mon -.-> agent_{agent.account_id}")
        
        mermaid.append("    end")
        
        return "\n".join(mermaid)
    
    def save_diagram(self, diagram_content: str, filename: str, format: str = "svg") -> Path:
        """
        Save diagram to file using Mermaid CLI
        
        Args:
            diagram_content: Mermaid diagram content
            filename: Output filename (without extension)
            format: Output format (svg, png, pdf)
            
        Returns:
            Path to saved file
        """
        # Save Mermaid file
        mermaid_file = self.output_dir / f"{filename}.mmd"
        with open(mermaid_file, 'w') as f:
            f.write(diagram_content)
        
        # Convert to desired format using Mermaid CLI
        output_file = self.output_dir / f"{filename}.{format}"
        
        try:
            # Check if mmdc is available
            result = subprocess.run(
                ["mmdc", "-i", str(mermaid_file), "-o", str(output_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Generated diagram: {output_file}")
                return output_file
            else:
                logger.error(f"Mermaid CLI error: {result.stderr}")
                # Fall back to saving as .mmd only
                return mermaid_file
        
        except FileNotFoundError:
            logger.warning("Mermaid CLI (mmdc) not found, saving as .mmd only")
            return mermaid_file
    
    def generate_architecture_report(self) -> Dict[str, Any]:
        """Generate comprehensive architecture report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "current_state": {
                "name": self.current_state.name,
                "description": self.current_state.description,
                "component_count": len(self.current_state.components),
                "agent_count": len(self.current_state.agent_accounts),
                "key_improvements": [
                    "Multi-agent coordination system",
                    "Enhanced FAISS integration with Ryzen optimization",
                    "Agent health monitoring and management",
                    "Task coordination and workflow management",
                    "Enhanced monitoring with agent metrics"
                ]
            },
            "target_state": {
                "name": self.target_state.name,
                "description": self.target_state.description,
                "component_count": len(self.target_state.components),
                "agent_count": len(self.target_state.agent_accounts),
                "new_components": [
                    "Agent Coordinator Service",
                    "Task Coordinator Service", 
                    "Health Monitor Service",
                    "Account Manager Service",
                    "Enhanced CLI Agent Accounts"
                ],
                "enhanced_components": [
                    "API Server (multi-agent integration)",
                    "Redis (Streams support)",
                    "Prometheus (agent metrics)",
                    "FAISS (Ryzen optimization)"
                ]
            },
            "migration_path": [
                "Phase 1: Deploy agent coordination infrastructure",
                "Phase 2: Implement agent account management",
                "Phase 3: Deploy health monitoring system",
                "Phase 4: Integrate task coordination",
                "Phase 5: Enhance existing services",
                "Phase 6: Optimize FAISS for Ryzen"
            ],
            "diagrams_generated": []
        }
        
        return report
    
    async def generate_all_diagrams(self) -> Dict[str, Path]:
        """Generate all architecture diagrams"""
        if not self.current_state or not self.target_state:
            await self.load_config()
            self.current_state = self.build_current_architecture()
            self.target_state = self.build_target_architecture()
        
        diagrams = {}
        
        # Generate current state diagrams
        current_overview = self.generate_mermaid_diagram(self.current_state, "overview")
        diagrams['current_overview'] = self.save_diagram(current_overview, "current_architecture_overview")
        
        current_components = self.generate_mermaid_diagram(self.current_state, "components")
        diagrams['current_components'] = self.save_diagram(current_components, "current_architecture_components")
        
        # Generate target state diagrams
        target_overview = self.generate_mermaid_diagram(self.target_state, "overview")
        diagrams['target_overview'] = self.save_diagram(target_overview, "target_architecture_overview")
        
        target_components = self.generate_mermaid_diagram(self.target_state, "components")
        diagrams['target_components'] = self.save_diagram(target_components, "target_architecture_components")
        
        target_agents = self.generate_mermaid_diagram(self.target_state, "agents")
        diagrams['target_agents'] = self.save_diagram(target_agents, "target_architecture_agents")
        
        # Generate comparison diagram
        comparison_diagram = self.generate_comparison_diagram()
        diagrams['comparison'] = self.save_diagram(comparison_diagram, "architecture_comparison")
        
        # Generate architecture report
        report = self.generate_architecture_report()
        report_file = self.output_dir / "architecture_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        diagrams['report'] = report_file
        
        logger.info(f"Generated {len(diagrams)} architecture diagrams and report")
        return diagrams
    
    def generate_comparison_diagram(self) -> str:
        """Generate comparison diagram showing current vs target"""
        mermaid = ["graph TB"]
        mermaid.append("    subgraph comparison[Architecture Comparison]")
        
        # Current state
        mermaid.append("        subgraph current[Current Architecture]")
        mermaid.append("            current_api[API Server]")
        mermaid.append("            current_qdrant[Qdrant]")
        mermaid.append("            current_faiss[FAISS]")
        mermaid.append("            current_redis[Redis]")
        mermaid.append("            current_postgres[PostgreSQL]")
        mermaid.append("        end")
        
        # Target state
        mermaid.append("        subgraph target[Target Architecture]")
        mermaid.append("            target_api[API Server (Enhanced)]")
        mermaid.append("            target_coordinator[Agent Coordinator]")
        mermaid.append("            target_task[Task Coordinator]")
        mermaid.append("            target_health[Health Monitor]")
        mermaid.append("            target_qdrant[Qdrant (Enhanced)]")
        mermaid.append("            target_faiss[FAISS (Ryzen Optimized)]")
        mermaid.append("            target_redis[Redis (Streams)]")
        mermaid.append("            target_postgres[PostgreSQL]")
        mermaid.append("            target_agents[CLI Agent Accounts]")
        mermaid.append("        end")
        
        # Migration arrows
        mermaid.append("        current_api -.-> target_api")
        mermaid.append("        current_qdrant -.-> target_qdrant")
        mermaid.append("        current_faiss -.-> target_faiss")
        mermaid.append("        current_redis -.-> target_redis")
        mermaid.append("        current_postgres -.-> target_postgres")
        
        # New components
        mermaid.append("        target_api --> target_coordinator")
        mermaid.append("        target_coordinator --> target_task")
        mermaid.append("        target_coordinator --> target_health")
        mermaid.append("        target_coordinator --> target_agents")
        
        mermaid.append("    end")
        
        return "\n".join(mermaid)


async def main():
    """Main entry point for testing"""
    generator = ArchitectureDiagramGenerator()
    
    # Build architecture states
    generator.current_state = generator.build_current_architecture()
    generator.target_state = generator.build_target_architecture()
    
    # Generate all diagrams
    diagrams = await generator.generate_all_diagrams()
    
    print(f"Generated {len(diagrams)} diagrams:")
    for name, path in diagrams.items():
        print(f"  {name}: {path}")
    
    # Print architecture summary
    print("\nArchitecture Summary:")
    print(f"Current state: {generator.current_state.name}")
    print(f"  - {len(generator.current_state.components)} components")
    print(f"  - {len(generator.current_state.agent_accounts)} agent accounts")
    
    print(f"Target state: {generator.target_state.name}")
    print(f"  - {len(generator.target_state.components)} components")
    print(f"  - {len(generator.target_state.agent_accounts)} agent accounts")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())