#!/usr/bin/env python3
import os
import httpx
import asyncio
import json

# Load environment
ENV_FILE = os.path.expanduser("~/.config/xnai/.env")
if os.path.exists(ENV_FILE):
    with open(ENV_FILE, 'r') as f:
        for line in f:
            if line.startswith('export '):
                key, value = line[7:].strip().split('=', 1)
                os.environ[key] = value.strip('"').strip("'")

async def test_key(idx, key):
    if not key or "key" in key.lower():
        return f"Account {idx}: [EMPTY/PLACEHOLDER]"
    
    url = "https://api.sambanova.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": "Meta-Llama-3.3-70B-Instruct",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return f"Account {idx}: ✅ SUCCESS"
            else:
                return f"Account {idx}: ❌ FAILED ({response.status_code}: {response.text[:50]})"
    except Exception as e:
        return f"Account {idx}: 💥 ERROR ({str(e)})"

async def main():
    print("🚀 Testing SambaNova 8-Account Rotation...")
    tasks = []
    for i in range(1, 9):
        key = os.getenv(f"SAMBANOVA_API_KEY_{i}")
        tasks.append(test_key(i, key))
    
    results = await asyncio.gather(*tasks)
    for res in results:
        print(res)

if __name__ == "__main__":
    asyncio.run(main())
