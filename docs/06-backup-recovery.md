---
title: "Backup & Disaster Recovery Procedures"
subtitle: "XNAi Foundation Multi-Tier System Recovery"
author: "XNAi Operations Team"
date: "2025-02-25"
status: "ready"
last_updated: "2025-02-25"
version: "1.0"
persona_focus: "SRE, DevOps, System Administrator"
---

# Backup & Disaster Recovery Procedures

## Overview

This document describes the comprehensive backup and recovery procedures for the XNAi Foundation multi-tier system, covering:
- **PostgreSQL** (Vikunja Database)
- **Redis** (Cache & Streams)
- **Qdrant** (Vector Database)

**Objectives:**
- Point-in-time recovery capability
- RTO (Recovery Time Objective): <1 hour
- Atomic backups of all three systems
- Tested and documented restore procedures

---

## 1. Backup Strategy

### 1.1 PostgreSQL Backup Strategy

#### Full Backups (Daily)
- **Schedule**: Daily at 2:00 AM UTC
- **Retention**: 30 days
- **Method**: `pg_dump` with gzip compression
- **Location**: `backups/postgresql/full_backup_*.sql.gz`
- **Compression**: 9 (optimal compression)

```bash
# Manual execution
bash scripts/backup-postgresql.sh full
```

**Features:**
- Atomic backup of entire database
- Compressed to ~20-30% of original size
- SHA256 checksum verification
- Metadata stored for recovery planning

#### WAL Archival (Hourly)
- **Schedule**: Automatic (via PostgreSQL WAL archival)
- **Retention**: 7 days (for point-in-time recovery)
- **Location**: `backups/postgresql/wal_archive/`
- **Method**: Continuous WAL segment archival

**Configuration Required:**
```ini
# In postgresql.conf
archive_mode = on
archive_command = 'test ! -f /backup/path/%f && cp %p /backup/path/%f'
```

#### Point-in-Time Recovery (PITR)
- Combines full backup + WAL segments
- Restore database to any point in time
- Requires both full backup and WAL files

### 1.2 Redis Backup Strategy

#### RDB Snapshots (Daily)
- **Schedule**: Daily at 2:30 AM UTC
- **Retention**: 7 days
- **Method**: `BGSAVE` (background save)
- **Location**: `backups/redis/rdb_snapshot_*.rdb.gz`
- **Compression**: gzip

```bash
# Manual execution
bash scripts/backup-redis.sh
```

**Features:**
- Non-blocking background save
- Point-in-time consistent snapshot
- Full in-memory state capture
- Minimal performance impact

#### AOF (Append-Only File) - Optional
- **Status**: Optional (disabled by default)
- **Location**: `backups/redis/aof_backup_*.aof.gz`
- **Format**: Human-readable command log
- **Purpose**: Granular recovery capability

### 1.3 Qdrant Backup Strategy

#### Collection Snapshots (Daily)
- **Schedule**: Daily at 2:45 AM UTC
- **Retention**: 7 days
- **Method**: Qdrant API snapshots
- **Location**: `backups/qdrant/full_backup_*/*.snapshot`

```bash
# Manual execution
bash scripts/backup-qdrant.sh
```

**Features:**
- All collections backed up
- Binary snapshot format
- Preserves collection state and metadata
- Supports incremental backups

#### Incremental Backups
- Snapshot individual collections
- Useful for selective restoration
- Faster backup for large deployments

### 1.4 Atomic Backup Procedure

**Ensures all three systems backed up at same point in time**

```bash
# Execute atomic backup (all systems)
bash scripts/backup-atomic-all.sh
```

**Backup Structure:**
```
backups/atomic_20250225_020000/
├── postgresql/
│   ├── vikunja.sql.gz
│   ├── vikunja.sql.gz.sha256
│   └── METADATA
├── redis/
│   ├── dump.rdb.gz
│   ├── dump.rdb.gz.sha256
│   └── METADATA
├── qdrant/
│   ├── collection1_snapshot.snapshot
│   ├── collection1_snapshot.snapshot.sha256
│   ├── collection2_snapshot.snapshot
│   ├── collection2_snapshot.snapshot.sha256
│   └── METADATA
└── MANIFEST
```

---

## 2. Backup Schedule

### Automated Schedule (Recommended)

Add to crontab for automated execution:

```bash
# Daily full backups
0 2 * * * cd /path/to/xnai-foundation && bash scripts/backup-postgresql.sh full >> logs/backup/pg_backup.log 2>&1
30 2 * * * cd /path/to/xnai-foundation && bash scripts/backup-redis.sh >> logs/backup/redis_backup.log 2>&1
45 2 * * * cd /path/to/xnai-foundation && bash scripts/backup-qdrant.sh >> logs/backup/qdrant_backup.log 2>&1

# Atomic backup (weekly, Sunday at 3 AM)
0 3 * * 0 cd /path/to/xnai-foundation && bash scripts/backup-atomic-all.sh >> logs/backup/atomic_backup.log 2>&1
```

### Manual Backup Execution

```bash
# Single system backups
bash scripts/backup-postgresql.sh full
bash scripts/backup-redis.sh
bash scripts/backup-qdrant.sh

# Atomic backup (all systems)
bash scripts/backup-atomic-all.sh
```

---

## 3. Backup Retention Policy

| System | Type | Retention | Location |
|--------|------|-----------|----------|
| PostgreSQL | Full | 30 days | `backups/postgresql/full_backup_*` |
| PostgreSQL | WAL | 7 days | `backups/postgresql/wal_archive/*` |
| Redis | RDB | 7 days | `backups/redis/rdb_snapshot_*` |
| Redis | AOF | 7 days | `backups/redis/aof_backup_*` |
| Qdrant | Snapshots | 7 days | `backups/qdrant/full_backup_*/` |
| Atomic | All | 7 days | `backups/atomic_*/` |

Automated cleanup removes backups beyond retention period.

---

## 4. Restore Procedures

### 4.1 PostgreSQL Restore

#### Full Restore from Latest Backup

```bash
# Find latest backup
LATEST_BACKUP=$(ls -1 backups/postgresql/full_backup_*.sql.gz | tail -1)

# Restore
bash scripts/restore-postgresql.sh full "${LATEST_BACKUP}"
```

**Process:**
1. Verifies backup file integrity (SHA256)
2. Decompresses backup
3. Connects to PostgreSQL
4. Drops existing database (if FORCE_RESTORE=true)
5. Creates new database
6. Restores from backup
7. Verifies restoration

**Environment Variables:**
```bash
FORCE_RESTORE=true          # Allow dropping existing database
VIKUNJA_DB_HOST=vikunja-db  # Database host
VIKUNJA_DB_USER=vikunja     # Database user
VIKUNJA_DB_PASSWORD=...     # Database password
```

#### Point-in-Time Recovery (PITR)

```bash
# Restore to specific point in time
bash scripts/restore-postgresql.sh pitr "2025-02-25 15:30:00"
```

**Requirements:**
- Full backup before target time
- WAL files covering time range
- Target time in format: "YYYY-MM-DD HH:MM:SS"

**Process:**
1. Finds base backup before target time
2. Restores from base backup
3. Applies WAL segments up to target time

#### Restore from Atomic Backup

```bash
# Find atomic backup
ATOMIC_DIR=$(ls -1d backups/atomic_* | tail -1)

# Restore
bash scripts/restore-postgresql.sh atomic "${ATOMIC_DIR}/postgresql"
```

### 4.2 Redis Restore

#### RDB Restore

```bash
# Find latest RDB snapshot
LATEST_RDB=$(ls -1 backups/redis/rdb_snapshot_*.rdb.gz | tail -1)

# Restore
bash scripts/restore-redis.sh rdb "${LATEST_RDB}"
```

**Process:**
1. Verifies backup integrity
2. Stops Redis server
3. Backs up existing dump.rdb
4. Stages restored RDB file
5. Requires manual Redis restart

**After Staging:**
```bash
# Restart Redis
docker-compose restart redis

# Verify
redis-cli PING
```

#### AOF Restore (Optional)

```bash
# Find latest AOF
LATEST_AOF=$(ls -1 backups/redis/aof_backup_*.aof.gz | tail -1)

# Restore
bash scripts/restore-redis.sh aof "${LATEST_AOF}"
```

**Note:** Takes longer to load than RDB; provides granular recovery.

#### Restore from Atomic Backup

```bash
# Find atomic backup
ATOMIC_DIR=$(ls -1d backups/atomic_* | tail -1)

# Restore
bash scripts/restore-redis.sh atomic "${ATOMIC_DIR}/redis"
```

### 4.3 Qdrant Restore

#### Full Collection Restore

```bash
# Find full backup
FULL_BACKUP=$(ls -1d backups/qdrant/full_backup_* | tail -1)

# Restore all collections
bash scripts/restore-qdrant.sh full "${FULL_BACKUP}"
```

**Process:**
1. Verifies Qdrant connectivity
2. Checks backup integrity
3. Uploads each snapshot
4. Verifies restoration
5. Reports restored collections

#### Single Collection Restore

```bash
# Find snapshot file
SNAPSHOT=$(ls -1 backups/qdrant/full_backup_*/*_*.snapshot | head -1)
COLLECTION="my_collection"

# Restore specific collection
bash scripts/restore-qdrant.sh collection "${SNAPSHOT}" "${COLLECTION}"
```

#### Restore from Atomic Backup

```bash
# Find atomic backup
ATOMIC_DIR=$(ls -1d backups/atomic_* | tail -1)

# Restore
bash scripts/restore-qdrant.sh full "${ATOMIC_DIR}/qdrant"
```

---

## 5. Atomic System Restore

### Full System Restore (All Three)

```bash
# Find atomic backup
ATOMIC_DIR=$(ls -1d backups/atomic_* | tail -1)

# Execute atomic restore
bash scripts/restore-all-systems.sh "${ATOMIC_DIR}"
```

**Restore Order:**
1. PostgreSQL (database)
2. Redis (cache)
3. Qdrant (vector database)

**Process:**
1. Validates atomic backup directory
2. Confirms restore with user
3. Restores PostgreSQL
4. Stages Redis files
5. Restores Qdrant collections
6. Performs health checks
7. Verifies all systems

**Expected Timeline:**
- PostgreSQL: ~5-15 minutes (depends on database size)
- Redis: ~1-5 minutes
- Qdrant: ~5-20 minutes (depends on collection sizes)
- **Total RTO: <1 hour**

---

## 6. Testing Recovery Procedures

### 6.1 Test PostgreSQL Restore

```bash
# Non-destructive test (restore to different host/database)
export FORCE_RESTORE=true
export VIKUNJA_DB_HOST=test-postgres
bash scripts/restore-postgresql.sh full backups/postgresql/full_backup_*.sql.gz
```

### 6.2 Test Redis Restore

```bash
# Test in staging environment
export REDIS_HOST=test-redis
export REDIS_PORT=6379
bash scripts/restore-redis.sh rdb backups/redis/rdb_snapshot_*.rdb.gz
```

### 6.3 Test Qdrant Restore

```bash
# Test with staging Qdrant instance
export QDRANT_HOST=test-qdrant
export QDRANT_PORT=6333
bash scripts/restore-qdrant.sh full backups/qdrant/full_backup_*/
```

### 6.4 Full Disaster Recovery Drill

**Monthly procedure:**

```bash
# 1. Prepare staging environment
docker-compose -f docker-compose.staging.yml up -d

# 2. Run full restore
bash scripts/restore-all-systems.sh backups/atomic_*/

# 3. Verify all systems
bash scripts/verify-recovery.sh

# 4. Document results
# Record: time taken, any issues, fixes applied

# 5. Cleanup staging
docker-compose -f docker-compose.staging.yml down -v
```

---

## 7. Disaster Recovery Runbook

### Scenario 1: Single System Failure

#### PostgreSQL Failure (Database Corruption)

**Symptoms:**
- Application cannot connect to database
- Query errors or timeouts
- Corrupted indices

**Recovery Steps:**

1. **Assess Damage**
   ```bash
   # Check PostgreSQL status
   docker-compose logs vikunja-db | tail -50
   
   # Try connection
   psql -h vikunja-db -U vikunja -d vikunja -c "SELECT 1"
   ```

2. **Restore from Latest Backup**
   ```bash
   export FORCE_RESTORE=true
   LATEST=$(ls -1 backups/postgresql/full_backup_*.sql.gz | tail -1)
   bash scripts/restore-postgresql.sh full "${LATEST}"
   ```

3. **Verify**
   ```bash
   # Check tables
   psql -h vikunja-db -U vikunja -d vikunja -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
   
   # Check application
   curl http://localhost:8000/vikunja/api/v1/user
   ```

4. **Document**
   - Record incident time
   - Note cause of failure
   - Update runbook if needed

#### Redis Failure (Memory Data Loss)

**Symptoms:**
- Redis not responding
- Connection refused
- Session loss

**Recovery Steps:**

1. **Check Status**
   ```bash
   docker-compose logs redis | tail -50
   redis-cli PING
   ```

2. **Restore from RDB**
   ```bash
   LATEST=$(ls -1 backups/redis/rdb_snapshot_*.rdb.gz | tail -1)
   bash scripts/restore-redis.sh rdb "${LATEST}"
   docker-compose restart redis
   ```

3. **Verify**
   ```bash
   redis-cli PING
   redis-cli INFO stats
   ```

#### Qdrant Failure (Vector DB Unavailable)

**Symptoms:**
- Vector search not working
- Qdrant API timeout
- Collection errors

**Recovery Steps:**

1. **Check Status**
   ```bash
   curl http://localhost:6333/health
   docker-compose logs qdrant | tail -50
   ```

2. **Restore from Backup**
   ```bash
   LATEST=$(ls -1d backups/qdrant/full_backup_* | tail -1)
   bash scripts/restore-qdrant.sh full "${LATEST}"
   ```

3. **Verify**
   ```bash
   curl http://localhost:6333/collections
   ```

---

### Scenario 2: Complete System Failure

**Symptoms:**
- Multiple services down
- Unable to access application
- Potential data center issue

**Recovery Steps:**

1. **Assess Situation**
   ```bash
   # Check all services
   docker-compose ps
   docker-compose logs | tail -100
   ```

2. **Determine Recovery Strategy**
   - Minor corruption: Restart services
   - Major corruption: Full restore needed
   - Data center failure: Failover to backup

3. **Execute Full System Restore**
   ```bash
   # Get latest atomic backup
   ATOMIC=$(ls -1d backups/atomic_* | tail -1)
   
   # Execute recovery
   bash scripts/restore-all-systems.sh "${ATOMIC}"
   ```

4. **Verify All Systems**
   ```bash
   # Check databases
   psql -h vikunja-db -U vikunja -d vikunja -c "SELECT COUNT(*) FROM pg_tables;"
   
   # Check cache
   redis-cli INFO stats
   
   # Check vectors
   curl http://localhost:6333/collections
   
   # Check application
   curl http://localhost:8000/vikunja/api/v1/user
   ```

5. **Post-Recovery**
   - Verify all data is accessible
   - Run application health checks
   - Monitor system for 24 hours
   - Document incident

---

### Scenario 3: Data Loss / Corruption

**Symptoms:**
- Missing records
- Corrupted data
- Inconsistent state across systems

**Recovery Steps:**

1. **Stop All Applications**
   ```bash
   docker-compose down
   ```

2. **Restore to Last Known Good State**
   ```bash
   # Use PITR if available
   bash scripts/restore-postgresql.sh pitr "2025-02-25 12:00:00"
   
   # Or full restore
   LATEST=$(ls -1 backups/postgresql/full_backup_*.sql.gz | tail -1)
   bash scripts/restore-postgresql.sh full "${LATEST}"
   ```

3. **Restore Other Systems**
   ```bash
   # Redis
   LATEST_REDIS=$(ls -1 backups/redis/rdb_snapshot_*.rdb.gz | tail -1)
   bash scripts/restore-redis.sh rdb "${LATEST_REDIS}"
   
   # Qdrant
   LATEST_QDRANT=$(ls -1d backups/qdrant/full_backup_* | tail -1)
   bash scripts/restore-qdrant.sh full "${LATEST_QDRANT}"
   ```

4. **Start All Services**
   ```bash
   docker-compose up -d
   ```

5. **Validate Data Integrity**
   ```bash
   # Run application tests
   pytest tests/
   
   # Manual verification
   # Check all critical data
   ```

---

## 8. Backup Monitoring & Maintenance

### 8.1 Backup Health Monitoring

**Check backup status:**
```bash
# PostgreSQL backups
ls -lh backups/postgresql/full_backup_*.sql.gz | tail -3

# Redis backups
ls -lh backups/redis/rdb_snapshot_*.rdb.gz | tail -3

# Qdrant backups
ls -d backups/qdrant/full_backup_* | tail -3

# Atomic backups
ls -d backups/atomic_* | tail -3
```

### 8.2 Verification Procedures

**Verify backup integrity:**
```bash
# Check checksums
cd backups/postgresql
sha256sum -c *.sha256

cd ../redis
sha256sum -c *.sha256

cd ../qdrant
find . -name "*.sha256" -exec sh -c 'cd "$(dirname "{}")" && sha256sum -c "$(basename "{}")"' \;
```

### 8.3 Backup Archival

**Archive old backups (offsite storage):**
```bash
# Compress atomic backups older than 30 days
find backups/atomic_* -type d -mtime +30 -exec tar czf {}.tar.gz {} \;

# Copy to S3 (example)
aws s3 sync backups/atomic_*.tar.gz s3://xnai-backup-bucket/

# Verify upload
aws s3 ls s3://xnai-backup-bucket/ --recursive
```

---

## 9. Performance Baselines

### Backup Performance

| System | Size | Duration | Notes |
|--------|------|----------|-------|
| PostgreSQL (50MB) | 50MB | ~2 min | Depends on compression |
| PostgreSQL (500MB) | 500MB | ~20 min | Full backup |
| Redis (100MB) | 100MB | ~30 sec | BGSAVE |
| Qdrant (5 collections) | 500MB | ~5 min | API-based snapshots |
| **Atomic All** | ~1.2GB | ~30 min | Parallel-capable |

### Restore Performance

| System | Size | Duration | Notes |
|--------|------|----------|-------|
| PostgreSQL (50MB) | 50MB | ~5 min | Restore + verify |
| PostgreSQL (500MB) | 500MB | ~15 min | Full restore |
| Redis (100MB) | 100MB | ~1 min | RDB load |
| Qdrant (5 collections) | 500MB | ~10 min | API-based restore |
| **Atomic All** | ~1.2GB | ~30-45 min | Full system restore |

---

## 10. Troubleshooting

### PostgreSQL Restore Issues

**Issue: "PSQL command not found"**
```bash
# Install postgresql-client
apt-get install postgresql-client-16
```

**Issue: "Checksum verification failed"**
```bash
# Backup file may be corrupted
# Try without checksum verification (NOT RECOMMENDED)
# Or restore from alternative backup
```

**Issue: "Database connection timeout"**
```bash
# Check PostgreSQL is running
docker-compose ps vikunja-db

# Check connectivity
psql -h vikunja-db -U vikunja -d postgres -c "SELECT 1"
```

### Redis Restore Issues

**Issue: "Redis shutdown may have failed"**
```bash
# Force stop Redis
docker-compose stop redis -t 30

# Check data permissions
ls -la data/redis/

# Restore files with correct permissions
chmod 644 data/redis/dump.rdb

# Restart
docker-compose restart redis
```

**Issue: "RDB file is corrupted"**
```bash
# Use AOF if available
LATEST_AOF=$(ls -1 backups/redis/aof_backup_*.aof.gz | tail -1)
bash scripts/restore-redis.sh aof "${LATEST_AOF}"
```

### Qdrant Restore Issues

**Issue: "Connection refused to Qdrant"**
```bash
# Check Qdrant is running
docker-compose ps qdrant

# Check API port
curl http://localhost:6333/health

# Restart if needed
docker-compose restart qdrant
```

**Issue: "Collection snapshot upload failed"**
```bash
# Verify snapshot file exists and is valid
ls -lh backups/qdrant/full_backup_*/*.snapshot

# Try restoring to different collection name
bash scripts/restore-qdrant.sh collection <snapshot> collection_v2
```

---

## 11. Quick Reference

### Command Cheatsheet

```bash
# Full backups
bash scripts/backup-postgresql.sh full
bash scripts/backup-redis.sh
bash scripts/backup-qdrant.sh

# Atomic backup (all systems)
bash scripts/backup-atomic-all.sh

# Full system restore
bash scripts/restore-all-systems.sh backups/atomic_*/

# Single system restore
bash scripts/restore-postgresql.sh full backups/postgresql/full_backup_*.sql.gz
bash scripts/restore-redis.sh rdb backups/redis/rdb_snapshot_*.rdb.gz
bash scripts/restore-qdrant.sh full backups/qdrant/full_backup_*/

# Verify backups
sha256sum -c backups/**/*.sha256

# List recent backups
ls -lht backups/*/full_backup_* | head -10

# Monitor backup logs
tail -f logs/backup/*.log
```

---

## 12. Contact & Escalation

**For backup issues:**
- Check logs in `logs/backup/`
- Review this documentation
- Contact XNAi Ops team

**Escalation path:**
1. Review runbook procedures
2. Check backup integrity
3. Attempt staged recovery test
4. Document findings and escalate

---

## Appendix: Related Documents

- [Infrastructure Documentation](./07-infrastructure.md)
- [Operations Manual](./04-operations.md)
- [System Architecture](./02-architecture.md)
- [Disaster Recovery Plan](./08-disaster-recovery-plan.md)

---

**Last Updated**: 2025-02-25  
**Version**: 1.0  
**Owner**: XNAi Operations Team  
**Review Cycle**: Quarterly
