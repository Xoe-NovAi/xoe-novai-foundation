# Enhanced Monitoring System

## Overview

The Enhanced Monitoring System provides comprehensive monitoring for multi-agent coordination, FAISS performance, and system health with advanced metrics collection and alerting capabilities.

## Features

### Multi-Agent Coordination Monitoring
- **Agent Performance Tracking**: Monitor agent status, task count, success rates, and response times
- **Queue Management**: Track agent queue lengths and task distribution
- **Error Tracking**: Monitor error counts and failure rates across agents
- **Resource Usage**: Track CPU and memory usage per agent

### FAISS Performance Monitoring
- **Index Metrics**: Monitor index size, build time, and memory usage
- **Query Performance**: Track query latency and throughput
- **Quality Metrics**: Monitor recall rates and search quality
- **Resource Utilization**: Track CPU and GPU usage for FAISS operations

### System Health Monitoring
- **Resource Monitoring**: CPU, memory, and disk usage tracking
- **Network I/O**: Monitor network traffic and connection counts
- **Service Health**: Track Redis and PostgreSQL connection status
- **Performance Baselines**: Establish and monitor performance thresholds

### Coordination Metrics
- **Workflow Tracking**: Monitor multi-agent workflow completion rates
- **Latency Measurement**: Track coordination and communication latency
- **Load Balancing**: Monitor task distribution balance across agents
- **Communication Overhead**: Track coordination communication costs

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent Layer   │    │  FAISS Layer    │    │  System Layer   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Status        │    │ • Index Size    │    │ • CPU Usage     │
│ • Task Count    │    │ • Query Latency │    │ • Memory Usage  │
│ • Success Rate  │    │ • Recall Rate   │    │ • Disk Usage    │
│ • Response Time │    │ • Throughput    │    │ • Network I/O   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Coordination    │
                    │ Layer           │
                    ├─────────────────┤
                    │ • Workflow      │
                    │ • Latency       │
                    │ • Balance       │
                    │ • Overhead      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Prometheus      │
                    │ Metrics         │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Alerting &      │
                    │ Reporting       │
                    └─────────────────┘
```

## Configuration

### Basic Configuration

```yaml
# configs/multi-agent-config.yaml
monitoring:
  enhanced:
    interval: 30                    # Monitoring interval in seconds
    retention_hours: 24             # Metrics history retention
    alert_cooldown: 5               # Alert cooldown in minutes
  
  alert_thresholds:
    max_failed_agents: 3
    max_error_rate: 5
    max_cpu_usage: 80
    max_memory_usage: 85
    max_disk_usage: 90
    max_query_latency: 0.5
    min_recall_rate: 0.8
```

### Prometheus Integration

The system automatically exposes metrics on port 8000:

```bash
# Access Prometheus metrics
curl http://localhost:8000/metrics
```

### Redis Integration

```yaml
# Environment variables
REDIS_URL: redis://localhost:6379
```

## Usage

### Starting the Monitoring System

```python
from scripts.enhanced_monitoring import EnhancedMonitoringSystem

async def main():
    # Initialize monitoring system
    monitoring = EnhancedMonitoringSystem()
    await monitoring.initialize()
    
    # Add custom alert handlers
    async def custom_alert_handler(alert_type, data):
        print(f"Custom alert: {alert_type} - {data}")
    
    monitoring.add_alert_handler(custom_alert_handler)
    
    # Start monitoring
    await monitoring.start_monitoring()
    
    # Run for desired duration
    await asyncio.sleep(300)  # 5 minutes
    
    # Stop monitoring
    await monitoring.stop_monitoring()
    
    # Export metrics report
    await monitoring.export_metrics_report()

if __name__ == "__main__":
    asyncio.run(main())
```

### Metrics Collection

The system collects metrics from multiple sources:

1. **Agent Metrics**: Collected from Redis keys `agent:*:metrics`
2. **FAISS Metrics**: Collected from FAISS monitoring endpoints
3. **System Metrics**: Collected using `psutil` and system APIs
4. **Coordination Metrics**: Calculated from agent and task data

### Alerting

The system provides configurable alerting for:

- **Agent Failures**: High number of failed agents
- **Error Rates**: Elevated error rates per agent
- **Resource Usage**: High CPU, memory, or disk usage
- **FAISS Performance**: Poor query latency or recall rates

### Metrics Export

```python
# Get current metrics summary
summary = monitoring.get_metrics_summary()
print(json.dumps(summary, indent=2))

# Export comprehensive report
report_path = await monitoring.export_metrics_report()
print(f"Report exported to: {report_path}")
```

## Metrics Reference

### Agent Metrics

| Metric | Description | Type | Labels |
|--------|-------------|------|--------|
| `xnai_agent_status` | Agent status (1=active, 0=inactive) | Gauge | agent_id |
| `xnai_agent_task_count` | Number of tasks assigned to agent | Gauge | agent_id |
| `xnai_agent_success_rate` | Agent success rate | Gauge | agent_id |
| `xnai_agent_response_time` | Agent response time | Histogram | agent_id |
| `xnai_agent_memory_usage` | Agent memory usage | Gauge | agent_id |
| `xnai_agent_cpu_usage` | Agent CPU usage | Gauge | agent_id |
| `xnai_agent_error_count` | Agent error count | Counter | agent_id |
| `xnai_agent_queue_length` | Agent task queue length | Gauge | agent_id |

### FAISS Metrics

| Metric | Description | Type |
|--------|-------------|------|
| `xnai_faiss_index_size` | FAISS index size | Gauge |
| `xnai_faiss_memory_usage` | FAISS memory usage | Gauge |
| `xnai_faiss_query_latency` | FAISS query latency | Histogram |
| `xnai_faiss_recall_rate` | FAISS recall rate | Gauge |
| `xnai_faiss_throughput` | FAISS throughput | Gauge |
| `xnai_faiss_cpu_usage` | FAISS CPU usage | Gauge |
| `xnai_faiss_gpu_usage` | FAISS GPU usage | Gauge |

### System Metrics

| Metric | Description | Type | Labels |
|--------|-------------|------|--------|
| `xnai_system_cpu_usage` | System CPU usage | Gauge | |
| `xnai_system_memory_usage` | System memory usage | Gauge | |
| `xnai_system_disk_usage` | System disk usage | Gauge | |
| `xnai_system_network_io` | System network I/O | Gauge | direction |
| `xnai_system_active_connections` | Active network connections | Gauge | |

### Coordination Metrics

| Metric | Description | Type |
|--------|-------------|------|
| `xnai_coordination_total_agents` | Total coordinated agents | Gauge |
| `xnai_coordination_active_agents` | Active coordinated agents | Gauge |
| `xnai_coordination_latency` | Coordination latency | Histogram |
| `xnai_coordination_balance` | Task distribution balance | Gauge |
| `xnai_coordination_overhead` | Communication overhead | Gauge |
| `xnai_coordination_completion_rate` | Workflow completion rate | Gauge |

## Dashboard Integration

### Grafana Dashboard

Create a Grafana dashboard using the Prometheus data source:

```json
{
  "dashboard": {
    "title": "XNAi Foundation Enhanced Monitoring",
    "panels": [
      {
        "title": "Agent Status",
        "type": "stat",
        "targets": [
          {
            "expr": "xnai_agent_status",
            "legendFormat": "{{agent_id}}"
          }
        ]
      },
      {
        "title": "FAISS Query Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(xnai_faiss_query_latency_sum[5m]) / rate(xnai_faiss_query_latency_count[5m])",
            "legendFormat": "Average Latency"
          }
        ]
      }
    ]
  }
}
```

### Custom Dashboards

The system provides a metrics summary API for custom dashboard integration:

```python
summary = monitoring.get_metrics_summary()
# Use summary data to populate custom dashboards
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failures**
   - Check Redis server status
   - Verify Redis URL configuration
   - Ensure Redis is accessible from monitoring system

2. **High Memory Usage**
   - Adjust `history_retention_hours` in configuration
   - Monitor metrics history cleanup
   - Check for memory leaks in monitoring tasks

3. **Missing Metrics**
   - Verify agent metrics are being published to Redis
   - Check FAISS monitoring integration
   - Ensure system metrics collection is working

4. **Alert Spam**
   - Adjust alert thresholds
   - Increase alert cooldown periods
   - Review alert handler logic

### Performance Tuning

1. **Monitoring Interval**
   - Default: 30 seconds
   - Adjust based on system load and requirements
   - Shorter intervals provide more granular data but higher overhead

2. **History Retention**
   - Default: 24 hours
   - Adjust based on storage capacity and analysis needs
   - Longer retention requires more memory and storage

3. **Alert Thresholds**
   - Start with conservative thresholds
   - Adjust based on observed system behavior
   - Use historical data to set appropriate thresholds

## Security Considerations

### Data Protection
- Metrics data may contain sensitive information
- Ensure proper access controls on monitoring endpoints
- Consider data encryption for metrics storage

### Network Security
- Monitor system exposes HTTP endpoints
- Use appropriate firewall rules
- Consider authentication for monitoring access

### Alert Security
- Alert handlers may process sensitive data
- Implement proper input validation
- Log alert processing for audit trails

## Integration Examples

### Kubernetes Integration

```yaml
# kubernetes/monitoring.yaml
apiVersion: v1
kind: Service
metadata:
  name: xnai-monitoring
spec:
  selector:
    app: xnai-monitoring
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xnai-monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: xnai-monitoring
  template:
    metadata:
      labels:
        app: xnai-monitoring
    spec:
      containers:
      - name: monitoring
        image: xnai-foundation/enhanced-monitoring:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
```

### Docker Compose Integration

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  monitoring:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./monitoring/reports:/app/monitoring/reports
```

## Best Practices

1. **Monitoring Configuration**
   - Start with default thresholds and adjust based on observed behavior
   - Use appropriate monitoring intervals for your use case
   - Regularly review and update alert thresholds

2. **Resource Management**
   - Monitor the monitoring system itself for resource usage
   - Implement proper cleanup of old metrics data
   - Use appropriate retention policies

3. **Alert Management**
   - Implement meaningful alert handlers
   - Use alert cooldowns to prevent spam
   - Regularly review and tune alert thresholds

4. **Data Analysis**
   - Use historical data to identify trends and patterns
   - Implement automated reporting for regular analysis
   - Use metrics data for capacity planning

## Future Enhancements

- **Machine Learning Integration**: Use ML for anomaly detection
- **Predictive Alerting**: Predict issues before they occur
- **Multi-Cluster Support**: Monitor across multiple clusters
- **Custom Metrics**: Support for custom application metrics
- **Real-time Dashboards**: Live updating dashboards
- **Integration APIs**: REST APIs for external integrations