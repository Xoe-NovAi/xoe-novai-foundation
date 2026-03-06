#!/usr/bin/env python3
"""
Enhanced Monitoring System for XNAi Foundation

This script implements comprehensive monitoring for multi-agent coordination,
FAISS performance, and system health with advanced metrics collection and alerting.

Author: XNAi Foundation
License: AGPL-3.0-only
"""

import asyncio
import json
import logging
import time
import psutil
import GPUtil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, asdict
import redis.asyncio as redis
import yaml
from prometheus_client import Gauge, Counter, Histogram, start_http_server
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    agent_id: str
    timestamp: float
    status: str  # active, idle, busy, failed
    task_count: int
    success_rate: float
    avg_response_time: float
    memory_usage: float
    cpu_usage: float
    error_count: int
    queue_length: int


@dataclass
class FAISSMetrics:
    """FAISS performance metrics"""
    timestamp: float
    index_size: int
    memory_usage: float
    query_latency: float
    index_build_time: float
    recall_rate: float
    throughput: float
    cpu_usage: float
    gpu_usage: Optional[float]


@dataclass
class SystemMetrics:
    """System-level metrics"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    redis_connections: int
    postgres_connections: int


@dataclass
class CoordinationMetrics:
    """Multi-agent coordination metrics"""
    timestamp: float
    total_agents: int
    active_agents: int
    coordination_latency: float
    task_distribution_balance: float
    communication_overhead: float
    workflow_completion_rate: float


class EnhancedMonitoringSystem:
    """Enhanced monitoring system for XNAi Foundation"""
    
    def __init__(self, config_path: str = "configs/multi-agent-config.yaml"):
        """
        Initialize the enhanced monitoring system
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config: Optional[Dict] = None
        
        # Redis connection
        self.redis_client: Optional[redis.Redis] = None
        
        # Prometheus metrics
        self.setup_prometheus_metrics()
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # Metrics storage
        self.agent_metrics_history: List[AgentMetrics] = []
        self.faiss_metrics_history: List[FAISSMetrics] = []
        self.system_metrics_history: List[SystemMetrics] = []
        self.coordination_metrics_history: List[CoordinationMetrics] = []
        
        # Alerting
        self.alert_thresholds: Dict[str, float] = {}
        self.alert_handlers: List[Callable[[str, Dict], Awaitable[None]]] = []
        
        # Configuration
        self.monitoring_interval = 30  # seconds
        self.history_retention_hours = 24
        self.alert_cooldown_minutes = 5
    
    async def load_config(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            self.config = config_data.get('monitoring', {})
            
            # Update monitoring settings
            if 'enhanced' in self.config:
                enhanced_config = self.config['enhanced']
                self.monitoring_interval = enhanced_config.get('interval', 30)
                self.history_retention_hours = enhanced_config.get('retention_hours', 24)
                self.alert_cooldown_minutes = enhanced_config.get('alert_cooldown', 5)
            
            # Load alert thresholds
            if 'alert_thresholds' in self.config:
                self.alert_thresholds = self.config['alert_thresholds']
            
            logger.info("Loaded enhanced monitoring configuration")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics"""
        # Agent metrics
        self.agent_status_gauge = Gauge('xnai_agent_status', 'Agent status', ['agent_id'])
        self.agent_task_count = Gauge('xnai_agent_task_count', 'Agent task count', ['agent_id'])
        self.agent_success_rate = Gauge('xnai_agent_success_rate', 'Agent success rate', ['agent_id'])
        self.agent_response_time = Histogram('xnai_agent_response_time', 'Agent response time', ['agent_id'])
        self.agent_memory_usage = Gauge('xnai_agent_memory_usage', 'Agent memory usage', ['agent_id'])
        self.agent_cpu_usage = Gauge('xnai_agent_cpu_usage', 'Agent CPU usage', ['agent_id'])
        self.agent_error_count = Counter('xnai_agent_error_count', 'Agent error count', ['agent_id'])
        self.agent_queue_length = Gauge('xnai_agent_queue_length', 'Agent queue length', ['agent_id'])
        
        # FAISS metrics
        self.faiss_index_size = Gauge('xnai_faiss_index_size', 'FAISS index size')
        self.faiss_memory_usage = Gauge('xnai_faiss_memory_usage', 'FAISS memory usage')
        self.faiss_query_latency = Histogram('xnai_faiss_query_latency', 'FAISS query latency')
        self.faiss_recall_rate = Gauge('xnai_faiss_recall_rate', 'FAISS recall rate')
        self.faiss_throughput = Gauge('xnai_faiss_throughput', 'FAISS throughput')
        self.faiss_cpu_usage = Gauge('xnai_faiss_cpu_usage', 'FAISS CPU usage')
        self.faiss_gpu_usage = Gauge('xnai_faiss_gpu_usage', 'FAISS GPU usage')
        
        # System metrics
        self.system_cpu_usage = Gauge('xnai_system_cpu_usage', 'System CPU usage')
        self.system_memory_usage = Gauge('xnai_system_memory_usage', 'System memory usage')
        self.system_disk_usage = Gauge('xnai_system_disk_usage', 'System disk usage')
        self.system_network_io = Gauge('xnai_system_network_io', 'System network I/O', ['direction'])
        self.system_active_connections = Gauge('xnai_system_active_connections', 'System active connections')
        
        # Coordination metrics
        self.coordination_total_agents = Gauge('xnai_coordination_total_agents', 'Total coordinated agents')
        self.coordination_active_agents = Gauge('xnai_coordination_active_agents', 'Active coordinated agents')
        self.coordination_latency = Histogram('xnai_coordination_latency', 'Coordination latency')
        self.coordination_balance = Gauge('xnai_coordination_balance', 'Task distribution balance')
        self.coordination_overhead = Gauge('xnai_coordination_overhead', 'Communication overhead')
        self.coordination_completion_rate = Gauge('xnai_coordination_completion_rate', 'Workflow completion rate')
    
    async def initialize(self) -> None:
        """Initialize the monitoring system"""
        await self.load_config()
        
        # Initialize Redis connection
        await self._init_redis()
        
        # Start Prometheus server
        start_http_server(8000)
        
        logger.info("Enhanced monitoring system initialized")
    
    async def _init_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                os.getenv('REDIS_URL', 'redis://localhost:6379'),
                decode_responses=False
            )
            await self.redis_client.ping()
            logger.info("Redis connection established for monitoring")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def start_monitoring(self) -> None:
        """Start the enhanced monitoring system"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        
        # Start monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._monitor_agents()),
            asyncio.create_task(self._monitor_faiss()),
            asyncio.create_task(self._monitor_system()),
            asyncio.create_task(self._monitor_coordination()),
            asyncio.create_task(self._cleanup_history()),
            asyncio.create_task(self._check_alerts())
        ]
        
        logger.info("Enhanced monitoring system started")
    
    async def stop_monitoring(self) -> None:
        """Stop the enhanced monitoring system"""
        if not self.monitoring_active:
            logger.warning("Monitoring is not active")
            return
        
        self.monitoring_active = False
        
        # Cancel monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        logger.info("Enhanced monitoring system stopped")
    
    async def _monitor_agents(self) -> None:
        """Monitor agent performance metrics"""
        while self.monitoring_active:
            try:
                # Get agent metrics from Redis
                agent_metrics = await self._collect_agent_metrics()
                
                # Update Prometheus metrics
                for metric in agent_metrics:
                    self.agent_status_gauge.labels(agent_id=metric.agent_id).set(1 if metric.status == 'active' else 0)
                    self.agent_task_count.labels(agent_id=metric.agent_id).set(metric.task_count)
                    self.agent_success_rate.labels(agent_id=metric.agent_id).set(metric.success_rate)
                    self.agent_response_time.labels(agent_id=metric.agent_id).observe(metric.avg_response_time)
                    self.agent_memory_usage.labels(agent_id=metric.agent_id).set(metric.memory_usage)
                    self.agent_cpu_usage.labels(agent_id=metric.agent_id).set(metric.cpu_usage)
                    self.agent_error_count.labels(agent_id=metric.agent_id).inc(metric.error_count)
                    self.agent_queue_length.labels(agent_id=metric.agent_id).set(metric.queue_length)
                
                # Store in history
                self.agent_metrics_history.extend(agent_metrics)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring agents: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_agent_metrics(self) -> List[AgentMetrics]:
        """Collect agent metrics from Redis"""
        metrics = []
        
        try:
            # Get agent keys from Redis
            agent_keys = await self.redis_client.keys("agent:*:metrics")
            
            for key in agent_keys:
                data = await self.redis_client.get(key)
                if data:
                    agent_data = json.loads(data.decode())
                    
                    metric = AgentMetrics(
                        agent_id=agent_data.get('agent_id', ''),
                        timestamp=agent_data.get('timestamp', time.time()),
                        status=agent_data.get('status', 'unknown'),
                        task_count=agent_data.get('task_count', 0),
                        success_rate=agent_data.get('success_rate', 0.0),
                        avg_response_time=agent_data.get('avg_response_time', 0.0),
                        memory_usage=agent_data.get('memory_usage', 0.0),
                        cpu_usage=agent_data.get('cpu_usage', 0.0),
                        error_count=agent_data.get('error_count', 0),
                        queue_length=agent_data.get('queue_length', 0)
                    )
                    
                    metrics.append(metric)
        
        except Exception as e:
            logger.error(f"Error collecting agent metrics: {e}")
        
        return metrics
    
    async def _monitor_faiss(self) -> None:
        """Monitor FAISS performance metrics"""
        while self.monitoring_active:
            try:
                # Collect FAISS metrics
                faiss_metrics = await self._collect_faiss_metrics()
                
                # Update Prometheus metrics
                self.faiss_index_size.set(faiss_metrics.index_size)
                self.faiss_memory_usage.set(faiss_metrics.memory_usage)
                self.faiss_query_latency.observe(faiss_metrics.query_latency)
                self.faiss_recall_rate.set(faiss_metrics.recall_rate)
                self.faiss_throughput.set(faiss_metrics.throughput)
                self.faiss_cpu_usage.set(faiss_metrics.cpu_usage)
                
                if faiss_metrics.gpu_usage is not None:
                    self.faiss_gpu_usage.set(faiss_metrics.gpu_usage)
                
                # Store in history
                self.faiss_metrics_history.append(faiss_metrics)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring FAISS: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_faiss_metrics(self) -> FAISSMetrics:
        """Collect FAISS metrics"""
        try:
            # This would integrate with the FAISS monitoring in the API
            # For now, return mock data
            return FAISSMetrics(
                timestamp=time.time(),
                index_size=1000000,
                memory_usage=psutil.virtual_memory().percent,
                query_latency=0.05,
                index_build_time=10.0,
                recall_rate=0.95,
                throughput=1000.0,
                cpu_usage=psutil.cpu_percent(),
                gpu_usage=self._get_gpu_usage()
            )
        except Exception as e:
            logger.error(f"Error collecting FAISS metrics: {e}")
            return FAISSMetrics(
                timestamp=time.time(),
                index_size=0,
                memory_usage=0.0,
                query_latency=0.0,
                index_build_time=0.0,
                recall_rate=0.0,
                throughput=0.0,
                cpu_usage=0.0,
                gpu_usage=None
            )
    
    def _get_gpu_usage(self) -> Optional[float]:
        """Get GPU usage percentage"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].load * 100
            return None
        except Exception:
            return None
    
    async def _monitor_system(self) -> None:
        """Monitor system-level metrics"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                system_metrics = await self._collect_system_metrics()
                
                # Update Prometheus metrics
                self.system_cpu_usage.set(system_metrics.cpu_usage)
                self.system_memory_usage.set(system_metrics.memory_usage)
                self.system_disk_usage.set(system_metrics.disk_usage)
                
                for direction, value in system_metrics.network_io.items():
                    self.system_network_io.labels(direction=direction).set(value)
                
                self.system_active_connections.set(system_metrics.active_connections)
                
                # Store in history
                self.system_metrics_history.append(system_metrics)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring system: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Active connections
            connections = len(psutil.net_connections())
            
            return SystemMetrics(
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                active_connections=connections,
                redis_connections=0,  # Would need Redis connection count
                postgres_connections=0  # Would need PostgreSQL connection count
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=time.time(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                active_connections=0,
                redis_connections=0,
                postgres_connections=0
            )
    
    async def _monitor_coordination(self) -> None:
        """Monitor multi-agent coordination metrics"""
        while self.monitoring_active:
            try:
                # Collect coordination metrics
                coordination_metrics = await self._collect_coordination_metrics()
                
                # Update Prometheus metrics
                self.coordination_total_agents.set(coordination_metrics.total_agents)
                self.coordination_active_agents.set(coordination_metrics.active_agents)
                self.coordination_latency.observe(coordination_metrics.coordination_latency)
                self.coordination_balance.set(coordination_metrics.task_distribution_balance)
                self.coordination_overhead.set(coordination_metrics.communication_overhead)
                self.coordination_completion_rate.set(coordination_metrics.workflow_completion_rate)
                
                # Store in history
                self.coordination_metrics_history.append(coordination_metrics)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring coordination: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_coordination_metrics(self) -> CoordinationMetrics:
        """Collect coordination metrics"""
        try:
            # Get coordination data from Redis
            coordination_data = await self.redis_client.get("coordination:metrics")
            
            if coordination_data:
                data = json.loads(coordination_data.decode())
                return CoordinationMetrics(
                    timestamp=data.get('timestamp', time.time()),
                    total_agents=data.get('total_agents', 0),
                    active_agents=data.get('active_agents', 0),
                    coordination_latency=data.get('coordination_latency', 0.0),
                    task_distribution_balance=data.get('task_distribution_balance', 0.0),
                    communication_overhead=data.get('communication_overhead', 0.0),
                    workflow_completion_rate=data.get('workflow_completion_rate', 0.0)
                )
            else:
                # Calculate from agent metrics
                active_agents = len([m for m in self.agent_metrics_history if m.status == 'active'])
                total_agents = len(set(m.agent_id for m in self.agent_metrics_history))
                
                return CoordinationMetrics(
                    timestamp=time.time(),
                    total_agents=total_agents,
                    active_agents=active_agents,
                    coordination_latency=0.1,  # Mock value
                    task_distribution_balance=0.8,  # Mock value
                    communication_overhead=0.05,  # Mock value
                    workflow_completion_rate=0.9  # Mock value
                )
        
        except Exception as e:
            logger.error(f"Error collecting coordination metrics: {e}")
            return CoordinationMetrics(
                timestamp=time.time(),
                total_agents=0,
                active_agents=0,
                coordination_latency=0.0,
                task_distribution_balance=0.0,
                communication_overhead=0.0,
                workflow_completion_rate=0.0
            )
    
    async def _cleanup_history(self) -> None:
        """Clean up old metrics history"""
        while self.monitoring_active:
            try:
                cutoff_time = time.time() - (self.history_retention_hours * 3600)
                
                # Clean up agent metrics
                self.agent_metrics_history = [
                    m for m in self.agent_metrics_history if m.timestamp > cutoff_time
                ]
                
                # Clean up FAISS metrics
                self.faiss_metrics_history = [
                    m for m in self.faiss_metrics_history if m.timestamp > cutoff_time
                ]
                
                # Clean up system metrics
                self.system_metrics_history = [
                    m for m in self.system_metrics_history if m.timestamp > cutoff_time
                ]
                
                # Clean up coordination metrics
                self.coordination_metrics_history = [
                    m for m in self.coordination_metrics_history if m.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error cleaning up history: {e}")
                await asyncio.sleep(3600)
    
    async def _check_alerts(self) -> None:
        """Check for alert conditions"""
        while self.monitoring_active:
            try:
                # Check agent alerts
                await self._check_agent_alerts()
                
                # Check system alerts
                await self._check_system_alerts()
                
                # Check FAISS alerts
                await self._check_faiss_alerts()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error checking alerts: {e}")
                await asyncio.sleep(60)
    
    async def _check_agent_alerts(self) -> None:
        """Check agent-related alerts"""
        try:
            # Check for failed agents
            failed_agents = [m for m in self.agent_metrics_history if m.status == 'failed']
            if len(failed_agents) > self.alert_thresholds.get('max_failed_agents', 3):
                await self._trigger_alert('high_failed_agents', {
                    'failed_count': len(failed_agents),
                    'threshold': self.alert_thresholds.get('max_failed_agents', 3)
                })
            
            # Check for high error rates
            for agent_id in set(m.agent_id for m in self.agent_metrics_history):
                agent_metrics = [m for m in self.agent_metrics_history if m.agent_id == agent_id]
                if len(agent_metrics) > 0:
                    avg_error_rate = statistics.mean(m.error_count for m in agent_metrics[-10:])
                    if avg_error_rate > self.alert_thresholds.get('max_error_rate', 5):
                        await self._trigger_alert('high_agent_error_rate', {
                            'agent_id': agent_id,
                            'error_rate': avg_error_rate,
                            'threshold': self.alert_thresholds.get('max_error_rate', 5)
                        })
        
        except Exception as e:
            logger.error(f"Error checking agent alerts: {e}")
    
    async def _check_system_alerts(self) -> None:
        """Check system-related alerts"""
        try:
            if len(self.system_metrics_history) > 0:
                latest = self.system_metrics_history[-1]
                
                # Check CPU usage
                if latest.cpu_usage > self.alert_thresholds.get('max_cpu_usage', 80):
                    await self._trigger_alert('high_cpu_usage', {
                        'cpu_usage': latest.cpu_usage,
                        'threshold': self.alert_thresholds.get('max_cpu_usage', 80)
                    })
                
                # Check memory usage
                if latest.memory_usage > self.alert_thresholds.get('max_memory_usage', 85):
                    await self._trigger_alert('high_memory_usage', {
                        'memory_usage': latest.memory_usage,
                        'threshold': self.alert_thresholds.get('max_memory_usage', 85)
                    })
                
                # Check disk usage
                if latest.disk_usage > self.alert_thresholds.get('max_disk_usage', 90):
                    await self._trigger_alert('high_disk_usage', {
                        'disk_usage': latest.disk_usage,
                        'threshold': self.alert_thresholds.get('max_disk_usage', 90)
                    })
        
        except Exception as e:
            logger.error(f"Error checking system alerts: {e}")
    
    async def _check_faiss_alerts(self) -> None:
        """Check FAISS-related alerts"""
        try:
            if len(self.faiss_metrics_history) > 0:
                latest = self.faiss_metrics_history[-1]
                
                # Check query latency
                if latest.query_latency > self.alert_thresholds.get('max_query_latency', 0.5):
                    await self._trigger_alert('high_faiss_latency', {
                        'query_latency': latest.query_latency,
                        'threshold': self.alert_thresholds.get('max_query_latency', 0.5)
                    })
                
                # Check recall rate
                if latest.recall_rate < self.alert_thresholds.get('min_recall_rate', 0.8):
                    await self._trigger_alert('low_faiss_recall', {
                        'recall_rate': latest.recall_rate,
                        'threshold': self.alert_thresholds.get('min_recall_rate', 0.8)
                    })
        
        except Exception as e:
            logger.error(f"Error checking FAISS alerts: {e}")
    
    async def _trigger_alert(self, alert_type: str, data: Dict[str, Any]) -> None:
        """Trigger an alert"""
        try:
            alert_data = {
                'type': alert_type,
                'timestamp': time.time(),
                'data': data
            }
            
            # Store alert in Redis
            await self.redis_client.lpush("alerts", json.dumps(alert_data))
            
            # Call alert handlers
            for handler in self.alert_handlers:
                try:
                    await handler(alert_type, data)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
            
            logger.warning(f"Alert triggered: {alert_type} - {data}")
        
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    def add_alert_handler(self, handler: Callable[[str, Dict], Awaitable[None]]) -> None:
        """Add an alert handler"""
        self.alert_handlers.append(handler)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for dashboard"""
        summary = {
            'timestamp': time.time(),
            'agents': {
                'total': len(set(m.agent_id for m in self.agent_metrics_history)),
                'active': len([m for m in self.agent_metrics_history if m.status == 'active']),
                'failed': len([m for m in self.agent_metrics_history if m.status == 'failed']),
                'avg_success_rate': self._calculate_avg_success_rate(),
                'avg_response_time': self._calculate_avg_response_time()
            },
            'faiss': {
                'index_size': self._get_latest_faiss_metric('index_size', 0),
                'memory_usage': self._get_latest_faiss_metric('memory_usage', 0.0),
                'query_latency': self._get_latest_faiss_metric('query_latency', 0.0),
                'recall_rate': self._get_latest_faiss_metric('recall_rate', 0.0),
                'throughput': self._get_latest_faiss_metric('throughput', 0.0)
            },
            'system': {
                'cpu_usage': self._get_latest_system_metric('cpu_usage', 0.0),
                'memory_usage': self._get_latest_system_metric('memory_usage', 0.0),
                'disk_usage': self._get_latest_system_metric('disk_usage', 0.0),
                'active_connections': self._get_latest_system_metric('active_connections', 0)
            },
            'coordination': {
                'total_agents': self._get_latest_coordination_metric('total_agents', 0),
                'active_agents': self._get_latest_coordination_metric('active_agents', 0),
                'coordination_latency': self._get_latest_coordination_metric('coordination_latency', 0.0),
                'task_distribution_balance': self._get_latest_coordination_metric('task_distribution_balance', 0.0),
                'workflow_completion_rate': self._get_latest_coordination_metric('workflow_completion_rate', 0.0)
            }
        }
        
        return summary
    
    def _calculate_avg_success_rate(self) -> float:
        """Calculate average success rate across all agents"""
        if not self.agent_metrics_history:
            return 0.0
        
        success_rates = [m.success_rate for m in self.agent_metrics_history]
        return statistics.mean(success_rates) if success_rates else 0.0
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time across all agents"""
        if not self.agent_metrics_history:
            return 0.0
        
        response_times = [m.avg_response_time for m in self.agent_metrics_history]
        return statistics.mean(response_times) if response_times else 0.0
    
    def _get_latest_faiss_metric(self, metric_name: str, default: Any) -> Any:
        """Get latest FAISS metric value"""
        if not self.faiss_metrics_history:
            return default
        
        latest = self.faiss_metrics_history[-1]
        return getattr(latest, metric_name, default)
    
    def _get_latest_system_metric(self, metric_name: str, default: Any) -> Any:
        """Get latest system metric value"""
        if not self.system_metrics_history:
            return default
        
        latest = self.system_metrics_history[-1]
        return getattr(latest, metric_name, default)
    
    def _get_latest_coordination_metric(self, metric_name: str, default: Any) -> Any:
        """Get latest coordination metric value"""
        if not self.coordination_metrics_history:
            return default
        
        latest = self.coordination_metrics_history[-1]
        return getattr(latest, metric_name, default)
    
    async def export_metrics_report(self, output_dir: str = "monitoring/reports") -> Path:
        """Export comprehensive metrics report"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        report_data = {
            'summary': self.get_metrics_summary(),
            'agent_history': [asdict(m) for m in self.agent_metrics_history],
            'faiss_history': [asdict(m) for m in self.faiss_metrics_history],
            'system_history': [asdict(m) for m in self.system_metrics_history],
            'coordination_history': [asdict(m) for m in self.coordination_metrics_history]
        }
        
        report_file = output_path / f"metrics_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"Metrics report exported to: {report_file}")
        return report_file


async def main():
    """Main entry point for testing"""
    monitoring = EnhancedMonitoringSystem()
    await monitoring.initialize()
    
    # Add a simple alert handler
    async def simple_alert_handler(alert_type: str, data: Dict):
        print(f"ALERT: {alert_type} - {data}")
    
    monitoring.add_alert_handler(simple_alert_handler)
    
    # Start monitoring
    await monitoring.start_monitoring()
    
    # Run for 5 minutes then stop
    await asyncio.sleep(300)
    await monitoring.stop_monitoring()
    
    # Export report
    await monitoring.export_metrics_report()
    
    print("Enhanced monitoring test completed")


if __name__ == "__main__":
    asyncio.run(main())