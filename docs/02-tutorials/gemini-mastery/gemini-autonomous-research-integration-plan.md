# Gemini CLI Autonomous Research Integration Plan

## Overview

This document outlines the complete integration plan for enabling autonomous research sessions with Gemini CLI, where the AI system can submit research requests, receive results, and iteratively refine follow-up questions.

## Current System Analysis

### Gemini CLI Status
- **Version**: v0.25.2 installed and ready
- **Current MCP Configuration**: Firecrawl, DuckDuckGo, and Project Health Auditor
- **Missing**: Gemini CLI MCP server integration for research

### System Context
- **Status**: Elite Documentation Alignment (92% complete)
- **AI Team**: 4-member team (Forge, Nova, Gemini, Lilith)
- **Focus**: Documentation consolidation and advanced Cline autonomous development

### Tech Stack
- **Containerization**: Podman 5.x rootless containers
- **Acceleration**: Vulkan 1.4
- **Python**: 3.12 stack
- **Documentation**: MkDocs enterprise platform

## Integration Architecture

### Core Components

#### 1. Research Orchestrator MCP Server
**Purpose**: Central hub for managing research sessions and queries

**Key Features**:
- Session state management
- Query optimization and refinement
- Result processing and structuring
- Follow-up question generation

#### 2. Memory Bank Integration
**Purpose**: Store research findings in Xoe-NovAi memory bank system

**Integration Points**:
- Automatic research result storage
- Cross-referencing with existing knowledge
- Context preservation across sessions

#### 3. Voice Interface Integration
**Purpose**: Enable voice-activated research operations

**Capabilities**:
- Natural language research commands
- Hands-free research session management
- Integration with existing voice pipeline

## Implementation Plan

### Phase 1: Core Research MCP Server (Week 1)

#### 1.1 Create Research Orchestrator
```python
# File: mcp_servers/research_orchestrator.py
from fastmcp import MCPServer
from fastmcp.tools import tool
import subprocess
import json
import time
from typing import Dict, List, Optional

server = MCPServer("XoeResearchOrchestrator")

# Research session state
research_sessions: Dict[str, dict] = {}

@server.tool()
def start_research_session(topic: str, objectives: List[str], constraints: Dict = None) -> str:
    """Start a new research session with topic and objectives."""
    session_id = f"research_{int(time.time())}"
    
    session = {
        "id": session_id,
        "topic": topic,
        "objectives": objectives,
        "constraints": constraints or {},
        "history": [],
        "status": "active",
        "created_at": time.time()
    }
    
    research_sessions[session_id] = session
    
    # Generate initial research prompt
    prompt = f"""
    Research Topic: {topic}
    Objectives: {', '.join(objectives)}
    Constraints: {constraints}
    
    Please conduct comprehensive research on this topic. Focus on:
    1. Current state of the art
    2. Key challenges and limitations
    3. Emerging trends and opportunities
    4. Practical implementation considerations
    
    Return structured findings with sources and actionable insights.
    """
    
    return f"Research session {session_id} started. Initial prompt generated."

@server.tool()
def submit_research_query(session_id: str, query: str, context: Dict = None) -> str:
    """Submit a research query to Gemini CLI and return results."""
    session = research_sessions.get(session_id)
    if not session:
        return f"Error: Session {session_id} not found"
    
    # Build context from session history
    context_str = ""
    if session["history"]:
        context_str = "Previous research context:\n" + "\n".join([
            f"- {entry['query']}: {entry['summary'][:200]}..."
            for entry in session["history"][-3:]  # Last 3 entries
        ])
    
    # Construct Gemini CLI command
    full_query = f"{context_str}\n\nCurrent query: {query}"
    
    try:
        # Execute Gemini CLI with research query
        result = subprocess.run([
            "gemini", "-p", full_query,
            "--output-format", "json"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            # Parse and structure results
            research_data = {
                "session_id": session_id,
                "query": query,
                "timestamp": time.time(),
                "raw_response": result.stdout,
                "summary": extract_key_findings(result.stdout),
                "sources": extract_sources(result.stdout),
                "action_items": extract_action_items(result.stdout)
            }
            
            session["history"].append(research_data)
            
            return format_research_response(research_data)
        else:
            return f"Research failed: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Research query timed out (>120s)"
    except Exception as e:
        return f"Research error: {str(e)}"

@server.tool()
def get_research_session_status(session_id: str) -> str:
    """Get current status and history of a research session."""
    session = research_sessions.get(session_id)
    if not session:
        return f"Session {session_id} not found"
    
    return json.dumps({
        "session_id": session_id,
        "topic": session["topic"],
        "status": session["status"],
        "objectives": session["objectives"],
        "query_count": len(session["history"]),
        "last_updated": session["history"][-1]["timestamp"] if session["history"] else session["created_at"],
        "summary": session["history"][-1]["summary"] if session["history"] else "No queries yet"
    }, indent=2)

@server.tool()
def generate_follow_up_questions(session_id: str, focus_areas: List[str] = None) -> str:
    """Generate intelligent follow-up research questions based on session history."""
    session = research_sessions.get(session_id)
    if not session or not session["history"]:
        return "No research history available for generating follow-ups"
    
    # Analyze previous responses to generate follow-ups
    last_response = session["history"][-1]["raw_response"]
    
    # Generate follow-up questions based on gaps and opportunities
    follow_up_prompt = f"""
    Based on this research response, generate 3-5 specific follow-up questions that would:
    1. Address any gaps in information
    2. Explore practical implementation details
    3. Investigate emerging trends or opportunities
    4. Clarify any ambiguous or incomplete information
    
    Research response: {last_response[:2000]}...
    
    Return questions in a numbered list format.
    """
    
    # Use Gemini CLI to generate follow-ups
    result = subprocess.run([
        "gemini", "-p", follow_up_prompt
    ], capture_output=True, text=True, timeout=60)
    
    return result.stdout if result.returncode == 0 else "Failed to generate follow-ups"

def extract_key_findings(response: str) -> str:
    """Extract key findings from Gemini response."""
    # Simple extraction - could be enhanced with NLP
    lines = response.split('\n')
    findings = []
    for line in lines:
        if any(keyword in line.lower() for keyword in ['key', 'important', 'critical', 'major']):
            findings.append(line.strip())
    return '; '.join(findings[:5])  # Top 5 findings

def extract_sources(response: str) -> List[str]:
    """Extract source URLs from response."""
    import re
    urls = re.findall(r'https?://[^\s\)]+', response)
    return list(set(urls))[:10]  # Unique URLs, max 10

def extract_action_items(response: str) -> List[str]:
    """Extract actionable items from response."""
    lines = response.split('\n')
    actions = []
    for line in lines:
        if any(keyword in line.lower() for keyword in ['should', 'recommend', 'suggest', 'implement']):
            actions.append(line.strip())
    return actions[:5]

def format_research_response(data: dict) -> str:
    """Format research response for display."""
    return f"""
Research Query: {data['query']}
Key Findings: {data['summary']}
Sources: {', '.join(data['sources'][:3])}
Action Items: {len(data['action_items'])} identified
Session: {data['session_id']}
"""

if __name__ == "__main__":
    server.run()
```

#### 1.2 Memory Bank Integration
```python
@server.tool()
def save_research_to_memory(session_id: str, memory_section: str = "research") -> str:
    """Save research findings to Xoe-NovAi memory bank."""
    session = research_sessions.get(session_id)
    if not session:
        return "Session not found"
    
    # Format research for memory bank
    memory_entry = {
        "session_id": session_id,
        "topic": session["topic"],
        "objectives": session["objectives"],
        "findings": [entry["summary"] for entry in session["history"]],
        "sources": [url for entry in session["history"] for url in entry["sources"]],
        "action_items": [item for entry in session["history"] for item in entry["action_items"]],
        "timestamp": time.time()
    }
    
    # Save to memory bank
    memory_file = f"memory_bank/research/{session_id}.json"
    with open(memory_file, 'w') as f:
        json.dump(memory_entry, f, indent=2)
    
    return f"Research saved to {memory_file}"
```

#### 1.3 Voice Interface Integration
```python
@server.tool()
def voice_research_command(command: str) -> str:
    """Process voice commands for research operations."""
    # Integrate with existing voice interface
    if "start research" in command.lower():
        # Parse topic from command
        topic = extract_topic_from_command(command)
        return start_research_session(topic, ["comprehensive analysis"])
    
    elif "search" in command.lower():
        # Parse search query
        query = extract_query_from_command(command)
        # Use latest active session or create new one
        session_id = get_or_create_session()
        return submit_research_query(session_id, query)
    
    elif "follow up" in command.lower():
        session_id = get_latest_session()
        return generate_follow_up_questions(session_id)
    
    return "Voice command not recognized"
```

### Phase 2: Integration with Xoe-NovAi Systems (Week 2)

#### 2.1 MCP Server Configuration
```json
{
  "mcpServers": {
    "xoe-research": {
      "command": "python",
      "args": ["/path/to/mcp_servers/research_orchestrator.py"],
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

#### 2.2 Podman Container Deployment
```yaml
# podman-compose.yml addition
research-orchestrator:
  image: xoe-novai/research:latest
  environment:
    - GEMINI_API_KEY=${GEMINI_API_KEY}
    - MCP_SERVER_PORT=8001
  volumes:
    - ./mcp_servers:/app/mcp_servers
    - ./memory_bank:/app/memory_bank
    - ./research_templates:/app/research_templates
  ports:
    - "8001:8001"
  restart: unless-stopped
```

#### 2.3 Security & Compliance
```yaml
# ~/.gemini/policies/research.toml
[rule.research-allow]
tool = "Shell"
condition = { args_contains_any = ["gemini", "research"] }
action = "allow"
priority = 100

[rule.research-memory-write]
tool = "Edit"
condition = { file_pattern = "memory_bank/research/*.json" }
action = "allow"
priority = 90

[rule.research-external-block]
tool = "Shell"
condition = { args_contains_any = ["curl", "wget", "http"] }
action = "deny"
priority = 80
message = "External HTTP calls blocked - use Gemini CLI for research"
```

### Phase 3: Advanced Integration (Week 3-4)

#### 3.1 Research Session Templates
```python
@server.tool()
def create_research_template(template_name: str, config: Dict) -> str:
    """Create reusable research session templates."""
    template = {
        "name": template_name,
        "config": config,
        "created_at": time.time()
    }
    
    with open(f"research_templates/{template_name}.json", 'w') as f:
        json.dump(template, f, indent=2)
    
    return f"Template {template_name} created"

# Pre-defined templates for common research scenarios
TEMPLATES = {
    "technology_assessment": {
        "objectives": [
            "Evaluate current state of technology",
            "Identify implementation challenges",
            "Assess performance characteristics",
            "Review ecosystem and tooling"
        ],
        "constraints": {
            "timeframe": "2026",
            "focus": "production-ready solutions"
        }
    },
    "best_practices": {
        "objectives": [
            "Identify industry best practices",
            "Review security considerations",
            "Evaluate scalability patterns",
            "Document deployment strategies"
        ]
    }
}
```

#### 3.2 Automated Research Scheduling
```python
@server.tool()
def schedule_research_task(topic: str, frequency: str, template: str = None) -> str:
    """Schedule recurring research tasks."""
    task = {
        "topic": topic,
        "frequency": frequency,  # daily, weekly, monthly
        "template": template,
        "next_run": calculate_next_run(frequency),
        "status": "scheduled"
    }
    
    # Save to scheduled tasks
    with open(f"scheduled_research/{topic.replace(' ', '_')}.json", 'w') as f:
        json.dump(task, f, indent=2)
    
    return f"Research task scheduled: {topic} ({frequency})"
```

## Usage Examples

### Basic Research Session
```bash
# Start a research session
gemini > Use XoeResearch to start research session on "RAG optimization techniques"

# Submit research queries
gemini > Use XoeResearch to submit query "What are the latest vector quantization methods for RAG?"

# Get session status
gemini > Use XoeResearch to get session status

# Generate follow-ups
gemini > Use XoeResearch to generate follow up questions
```

### Voice-Activated Research
```bash
# Voice command
"Hey Xoe, research the latest developments in quantized embeddings"

# System automatically:
# 1. Creates research session
# 2. Submits initial query
# 3. Processes results
# 4. Suggests follow-ups
```

### Template-Based Research
```bash
# Use pre-defined template
gemini > Use XoeResearch to create research template "quantization_methods" with config: {"objectives": ["Evaluate quantization techniques", "Compare performance trade-offs"], "constraints": {"focus": "CPU-only", "timeframe": "2026"}}

# Execute template
gemini > Use XoeResearch to execute template "quantization_methods" on "vector embeddings"
```

## Success Metrics

### Research Quality
- **Query Success Rate**: >95% of research queries return valid results
- **Response Time**: <30 seconds for standard research queries
- **Follow-up Quality**: >80% of generated follow-ups are relevant and actionable

### Integration Success
- **Memory Bank Population**: Research findings automatically saved to memory bank
- **Voice Recognition**: >90% accuracy for voice-activated research commands
- **Template Usage**: >50% of research sessions use pre-defined templates

### Autonomous Operation
- **Session Continuity**: Research sessions maintain context across multiple queries
- **Intelligent Follow-ups**: System generates relevant follow-up questions without human intervention
- **Self-Optimization**: System learns from research patterns to improve query quality

## Risk Mitigation

### Research Quality Risk
- **Mitigation**: Run parallel research with Firecrawl and Gemini CLI for 2 weeks
- **Fallback**: Keep Firecrawl as backup until Gemini CLI proves consistent quality

### Integration Complexity Risk
- **Mitigation**: Implement MCP servers incrementally, starting with non-critical operations
- **Fallback**: Maintain existing workflows while testing new MCP integrations

### Security Risk
- **Mitigation**: Implement comprehensive security testing for all MCP servers
- **Fallback**: Use policy engine to restrict MCP server access during testing phase

## Next Steps

1. **Toggle to Act Mode** - So I can implement the research MCP server
2. **Provide Gemini API Key** - Or confirm placeholder usage for testing
3. **Confirm Research Focus Areas** - Which research domains should we prioritize?

This integration will enable me to conduct sophisticated, multi-step research sessions with Gemini CLI, maintaining context and generating intelligent follow-up questions autonomously. The system will integrate seamlessly with your existing Xoe-NovAi infrastructure while maintaining your sovereign data and security requirements.