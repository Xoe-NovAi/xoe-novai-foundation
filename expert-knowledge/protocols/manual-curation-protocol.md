# Protocol: Manual Technical Manual Curation
## Version: 1.0.0 | Date: 2026-02-15

### Overview
This protocol defines how to manually trigger the ingestion of technical manuals and books into the XNAi Sovereign Knowledge Base (FAISS/Redis).

### Workflow
1.  **Task Creation**: Create a task in **Vikunja** with the title `curate: {path_to_book}`.
    - Example: `curate: /library/manuals/ryzen_7_5700U_specs.pdf`
2.  **Bridge Detection**: The `CurationBridge` polls Vikunja every 60 seconds for tasks starting with `curate:`.
3.  **Agent Bus Dispatch**: The bridge sends a `CURATE_BOOK` task to the **Agent Bus**.
4.  **Worker Execution**: The `curation_worker` (running on the host or in a container) fetches the task, runs the ingestion pipeline, and acknowledges completion.
5.  **Persistence**:
    - **Redis**: Stores book metadata and ingestion status.
    - **FAISS**: Stores the vector embeddings for RAG retrieval.

### Manual Trigger (CLI)
If Vikunja is unavailable, curators can manually push to the bus:
```bash
PYTHONPATH=. venv/bin/python3 -c "from app.XNAi_rag_app.core.agent_bus import AgentBusClient; import anyio; async def push(): async with AgentBusClient('did:manual') as b: await b.send_task('*', 'CURATE_BOOK', {'source_path': '/path/to/book'}); anyio.run(push)"
```
