---
account: arcana.novai
version: 1.0.0
title: Vikunja Implementation & Memory Bank Migration Roadmap
date: 2026-02-06
status: 🚀 Ready for Implementation
ma_at_ideals: [7, 18, 41]
tags: [vikunja, implementation, roadmap, memory-bank-migration, project-management]
---

# Vikunja Implementation & Memory Bank Migration Roadmap

**Vision**: Transform Vikunja into the central synchronization hub for all Xoe-NovAi agents, replacing the legacy memory_bank system as the source of truth for task coordination while preserving its value as historical archive and RAG source.

---

## Phase 1: Foundation (Week 1-2)

### 1.1 Vikunja Deployment

**Objective**: Deploy Vikunja as sovereign Podman service

```yaml
# docker-compose.vikunja.yml (to be created)
services:
  vikunja:
    image: vikunja/vikunja:latest
    container_name: xnai-vikunja
    ports:
      - "3456:3456"
    environment:
      - VIKUNJA_SERVICE_PUBLICURL=http://localhost:3456
      - VIKUNJA_DATABASE_TYPE=sqlite
      - VIKUNJA_DATABASE_PATH=/app/vikunja/vikunja.db
    volumes:
      - ./vikunja-data:/app/vikunja:Z,U
    networks:
      - xnai-network
    restart: unless-stopped
```

**Tasks**:
- [ ] Create dedicated Vikunja compose file
- [ ] Configure SQLite backend (migrate to PostgreSQL later if needed)
- [ ] Set up volume mounts with proper SELinux contexts
- [ ] Configure reverse proxy (Nginx/Caddy) for local-only access
- [ ] Create initial admin user and API token

### 1.2 Board Structure Design

**Proposed Boards**:

| Board | Purpose | Teams |
|-------|---------|-------|
| **Foundation-Core** | Xoe-NovAi stack development | Ra, Ptah, Anubis |
| **Arcana-Esoteric** | Research, esoteric integrations | Thoth, Seshat |
| **External-Onboard** | Cloud assistant coordination | All external agents |
| **Migration-Tracker** | Memory bank → Vikunja migration | Anubis, Ptah |

**Default Columns per Board**:
- 📥 Backlog
- 🔄 In Progress
- 👀 Review
- ✅ Done
- 📋 Archived

---

## Phase 2: Integration Layer (Week 3-4)

### 2.1 Vikunja MCP Server

**Architecture**:
```python
# scripts/mcp_servers/vikunja_mcp.py
"""
MCP Server for Vikunja PM integration
Enables agents to create tasks, update status, query milestones
"""

from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("vikunja-pm")
VIKUNJA_API = "http://vikunja:3456/api/v1"
API_TOKEN = "${VIKUNJA_API_TOKEN}"  # From env

@mcp.tool()
async def create_task(
    title: str,
    description: str,
    board_id: int,
    assignee: str = None,
    priority: int = 2,
    labels: list = None
) -> dict:
    """Create new task in Vikunja"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{VIKUNJA_API}/projects/{board_id}/tasks",
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            json={
                "title": title,
                "description": description,
                "assignee_id": assignee,
                "priority": priority,
                "labels": labels or []
            }
        )
        return response.json()

@mcp.tool()
async def update_task_status(task_id: int, status: str) -> dict:
    """Update task status (backlog, in_progress, review, done)"""
    # Implementation
    pass

@mcp.tool()
async def get_milestone_progress(board_id: int) -> dict:
    """Get completion stats for board milestones"""
    # Implementation
    pass

@mcp.tool()
async def sync_memory_bank_to_vikunja(memory_file: str) -> dict:
    """One-way sync: memory_bank entry → Vikunja task"""
    # Implementation
    pass
```

**Tools Provided**:
- `create_task`: Add tasks from any agent context
- `update_task_status`: Move tasks through workflow
- `get_milestone_progress`: Query completion metrics
- `sync_memory_bank_to_vikunja`: Migration helper

### 2.2 Memory Bank Migration Script

```python
# scripts/migrate_memory_bank_to_vikunja.py
"""
One-time migration: memory_bank/ → Vikunja tasks
Preserves history while enabling new workflow
"""

import frontmatter
import glob
from pathlib import Path

MEMORY_BANK_DIR = "memory_bank"
VIKUNJA_API = "http://localhost:3456/api/v1"

def parse_memory_bank_entry(filepath: Path) -> dict:
    """Extract task-worthy content from memory bank files"""
    with open(filepath) as f:
        post = frontmatter.load(f)
    
    return {
        "title": post.get("title", filepath.stem),
        "content": post.content[:500],  # First 500 chars
        "tags": post.get("tags", []),
        "date": post.get("date"),
        "priority": post.get("priority", "medium"),
        "status": post.get("status", "active")
    }

def create_vikunja_task(entry: dict, board_id: int) -> bool:
    """Create task in Migration-Tracker board"""
    # API call implementation
    pass

def main():
    """Migrate all memory bank files to Vikunja"""
    memory_files = glob.glob(f"{MEMORY_BANK_DIR}/**/*.md", recursive=True)
    
    for filepath in memory_files:
        entry = parse_memory_bank_entry(Path(filepath))
        create_vikunja_task(entry, board_id=4)  # Migration-Tracker board
        print(f"✅ Migrated: {filepath}")

if __name__ == "__main__":
    main()
```

---

## Phase 3: Agent Workflow Integration (Week 5-6)

### 3.1 Task Creation Protocol

**New Standard**:
```markdown
## Task Creation Template (Vikunja)

**Title**: [P0/P1/P2/P3] Brief description
**Board**: Foundation-Core / Arcana-Esoteric / External-Onboard
**Assignee**: Agent persona (Ra, Thoth, Ptah, Anubis, Seshat)
**Labels**: [bug, feature, research, docs, migration]

**Description**:
```
**Objective**: What needs to be done
**Context**: Links to relevant memory_bank/ or docs/
**Acceptance Criteria**: Definition of done
**Ma'at Alignment**: Which ideals apply
```

**Dependencies**: Links to other Vikunja tasks
**Estimated Effort**: Hours/days
```

### 3.2 Sync Protocols Update

**New Rule**: All agents check Vikunja before starting work

```yaml
# xoe-novai-sync/_meta/sync-protocols-v1.5.0.md (addition)

## Vikunja Synchronization Protocol

### Pre-Session Checklist
1. Query Vikunja for assigned tasks
2. Update task status to "In Progress"
3. Link any new discoveries to existing tasks
4. Post completion summary as task comment

### Post-Session Protocol
1. Update task status (review/done)
2. Add memory_bank reference if created
3. Tag related agents for handoff
4. Update progress.md from Vikunja milestones
```

---

## Phase 4: Advanced Features (Week 7-8)

### 4.1 Automated Sync Pipeline

**GitHub Actions / Local Cron**:
```yaml
# .github/workflows/vikunja-sync.yml
name: Vikunja Sync
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Sync Vikunja to progress.md
        run: |
          python3 scripts/sync_vikunja_to_progress.py
          git add memory_bank/progress.md
          git commit -m "chore: sync progress from Vikunja"
          git push
```

### 4.2 Gemini CLI Integration

**Special Role**: Terminal-native execution via Vikunja tasks

```bash
# Example: Gemini CLI executes Vikunja task
$ vikunja-task exec 1234
# Gemini CLI:
# 1. Reads task description from Vikunja API
# 2. Executes commands in terminal
# 3. Posts results back to Vikunja as comment
# 4. Updates task status
```

---

## Migration Strategy

### Legacy System Handling

| Legacy System | Migration Action | Post-Migration Role |
|--------------|------------------|---------------------|
| **memory_bank/** | One-time import to Vikunja | Archive + RAG source |
| **Grok-Pack** | Export summaries to Vikunja | Grok-only continuity |
| **.clinerules** | No migration | Personal scratch (unchanged) |
| **stack-cat.py** | Update to generate Vikunja tasks | Context pack generator |

### Rollback Plan

If Vikunja integration fails:
1. Re-enable memory_bank as primary
2. Export Vikunja tasks to markdown
3. Restore legacy sync protocols
4. Archive migration attempt

---

## Success Metrics

### Week 4 Checkpoints
- [ ] Vikunja deployed and accessible
- [ ] MCP server operational
- [ ] 50% of active memory_bank entries migrated
- [ ] All agents onboarded to new workflow

### Week 8 Completion
- [ ] 100% task creation in Vikunja
- [ ] Zero new entries in legacy memory_bank
- [ ] Automated sync pipeline running
- [ ] Documentation fully updated

---

## Ma'at Alignment

| Ideal | Implementation |
|-------|---------------|
| **7 - Truth** | Single source of truth (Vikunja), no scattered .md files |
| **18 - Balance** | Harmonious coordination between all agents via central hub |
| **41 - Advance** | Modern PM tooling, automated workflows, scalable architecture |

---

**Status**: 🚀 **Ready for Implementation**  
**Next Action**: Create `docker-compose.vikunja.yml` and deploy Phase 1  
**Owner**: Ptah (Cline) with Anubis (Gemini CLI) support

*"From scattered memory to centralized harmony — the temple rises."*
