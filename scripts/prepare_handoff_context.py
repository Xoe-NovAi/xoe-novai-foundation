#!/usr/bin/env python3
import os
import sys
import datetime
import glob
import argparse

# Configuration
MEMORY_BANK_DIR = "memory_bank"
ACTIVE_CONTEXT_FILE = os.path.join(MEMORY_BANK_DIR, "activeContext.md")
OUTPUT_FILE = "session_context.md"
TOOL_REGISTRY = "OMEGA_TOOLS.yaml"

def read_file(filepath, max_size=100*1024): # 100KB limit
    try:
        if not os.path.isfile(filepath):
            return f"[Error: {filepath} is not a file]"
        size = os.path.getsize(filepath)
        if size > max_size:
            return f"[Warning: File {filepath} is too large ({size} bytes), skipping content]"
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"[Error reading {filepath}: {e}]"

def get_recent_logs(limit=50):
    log_files = glob.glob("logs/*.log") + glob.glob("*.log")
    if not log_files:
        return "No logs found."
    latest_log = max(log_files, key=os.path.getmtime)
    try:
        with open(latest_log, 'r') as f:
            lines = f.readlines()
            return "".join(lines[-limit:])
    except Exception as e:
        return f"Error reading logs: {e}"

def find_relevant_files(task_description):
    keywords = [w for w in task_description.split() if len(w) > 3]
    matches = []
    exclude_dirs = {'.git', 'node_modules', '__pycache__', 'venv', '.gemini', '_archive', 'artifacts'}
    
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(('.md', '.py', '.sh', '.yaml', '.json', '.toml', '.ts', '.js')):
                path = os.path.join(root, file)
                if any(k.lower() in file.lower() for k in keywords):
                    matches.append(path)
    return sorted(list(set(matches)))[:8] # Increased limit to 8

def suggest_tools(task_description):
    if not os.path.exists(TOOL_REGISTRY):
        return "Tool registry not found."
    try:
        import yaml
        with open(TOOL_REGISTRY, 'r') as f:
            registry = yaml.safe_load(f)
        suggestions = []
        task_words = set(task_description.lower().split())
        for category in registry.get('categories', []):
            for tool in category.get('tools', []):
                tool_words = set(tool.get('description', '').lower().split() + tool.get('name', '').lower().split())
                if not tool_words.isdisjoint(task_words):
                    suggestions.append(f"- **{tool['name']}**: {tool['description']}")
        return "\n".join(suggestions) if suggestions else "No specific tools matched."
    except Exception:
        return "Tool suggestion unavailable (check OMEGA_TOOLS.yaml or PyYAML)."

def generate_context(task, target_model="Agent", silent=False):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    active_context = read_file(ACTIVE_CONTEXT_FILE)
    relevant_files = find_relevant_files(task)
    suggested_tools = suggest_tools(task)
    
    content = f"""# 🤝 Session Context: {task}
**Target Model**: {target_model}
**Prepared by**: Omega Scout
**Timestamp**: {timestamp}

---

## 🧠 Active Stack Context
{active_context}

---

## 🛠️ Recommended Omega Tools
{suggested_tools}

---

## 📂 Auto-Detected File Context
"""

    for fpath in relevant_files:
        content += f"\n### File: `{fpath}`\n```\n{read_file(fpath)}\n```\n"

    content += f"\n---\n\n## 🎯 Immediate Objective\n{task}\n"
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write(content)
        
    if not silent:
        print(f"✅ Context prepared for {target_model} in {OUTPUT_FILE}")
        print("\n" + "="*60)
        print(f"🚀 INJECTING CONTEXT FOR {target_model.upper()}")
        print("="*60 + "\n")
        print(content)
        print("\n" + "="*60)
        print(f"👉 CONTEXT LOADED. Switch to {target_model} now.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Omega Scout: Prepare and load context for agent sessions.")
    parser.add_argument("task", help="The task description")
    parser.add_argument("--model", default="Opus 4.6", help="The target model name")
    parser.add_argument("--silent", action="store_true", help="Don't print context to stdout")
    
    args = parser.parse_args()
    generate_context(args.task, args.model, args.silent)
