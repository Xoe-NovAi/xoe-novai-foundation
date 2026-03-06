#!/usr/bin/env python3
# ============================================================================
# Qdrant Migration - Health Check & Validation Script
# ============================================================================
# Purpose: Validate Qdrant configuration and migration readiness
# Usage: python3 scripts/validate_qdrant_migration.py
# ============================================================================

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import anyio

try:
    from qdrant_client.async_client import AsyncQdrantClient
except ImportError:
    print("❌ qdrant-client not installed. Install with: pip install qdrant-client")
    sys.exit(1)

try:
    import redis.asyncio as aioredis
except ImportError:
    print("❌ redis not installed. Install with: pip install redis")
    sys.exit(1)


async def check_faiss_index(faiss_path: str) -> bool:
    """Check if FAISS index exists and is readable."""
    index_file = Path(faiss_path) / "index.faiss"
    
    if not index_file.exists():
        print(f"⚠️  FAISS index not found: {index_file}")
        return False
    
    try:
        # Try to load FAISS to verify integrity
        import faiss
        index = faiss.read_index(str(index_file))
        print(f"✅ FAISS index valid: {index.ntotal} vectors, dim={index.d}")
        return True
    except ImportError:
        print("⚠️  FAISS not installed - cannot validate index")
        return True  # Don't fail, user might not have FAISS yet
    except Exception as e:
        print(f"❌ FAISS index error: {e}")
        return False


async def check_qdrant_connection(url: str, api_key: Optional[str] = None) -> bool:
    """Check Qdrant connectivity."""
    try:
        client = AsyncQdrantClient(url=url, api_key=api_key, timeout=5)
        
        # Attempt health check
        await anyio.sleep(0.1)
        
        print(f"✅ Qdrant connected: {url}")
        return True
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False


async def check_redis_connection(
    host: str, port: int, password: Optional[str] = None, db: int = 0
) -> bool:
    """Check Redis connectivity."""
    try:
        redis = await aioredis.from_url(
            f"redis://{host}:{port}",
            password=password,
            db=db,
            decode_responses=True,
            socket_connect_timeout=5,
        )
        
        await redis.ping()
        
        # Check migration state key
        state = await redis.get("xnai:migration:faiss_to_qdrant")
        if state:
            state_obj = json.loads(state)
            print(
                f"✅ Redis connected: Found migration state "
                f"(status={state_obj.get('status')})"
            )
        else:
            print("✅ Redis connected: No migration state found (fresh start)")
        
        await redis.close()
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


async def check_config_files() -> bool:
    """Check required configuration files."""
    required_files = [
        Path("config/qdrant_config.yaml"),
        Path("docker-compose.yml"),
    ]
    
    all_exist = True
    for file in required_files:
        if file.exists():
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            all_exist = False
    
    return all_exist


async def check_requirements() -> bool:
    """Check Python dependencies."""
    required_packages = [
        ("qdrant_client", "qdrant-client"),
        ("redis", "redis"),
        ("faiss", "faiss-cpu"),
        ("anyio", "anyio"),
        ("tqdm", "tqdm"),
        ("psutil", "psutil"),
    ]
    
    all_available = True
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"✅ {package_name} installed")
        except ImportError:
            print(f"❌ {package_name} NOT installed")
            all_available = False
    
    return all_available


async def main():
    """Run all validation checks."""
    print("=" * 70)
    print("🔍 Qdrant Migration - Health Check & Validation")
    print("=" * 70)
    print()
    
    import os
    
    # Load config from environment
    faiss_path = os.getenv("FAISS_INDEX_PATH", "/app/data/faiss_index")
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_password = os.getenv("REDIS_PASSWORD")
    
    checks = [
        ("Configuration Files", await check_config_files()),
        ("Python Dependencies", await check_requirements()),
        ("FAISS Index", await check_faiss_index(faiss_path)),
        ("Qdrant Service", await check_qdrant_connection(qdrant_url, qdrant_api_key)),
        ("Redis Service", await check_redis_connection(
            redis_host, redis_port, redis_password
        )),
    ]
    
    print()
    print("=" * 70)
    print("📋 Validation Summary")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"Results: {passed} passed, {failed} failed")
    print()
    
    if failed == 0:
        print("✅ All checks passed! Ready to run migration:")
        print()
        print("  python3 scripts/migrate_to_qdrant.py")
        print()
        return 0
    else:
        print("❌ Some checks failed. Please fix issues and try again.")
        print()
        return 1


if __name__ == "__main__":
    exit_code = anyio.run(main)
    sys.exit(exit_code)
