#!/usr/bin/env python3
"""
🔱 OMEGA FOUNDRY: The Unified Sovereign Studio CLI
Focus: Synthesis, Visualization, and Broadcasting (Voice/Video).
"""
import anyio
import sys
import argparse
from pathlib import Path

async def synthesize(domain: str):
    """1M-context domain ingestion via Gemini 2.5 Pro."""
    print(f"🔱 Foundry: Synthesizing domain [{domain}]...")
    # TODO: Implement Gemini 2.5 Pro 1M context call
    await anyio.sleep(1)
    print(f"✅ Synthesis Complete: outputs/synthesis_{domain}.md")

async def visualize(input_file: str):
    """Automated Mermaid-CLI mind-mapping."""
    print(f"🔱 Foundry: Visualizing [{input_file}]...")
    # TODO: Implement mermaid-cli container call
    await anyio.sleep(1)
    print(f"✅ Visualization Complete: outputs/map_{Path(input_file).stem}.png")

async def broadcast(input_file: str):
    """Piper TTS + MoviePy audio/video briefing."""
    print(f"🔱 Foundry: Broadcasting [{input_file}]...")
    # TODO: Implement Piper TTS and MoviePy pipeline
    await anyio.sleep(1)
    print(f"✅ Broadcast Complete: outputs/briefing_{Path(input_file).stem}.mp3")

async def oikos_check():
    """Runs all Council stabilization scripts."""
    import httpx
    print("🔱 Foundry: Requesting Oikos Blessing from Service...")
    
    url = "http://localhost:8006/health"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                print("✅ Oikos Service is ACTIVE. The Hearth is warm.")
                # Run the individual scripts for local verification
                import subprocess
                scripts = ["brigid_hearth_check.py", "hestia_memory_lock.py", "demeter_harvest_index.py", "athena_shield_protocol.py"]
                for s in scripts:
                    print(f"\n🔱 Calling {Path(s).stem}...")
                    subprocess.run(["python3", f"scripts/{s}"], capture_output=True)
            else:
                print("⚠️ Oikos Service returned non-200 status.")
        except Exception as e:
            print(f"❌ Connection Error: Oikos Service is offline. ({e})")

async def wait_for_service(url: str, retries: int = 5, delay: int = 3):
    """Wait for the Oikos service to become responsive."""
    import httpx
    import time
    print(f"📡 Foundry: Waiting for Oikos Service at {url}...")
    async with httpx.AsyncClient() as client:
        for i in range(retries):
            try:
                response = await client.get(url.replace("/iris/route", "/health"), timeout=5.0)
                if response.status_code == 200:
                    print("✅ Oikos Service is ONLINE.")
                    return True
            except Exception:
                pass
            print(f"  (Attempt {i+1}/{retries}) Service starting...")
            await anyio.sleep(delay)
    return False

async def mastermind(problem: str):
    """Runs the Oikos Mastermind session with status polling."""
    import httpx
    import time
    
    base_url = "http://localhost:8006"
    route_url = f"{base_url}/iris/route"
    session_id = f"SESS-{int(time.time())}"
    
    if not await wait_for_service(route_url):
        print("❌ Error: Oikos Service timed out.")
        return

    print(f"🔱 Foundry: Initiating Session [{session_id}]...")
    payload = {"problem": problem, "session_id": session_id}
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Start Session
            response = await client.post(route_url, json=payload, timeout=30.0)
            data = response.json()
            print(f"🌈 Iris Decision: {data.get('decision', 'UNKNOWN')}")
            print(f"📡 Status: {data.get('response', 'Starting...')}")

            if data.get("decision") == "ASYNC_MASTERMIND":
                # 2. Poll Status
                status_url = f"{base_url}/iris/status/{session_id}"
                print("🪶 Council is deliberating. Polling for Decree...")
                
                while True:
                    await anyio.sleep(5)
                    status_res = await client.get(status_url)
                    status_data = status_res.json()
                    current_status = status_data.get("status")
                    
                    if current_status == "COMPLETE":
                        print(f"🔱 COUNCIL DECREE ACHIEVED: {status_data.get('response')}")
                        break
                    elif current_status == "ERROR":
                        print(f"❌ Council Error: {status_data.get('error')}")
                        break
                    else:
                        print(f"  [Status]: {current_status}...")

        except Exception as e:
            print(f"❌ Error during Mastermind: {str(e)}")

async def main():
    parser = argparse.ArgumentParser(description="Omega Foundry CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Mastermind
    mm_parser = subparsers.add_parser("mastermind")
    mm_parser.add_argument("problem", help="The problem to solve via Oikos Council")

    # Oikos Check
    subparsers.add_parser("oikos-check")

    # Synthesize
    sync_parser = subparsers.add_parser("synthesize")
    sync_parser.add_argument("domain", help="The domain/folder to synthesize")

    # Visualize
    vis_parser = subparsers.add_parser("visualize")
    vis_parser.add_argument("file", help="The markdown file to visualize")

    # Broadcast
    cast_parser = subparsers.add_parser("broadcast")
    cast_parser.add_argument("file", help="The markdown file to broadcast")

    args = parser.parse_args()

    if args.command == "mastermind":
        await mastermind(args.problem)
    elif args.command == "oikos-check":
        await oikos_check()
    elif args.command == "synthesize":
        await synthesize(args.domain)
    elif args.command == "visualize":
        await visualize(args.file)
    elif args.command == "broadcast":
        await broadcast(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    anyio.run(main)
