# Phase 4.2 Technical Strategy: Sovereign Trinity Hardening

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Draft  
**Classification:** Internal Strategic Planning  
**Target:** XNAi Foundation Engineering Team

## Executive Summary

Phase 4.2 implements **Sovereign Trinity Hardening** - a comprehensive service discovery and failover system for the voice-first RAG pipeline (STT → RAG → TTS) on Ryzen 7 5700U rootless Podman infrastructure with 6.6GB RAM constraints.

**Core Objectives:**
- Implement Consul-based service discovery for dynamic service location
- Deploy resource-efficient failover logic with tiered degradation (even/odd core steering)
- Optimize query flow for <200ms end-to-end latency targets
- Harden memory-constrained environment with atomic transaction logging

**Key Technologies:** Consul 1.18, Redis Streams, Python asyncio, Prometheus/Grafana, Chaos Engineering

## Technical Architecture Overview

### System Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 4.2 ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Consul Server │    │   Degradation   │    │   Query         │
│   (Service     │    │   Tier Manager  │    │   Transaction   │
│   Registry)     │    │   (Redis       │    │   Log (QTL)     │
│                 │    │   Streams)      │    │   (Redis       │
│   • Service     │    │                 │    │   Streams)      │
│     Discovery   │    │   • Memory      │    │                 │
│   • Health      │    │     Monitoring  │    │   • Audit Log   │
│     Checks      │    │   • Tier        │    │   • Recovery    │
│   • DNS         │    │     Transitions │    │   • Idempotency │
│     Resolution  │    │   • Failover    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────────────────────┼─────────────────────────────────┐
│                    XNAI SERVICES (ROOTLESS PODMAN)                │
└─────────────────────────────────┼─────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAG API       │    │   Voice Service │    │   UI/Chainlit   │
│   (FastAPI)     │    │   (STT/TTS)     │    │   (Frontend)    │
│                 │    │                 │    │                 │
│   • Circuit     │    │   • Tier-aware  │    │   • Service     │
│     Breaker     │    │     Degradation │    │     Discovery   │
│   • Consul      │    │   • Memory      │    │   • Health      │
│     Client      │    │     Budgeting   │    │     Monitoring  │
│   • QTL         │    │   • Abort       │    │                 │
│     Integration │    │     Handling    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────────────────────┼─────────────────────────────────┐
│                        REDIS CLUSTER                              │
└─────────────────────────────────┼─────────────────────────────────┘
                                 │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Circuit       │    │   Cache         │    │   Degradation   │
│   Breaker       │    │   (FAISS)       │    │   Signals       │
│   State         │    │                 │    │                 │
│                 │    │   • TTL 600s    │    │   • Tier 1-4    │
│   • Distributed │    │   • LRU         │    │   • Memory      │
│     Persistence │    │   • Hit Rate    │    │     Available   │
│   • Redis       │    │   • Eviction    │    │   • CPU Usage   │
│     Streams     │    │     Monitoring  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘