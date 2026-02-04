"""
Memory Bank Integration
======================
Integration with Xoe-NovAi memory bank system for observability events.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any

class MemoryBankIntegration:
    """Integration with memory bank system"""
    
    def __init__(self):
        # Determine the root directory relative to this file
        # This assumes app/XNAi_rag_app/memory_bank_integration.py
        # We want to reach ../../memory_bank from here? 
        # Actually, in the container, it depends on how volumes are mounted.
        # Dockerfile says: COPY . /app (usually).
        # And volumes: - ./memory_bank:/memory_bank (maybe?)
        # Let's check docker-compose.yml again to see where memory_bank is.
        # It's not explicitly mounted in the RAG service in the previous turn's file read.
        # But 'expert-knowledge', 'library', 'knowledge' are.
        # Wait, the RAG service doesn't have memory_bank mounted in the `docker-compose.yml` I read earlier.
        # The plan says: self.memory_bank_path = os.getenv('MEMORY_BANK_PATH', './memory_bank')
        # I should probably just write to a log location that is mounted, or handle the missing dir gracefully.
        
        self.memory_bank_path = os.getenv('MEMORY_BANK_PATH', '/app/logs/memory_bank_events')
        self.ensure_memory_bank_exists()
    
    def ensure_memory_bank_exists(self):
        """Ensure memory bank directory exists"""
        try:
            os.makedirs(self.memory_bank_path, exist_ok=True)
        except OSError:
            # Fallback if we can't create the dir (permission issues?)
            pass
    
    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log event to memory bank"""
        event = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'details': details,
            'source': 'observability'
        }
        
        # Write to memory bank
        filename = f"{self.memory_bank_path}/observability_events.json"
        self._append_to_file(filename, event)
    
    def _append_to_file(self, filename: str, event: Dict[str, Any]):
        """Append event to file"""
        try:
            events = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        content = f.read()
                        if content:
                            events = json.loads(content)
                except json.JSONDecodeError:
                    pass # Start fresh if corrupt
            
            events.append(event)
            
            with open(filename, 'w') as f:
                json.dump(events, f, indent=2)
        except Exception as e:
            # Fallback logging to stdout if file write fails
            print(f"Memory bank write failed: {e}")
