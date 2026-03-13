import anyio
import json
import os
import yaml
import logging
from pathlib import Path
import sys

# ODES: The Monad Integration
# 🏙️ Metropolis Broker v2.2 (The Technites' Gate)

# Add app directory to Python path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.XNAi_rag_app.core.paths import (
    get_config_path,
    get_script_path,
    OMEGA_ROOT
)
from app.XNAi_rag_app.core.agent_bus import AgentBusClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ODES:Broker")

# 🏛️ Ennead Configuration
DOMAIN_CONFIG = get_config_path("metropolis-domains.yaml")
DISPATCHER_GEMINI = get_script_path("xnai-gemini-dispatcher.sh")
DISPATCHER_OPENCODE = get_script_path("xnai-opencode-dispatcher.sh")

# 🧩 The Ennead Mapping (Programmatic Generation)
def build_expert_map():
    with open(DOMAIN_CONFIG) as f:
        domains = yaml.safe_load(f).get("domains", {})
    
    emap = {}
    for domain_name in domains:
        # Tier 1/2: Helios (Gemini) - The Strategic/Tactical
        emap[f"expert:{domain_name}:prime"] = [str(DISPATCHER_GEMINI), f"--{domain_name}"]
        # Tier 2/3: Hephaestus (OpenCode) - The Implementation
        emap[f"expert:{domain_name}:sub"] = [str(DISPATCHER_OPENCODE), f"--{domain_name}"]
    
    # 🏺 Classical ODES Fallbacks (Defaults)
    defaults = {
        "expert:architect": "expert:architect:prime",
        "expert:api":       "expert:api:prime",
        "expert:ui":        "expert:ui:prime",
        "expert:data":      "expert:data:prime",
        "expert:ops":       "expert:ops:prime",
        "expert:research":  "expert:research:prime",
        "expert:test":      "expert:test:prime",
        "expert:security":  "expert:security:prime",
        "expert:auditor":   "expert:security:prime"
    }
    return emap, defaults

EXPERT_MAP, DEFAULT_MAPPINGS = build_expert_map()

async def handle_expert_task(bus: AgentBusClient, task: dict):
    """
    ⚖️ The Monad Execution Logic
    Handles the fractal dispatch of Technite tasks.
    """
    target_raw = task.get("target")
    target = DEFAULT_MAPPINGS.get(target_raw, target_raw)
    cmd_base = EXPERT_MAP.get(target)
    
    if not cmd_base:
        return

    payload = task.get("payload", {})
    prompt = payload.get("prompt", "")
    
    logger.info(f"🔗 ODES Dispatch: {target_raw} -> {target}...")
    
    # 🛡️ Auditor's Watchdog (Non-blocking with hard timeout)
    try:
        # Launch Technite via Universal Dispatcher
        cmd = cmd_base + ["run", prompt, "--format", "json"]
        
        with anyio.move_on_after(300) as scope:
            result = await anyio.run_process(
                cmd,
                check=True,
                stdout=anyio.subprocess.PIPE,
                stderr=anyio.subprocess.PIPE
            )
            
            # 🧪 Brigid's Synthesis (Cleaning and returning result)
            response_text = result.stdout.decode().strip() or "[Technite task completed]"
            
            await bus.send_task(task["sender"], "expert_response", {
                "response": response_text,
                "status": "completed",
                "ref_task_id": task["id"],
                "technite": target
            })
            logger.info(f"✅ Techne complete: {target}")
            return

        if scope.cancel_called:
            logger.warning(f"⏰ Techne Timeout (300s): {target}")
            await bus.send_task(task["sender"], "expert_error", {
                "error": "Phronesis Timeout: Execution exceeded 300s",
                "ref_task_id": task["id"]
            })

    except anyio.subprocess.ProcessLookupError:
        logger.error(f"❌ Techne Process Lost: {target}")
    except Exception as e:
        # Check if it's a process error without requiring the exact attribute path
        if "CalledProcessError" in str(type(e)):
            logger.error(f"❌ Techne Error: {e}")
        else:
            logger.error(f"❌ ODES General Failure: {e}")
        
        await bus.send_task(task["sender"], "expert_error", {
            "error": str(e), "ref_task_id": task["id"]
        })

async def main():
    logger.info(f"🏙️  Metropolis ODES Broker Online. Monad Gate Active.")
    
    # 🌊 Listening for the Agent Bus
    async with AgentBusClient(agent_did="broker:metropolis:001") as bus:
        while True:
            try:
                # Read ALL pending messages (Opus Fix 1.2)
                response = await bus.redis.xreadgroup(
                    groupname=bus.group_name,
                    consumername=bus.agent_did,
                    streams={bus.stream_name: ">"},
                    count=5,
                    block=2000,
                )
                
                if response:
                    for stream_name, messages in response:
                        for msg_id, data in messages:
                            target = data.get(b"target", b"").decode()
                            resolved_target = DEFAULT_MAPPINGS.get(target, target)
                            
                            # Claim if targeted at any known Technite
                            if resolved_target in EXPERT_MAP:
                                task = {
                                    "id": msg_id.decode(),
                                    "sender": data.get(b"sender", b"").decode(),
                                    "target": target,
                                    "type": data.get(b"type", b"").decode(),
                                    "payload": json.loads(data.get(b"payload", b"{}").decode()),
                                }
                                # Execute asynchronously (Lilith's Chaos)
                                await handle_expert_task(bus, task)
                                await bus.redis.xack(bus.stream_name, bus.group_name, msg_id)
                
            except Exception as e:
                logger.error(f"Broker Loop Disruption: {e}")
                await anyio.sleep(1)
            
            await anyio.sleep(0.1)

if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        logger.info("ODES Broker shutting down...")
