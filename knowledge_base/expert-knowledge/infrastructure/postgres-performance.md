# PostgreSQL Performance Tuning (XNAi Foundation)

**Status**: 🟢 CURRENT  
**Last Updated**: 2026-02-28  
**Owner**: MC-Overseer  
**Domain**: Infrastructure

---

## Overview

In the XNAi Foundation stack, **PostgreSQL 16** serves as the relational database backend for Vikunja and other metadata services. It is optimized for the AMD Ryzen 5700U and NVMe storage, focusing on low-latency OLTP performance and efficient memory management.

---

## 🚀 Performance Benchmarks (2026)

| Metric | Setting | Impact |
|--------|---------|--------|
| **Latency** | `synchronous_commit = off` | ~30% reduction in write latency |
| **I/O Throughput** | `random_page_cost = 1.1` | Optimized for SSD seek times |
| **Concurrency** | `max_connections = 100` | Peak performance for 8-core CPU |
| **Caching** | `shared_buffers = 25% RAM` | Balanced between Postgres and OS cache |

---

## 🛠 Tuning for XNAi Stack

The `config/postgres.conf` file is optimized with the following "2026 Best Practices":

### 1. Core Memory Settings
- **`shared_buffers = 1.5GB`**: (Assuming 6GB RAM limit for Postgres container).
- **`work_mem = 16MB`**: Prevents OOM for concurrent simple queries.
- **`maintenance_work_mem = 256MB`**: Speeds up index builds and VACUUM.
- **`effective_cache_size = 4GB`**: Informs the planner of available memory.

### 2. SSD-Specific I/O
- **`random_page_cost = 1.1`**: Essential for NVMe/SSD storage.
- **`effective_io_concurrency = 200`**: Satures the SSD queue depth.
- **`wal_compression = lz4`**: High-speed WAL compression.

### 3. Checkpoints & Reliability
- **`checkpoint_timeout = 15min`**: Reduces I/O jitter.
- **`checkpoint_completion_target = 0.9`**: Spreads write load across the timeout.
- **`max_wal_size = 4GB`**: Prevents frequent checkpoints.

---

## 📈 Operational Workflows

### 1. Monitoring & Stats
Postgres is configured with `pg_stat_statements` for query analysis.
- **Check Stats**: `SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC;`
- **Health Check**: `pg_isready -h localhost -p 5432`

### 2. Backups (Vikunja-specific)
Vikunja metadata is critical.
```bash
# Manual Dump
docker exec xnai_postgres pg_dumpall -U postgres > backups/postgres_full_dump.sql

# Restore
cat backups/postgres_full_dump.sql | docker exec -i xnai_postgres psql -U postgres
```

### 3. Autovacuum Tuning
On the Ryzen host, we lower the scale factor to prevent table bloat:
- **`autovacuum_vacuum_scale_factor = 0.02`** (Trigger at 2% change).

---

## ⚠️ Known Issues & Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| Connection Spikes | Too many clients (>100) | Use PgBouncer in transaction mode. |
| OOM Kill | `shared_buffers` + `work_mem` too high | Reduce `shared_buffers` or lower `max_connections`. |
| High Disk I/O Wait | Frequent checkpoints | Increase `checkpoint_timeout` and `max_wal_size`. |

---

## 📚 References
- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
- [XNAi Database Strategy](memory_bank/strategies/production-tight-stack/PLAN-PRODUCTION-TIGHT-STACK.md)
