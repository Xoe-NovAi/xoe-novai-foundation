# Phase 4.2 Implementation Plan: Sovereign Trinity Hardening

**Version:** 1.0  
**Date:** 2026-02-15  
**Owner:** Gemini CLI (Orchestrator) / Cline (Engineer)

## Executive Summary
Implementation of service discovery (Consul), tiered degradation (resource-aware), and query transaction logging (Redis Streams) to harden the Sovereign Trinity pipeline on the Ryzen 7 5700U host.

---

## Phase 4.2.1: Infrastructure (Consul)
**Goal:** Deploy a functional Consul registry in rootless Podman.

- [x] **Task 1:** Update `docker-compose.yml` with `consul` service.
  - Image: `consul:1.15.4` (stable)
  - Ports: 8500 (HTTP), 8600 (DNS)
  - Networking: `slirp4netns:mtu=1500` optimization.
- [x] **Task 2:** Configure Consul persistence in `data/consul`.
- [x] **Task 3:** Verify Consul UI access via `http://localhost:8500`.

---

## Phase 4.2.2: Service Registration & Health [COMPLETE]
**Goal:** Auto-register services and monitor health.

- [x] **Task 1:** Implement `app/XNAi_rag_app/core/consul_client.py`.
  - Service registration with TTL health checks.
  - DNS resolution utility.
- [x] **Task 2:** Integrate with `services_init.py`.
  - Register `rag-api`.
- [x] **Task 3:** Standardize `/health` endpoints.
  - Ensure all services return 200 OK and basic metadata.

---

## Phase 4.2.3: Tiered Degradation (Ma'at-Aligned)
**Goal:** Graceful failure under memory pressure (6.6GB host).

- [ ] **Task 1:** Create `app/XNAi_rag_app/core/degradation.py`.
  - `DegradationTierManager` (Polls `psutil`).
  - Tiers: 1 (Full), 2 (Reduced Context), 3 (Cache-only), 4 (Read-only).
- [ ] **Task 2:** Redis Streams Signaling.
  - Broadcast tier changes to `xnai_degradation` stream.
- [ ] **Task 3:** Application Adaptation.
  - RAG API: Reduce context window on Tier 2+.
  - Voice: Switch to "Small" Whisper on Tier 3.

---

## Phase 4.2.4: Query Transaction Log (QTL)
**Goal:** Audit trail and crash recovery for query flows.

- [ ] **Task 1:** Implement `QueryTransactionLog` middleware.
  - Append to `xnai_queries` Redis Stream.
  - Fields: `txn_id`, `status`, `duration`, `model_used`.
- [ ] **Task 2:** Idempotency Logic.
  - Check Redis cache for `txn_id` before processing.

---

## Phase 4.2.5: Verification & Chaos
**Goal:** Validate hardening.

- [ ] **Task 1:** `tests/integration/test_consul_discovery.py`.
- [ ] **Task 2:** `tests/chaos/test_memory_pressure.py`.
  - Simulate 95%+ RAM usage and verify Tier 3 transition.
- [ ] **Task 3:** Final Latency Benchmark.
  - Target: <2.5s end-to-end voice latency at Tier 1.

---

## Success Criteria
1.  **Zero OOMs** during 10-query concurrent burst.
2.  **Auto-recovery** within 30s of a service crash.
3.  **Full Audit Trail** for every query in Redis.
