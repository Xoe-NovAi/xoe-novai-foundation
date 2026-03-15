# zRAM Monitor for Hellenic Ingestion (SESS-26)

## Overview

`xnai_zram_monitor.py` is a **SAFETY CRITICAL** memory management module that monitors zRAM usage and triggers automatic backoff during document ingestion to prevent OOM kills.

## Features

- **Real-time zRAM monitoring**: Queries zramctl for current zram0 (lz4 hot tier) usage
- **Automatic backoff**: Triggers 30-second pause when zRAM exceeds 90% threshold
- **Robust parsing**: Handles K, M, G, T unit conversions and real-world zramctl output
- **Comprehensive logging**: ISO-8601 timestamps, usage percentages, and remaining memory
- **Graceful degradation**: Continues processing if zramctl is unavailable
- **Configurable thresholds**: Backoff duration and usage threshold are configurable

## Function Reference

### `check_and_backoff(backoff_duration: int = 30) -> bool`

Main function for ingestion loop integration.

**Returns:**
- `True` if zRAM usage is safe (<90%), continue processing
- `False` if backoff was triggered, skip to next iteration

**Algorithm:**
1. Query zramctl for zram0 stats
2. Calculate usage percentage: `(TOTAL / DISKSIZE) * 100`
3. IF usage > 90%:
   - Log warning with timestamp, usage %, and memory stats
   - Sleep for `backoff_duration` seconds
   - Return False (back off)
4. ELSE: Return True (continue)

**Example Usage:**
```python
from xnai_zram_monitor import check_and_backoff

for document in documents:
    if not check_and_backoff():
        continue  # Back off from processing
    process_document(document)  # Safe to process
```

### `_parse_zramctl_output() -> Optional[Tuple[float, float, float]]`

Internal parser for zramctl output.

**Returns:** Tuple of `(disksize_gb, total_gb, usage_percent)` or None on error

**Example output:**
```python
(4.0, 0.48, 12.0)  # 4GB total, 0.48GB used, 12% usage
```

### `_parse_size_to_gb(size_str: str) -> float`

Converts size strings to gigabytes.

**Supported units:** K, M, G, T (case-insensitive)

**Examples:**
```python
_parse_size_to_gb("4G")       # 4.0
_parse_size_to_gb("479.5M")   # 0.4795
_parse_size_to_gb("1000K")    # 0.001
```

## Configuration

Default constants (in module):
```python
DEFAULT_BACKOFF_DURATION_SECONDS = 30  # Backoff sleep duration
ZRAM_USAGE_THRESHOLD_PERCENT = 90      # Trigger threshold
ZRAM_DEVICE = "zram0"                  # Device to monitor (lz4)
```

## Logging

Backoff events are logged with WARNING level:
```
[2025-03-14T12:34:56.789Z] zRAM0 backoff triggered: 95.3% > 90%, pausing 30s (used: 3.81GB/4.00GB, remaining: 0.19GB)
```

## Testing

Comprehensive test suite with 20 tests covering:

1. **Parser tests** (7 tests)
   - Size unit conversion (K, M, G, T)
   - Edge cases and invalid input

2. **zramctl output parsing** (5 tests)
   - Real-world output parsing
   - Low, normal, and high usage scenarios
   - Error and timeout handling

3. **Normal operation** (2 tests)
   - Returns True under normal conditions
   - No sleep delays
   - Multiple sequential checks

4. **Backoff triggering** (2 tests)
   - Returns False on high usage
   - Sleeps for correct duration

5. **Logging** (2 tests)
   - Captures backoff events with full details
   - No spurious logging on normal operation

6. **Integration tests** (2 tests)
   - Real zramctl command execution
   - Integration pattern verification

**Run tests:**
```bash
cd app/XNAi_rag_app/core
python3 -m pytest tests/test_xnai_zram_monitor.py -v
```

**Test results:** ✅ 20/20 passed

## System Requirements

- Python 3.9+
- `zramctl` utility (available on systems with zram support)
- Standard library: subprocess, logging, time, re, datetime

## Implementation Notes

- No external dependencies beyond Python stdlib
- Subprocess timeout: 5 seconds
- Error handling ensures graceful degradation
- ISO-8601 timestamps for log parsing and analytics
- Memory calculations include remaining capacity for operator awareness

## Safety Considerations

✅ **SAFETY CRITICAL**: Prevents zRAM overflow and OOM kills
✅ **Non-blocking**: Backoff is explicit pause, not async
✅ **Transparent**: All backoff events are logged
✅ **Graceful**: Continues if zramctl unavailable (rather than stalling)
✅ **Monitored**: Detailed memory stats in every log message

## Integration Points

### Hellenic Ingestion Loop
```python
from xnai_zram_monitor import check_and_backoff

class HellenicIngestion:
    def process_documents(self, documents):
        for doc in documents:
            if not check_and_backoff():
                self.logger.info("Backing off due to zRAM pressure")
                continue
            self.ingest_document(doc)
```

### Health Monitoring
The module integrates with `app/XNAi_rag_app/core/health/` infrastructure:
- Logs warnings for observability systems
- Can be wrapped with circuit breakers if needed
- Memory statistics feed into health dashboard

## Future Enhancements

- Multi-tier memory monitoring (zram0, zram1, regular swap)
- Prometheus metrics export
- Adaptive threshold based on system load
- Per-document memory estimation

---
**Status:** ✅ COMPLETE
**SESS ID:** SESS-26
**Block:** 0.7 - zRAM Monitor
**Safety Level:** CRITICAL
