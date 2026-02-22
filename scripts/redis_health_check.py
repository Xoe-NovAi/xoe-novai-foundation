#!/usr/bin/env python3
"""
Redis health check helper for local developer usage.

Checks connectivity using REDIS_URL or REDIS_HOST/REDIS_PASSWORD env vars.
Default password from docker-compose.yml: changeme123
"""

import os
import sys
import subprocess
from datetime import datetime

def check_redis_cli():
    """Test Redis using redis-cli (simpler fallback)."""
    host = os.getenv('REDIS_HOST', '127.0.0.1')
    port = os.getenv('REDIS_PORT', '6379')
    password = os.getenv('REDIS_PASSWORD', 'changeme123')
    
    cmd = ['redis-cli', '-h', host, '-p', port, '-a', password, 'PING']
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=3, text=True)
        output = result.stdout + result.stderr
        if 'PONG' in output:
            print(f"[{datetime.now().isoformat()}] ✓ Redis PING OK")
            return True
        else:
            print(f"[{datetime.now().isoformat()}] ✗ Redis PING failed")
            print(f"   Output: {output[:200]}")
            return False
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ✗ Redis check error: {e}")
        return False

def main():
    try:
        from scripts.agent_state_redis2 import RedisAgentStateAdapter
        ada = RedisAgentStateAdapter()
        if ada.client:
            try:
                ada.client.ping()
                print(f"[{datetime.now().isoformat()}] ✓ Redis connected at {ada.url}")
                return True
            except Exception as e:
                print(f"[{datetime.now().isoformat()}] ✗ Redis adapter failed: {e}")
                return check_redis_cli()
        else:
            print(f"[{datetime.now().isoformat()}] ⚠ No Redis client, trying redis-cli...")
            return check_redis_cli()
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ⚠ Fallback to redis-cli: {e}")
        return check_redis_cli()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
