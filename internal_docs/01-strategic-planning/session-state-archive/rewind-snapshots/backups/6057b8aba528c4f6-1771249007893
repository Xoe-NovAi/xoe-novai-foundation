# Qdrant Migration - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Validate Your Setup
```bash
python3 scripts/validate_qdrant_migration.py
```

### 2. Start Services
```bash
docker-compose up -d redis qdrant
```

### 3. Run Migration
```bash
python3 scripts/migrate_to_qdrant.py
```

### 4. Verify Success
```bash
curl http://localhost:6333/collections/xnai_knowledge
```

## 📋 Prerequisites Checklist

- [ ] Docker and docker-compose installed
- [ ] FAISS index exists at `./data/faiss_index/index.faiss`
- [ ] Redis password set in `secrets/redis_password.txt` or `.env`
- [ ] Python 3.8+ with pip installed
- [ ] 6.6GB RAM minimum (optimized for Ryzen 7)

## ⚙️ Configuration

### Essential Environment Variables
```bash
REDIS_PASSWORD=your_password        # Required for Redis
QDRANT_URL=http://qdrant:6333      # Default, adjust if needed
FAISS_INDEX_PATH=/app/data/faiss_index  # Path to FAISS index
VECTOR_SIZE=384                     # Embedding dimension
```

### Optional Tuning
```bash
BATCH_SIZE=500                      # Vectors per batch (default 500)
MAX_MEMORY_PERCENT=0.6              # Percent of RAM to use (default 60%)
```

## 📊 What Happens During Migration

```
FAISS Index (in-memory)
         ↓
   [Load Vectors]
         ↓
  [Batch Processing]
    (500 per batch)
         ↓
  [Add Metadata] ← Metadata-first strategy
         ↓
   [Redis State] ← Progress tracking
         ↓
 [Qdrant Upsert] ← On-disk persistent storage
         ↓
 [Collection Created]
   with indexed payloads
```

## 🔍 Monitoring

### Real-Time Progress
```bash
# Watch the progress bar
tail -f logs/migration.log
```

### Check Current State
```bash
# Get migration state from Redis
redis-cli -a $REDIS_PASSWORD get xnai:migration:faiss_to_qdrant | jq .

# Get collection stats
curl http://localhost:6333/collections/xnai_knowledge
```

### Monitor Resources
```bash
docker stats xnai_qdrant xnai_redis
```

## ✅ Verification Steps

### 1. Check Services Are Running
```bash
docker-compose ps

# Expected output:
# xnai_qdrant  Up (healthy)
# xnai_redis   Up (healthy)
```

### 2. Verify Collection Exists
```bash
curl http://localhost:6333/collections/xnai_knowledge
```

### 3. Count Migrated Vectors
```bash
curl http://localhost:6333/collections/xnai_knowledge/points/count
```

### 4. Check Sample Point
```bash
# Get first point with metadata
curl http://localhost:6333/collections/xnai_knowledge/points/1
```

## 🔧 Troubleshooting

### Migration Fails: "Connection refused"
```bash
# Check Qdrant is running
docker-compose ps qdrant

# Restart if needed
docker-compose restart qdrant
```

### Memory Issues: "Memory limit approaching"
```bash
# Reduce batch size
BATCH_SIZE=250 python3 scripts/migrate_to_qdrant.py

# Or reduce memory limit
MAX_MEMORY_PERCENT=0.4 python3 scripts/migrate_to_qdrant.py
```

### FAISS Index Not Found
```bash
# Verify index exists
ls -lh ./data/faiss_index/index.faiss

# Or set correct path
FAISS_INDEX_PATH=/path/to/index python3 scripts/migrate_to_qdrant.py
```

### Resume Interrupted Migration
```bash
# Just run again - will continue from last checkpoint
python3 scripts/migrate_to_qdrant.py

# To force restart from beginning
# (Delete the migration state in Redis first)
redis-cli -a $REDIS_PASSWORD DEL xnai:migration:faiss_to_qdrant
python3 scripts/migrate_to_qdrant.py
```

## 📈 Performance Tuning

### For Speed (more memory usage)
```bash
BATCH_SIZE=1000 python3 scripts/migrate_to_qdrant.py
```

### For Safety (lower memory usage)
```bash
BATCH_SIZE=250 MAX_MEMORY_PERCENT=0.4 python3 scripts/migrate_to_qdrant.py
```

## 🎯 What Gets Created

### Qdrant Collection
- **Name**: `xnai_knowledge`
- **Vectors**: Stored on disk (on_disk: true)
- **Dimension**: 384 (configurable)
- **Distance**: COSINE (configurable)
- **Persistence**: `./data/qdrant/storage`

### Indexed Metadata (Payloads)
- `source`: Original data source
- `faiss_id`: Original FAISS ID
- `migrated_at`: Timestamp
- `batch_num`: Batch number (for recovery)

### Migration State (Redis)
- Stored at key: `xnai:migration:faiss_to_qdrant`
- Tracks: progress, failures, timestamps
- Enables: resume capability

## 📚 More Information

For detailed information, see:
- **Full Guide**: `docs/QDRANT_MIGRATION.md`
- **Architecture**: `docs/QDRANT_MIGRATION.md#architecture`
- **Troubleshooting**: `docs/QDRANT_MIGRATION.md#troubleshooting`

## 🆘 Getting Help

1. **Check logs**:
   ```bash
   tail -f logs/migration.log
   ```

2. **Validate setup**:
   ```bash
   python3 scripts/validate_qdrant_migration.py
   ```

3. **Check services**:
   ```bash
   docker-compose logs qdrant
   docker-compose logs redis
   ```

4. **Manual verification**:
   ```bash
   # Qdrant health
   curl http://localhost:6333/health
   
   # Redis health
   redis-cli -a $REDIS_PASSWORD ping
   ```

---

**Quick Links**:
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [AnyIO Docs](https://anyio.readthedocs.io/)
