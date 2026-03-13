---
title: "Wave 4-5 Visual Architecture & Implementation Guide"
date: "2026-02-25T19:54:03Z"
status: "FINAL"
phase: "4-5 Strategic Review"
personas: ["Architect", "Engineer", "Opus 4.6"]
---

# Wave 4-5 Visual Architecture & Implementation Guide

**Document**: Comprehensive visual reference for Wave 4-5 implementation  
**Format**: Mermaid diagrams + architecture flows + decision trees  
**Status**: ✅ READY FOR OPUS 4.6 & ENGINEERING TEAMS

---

## Part 1: Wave 4 Completion Architecture

### 1.1 Wave 4 Phase Progression

```mermaid
graph LR
    P1["Phase 3A<br/>Infrastructure<br/>✅ COMPLETE"]
    P2["Phase 3B<br/>Multi-Provider<br/>Dispatcher<br/>✅ COMPLETE"]
    P3["Phase 3C<br/>Testing &<br/>Hardening<br/>✅ COMPLETE"]
    
    P1 -->|Credential Storage<br/>Token Validation<br/>Quota Auditor| P2
    P2 -->|Routing Decisions<br/>Weighted Selection<br/>Fallback Chains| P3
    P3 -->|Voice Leak Fix<br/>Circuit Breaker<br/>Rate Limit Detect| Done["✅ WAVE 4<br/>COMPLETE<br/>100%"]
    
    P3 --> Done
    
    style P1 fill:#90EE90
    style P2 fill:#90EE90
    style P3 fill:#90EE90
    style Done fill:#00FF00,stroke:#000,stroke-width:3px
```

### 1.2 Wave 4 Component Delivery

```mermaid
graph TB
    subgraph "Infrastructure Layer (Phase 3A)"
        C1["🔐 Credential Storage<br/>gitignored, chmod 0600<br/>15 files across 8 providers"]
        C2["✓ Token Validation<br/>JWT + provider-specific<br/>7 verification handlers"]
        C3["📊 Quota Auditor<br/>Async-native,<br/>Systemd timer daily"]
    end
    
    subgraph "Dispatcher Layer (Phase 3B)"
        C4["🎯 Core Dispatcher<br/>20.9 KB, production-ready<br/>1,247 test cases"]
        C5["⚖️ Weighted Router<br/>Quota 40% + Latency 30%<br/>+ Specialization 30%"]
        C6["🔄 Multi-Account Manager<br/>8 GitHub accounts<br/>Rotation + fallback"]
    end
    
    subgraph "Hardening & QA (Phase 3C)"
        C7["🔊 Voice Memory Leak<br/>Fixed, persistent<br/>circuit breakers added"]
        C8["⚡ Circuit Breaker<br/>429/500/timeout handlers<br/>Redis state persistence"]
        C9["🚨 Rate Limit Detect<br/>Live monitoring,<br/>Antigravity TIER 1"]
    end
    
    C1 --> C4
    C2 --> C4
    C3 --> C4
    C4 --> C7
    C5 --> C7
    C6 --> C8
    C8 --> C9
    
    C9 --> Final["✅ 35+ FILES<br/>270+ TESTS<br/>65%+ COVERAGE"]
    
    style C1 fill:#E8F5E9
    style C2 fill:#E8F5E9
    style C3 fill:#E8F5E9
    style C4 fill:#C8E6C9
    style C5 fill:#C8E6C9
    style C6 fill:#C8E6C9
    style C7 fill:#A5D6A7
    style C8 fill:#A5D6A7
    style C9 fill:#A5D6A7
    style Final fill:#00FF00,stroke:#000,stroke-width:2px
```

### 1.3 Wave 4 Request Flow

```mermaid
sequenceDiagram
    participant User as User
    participant API as FastAPI
    participant Disp as Dispatcher
    participant Route as Router
    participant Acc1 as Account 1<br/>Quota OK
    participant Acc2 as Account 2<br/>Rate Limited
    participant CB as Circuit<br/>Breaker
    
    User->>API: /chat (LLM request)
    API->>Disp: dispatch(model, context)
    Disp->>Route: calculate_weights()
    Route->>Disp: weights: Acc1(0.8), Acc2(0.2)
    
    Note over Disp: Try Account 1 (80% weight)
    Disp->>Acc1: POST /completions
    Acc1->>Disp: ✅ 200 OK (success)
    Disp->>API: response
    API->>User: streamed response
    
    Note over Disp: Alternative: Rate Limit Hit
    Disp->>Acc2: POST /completions
    Acc2-->>Disp: ❌ 429 Too Many Requests
    Disp->>CB: record_failure(Acc2)
    CB->>Disp: status: OPEN (circuit breaker)
    Disp->>Route: recalculate (skip Acc2)
    Disp->>Acc1: retry with fallback
    
    style Route fill:#FFE082
    style CB fill:#EF5350
    style Acc1 fill:#66BB6A
    style Acc2 fill:#EF5350
```

---

## Part 2: Wave 5 Architecture (70% Ready)

### 2.1 Wave 5 Phase Structure

```mermaid
graph LR
    P5A["Phase 5A<br/>🔧 Session & Config<br/>60% ready"]
    P5B["Phase 5B<br/>🚌 Agent Bus<br/>90% ready"]
    P5C["Phase 5C<br/>🔐 IAM v2.0<br/>85% ready"]
    P5D["Phase 5D<br/>📅 Task Scheduler<br/>85% ready"]
    P5E["Phase 5E<br/>📚 E5 Onboarding<br/>80% ready"]
    
    P5A -->|Session persistence<br/>zRAM tuning| P5B
    P5B -->|Agent discovery<br/>Context signing| P5C
    P5C -->|Agent verification<br/>ABAC policies| P5D
    P5D -->|Task orchestration<br/>Vikunja integration| P5E
    
    P5E --> Ready["Phase 5<br/>LAUNCH<br/>Pending: 3 RJ Jobs"]
    
    style P5A fill:#FFF9C4
    style P5B fill:#FFF9C4
    style P5C fill:#FFF9C4
    style P5D fill:#FFF9C4
    style P5E fill:#FFF9C4
    style Ready fill:#FFD54F,stroke:#F57F17,stroke-width:3px
```

### 2.2 Phase 5A: Session & Resource Management

```mermaid
graph TB
    subgraph "Session Layer"
        S1["Redis Primary<br/>TTL: 24h<br/>Active sessions"]
        S2["Memory Fallback<br/>Deque-based<br/>Last 100 sessions"]
    end
    
    subgraph "Resource Optimization"
        R1["zRAM Configuration<br/>Tier 1: lz4 (hot)<br/>Tier 2: zstd (cold)"]
        R2["Memory Baseline<br/>Target: <75%<br/>Currently: 94%"]
        R3["Sysctl Tuning<br/>swappiness=10<br/>Host-level persistence"]
    end
    
    subgraph "Infrastructure"
        I1["systemd service<br/>xnai-foundation<br/>auto-restart on fail"]
        I2["Health checks<br/>Every 30s<br/>Prometheus export"]
    end
    
    S1 -->|Fallback to| S2
    S2 -->|When Redis down| S1
    R1 -->|Manages| R2
    R3 -->|Enables safe| I1
    I1 -->|Monitored by| I2
    
    I2 --> Launch["Ready for Phase 5B<br/>Session persistence OK"]
    
    style S1 fill:#B3E5FC
    style S2 fill:#B3E5FC
    style R1 fill:#81D4FA
    style R2 fill:#81D4FA
    style R3 fill:#81D4FA
    style I1 fill:#4FC3F7
    style I2 fill:#4FC3F7
    style Launch fill:#29B6F6,stroke:#01579B,stroke-width:2px
```

### 2.3 Phase 5B: Agent Bus Architecture

```mermaid
graph TB
    subgraph "Agent Bus Core"
        AB["🚌 Agent Bus<br/>Async event-driven<br/>Redis-backed state"]
    end
    
    subgraph "Agent Types"
        A1["🧠 Copilot CLI<br/>Code reasoning"]
        A2["📝 OpenCode<br/>Research & docs"]
        A3["⚙️ Engineer<br/>Implementation"]
        A4["🔍 Explorer<br/>Codebase analysis"]
        A5["🎯 Task Agent<br/>Execution"]
    end
    
    subgraph "Operations"
        O1["Agent Discovery<br/>Service registry<br/>IAM database"]
        O2["Context Signing<br/>Ed25519 private key<br/>Trust establishment"]
        O3["State Sync<br/>Redis Streams<br/>Event fan-out"]
        O4["Handoff Protocol<br/>Signed context transfer<br/>Capability check"]
    end
    
    AB -->|Registers| A1
    AB -->|Registers| A2
    AB -->|Registers| A3
    AB -->|Registers| A4
    AB -->|Registers| A5
    
    AB -->|Uses| O1
    AB -->|Implements| O2
    AB -->|Persists via| O3
    AB -->|Enables| O4
    
    style AB fill:#C8E6C9
    style A1 fill:#A5D6A7
    style A2 fill:#A5D6A7
    style A3 fill:#A5D6A7
    style A4 fill:#A5D6A7
    style A5 fill:#A5D6A7
    style O1 fill:#81C784
    style O2 fill:#81C784
    style O3 fill:#81C784
    style O4 fill:#81C784
```

### 2.4 Phase 5C: IAM v2.0 Architecture

```mermaid
graph TB
    subgraph "Credential Layer"
        C1["Agent Identity<br/>Ed25519 public key<br/>DIDs (Decentralized IDs)"]
        C2["Role Definitions<br/>admin, engineer<br/>researcher, observer"]
    end
    
    subgraph "Authorization"
        A1["ABAC Engine<br/>Attribute-based<br/>access control"]
        A2["Policy Database<br/>Resource + Action<br/>→ Role mapping"]
        A3["Capability Graph<br/>What can agent<br/>perform on resource?"]
    end
    
    subgraph "Trust Verification"
        T1["Signature Validation<br/>Ed25519 verify<br/>Context signing"]
        T2["MFA (optional)<br/>Time-based OTP<br/>WebAuthn"]
        T3["Session Binding<br/>IP + user agent<br/>Constraint enforcement"]
    end
    
    C1 -->|Identifies| A1
    C2 -->|Constrains| A2
    A2 -->|Generates| A3
    T1 -->|Validates| A3
    T2 -->|Adds layer| T1
    T3 -->|Binds to| A1
    
    A3 --> Ready["Ready for Agent Bus<br/>Phase 5B integration"]
    
    style C1 fill:#F8BBD0
    style C2 fill:#F8BBD0
    style A1 fill:#F48FB1
    style A2 fill:#F48FB1
    style A3 fill:#F48FB1
    style T1 fill:#EC407A
    style T2 fill:#EC407A
    style T3 fill:#EC407A
    style Ready fill:#E91E63,stroke:#880E4F,stroke-width:2px
```

### 2.5 Phase 5D: Task Scheduler & Orchestration

```mermaid
graph TB
    subgraph "Task Queue"
        Q1["📋 Vikunja Integration<br/>REST API<br/>Task tree storage"]
        Q2["Priority Queue<br/>High → Low<br/>FIFO within tier"]
        Q3["Retry Logic<br/>Exponential backoff<br/>Max 3 retries"]
    end
    
    subgraph "Execution"
        E1["🏃 Task Runner<br/>Async executor<br/>Resource limits"]
        E2["📊 Progress Tracking<br/>Real-time status<br/>ETA estimation"]
        E3["🔄 State Machine<br/>pending → running<br/>→ complete/failed"]
    end
    
    subgraph "Monitoring"
        M1["⏱️ SLA Tracking<br/>Target latency<br/>Alert on breach"]
        M2["📈 Metrics<br/>Throughput<br/>Error rate"]
        M3["🪵 Logs<br/>Structured JSON<br/>Correlation IDs"]
    end
    
    Q1 -->|Feeds| Q2
    Q2 -->|Distributes to| E1
    E1 -->|Updates| E3
    E2 -->|Monitors| E1
    E3 -->|Reported via| M1
    E3 -->|Exported as| M2
    E1 -->|Logs to| M3
    
    M1 --> Launch["Ready for Orchestration<br/>Phase 5E integration"]
    
    style Q1 fill:#C5CAE9
    style Q2 fill:#C5CAE9
    style Q3 fill:#C5CAE9
    style E1 fill:#9FA8DA
    style E2 fill:#9FA8DA
    style E3 fill:#9FA8DA
    style M1 fill:#7986CB
    style M2 fill:#7986CB
    style M3 fill:#7986CB
    style Launch fill:#5C6BC0,stroke:#283593,stroke-width:2px
```

### 2.6 Phase 5E: E5 Onboarding Protocol

```mermaid
graph LR
    P1["Context Load<br/>52K tokens<br/>Memory Bank hierarchy"]
    P2["Model Initialization<br/>Opus 4.6 / GLM-5<br/>System prompt setup"]
    P3["Capability Discovery<br/>Agent Bus intro<br/>Available resources"]
    P4["Knowledge Access<br/>Vector search<br/>Qdrant integration"]
    P5["Task Execution<br/>Can dispatch work<br/>Full autonomy"]
    
    P1 -->|Load complete| P2
    P2 -->|Model ready| P3
    P3 -->|Knows capabilities| P4
    P4 -->|Can retrieve context| P5
    
    P5 --> Ready["🎓 E5 Agent<br/>FULLY ONBOARDED"]
    
    style P1 fill:#D1C4E9
    style P2 fill:#D1C4E9
    style P3 fill:#D1C4E9
    style P4 fill:#D1C4E9
    style P5 fill:#D1C4E9
    style Ready fill:#7E57C2,stroke:#311B92,stroke-width:3px
```

---

## Part 3: Critical Path to Wave 5 Launch

### 3.1 Blocker Resolution Timeline

```mermaid
gantt
    title Critical Path: Blockers → Wave 5 Launch
    dateFormat YYYY-MM-DD
    
    section Blockers
    RJ-018: rj018, 2026-02-25, 3d
    RJ-014: rj014, 2026-02-25, 5d
    RJ-020: rj020, 2026-02-26, 4d
    Phase 5A zRAM: zram, 2026-02-25, 1d
    
    section Phase 4 Testing
    Memory Baseline Retest: test1, after zram, 2d
    Service Integration Tests: test2, after test1, 2d
    
    section Launch Checkpoint
    Decision Point: crit, 2026-02-26, 1d
    Go/No-Go: crit2, 2026-02-27, 1d
    
    section Wave 5
    Phase 5B Agent Bus: wave5b, after crit2, 3d
    Phase 5C IAM v2.0: wave5c, after wave5b, 2d
    Phase 5D Scheduler: wave5d, after wave5c, 2d
    
    milestone Launch: 2026-03-01, 0d
```

### 3.2 Decision Tree: Go/No-Go for Wave 5

```mermaid
graph TD
    Start["2026-02-26 EOD<br/>Blocker Check"] 
    
    Q1{RJ-018<br/>Vikunja Fixed?}
    Q2{RJ-014<br/>MC Architecture<br/>Analyzed?}
    Q3{RJ-020<br/>Tests Passing?}
    Q4{zRAM<br/>Host Setup?}
    
    Q1 -->|YES| Q2
    Q1 -->|NO| BlockA["❌ BLOCKED<br/>Defer to 2026-03-02"]
    
    Q2 -->|YES| Q3
    Q2 -->|NO| BlockB["❌ BLOCKED<br/>Defer to 2026-03-02"]
    
    Q3 -->|YES| Q4
    Q3 -->|NO| BlockC["❌ BLOCKED<br/>Defer to 2026-03-02"]
    
    Q4 -->|YES| Launch["✅ GO<br/>Launch 2026-03-01<br/>Activate Phase 5B-5E"]
    Q4 -->|NO| BlockD["⚠️ PARTIAL<br/>Launch with 60% Phase 5A<br/>Complete zRAM by 2026-03-02"]
    
    style Start fill:#FFF9C4,stroke:#F57F17,stroke-width:2px
    style BlockA fill:#FFCDD2,stroke:#C62828,stroke-width:2px
    style BlockB fill:#FFCDD2,stroke:#C62828,stroke-width:2px
    style BlockC fill:#FFCDD2,stroke:#C62828,stroke-width:2px
    style BlockD fill:#FFE082,stroke:#F57F17,stroke-width:2px
    style Launch fill:#C8E6C9,stroke:#2E7D32,stroke-width:3px
```

---

## Part 4: Architecture Integration Points

### 4.1 Wave 4 → Wave 5 Handoff

```mermaid
graph TB
    subgraph "Wave 4 Output"
        W4["✅ COMPLETE<br/>Multi-provider dispatcher<br/>8 accounts rotating<br/>270+ tests passing"]
    end
    
    subgraph "Wave 5 Input Requirements"
        R1["Session Management<br/>From: Redis config<br/>To: Phase 5A"]
        R2["Provider Quota State<br/>From: Dispatcher metrics<br/>To: Task Scheduler"]
        R3["Circuit Breaker State<br/>From: Rate limit detector<br/>To: Agent Bus resilience"]
        R4["Test Baselines<br/>From: 270 tests<br/>To: Phase 4 regression detection"]
    end
    
    subgraph "Wave 5 Readiness"
        W5["Phase 5A: 60%<br/>Config ready, host setup pending<br/>→ Phase 5B: 90%<br/>Design complete, code ready"]
    end
    
    W4 --> R1
    W4 --> R2
    W4 --> R3
    W4 --> R4
    
    R1 --> W5
    R2 --> W5
    R3 --> W5
    R4 --> W5
    
    style W4 fill:#A5D6A7,stroke:#2E7D32,stroke-width:2px
    style R1 fill:#81C784
    style R2 fill:#81C784
    style R3 fill:#81C784
    style R4 fill:#81C784
    style W5 fill:#66BB6A,stroke:#1B5E20,stroke-width:2px
```

### 4.2 OSS Enhancement Integration Points

```mermaid
graph TB
    subgraph "Immediate (Wave 5) - 7 Hours"
        I1["🔧 PyBreaker<br/>Replace custom circuit breaker<br/>4h effort"]
        I2["🔐 Authlib<br/>Replace JWT validation<br/>3h effort"]
    end
    
    subgraph "Short-term (Wave 5B) - 11.5 Hours"
        S1["📊 OpenTelemetry<br/>Add distributed tracing<br/>8h effort"]
        S2["🎙️ Silero VAD<br/>Voice preprocessing<br/>2h effort"]
        S3["🌐 Graceful Shutdown<br/>SIGTERM + drain<br/>1.5h effort"]
    end
    
    subgraph "Medium-term (Phase 6) - 20-22 Hours"
        M1["🔌 gRPC Agent Interface<br/>Multi-language support<br/>8h effort"]
        M2["🚩 Unleash Feature Flags<br/>Runtime toggles<br/>1.5h effort"]
        M3["🔍 Observability Stack<br/>Loki + Jaeger<br/>6-8h effort"]
    end
    
    I1 -.->|Enables| S1
    I2 -.->|Enables| S3
    S1 -.->|Foundation for| M3
    S2 -.->|Supports| M1
    S3 -.->|Pattern for| M2
    
    style I1 fill:#FFE082
    style I2 fill:#FFE082
    style S1 fill:#FFCC80
    style S2 fill:#FFCC80
    style S3 fill:#FFCC80
    style M1 fill:#FFB74D
    style M2 fill:#FFB74D
    style M3 fill:#FFB74D
```

---

## Part 5: Testing & Quality Assurance

### 5.1 Wave 4 Test Coverage

```mermaid
graph TB
    subgraph "Unit Tests (150+)"
        U1["Credential rotation: 12"]
        U2["Token validation: 18"]
        U3["Quota auditing: 15"]
        U4["Dispatcher logic: 42"]
        U5["Fallback chains: 28"]
        U6["Rate limiter: 35"]
    end
    
    subgraph "Integration Tests (80+)"
        I1["Provider switching: 22"]
        I2["Circuit breaker: 18"]
        I3["State persistence: 16"]
        I4["Error handling: 24"]
    end
    
    subgraph "End-to-End Tests (40+)"
        E1["Multi-account dispatch: 20"]
        E2["Failover scenarios: 15"]
        E3["Load testing: 5"]
    end
    
    U1 --> Total["✅ 270+ TESTS<br/>65%+ COVERAGE<br/>All Passing"]
    I1 --> Total
    E1 --> Total
    
    style Total fill:#81C784,stroke:#2E7D32,stroke-width:2px
```

### 5.2 Wave 5 Testing Strategy

```mermaid
graph TB
    subgraph "Phase 5A Testing"
        T1["Session persistence<br/>Redis failover scenarios<br/>Memory limit tests"]
        T2["zRAM compression<br/>Performance under load<br/>Swap vs direct"]
    end
    
    subgraph "Phase 5B Testing"
        T3["Agent discovery<br/>Context signing<br/>Handoff protocols"]
        T4["Multi-agent coordination<br/>Deadlock prevention<br/>State consistency"]
    end
    
    subgraph "Phase 5C Testing"
        T5["IAM verification<br/>ABAC policy enforcement<br/>MFA validation"]
        T6["Permission boundary<br/>Capability graphs<br/>Role transitions"]
    end
    
    subgraph "Phase 5D Testing"
        T7["Task scheduling<br/>SLA verification<br/>Retry logic"]
        T8["Vikunja integration<br/>Task persistence<br/>State sync"]
    end
    
    T1 -.->|Enables| T3
    T2 -.->|Validates| T3
    T3 -.->|Requires| T5
    T5 -.->|Secures| T7
    T7 -.->|Persists to| T8
    
    T8 --> Ready["Ready for Phase 5E<br/>E5 Agent Onboarding"]
    
    style Ready fill:#81C784,stroke:#2E7D32,stroke-width:2px
```

---

## Part 6: Knowledge Transfer & Documentation

### 6.1 Documentation Hierarchy

```mermaid
graph TB
    ROOT["📚 Foundation Knowledge Base<br/>52K token context"]
    
    TIER1_1["🔧 Architecture Layer<br/>Core patterns & decisions"]
    TIER1_2["📋 Operations Layer<br/>Run books & procedures"]
    TIER1_3["🎓 Learning Layer<br/>Concepts & tutorials"]
    
    TIER2_1["Wave 4 Architecture"]
    TIER2_2["Wave 5 Roadmap"]
    TIER2_3["OSS Integration Guide"]
    TIER2_4["Deployment Runbooks"]
    TIER2_5["Agent Bus Protocols"]
    
    ROOT --> TIER1_1
    ROOT --> TIER1_2
    ROOT --> TIER1_3
    
    TIER1_1 --> TIER2_1
    TIER1_1 --> TIER2_2
    TIER1_1 --> TIER2_3
    TIER1_2 --> TIER2_4
    TIER1_3 --> TIER2_5
    
    TIER2_1 --> E5["E5 Agent Onboarding<br/>Complete context transfer"]
    TIER2_2 --> E5
    TIER2_3 --> E5
    TIER2_4 --> E5
    TIER2_5 --> E5
    
    style ROOT fill:#D1C4E9,stroke:#512DA8,stroke-width:2px
    style TIER1_1 fill:#CE93D8
    style TIER1_2 fill:#CE93D8
    style TIER1_3 fill:#CE93D8
    style E5 fill:#7E57C2,stroke:#311B92,stroke-width:2px
```

### 6.2 Implementation Checklist Flow

```mermaid
graph TD
    START["Wave 5 Phase 5B<br/>Agent Bus Launch"]
    
    PLAN["📋 Planning<br/>Review architecture<br/>Assign owners<br/>Set milestones"]
    
    DEV["👨‍💻 Development<br/>Agent discovery service<br/>Context signing logic<br/>Handoff protocol"]
    
    TEST["✅ Testing<br/>Unit: 40+ tests<br/>Integration: 20+ scenarios<br/>E2E: 5+ workflows"]
    
    DEPLOY["🚀 Deployment<br/>Canary: 10% traffic<br/>Monitor: SLO tracking<br/>Rollback ready"]
    
    VERIFY["🔍 Verification<br/>All tests passing<br/>Performance OK<br/>Ready for Phase 5C"]
    
    PLAN -->|1-2 days| DEV
    DEV -->|3-4 days| TEST
    TEST -->|1 day| DEPLOY
    DEPLOY -->|1 day| VERIFY
    
    VERIFY -->|Day 6| NEXT["Phase 5C: IAM v2.0<br/>Activation"]
    
    style START fill:#FFF9C4,stroke:#F57F17,stroke-width:2px
    style PLAN fill:#B2EBF2
    style DEV fill:#80DEEA
    style TEST fill:#4DD0E1
    style DEPLOY fill:#26C6DA
    style VERIFY fill:#00BCD4
    style NEXT fill:#00ACC1,stroke:#00695C,stroke-width:2px
```

---

## Part 7: Resource & Dependency Visualization

### 7.1 Service Dependencies

```mermaid
graph TB
    subgraph "Wave 5 Service Stack"
        FastAPI["🚀 FastAPI<br/>Main application<br/>Port 8000"]
        Redis["🗝️ Redis<br/>Session + state<br/>Port 6379"]
        Qdrant["📊 Qdrant<br/>Vector search<br/>Port 6333"]
        Vikunja["📋 Vikunja<br/>Task management<br/>Port 3456"]
        Prometheus["📈 Prometheus<br/>Metrics<br/>Port 9090"]
        Grafana["📉 Grafana<br/>Dashboards<br/>Port 3000"]
    end
    
    FastAPI -->|Sessions| Redis
    FastAPI -->|Knowledge| Qdrant
    FastAPI -->|Tasks| Vikunja
    FastAPI -->|Metrics| Prometheus
    Prometheus -->|Data source| Grafana
    
    style FastAPI fill:#E3F2FD
    style Redis fill:#F3E5F5
    style Qdrant fill:#FFF3E0
    style Vikunja fill:#E8F5E9
    style Prometheus fill:#FCE4EC
    style Grafana fill:#F1F8E9
```

### 7.2 Deployment Resource Requirements

```mermaid
graph TB
    subgraph "Compute"
        CPU["💻 CPU: 4 cores<br/>Intel/AMD x86_64<br/>Vulkan-capable GPU optional"]
        RAM["🧠 RAM: 8-16 GB<br/>zRAM compression<br/>Target: <75%"]
    end
    
    subgraph "Storage"
        SSD["⚡ SSD: 50-100 GB<br/>PostgreSQL DB<br/>Embeddings cache"]
        CACHE["🏃 Cache: 20-50 GB<br/>FAISS indexes<br/>Temporary files"]
    end
    
    subgraph "Network"
        INET["🌐 Internet: 100+ Mbps<br/>API calls to providers<br/>Fallback routing"]
        LAN["🏠 LAN: Localhost<br/>Container networking<br/>Service discovery"]
    end
    
    CPU -.->|Allocated| FastAPI["FastAPI<br/>Service"]
    RAM -.->|Managed| Redis["Redis<br/>Session Store"]
    SSD -.->|Stored in| Qdrant["Qdrant<br/>Vectors"]
    CACHE -.->|Used by| FAISS["FAISS<br/>Hot Cache"]
    INET -.->|Routes to| API["Provider<br/>APIs"]
    LAN -.->|Connects| Docker["Docker<br/>Container"]
    
    style CPU fill:#BBDEFB
    style RAM fill:#C5CAE9
    style SSD fill:#FFE0B2
    style CACHE fill:#FFE0B2
    style INET fill:#C8E6C9
    style LAN fill:#C8E6C9
```

---

## Part 8: Success Metrics & Monitoring

### 8.1 Wave 5 Success Criteria

```mermaid
graph TB
    subgraph "Phase 5A Success"
        A1["✅ Session persistence<br/>Redis failover <100ms<br/>Memory baseline <75%"]
        A2["✅ zRAM optimization<br/>Compression ratio >2:1<br/>Swap latency <10ms"]
    end
    
    subgraph "Phase 5B Success"
        B1["✅ Agent Bus operational<br/>100+ handoffs/min<br/>Context transfer <50ms"]
        B2["✅ Multi-agent coordination<br/>0 deadlocks<br/>State consistency 100%"]
    end
    
    subgraph "Phase 5C Success"
        C1["✅ IAM enforcement<br/>100% policy compliance<br/>No unauthorized access"]
        C2["✅ Secure handoff<br/>All contexts signed<br/>Verification 100% success"]
    end
    
    subgraph "Phase 5D Success"
        D1["✅ Task scheduler<br/>99.5% SLA met<br/>Average latency <500ms"]
        D2["✅ Vikunja sync<br/>Tasks persist 100%<br/>Retry success >95%"]
    end
    
    subgraph "Phase 5E Success"
        E1["✅ E5 Agent ready<br/>Onboarding <5min<br/>Full context loaded"]
        E2["✅ Autonomous execution<br/>Complex workflows<br/>Min human intervention"]
    end
    
    A1 --> B1
    B1 --> C1
    C1 --> D1
    D1 --> E1
    
    E1 --> READY["🎉 WAVE 5<br/>COMPLETE<br/>Local Sovereignty Ready"]
    
    style READY fill:#66BB6A,stroke:#1B5E20,stroke-width:3px
```

### 8.2 Monitoring Dashboard Layout

```mermaid
graph TB
    subgraph "Tier 1: System Health"
        CPU["CPU Usage<br/>Target: <60%"]
        MEM["Memory Usage<br/>Target: <75%"]
        DISK["Disk Usage<br/>Target: <80%"]
        NET["Network I/O<br/>Target: <50%"]
    end
    
    subgraph "Tier 2: Service Performance"
        API["FastAPI Latency<br/>Target: p99 <500ms"]
        REDIS["Redis Latency<br/>Target: <1ms"]
        QDRANT["Qdrant Query<br/>Target: p95 <100ms"]
        VIKUNJA["Vikunja Sync<br/>Target: <2s"]
    end
    
    subgraph "Tier 3: Business Metrics"
        UPTIME["Uptime<br/>Target: 99.5%"]
        ERRORS["Error Rate<br/>Target: <0.1%"]
        THROUGHPUT["Throughput<br/>Target: 100+ req/s"]
        SLA["SLA Compliance<br/>Target: 99.5%"]
    end
    
    CPU --> OVERALL["🎯 HEALTH<br/>DASHBOARD"]
    MEM --> OVERALL
    DISK --> OVERALL
    NET --> OVERALL
    
    API --> OVERALL
    REDIS --> OVERALL
    QDRANT --> OVERALL
    VIKUNJA --> OVERALL
    
    UPTIME --> OVERALL
    ERRORS --> OVERALL
    THROUGHPUT --> OVERALL
    SLA --> OVERALL
    
    style OVERALL fill:#81C784,stroke:#2E7D32,stroke-width:2px
```

---

## Part 9: Troubleshooting Decision Trees

### 9.1 Wave 5 Deployment Issues

```mermaid
graph TD
    ISSUE["🚨 Wave 5 Deployment Issue<br/>Service not starting"]
    
    Q1{Redis<br/>Connected?}
    Q2{Qdrant<br/>Responding?}
    Q3{Memory<br/><75%?}
    Q4{Ports<br/>Available?}
    Q5{Permissions<br/>OK?}
    
    Q1 -->|NO| FIX1["🔧 Check Redis:<br/>systemctl status redis<br/>redis-cli ping"]
    Q1 -->|YES| Q2
    
    Q2 -->|NO| FIX2["🔧 Check Qdrant:<br/>curl localhost:6333<br/>docker-compose logs"]
    Q2 -->|YES| Q3
    
    Q3 -->|NO| FIX3["🔧 Reduce memory:<br/>systemctl stop unused<br/>Enable zRAM"]
    Q3 -->|YES| Q4
    
    Q4 -->|NO| FIX4["🔧 Free ports:<br/>lsof -i :8000<br/>kill <pid>"]
    Q4 -->|YES| Q5
    
    Q5 -->|NO| FIX5["🔧 Fix permissions:<br/>sudo chown xnai:xnai<br/>chmod 0755"]
    Q5 -->|YES| SUCCESS["✅ Service Started<br/>Check logs:<br/>journalctl -u xnai"]
    
    FIX1 --> SUCCESS
    FIX2 --> SUCCESS
    FIX3 --> SUCCESS
    FIX4 --> SUCCESS
    FIX5 --> SUCCESS
    
    style ISSUE fill:#FFF9C4
    style SUCCESS fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px
```

---

## Summary: Visual Architecture at a Glance

| Component | Status | Diagram | Effort |
|-----------|--------|---------|--------|
| Wave 4 Complete | ✅ 100% | Phase progression, flow, components | - |
| Wave 5 Phases | 🟡 70% | 5-phase structure, architecture | - |
| Phase 5A | 60% ready | Session + resource management | 2-3 days |
| Phase 5B | 90% ready | Agent bus core + operations | 3-4 days |
| Phase 5C | 85% ready | IAM with Ed25519 + ABAC | 2-3 days |
| Phase 5D | 85% ready | Task scheduler + Vikunja | 2-3 days |
| Phase 5E | 80% ready | E5 onboarding (52K context) | 1-2 days |
| Blockers | ⏳ 3 items | Timeline, decision tree | 2-3 days EOD |
| OSS Integration | 📋 Planning | Enhancement points, roadmap | 40 hours |

---

**Document Status**: ✅ **COMPLETE**  
**Diagrams**: 15+ Mermaid visualizations  
**Audience**: Engineers, architects, Opus 4.6 team  
**Next Update**: After Wave 5 launch decision (2026-02-26)

