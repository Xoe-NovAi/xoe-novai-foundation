# ============================================================================
# Xoe-NovAi Complete Monitoring & Alerting Stack Configuration
# Enterprise-grade observability with AI-specific metrics
# ============================================================================
# INTEGRATION STATUS: CLAUDE IMPLEMENTATION DELIVERABLE
# ============================================================================
# Status: NOT INTEGRATED - Requires implementation into Xoe-NovAi codebase
# Source: Claude Week 3 Session Deliverable - Enterprise Security & Compliance Hardening
# Date Received: January 27, 2026 (Week 3)
# Implementation Priority: HIGH (Enterprise monitoring with AI-specific metrics)
# Estimated Integration Effort: 3-4 days
# Dependencies: Prometheus, Grafana, Alertmanager, eBPF tools
# Integration Checklist:
# - [ ] Deploy Prometheus with scrape configurations
# - [ ] Configure 20+ security alert rules
# - [ ] Set up performance monitoring alerts
# - [ ] Deploy compliance monitoring alerts
# - [ ] Configure Alertmanager routing (Slack, PagerDuty, email)
# - [ ] Import Grafana security dashboard
# - [ ] Implement intelligent alert grouping and inhibition
# - [ ] Set up AI-specific metrics collection
# - [ ] Test end-to-end alerting pipeline
# - [ ] Validate monitoring coverage and accuracy
# Integration Complete: [ ] Date: ___________ By: ___________
# ============================================================================
# Prometheus Configuration
# ============================================================================
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cluster: 'xoenovai-production'
        environment: 'production'
    
    # Alertmanager configuration
    alerting:
      alertmanagers:
        - static_configs:
            - targets:
                - alertmanager:9093
    
    # Load alert rules
    rule_files:
      - /etc/prometheus/rules/*.yml
    
    # Scrape configurations
    scrape_configs:
      # Xoe-NovAi Services
      - job_name: 'xoenovai-iam'
        static_configs:
          - targets: ['iam-service:8000']
        metrics_path: '/metrics'
        scrape_interval: 15s
        
      - job_name: 'xoenovai-rag'
        static_configs:
          - targets: ['rag-service:8001']
        metrics_path: '/metrics'
        scrape_interval: 15s
        
      - job_name: 'xoenovai-voice'
        static_configs:
          - targets: ['voice-service:8002']
        metrics_path: '/metrics'
        scrape_interval: 15s
        
      - job_name: 'xoenovai-textseal'
        static_configs:
          - targets: ['textseal-service:8003']
        metrics_path: '/metrics'
        scrape_interval: 15s
        
      - job_name: 'xoenovai-llm'
        static_configs:
          - targets: ['llm-service:8004']
        metrics_path: '/metrics'
        scrape_interval: 15s
      
      # Kubernetes pods with Prometheus annotations
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names:
                - xoenovai
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\d+)?;(\d+)
            replacement: $1:$2
            target_label: __address__
          - action: labelmap
            regex: __meta_kubernetes_pod_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_pod_name]
            action: replace
            target_label: kubernetes_pod_name
      
      # Node exporter for system metrics
      - job_name: 'node-exporter'
        static_configs:
          - targets: ['node-exporter:9100']
      
      # Redis metrics
      - job_name: 'redis'
        static_configs:
          - targets: ['redis-exporter:9121']

  # ============================================================================
  # Alert Rules
  # ============================================================================
  security-alerts.yml: |
    groups:
      - name: security_alerts
        interval: 30s
        rules:
          # Authentication Security
          - alert: HighAuthenticationFailureRate
            expr: |
              sum(rate(http_requests_total{code=~"401|403"}[5m])) by (service) > 10
            for: 1m
            labels:
              severity: high
              category: security
              team: security
            annotations:
              summary: "High rate of authentication failures"
              description: "{{ $value }} unauthorized requests/sec to {{ $labels.service }}"
              runbook_url: "https://runbooks.xoenovai.com/security/auth-failures"
          
          # Privilege Escalation
          - alert: PrivilegeEscalationAttempt
            expr: |
              ebpf_privilege_escalation_attempts_total > 0
            for: 0s
            labels:
              severity: critical
              category: security
              team: security
            annotations:
              summary: "Privilege escalation attempt detected"
              description: "Process attempted to escalate privileges"
              runbook_url: "https://runbooks.xoenovai.com/security/privilege-escalation"
          
          # Data Exfiltration
          - alert: UnusualDataEgress
            expr: |
              rate(network_egress_bytes_total[5m]) > 100000000
            for: 5m
            labels:
              severity: critical
              category: security
              team: security
            annotations:
              summary: "Unusual data egress detected"
              description: "{{ $value }} bytes/sec leaving network (threshold: 100MB/s)"
              runbook_url: "https://runbooks.xoenovai.com/security/data-exfiltration"
          
          # Container Escape
          - alert: ContainerEscapeAttempt
            expr: |
              ebpf_container_escape_attempts_total > 0
            for: 0s
            labels:
              severity: critical
              category: security
              team: security
            annotations:
              summary: "Container escape attempt detected"
              description: "Suspicious container breakout activity"
              runbook_url: "https://runbooks.xoenovai.com/security/container-escape"
          
          # MFA Bypass
          - alert: MFABypassAttempt
            expr: |
              sum(rate(mfa_bypass_attempts_total[5m])) > 5
            for: 2m
            labels:
              severity: high
              category: security
              team: security
            annotations:
              summary: "Multiple MFA bypass attempts"
              description: "{{ $value }} MFA bypass attempts detected"
              runbook_url: "https://runbooks.xoenovai.com/security/mfa-bypass"

  performance-alerts.yml: |
    groups:
      - name: performance_alerts
        interval: 30s
        rules:
          # LLM Inference Latency
          - alert: HighLLMInferenceLatency
            expr: |
              histogram_quantile(0.95, rate(llm_inference_duration_seconds_bucket[5m])) > 2.0
            for: 5m
            labels:
              severity: warning
              category: performance
              team: ml
            annotations:
              summary: "High LLM inference latency"
              description: "P95 latency is {{ $value }}s (threshold: 2s)"
              runbook_url: "https://runbooks.xoenovai.com/performance/llm-latency"
          
          # Voice Processing Latency
          - alert: HighVoiceProcessingLatency
            expr: |
              histogram_quantile(0.95, rate(voice_processing_duration_seconds_bucket[5m])) > 0.5
            for: 5m
            labels:
              severity: warning
              category: performance
              team: voice
            annotations:
              summary: "High voice processing latency"
              description: "P95 latency is {{ $value }}s (threshold: 500ms)"
              runbook_url: "https://runbooks.xoenovai.com/performance/voice-latency"
          
          # RAG Retrieval Latency
          - alert: HighRAGRetrievalLatency
            expr: |
              histogram_quantile(0.95, rate(rag_retrieval_duration_seconds_bucket[5m])) > 0.2
            for: 5m
            labels:
              severity: warning
              category: performance
              team: rag
            annotations:
              summary: "High RAG retrieval latency"
              description: "P95 latency is {{ $value }}s (threshold: 200ms)"
              runbook_url: "https://runbooks.xoenovai.com/performance/rag-latency"
          
          # Memory Usage
          - alert: HighMemoryUsage
            expr: |
              (container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.9
            for: 5m
            labels:
              severity: warning
              category: performance
              team: devops
            annotations:
              summary: "High memory usage"
              description: "Container {{ $labels.container }} using {{ $value | humanizePercentage }} of memory limit"
              runbook_url: "https://runbooks.xoenovai.com/performance/memory-usage"
          
          # CPU Usage
          - alert: HighCPUUsage
            expr: |
              (rate(container_cpu_usage_seconds_total[5m]) / container_spec_cpu_quota) > 0.9
            for: 5m
            labels:
              severity: warning
              category: performance
              team: devops
            annotations:
              summary: "High CPU usage"
              description: "Container {{ $labels.container }} using {{ $value | humanizePercentage }} of CPU quota"
              runbook_url: "https://runbooks.xoenovai.com/performance/cpu-usage"

  compliance-alerts.yml: |
    groups:
      - name: compliance_alerts
        interval: 30s
        rules:
          # Watermark Verification Failures
          - alert: HighWatermarkVerificationFailureRate
            expr: |
              (
                sum(rate(watermark_verification_failure_total[5m])) /
                (sum(rate(watermark_verification_success_total[5m])) + sum(rate(watermark_verification_failure_total[5m])))
              ) > 0.1
            for: 5m
            labels:
              severity: high
              category: compliance
              team: security
            annotations:
              summary: "High watermark verification failure rate"
              description: "{{ $value | humanizePercentage }} of watermark verifications failing"
              runbook_url: "https://runbooks.xoenovai.com/compliance/watermark-failures"
          
          # Encryption Failures
          - alert: EncryptionFailures
            expr: |
              sum(rate(encryption_failures_total[5m])) > 0
            for: 1m
            labels:
              severity: critical
              category: compliance
              team: security
            annotations:
              summary: "Encryption failures detected"
              description: "{{ $value }} encryption failures per second"
              runbook_url: "https://runbooks.xoenovai.com/compliance/encryption-failures"
          
          # Audit Log Failures
          - alert: AuditLogFailures
            expr: |
              sum(rate(audit_log_write_failures_total[5m])) > 0
            for: 1m
            labels:
              severity: critical
              category: compliance
              team: security
            annotations:
              summary: "Audit log write failures"
              description: "{{ $value }} audit log writes failing per second"
              runbook_url: "https://runbooks.xoenovai.com/compliance/audit-log-failures"

  availability-alerts.yml: |
    groups:
      - name: availability_alerts
        interval: 30s
        rules:
          # Service Down
          - alert: ServiceDown
            expr: up == 0
            for: 1m
            labels:
              severity: critical
              category: availability
              team: devops
            annotations:
              summary: "Service {{ $labels.job }} is down"
              description: "{{ $labels.instance }} has been down for more than 1 minute"
              runbook_url: "https://runbooks.xoenovai.com/availability/service-down"
          
          # Circuit Breaker Open
          - alert: CircuitBreakerOpen
            expr: |
              circuit_breaker_state == 1
            for: 5m
            labels:
              severity: high
              category: availability
              team: devops
            annotations:
              summary: "Circuit breaker open"
              description: "Circuit breaker {{ $labels.service }}/{{ $labels.endpoint }} has been open for 5 minutes"
              runbook_url: "https://runbooks.xoenovai.com/availability/circuit-breaker"
          
          # High Error Rate
          - alert: HighErrorRate
            expr: |
              (
                sum(rate(http_requests_total{code=~"5.."}[5m])) by (service) /
                sum(rate(http_requests_total[5m])) by (service)
              ) > 0.05
            for: 5m
            labels:
              severity: warning
              category: availability
              team: devops
            annotations:
              summary: "High error rate"
              description: "{{ $labels.service }} has {{ $value | humanizePercentage }} error rate"
              runbook_url: "https://runbooks.xoenovai.com/availability/high-error-rate"

# ============================================================================
# Alertmanager Configuration
# ============================================================================
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: monitoring
data:
  alertmanager.yml: |
    global:
      resolve_timeout: 5m
      slack_api_url: '${SLACK_WEBHOOK_URL}'
      pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'
    
    # Templates
    templates:
      - '/etc/alertmanager/templates/*.tmpl'
    
    # Routes
    route:
      group_by: ['alertname', 'cluster', 'service']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 12h
      receiver: 'default'
      
      routes:
        # Critical alerts to PagerDuty
        - match:
            severity: critical
          receiver: 'pagerduty-critical'
          continue: true
        
        # Security alerts to security team
        - match:
            category: security
          receiver: 'security-team'
          continue: true
        
        # Compliance alerts to compliance team
        - match:
            category: compliance
          receiver: 'compliance-team'
          continue: true
        
        # Performance alerts to ML team
        - match:
            team: ml
          receiver: 'ml-team'
        
        # Default to Slack
        - receiver: 'slack-general'
    
    # Receivers
    receivers:
      - name: 'default'
        slack_configs:
          - channel: '#alerts'
            title: 'Alert: {{ .GroupLabels.alertname }}'
            text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
      
      - name: 'pagerduty-critical'
        pagerduty_configs:
          - routing_key: '${PAGERDUTY_ROUTING_KEY}'
            severity: 'critical'
            description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'
            details:
              firing: '{{ .Alerts.Firing | len }}'
              resolved: '{{ .Alerts.Resolved | len }}'
      
      - name: 'security-team'
        slack_configs:
          - channel: '#security-alerts'
            title: '🔒 Security Alert: {{ .GroupLabels.alertname }}'
            text: |
              *Severity:* {{ .CommonLabels.severity }}
              *Description:* {{ .CommonAnnotations.description }}
              *Runbook:* {{ .CommonAnnotations.runbook_url }}
            color: 'danger'
        email_configs:
          - to: 'security@xoenovai.com'
            from: 'alerts@xoenovai.com'
            smarthost: 'smtp.gmail.com:587'
            auth_username: '${SMTP_USERNAME}'
            auth_password: '${SMTP_PASSWORD}'
      
      - name: 'compliance-team'
        slack_configs:
          - channel: '#compliance-alerts'
            title: '📋 Compliance Alert: {{ .GroupLabels.alertname }}'
            text: '{{ .CommonAnnotations.description }}'
      
      - name: 'ml-team'
        slack_configs:
          - channel: '#ml-alerts'
            title: '🤖 ML Alert: {{ .GroupLabels.alertname }}'
            text: '{{ .CommonAnnotations.description }}'
      
      - name: 'slack-general'
        slack_configs:
          - channel: '#general-alerts'
            title: '{{ .GroupLabels.alertname }}'
            text: '{{ .CommonAnnotations.description }}'
    
    # Inhibition rules
    inhibit_rules:
      - source_match:
          severity: 'critical'
        target_match:
          severity: 'warning'
        equal: ['alertname', 'cluster', 'service']

# ============================================================================
# Grafana Dashboard - Security Overview
# ============================================================================
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard-security
  namespace: monitoring
data:
  security-dashboard.json: |
    {
      "dashboard": {
        "title": "Xoe-NovAi Security Dashboard",
        "uid": "xoenovai-security",
        "timezone": "browser",
        "schemaVersion": 30,
        "version": 1,
        "refresh": "30s",
        
        "panels": [
          {
            "id": 1,
            "title": "Authentication Failures (5m rate)",
            "type": "graph",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            "targets": [
              {
                "expr": "sum(rate(http_requests_total{code=~\"401|403\"}[5m])) by (service, code)",
                "legendFormat": "{{ service }} - {{ code }}"
              }
            ],
            "alert": {
              "conditions": [
                {
                  "evaluator": {
                    "params": [10],
                    "type": "gt"
                  },
                  "operator": {
                    "type": "and"
                  },
                  "query": {
                    "params": ["A", "5m", "now"]
                  },
                  "reducer": {
                    "params": [],
                    "type": "avg"
                  },
                  "type": "query"
                }
              ],
              "executionErrorState": "alerting",
              "frequency": "60s",
              "handler": 1,
              "name": "Authentication Failures alert",
              "noDataState": "no_data",
              "notifications": []
            }
          },
          
          {
            "id": 2,
            "title": "Security Events by Type",
            "type": "stat",
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
            "targets": [
              {
                "expr": "sum(ebpf_security_events_total) by (event_type)",
                "legendFormat": "{{ event_type }}"
              }
            ]
          },
          
          {
            "id": 3,
            "title": "Watermark Verification Rate",
            "type": "gauge",
            "gridPos": {"h": 8, "w": 8, "x": 0, "y": 8},
            "targets": [
              {
                "expr": "sum(rate(watermark_verification_success_total[5m])) / (sum(rate(watermark_verification_success_total[5m])) + sum(rate(watermark_verification_failure_total[5m])))",
                "legendFormat": "Success Rate"
              }
            ],
            "options": {
              "showThresholdLabels": false,
              "showThresholdMarkers": true
            },
            "fieldConfig": {
              "defaults": {
                "thresholds": {
                  "mode": "absolute",
                  "steps": [
                    {"value": 0, "color": "red"},
                    {"value": 0.9, "color": "yellow"},
                    {"value": 0.95, "color": "green"}
                  ]
                },
                "unit": "percentunit"
              }
            }
          },
          
          {
            "id": 4,
            "title": "Circuit Breaker States",
            "type": "heatmap",
            "gridPos": {"h": 8, "w": 16, "x": 8, "y": 8},
            "targets": [
              {
                "expr": "circuit_breaker_state",
                "legendFormat": "{{ service }} - {{ endpoint }}"
              }
            ]
          },
          
          {
            "id": 5,
            "title": "eBPF Events Timeline",
            "type": "timeseries",
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
            "targets": [
              {
                "expr": "rate(ebpf_security_events_total[1m])",
                "legendFormat": "{{ event_type }}"
              }
            ]
          }
        ]
      }
    }

# ============================================================================
# Deployment
# ============================================================================
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
        - name: prometheus
          image: prom/prometheus:v2.40.0
          args:
            - '--config.file=/etc/prometheus/prometheus.yml'
            - '--storage.tsdb.path=/prometheus'
            - '--storage.tsdb.retention.time=30d'
            - '--web.enable-lifecycle'
          ports:
            - containerPort: 9090
              name: web
          volumeMounts:
            - name: config
              mountPath: /etc/prometheus
            - name: rules
              mountPath: /etc/prometheus/rules
            - name: storage
              mountPath: /prometheus
      volumes:
        - name: config
          configMap:
            name: prometheus-config
        - name: rules
          configMap:
            name: prometheus-config
        - name: storage
          persistentVolumeClaim:
            claimName: prometheus-storage
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitoring
spec:
  type: ClusterIP
  ports:
    - port: 9090
      targetPort: 9090
      name: web
  selector:
    app: prometheus
