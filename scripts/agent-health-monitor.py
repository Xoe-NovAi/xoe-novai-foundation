#!/usr/bin/env python3
"""
Agent Health Monitor for XNAi Foundation

This script monitors the health and performance of all agent accounts,
providing real-time status updates and alerting on issues.

Author: XNAi Foundation
License: AGPL-3.0-only
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path
import redis.asyncio as redis
import yaml
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class HealthMetrics:
    """Health metrics for an agent"""
    agent_id: str
    timestamp: datetime
    status: str
    response_time: float
    success_rate: float
    error_count: int
    memory_usage: float
    cpu_usage: float
    active_tasks: int
    queue_length: int


@dataclass
class Alert:
    """Alert information"""
    agent_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool


class AgentHealthMonitor:
    """Monitors agent health and performance"""
    
    def __init__(self, config_path: str = "configs/multi-agent-config.yaml"):
        """
        Initialize the health monitor
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config: Optional[Dict] = None
        self.redis_client: Optional[redis.Redis] = None
        
        # Health tracking
        self.health_metrics: Dict[str, List[HealthMetrics]] = {}
        self.alerts: List[Alert] = []
        
        # Monitoring configuration
        self.monitoring_interval = 30  # seconds
        self.metrics_retention_hours = 24
        self.alert_thresholds = {
            'response_time': 30.0,  # seconds
            'success_rate': 0.8,    # 80%
            'error_count': 5,
            'memory_usage': 80.0,   # 80%
            'cpu_usage': 80.0       # 80%
        }
        
        # Event handlers
        self.on_health_update: Optional[Callable[[HealthMetrics], None]] = None
        self.on_alert: Optional[Callable[[Alert], None]] = None
        
        # Running state
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
    
    async def load_config(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            self.config = config_data.get('multi_agent', {})
            
            # Update monitoring settings from config
            if 'monitoring' in self.config:
                monitoring_config = self.config['monitoring']
                self.monitoring_interval = monitoring_config.get('interval', 30)
                self.metrics_retention_hours = monitoring_config.get('retention_hours', 24)
            
            if 'alert_thresholds' in self.config:
                self.alert_thresholds.update(self.config['alert_thresholds'])
            
            logger.info("Loaded health monitor configuration")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def initialize(self) -> None:
        """Initialize the health monitor"""
        await self.load_config()
        
        # Initialize Redis connection
        await self._init_redis()
        
        # Load existing metrics and alerts
        await self._load_state()
        
        logger.info("Agent health monitor initialized")
    
    async def _init_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                os.getenv('REDIS_URL', 'redis://localhost:6379'),
                decode_responses=False
            )
            await self.redis_client.ping()
            logger.info("Redis connection established for health monitoring")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def _load_state(self) -> None:
        """Load existing health metrics and alerts from Redis"""
        try:
            # Load health metrics
            metrics_keys = await self.redis_client.keys("health:metrics:*")
            for key in metrics_keys:
                agent_id = key.decode().split(":")[-1]
                metrics_data = await self.redis_client.lrange(key, 0, -1)
                
                metrics_list = []
                for metric_data in metrics_data:
                    metric_dict = json.loads(metric_data.decode())
                    metric_dict['timestamp'] = datetime.fromisoformat(metric_dict['timestamp'])
                    metrics_list.append(HealthMetrics(**metric_dict))
                
                self.health_metrics[agent_id] = metrics_list
            
            # Load alerts
            alerts_data = await self.redis_client.get("health:alerts")
            if alerts_data:
                alerts_list = json.loads(alerts_data.decode())
                for alert_dict in alerts_list:
                    alert_dict['timestamp'] = datetime.fromisoformat(alert_dict['timestamp'])
                    self.alerts.append(Alert(**alert_dict))
            
            logger.info(f"Loaded health state: {len(self.health_metrics)} agents, {len(self.alerts)} alerts")
            
        except Exception as e:
            logger.error(f"Failed to load health state: {e}")
    
    async def start_monitoring(self) -> None:
        """Start the health monitoring loop"""
        if self.running:
            logger.warning("Health monitoring is already running")
            return
        
        self.running = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started agent health monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop the health monitoring loop"""
        if not self.running:
            logger.warning("Health monitoring is not running")
            return
        
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        # Save state before stopping
        await self._save_state()
        logger.info("Stopped agent health monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.running:
            try:
                await self._collect_health_metrics()
                await self._check_alerts()
                await self._cleanup_old_data()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _collect_health_metrics(self) -> None:
        """Collect health metrics from all agents"""
        try:
            # Get list of agents from Redis
            agent_keys = await self.redis_client.keys("agent:*")
            agent_ids = set()
            
            for key in agent_keys:
                key_str = key.decode()
                if key_str.startswith("agent:") and not key_str.endswith(":tasks") and not key_str.endswith(":results"):
                    agent_id = key_str.split(":")[1]
                    agent_ids.add(agent_id)
            
            # Collect metrics for each agent
            for agent_id in agent_ids:
                metrics = await self._get_agent_metrics(agent_id)
                if metrics:
                    await self._update_health_metrics(agent_id, metrics)
        
        except Exception as e:
            logger.error(f"Error collecting health metrics: {e}")
    
    async def _get_agent_metrics(self, agent_id: str) -> Optional[HealthMetrics]:
        """Get health metrics for a specific agent"""
        try:
            # Get agent info from Redis
            agent_info = await self.redis_client.hgetall(f"agent:{agent_id}")
            if not agent_info:
                return None
            
            # Parse agent info
            status = agent_info.get(b'status', b'unknown').decode()
            last_heartbeat_str = agent_info.get(b'last_heartbeat', b'').decode()
            
            # Calculate response time (time since last heartbeat)
            response_time = 0.0
            if last_heartbeat_str:
                last_heartbeat = datetime.fromisoformat(last_heartbeat_str)
                response_time = (datetime.now() - last_heartbeat).total_seconds()
            
            # Get performance metrics
            performance_metrics = json.loads(agent_info.get(b'performance_metrics', b'{}').decode())
            
            # Get queue length
            queue_length = await self.redis_client.llen(f"agent:{agent_id}:tasks")
            
            # Calculate success rate
            total_requests = performance_metrics.get('total_requests', 0)
            successful_requests = performance_metrics.get('successful_requests', 0)
            success_rate = successful_requests / total_requests if total_requests > 0 else 1.0
            
            # Get error count (from failed requests)
            error_count = total_requests - successful_requests
            
            # Simulate memory and CPU usage (would be real metrics in production)
            memory_usage = performance_metrics.get('memory_usage', 0.0)
            cpu_usage = performance_metrics.get('cpu_usage', 0.0)
            
            # Count active tasks
            active_tasks = 1 if agent_info.get(b'current_task') else 0
            
            return HealthMetrics(
                agent_id=agent_id,
                timestamp=datetime.now(),
                status=status,
                response_time=response_time,
                success_rate=success_rate,
                error_count=error_count,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                active_tasks=active_tasks,
                queue_length=queue_length
            )
        
        except Exception as e:
            logger.error(f"Error getting metrics for agent {agent_id}: {e}")
            return None
    
    async def _update_health_metrics(self, agent_id: str, metrics: HealthMetrics) -> None:
        """Update health metrics for an agent"""
        # Add to local storage
        if agent_id not in self.health_metrics:
            self.health_metrics[agent_id] = []
        
        self.health_metrics[agent_id].append(metrics)
        
        # Keep only recent metrics
        cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
        self.health_metrics[agent_id] = [
            m for m in self.health_metrics[agent_id]
            if m.timestamp >= cutoff_time
        ]
        
        # Save to Redis
        metrics_key = f"health:metrics:{agent_id}"
        metrics_data = json.dumps(asdict(metrics), default=str)
        await self.redis_client.lpush(metrics_key, metrics_data)
        await self.redis_client.expire(metrics_key, self.metrics_retention_hours * 3600)  # Set expiry
        
        # Notify health update handler
        if self.on_health_update:
            self.on_health_update(metrics)
        
        logger.debug(f"Updated health metrics for agent {agent_id}")
    
    async def _check_alerts(self) -> None:
        """Check for new alerts based on health metrics"""
        try:
            current_time = datetime.now()
            
            for agent_id, metrics_list in self.health_metrics.items():
                if not metrics_list:
                    continue
                
                latest_metrics = metrics_list[-1]
                
                # Check response time
                if latest_metrics.response_time > self.alert_thresholds['response_time']:
                    await self._create_alert(
                        agent_id, 'high_response_time', 'warning',
                        f"High response time: {latest_metrics.response_time:.2f}s"
                    )
                
                # Check success rate
                if latest_metrics.success_rate < self.alert_thresholds['success_rate']:
                    await self._create_alert(
                        agent_id, 'low_success_rate', 'critical',
                        f"Low success rate: {latest_metrics.success_rate:.2%}"
                    )
                
                # Check error count
                if latest_metrics.error_count > self.alert_thresholds['error_count']:
                    await self._create_alert(
                        agent_id, 'high_error_count', 'critical',
                        f"High error count: {latest_metrics.error_count}"
                    )
                
                # Check memory usage
                if latest_metrics.memory_usage > self.alert_thresholds['memory_usage']:
                    await self._create_alert(
                        agent_id, 'high_memory_usage', 'warning',
                        f"High memory usage: {latest_metrics.memory_usage:.1f}%"
                    )
                
                # Check CPU usage
                if latest_metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
                    await self._create_alert(
                        agent_id, 'high_cpu_usage', 'warning',
                        f"High CPU usage: {latest_metrics.cpu_usage:.1f}%"
                    )
                
                # Check for agent offline
                if latest_metrics.status == 'offline':
                    await self._create_alert(
                        agent_id, 'agent_offline', 'critical',
                        f"Agent is offline"
                    )
        
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def _create_alert(self, agent_id: str, alert_type: str, severity: str, message: str) -> None:
        """Create a new alert"""
        # Check if similar alert already exists and is not resolved
        for alert in self.alerts:
            if (alert.agent_id == agent_id and 
                alert.alert_type == alert_type and 
                not alert.resolved and
                (datetime.now() - alert.timestamp) < timedelta(minutes=5)):
                return  # Alert already exists and is recent
        
        # Create new alert
        alert = Alert(
            agent_id=agent_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            resolved=False
        )
        
        self.alerts.append(alert)
        
        # Save to Redis
        await self._save_alerts()
        
        # Notify alert handler
        if self.on_alert:
            self.on_alert(alert)
        
        logger.warning(f"Created alert for agent {agent_id}: {alert_type} - {message}")
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old metrics and resolved alerts"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
            
            # Clean up old metrics
            for agent_id in list(self.health_metrics.keys()):
                self.health_metrics[agent_id] = [
                    m for m in self.health_metrics[agent_id]
                    if m.timestamp >= cutoff_time
                ]
                if not self.health_metrics[agent_id]:
                    del self.health_metrics[agent_id]
            
            # Clean up old resolved alerts
            self.alerts = [
                alert for alert in self.alerts
                if not alert.resolved or alert.timestamp >= cutoff_time
            ]
            
            # Save cleaned state
            await self._save_state()
        
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def _save_state(self) -> None:
        """Save health metrics and alerts to Redis"""
        try:
            # Save alerts
            alerts_data = [asdict(alert) for alert in self.alerts]
            for alert in alerts_data:
                alert['timestamp'] = alert['timestamp'].isoformat()
            
            await self.redis_client.set("health:alerts", json.dumps(alerts_data))
            
            logger.debug("Saved health state to Redis")
        
        except Exception as e:
            logger.error(f"Error saving health state: {e}")
    
    async def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_agents': len(self.health_metrics),
            'active_agents': 0,
            'offline_agents': 0,
            'agents_with_issues': 0,
            'alerts': [],
            'agent_details': {}
        }
        
        for agent_id, metrics_list in self.health_metrics.items():
            if not metrics_list:
                continue
            
            latest_metrics = metrics_list[-1]
            
            # Count agent status
            if latest_metrics.status == 'active':
                report['active_agents'] += 1
            elif latest_metrics.status == 'offline':
                report['offline_agents'] += 1
            
            # Check for issues
            issues = []
            if latest_metrics.response_time > self.alert_thresholds['response_time']:
                issues.append('high_response_time')
            if latest_metrics.success_rate < self.alert_thresholds['success_rate']:
                issues.append('low_success_rate')
            if latest_metrics.error_count > self.alert_thresholds['error_count']:
                issues.append('high_error_count')
            if latest_metrics.memory_usage > self.alert_thresholds['memory_usage']:
                issues.append('high_memory_usage')
            if latest_metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
                issues.append('high_cpu_usage')
            
            if issues:
                report['agents_with_issues'] += 1
            
            # Add agent details
            report['agent_details'][agent_id] = {
                'status': latest_metrics.status,
                'response_time': latest_metrics.response_time,
                'success_rate': latest_metrics.success_rate,
                'error_count': latest_metrics.error_count,
                'memory_usage': latest_metrics.memory_usage,
                'cpu_usage': latest_metrics.cpu_usage,
                'active_tasks': latest_metrics.active_tasks,
                'queue_length': latest_metrics.queue_length,
                'issues': issues,
                'last_update': latest_metrics.timestamp.isoformat()
            }
        
        # Add active alerts
        report['alerts'] = [
            {
                'agent_id': alert.agent_id,
                'type': alert.alert_type,
                'severity': alert.severity,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'resolved': alert.resolved
            }
            for alert in self.alerts
            if not alert.resolved
        ]
        
        return report
    
    async def resolve_alert(self, alert_index: int) -> bool:
        """Resolve an alert by index"""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index].resolved = True
            await self._save_state()
            logger.info(f"Resolved alert {alert_index}")
            return True
        return False
    
    async def get_agent_health_history(self, agent_id: str, hours: int = 24) -> List[HealthMetrics]:
        """Get health history for a specific agent"""
        if agent_id not in self.health_metrics:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            m for m in self.health_metrics[agent_id]
            if m.timestamp >= cutoff_time
        ]


async def main():
    """Main entry point for testing"""
    monitor = AgentHealthMonitor()
    await monitor.initialize()
    await monitor.start_monitoring()
    
    try:
        # Monitor for 5 minutes
        await asyncio.sleep(300)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        await monitor.stop_monitoring()
        
        # Generate final report
        report = await monitor.get_health_report()
        print(f"Final health report: {json.dumps(report, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())