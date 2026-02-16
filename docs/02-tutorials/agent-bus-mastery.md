# Tutorial: Agent Bus Mastery
**Level**: Advanced | **Audience**: AI-Steered Developers

The **Agent Bus** is the nervous system of the Xoe-NovAi Foundation. It allows multiple AI assistants to collaborate autonomously, passing tasks and strategies between each other with minimal human intervention.

---

## 🛠️ How It Works

The Agent Bus uses a simple filesystem-based "Mailbox" system located at `internal_docs/communication_hub/`.

### 1. The Mailboxes
- `inbox_gemini.md`: Messages for Gemini CLI.
- `inbox_copilot.md`: Messages for Copilot CLI.
- `inbox_cline.md`: Messages for Cline.

### 2. Sending a Message
To send a message, append a structured block to the recipient's inbox.

**Example: Sending a refactor request to Cline**
```bash
cat <<EOF >> internal_docs/communication_hub/inbox_cline.md
---
FROM: Gemini CLI
STATUS: TASK
TASK_ID: REF-001
---
### Refactor API Exceptions
Please refactor 'app/api/exceptions.py' to use the new Unified Exception Hierarchy.
---
EOF
```

---

## 🤖 Automating the Loop

You can set up "Watchers" that trigger agents when new messages arrive.

### Simple Bash Watcher for Gemini CLI
```bash
# A simple loop to check for new messages
while true; do
  if [ -s internal_docs/communication_hub/inbox_gemini.md ]; then
    echo "New message detected for Gemini!"
    # Trigger Gemini CLI logic here
  fi
  sleep 60
done
```

---

## 🎯 Best Practices

1. **Be Specific**: Use `TASK_ID` to link messages to Vikunja tasks.
2. **Contextual Links**: Instead of pasting large code blocks, provide the file path.
3. **Audit Trails**: Once a message is processed, move it to the `archive/` directory.

---

## 🛑 Security Warning
The Agent Bus operates with the same permissions as the user. Ensure your agents are configured with appropriate guardrails (e.g., restricted `sudo` access for runners).
