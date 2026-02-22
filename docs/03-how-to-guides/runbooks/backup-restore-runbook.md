# Backup and Restore Runbook

> **Version**: 1.0.0  
> **Last Updated**: 2026-02-21  
> **RPO Target**: 24 hours | **RTO Target**: 2 hours

---

## Overview

This runbook covers backup and restore procedures for all XNAi Foundation Stack services.

---

## Services Requiring Backup

| Service | Data Location | Backup Method | Frequency |
|---------|--------------|---------------|-----------|
| Redis | `/data/redis/` | RDB snapshot | Daily |
| FAISS Index | `/app/data/faiss_index/` | File copy | On update |
| Qdrant | `/data/qdrant/` | Snapshot API | Daily |
| PostgreSQL (Vikunja) | `/var/lib/postgresql/` | pg_dump | Daily |
| VictoriaMetrics | `/victoria-metrics-data/` | vmbackup | Daily |
| IAM Database | `/app/data/iam.db` | File copy | Daily |
| Config Files | `./configs/`, `.env` | File copy | On change |

---

## Backup Procedures

### Quick Backup (All Services)

```bash
#!/bin/bash
# backup-all.sh - Run daily via cron

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Redis
podman exec xnai_redis redis-cli -a "$REDIS_PASSWORD" BGSAVE
cp ./data/redis/dump.rdb "$BACKUP_DIR/redis.rdb"

# FAISS Index
cp -r ./data/faiss_index "$BACKUP_DIR/"

# IAM Database
cp ./data/iam.db "$BACKUP_DIR/"

# Config Files
tar -czf "$BACKUP_DIR/configs.tar.gz" ./configs/ .env config.toml

# Compress
tar -czf "/backups/xnai-backup-$(date +%Y%m%d).tar.gz" -C "$BACKUP_DIR" .

echo "Backup complete: /backups/xnai-backup-$(date +%Y%m%d).tar.gz"
```

### Redis Backup

```bash
# Trigger RDB snapshot
podman exec xnai_redis redis-cli -a "$REDIS_PASSWORD" BGSAVE

# Wait for completion
podman exec xnai_redis redis-cli -a "$REDIS_PASSWORD" LASTSAVE

# Copy snapshot
cp ./data/redis/dump.rdb /backups/redis-$(date +%Y%m%d).rdb
```

### FAISS Index Backup

```bash
# Stop services using the index (optional but recommended)
podman-compose stop rag

# Copy index files
cp -r ./data/faiss_index /backups/faiss-$(date +%Y%m%d)/

# Restart services
podman-compose start rag
```

### Qdrant Backup (if enabled)

```bash
# Create snapshot via API
curl -X POST "http://localhost:6333/collections/xnai/snapshots" \
  -H "api-key: $QDRANT_API_KEY"

# Download snapshot
curl "http://localhost:6333/collections/xnai/snapshots/latest" \
  -H "api-key: $QDRANT_API_KEY" \
  -o /backups/qdrant-$(date +%Y%m%d).snapshot
```

### PostgreSQL (Vikunja) Backup

```bash
# pg_dump from container
podman exec xnai_vikunja-db pg_dump -U vikunja vikunja > /backups/vikunja-$(date +%Y%m%d).sql
```

### VictoriaMetrics Backup

```bash
# Use vmbackup tool
vmbackup-prod \
  -storageDataPath=./data/victoriametrics \
  -snapshot.createURL=http://localhost:8428/snapshot/create \
  -dst=/backups/vm-$(date +%Y%m%d)/
```

---

## Restore Procedures

### Redis Restore

```bash
# Stop Redis
podman-compose stop redis

# Restore RDB file
cp /backups/redis-TIMESTAMP.rdb ./data/redis/dump.rdb

# Start Redis
podman-compose start redis

# Verify
podman exec xnai_redis redis-cli -a "$REDIS_PASSWORD" PING
```

### FAISS Index Restore

```bash
# Stop RAG service
podman-compose stop rag

# Restore index
rm -rf ./data/faiss_index
cp -r /backups/faiss-TIMESTAMP ./data/faiss_index

# Start RAG service
podman-compose start rag

# Verify
curl http://localhost:8000/health
```

### Qdrant Restore

```bash
# Upload snapshot
curl -X PUT "http://localhost:6333/collections/xnai/snapshots/upload" \
  -H "api-key: $QDRANT_API_KEY" \
  -T /backups/qdrant-TIMESTAMP.snapshot

# Recover from snapshot
curl -X PUT "http://localhost:6333/collections/xnai/snapshots/recover" \
  -H "api-key: $QDRANT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"snapshot_name": "uploaded-snapshot"}'
```

### PostgreSQL (Vikunja) Restore

```bash
# Stop Vikunja
podman-compose stop vikunja vikunja-db

# Restore database
cat /backups/vikunja-TIMESTAMP.sql | podman exec -i xnai_vikunja-db psql -U vikunja vikunja

# Start Vikunja
podman-compose start vikunja-db vikunja

# Verify
curl http://localhost:3456/api/v1/info
```

### Full Stack Restore

```bash
#!/bin/bash
# restore-all.sh - Disaster recovery

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: ./restore-all.sh /backups/xnai-backup-TIMESTAMP.tar.gz"
  exit 1
fi

# Stop all services
podman-compose down

# Extract backup
tar -xzf "$BACKUP_FILE" -C /tmp/restore/

# Restore all data
cp /tmp/restore/redis.rdb ./data/redis/dump.rdb
cp -r /tmp/restore/faiss_index ./data/
cp /tmp/restore/iam.db ./data/
tar -xzf /tmp/restore/configs.tar.gz -C ./

# Start services
podman-compose up -d

# Verify
sleep 30
curl http://localhost:8000/health
curl http://localhost:8001/health

echo "Restore complete"
```

---

## Verification Procedures

### Post-Restore Checklist

- [ ] Redis: `redis-cli PING` returns PONG
- [ ] RAG API: `/health` returns healthy
- [ ] Voice UI: `localhost:8001` loads
- [ ] Vikunja: Can login and view tasks
- [ ] Vector search: Query returns results
- [ ] Metrics: Grafana dashboards show data

### Data Integrity Check

```bash
# Redis
podman exec xnai_redis redis-cli -a "$REDIS_PASSWORD" DBSIZE

# FAISS Index
ls -la ./data/faiss_index/
python -c "import faiss; idx = faiss.read_index('./data/faiss_index/index.faiss'); print(idx.ntotal)"

# PostgreSQL
podman exec xnai_vikunja-db psql -U vikunja -c "SELECT COUNT(*) FROM tasks;"
```

---

## Scheduling

### Cron Configuration

```cron
# /etc/cron.d/xnai-backup

# Daily backup at 2 AM
0 2 * * * xnai /home/xnai/scripts/backup-all.sh >> /var/log/xnai-backup.log 2>&1

# Weekly full backup (Sunday 3 AM)
0 3 * * 0 xnai /home/xnai/scripts/backup-full.sh >> /var/log/xnai-backup.log 2>&1

# Cleanup old backups (keep 30 days)
0 4 * * * xnai find /backups -mtime +30 -delete
```

---

## Retention Policy

| Backup Type | Retention | Location |
|-------------|-----------|----------|
| Daily | 30 days | Local `/backups/` |
| Weekly | 90 days | Local + Remote |
| Monthly | 1 year | Remote only |

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Redis restore fails | RDB version mismatch | Check Redis version compatibility |
| FAISS index corrupt | Incomplete backup | Rebuild index from source docs |
| Permission denied | Wrong UID/GID | `chown -R 1001:1001 ./data/` |
| Restore too slow | Large backup file | Use incremental backups |

### Emergency Contacts

- Stack maintainer: [UPDATE]
- Backup storage: `/backups/`
- Documentation: `docs/03-how-to-guides/runbooks/`

---

## Related Documentation

- [Crawler Operations Runbook](CRAWLER-OPERATIONS-RUNBOOK.md)
- [Docker Testing Guide](docker-testing.md)
- [Configuration Reference](../03-reference/configuration.md)
