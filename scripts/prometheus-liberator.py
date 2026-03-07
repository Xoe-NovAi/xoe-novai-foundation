import json
import os
from datetime import datetime
from pathlib import Path

def liberate_grok(json_path, output_dir):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Liberate Conversations
    for conv_wrap in data.get('conversations', []):
        conv = conv_wrap.get('conversation', {})
        responses = conv_wrap.get('responses', [])
        
        title = conv.get('title', 'Untitled_Conversation').replace('/', '_').replace(' ', '_')
        timestamp = conv.get('create_time', 'unknown_time').split('T')[0]
        filename = f"{timestamp}_{title}.md"
        
        with open(output_path / filename, 'w') as f_out:
            f_out.write(f"# {conv.get('title')}\n\n")
            f_out.write(f"> **Liberated From**: Grok.com\n")
            f_out.write(f"> **Original Timestamp**: {conv.get('create_time')}\n\n---\n\n")
            
            for resp_wrap in responses:
                resp = resp_wrap.get('response', {})
                sender = resp.get('sender', 'unknown').upper()
                message = resp.get('message', '')
                f_out.write(f"### 🎙️ {sender}\n{message}\n\n")

    # 2. Liberate Souls (System Prompts)
    for project in data.get('projects', []):
        name = project.get('name', 'Untitled_Project').replace(' ', '_')
        soul = project.get('custom_personality', '')
        if soul:
            soul_filename = f"SOUL_{name}.md"
            with open(output_path / soul_filename, 'w') as f_soul:
                f_soul.write(f"# 💎 Liberated Soul: {name}\n\n{soul}")

if __name__ == "__main__":
    # Point to the unzipped Rosetta stone
    rosetta_path = "/tmp/grok_rosetta/ttl/30d/export_data/20ad039b-e905-4c23-938f-68c37137a57e/prod-grok-backend.json"
    target_dir = "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/expert-knowledge/reclaimed_gnosis/grok_liberation"
    liberate_grok(rosetta_path, target_dir)
    print(f"✅ Gnosis Liberated to {target_dir}")
