# Explanation: Staging Cleanup and Connection Management

> **Date**: 2026-02-22
> **Author**: GEMINI-MC
> **Status**: INITIAL DRAFT
> **Context**: Research Tasks G-004, G-010

---

## 1. Staging Cleanup Architecture

The XNAi Foundation staging layer requires a reliable, declarative cleanup system. While `systemd-tmpfiles` handles the majority of simple file age-based deletions, complex scenarios (e.g., verifying a task is "Complete" in Redis before deleting its raw data) require a more flexible systemd timer approach.

### 1.1 systemd-tmpfiles Configuration (G-004)

`systemd-tmpfiles` is the modern standard for declarative cleanup.

**Configuration Template**: `xnai-staging.conf`
```conf
# Type  Path            Mode UID  GID  Age  Argument
d       /path/to/rejected  0755 root root 2d   -
d       /path/to/extracted 0755 root root 7d   -
d       /path/to/distilled 0755 root root 30d  -
```

**System Integration**:
- Place in `/etc/tmpfiles.d/` for system-wide execution.
- Managed by `systemd-tmpfiles-setup.service` (at boot) and `systemd-tmpfiles-clean.timer` (daily).

### 1.2 Custom Cleanup with systemd Timers

For data that requires cross-service validation (e.g., checking Qdrant before deleting a distilled file):

**Service**: `xnai-staging-cleanup.service`
```ini
[Unit]
Description=XNAi custom staging cleanup service
After=network.target redis.service

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /home/arcana-novai/Documents/xnai-foundation/scripts/cleanup_staging.py --verified
User=root
```

**Timer**: `xnai-staging-cleanup.timer`
```ini
[Unit]
Description=Run XNAi staging cleanup every 6 hours

[Timer]
OnBootSec=15min
OnUnitActiveSec=6h
Unit=xnai-staging-cleanup.service
Persistent=true

[Install]
WantedBy=timers.target
```

---

## 2. WebSocket Connection Management (G-010)

The `ConnectionManager` is the central component for managing WebSocket-based agent coordination.

### 2.1 Pattern: ConnectionManager Class

This class tracks active `WebSocket` connections and handles lifecycle events.

```python
class ConnectionManager:
    def __init__(self):
        # Map agent_id to active WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, agent_id: str):
        await websocket.accept()
        self.active_connections[agent_id] = websocket
        logger.info(f"Agent {agent_id} connected.")

    def disconnect(self, agent_id: str):
        if agent_id in self.active_connections:
            del self.active_connections[agent_id]
            logger.info(f"Agent {agent_id} disconnected.")

    async def send_personal_message(self, message: str, agent_id: str):
        if agent_id in self.active_connections:
            await self.active_connections[agent_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)
```

### 2.2 Lifecycle & Error Handling

- **Automatic Cleanup**: Connections are removed from the manager when the `receive_json()` loop breaks due to a `WebSocketDisconnect`.
- **Duplicate Prevention**: If an `agent_id` reconnects, the existing connection is closed and replaced with the new one.
- **Heartbeats**: The manager should periodically iterate through `active_connections` and perform a `ping` to ensure the underlying TCP socket is still alive.

---

## 3. Next Steps

1. Implement `scripts/cleanup_staging.py` for verified-only deletions.
2. Integrate `ConnectionManager` into the `app/XNAi_rag_app/core/agent_bus.py`.
3. Add Prometheus metrics for `active_websocket_connections` and `staging_files_deleted_total`.
