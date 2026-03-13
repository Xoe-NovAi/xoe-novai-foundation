#!/usr/bin/env python3
"""
🔱 GNOSTIC PRE-FLIGHT: mmap-Optimized Crystal Rigidity Audit
High-performance AST-signature verification for the Omega Stack.
[AP:docs/protocols/ZLV_RIGIDITY_PROTOCOL.md]
"""
import os
import sys
import re
import mmap
import hashlib
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from app.XNAi_rag_app.core.linguistics import ZippedLogosDecoder
except ImportError:
    print("❌ ERROR: Could not import ZippedLogosDecoder.")
    sys.exit(1)

REGISTRY_PATH = PROJECT_ROOT / "memory_bank/ALETHIA_REGISTRY.md"

def get_expected_hash(file_name: str) -> str:
    """Efficiently extracts the Crystal Hash from the ALETHIA_REGISTRY.md."""
    if not REGISTRY_PATH.exists(): return ""
    with open(REGISTRY_PATH, "r+b") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            pattern = rb"- \*\*ZLV \(" + file_name.encode() + rb"\)\*\*: `([a-f0-9]+)`"
            match = re.search(pattern, mm, re.IGNORECASE)
            return match.group(1).decode() if match else ""

def preflight_check():
    """Main pre-flight routine with mmap-optimized ZLV."""
    print("🔱 OMEGA STACK: Pre-Flight Gnostic Audit")
    decoder = ZippedLogosDecoder()
    
    # 1. Rigidity Check (Linguistics)
    linguistics_path = PROJECT_ROOT / "app/XNAi_rag_app/core/linguistics.py"
    expected = get_expected_hash("Linguistics")
    
    if not expected:
        print("⚠️ Warning: No ZLV hash found for Linguistics in Registry.")
    elif not linguistics_path.exists():
        print("❌ Error: Linguistics module missing.")
    else:
        with open(linguistics_path, "r") as f:
            current_code = f.read()
            if decoder.verify_integrity(current_code, expected):
                print(f"✅ Rigid: {linguistics_path.relative_to(PROJECT_ROOT)} (ZLV Match)")
            else:
                print(f"❌ Brittle: {linguistics_path.relative_to(PROJECT_ROOT)} (Hash Mismatch)")

    # 2. Mesh Connectivity (The 4-Step Sync)
    print("🏙️  Checking Metropolis Mesh Connectivity...")
    import socket
    ports = {8000: "RAG API", 8002: "CLI Ingress", 8005: "MCP Context", 8006: "Oikos Mastermind"}
    for port, name in ports.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(('localhost', port)) == 0:
                print(f"✅ Port {port}: {name} ONLINE")
            else:
                print(f"⚠️ Port {port}: {name} OFFLINE")

    # 3. UID Integrity
    if os.getuid() == 1000:
        print("✅ UID Integrity: 1000 (Sovereign)")
    else:
        print(f"⚠️ Warning: Non-standard UID detected ({os.getuid()})")

if __name__ == "__main__":
    preflight_check()
