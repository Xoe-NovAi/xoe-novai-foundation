#!/usr/bin/env python3
"""
👁️ SCREENSHOT WORKER: The Visual Monitor
========================================
Captures terminal screenshots for visual verification during headless runs.
"""

import time
import os
from pathlib import Path
from PIL import ImageGrab

def capture_screenshot(output_path: Path):
    """Captures a screenshot of the entire screen."""
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(output_path)
        # print(f"👁️ Screenshot captured: {output_path}")
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")

def main():
    output_dir = Path("dashboard/artifacts/screenshots")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # print("👁️ Starting Screenshot Worker...")
    
    while True:
        timestamp = int(time.time())
        output_file = output_dir / f"terminal_state_{timestamp}.png"
        capture_screenshot(output_file)
        
        # Cleanup: Only keep the last 10 screenshots
        all_screenshots = sorted(output_dir.glob("terminal_state_*.png"))
        if len(all_screenshots) > 10:
            for s in all_screenshots[:-10]:
                s.unlink()
                
        time.sleep(60) # Capture every 60 seconds

if __name__ == "__main__":
    main()
