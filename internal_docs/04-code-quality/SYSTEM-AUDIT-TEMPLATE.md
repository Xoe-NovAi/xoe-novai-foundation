# XNAi System Audit Template (v1.0)
## Agent: {Agent Name} | Date: {Date} | Target: {Subsystem}

### 1. Functional Verification
- [ ] Service is reachable (HTTP/TCP).
- [ ] Core API endpoints responding.
- [ ] Authentication/Authorization operational.
- [ ] Persistent storage verified (DB/Filesystem).

### 2. Integration Status
- [ ] **Redis**: Connected (Persistence/Streams/Caching).
- [ ] **Consul**: Registered (Health/Metadata).
- [ ] **IAM**: Identity verified via Sovereign Handshake.
- [ ] **Cross-Service**: Upstream/Downstream dependencies healthy.

### 3. Hardware Alignment (Ryzen 7 5700U)
- [ ] Memory footprint within quota.
- [ ] CPU utilization baseline recorded.
- [ ] IO latency within acceptable bounds (WAL/MMAP check).

### 4. Knowledge Gaps & Risks
- List any undocumented patterns or legacy code debt.
- Identify blockers for upcoming implementations (e.g., Qdrant readiness).

### 5. Recommendations
- Immediate fixes required.
- Optimization opportunities.
- Phase alignment check.
