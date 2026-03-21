# GGUF mmap() Zero-Copy Model Loading Guide

**For**: Xoe-NovAi Phase 10 Memory Optimization  
**Target**: <6GB RAM constraint with 12GB zRAM  
**Purpose**: Enable on-demand loading of Krikri-7B without resident memory usage

---

## 🎯 Executive Summary

**mmap() enables lazy-loading of GGUF models**, reducing memory footprint from ~7GB (resident) to ~40MB (page tables only) for Krikri-7B. The model data remains on disk and is loaded into RAM **only when accessed**, leveraging the kernel page cache for subsequent fast access.

**Key Benefits for Xoe-NovAi**:
- **Memory Savings**: 7GB → 40MB page tables (99.4% reduction)
- **Fast Subsequent Loads**: First run: 5-10s, Next runs: <1s (kernel cache)
- **Multiple Instances**: Shared memory mappings across processes
- **Sparse Model Efficiency**: Only accessed layers loaded into RAM

---

## 📐 How mmap() Works with GGUF

### Traditional Model Loading (read())
```
Disk → read() → Copy to RAM → Model Buffer
      ↓
   Doubles memory usage during load
   Evicts kernel file cache
   Slow subsequent loads
```

### Zero-Copy mmap() Loading
```
Disk GGUF → mmap() → Virtual Memory Address Space → Kernel Page Cache
              ↓
          No copy to RAM!
          Direct memory mapping
          Lazy page loading
```

**Critical Requirement**: GGUF file layout on disk **must match** memory layout exactly (why GGUF exists).

---

## 🏗️ GGUF File Format Architecture

### Structure
```
GGUF File = [Header | Metadata | Tensor Info | Tensor Data]

Header:
- Magic: GGUF (4 bytes)
- Version: uint32
- Tensor count: uint64
- Metadata count: uint64

Metadata:
- Key-value pairs (architecture, hyperparams, tokenizer)
- Stored in KV format

Tensor Info:
- Name, dimensions, type, offset
- Maps to actual tensor data location

Tensor Data:
- Contiguous memory-aligned weights
- Ready for direct memory access via mmap()
```

**Why it's memory-mappable**: 
1. **Self-contained**: Everything in one file
2. **Alignment**: Data properly aligned for CPU/GPU
3. **Contiguity**: Weights stored contiguously
4. **Metadata separation**: Headers don't interfere with weight access

---

## 💻 Implementation for Python (Xoe-NovAi Stack)

### Option 1: llama-cpp-python (Recommended)
```python
from llama_cpp import Llama

# Zero-copy loading with mmap enabled (default)
model = Llama(
    model_path="/models/Krikri-7B-Q4_K_M.gguf",
    n_ctx=2048,           # Context window
    n_threads=12,         # Ryzen 5700U has 16 threads
    use_mmap=True,        # CRITICAL: Enable mmap (default)
    use_mlock=False,      # Don't lock pages in RAM (we want lazy load)
    n_gpu_layers=0,       # CPU-only for XNAi
    verbose=False
)

# Memory footprint: ~40MB page tables, not 7GB!
# Actual RAM usage grows as model layers are accessed
```

### Option 2: Direct mmap (Advanced)
```python
import mmap
import struct
import os

class GGUFMapper:
    def __init__(self, model_path: str):
        self.fd = os.open(model_path, os.O_RDONLY)
        self.file_size = os.fstat(self.fd).st_size
        
        # Memory-map the entire GGUF file
        self.mapped = mmap.mmap(
            self.fd, 
            length=0,           # Map entire file
            access=mmap.ACCESS_READ,  # Read-only
            flags=mmap.MAP_SHARED     # Share with other processes
        )
        
    def read_header(self):
        """Parse GGUF header without loading data"""
        magic = self.mapped[0:4]
        version = struct.unpack('<I', self.mapped[4:8])[0]
        tensor_count = struct.unpack('<Q', self.mapped[8:16])[0]
        metadata_count = struct.unpack('<Q', self.mapped[16:24])[0]
        
        return {
            'magic': magic,
            'version': version,
            'tensor_count': tensor_count,
            'metadata_count': metadata_count
        }
    
    def get_tensor_data(self, offset: int, size: int):
        """Access tensor data lazily via mmap slice"""
        return self.mapped[offset:offset+size]
    
    def close(self):
        self.mapped.close()
        os.close(self.fd)
```

---

## 🧠 Memory Access Patterns for Krikri-7B

### Sparse Model Characteristics
Large models like Krikri-7B are sparse - while there's 7GB of weights, only a small portion is used at evaluation time depending on the prompt.

**XNAi Optimization Strategy**:
```python
# Example: On-demand loading with usage tracking
import psutil
from llama_cpp import Llama

class OnDemandModel:
    def __init__(self, model_path: str):
        self.model = None
        self.model_path = model_path
        self.last_used = None
        
    def generate(self, prompt: str) -> str:
        # Lazy load only when needed
        if self.model is None:
            print("🔄 Loading Krikri-7B via mmap...")
            self.model = Llama(
                model_path=self.model_path,
                use_mmap=True,
                use_mlock=False
            )
            print(f"✅ Loaded (RSS: {self._get_memory_mb()}MB)")
        
        self.last_used = time.time()
        return self.model(prompt, max_tokens=256)
    
    def unload(self):
        """Release model if inactive"""
        if self.model and time.time() - self.last_used > 300:
            del self.model
            self.model = None
            print("🗑️ Unloaded Krikri-7B")
    
    def _get_memory_mb(self) -> int:
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
```

---

## ⚡ Performance Characteristics

### Startup Latency
| Scenario | Time | Memory (RSS) |
|----------|------|--------------|
| First load (cold) | 5-10s | ~40MB → 1-2GB |
| Subsequent load (warm cache) | <1s | ~40MB → cached |
| With `use_mlock=True` | 10-15s | Entire 7GB resident |

**Recommendation for XNAi**: 
- Use `use_mmap=True` (default)
- Set `use_mlock=False` (allow lazy load)
- Accept 5-10s first load for 99% memory savings

### Memory Growth During Inference
```
Initial:      40MB (page tables)
After prompt: 200-500MB (accessed layers)
After 100 tokens: 800MB-1.2GB (more layers accessed)
Steady state: 1.5-2GB (typical working set)
```

**zRAM Integration**: When combined with 12GB zRAM, infrequently accessed pages are compressed, further reducing physical RAM pressure.

---

## 🔧 XNAi Stack Integration

### Phase 10 Implementation Plan

#### Step 1: Install llama-cpp-python with mmap support
```bash
# In Dockerfile or requirements.txt
pip install llama-cpp-python --break-system-packages

# Verify mmap support
python3 -c "from llama_cpp import Llama; print('mmap supported')"
```

#### Step 2: Create Model Lifecycle Manager
```python
# /app/XNAi_rag_app/core/model_lifecycle.py

from typing import Optional
from llama_cpp import Llama
import asyncio
import logging

logger = logging.getLogger(__name__)

class ModelLifecycleManager:
    """
    Manages on-demand loading of heavyweight models like Krikri-7B.
    Uses mmap() for zero-copy, lazy loading.
    """
    
    def __init__(self, config: dict):
        self.models = {}
        self.config = config
        self.unload_timer = 600  # 10 minutes idle
        
    async def get_model(self, model_key: str) -> Llama:
        """Get model, loading if necessary"""
        if model_key not in self.models:
            logger.info(f"📂 Loading {model_key} via mmap...")
            self.models[model_key] = {
                'instance': self._load_model(model_key),
                'last_used': asyncio.get_event_loop().time()
            }
        
        self.models[model_key]['last_used'] = asyncio.get_event_loop().time()
        return self.models[model_key]['instance']
    
    def _load_model(self, model_key: str) -> Llama:
        """Load model with mmap enabled"""
        config = self.config[model_key]
        return Llama(
            model_path=config['path'],
            n_ctx=config.get('n_ctx', 2048),
            n_threads=config.get('n_threads', 12),
            use_mmap=True,       # Zero-copy
            use_mlock=False,     # Lazy load
            n_gpu_layers=0,      # CPU-only
            verbose=False
        )
    
    async def cleanup_idle(self):
        """Unload models idle > unload_timer"""
        current_time = asyncio.get_event_loop().time()
        for model_key, data in list(self.models.items()):
            if current_time - data['last_used'] > self.unload_timer:
                logger.info(f"🗑️ Unloading idle model: {model_key}")
                del data['instance']
                del self.models[model_key]
```

#### Step 3: Update config.toml
```toml
[models.krikri7b]
path = "/models/Krikri-7B-Instruct-Q4_K_M.gguf"
n_ctx = 4096
n_threads = 12
use_mmap = true
use_mlock = false
unload_after_idle_seconds = 600

[models.ancient_greek_bert]
path = "/models/ancient-greek-bert-Q6_K.gguf"
n_ctx = 512
n_threads = 6
use_mmap = true
use_mlock = true  # Small model, keep resident
```

#### Step 4: FastAPI Endpoint Integration
```python
# /app/XNAi_rag_app/api/routes/generation.py

from fastapi import APIRouter, Depends
from app.XNAi_rag_app.core.model_lifecycle import ModelLifecycleManager

router = APIRouter()

@router.post("/generate/ancient-greek")
async def generate_ancient_greek(
    prompt: str,
    model_mgr: ModelLifecycleManager = Depends(get_model_manager)
):
    """
    Generate Ancient Greek text using Krikri-7B (on-demand loaded)
    """
    model = await model_mgr.get_model('krikri7b')
    
    # Model is now loaded (mmap'd) and ready
    response = model(
        prompt=prompt,
        max_tokens=256,
        temperature=0.7,
        stop=["</s>"]
    )
    
    return {"generated": response['choices'][0]['text']}
```

---

## 📊 Memory Budget Impact

### Before mmap() Optimization
```
Total: 6GB physical RAM
├─ System: 400MB
├─ Redis: 512MB
├─ Qdrant: 1GB
├─ PostgreSQL: 512MB
├─ Qwen 0.6B: 600MB
├─ API/Services: 1GB
├─ Chainlit UI: 500MB
├─ Krikri-7B: ❌ CANNOT FIT (needs 7GB resident)
└─ Available: 1.5GB

Result: Krikri-7B unusable
```

### After mmap() Optimization
```
Total: 6GB physical RAM + 12GB zRAM
├─ System: 400MB
├─ Redis: 512MB
├─ Qdrant: 1GB
├─ PostgreSQL: 512MB
├─ Qwen 0.6B: 600MB
├─ API/Services: 1GB
├─ Chainlit UI: 500MB
├─ Krikri-7B (mmap'd): 40MB page tables + 1-2GB working set (in zRAM)
└─ Available: 1.4GB physical + 10GB zRAM

Result: ✅ Krikri-7B usable on-demand!
```

---

## 🎯 Success Metrics for Phase 10

### Memory Optimization KPIs
| Metric | Target | Validation |
|--------|--------|------------|
| Krikri-7B initial RSS | <100MB | `ps aux | grep krikri` |
| First inference latency | <15s | API response time |
| Subsequent inference | <5s | Warm cache performance |
| Working set size | <2GB | `smem -t -k` |
| zRAM compression ratio | >2:1 | `zramctl` |
| Total RAM usage | <5.5GB | Leave 500MB headroom |

### Testing Commands
```bash
# 1. Monitor memory before/after model load
watch -n 1 'free -h && echo "---" && smem -t -k'

# 2. Check mmap usage
cat /proc/$(pgrep -f krikri)/maps | grep gguf

# 3. Verify zero-copy
# Should show GGUF file mapped, not copied
lsof -p $(pgrep -f krikri) | grep gguf

# 4. zRAM statistics
zramctl
cat /sys/block/zram0/mm_stat
```

---

## ⚠️ Important Considerations

### When mmap() May Not Work
1. **Network filesystems**: NFS/SMB may have issues with mmap()
2. **Docker volumes**: Ensure proper mount options
3. **Read-only containers**: GGUF must be accessible as read-only file

### Podman Rootless Compatibility
```yaml
# docker-compose.yml
volumes:
  - ./models:/models:ro,z  # z label for SELinux, ro for read-only
```

### zRAM Tuning for mmap()
```bash
# /etc/sysctl.d/99-zram-mmap.conf
vm.swappiness=180          # Aggressive zRAM usage
vm.page-cluster=0          # Disable readahead (better for mmap)
vm.vfs_cache_pressure=50   # Keep page cache longer
```

---

## 📚 References

- llama.cpp GGUF format provides memory-mappable format with embedded metadata and zero-copy loading via mmap()
- llama.cpp uses memory mapping to load models efficiently, streaming only needed parts
- mmap() avoids copying pages, reducing memory from 40GB to 20GB for LLaMA models
- mmap() doesn't create extra copy in RAM and lives in kernel page cache, loading instantly on subsequent runs

---

**Status**: Ready for Phase 10 Implementation  
**Priority**: P1 (enables Krikri-7B integration)  
**Validation**: Memory profiling under load required
