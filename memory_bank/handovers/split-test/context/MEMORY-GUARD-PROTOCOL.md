# Memory Guard Protocol

## Purpose
Implement a memory protection system to prevent data loss during split test operations.

## Implementation

### 1. Pre-Test Backup
```bash
# Create timestamped backup before any test
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="memory_bank/backups/split_test_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

# Backup critical memory files
cp memory_bank/activeContext.md "$BACKUP_DIR/"
cp memory_bank/progress.md "$BACKUP_DIR/"
cp -r memory_bank/handovers/split-test/context "$BACKUP_DIR/"
```

### 2. Atomic Operations
- All memory writes use atomic file operations
- Use temporary files with rename for consistency
- Implement checksum verification for critical files

### 3. Rollback Mechanism
```bash
# Rollback function
rollback_memory() {
    local backup_dir="$1"
    if [ -d "$backup_dir" ]; then
        cp "$backup_dir/activeContext.md" memory_bank/
        cp "$backup_dir/progress.md" memory_bank/
        cp -r "$backup_dir/context" memory_bank/handovers/split-test/
        echo "Memory rollback completed from $backup_dir"
    else
        echo "Backup directory not found: $backup_dir"
        return 1
    fi
}
```

### 4. Memory Validation
```python
def validate_memory_integrity():
    """Validate memory bank integrity after operations."""
    import hashlib
    
    critical_files = [
        "memory_bank/activeContext.md",
        "memory_bank/progress.md"
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
                checksum = hashlib.sha256(content).hexdigest()
                print(f"{file_path}: {checksum}")
        else:
            print(f"CRITICAL: Missing file {file_path}")
            return False
    return True
```

### 5. Memory Watchdog
Monitor memory bank for unauthorized changes and trigger alerts.

## Usage
- Always run pre-test backup before split tests
- Validate memory integrity after each operation
- Use rollback mechanism if corruption detected
- Monitor memory changes during test execution