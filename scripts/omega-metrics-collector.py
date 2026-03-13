#!/usr/bin/env python3
"""
Omega Metrics Collector (v2.1)
==============================
Aggregates session history, usage metrics, and quota status from all 
8 isolated domain instances into a dashboard-ready report.
"""

import os
import json
import glob
from datetime import datetime

INSTANCE_ROOT = "/tmp/xnai-instances"
OUTPUT_FILE = "artifacts/omega_instance_metrics.json"

# Domain mapping for clear dashboard labels
DOMAIN_MAP = {
    1: "Architect",
    2: "API / Backend",
    3: "UI / Frontend",
    4: "Voice / Audio",
    5: "Data / RAG",
    6: "Ops / Infra",
    7: "Research",
    8: "Test / QA"
}

# Quota limits (Free Tier 2026)
QUOTA_LIMITS = {
    "gemini_pro_daily": 50,
    "gemini_flash_daily": 1500
}

def parse_session_data(session_path):
    """Extract token totals and request counts from a gemini-cli session JSON."""
    total_tokens = 0
    message_count = 0
    request_count = 0
    try:
        with open(session_path, 'r') as f:
            data = json.load(f)
            messages = data.get("messages", [])
            for msg in messages:
                if msg.get("type") == "user":
                    request_count += 1
                tokens = msg.get("tokens", {})
                total_tokens += tokens.get("total", 0)
            message_count = len(messages)
    except Exception:
        pass
    return total_tokens, message_count, request_count

def collect_metrics():
    summary = {
        "timestamp": datetime.now().isoformat(),
        "instances": {},
        "global_status": "healthy"
    }
    
    total_network_tokens = 0
    
    for i in range(1, 9):
        instance_path = os.path.join(INSTANCE_ROOT, f"instance-{i}")
        gemini_home = os.path.join(instance_path, "gemini-cli")
        
        inst_data = {
            "name": DOMAIN_MAP.get(i, f"Instance {i}"),
            "status": "active" if os.path.exists(instance_path) else "inactive",
            "gemini": {
                "sessions": 0,
                "total_tokens": 0,
                "total_messages": 0,
                "total_requests": 0,
                "last_active": None,
                "quota_status": "nominal"
            },
            "opencode": {
                "active": os.path.exists(os.path.join(instance_path, "opencode"))
            }
        }
        
        # Collect Gemini History & Tokens
        history_patterns = [
            os.path.join(gemini_home, ".gemini/tmp/omega-stack/chats/*.json"),
            os.path.join(gemini_home, ".gemini/history/*.json")
        ]
        
        all_history = []
        for pattern in history_patterns:
            all_history.extend(glob.glob(pattern))
            
        inst_data["gemini"]["sessions"] = len(all_history)
        
        for session_file in all_history:
            tokens, messages, requests = parse_session_data(session_file)
            inst_data["gemini"]["total_tokens"] += tokens
            inst_data["gemini"]["total_messages"] += messages
            inst_data["gemini"]["total_requests"] += requests
            
        # Check Quota (simplified daily heuristic)
        if inst_data["gemini"]["total_requests"] > QUOTA_LIMITS["gemini_pro_daily"] * 0.8:
            inst_data["gemini"]["quota_status"] = "approaching_limit"
        if inst_data["gemini"]["total_requests"] >= QUOTA_LIMITS["gemini_pro_daily"]:
            inst_data["gemini"]["quota_status"] = "limit_reached"
            summary["global_status"] = "warning"
            
        if all_history:
            latest_file = max(all_history, key=os.path.getmtime)
            mtime = os.path.getmtime(latest_file)
            inst_data["gemini"]["last_active"] = datetime.fromtimestamp(mtime).isoformat()
            
        summary["instances"][f"instance-{i}"] = inst_data
        total_network_tokens += inst_data["gemini"]["total_tokens"]
        
    summary["total_network_tokens"] = total_network_tokens
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(summary, f, indent=2)
        
    print(f"✅ Quota-aware metrics collected. Total network tokens: {total_network_tokens}")

if __name__ == "__main__":
    collect_metrics()
