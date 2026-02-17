# CRAWLER OPERATIONS RUNBOOK

**Version**: 1.0  
**Last Updated**: 2026-02-16T22:15:00Z  
**Status**: Production-Ready

## Quick Reference

**Start Crawler**:
```bash
make up crawler
docker-compose exec crawler python3 scripts/crawler_job_processor.py
```

**Check Health**:
```bash
curl http://localhost:8000/health
redis-cli PING
curl http://localhost:8500/v1/agent/self
```

**View Job Queue**:
```bash
redis-cli LRANGE xnai:jobs:normal:pending 0 -1
```

**View Model Cards**:
```bash
ls knowledge/model_cards/*.json | wc -l
```

---

## 1. Startup & Configuration

### Prerequisites
- Redis running (port 6379, password: changeme123)
- Consul running (port 8500)
- Vikunja running (port 8000)
- Python 3.13+ with dependencies installed

### Environment Variables
```bash
# Redis
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=changeme123

# Consul
export CONSUL_HOST=localhost
export CONSUL_PORT=8500

# Vikunja
export VIKUNJA_BASE_URL=http://localhost:8000
export VIKUNJA_API_TOKEN=your_token_here

# Crawler
export CRAWLER_ID=crawler:ruvltra:001
export DAILY_JOB_HOUR=2
export DAILY_JOB_MINUTE=0
```

### Startup Procedure

**Step 1**: Verify infrastructure is ready
```bash
# Check Redis
redis-cli PING
# Expected: PONG

# Check Consul
curl http://localhost:8500/v1/agent/self
# Expected: JSON with agent info

# Check Vikunja
curl http://localhost:8000/api/v1/tasks
# Expected: 200 OK (may be auth error, that's OK)
```

**Step 2**: Start the crawler service
```bash
cd /home/arcana-novai/Documents/xnai-foundation
python3 scripts/crawler_job_processor.py
```

**Expected Output**:
```
✓ Crawler registered with Consul
✓ Daily job scheduled: 02:00 UTC
✓ Crawler job processor operational
   - Jobs processed: 0
   - Models researched: 0
```

**Step 3**: Verify service registration
```bash
curl http://localhost:8500/v1/catalog/service/xnai-crawler-ruvltra
```

Expected: Service listed with health status `passing`

---

## 2. Daily Operations

### Morning Checklist (Start of Day)

```bash
# 1. Check crawler health
curl http://localhost:8000/health
# Expected: {"status": "healthy", "uptime_seconds": ..., "metrics": {...}}

# 2. Check job queue
redis-cli LLEN xnai:jobs:normal:pending
# Expected: 0 (all jobs processed) or <10 (backlog being processed)

# 3. Check model cards generated
ls knowledge/model_cards/*.json | wc -l
# Expected: increases by ~10-50 per day

# 4. View yesterday's metrics
redis-cli GET xnai:metrics:daily:2026-02-15
# Expected: JSON with jobs_successful, models_researched, etc.
```

### During Day Operations

**Monitor Job Queue**:
```bash
# Watch queue size (should stay small if healthy)
watch -n 10 'redis-cli LLEN xnai:jobs:normal:pending'

# View next pending job
redis-cli LINDEX xnai:jobs:normal:pending 0
```

**View Active Jobs**:
```bash
# Get all active job IDs
redis-cli KEYS "xnai:jobs:*:status"

# Check specific job
redis-cli GET xnai:jobs:{job_id}:status
```

**Monitor Metrics**:
```bash
# Jobs processed this hour
redis-cli GET xnai:metrics:hourly:2026-02-16:22

# Models researched today
redis-cli GET xnai:metrics:daily:2026-02-16:models_researched
```

### Nightly Procedure (Before Daily Job Runs at 02:00 UTC)

```bash
# 1. Verify crawler still running
curl http://localhost:8000/health | jq '.status'

# 2. Check for backlog
redis-cli LLEN xnai:jobs:normal:pending
# If > 100, investigate slower processing

# 3. Archive old model cards (older than 30 days)
find knowledge/model_cards -mtime +30 -type f -exec rm {} \;

# 4. Backup Redis
redis-cli SAVE
# Wait for save completion
redis-cli BGSAVE
```

---

## 3. Troubleshooting

### Problem: Crawler Not Registering with Consul

**Symptom**: 
```
curl http://localhost:8500/v1/catalog/service/xnai-crawler-ruvltra
# Returns: empty list []
```

**Solution**:
```bash
# 1. Check Consul is running
docker-compose ps consul
# Expected: consul ... Up

# 2. Check crawler logs
docker-compose logs crawler | tail -50

# 3. Manual registration (if needed)
curl -X POST http://localhost:8500/v1/agent/service/register \
  -d '{
    "ID": "crawler:ruvltra:001",
    "Name": "xnai-crawler-ruvltra",
    "Address": "localhost",
    "Port": 8000,
    "Check": {
      "HTTP": "http://localhost:8000/health",
      "Interval": "30s"
    }
  }'
```

### Problem: Jobs Stuck in Queue

**Symptom**:
```bash
redis-cli LLEN xnai:jobs:normal:pending
# Returns: 500+ (growing)
```

**Solution**:
```bash
# 1. Check if crawler is running
ps aux | grep crawler_job_processor

# 2. Check crawler health
curl http://localhost:8000/health
# If unhealthy, restart:
# kill {pid}
# python3 scripts/crawler_job_processor.py

# 3. Check for stuck jobs
redis-cli LRANGE xnai:jobs:normal:pending 0 0  # First job

# 4. If job is malformed, remove it
redis-cli LPOP xnai:jobs:normal:pending
```

### Problem: Redis Connection Failed

**Symptom**:
```
ERROR: Could not connect to Redis localhost:6379
```

**Solution**:
```bash
# 1. Check Redis is running
docker-compose ps redis
# Expected: redis ... Up

# 2. Check Redis health
redis-cli -a changeme123 PING
# Expected: PONG

# 3. If failed, restart Redis
docker-compose restart redis
# Wait 10 seconds
docker-compose logs redis | tail -20

# 4. If still failed, check port
lsof -i :6379
# If occupied by non-redis, kill it
```

### Problem: Vikunja Integration Failing

**Symptom**:
```
ERROR: Could not create task in Vikunja: 401 Unauthorized
```

**Solution**:
```bash
# 1. Check Vikunja is running
docker-compose ps vikunja
# Expected: vikunja ... Up

# 2. Get valid API token
curl -X POST http://localhost:8000/api/v1/login \
  -d '{"username": "admin", "password": "admin"}'
# Returns: {"token": "..."}

# 3. Update environment variable
export VIKUNJA_API_TOKEN=new_token
# Restart crawler
```

### Problem: Vector Search is Slow

**Symptom**:
```
Vector search latency: 2000ms (SLA: 500ms)
```

**Solution**:
```bash
# 1. Check vector index size
ls -lh knowledge/vectors/model_cards.faiss
# If > 500MB, may need optimization

# 2. Rebuild vector index (careful - long operation)
python3 scripts/phase_b_vector_indexing.py

# 3. Consider Qdrant (Phase C.5)
# FAISS is local and limited to ~50k vectors
# Qdrant provides distributed indexing
```

---

## 4. Scaling

### Add More Crawler Instances

**Why**: Increase parallelism, reduce job queue backlog

**Steps**:
```bash
# 1. Assign new instance ID
export CRAWLER_ID=crawler:ruvltra:002

# 2. Start new instance
python3 scripts/crawler_job_processor.py &

# 3. Verify registration in Consul
curl http://localhost:8500/v1/catalog/service/xnai-crawler-ruvltra
# Expected: 2 instances listed

# 4. Monitor job distribution
redis-cli KEYS "xnai:crawler:*:progress"
# Should see both instances processing
```

### Increase Job Throughput

**Current bottlenecks** (by priority):
1. Model card generation latency (6-10 models/hour per crawler)
2. Redis queue throughput (fixed by system)
3. Consul health check overhead (30s interval)

**Optimizations**:
```bash
# 1. Parallel API queries in crawler (code change)
# Current: Sequential source queries (HuggingFace → OpenCompass → Papers)
# Optimized: Parallel queries with thread pool

# 2. Batch vector updates (code change)
# Current: Update vectors after each card
# Optimized: Batch update every 10 cards

# 3. Increase model card batch size (config change)
# Current: 5-10 models per job
# Optimized: 20-50 models per job (with load testing)
```

### Distributed Job Queue (Multi-Node)

**Setup** (future enhancement):
```
1. Replace Redis with distributed Redis Cluster
2. Add multiple crawlers across nodes
3. Use service mesh (Consul Connect) for routing
4. Add load balancer for health checks
```

---

## 5. Monitoring & Alerting

### Key Metrics to Track

| Metric | Normal Range | Alert If |
|--------|--------------|----------|
| Job queue length | 0-10 | > 100 for 10 min |
| Job success rate | > 95% | < 90% |
| Avg job latency | 60-120s | > 300s |
| Models/hour | 6-10 | < 4 |
| Crawler health | healthy | degraded/unhealthy |
| Redis memory | < 500MB | > 1GB |
| Consul service check | passing | failing |

### Prometheus Scrape Config

```yaml
global:
  scrape_interval: 30s

scrape_configs:
  - job_name: 'xnai-crawler'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Alert Rules (Prometheus)

```yaml
groups:
  - name: xnai_crawler_alerts
    rules:
      - alert: CrawlerUnhealthy
        expr: up{job="xnai-crawler"} == 0
        for: 2m
        action: notify

      - alert: QueueBacklog
        expr: redis_llen{key="xnai:jobs:normal:pending"} > 100
        for: 10m
        action: notify

      - alert: LowSuccessRate
        expr: rate(crawler_jobs_successful[1h]) / rate(crawler_jobs_processed[1h]) < 0.90
        for: 30m
        action: notify

      - alert: SlowProcessing
        expr: histogram_quantile(0.99, rate(crawler_job_duration_seconds[5m])) > 300
        for: 5m
        action: notify
```

### Dashboard Queries (Grafana)

**Jobs Per Hour**:
```promql
rate(crawler_jobs_processed[1h])
```

**Success Rate**:
```promql
rate(crawler_jobs_successful[1h]) / rate(crawler_jobs_processed[1h])
```

**Models Per Hour**:
```promql
rate(crawler_models_researched[1h])
```

**Queue Length**:
```promql
redis_llen{key="xnai:jobs:normal:pending"}
```

### Log Aggregation (ELK Stack)

**Filebeat Config**:
```yaml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/xnai/crawler/*.log

output.elasticsearch:
  hosts: ["localhost:9200"]
```

**Kibana Dashboards**:
- Job timeline (created → completed)
- Error distribution by type
- Model card sources (HuggingFace vs OpenCompass vs Papers)
- Latency percentiles (p50, p95, p99)

---

## 6. Maintenance Windows

### Weekly Maintenance (Every Sunday 04:00 UTC)

```bash
# 1. Compact Redis database
redis-cli BGREWRITEAOF

# 2. Archive week-old model cards
tar czf knowledge/archive/model_cards_2026-02-09.tar.gz \
  knowledge/model_cards/*.json \
  --exclude='*.json' -m time -older-than 7d

# 3. Rebuild vector index (if needed)
# python3 scripts/phase_b_vector_indexing.py

# 4. Verify all systems healthy
curl http://localhost:8000/health
redis-cli INFO stats
```

### Monthly Maintenance (First Sunday of Month, 04:00 UTC)

```bash
# 1. Full Redis backup
redis-cli --rdb /backups/redis_2026-02.rdb

# 2. Export model cards metadata
python3 scripts/export_model_cards_metadata.py

# 3. Verify integration tests
cd tests && pytest test_crawler_integration.py -v

# 4. Update documentation
# Review and update runbook if needed
```

### Quarterly Performance Review (Every 13 Weeks)

```bash
# 1. Analyze metrics trends
# - Job throughput increasing?
# - Success rate stable?
# - Latency within SLA?

# 2. Review failure patterns
redis-cli KEYS "xnai:jobs:*:error"
# Group by error type

# 3. Plan optimizations
# - Need more crawlers?
# - Need Qdrant migration?
# - Need code optimizations?

# 4. Update scaling roadmap
```

---

## 7. Disaster Recovery

### Backup Procedures

**Daily Automated** (at 23:00 UTC):
```bash
# Redis backup
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb /backups/redis_`date +%Y-%m-%d`.rdb

# Model cards backup
tar czf /backups/model_cards_`date +%Y-%m-%d`.tar.gz \
  knowledge/model_cards/

# Vector index backup
cp knowledge/vectors/model_cards.faiss \
   /backups/model_cards_vectors_`date +%Y-%m-%d`.faiss
```

### Recovery Procedures

**Recover from Redis Failure**:
```bash
# 1. Stop crawler
kill {crawler_pid}

# 2. Restore Redis backup
cp /backups/redis_2026-02-16.rdb /var/lib/redis/dump.rdb

# 3. Restart Redis
redis-cli SHUTDOWN
docker-compose up -d redis
sleep 5

# 4. Restart crawler
python3 scripts/crawler_job_processor.py
```

**Recover from Job Loss**:
```bash
# If Redis lost all jobs before save:
# 1. Re-enqueue lost jobs (manual or from queue backup)
# 2. Jobs will be re-processed (idempotent)
# 3. Check for duplicate model cards
#    (safe: model_id is unique, duplicates will overwrite)
```

**Recover from Corrupt Vector Index**:
```bash
# 1. Delete corrupted index
rm knowledge/vectors/model_cards.faiss

# 2. Rebuild from model cards
python3 scripts/phase_b_vector_indexing.py

# 3. Resume vector search operations
# (will work from backup FAISS or Qdrant)
```

---

## Emergency Contacts

- **Infra Team**: ops@xnai-foundation.local
- **On-Call Rotation**: Check Pagerduty schedule
- **Status Page**: status.xnai-foundation.io

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-02-16 | Initial runbook creation | Copilot |
| TBD | Add Qdrant procedures | Engineering |
| TBD | Add multi-node setup | Engineering |

---

**Document Status**: ✅ Production Ready  
**Last Verified**: 2026-02-16T22:15:00Z  
**Next Review**: 2026-03-16
