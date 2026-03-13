#!/usr/bin/env python3
"""
Queue Technical Manuals for Curation
"""
import subprocess
import time
import sys

manuals = [
    "https://docs.podman.io/en/latest/",
    "https://anyio.readthedocs.io/en/stable/",
    "https://fastapi.tiangolo.com/",
    "https://docs.pydantic.dev/latest/",
]

def queue_manual(url):
    print(f"Queueing: {url}")
    try:
        subprocess.run(["python3", "scripts/curate.py", "--url", url], check=True)
        print(f"Successfully queued: {url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to queue {url}: {e}")
        return False

def main():
    print("Starting manual queuing process...")
    for url in manuals:
        queue_manual(url)
        time.sleep(2) # Be polite
    print("All manuals queued.")

if __name__ == "__main__":
    main()
