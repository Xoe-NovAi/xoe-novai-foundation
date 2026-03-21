#!/usr/bin/env python3
"""
AMR Chat Tracker
================
Tracks and archives Autonomous Marathon Run (AMR) chat sessions for historic mining.
"""

import json
import os
import sys
import uuid
from datetime import datetime

HISTORY_FILE = "data/amr_history.jsonl"

def init_history():
    """Initialize the history file if it doesn't exist."""
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            pass  # Create empty file

def start_session(goal: str, mode: str = "headless") -> str:
    """Start a new AMR session."""
    init_history()
    session_id = str(uuid.uuid4())
    entry = {
        "event": "session_start",
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "goal": goal,
        "mode": mode,
        "status": "active"
    }
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"AMR Session Started: {session_id}")
    return session_id

def log_deliberation(session_id: str, agent: str, message: str):
    """Log a council deliberation."""
    entry = {
        "event": "deliberation",
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "message": message
    }
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def end_session(session_id: str, outcome: str, notes: str = ""):
    """End an AMR session."""
    entry = {
        "event": "session_end",
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "outcome": outcome,
        "notes": notes,
        "status": "completed"
    }
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"AMR Session Ended: {session_id} ({outcome})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python amr_chat_tracker.py [start|log|end] ...")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        goal = sys.argv[2] if len(sys.argv) > 2 else "Untitled Marathon"
        start_session(goal)
    elif command == "log":
        sid = sys.argv[2]
        agent = sys.argv[3]
        msg = sys.argv[4]
        log_deliberation(sid, agent, msg)
    elif command == "end":
        sid = sys.argv[2]
        outcome = sys.argv[3] if len(sys.argv) > 3 else "unknown"
        end_session(sid, outcome)
