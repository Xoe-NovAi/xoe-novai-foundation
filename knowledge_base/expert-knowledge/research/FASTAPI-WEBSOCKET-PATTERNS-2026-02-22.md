# Research: FastAPI WebSocket Patterns for MC Coordination

> **Date**: 2026-02-22
> **Author**: GEMINI-MC
> **Status**: INITIAL DRAFT
> **Context**: Phase 4 Preparation / Research Tasks G-008, G-009, G-010

---

## 1. Overview

WebSockets are the primary communication channel for real-time coordination between the MC-Overseer and its specialized agents (Cline, Gemini). They enable low-latency, bidirectional data flow and efficient response streaming.

## 2. Best Practices & Patterns

### 2.1 Connection Management (G-010)
- **ConnectionManager Pattern**: Implement a centralized class to track active `WebSocket` objects.
- **Client Identification**: Use a unique `client_id` (or `agent_id`) to route messages to specific agents.
- **Graceful Disconnects**: Always catch `WebSocketDisconnect` to clean up resources and notify other agents.
- **Heartbeats**: Implement a "ping/pong" mechanism to detect stale connections that haven't explicitly closed.

### 2.2 Multi-Agent Coordination (G-008)
- **Message Schemas**: Use Pydantic models to define structured JSON messages for `tasks`, `status_updates`, and `handoffs`.
- **Broadcast vs. Unicast**: 
  - *Broadcast*: For system-wide alerts or global state changes (e.g., "New Coordination Key").
  - *Unicast*: For direct task assignments (e.g., "CLINE-1, execute R003-1").
- **Agent Handshakes**: Implement a secure handshake during connection initialization (e.g., passing a DID or API key).

### 2.3 Response Streaming (G-009)
- **Token-by-Token Streaming**: Essential for real-time feedback during long-running LLM tasks.
- **Buffered Flushing**: Send data in small, meaningful chunks rather than single characters to balance latency and overhead.
- **Async Iterators**: Use `async for` loops to stream data from backend services (e.g., Qdrant search results) directly to the WebSocket.

---

## 3. Proposed XNAi WebSocket Architecture

### 3.1 Endpoint Structure
```python
@app.websocket("/ws/v1/coordination/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    await manager.connect(websocket, agent_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Route message via Agent Bus
            await process_agent_message(agent_id, data)
    except WebSocketDisconnect:
        manager.disconnect(agent_id)
```

### 3.2 Message Protocol (Example)
```json
{
  "type": "task_assignment",
  "payload": {
    "task_id": "G-001",
    "instruction": "Research TTL cleanup..."
  },
  "metadata": {
    "timestamp": "2026-02-22T23:00:00Z",
    "sender": "MC-OVERSEER"
  }
}
```

---

## 4. Operational Guardrails

1. **Authentication**: All WebSocket connections must be authenticated via a token passed in the query string or headers.
2. **Rate Limiting**: Limit the number of messages per second to prevent agent loops from flooding the server.
3. **Payload Sanitization**: Validate all incoming JSON against Pydantic models before processing.
4. **AnyIO Concurrency**: Use `anyio.create_task_group()` to manage background tasks associated with a connection.

---

## 5. Next Steps
1. Implement the `ConnectionManager` in `app/XNAi_rag_app/core/agent_bus.py`.
2. Define the Pydantic message models in `app/XNAi_rag_app/core/state.py`.
3. Create a mock WebSocket client for testing the coordination flow.
