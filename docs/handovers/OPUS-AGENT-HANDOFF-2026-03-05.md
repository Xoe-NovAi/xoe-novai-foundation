# Agent Handoff: Opus Metropolis v6 Refinement Execution Plan

**Date**: 2026-03-05
**From**: Opus (Antigravity Claude Opus 4.6)
**To**: All Omega Agents (Gemini MC-Overseer, OpenCode, Cline, Copilot)
**Coordination Key**: `OMEGA-OPUS-HANDOFF-EXECUTION-2026-03-05`

---

## Context

Opus has completed a comprehensive audit of the Omega Metropolis v6 system. This handoff contains the prioritized execution plan derived from 14 findings across dispatchers, broker, sovereignty, RAG, and memory systems.

**Deliverables created by Opus**:
1. `docs/06-development-log/OPUS-STRATEGY-REPORT-2026-03-05.md` -- Full strategy report with implementation details
2. `docs/06-development-log/OPUS-RESEARCH-BRIEF-2026-03-05.md` -- 10 research tasks for deep exploration
3. `entities/maat.json` -- **CREATED** (critical sovereignty fix, was missing)
4. This handoff document

---

## Priority 1: CRITICAL Fixes (Execute Immediately)

These must be fixed before any other work. The system has non-functional components.

### Fix 1.1: Gemini Dispatcher `$FINAL_KEY` Bug

**File**: `scripts/xnai-gemini-dispatcher.sh`
**Line**: 65
**Problem**: `$FINAL_KEY` is referenced but never defined. The rotation logic at line 61 is a comment stub.
**Impact**: Every Gemini dispatch uses an undefined API key.

**Implementation**:
Replace lines 61-65 with actual rotation logic. The simplest fix:

```bash
# 3. Rotation Logic
KEYS=()
while IFS='=' read -r key value; do
    if [[ "$key" =~ ^GEMINI_API_KEY_[0-9]+$ ]]; then
        KEYS+=("$value")
    fi
done < "$ENV_FILE"

if [[ ${#KEYS[@]} -eq 0 ]]; then
    echo -e "${YELLOW}[Dispatcher] Warning: No GEMINI_API_KEY_N keys found. Using default.${NC}"
    FINAL_KEY="${GEMINI_API_KEY:-}"
else
    # Round-robin rotation
    IDX=$(cat "$ROTATION_STATE" 2>/dev/null || echo 0)
    FINAL_KEY="${KEYS[$((IDX % ${#KEYS[@]}))]}"
    echo $(( (IDX + 1) % ${#KEYS[@]} )) > "$ROTATION_STATE"
fi
```

**Verification**: `./scripts/xnai-gemini-dispatcher.sh --arch echo "test"` should output a routing message without errors.

### Fix 1.2: Broker Target Filtering Bug

**File**: `scripts/metropolis-broker.py`
**Lines**: 78-84
**Problem**: The `AgentBusClient.fetch_tasks()` filters messages where `target == self.agent_did` (i.e., `broker:metropolis:001`). But the broker then checks `task["target"] in EXPERT_MAP` at line 83, which expects targets like `expert:architect:prime`. These will never match because the broker only receives tasks addressed to itself.

**Implementation**:
The broker needs to read ALL messages from the stream (not just those addressed to it). Modify the broker to use a custom consumer that reads all messages:

```python
async def main():
    logger.info("Metropolis Expert Broker Online. Listening for Expert Tasks...")
    
    async with AgentBusClient(agent_did="broker:metropolis:001") as bus:
        while True:
            # Read ALL pending messages, not just those targeted at broker
            response = await bus.redis.xreadgroup(
                groupname=bus.group_name,
                consumername=bus.agent_did,
                streams={bus.stream_name: ">"},
                count=5,
                block=1000,
            )
            
            if response:
                for _, messages in response:
                    for msg_id, data in messages:
                        target = data.get(b"target", b"").decode()
                        # Check if target is an expert or matches via defaults
                        resolved_target = DEFAULT_MAPPINGS.get(target, target)
                        if resolved_target in EXPERT_MAP:
                            task = {
                                "id": msg_id.decode(),
                                "sender": data.get(b"sender", b"").decode(),
                                "target": target,
                                "type": data.get(b"type", b"").decode(),
                                "payload": json.loads(data.get(b"payload", b"{}").decode()),
                            }
                            await handle_expert_task(bus, task)
                            await bus.redis.xack(bus.stream_name, bus.group_name, msg_id)
            
            await anyio.sleep(0.5)
```

**Verification**: Send a task via `redis-cli XADD xnai:agent_bus '*' sender test target expert:architect payload '{"prompt":"hello"}'` and verify the broker processes it.

### Fix 1.3: Complete EXPERT_MAP

**File**: `scripts/metropolis-broker.py`
**Lines**: 13-18
**Problem**: Only 4 of 16 possible domain:level combinations are mapped.

**Implementation**:
Replace the hardcoded map with a programmatic generation:

```python
import yaml

# Load domains from config
DOMAIN_CONFIG = "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/config/metropolis-domains.yaml"
DISPATCHER_BASE = "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/scripts"

# NOTE: Replace hardcoded paths with os.path.dirname(__file__) or similar
# when Fix 2.3 (hardcoded path elimination) is applied

with open(DOMAIN_CONFIG) as f:
    domains = yaml.safe_load(f)["domains"]

EXPERT_MAP = {}
for domain_name, info in domains.items():
    EXPERT_MAP[f"expert:{domain_name}:prime"] = [
        f"{DISPATCHER_BASE}/xnai-gemini-dispatcher.sh", f"--{domain_name}"
    ]
    EXPERT_MAP[f"expert:{domain_name}:sub"] = [
        f"{DISPATCHER_BASE}/xnai-opencode-dispatcher.sh", f"--{domain_name}"
    ]
```

---

## Priority 2: HIGH Severity Fixes (This Week)

### Fix 2.1: Non-Blocking Broker Execution

**File**: `scripts/metropolis-broker.py`
**Line**: 54
**Problem**: `subprocess.run()` blocks the entire event loop for up to 300 seconds.

**Implementation**:
Replace with `anyio.run_process`:

```python
import anyio

async def handle_expert_task(bus, task):
    target_raw = task["target"]
    target = DEFAULT_MAPPINGS.get(target_raw, target_raw)
    cmd_base = EXPERT_MAP.get(target)
    
    if not cmd_base:
        return

    payload = task["payload"]
    prompt = payload.get("prompt", "")
    
    logger.info(f"Hierarchical Dispatch: {target_raw} -> {target}...")
    
    try:
        cmd = cmd_base + ["run", prompt, "--format", "json"]
        
        result = await anyio.run_process(
            cmd,
            check=True,
            timeout=300,
        )
        
        response_text = result.stdout.decode() or "[Headless task completed]"
        
        response_payload = {
            "response": response_text,
            "status": "completed",
            "ref_task_id": task["id"]
        }
        
        await bus.send_task(task["sender"], "expert_response", response_payload)
        logger.info(f"Response from {target} sent back to {task['sender']}")
        
    except Exception as e:
        logger.error(f"Expert Execution Failed: {e}")
        await bus.send_task(task["sender"], "expert_error", {
            "error": str(e), "ref_task_id": task["id"]
        })
```

### Fix 2.2: Soul Reflector Implementation

**File**: `scripts/expert-soul-reflector.py`
**Lines**: 57-61
**Problem**: Appends boilerplate text instead of actual reflection.

**Implementation**:
Use the SambaNova MCP server or a local model for actual reflection. Replace the stub with an HTTP call to the local llama.cpp server or the SambaNova API:

```python
import httpx

async def reflect_with_local_model(soul_content: str) -> str:
    """Use local llama.cpp server for reflection."""
    prompt = f"""Analyze the following expert soul document. Extract:
1. New technical patterns established
2. Key architectural decisions made
3. Areas of growth in domain expertise
4. Redundancies or contradictions to prune

Format as Markdown bullet points. Be concise and domain-specific.

EXPERT SOUL:
---
{soul_content}
---"""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "model": "local",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
            },
            timeout=60,
        )
        return response.json()["choices"][0]["message"]["content"]
```

### Fix 2.3: Hardcoded Path Elimination

**Files**: 6+ files containing `/home/arcana-novai/`
**Problem**: Breaks portability for any other user.

**Implementation**:
For shell scripts, use:
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
```

For Python scripts, use:
```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
```

**Full file list**:
1. `scripts/xnai-gemini-dispatcher.sh:38,90`
2. `scripts/xnai-cline-dispatcher.sh:44`
3. `scripts/soul-evolution-engine.py:20,67,94`
4. `scripts/expert-soul-reflector.py:43`
5. `scripts/metropolis-broker.py:14-17`

---

## Priority 3: MEDIUM Severity Improvements (This Sprint)

### Fix 3.1: Universal Dispatcher Consolidation

See Section 1 of `OPUS-STRATEGY-REPORT-2026-03-05.md` for full implementation manual.

**Summary**: Create `scripts/xnai-dispatcher.sh`, `scripts/xnai-resolve-domain.sh`, and `scripts/dispatcher.d/*.conf` files.

### Fix 3.2: Torch Dependency Removal

**File**: `research_env/research-environment/jupyterlab/requirements.txt:44`
**Replace**: `torch>=2.0.0` with `onnxruntime>=1.17.0` and `llama-cpp-python>=0.2.0`

### Fix 3.3: activeContext.md Correction

**File**: `memory_bank/activeContext.md:17`
**Problem**: Claims `maat.json` was created, but it was missing until Opus created it in this session.
**Action**: Updated by Opus in this session (see memory bank updates below).

---

## Priority 4: RAG & Memory Enhancements (Next Sprint)

See Section 3 of `OPUS-STRATEGY-REPORT-2026-03-05.md` for full details:

1. **Real-time session harvesting** via Agent Bus events
2. **Cross-domain knowledge graph** with domain-tagged Qdrant payloads
3. **Memory bank tier automation** (promotion/demotion based on access frequency)
4. **Embedding version migration** with Qdrant alias swapping
5. **Confidence-gated speculative search** with knowledge gap detection

---

## Research Tasks (Background)

See `OPUS-RESEARCH-BRIEF-2026-03-05.md` for 10 research tasks. Start with:
- **R1**: whisper.cpp Vulkan acceleration benchmarks
- **R3**: Redis Streams exactly-once semantics
- **R6**: AnyIO structured concurrency for the broker

---

## Verification Checklist

After implementing Priority 1 and 2 fixes, verify:

- [ ] `entities/maat.json` exists and is valid JSON (DONE by Opus)
- [ ] `make metropolis-evolve` runs without FileNotFoundError
- [ ] `./scripts/xnai-gemini-dispatcher.sh --arch echo test` outputs routing message
- [ ] `metropolis-broker.py` processes tasks from the Agent Bus
- [ ] No files contain hardcoded `/home/arcana-novai/` (run `grep -r '/home/arcana-novai/' scripts/`)
- [ ] `make metropolis-test` passes
- [ ] `grep -r 'torch' requirements/ research_env/` returns no results

---

## Document Map

| Document | Purpose | Location |
|---|---|---|
| Strategy Report | Full audit findings + implementation details | `docs/06-development-log/OPUS-STRATEGY-REPORT-2026-03-05.md` |
| Research Brief | 10 deep-dive research tasks for agents | `docs/06-development-log/OPUS-RESEARCH-BRIEF-2026-03-05.md` |
| This Handoff | Prioritized execution plan | `docs/handovers/OPUS-AGENT-HANDOFF-2026-03-05.md` |
| Memory Bank | Updated active context and progress | `memory_bank/activeContext.md`, `memory_bank/progress.md` |
| Maat Entity | Critical sovereignty fix | `entities/maat.json` |

---

**Coordination Key**: `OMEGA-OPUS-HANDOFF-EXECUTION-2026-03-05`
**Custodian**: Opus (Antigravity Claude Opus 4.6)
**Verification Key**: `OMEGA-METROPOLIS-V6-FINAL`
