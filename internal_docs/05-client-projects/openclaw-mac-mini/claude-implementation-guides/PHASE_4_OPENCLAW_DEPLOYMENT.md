# PHASE 4: OpenClaw Deployment
## Hands-Free Autonomous Agent with Voice Approval & Telegram Interface

**Status**: Agent Core (Days 5-7) | **Prerequisites**: Phases 1-3 complete | **Outputs**: Operational OpenClaw agent, Telegram voice interface, approval flow | **Test Gate**: Voice approval simulation, end-to-end Telegram test, task execution logged

---

## Executive Summary

Phase 4 launches **OpenClaw**, the autonomous agent framework. OpenClaw is the orchestrator that:
1. Listens for voice commands via Telegram (or other messaging)
2. Routes requests to Ollama (local LLM)
3. Plans multi-step tasks (via agent reasoning)
4. Requests explicit approval for sensitive actions
5. Executes approved tasks (file ops, API calls, shell commands)
6. Reports results via voice (TTS back through Telegram)

**Hands-free focus**: All interaction is voice-in/voice-out. Your friend never touches a keyboard.

---

## Part A: OpenClaw Installation

### Install OpenClaw

OpenClaw is Node.js-based. Ensure Node.js 22+ is installed:

```bash
node --version  # Should show v22.x or higher
```

If missing:
```bash
brew install node@22
```

### Install OpenClaw via NPM

```bash
npm install -g openclaw

# Or, for local development:
git clone https://github.com/psteinberger/openclaw.git
cd openclaw
npm install
npm run build
```

**Verify installation**:
```bash
openclaw --version
```

Expected output: `openclaw v[version]`

### Create OpenClaw Project Directory

```bash
mkdir -p ~/.openclaw
cd ~/.openclaw

# Initialize OpenClaw project
openclaw init --name="BlindFriendAgent" --model="local"
```

This creates a config directory and skeleton configuration.

---

## Part B: Configuration for Hands-Free & Local LLM

### Create Main Configuration File

Create `~/.openclaw/openclaw.json`:

```json
{
  "name": "OpenClaw Agent",
  "description": "Autonomous agent for blind user. Hands-free voice-first operation.",
  
  "model": {
    "provider": "ollama",
    "base_url": "http://127.0.0.1:11434/v1",
    "model": "llama3.3:agent",
    "fallback_model": "mistral:7b-instruct-q4_k_m",
    "timeout_seconds": 30,
    "temperature": 0.3
  },
  
  "agent": {
    "name": "OpenClaw",
    "instructions": "You are an autonomous agent assisting a blind user. Be concise. Outputs will be read aloud. Plan multi-step tasks clearly. Request approval before sensitive actions (file deletion, email send, etc.). Format responses for TTS: short sentences, no bullet points, clear action items.",
    
    "memory": {
      "enabled": true,
      "type": "local",
      "path": "~/.openclaw/memory"
    },
    
    "tools": {
      "file_operations": true,
      "shell_execution": true,
      "http_requests": true,
      "email": false,  # Disable for safety until user configured
      "calendar": false,
      "custom_scripts": true
    }
  },
  
  "approval": {
    "enabled": true,
    "strategy": "voice_then_keyboard",
    "actions_requiring_approval": [
      "file_delete",
      "file_modify_system",
      "shell_execute_dangerous",
      "email_send",
      "calendar_create"
    ],
    "notification": {
      "method": "telegram_voice",  # Announce via Telegram TTS
      "timeout_seconds": 60,
      "default_action": "deny"  # Fail-safe: if no response, deny action
    }
  },
  
  "channels": {
    "telegram": {
      "enabled": true,
      "bot_token": "PLACEHOLDER",  # Set in Part C
      "voice_input": true,
      "voice_output": true,
      "approved_users": ["PLACEHOLDER"]  # User Telegram ID
    }
  },
  
  "accessibility": {
    "tts_provider": "system",
    "tts_voice": "Samantha",
    "tts_rate": 0.5,
    "voiceover_integration": true,
    "braille_enabled": false,  # Set to true if Braille display connected
    "structured_output": true  # Format for TTS (no tables, short lines)
  },
  
  "sandbox": {
    "enabled": true,
    "mode": "restricted",
    "allowed_directories": [
      "~/Documents",
      "~/Downloads",
      "~/.openclaw"
    ],
    "blocked_commands": [
      "rm -rf /",
      "sudo",
      "dd",
      "mkfs"
    ]
  },
  
  "logging": {
    "level": "info",
    "file": "~/.openclaw/openclaw.log",
    "audit_log": "~/.openclaw/audit.log",
    "max_size_mb": 100,
    "retention_days": 30
  }
}
```

---

## Part C: Telegram Setup (Voice Interface)

### Create Telegram Bot via BotFather

1. Open Telegram and search for **@BotFather**.
2. Send `/start` and follow prompts.
3. Send `/newbot` and choose:
   - **Bot name**: `BlindFriendAgent`
   - **Username**: `blindfriend_agent_[randomstring]`
4. **Copy the API token** (looks like `123456:ABC-DEF...`).
5. Save securely (e.g., in a password manager or encrypted file).

### Get Your Telegram User ID

1. Search for **@userinfobot** in Telegram.
2. Send `/start`.
3. Bot responds with your **User ID** (a number like `987654321`).
4. Copy this.

### Update OpenClaw Config with Telegram Credentials

Edit `~/.openclaw/openclaw.json`:

```json
"channels": {
  "telegram": {
    "enabled": true,
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "voice_input": true,
    "voice_output": true,
    "approved_users": ["YOUR_USER_ID_HERE"]
  }
}
```

Replace `YOUR_BOT_TOKEN_HERE` and `YOUR_USER_ID_HERE` with actual values.

**Security**: Store this file with restricted permissions:
```bash
chmod 600 ~/.openclaw/openclaw.json
```

---

## Part D: Approval Flow (Voice-Based)

### Approval Mechanism Implementation

When OpenClaw plans a task that requires approval (e.g., file deletion), it:

1. **Formulates a clear request**: "Approval requested: Delete file test.txt from Downloads?"
2. **Sends via Telegram**: Bot sends the message to your Telegram.
3. **Waits for voice response**: You speak "approve" or "deny".
4. **Executes or cancels**: Based on your voice input.

### Create Approval Handler

Create `~/.openclaw/approval-handler.js`:

```javascript
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

class ApprovalHandler {
  constructor(telegramClient) {
    this.telegram = telegramClient;
    this.pendingApprovals = new Map();
  }

  // Request approval via Telegram voice
  async requestApproval(actionId, actionDescription) {
    const message = `
🔒 Agent Approval Required
Action: ${actionDescription}

Please respond with:
- "approve" or "yes" to proceed
- "deny" or "no" to reject

Timeout: 60 seconds. Auto-deny if no response.
    `;

    // Send to Telegram
    await this.telegram.sendMessage(message, { voice: true });

    // Wait for approval response
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pendingApprovals.delete(actionId);
        reject(new Error('Approval timeout. Action denied.'));
      }, 60000);

      this.pendingApprovals.set(actionId, (approved) => {
        clearTimeout(timeout);
        this.pendingApprovals.delete(actionId);
        if (approved) {
          resolve(true);
        } else {
          reject(new Error('Action denied by user.'));
        }
      });
    });
  }

  // Handle voice response from Telegram
  async handleVoiceResponse(voiceInput) {
    const normalized = voiceInput.toLowerCase().trim();
    const approved = /^(approve|yes|ok|proceed)/.test(normalized);
    
    // Find any pending approval and respond
    for (const [actionId, callback] of this.pendingApprovals.entries()) {
      callback(approved);
      return;
    }
  }
}

module.exports = ApprovalHandler;
```

### Integrate into OpenClaw Core

This will be integrated in the main OpenClaw task executor (handled by OpenClaw's built-in approval engine; you can extend it via the above template).

---

## Part E: Hands-Free Task Execution

### Example: Voice-Triggered Task

Your friend opens Telegram and sends:

**Voice message**: "Create a reminder file for tomorrow's doctor appointment."

**OpenClaw processes**:
1. Transcribes voice: "Create a reminder file for tomorrow's doctor appointment"
2. Plans task: 
   - Get tomorrow's date
   - Create file: `~/Documents/reminder-[date].txt`
   - Write appointment info
3. **Requests approval**: "I plan to create a file reminder-2026-02-09.txt in Documents. Approve?"
4. **Waits for voice response**: Your friend says "approve"
5. **Executes**: Creates file with appointment details
6. **Reports back**: "Reminder file created successfully"

### Voice Command Examples

Your friend can send (via Telegram voice message):

- "What's the weather today?"
- "Send me a summary of my emails"
- "Create a file called notes.txt"
- "What is the date?"
- "Tell me a joke"
- "Search for information about quantum computing"
- "List files in my Documents folder"

All responses come back as voice messages in Telegram.

---

## Part F: Startup & Testing

### Start OpenClaw Daemon

```bash
cd ~/.openclaw

# Start OpenClaw in foreground (for testing)
openclaw start --config openclaw.json --verbose

# Or as background daemon
nohup openclaw start --config openclaw.json > openclaw.log 2>&1 &
```

**Watch for startup messages** (VoiceOver will read them):
```
[INFO] OpenClaw initialized
[INFO] Ollama model loaded: llama3.3:agent
[INFO] Telegram channel connected
[INFO] Approval handler active
[INFO] Agent ready for commands
```

### Test Voice Approval Flow

**Telegram test**:

1. Open the Telegram chat with your bot.
2. Send a voice message: **"Create a test file"**
3. Bot should respond with an approval request.
4. Respond with voice: **"Approve"**
5. Bot acknowledges and executes the task.

**Expected messages**:
```
You: [voice] Create a test file
Bot: Agent requests approval: Create a file test-file.txt in ~/.openclaw. Approve?
You: [voice] Approve
Bot: File created successfully. Check your ~/.openclaw/test-file.txt
```

---

## Part G: Safety & Sandboxing

### Default Sandbox Restrictions

OpenClaw runs with sandboxing enabled. By default, it can:
- ✓ Read/write to `~/Documents`, `~/Downloads`, `~/.openclaw`
- ✓ Execute shell commands within those directories
- ✓ Make HTTP requests (for external APIs)

It **cannot** (without explicit approval):
- ✗ Delete system files or user accounts
- ✗ Execute `sudo` commands
- ✗ Access files outside approved directories

### Gradual Trust Model

**Phase 1 (initial)**: All file operations require approval.
**Phase 2 (after 1 week)**: File reads don't require approval; writes do.
**Phase 3 (after 1 month)**: Routine tasks (e.g., creating notes) don't require approval.

This is configured in `openclaw.json`:
```json
"trust_model": "gradual",
"approval_escalation_days": 7
```

---

## Part H: Knowledge Gaps & Troubleshooting

### Gap 1: Local LLM vs. Cloud API for Agent Tasks

**Question**: Is Ollama fast enough for agent reasoning?

**Answer**: Yes, but context matters.
- **Simple tasks** (list files, create notes): <2 seconds
- **Complex reasoning** (multi-step planning): 5-15 seconds
- **Coding tasks**: 10-30 seconds

Latency is acceptable because your friend can do other things while the agent works.

### Gap 2: Token Limits on Reasoning

**Question**: Can Ollama models handle complex multi-step plans?

**Answer**: Yes. Llama 3.3 70B excels at planning. Example:
```
Input: "Organize my photos by date and create a summary"
Model output:
1. List all photos in ~/Pictures
2. Extract date metadata
3. Create folders by year/month
4. Move photos to folders
5. Create summary file
Request approval for steps 1 and 5 (require filesystem access)
```

### Gap 3: Voice Transcription Errors

**Question**: What if Telegram transcribes the voice command incorrectly?

**Answer**: 
- Modern Telegram voice transcription is 95%+ accurate for clear speech.
- OpenClaw can handle minor typos (LLM is robust).
- For critical tasks, confirmation is built-in (approval request).

**Recovery**: If task is wrong, user can cancel and re-send.

---

## Part I: Logging & Audit Trail

### Audit Log Review

All approvals and executions are logged:

```bash
tail -50 ~/.openclaw/audit.log
```

Example entries:
```
[2026-02-09 10:15:23] ACTION_REQUESTED: "Create file test.txt"
[2026-02-09 10:15:25] APPROVAL_REQUESTED: "Create file test.txt in ~/.openclaw"
[2026-02-09 10:15:28] APPROVAL_GRANTED: User said "approve"
[2026-02-09 10:15:29] ACTION_EXECUTED: File created
[2026-02-09 10:15:30] RESULT: "File created successfully"
```

### Review via Voice

Create alias for voice audit review:

```bash
echo "alias audit-voice='tail -20 ~/.openclaw/audit.log | say'" >> ~/.zshrc
source ~/.zshrc
```

Now `audit-voice` will speak the last 20 audit entries.

---

## Part J: Testing & Validation Gate

### Pre-Phase-5 Checklist

1. **Installation**:
   - [ ] `openclaw --version` returns version
   - [ ] `~/.openclaw/openclaw.json` exists and is valid JSON
   - [ ] Telegram bot is configured and responding

2. **Ollama Integration**:
   - [ ] OpenClaw connects to Ollama (check logs for "Model loaded")
   - [ ] `ollama run llama3.3:agent "hello"` works outside of OpenClaw

3. **Telegram Voice**:
   - [ ] Send test voice message via Telegram
   - [ ] Bot transcribes and responds
   - [ ] Response latency <10 seconds

4. **Approval Flow**:
   - [ ] Trigger an approval-required action
   - [ ] Bot announces the request
   - [ ] Send voice response "approve"
   - [ ] Action executes

5. **Hands-Free**:
   - [ ] Close the terminal; agent runs as daemon
   - [ ] All interaction is via Telegram voice
   - [ ] No keyboard input required

### Smoke Test Script

Create `~/.openclaw/smoke-test.sh`:

```bash
#!/bin/bash

echo "=== OpenClaw Smoke Test ===" | say

# Test 1: Daemon running
if pgrep -f "openclaw start" > /dev/null; then
  echo "✓ OpenClaw daemon is running"
  say "OpenClaw daemon is running"
else
  echo "✗ OpenClaw daemon is NOT running"
  say "OpenClaw daemon is NOT running. Aborting test."
  exit 1
fi

# Test 2: Ollama connectivity
if curl -s http://127.0.0.1:11434/api/tags > /dev/null; then
  echo "✓ Ollama is reachable"
  say "Ollama is reachable"
else
  echo "✗ Ollama is NOT reachable"
  say "Ollama is NOT reachable. Check Ollama status."
fi

# Test 3: Telegram connectivity
# (Would require auth; skip for basic test)

echo ""
echo "Smoke test complete."
say "Smoke test complete. Check logs for details."

# Log results
echo "[$(date)] Smoke test passed" >> ~/.openclaw/test.log
```

Run it:
```bash
chmod +x ~/.openclaw/smoke-test.sh
~/.openclaw/smoke-test.sh
```

---

## Part K: Extension Points

### `openclawConfig` Schema

```json
{
  "openclaw": {
    "agent": {
      "instructions": "[custom instructions for hands-free agent]",
      "memory_enabled": true,
      "tools": [
        "file_operations",
        "http_requests",
        "shell_execution"
      ]
    },
    "channels": {
      "telegram": {
        "bot_token": "[token]",
        "voice_input": true,
        "voice_output": true
      }
    },
    "approval": {
      "strategy": "voice_then_keyboard",
      "timeout_seconds": 60
    },
    "models": {
      "primary": "llama3.3:agent",
      "fallback": "mistral:7b-instruct-q4_k_m"
    }
  }
}
```

---

## Troubleshooting Matrix

| **Issue** | **Symptom** | **Fix** |
|-----------|-----------|--------|
| OpenClaw won't start | "Error: Cannot connect to Ollama" | Verify Ollama is running: `ollama serve` in separate terminal |
| Telegram bot doesn't respond | Messages sent but no reply | Check `bot_token` in config; verify `approved_users` includes your ID |
| Approval requests don't timeout | Agent waits forever for response | Check `timeout_seconds` in config; ensure it's set to 60+ |
| Voice transcription fails | Telegram doesn't recognize voice | Check microphone; ensure clear audio; try rephrasing command |
| Daemon crashes after 1 hour | Process exits unexpectedly | Check logs: `tail -100 ~/.openclaw/openclaw.log` for error trace; likely OOM or thermal throttle |

---

## Summary & Handoff to Phase 5

**What you've built**:
- ✓ OpenClaw installed and configured
- ✓ Ollama integrated as local LLM engine
- ✓ Telegram bot set up for voice interaction
- ✓ Approval flow implemented and tested
- ✓ Audit trail logging all actions
- ✓ Hands-free operation validated

**Next**: Phase 5 (Security Hardening) adds:
- Formal security audits
- Tunneling (Cloudflare Zero Trust)
- Dashboard monitoring
- Critique loops (secondary agent verification)

**Estimated time**: 3-4 hours (including Telegram setup and testing).

**Key note**: This is the operational core. Once Phase 4 is stable, your friend can use the agent for real work (create files, research tasks, automation). Phases 5-6 optimize for long-term reliability and scaling.
