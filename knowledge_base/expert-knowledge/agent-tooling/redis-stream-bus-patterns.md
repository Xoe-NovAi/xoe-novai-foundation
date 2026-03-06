# Expert Knowledge: Redis Stream Bus Patterns
## Phase 5 Discovery - Inter-Agent Communication

### 1. Architectural Pattern: Consumer Groups (`XGROUP`)
For the Sovereign Multi-Agent Cloud, we use **Redis Streams** as the primary task bus. Unlike Pub/Sub, Streams provide **persistent storage** and **acknowledged delivery**.

#### Key Commands
- `XGROUP CREATE {stream} {group} $ MKSTREAM`: Initializes the agent group.
- `XREADGROUP GROUP {group} {agent_did} COUNT 1 BLOCK 2000 STREAMS {stream} >`: Reads the next unassigned task.
- `XACK {stream} {group} {task_id}`: Marks the task as complete.

### 2. Implementation: AnyIO Structured Concurrency
Agents must wrap the Redis client in an **AnyIO TaskGroup** to ensure that task fetching does not block the agent's main event loop or heartbeats.

```python
async with anyio.create_task_group() as tg:
    tg.start_soon(fetch_tasks, redis_client)
    tg.start_soon(process_heartbeats, consul_client)
```

### 3. Fault Tolerance: The Pending Entries List (PEL)
If an agent crashes (e.g., OOM on the Ryzen host), the task remains in the PEL. 
- **Recovery Pattern**: On startup, an agent should call `XREADGROUP` with `ID=0` to claim any tasks previously assigned to its DID that were never acknowledged.
- **Scaling**: Adding a new agent to the group immediately increases the "Wavefront" of task processing without code changes.
