#!/usr/bin/env python3
import sys
import os
import yaml
import glob

REGISTRY_FILE = "OMEGA_TOOLS.yaml"

def validate_registry():
    if not os.path.exists(REGISTRY_FILE):
        print(f"Error: {REGISTRY_FILE} not found.")
        return 1
    
    try:
        with open(REGISTRY_FILE, 'r') as f:
            data = yaml.safe_load(f)
            
        print(f"Validating {len(data.get('categories', []))} categories...")
        
        errors = 0
        for cat in data.get('categories', []):
            for tool in cat.get('tools', []):
                name = tool.get('name')
                type_ = tool.get('type')
                
                if type_ == 'script':
                    script_path = name.split()[0] # Handle arguments if any
                    if not os.path.exists(script_path):
                        print(f"[ERROR] Script not found: {script_path}")
                        errors += 1
                elif type_ == 'make':
                    # TODO: Validate make target exists
                    pass
                    
        if errors == 0:
            print("✅ Registry is valid.")
            return 0
        else:
            print(f"❌ Found {errors} errors.")
            return 1
            
    except Exception as e:
        print(f"Validation failed: {e}")
        return 1

def list_tools():
    # Simple lister
    with open(REGISTRY_FILE, 'r') as f:
        data = yaml.safe_load(f)
    
    for cat in data.get('categories', []):
        print(f"\n## {cat['name']}")
        for tool in cat.get('tools', []):
            print(f"  - {tool['name']}: {tool.get('description', '')}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "validate":
        sys.exit(validate_registry())
    elif cmd == "list":
        list_tools()
    else:
        print("Usage: tool_manager.py [validate|list]")
