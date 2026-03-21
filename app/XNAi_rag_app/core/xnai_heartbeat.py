"""
XNAi Heartbeat
==============
Logs vital system statistics to .logs/heartbeat.jsonl.
"""
import psutil
import json
import time
import os
from datetime import datetime

LOG_FILE = ".logs/heartbeat.jsonl"

def log_heartbeat():
    if not os.path.exists(".logs"):
        os.makedirs(".logs")
        
    stats = {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
        "swap_percent": psutil.swap_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(stats) + "\n")
    
    print(f"Heartbeat: RAM {stats['ram_percent']}% | CPU {stats['cpu_percent']}%")

if __name__ == "__main__":
    log_heartbeat()
