# XNAi Vikunja MCP Server

MCP server providing task management integration via Vikunja API.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Add to `.opencode/opencode.json`:

```json
{
  "mcp": {
    "servers": {
      "xnai-vikunja": {
        "command": "python",
        "args": ["mcp-servers/xnai-vikunja/server.py"],
        "env": {
          "VIKUNJA_URL": "http://localhost:3456",
          "VIKUNJA_TOKEN": "your-token-here"
        }
      }
    }
  }
}
```

## Tools

### list_projects

List all Vikunja projects.

### list_tasks

List tasks in a project.

**Parameters:**
- `project_id` (integer, required): Project ID

### create_task

Create a new task.

**Parameters:**
- `project_id` (integer, required): Project ID
- `title` (string, required): Task title
- `description` (string): Task description
- `priority` (integer): Priority 1-5 (1=critical, 5=someday)

**Example:**
```json
{
  "project_id": 1,
  "title": "Implement authentication",
  "description": "Add JWT-based authentication",
  "priority": 2
}
```

### update_task

Update an existing task.

**Parameters:**
- `task_id` (integer, required): Task ID
- `title` (string): New title
- `description` (string): New description
- `done` (boolean): Mark as complete

### vikunja_health

Check Vikunja API health.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| VIKUNJA_URL | http://localhost:3456 | Vikunja API URL |
| VIKUNJA_TOKEN | | API token (optional) |
