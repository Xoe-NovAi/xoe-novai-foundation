# 🔱 Agent Bus Auto-Connect Logic
async def bootstrap_registration(self):
    """S4: Automated identity broadcast on startup."""
    identity_payload = {
        "agent_id": self.agent_id,
        "did": self.agent_did,
        "capabilities": self.capabilities,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await self.send_task(target_did="*", task_type="identity_announcement", payload=identity_payload)
    logger.info(f"🔱 Metropolis: Agent {self.agent_id} has joined the mesh.")
