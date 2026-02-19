# XNAi RAG MCP Server

MCP server providing semantic search capabilities via the XNAi Foundation RAG API.

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
      "xnai-rag": {
        "command": "python",
        "args": ["mcp-servers/xnai-rag/server.py"],
        "env": {
          "RAG_API_URL": "http://localhost:8000"
        }
      }
    }
  }
}
```

## Tools

### semantic_search

Search the Foundation knowledge base.

**Parameters:**
- `query` (string, required): Search query
- `mode` (string): "semantic", "lexical", or "hybrid" (default: "hybrid")
- `top_k` (integer): Number of results (default: 10)

**Example:**
```json
{
  "query": "implement authentication",
  "mode": "hybrid",
  "top_k": 5
}
```

### rag_health

Check RAG API health status.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| RAG_API_URL | http://localhost:8000 | RAG API endpoint |
