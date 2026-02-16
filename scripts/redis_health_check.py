#!/usr/bin/env python3
"""
Redis health check helper for local developer usage.

Checks connectivity using REDIS_URL or REDIS_HOST/REDIS_PASSWORD env vars and prints
helpful guidance if authentication is required.
"""

import os
import sys

try:
    from scripts.agent_state_redis2 import RedisAgentStateAdapter
except Exception:
    print("Redis helper module not available. Ensure scripts/agent_state_redis2.py exists.")
    sys.exit(1)


def main():
    ada = RedisAgentStateAdapter()
    if ada.client:
        try:
            ada.client.ping()
            print("OK: Connected to Redis at:", ada.url)
        except Exception as e:
            print("ERROR: Redis ping failed:", e)
            print("Ensure REDIS_URL or REDIS_PASSWORD env vars are set with correct credentials.")
    else:
        print("No Redis client available or failed to connect.")
        print("Set REDIS_URL or REDIS_HOST/REDIS_PASSWORD and retry.")

if __name__ == '__main__':
    main()
