#!/usr/bin/env python3
"""
Xoe-NovAi Sovereign Engine Watcher (v2.1)
The "Pulse" of the Sovereign Engine. 
Handles autonomous dispatching, JSON-parsing, and task resumption.
"""
import os
import json
import time
import subprocess
import sys
import re
from pathlib import Path

# Optional Redis adapter for agent state - prefer improved adapter
_redis_adapter = None
try:
    from scripts.agent_state_redis2 import RedisAgentStateAdapter
    _redis_adapter = RedisAgentStateAdapter()
except Exception:
    try:
        from scripts.agent_state_redis import RedisAgentStateAdapter
        _redis_adapter = RedisAgentStateAdapter()
    except Exception:
        _redis_adapter = None

# Configuration
INBOX_DIR = Path("internal_docs/communication_hub/inbox")
OUTBOX_DIR = Path("internal_docs/communication_hub/outbox")
STATE_DIR = Path("internal_docs/communication_hub/state")
POLL_INTERVAL = 10 

def stream_command(cmd, log_prefix="[*]"):
    """Run a command and stream its output while capturing it."""
    print(f"{log_prefix} Dispatching: {' '.join(cmd)}")
    full_output = []
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        for line in process.stdout:
            # Strip ANSI escape codes for cleaner logging
            clean_line = re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', '', line)
            sys.stdout.write(f"{log_prefix} {clean_line}")
            sys.stdout.flush()
            full_output.append(clean_line)
            
        process.wait()
        return "".join(full_output), process.returncode
    except Exception as e:
        print(f"{log_prefix} EXECUTION CRASH: {e}")
        return str(e), 1

def update_agent_state(agent_name, status, task_id=None, extra=None):
    """Update the persistent state file for the agent."""
    state_file = STATE_DIR / f"{agent_name}.json"
    state = {
        "agent_id": agent_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": status,
        "last_task_id": task_id
    }
    if extra:
        state.update(extra)
    # Persist to Redis if available, else filesystem fallback
    if _redis_adapter:
        try:
            _redis_adapter.save_state(agent_name, state)
        except Exception as e:
            print(f"{log_prefix} Redis save failed: {e}")
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
    else:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

def process_message(agent_name, message_path):
    print(f"\n[!] ALERT: Processing {message_path.name}...")
    try:
        with open(message_path, 'r') as f:
            msg = json.load(f)
        
        task_id = msg.get("message_id", "unknown")
        # Check for description at root or in content
        task_desc = msg.get("description") or msg.get("content", {}).get("description", "No description provided")
        model_name = msg.get("model_preference") or msg.get("content", {}).get("model_preference")
        
        update_agent_state(agent_name, "busy", task_id=task_id)
        output, code = execute_task(agent_name, task_desc, model_name)
        
        # Write response to outbox
        response_file = OUTBOX_DIR / f"{agent_name}_response_{int(time.time())}.json"
        response = {
            "message_id": f"resp-{task_id}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sender": agent_name,
            "target": msg.get("sender"),
            "type": "task_completion",
            "content": {
                "status": "success" if code == 0 else "failed",
                "exit_code": code,
                "output_summary": output[-1000:] if output else "No output captured."
            }
        }
        with open(response_file, 'w') as f:
            json.dump(response, f, indent=2)
        
        update_agent_state(agent_name, "idle", task_id=task_id)
        message_path.unlink() # Delete from inbox after success
        print(f"[*] Task {task_id} complete. Response in outbox.")
        
    except Exception as e:
        print(f"[!] Error in loop: {e}")
        update_agent_state(agent_name, "error", extra={"error": str(e)})

def execute_task(agent_name, task_desc, model_name=None):
    if agent_name == "cline":
        # Using JSON output and YOLO for maximum automation
        cmd = ["cline", "--yolo", "--json"]
        if model_name:
            cmd.extend(["--model", model_name])
        cmd.append(task_desc)
    elif agent_name == "gemini":
        cmd = ["gemini", "--prompt", task_desc, "--yolo", "--output-format", "json"]
    elif agent_name.startswith('cline') or 'kat' in agent_name.lower():
        # Cline/Kat dispatch support with model_preference
        model = model_name or 'kwaipilot/kat-coder-pro'
        cmd = ['cline', '--yolo', task_desc, '--silent', '--model', model]
        log_prefix = f'[{agent_name.upper()}]'
        return stream_command(cmd, log_prefix=log_prefix)
    elif agent_name == "copilot" or agent_name == "haiku":
        # Force Haiku 4.5 for free tier reliability
        model = "claude-haiku-4.5"
        cmd = ["copilot", "--yolo", "--prompt", task_desc, "--silent", "--model", model]
    else:
        print(f"[!] Unknown agent: {agent_name}")
        return "Unknown agent", 1

    return stream_command(cmd, log_prefix=f"[{agent_name.upper()}]")

def main():
    print(f"[*] Xoe-NovAi Sovereign Engine Watcher v2.1")
    print(f"[*] Architecture: Ryzen 7 5700U | Role: Dispatcher")
    print(f"[*] Monitoring {INBOX_DIR}...")
    
    for d in [INBOX_DIR, OUTBOX_DIR, STATE_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    
    heartbeat_count = 0
    try:
        while True:
            found = False
            for msg_file in INBOX_DIR.glob("*.json"):
                agent_name = msg_file.name.split('_')[0]
                process_message(agent_name, msg_file)
                found = True
            
            if not found:
                heartbeat_count += 1
                if heartbeat_count % 6 == 0: # Every 60s
                    print(f"[*] Pulse... (Monitoring {INBOX_DIR})")
                
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n[*] Engine cooling down... shutdown complete.")

if __name__ == "__main__":
    main()
