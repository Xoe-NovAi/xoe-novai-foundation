#!/usr/bin/env python3
"""
XNAi Model Integrity Guard (v1.0.0)
==================================

Verifies the integrity of local model weights against a known SHA-256 manifest.
Ensures that models haven't been tampered with or corrupted.
"""

import os
import hashlib
import json
import logging
from typing import Dict

logger = logging.getLogger("integrity-guard")
logging.basicConfig(level=logging.INFO)

MANIFEST_PATH = "models/manifest.json"

def calculate_sha256(file_path: str) -> str:
    """Calculate the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in 4MB chunks
        for byte_block in iter(lambda: f.read(4194304), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_models():
    """Verify all models listed in the manifest."""
    if not os.path.exists(MANIFEST_PATH):
        logger.warning(f"No manifest found at {MANIFEST_PATH}. Integrity check skipped.")
        return

    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    for model_name, expected_hash in manifest.items():
        model_path = os.path.join("models", model_name)
        if not os.path.exists(model_path):
            logger.error(f"Model MISSING: {model_name}")
            continue

        logger.info(f"Verifying {model_name}...")
        actual_hash = calculate_sha256(model_path)
        
        if actual_hash == expected_hash:
            logger.info(f"✅ {model_name}: Integrity Verified.")
        else:
            logger.error(f"❌ {model_name}: HASH MISMATCH! Expected {expected_hash}, got {actual_hash}")

if __name__ == "__main__":
    verify_models()
