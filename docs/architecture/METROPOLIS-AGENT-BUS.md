# 📡 Metropolis Agent Bus Routing

**Version**: 1.0 (Hardened)  
**Coordination Key**: `METROPOLIS-BUS-2026`

## 🌌 Overview
The **Agent Bus** is the central nervous system of the Omega Stack. In the Metropolis implementation, it facilitates asynchronous communication between isolated technical domains.

---

## 📊 Bus Routing Flow

The following diagram shows how a task is routed from a generic agent to a specific technical expert cluster.

```mermaid
flowchart TD
    Sender[External Agent / UI] -- "1. Post Task to Redis Stream" --> Bus[(xnai:agent_bus)]
    
    subgraph "Metropolis Nervous System"
        Bus -- "2. Fetch Task" --> Broker[Metropolis Broker]
        Broker -- "3. Resolve Domain Cluster" --> Resolver{Domain Registry}
        
        Resolver -- "ID: 1" --> Arch[Architect Cluster]
        Resolver -- "ID: 2" --> API[API Cluster]
        Resolver -- "ID: N" --> Other[Other Domains...]
    end
    
    subgraph "Domain Execution (Isolated)"
        Arch -- "Headless Dispatch" --> G1[Gemini Prime]
        G1 -- "Sub-dispatch" --> S1[SambaNova Sub]
    end
    
    S1 -- "4. Result to Broker" --> Broker
    Broker -- "5. Post Response to Bus" --> Bus
    Bus -- "6. Delivery" --> Sender
```

---

## 🧬 Routing Protocols

1.  **Targeting**: Tasks must be tagged with `expert:[domain]:[level]`.
2.  **Acknowledgment**: The Broker acknowledges the task immediately upon receipt to prevent duplicate processing.
3.  **Persistence**: If an expert cluster is offline, the task remains in the stream (PEL - Pending Entries List) until the cluster returns.

---
**Custodian**: Gemini CLI (MC-Overseer)  
**Verification Key**: `OMEGA-BUS-FLOW-2026-03-04`
