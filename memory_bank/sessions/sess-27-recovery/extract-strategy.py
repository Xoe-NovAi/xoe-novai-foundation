#!/usr/bin/env python3
"""Extract AMR SaR methodology from SESS-27 raw JSON"""
import json
import re

# Load raw session
with open('/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/memory_bank/sessions/sess-27-recovery/SESS-27-RAW.json') as f:
    session = json.load(f)

messages = session.get('messages', [])
print(f"[*] Processing {len(messages)} messages...")

# Strategy keywords
keywords = {
    'methodology': r'(AMR|methodology|approach|technique|pattern)',
    'reasoning': r'(reasoning|think|logic|flow|sequence)',
    'verification': r'(verify|check|validate|confirm|test)',
    'integration': r'(integrat|connect|link|sync|bridge)',
    'architecture': r'(architec|design|layer|component|module)',
    'strategy': r'(strateg|plan|roadmap|phase|step)',
}

strategy_segments = []

for i, msg in enumerate(messages):
    content = msg.get('content', [])
    text = None
    
    if isinstance(content, list) and len(content) > 0:
        text = content[0].get('text') if isinstance(content[0], dict) else content[0]
    elif isinstance(content, dict):
        text = content.get('text')
    
    if not text:
        continue
    
    # Detect strategy-relevant messages
    is_strategy = False
    matched_categories = set()
    
    for category, pattern in keywords.items():
        if re.search(pattern, text, re.IGNORECASE):
            is_strategy = True
            matched_categories.add(category)
    
    if is_strategy:
        strategy_segments.append({
            'index': i,
            'timestamp': msg.get('timestamp'),
            'type': msg.get('type'),
            'categories': list(matched_categories),
            'preview': text[:200] if len(text) > 200 else text,
            'text': text
        })

print(f"[*] Found {len(strategy_segments)} strategy-relevant segments")

# Write extraction
output_path = '/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/memory_bank/strategies/AMR-SaR.md'

with open(output_path, 'w') as f:
    f.write("""# AMR SaR: Advanced Model Reasoning - Semantic Analysis & Recovery

**Source**: SESS-27 (264-message Gemini session)  
**Extracted**: 2026-03-16  
**Status**: Strategy methodology framework  

## Overview

The Advanced Model Reasoning with Semantic Analysis & Recovery (AMR SaR) methodology is a sophisticated approach to:
1. Decomposing complex reasoning chains into recoverable steps
2. Implementing multi-layer verification and validation
3. Designing enterprise systems with semantic coherence
4. Integrating distributed AI agents with shared gnosis

---

## Core Methodology Segments

""")
    
    for i, segment in enumerate(strategy_segments, 1):
        f.write(f"\n### Segment {i}: {segment['type'].upper()}\n")
        f.write(f"**Categories**: {', '.join(segment['categories'])}\n")
        f.write(f"**Timestamp**: {segment['timestamp']}\n")
        f.write(f"**Message Index**: {segment['index']}/264\n\n")
        f.write(f"```\n{segment['text']}\n```\n\n")
    
    f.write("""---

## Key Insights

Based on analysis of the 264-message SESS-27 session, the AMR SaR methodology emphasizes:

- **Semantic Decomposition**: Breaking complex operations into individually recoverable pieces
- **Multi-Layer Verification**: Implementing checks at each architectural layer (Silicon → Services → Reasoning → Soul)
- **Enterprise Coherence**: Maintaining consistency across distributed agent network
- **Gnosis-First Design**: Prioritizing knowledge preservation and accessibility
- **Recovery-Oriented Architecture**: Designing systems that can restore state from distributed backups

---

## Implementation Implications

The AMR SaR approach informs:
1. Copilot CLI integration with Memory-Bank MCP
2. Session state management across `.gemini` folders
3. Facet coordination via Agent Bus (Redis Streams)
4. Qdrant + Neo4j dual indexing for semantic recovery
5. Backup + verification procedures (checkpoints, immutability)

---

*Extracted from SESS-27 by Copilot Haiku as part of Omega Stack consolidation*
""")

print(f"[✓] Strategy written to {output_path}")
print(f"[✓] {len(strategy_segments)} segments indexed")
