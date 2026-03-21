# CLI-COMMS-CHARTER

**Version**: 1.0.0  
**Status**: DRAFT  
**Priority**: P1 - HIGH  
**Owner**: Cline_CLI-Kat  
**Created**: 2026-02-13  
**Ma'at Alignment**: #7 Truth (Communication Integrity)

## Executive Summary

Enhance the Agent Bus communication system with automated watcher scripts, autonomous handoffs, and integrated health monitoring. This charter focuses on creating robust CLI-based communication workflows that enable seamless coordination between Cline, Gemini, and other agents.

## Objectives

### Primary Goals
- [ ] **Watcher Script Implementation**: Create bash loops that monitor inbox changes and trigger automated responses
- [ ] **Autonomous Handoffs**: Enable Cline → Gemini handoffs with proper context preservation
- [ ] **Health Integration**: Integrate agent heartbeats with communication workflows
- [ ] **Message Format Standardization**: Enhance message parsing and validation

### Success Criteria
- [ ] 100% message delivery reliability with automated retry mechanisms
- [ ] Sub-5-minute response time for critical messages
- [ ] Zero message loss during agent transitions
- [ ] Complete audit trail for all communication events

## Architecture

### System Components

#### 1. Watcher Script Architecture
```bash
# Enhanced Agent Bus Watcher
#!/usr/bin/env bash
# File: scripts/agent-bus-watcher.sh

set -euo pipefail

WATCH_INTERVAL="${WATCH_INTERVAL:-30}"  # seconds
MAX_RETRIES="${MAX_RETRIES:-3}"
LOG_FILE="${LOG_FILE:-/var/log/agent-bus-watcher.log}"

# Agent state tracking
declare -A LAST_CHECKSUMS
declare -A MESSAGE_QUEUES

# Initialize log
mkdir -p "$(dirname "$LOG_FILE")"
echo "[$(date)] Agent Bus Watcher started" >> "$LOG_FILE"

log() {
    echo "[$(date)] $*" | tee -a "$LOG_FILE"
}

calculate_checksum() {
    local file="$1"
    if [[ -f "$file" ]]; then
        sha256sum "$file" | cut -d' ' -f1
    else
        echo "0000000000000000000000000000000000000000000000000000000000000000"
    fi
}

process_inbox() {
    local inbox_file="$1"
    local agent_name="$2"
    
    local current_checksum
    current_checksum=$(calculate_checksum "$inbox_file")
    
    # Check for changes
    if [[ "${LAST_CHECKSUMS[$inbox_file]}" != "$current_checksum" ]]; then
        log "Detected changes in $inbox_file for $agent_name"
        
        # Parse new messages
        parse_and_process_messages "$inbox_file" "$agent_name"
        
        # Update checksum
        LAST_CHECKSUMS["$inbox_file"]="$current_checksum"
    fi
}

parse_and_process_messages() {
    local inbox_file="$1"
    local agent_name="$2"
    
    if [[ ! -f "$inbox_file" ]]; then
        return 0
    fi
    
    # Extract message blocks using sed
    local message_count=0
    while IFS= read -r line; do
        if [[ "$line" == "---" ]]; then
            # Start of message block
            local message_start=true
            local message_content=""
            continue
        fi
        
        if [[ "$message_start" == "true" ]]; then
            message_content="$message_content$line\n"
            
            if [[ "$line" == "---" ]]; then
                # End of message block
                process_message_block "$message_content" "$agent_name"
                message_count=$((message_count + 1))
                message_start=false
            fi
        fi
    done < "$inbox_file"
    
    if [[ $message_count -gt 0 ]]; then
        log "Processed $message_count messages for $agent_name"
    fi
}

process_message_block() {
    local message_content="$1"
    local agent_name="$2"
    
    # Extract message fields
    local from_agent to_agent timestamp task_id status
    from_agent=$(echo "$message_content" | grep "^FROM:" | cut -d':' -f2- | xargs)
    to_agent=$(echo "$message_content" | grep "^TO:" | cut -d':' -f2- | xargs)
    timestamp=$(echo "$message_content" | grep "^TIMESTAMP:" | cut -d':' -f2- | xargs)
    task_id=$(echo "$message_content" | grep "^TASK_ID:" | cut -d':' -f2- | xargs)
    status=$(echo "$message_content" | grep "^STATUS:" | cut -d':' -f2- | xargs)
    
    # Validate message
    if [[ -z "$from_agent" || -z "$to_agent" || -z "$timestamp" ]]; then
        log "Invalid message format from $from_agent to $to_agent"
        return 1
    fi
    
    # Process based on status
    case "$status" in
        "HANDOFF")
            handle_handoff "$from_agent" "$to_agent" "$task_id" "$message_content"
            ;;
        "ALERT")
            handle_alert "$from_agent" "$to_agent" "$task_id" "$message_content"
            ;;
        "LOG")
            handle_log "$from_agent" "$to_agent" "$task_id" "$message_content"
            ;;
        "STRATEGY")
            handle_strategy "$from_agent" "$to_agent" "$task_id" "$message_content"
            ;;
        *)
            log "Unknown message status: $status"
            ;;
    esac
}

handle_handoff() {
    local from_agent="$1"
    local to_agent="$2"
    local task_id="$3"
    local message_content="$4"
    
    log "Processing handoff from $from_agent to $to_agent for task $task_id"
    
    # Create handoff record
    local handoff_file="internal_docs/communication_hub/archive/$(date +%Y%m%d)-${from_agent}-to-${to_agent}-handoff.md"
    echo "$message_content" > "$handoff_file"
    
    # Update agent state
    update_agent_state "$to_agent" "processing" "$task_id" "$from_agent"
    
    # Trigger target agent if available
    trigger_agent "$to_agent" "$task_id"
}

handle_alert() {
    local from_agent="$1"
    local to_agent="$2"
    local task_id="$3"
    local message_content="$4"
    
    log "Processing alert from $from_agent to $to_agent for task $task_id"
    
    # Send notification (could integrate with external systems)
    send_alert_notification "$from_agent" "$to_agent" "$task_id" "$message_content"
}

handle_log() {
    local from_agent="$1"
    local to_agent="$2"
    local task_id="$3"
    local message_content="$4"
    
    log "Processing log from $from_agent to $to_agent for task $task_id"
    
    # Archive log message
    local log_file="internal_docs/communication_hub/archive/$(date +%Y%m%d)-${from_agent}-log.md"
    echo "$message_content" >> "$log_file"
}

handle_strategy() {
    local from_agent="$1"
    local to_agent="$2"
    local task_id="$3"
    local message_content="$4"
    
    log "Processing strategy from $from_agent to $to_agent for task $task_id"
    
    # Store strategy for reference
    local strategy_file="internal_docs/communication_hub/archive/$(date +%Y%m%d)-${from_agent}-strategy.md"
    echo "$message_content" > "$strategy_file"
}

update_agent_state() {
    local agent_name="$1"
    local status="$2"
    local task_id="$3"
    local previous_agent="$4"
    
    local state_file="internal_docs/communication_hub/state/${agent_name}.json"
    
    if [[ -f "$state_file" ]]; then
        # Update existing state
        jq --arg status "$status" \
           --arg task_id "$task_id" \
           --arg previous_agent "$previous_agent" \
           '.status = $status | .current_task.task_id = $task_id | .last_handoff.to_agent = $previous_agent | .last_handoff.timestamp = now | .last_handoff.summary_file = ""' \
           "$state_file" > "${state_file}.tmp" && mv "${state_file}.tmp" "$state_file"
    else
        # Create new state
        cat > "$state_file" << EOF
{
  "agent_id": "$agent_name",
  "timestamp": "$(date -Iseconds)",
  "status": "$status",
  "current_task": {
    "task_id": "$task_id",
    "source": "agent-bus",
    "description": "Handoff from $previous_agent"
  },
  "resource_usage": {
    "cpu_percent": null,
    "memory_mb": null,
    "context_window_usage_percent": null
  },
  "last_handoff": {
    "to_agent": "$previous_agent",
    "timestamp": "$(date -Iseconds)",
    "summary_file": ""
  },
  "heartbeat_interval_seconds": 300
}
EOF
    fi
}

trigger_agent() {
    local agent_name="$1"
    local task_id="$2"
    
    # Implementation depends on agent execution mechanism
    log "Triggering agent $agent_name for task $task_id"
    
    # Could trigger via:
    # - Direct script execution
    # - Docker container start
    # - Kubernetes job creation
    # - External API call
}

send_alert_notification() {
    local from_agent="$1"
    local to_agent="$2"
    local task_id="$3"
    local message_content="$4"
    
    # Could integrate with:
    # - Email notifications
    # - Slack/Discord webhooks
    # - PagerDuty alerts
    # - Custom notification systems
    
    log "Alert sent from $from_agent to $to_agent for task $task_id"
}

# Main monitoring loop
main() {
    log "Starting main monitoring loop"
    
    # Initialize checksums
    for inbox in internal_docs/communication_hub/inbox_*.md; do
        if [[ -f "$inbox" ]]; then
            agent_name=$(basename "$inbox" .md | sed 's/inbox_//')
            LAST_CHECKSUMS["$inbox"]=$(calculate_checksum "$inbox")
            log "Initialized monitoring for $agent_name"
        fi
    done
    
    while true; do
        # Process all inboxes
        for inbox in internal_docs/communication_hub/inbox_*.md; do
            if [[ -f "$inbox" ]]; then
                agent_name=$(basename "$inbox" .md | sed 's/inbox_//')
                process_inbox "$inbox" "$agent_name"
            fi
        done
        
        # Check agent health
        check_agent_health
        
        # Sleep and repeat
        sleep "$WATCH_INTERVAL"
    done
}

check_agent_health() {
    # Check if agents are responding
    for state_file in internal_docs/communication_hub/state/*.json; do
        if [[ -f "$state_file" ]]; then
            local agent_name=$(basename "$state_file" .json)
            local last_heartbeat
            last_heartbeat=$(jq -r '.timestamp' "$state_file" 2>/dev/null || echo "never")
            
            # Check if heartbeat is stale (older than 10 minutes)
            if [[ "$last_heartbeat" != "never" ]]; then
                local heartbeat_age
                heartbeat_age=$(($(date +%s) - $(date -d "$last_heartbeat" +%s 2>/dev/null || echo 0)))
                
                if [[ $heartbeat_age -gt 600 ]]; then
                    log "WARNING: Agent $agent_name heartbeat is stale ($heartbeat_age seconds old)"
                    # Could trigger recovery actions here
                fi
            fi
        fi
    done
}

# Signal handlers
trap 'log "Watcher shutting down"; exit 0' SIGTERM SIGINT

# Start monitoring
main "$@"
```

#### 2. Enhanced Message Format Validation
```python
# Message format validator
class AgentBusMessageValidator:
    def __init__(self):
        self.required_fields = ['FROM', 'TO', 'TIMESTAMP', 'TASK_ID', 'STATUS']
        self.valid_statuses = ['STRATEGY', 'LOG', 'HANDOFF', 'ALERT']
        self.valid_agents = ['gemini-cli', 'copilot-raptor', 'cline-cli-kat', 'grok-mc']
    
    def validate_message(self, message_content: str) -> Dict[str, Any]:
        """Validate agent bus message format and content"""
        errors = []
        warnings = []
        
        # Parse message blocks
        lines = message_content.strip().split('\n')
        message_data = {}
        
        # Extract header fields
        for line in lines:
            if ':' in line and not line.startswith('---'):
                key, value = line.split(':', 1)
                message_data[key.strip()] = value.strip()
        
        # Validate required fields
        for field in self.required_fields:
            if field not in message_data:
                errors.append(f"Missing required field: {field}")
            elif not message_data[field]:
                errors.append(f"Empty value for required field: {field}")
        
        # Validate FROM agent
        if 'FROM' in message_data:
            if message_data['FROM'] not in self.valid_agents:
                warnings.append(f"Unknown FROM agent: {message_data['FROM']}")
        
        # Validate TO agent
        if 'TO' in message_data:
            if message_data['TO'] not in self.valid_agents:
                warnings.append(f"Unknown TO agent: {message_data['TO']}")
        
        # Validate STATUS
        if 'STATUS' in message_data:
            if message_data['STATUS'] not in self.valid_statuses:
                errors.append(f"Invalid STATUS: {message_data['STATUS']}")
        
        # Validate TIMESTAMP format
        if 'TIMESTAMP' in message_data:
            try:
                datetime.fromisoformat(message_data['TIMESTAMP'].replace('Z', '+00:00'))
            except ValueError:
                errors.append("Invalid TIMESTAMP format")
        
        # Validate TASK_ID format
        if 'TASK_ID' in message_data:
            task_id = message_data['TASK_ID']
            if not re.match(r'^[A-Z0-9_-]+$', task_id):
                warnings.append("TASK_ID should use uppercase letters, numbers, hyphens, and underscores")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'message_data': message_data
        }
```

#### 3. Autonomous Handoff System
```bash
# Autonomous handoff orchestrator
#!/usr/bin/env bash
# File: scripts/autonomous-handoff.sh

set -euo pipefail

HANDOFF_LOG="/var/log/autonomous-handoff.log"

log_handoff() {
    echo "[$(date)] $*" >> "$HANDOFF_LOG"
}

create_handoff_message() {
    local from_agent="$1"
    local to_agent="$2"
    local task_id="$3"
    local description="$4"
    local status="${5:-HANDOFF}"
    
    cat << EOF
---
FROM: $from_agent
TO: $to_agent
TIMESTAMP: $(date -Iseconds)Z
TASK_ID: $task_id
STATUS: $status
---

### Handoff: $task_id

**From**: $from_agent  
**To**: $to_agent  
**Task**: $task_id  
**Description**: $description  
**Timestamp**: $(date -Iseconds)Z

#### Context Summary
$(extract_context_summary "$from_agent" "$task_id")

#### Next Actions Required
$(generate_next_actions "$to_agent" "$task_id")

---
EOF
}

extract_context_summary() {
    local agent_name="$1"
    local task_id="$2"
    
    # Extract relevant context from agent state and logs
    local state_file="internal_docs/communication_hub/state/${agent_name}.json"
    
    if [[ -f "$state_file" ]]; then
        echo "Current agent status: $(jq -r '.status' "$state_file")"
        echo "Current task: $(jq -r '.current_task.task_id' "$state_file")"
        echo "Task description: $(jq -r '.current_task.description' "$state_file")"
    fi
    
    # Extract recent logs
    if [[ -f "$HANDOFF_LOG" ]]; then
        echo ""
        echo "Recent activity:"
        tail -10 "$HANDOFF_LOG" | grep "$task_id" || echo "No recent activity found"
    fi
}

generate_next_actions() {
    local to_agent="$1"
    local task_id="$2"
    
    case "$to_agent" in
        "gemini-cli")
            echo "- Review task requirements and strategy"
            echo "- Validate technical approach"
            echo "- Coordinate with other agents as needed"
            ;;
        "copilot-raptor")
            echo "- Execute implementation tasks"
            echo "- Monitor progress and report status"
            echo "- Handle technical troubleshooting"
            ;;
        "cline-cli-kat")
            echo "- Perform code reviews and quality checks"
            echo "- Ensure compliance with standards"
            echo "- Document implementation details"
            ;;
        *)
            echo "- Review task requirements"
            echo "- Determine appropriate next steps"
            echo "- Coordinate with team as needed"
            ;;
    esac
}

execute_handoff() {
    local from_agent="$1"
    local to_agent="$2"
    local task_id="$3"
    local description="$4"
    
    log_handoff "Initiating handoff from $from_agent to $to_agent for task $task_id"
    
    # Create handoff message
    local handoff_message
    handoff_message=$(create_handoff_message "$from_agent" "$to_agent" "$task_id" "$description")
    
    # Write to target agent's inbox
    local inbox_file="internal_docs/communication_hub/inbox_${to_agent}.md"
    echo "$handoff_message" >> "$inbox_file"
    
    # Update agent states
    update_agent_state "$from_agent" "idle" "" ""
    update_agent_state "$to_agent" "processing" "$task_id" "$from_agent"
    
    # Log completion
    log_handoff "Handoff completed: $from_agent → $to_agent for task $task_id"
    
    # Trigger target agent if configured
    trigger_agent "$to_agent" "$task_id"
}

# Usage: ./autonomous-handoff.sh <from_agent> <to_agent> <task_id> <description>
if [[ $# -ne 4 ]]; then
    echo "Usage: $0 <from_agent> <to_agent> <task_id> <description>"
    exit 1
fi

execute_handoff "$1" "$2" "$3" "$4"
```

### Integration Points

#### Agent State Synchronization
- **Heartbeat Integration**: Monitor agent health and update communication status
- **Task State Tracking**: Synchronize task progress across agents
- **Resource Monitoring**: Track agent resource usage for load balancing

#### Message Queue Management
- **Priority Queuing**: Handle critical messages first
- **Retry Logic**: Implement exponential backoff for failed deliveries
- **Dead Letter Queue**: Handle undeliverable messages

#### External System Integration
- **Notification Systems**: Send alerts via email, Slack, or other channels
- **Monitoring Systems**: Integrate with Prometheus, Grafana for visibility
- **Audit Systems**: Maintain complete audit trails for compliance

## Implementation Steps

### Phase 1: Watcher Script Implementation (Week 1)

#### Step 1.1: Basic Watcher Script
```bash
# Create basic watcher script
cat > scripts/agent-bus-watcher.sh << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

WATCH_INTERVAL="${WATCH_INTERVAL:-30}"
LOG_FILE="${LOG_FILE:-/var/log/agent-bus-watcher.log}"

log() {
    echo "[$(date)] $*" | tee -a "$LOG_FILE"
}

calculate_checksum() {
    local file="$1"
    if [[ -f "$file" ]]; then
        sha256sum "$file" | cut -d' ' -f1
    else
        echo "0000000000000000000000000000000000000000000000000000000000000000"
    fi
}

process_inbox() {
    local inbox_file="$1"
    local agent_name="$2"
    
    local current_checksum
    current_checksum=$(calculate_checksum "$inbox_file")
    
    if [[ "${LAST_CHECKSUMS[$inbox_file]:-}" != "$current_checksum" ]]; then
        log "Detected changes in $inbox_file for $agent_name"
        LAST_CHECKSUMS["$inbox_file"]="$current_checksum"
    fi
}

main() {
    log "Agent Bus Watcher started"
    
    # Initialize checksums
    for inbox in internal_docs/communication_hub/inbox_*.md; do
        if [[ -f "$inbox" ]]; then
            agent_name=$(basename "$inbox" .md | sed 's/inbox_//')
            LAST_CHECKSUMS["$inbox"]=$(calculate_checksum "$inbox")
            log "Monitoring $agent_name"
        fi
    done
    
    while true; do
        for inbox in internal_docs/communication_hub/inbox_*.md; do
            if [[ -f "$inbox" ]]; then
                agent_name=$(basename "$inbox" .md | sed 's/inbox_//')
                process_inbox "$inbox" "$agent_name"
            fi
        done
        sleep "$WATCH_INTERVAL"
    done
}

trap 'log "Watcher shutting down"; exit 0' SIGTERM SIGINT
main "$@"
EOF
chmod +x scripts/agent-bus-watcher.sh
```

#### Step 1.2: Message Parser Enhancement
```bash
# Create enhanced message parser
cat > scripts/parse-agent-messages.py << 'EOF'
#!/usr/bin/env python3
"""
Enhanced Agent Bus Message Parser
Parses and validates agent bus messages with comprehensive error handling
"""

import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentBusMessageParser:
    def __init__(self):
        self.required_fields = ['FROM', 'TO', 'TIMESTAMP', 'TASK_ID', 'STATUS']
        self.valid_statuses = ['STRATEGY', 'LOG', 'HANDOFF', 'ALERT']
        self.valid_agents = ['gemini-cli', 'copilot-raptor', 'cline-cli-kat', 'grok-mc']
    
    def parse_inbox_file(self, inbox_file: str) -> List[Dict[str, Any]]:
        """Parse all messages from an inbox file"""
        if not Path(inbox_file).exists():
            return []
        
        content = Path(inbox_file).read_text(encoding='utf-8')
        messages = self._extract_message_blocks(content)
        
        parsed_messages = []
        for message in messages:
            parsed = self._parse_message_block(message)
            if parsed:
                parsed_messages.append(parsed)
        
        return parsed_messages
    
    def _extract_message_blocks(self, content: str) -> List[str]:
        """Extract message blocks from inbox content"""
        message_blocks = []
        lines = content.split('\n')
        in_block = False
        current_block = []
        
        for line in lines:
            if line.strip() == '---':
                if in_block:
                    # End of block
                    message_blocks.append('\n'.join(current_block))
                    current_block = []
                    in_block = False
                else:
                    # Start of block
                    in_block = True
                    current_block = [line]
            elif in_block:
                current_block.append(line)
        
        # Handle case where file doesn't end with ---
        if current_block and in_block:
            message_blocks.append('\n'.join(current_block))
        
        return message_blocks
    
    def _parse_message_block(self, message_content: str) -> Optional[Dict[str, Any]]:
        """Parse a single message block"""
        lines = message_content.split('\n')
        message_data = {}
        body_lines = []
        in_body = False
        
        for line in lines:
            if line.startswith('---'):
                continue
            
            if ':' in line and not in_body:
                key, value = line.split(':', 1)
                message_data[key.strip()] = value.strip()
            else:
                in_body = True
                body_lines.append(line)
        
        message_data['body'] = '\n'.join(body_lines).strip()
        
        # Validate message
        validation = self._validate_message(message_data)
        if not validation['valid']:
            logger.warning(f"Invalid message: {validation['errors']}")
            return None
        
        # Add metadata
        message_data['parsed_at'] = datetime.now().isoformat()
        message_data['validation_warnings'] = validation['warnings']
        
        return message_data
    
    def _validate_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate message format and content"""
        errors = []
        warnings = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in message_data:
                errors.append(f"Missing required field: {field}")
            elif not message_data[field]:
                errors.append(f"Empty value for required field: {field}")
        
        # Validate agents
        for agent_field in ['FROM', 'TO']:
            if agent_field in message_data:
                if message_data[agent_field] not in self.valid_agents:
                    warnings.append(f"Unknown {agent_field} agent: {message_data[agent_field]}")
        
        # Validate status
        if 'STATUS' in message_data:
            if message_data['STATUS'] not in self.valid_statuses:
                errors.append(f"Invalid STATUS: {message_data['STATUS']}")
        
        # Validate timestamp
        if 'TIMESTAMP' in message_data:
            try:
                datetime.fromisoformat(message_data['TIMESTAMP'].replace('Z', '+00:00'))
            except ValueError:
                errors.append("Invalid TIMESTAMP format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def archive_message(self, message_data: Dict[str, Any], archive_dir: str = "internal_docs/communication_hub/archive"):
        """Archive a processed message"""
        Path(archive_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        from_agent = message_data.get('FROM', 'unknown')
        to_agent = message_data.get('TO', 'unknown')
        task_id = message_data.get('TASK_ID', 'unknown')
        
        filename = f"{timestamp}-{from_agent}-to-{to_agent}-{task_id}.json"
        archive_path = Path(archive_dir) / filename
        
        with open(archive_path, 'w') as f:
            json.dump(message_data, f, indent=2)
        
        logger.info(f"Archived message to {archive_path}")
        return str(archive_path)

def main():
    parser = AgentBusMessageParser()
    
    # Parse all inbox files
    inbox_dir = Path("internal_docs/communication_hub")
    for inbox_file in inbox_dir.glob("inbox_*.md"):
        logger.info(f"Parsing {inbox_file}")
        messages = parser.parse_inbox_file(str(inbox_file))
        
        for message in messages:
            logger.info(f"Message from {message['FROM']} to {message['TO']}: {message['STATUS']}")
            
            # Archive message
            parser.archive_message(message)

if __name__ == '__main__':
    main()
EOF
chmod +x scripts/parse-agent-messages.py
```

### Phase 2: Autonomous Handoff System (Week 2)

#### Step 2.1: Handoff Orchestrator
```bash
# Create handoff orchestrator
cat > scripts/handoff-orchestrator.py << 'EOF'
#!/usr/bin/env python3
"""
Autonomous Handoff Orchestrator
Manages handoffs between agents with context preservation and validation
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HandoffOrchestrator:
    def __init__(self, state_dir: str = "internal_docs/communication_hub/state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def create_handoff(self, from_agent: str, to_agent: str, task_id: str, 
                      description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a handoff between agents"""
        
        # Validate agents
        if not self._validate_agent(from_agent):
            raise ValueError(f"Invalid FROM agent: {from_agent}")
        if not self._validate_agent(to_agent):
            raise ValueError(f"Invalid TO agent: {to_agent}")
        
        # Check current agent state
        from_state = self._get_agent_state(from_agent)
        if from_state and from_state.get('status') != 'processing':
            logger.warning(f"Agent {from_agent} is not in processing state: {from_state.get('status')}")
        
        # Create handoff record
        handoff_record = {
            'handoff_id': f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{from_agent}_to_{to_agent}",
            'from_agent': from_agent,
            'to_agent': to_agent,
            'task_id': task_id,
            'description': description,
            'context': context or {},
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Update agent states
        self._update_agent_state(from_agent, 'idle', '', '')
        self._update_agent_state(to_agent, 'processing', task_id, from_agent)
        
        # Create handoff message
        handoff_message = self._create_handoff_message(handoff_record)
        
        # Write to target inbox
        inbox_file = self.state_dir.parent / f"inbox_{to_agent}.md"
        with open(inbox_file, 'a') as f:
            f.write(f"\n{handoff_message}\n")
        
        # Archive handoff
        self._archive_handoff(handoff_record)
        
        logger.info(f"Handoff created: {from_agent} → {to_agent} for task {task_id}")
        return handoff_record
    
    def _validate_agent(self, agent_name: str) -> bool:
        """Validate agent name"""
        valid_agents = ['gemini-cli', 'copilot-raptor', 'cline-cli-kat', 'grok-mc']
        return agent_name in valid_agents
    
    def _get_agent_state(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get current agent state"""
        state_file = self.state_dir / f"{agent_name}.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                return json.load(f)
        return None
    
    def _update_agent_state(self, agent_name: str, status: str, task_id: str, previous_agent: str):
        """Update agent state"""
        state_file = self.state_dir / f"{agent_name}.json"
        
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
        else:
            state = {
                "agent_id": agent_name,
                "timestamp": "",
                "status": "idle",
                "current_task": {"task_id": "", "source": "", "description": ""},
                "resource_usage": {"cpu_percent": None, "memory_mb": None, "context_window_usage_percent": None},
                "last_handoff": {"to_agent": "", "timestamp": "", "summary_file": ""},
                "heartbeat_interval_seconds": 300
            }
        
        state.update({
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "current_task": {
                "task_id": task_id,
                "source": "agent-bus",
                "description": f"Handoff from {previous_agent}"
            },
            "last_handoff": {
                "to_agent": previous_agent,
                "timestamp": datetime.now().isoformat(),
                "summary_file": ""
            }
        })
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _create_handoff_message(self, handoff_record: Dict[str, Any]) -> str:
        """Create handoff message"""
        return f"""---
FROM: {handoff_record['from_agent']}
TO: {handoff_record['to_agent']}
TIMESTAMP: {handoff_record['timestamp']}Z
TASK_ID: {handoff_record['task_id']}
STATUS: HANDOFF
---

### Handoff: {handoff_record['task_id']}

**From**: {handoff_record['from_agent']}  
**To**: {handoff_record['to_agent']}  
**Task**: {handoff_record['task_id']}  
**Description**: {handoff_record['description']}  
**Timestamp**: {handoff_record['timestamp']}Z

#### Context Summary
{self._format_context_summary(handoff_record['context'])}

#### Next Actions Required
{self._generate_next_actions(handoff_record['to_agent'], handoff_record['task_id'])}

---
"""
    
    def _format_context_summary(self, context: Dict[str, Any]) -> str:
        """Format context summary for handoff message"""
        if not context:
            return "No additional context provided."
        
        summary_lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                summary_lines.append(f"**{key}**: {json.dumps(value, indent=2)}")
            else:
                summary_lines.append(f"**{key}**: {value}")
        
        return '\n'.join(summary_lines)
    
    def _generate_next_actions(self, to_agent: str, task_id: str) -> str:
        """Generate next actions for target agent"""
        action_templates = {
            'gemini-cli': [
                "- Review task requirements and strategy",
                "- Validate technical approach",
                "- Coordinate with other agents as needed"
            ],
            'copilot-raptor': [
                "- Execute implementation tasks",
                "- Monitor progress and report status",
                "- Handle technical troubleshooting"
            ],
            'cline-cli-kat': [
                "- Perform code reviews and quality checks",
                "- Ensure compliance with standards",
                "- Document implementation details"
            ],
            'grok-mc': [
                "- Review strategic alignment",
                "- Coordinate cross-agent activities",
                "- Escalate critical issues"
            ]
        }
        
        actions = action_templates.get(to_agent, [
            "- Review task requirements",
            "- Determine appropriate next steps",
            "- Coordinate with team as needed"
        ])
        
        return '\n'.join([f"{i+1}. {action}" for i, action in enumerate(actions)])
    
    def _archive_handoff(self, handoff_record: Dict[str, Any]):
        """Archive handoff record"""
        archive_dir = self.state_dir.parent / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        filename = f"{handoff_record['handoff_id']}.json"
        archive_path = archive_dir / filename
        
        with open(archive_path, 'w') as f:
            json.dump(handoff_record, f, indent=2)
        
        logger.info(f"Handoff archived to {archive_path}")

def main():
    orchestrator = HandoffOrchestrator()
    
    # Example handoff
    try:
        handoff = orchestrator.create_handoff(
            from_agent="cline-cli-kat",
            to_agent="gemini-cli", 
            task_id="VIKUNJA-UTILIZATION-20260213",
            description="Complete Vikunja utilization implementation",
            context={
                "progress": "Redis resilience implemented",
                "next_steps": "Memory bank migration pending",
                "dependencies": ["Redis connection", "Vikunja API access"]
            }
        )
        print(f"Handoff created: {handoff['handoff_id']}")
    except ValueError as e:
        logger.error(f"Handoff creation failed: {e}")

if __name__ == '__main__':
    main()
EOF
chmod +x scripts/handoff-orchestrator.py
```

### Phase 3: Health Integration (Week 3)

#### Step 3.1: Health Monitoring Integration
```bash
# Create health monitoring integration
cat > scripts/agent-health-monitor.py << 'EOF'
#!/usr/bin/env python3
"""
Agent Health Monitor
Monitors agent health and integrates with communication workflows
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentHealthMonitor:
    def __init__(self, state_dir: str = "internal_docs/communication_hub/state"):
        self.state_dir = Path(state_dir)
        self.heartbeat_timeout = 600  # 10 minutes
        self.critical_timeout = 1800  # 30 minutes
    
    def check_all_agents(self) -> Dict[str, Any]:
        """Check health of all agents"""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'agents': {},
            'summary': {
                'total': 0,
                'healthy': 0,
                'warning': 0,
                'critical': 0,
                'offline': 0
            }
        }
        
        for state_file in self.state_dir.glob("*.json"):
            agent_name = state_file.stem
            health_report['agents'][agent_name] = self._check_agent_health(agent_name)
        
        # Calculate summary
        for agent_data in health_report['agents'].values():
            health_report['summary']['total'] += 1
            health_report['summary'][agent_data['status']] += 1
        
        return health_report
    
    def _check_agent_health(self, agent_name: str) -> Dict[str, Any]:
        """Check health of a specific agent"""
        state_file = self.state_dir / f"{agent_name}.json"
        
        if not state_file.exists():
            return {
                'status': 'offline',
                'last_heartbeat': None,
                'age_seconds': None,
                'issues': ['No state file found']
            }
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except json.JSONDecodeError:
            return {
                'status': 'critical',
                'last_heartbeat': None,
                'age_seconds': None,
                'issues': ['Corrupted state file']
            }
        
        last_heartbeat_str = state.get('timestamp')
        if not last_heartbeat_str:
            return {
                'status': 'critical',
                'last_heartbeat': None,
                'age_seconds': None,
                'issues': ['No heartbeat timestamp']
            }
        
        try:
            last_heartbeat = datetime.fromisoformat(last_heartbeat_str.replace('Z', '+00:00'))
        except ValueError:
            return {
                'status': 'critical',
                'last_heartbeat': None,
                'age_seconds': None,
                'issues': ['Invalid timestamp format']
            }
        
        age_seconds = (datetime.now() - last_heartbeat.replace(tzinfo=None)).total_seconds()
        
        # Determine health status
        if age_seconds > self.critical_timeout:
            status = 'critical'
            issues = [f'Heartbeat too old: {age_seconds:.0f}s']
        elif age_seconds > self.heartbeat_timeout:
            status = 'warning'
            issues = [f'Heartbeat stale: {age_seconds:.0f}s']
        else:
            status = 'healthy'
            issues = []
        
        # Check for additional issues
        current_task = state.get('current_task', {})
        if current_task.get('task_id') and state.get('status') != 'processing':
            issues.append('Task assigned but not processing')
        
        return {
            'status': status,
            'last_heartbeat': last_heartbeat_str,
            'age_seconds': age_seconds,
            'issues': issues,
            'current_task': current_task.get('task_id'),
            'agent_status': state.get('status')
        }
    
    def generate_health_alert(self, health_report: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate health alert if needed"""
        critical_agents = [
            agent for agent, data in health_report['agents'].items()
            if data['status'] == 'critical'
        ]
        
        offline_agents = [
            agent for agent, data in health_report['agents'].items()
            if data['status'] == 'offline'
        ]
        
        if critical_agents or offline_agents:
            return {
                'alert_type': 'agent_health',
                'severity': 'critical' if critical_agents else 'warning',
                'timestamp': health_report['timestamp'],
                'critical_agents': critical_agents,
                'offline_agents': offline_agents,
                'message': f"Agent health issues detected: {len(critical_agents)} critical, {len(offline_agents)} offline"
            }
        
        return None
    
    def send_health_alert(self, alert: Dict[str, Any]):
        """Send health alert via communication system"""
        # Create alert message
        alert_message = f"""---
FROM: agent-health-monitor
TO: gemini-cli
TIMESTAMP: {alert['timestamp']}Z
TASK_ID: HEALTH_ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}
STATUS: ALERT
---

### Agent Health Alert

**Severity**: {alert['severity']}  
**Timestamp**: {alert['timestamp']}  

#### Critical Agents
{chr(10).join([f"- {agent}" for agent in alert['critical_agents']]) if alert['critical_agents'] else "None"}

#### Offline Agents  
{chr(10).join([f"- {agent}" for agent in alert['offline_agents']]) if alert['offline_agents'] else "None"}

#### Message
{alert['message']}

---
"""
        
        # Write to inbox
        inbox_file = self.state_dir.parent / "inbox_gemini-cli.md"
        with open(inbox_file, 'a') as f:
            f.write(f"\n{alert_message}\n")
        
        logger.warning(f"Health alert sent: {alert['message']}")

def main():
    monitor = AgentHealthMonitor()
    
    while True:
        health_report = monitor.check_all_agents()
        
        # Log summary
        summary = health_report['summary']
        logger.info(f"Health check: {summary['healthy']} healthy, {summary['warning']} warning, {summary['critical']} critical, {summary['offline']} offline")
        
        # Check for alerts
        alert = monitor.generate_health_alert(health_report)
        if alert:
            monitor.send_health_alert(alert)
        
        # Wait before next check
        time.sleep(300)  # Check every 5 minutes

if __name__ == '__main__':
    main()
EOF
chmod +x scripts/agent-health-monitor.py
```

## Test Plan

### Unit Tests
```bash
# Create test suite for CLI communications
cat > tests/test_cli_comms.py << 'EOF'
#!/usr/bin/env python3
"""
Test suite for CLI communications system
"""

import pytest
import tempfile
import json
from pathlib import Path
from scripts.parse_agent_messages import AgentBusMessageParser
from scripts.handoff_orchestrator import HandoffOrchestrator
from scripts.agent_health_monitor import AgentHealthMonitor

class TestAgentBusMessageParser:
    def setup_method(self):
        self.parser = AgentBusMessageParser()
    
    def test_parse_valid_message(self):
        """Test parsing of valid message"""
        message_content = """---
FROM: cline-cli-kat
TO: gemini-cli
TIMESTAMP: 2026-02-13T23:00:00Z
TASK_ID: TEST_TASK_001
STATUS: HANDOFF
---

### Test Message

This is a test message body.
---
"""
        
        messages = self.parser._extract_message_blocks(message_content)
        assert len(messages) == 1
        
        parsed = self.parser._parse_message_block(messages[0])
        assert parsed['FROM'] == 'cline-cli-kat'
        assert parsed['TO'] == 'gemini-cli'
        assert parsed['STATUS'] == 'HANDOFF'
    
    def test_invalid_message_validation(self):
        """Test validation of invalid message"""
        message_content = """---
FROM: cline-cli-kat
TO: gemini-cli
TIMESTAMP: 2026-02-13T23:00:00Z
TASK_ID: TEST_TASK_001
STATUS: INVALID_STATUS
---
"""
        
        messages = self.parser._extract_message_blocks(message_content)
        parsed = self.parser._parse_message_block(messages[0])
        assert parsed is None  # Should be rejected

class TestHandoffOrchestrator:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = HandoffOrchestrator(state_dir=self.temp_dir)
    
    def test_create_handoff(self):
        """Test handoff creation"""
        handoff = self.orchestrator.create_handoff(
            from_agent="cline-cli-kat",
            to_agent="gemini-cli",
            task_id="TEST_TASK_001",
            description="Test handoff"
        )
        
        assert handoff['from_agent'] == 'cline-cli-kat'
        assert handoff['to_agent'] == 'gemini-cli'
        assert handoff['task_id'] == 'TEST_TASK_001'
    
    def test_invalid_agent_validation(self):
        """Test validation of invalid agents"""
        with pytest.raises(ValueError, match="Invalid FROM agent"):
            self.orchestrator.create_handoff(
                from_agent="invalid-agent",
                to_agent="gemini-cli",
                task_id="TEST_TASK_001",
                description="Test"
            )

class TestAgentHealthMonitor:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = AgentHealthMonitor(state_dir=self.temp_dir)
    
    def test_healthy_agent(self):
        """Test healthy agent detection"""
        # Create healthy agent state
        state_file = Path(self.temp_dir) / "test-agent.json"
        state = {
            "agent_id": "test-agent",
            "timestamp": datetime.now().isoformat(),
            "status": "processing",
            "current_task": {"task_id": "TEST_TASK", "source": "agent-bus", "description": "Test"}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        health = self.monitor._check_agent_health("test-agent")
        assert health['status'] == 'healthy'
    
    def test_offline_agent(self):
        """Test offline agent detection"""
        health = self.monitor._check_agent_health("nonexistent-agent")
        assert health['status'] == 'offline'

if __name__ == '__main__':
    pytest.main([__file__])
EOF
```

### Integration Tests
```bash
# Create integration test script
cat > scripts/test-cli-comms-integration.py << 'EOF'
#!/usr/bin/env python3
"""
Integration test for CLI communications system
"""

import os
import time
import json
from pathlib import Path
from scripts.agent_bus_watcher import main as watcher_main
from scripts.handoff_orchestrator import HandoffOrchestrator
from scripts.agent_health_monitor import AgentHealthMonitor

def test_full_communication_flow():
    """Test complete communication flow"""
    print("Testing full CLI communication flow...")
    
    # Setup test environment
    test_dir = Path("test_cli_comms")
    test_dir.mkdir(exist_ok=True)
    
    # Test 1: Create handoff
    print("1. Testing handoff creation...")
    orchestrator = HandoffOrchestrator(state_dir=str(test_dir / "state"))
    
    handoff = orchestrator.create_handoff(
        from_agent="cline-cli-kat",
        to_agent="gemini-cli",
        task_id="INTEGRATION_TEST_001",
        description="Integration test handoff"
    )
    
    assert handoff['from_agent'] == 'cline-cli-kat'
    print("✅ Handoff created successfully")
    
    # Test 2: Check agent state
    print("2. Testing agent state updates...")
    state_file = test_dir / "state" / "gemini-cli.json"
    assert state_file.exists()
    
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    assert state['status'] == 'processing'
    assert state['current_task']['task_id'] == 'INTEGRATION_TEST_001'
    print("✅ Agent state updated correctly")
    
    # Test 3: Check inbox message
    print("3. Testing inbox message creation...")
    inbox_file = test_dir / "state" / ".." / "inbox_gemini-cli.md"
    assert inbox_file.exists()
    
    with open(inbox_file, 'r') as f:
        content = f.read()
    
    assert "HANDOFF" in content
    assert "INTEGRATION_TEST_001" in content
    print("✅ Inbox message created successfully")
    
    # Test 4: Health monitoring
    print("4. Testing health monitoring...")
    monitor = AgentHealthMonitor(state_dir=str(test_dir / "state"))
    health_report = monitor.check_all_agents()
    
    assert 'gemini-cli' in health_report['agents']
    assert health_report['agents']['gemini-cli']['status'] in ['healthy', 'warning']
    print("✅ Health monitoring working")
    
    print("🎉 All integration tests passed!")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)

if __name__ == '__main__':
    test_full_communication_flow()
EOF
chmod +x scripts/test-cli-comms-integration.py
```

## Risks & Mitigations

### Risk 1: Message Loss During High Volume
**Impact**: Critical communications may be missed during peak activity
**Mitigation**:
- Implement message queuing with persistence
- Use atomic file operations for message writing
- Add retry logic with exponential backoff
- Monitor message queue depth and alert on high volume

### Risk 2: Agent State Inconsistency
**Impact**: Confusion about which agent is responsible for which task
**Mitigation**:
- Use atomic state updates with file locking
- Implement state validation and reconciliation
- Add state change audit logging
- Create state recovery procedures

### Risk 3: Communication Deadlocks
**Impact**: Agents waiting indefinitely for responses
**Mitigation**:
- Implement timeout mechanisms for handoffs
- Add deadlock detection and resolution
- Use circuit breaker patterns for communication failures
- Create manual override procedures

### Risk 4: Security Vulnerabilities
**Impact**: Unauthorized access to communication channels
**Mitigation**:
- Implement message authentication and integrity checks
- Use secure file permissions for communication files
- Add access control for agent state files
- Monitor for suspicious communication patterns

## Ma'at Alignment Validation

### Principle #7: Truth (Communication Integrity)
**Alignment**: This charter ensures truthful and reliable communication by:
- Implementing comprehensive message validation
- Maintaining complete audit trails
- Ensuring message delivery reliability
- Providing transparent communication flows

**Validation Criteria**:
- [ ] All messages are validated before processing
- [ ] Complete audit trail maintained for all communications
- [ ] Message delivery success rate >99.9%
- [ ] Communication flows are transparent and traceable

### Principle #18: Balance (System Equilibrium)
**Alignment**: This charter ensures balanced communication by:
- Distributing communication load across agents
- Implementing graceful degradation during failures
- Maintaining equilibrium between automation and manual oversight
- Ensuring no single point of communication failure

**Validation Criteria**:
- [ ] Communication load is distributed appropriately
- [ ] System maintains functionality during partial failures
- [ ] Manual override capabilities are available
- [ ] No single point of communication failure exists

## Implementation Timeline

### Week 1: Watcher Script Implementation
- [ ] Create basic watcher script with file monitoring
- [ ] Implement message parser with validation
- [ ] Add message archiving functionality
- [ ] Test basic message processing

### Week 2: Autonomous Handoff System
- [ ] Implement handoff orchestrator
- [ ] Create context preservation mechanisms
- [ ] Add handoff validation and error handling
- [ ] Test handoff workflows

### Week 3: Health Integration
- [ ] Implement agent health monitoring
- [ ] Create health alert system
- [ ] Integrate health checks with communication workflows
- [ ] Add health-based communication routing

### Week 4: Validation & Optimization
- [ ] Comprehensive testing and validation
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Documentation and training

## Success Metrics

### Technical Metrics
- [ ] Message delivery reliability: 99.9%
- [ ] Response time for critical messages: <5 minutes
- [ ] Agent health monitoring coverage: 100%
- [ ] Handoff success rate: 100%

### Business Metrics
- [ ] Zero message loss during agent transitions
- [ ] Complete audit trail for all communications
- [ ] 100% agent state consistency
- [ ] Automated handoff success rate: >95%

### Operational Metrics
- [ ] System uptime: 99.9%
- [ ] Mean time to detect communication issues: <2 minutes
- [ ] Mean time to resolve communication failures: <10 minutes
- [ ] Support tickets related to communication: 0

## Next Steps

1. **Immediate**: Begin watcher script implementation
2. **Week 1**: Complete basic message monitoring and parsing
3. **Week 2**: Implement autonomous handoff system
4. **Week 3**: Add health monitoring integration
5. **Week 4**: Final validation and optimization

**Status**: Ready for implementation
**Priority**: P1 - HIGH
**Dependencies**: Agent state files, communication hub structure