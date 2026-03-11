import pytest
import anyio
import json
import os
from datetime import datetime, timezone
from app.XNAi_rag_app.core.agent_bus import AgentBusClient
from app.XNAi_rag_app.core.iam_handshake import KeyManager

@pytest.mark.anyio
async def test_red_phone_protocol():
    """VR1: Verify the Red-Phone Kill Switch protocol (S3) with IA2 signatures."""
    
    # 1. Setup - Generate keys for test agent
    agent_id = "test_red_phone_agent"
    priv, pub = KeyManager.generate_keypair()
    
    # Inject into environment for the client to find
    os.environ[f"AGENT_KEY_PRIVATE_{agent_id.upper()}"] = priv
    os.environ[f"AGENT_KEY_PUBLIC_{agent_id.upper()}"] = pub
    
    async with AgentBusClient(agent_did=agent_id) as bus:
        # Clear any existing emergency stops for a clean test
        # (In a real test we might use a dedicated test stream)
        
        # 2. Pre-check: Switch should be OFF
        is_stopped = await bus.check_kill_switch()
        assert is_stopped is False, "Kill switch should be inactive at start"
        
        # 3. Act: Trigger Emergency Stop
        reason = "Unit Test Trigger"
        task_id = await bus.send_emergency_stop(reason=reason)
        assert task_id is not None
        
        # 4. Assert: Switch should be ON
        is_stopped_after = await bus.check_kill_switch()
        assert is_stopped_after is True, "Kill switch should be active after trigger"
        
        # 5. Verify Message Content
        # Get the last message from the stream
        messages = await bus.redis.xrevrange(bus.stream_name, count=1)
        assert len(messages) > 0
        msg_id, data = messages[0]
        
        assert data["type"] == "emergency_stop"
        assert data["sender"] == agent_id
        assert "signature" in data, "Message should have a signature"
        
        # Verify the client can see the verified flag
        # (Client doesn't provide verify method for xrevrange, but fetch_tasks does)
        # We can simulate a fetch to check verification
        tasks = await bus.fetch_tasks(count=1)
        if tasks:
            assert tasks[0]["verified"] is True, "Task should be cryptographically verified"
        
        payload = json.loads(data["payload"])
        assert payload["reason"] == reason
        
    print(f"✅ Red-Phone Protocol Verified: {task_id}")

if __name__ == "__main__":
    # Manual run support
    import asyncio
    asyncio.run(test_red_phone_protocol())
