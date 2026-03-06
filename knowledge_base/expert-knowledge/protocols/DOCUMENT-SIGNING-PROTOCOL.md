---
tool: cline
model: claude-sonnet-4-6
account: arcana-novai
git_branch: main
session_id: sprint5-2026-02-18
version: v1.0.0
created: 2026-02-18
tags: [protocol, document-signing, frontmatter, provenance, institutional-memory]
---

# Document Signing Protocol
**v1.0.0 | 2026-02-18 | XNAi Foundation**

## Purpose

All documents, code files, and artifacts created by AI agents or human contributors in
the XNAi project MUST include standardized YAML frontmatter for provenance tracking,
institutional memory, and RAG ingestion quality.

---

## 1. Standard Frontmatter Fields

### Markdown Documents (.md)
```yaml
---
tool: cline|opencode|gemini-cli|copilot|human
model: claude-opus-4-5|gemini-2.0-flash|gpt-4o|...
account: arcana-novai|<github-username>
git_branch: main|feature/<name>
git_commit: <short-sha>        # optional, fill after commit
session_id: sprint5-2026-02-18|<uuid>
version: v1.0.0
created: 2026-02-18
updated: 2026-02-18            # update on each revision
tags: [tag1, tag2, tag3]
---
```

### Python Files (.py)
```python
# ---
# tool: cline
# model: claude-sonnet-4-6
# account: arcana-novai
# git_branch: main
# session_id: sprint5-2026-02-18
# version: v1.0.0
# created: 2026-02-18
# ---
```

### Shell Scripts (.sh)
```bash
#!/bin/bash
# ---
# tool: cline
# model: claude-sonnet-4-6
# account: arcana-novai
# git_branch: main
# session_id: sprint5-2026-02-18
# version: v1.0.0
# created: 2026-02-18
# ---
```

### YAML Config Files (.yaml/.yml)
```yaml
# ---
# tool: cline
# model: claude-sonnet-4-6
# account: arcana-novai
# git_branch: main
# session_id: sprint5-2026-02-18
# version: v1.0.0
# created: 2026-02-18
# ---
```

---

## 2. Field Definitions

| Field | Required | Description |
|-------|----------|-------------|
| `tool` | ✅ | CLI/tool that created the file |
| `model` | ✅ | AI model used (e.g., claude-opus-4-5) |
| `account` | ✅ | GitHub/account identifier |
| `git_branch` | ✅ | Branch at time of creation |
| `git_commit` | ⚪ | Short SHA — fill after `git commit` |
| `session_id` | ✅ | Sprint/session identifier |
| `version` | ✅ | Semantic version (v1.0.0) |
| `created` | ✅ | ISO date of creation (YYYY-MM-DD) |
| `updated` | ⚪ | ISO date of last modification |
| `tags` | ✅ | 2-5 relevant tags for RAG retrieval |

---

## 3. Tool Values Reference

| Tool | `tool` field value |
|------|-------------------|
| Cline (VSCodium) | `cline` |
| OpenCode CLI | `opencode` |
| Gemini CLI | `gemini-cli` |
| GitHub Copilot CLI | `copilot` |
| Antigravity CLI | `antigravity` |
| Human author | `human` |
| Automated script | `script` |

---

## 4. Model Values Reference

| Model | `model` field value |
|-------|---------------------|
| Claude Opus 4.5 | `claude-opus-4-5` |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` |
| Claude Haiku 3.5 | `claude-haiku-3-5` |
| Gemini 2.0 Flash | `gemini-2.0-flash` |
| Gemini 2.5 Pro | `gemini-2.5-pro` |
| GPT-4o | `gpt-4o` |
| Kimi K2.5 | `kimi-k2.5` |
| GLM-5 | `glm-5` |
| Local GGUF | `local-gguf/<model-name>` |

---

## 5. Session ID Convention

```
sprint<N>-YYYY-MM-DD        # Sprint sessions
research-YYYY-MM-DD         # Research sessions
hotfix-YYYY-MM-DD-<topic>   # Hotfix sessions
<uuid>                      # Auto-generated (Copilot/OpenCode)
```

---

## 6. Signing Scripts

### Inject Frontmatter into Existing .md File
Use `scripts/sign-document.sh`:
```bash
# Sign an existing document (prepends frontmatter if not present)
./scripts/sign-document.sh path/to/document.md \
  --tool cline \
  --model claude-opus-4-5 \
  --branch main \
  --session sprint5-2026-02-18 \
  --tags "research,protocol"
```

### Batch Sign All Unsigned Documents
```bash
# Find all .md files missing frontmatter and sign them
./scripts/sign-document.sh --batch expert-knowledge/ \
  --tool human \
  --model unknown \
  --branch main
```

### Auto-Sign on Git Commit (pre-commit hook)
```bash
# .git/hooks/pre-commit
#!/bin/bash
for file in $(git diff --cached --name-only --diff-filter=A | grep '\.md$'); do
  if ! head -3 "$file" | grep -q "^---"; then
    echo "WARNING: $file is missing frontmatter. Run sign-document.sh"
    exit 1
  fi
done
```

---

## 7. Compliance Rules

### RULES.md Enforcement
All AI agents operating in this repo (Cline, OpenCode, Gemini, Copilot) MUST:

1. **Include frontmatter** in ALL new .md files created
2. **Include comment header** in ALL new .py and .sh files created
3. **Use the correct tool/model values** from the reference tables above
4. **Set session_id** using the current sprint/session convention
5. **NOT modify** existing frontmatter unless making a revision (update `updated` field + bump version)

### Enforcement in RULES.md
```
RULE 15: All new .md files MUST include YAML frontmatter per DOCUMENT-SIGNING-PROTOCOL.md
RULE 16: All new .py and .sh files MUST include signed comment header
RULE 17: Frontmatter must be the FIRST content in the file (before any other text)
```

---

## 8. RAG Ingestion Integration

The `conversation_ingestion.py` and `model_intelligence_ingestion.py` scripts parse
frontmatter to enrich Qdrant payloads:

```python
import yaml
import re

def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if match:
        return yaml.safe_load(match.group(1))
    return {}

# Payload enrichment
frontmatter = extract_frontmatter(doc_content)
qdrant_payload = {
    "content": body_text,
    "tool": frontmatter.get("tool", "unknown"),
    "model": frontmatter.get("model", "unknown"),
    "session_id": frontmatter.get("session_id", ""),
    "version": frontmatter.get("version", "v1.0.0"),
    "tags": frontmatter.get("tags", []),
    "created": frontmatter.get("created", ""),
}
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2026-02-18 | Initial protocol definition |
