# 🧪 Resilience & Chaos Engineering

Omega Stack incorporates advanced resilience patterns to ensure the "Hearth" stays warm even under extreme load or component failure.

---

## 🛑 1. The Red-Phone Protocol (Global Halt)

The **Red-Phone** is a global emergency stop mechanism. When triggered, it broadcasts a high-priority signal across the Agent Bus that all active workers must obey.

### How to Trigger
```bash
# Via Python (AgentBusClient)
await bus.send_emergency_stop(reason="Security Breach Detected")
```

### How it Works
1. A message of type `emergency_stop` is added to the `xnai:agent_bus` stream.
2. Every compliant worker (Crawler, Miner, Curator) checks for this signal every loop iteration using `bus.check_kill_switch()`.
3. Upon detection, workers immediately halt their current task and exit or enter a "Safe Mode".

### Verification
Run the automated drill:
```bash
python3 -m pytest tests/test_red_phone_kill_switch.py
```

---

## 🐒 2. Chaos Monkey (Circuit Breakers)

The **Chaos Monkey** suite tests the resilience of the RAG pipeline's circuit breakers. It simulates upstream service failures to verify that the system "fails fast" without exhausting host resources.

### Objectives
- **Fail-Fast**: Ensure requests are rejected immediately when a service is down.
- **Auto-Recovery**: Verify the circuit closes again once the service returns.
- **Resource Protection**: Prevent "Cascading Failures" where one slow service bogs down the entire stack.

### Execution
```bash
# Run the circuit breaker chaos tests
python3 -m pytest tests/test_circuit_breaker_chaos.py -v
```

### Key Parameters
- `fail_max`: 3 (Max failures before the circuit opens).
- `reset_timeout`: 60s (Time to wait before attempting recovery).

---

## 🛠️ 3. Resilience Roadmap (Milestone 4.1)
- [ ] **Forced Failover Drill**: Automated script that kills the Redis container during high-throughput ingestion.
- [ ] **Network Partition Drill**: Simulate losing the `xnai_db_network` while keeping the `ui` alive.

---
*Document sealed by Gemini General. Integrity is maintained.*
