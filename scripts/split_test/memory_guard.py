#!/usr/bin/env python3
"""
Memory Guard - Protects memory bank during split test operations
"""

import os
import shutil
import hashlib
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MemoryGuard:
    """Memory protection system for split test operations."""
    
    def __init__(self, backup_dir: str = "memory_bank/backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.critical_files = [
            "memory_bank/activeContext.md",
            "memory_bank/progress.md",
            "memory_bank/projectbrief.md",
            "memory_bank/systemPatterns.md"
        ]
    
    def create_backup(self, test_id: str) -> str:
        """Create timestamped backup before test."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"split_test_{test_id}_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Backup critical files
        for file_path in self.critical_files:
            src = Path(file_path)
            if src.exists():
                dst = backup_path / src.name
                shutil.copy2(src, dst)
                logger.info(f"Backed up {file_path} to {dst}")
        
        # Backup context directory
        context_src = Path("memory_bank/handovers/split-test/context")
        if context_src.exists():
            context_dst = backup_path / "context"
            shutil.copytree(context_src, context_dst, dirs_exist_ok=True)
            logger.info(f"Backed up context to {context_dst}")
        
        # Create manifest
        manifest = {
            "test_id": test_id,
            "timestamp": timestamp,
            "backup_path": str(backup_path),
            "files": [str(f) for f in self.critical_files],
            "checksums": self._calculate_checksums()
        }
        
        with open(backup_path / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Backup created at {backup_path}")
        return str(backup_path)
    
    def validate_integrity(self) -> Dict[str, Any]:
        """Validate memory bank integrity."""
        results = {
            "valid": True,
            "missing_files": [],
            "checksum_mismatches": [],
            "current_checksums": {}
        }
        
        for file_path in self.critical_files:
            src = Path(file_path)
            if not src.exists():
                results["valid"] = False
                results["missing_files"].append(file_path)
                logger.error(f"CRITICAL: Missing file {file_path}")
                continue
            
            checksum = self._calculate_file_checksum(src)
            results["current_checksums"][file_path] = checksum
        
        return results
    
    def rollback(self, backup_path: str) -> bool:
        """Rollback memory bank from backup."""
        backup = Path(backup_path)
        if not backup.exists():
            logger.error(f"Backup directory not found: {backup_path}")
            return False
        
        try:
            # Restore critical files
            for file_path in self.critical_files:
                src = backup / Path(file_path).name
                dst = Path(file_path)
                if src.exists():
                    shutil.copy2(src, dst)
                    logger.info(f"Restored {file_path} from {src}")
            
            # Restore context
            context_src = backup / "context"
            if context_src.exists():
                context_dst = Path("memory_bank/handovers/split-test/context")
                shutil.copytree(context_src, context_dst, dirs_exist_ok=True)
                logger.info(f"Restored context from {context_src}")
            
            logger.info("Memory rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def _calculate_checksums(self) -> Dict[str, str]:
        """Calculate checksums for all critical files."""
        checksums = {}
        for file_path in self.critical_files:
            src = Path(file_path)
            if src.exists():
                checksums[file_path] = self._calculate_file_checksum(src)
        return checksums
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum for a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

def atomic_write(file_path: str, content: str) -> bool:
    """Write file atomically using temporary file and rename."""
    try:
        temp_path = f"{file_path}.tmp"
        with open(temp_path, "w") as f:
            f.write(content)
        
        # Atomic rename
        os.rename(temp_path, file_path)
        return True
    except Exception as e:
        logger.error(f"Atomic write failed for {file_path}: {e}")
        return False

def validate_file_integrity(file_path: str, expected_checksum: Optional[str] = None) -> bool:
    """Validate file integrity using checksum."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    # Calculate current checksum
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    current_checksum = hash_sha256.hexdigest()
    
    if expected_checksum and current_checksum != expected_checksum:
        logger.error(f"Checksum mismatch for {file_path}")
        return False
    
    logger.debug(f"File integrity check passed for {file_path}")
    return True

if __name__ == "__main__":
    # Test memory guard
    guard = MemoryGuard()
    
    # Create backup
    backup_path = guard.create_backup("test_123")
    print(f"Backup created at: {backup_path}")
    
    # Validate integrity
    results = guard.validate_integrity()
    print(f"Integrity check: {results}")
    
    # Test atomic write
    test_file = "test_atomic_write.txt"
    if atomic_write(test_file, "Test content"):
        print("Atomic write successful")
        os.remove(test_file)
    else:
        print("Atomic write failed")