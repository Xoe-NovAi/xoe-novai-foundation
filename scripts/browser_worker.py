#!/usr/bin/env python3
"""
Lightweight Browser Worker (Stub)
=================================
Integration stub for Lightpanda/BrowserOS.
Checks for binary availability and falls back to curl/requests if missing.
"""

import sys
import shutil
import subprocess

LIGHTPANDA_BIN = "lightpanda"

def check_browser():
    """Check if the browser binary is available."""
    if shutil.which(LIGHTPANDA_BIN):
        return True
    return False

def fetch_url(url):
    """Fetch a URL using the best available method."""
    if check_browser():
        print(f"Browsing with {LIGHTPANDA_BIN}: {url}")
        # subprocess.run([LIGHTPANDA_BIN, "--url", url])
        return "Browser content (stub)"
    else:
        print(f"Browser binary not found. Falling back to curl: {url}")
        try:
            result = subprocess.run(["curl", "-L", "-s", url], capture_output=True, text=True)
            return result.stdout[:500] + "..." # Truncate for stub
        except Exception as e:
            return f"Error fetching URL: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(fetch_url(url))
    else:
        print("Usage: python browser_worker.py [URL]")
