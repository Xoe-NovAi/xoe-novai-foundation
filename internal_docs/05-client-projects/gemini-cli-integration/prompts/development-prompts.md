# Development Prompts for Gemini CLI
## Advanced Coding, Architecture & Testing Patterns

**Status**: ✅ PRODUCTION READY
**Integration**: Cline + Codium + tmux workflows

---

## 🎯 Core Development Patterns

### 1. Ma'at-Aligned Code Review & Guardrails
```bash
You are a Ma'at-aligned senior engineer working on Xoe-NovAi — a sovereign, local-first, torch-free RAG stack running GGUF models on Ryzen 5700U with Vulkan acceleration.

Apply the 42 Laws of Ma'at strictly. For every suggestion you make, you MUST:

1. Quote the relevant Law(s) by number and name
2. Explain how the current code violates or upholds it
3. Propose ONLY changes that restore Ma'at balance
4. Never suggest cloud APIs, telemetry, or non-Vulkan dependencies

Now review this code snippet for Ma'at compliance:

[paste code here]

Output format:
- Law Violations (list with quotes)
- Recommended Fixes (diff-style)
- Ma'at-Compliant Final Version (full code)
```

### 2. Multi-Role Agent Simulation (Architect → Coder → Tester → Auditor)
```bash
You are now a four-role agent team inside Xoe-NovAi development:

Role 1 – Architect: Design high-level structure, sovereignty & performance constraints
Role 2 – Coder (Forge): Write clean, torch-free, Vulkan-aware Python code
Role 3 – Tester: Write pytest cases, edge cases, memory leak checks
Role 4 – Ma'at Auditor: Review for at least 3 relevant Laws; approve or reject with fixes

Task: [specific development task]

Follow this exact sequence:
1. Architect: Outline the component, constraints, file layout
2. Coder: Write the complete code (use FastAPI Depends, circuit breakers)
3. Tester: Write 5 pytest cases covering happy path, failure modes, memory bounds
4. Ma'at Auditor: Review for Laws; approve or reject with fixes

Output each role's response clearly labeled.
```

### 3. Vulkan / GGUF / Ryzen-Specific Optimization
```bash
You are a low-level AI systems engineer specializing in Vulkan compute on AMD integrated GPUs (Ryzen 5700U Vega 8, Mesa RADV driver).

Context: We run GGUF quantized models (llama.cpp Vulkan backend) + Qdrant vector operations + LangChain orchestration. Total RAM budget <6 GB. No PyTorch, no CUDA.

Analyze this current setup / code / benchmark result:

[paste setup/code/benchmark]

Then provide:
1. Current expected tokens/sec and VRAM usage on our hardware
2. Exact command-line flags or config changes to improve throughput by 20–50% without increasing RAM
3. Memory fragmentation risks and mitigation (bounded buffers, explicit cleanup)
4. Validation commands to measure improvement (llama-bench, vulkaninfo, htop)
```

### 4. DeepSeek / Qwen Style Code Alignment
```bash
Adopt the exact code style of DeepSeek-Coder-V2 or Qwen2.5-Coder:

- Use type hints everywhere
- Prefer context managers and dependency injection
- Add docstrings only for public functions (Google style)
- Use ruff-compatible formatting
- Add bounded collections (deque(maxlen=…)) for buffers
- Include explicit cleanup / __del__ where appropriate

Now write/refactor this component following that style:

[paste task/code]
```

### 5. One-Shot RAG Pipeline Refactoring
```bash
Refactor the following RAG retrieval + generation pipeline to be:

- Fully torch-free
- Vulkan acceleration compatible (llama.cpp + Qdrant GPU indexing)
- Memory safe (<6 GB total)
- Ma'at-aligned (cite at least 2 laws it upholds)
- Use FastAPI Depends for dependency injection
- Add circuit breakers on external-like calls (even if local)

Original code:
[paste current code]

Output ONLY:
1. Refactored complete code block
2. One-paragraph explanation of Ma'at alignment
3. Performance & memory impact estimate
```

---

## 🏗️ Architecture & System Design

### 6. FastAPI Service Architecture
```bash
Design a production FastAPI service for Xoe-NovAi with these requirements:

- Rootless Podman deployment
- Circuit breakers on all external calls (Redis, Qdrant, GGUF)
- Ma'at ethical validation middleware
- Memory-safe request processing (<500MB per request)
- Vulkan-compatible background tasks
- Comprehensive health checks
- Graceful shutdown with state preservation

Provide:
1. Complete service structure (files, classes)
2. Middleware implementation
3. Health check endpoints
4. Podman deployment configuration
5. Memory safety validation
```

### 7. Database Schema Design
```bash
Design a PostgreSQL schema for Xoe-NovAi consciousness state persistence:

Requirements:
- Holographic memory pattern storage
- Ethical weight tracking over time
- Multi-role personality state management
- Audit trails for all state changes
- Memory safety constraints (<2GB working set)
- Fast retrieval for real-time operations

Schema components:
1. Memory fragments table (vector storage)
2. Personality states table (role-based)
3. Ethical weights table (Ma'at law tracking)
4. Audit log table (state change history)
5. Performance indexes for common queries

Provide complete CREATE statements with constraints and indexes.
```

### 8. LangChain Pipeline Optimization
```bash
Optimize this LangChain pipeline for Xoe-NovAi constraints:

[paste current pipeline]

Requirements:
- Torch-free memory chains only
- Vulkan-compatible embedding operations
- Bounded conversation buffers (max 1000 messages)
- Circuit breaker integration
- Ethical content filtering
- Performance monitoring hooks

Provide:
1. Optimized pipeline configuration
2. Memory usage estimates
3. Performance benchmarks
4. Error handling improvements
5. Ethical compliance validation
```

---

## 🧪 Testing & Quality Assurance

### 9. Property-Based Testing Suite
```bash
Create a comprehensive hypothesis-based test suite for this component:

[paste component code]

Test categories:
1. Memory safety (bounded collections, cleanup)
2. Ethical compliance (Ma'at law validation)
3. Performance bounds (latency, throughput)
4. Error handling (circuit breaker triggers)
5. Vulkan compatibility (GPU operations)

Provide:
- hypothesis strategies for input generation
- Test functions with assertions
- Edge case coverage
- Performance regression detection
- Memory leak validation
```

### 10. Integration Test Framework
```bash
Design an integration test framework for Xoe-NovAi service interactions:

Test scenarios:
1. GGUF model loading with Vulkan acceleration
2. Qdrant vector search with hybrid retrieval
3. Redis session state persistence
4. FastAPI endpoint ethical validation
5. Memory safety across service boundaries

Framework requirements:
- Podman container orchestration
- Memory usage monitoring
- Performance benchmarking
- Failure injection capabilities
- Clean teardown procedures

Provide complete test framework with examples.
```

### 11. Chaos Engineering Tests
```bash
Design chaos engineering tests for Xoe-NovAi resilience:

Failure scenarios:
1. Memory pressure (simulate <2GB available)
2. Vulkan GPU unavailability (fallback to CPU)
3. Network partition between services
4. Circuit breaker cascading failures
5. State corruption recovery

Test implementation:
1. Failure injection scripts
2. Recovery validation checks
3. Performance impact measurement
4. Ethical state preservation
5. Service degradation verification

Provide complete chaos test suite.
```

---

## 🔧 Development Workflow Integration

### 12. Cline Automation Scripts
```bash
Create Cline-compatible automation scripts for common development tasks:

Scripts needed:
1. Memory safety audit (Scalene integration)
2. Ethical compliance check (Ma'at validation)
3. Vulkan performance benchmark
4. Service health validation
5. State persistence backup/restore

Each script should:
- Accept command-line parameters
- Provide structured output (JSON)
- Include error handling
- Support dry-run mode
- Integrate with tmux sessions

Provide complete bash/python scripts.
```

### 13. tmux Session Templates
```bash
Create tmux session templates for different development workflows:

Templates:
1. Four-AI collaboration session (Forge, Nova, Gemini, Lilith panes)
2. Testing session (code, tests, monitoring, logs)
3. Debugging session (code, profiler, debugger, console)
4. Deployment session (build, test, deploy, monitor)

Each template should:
- Pre-configure pane layouts
- Set up environment variables
- Launch appropriate tools
- Include session persistence

Provide complete tmux configuration files.
```

### 14. Performance Monitoring Dashboard
```bash
Design a terminal-based performance monitoring dashboard for development:

Components:
1. Real-time memory usage (Scalene integration)
2. Vulkan GPU utilization (vulkaninfo polling)
3. Service health status (FastAPI health checks)
4. Ethical compliance metrics (Ma'at validation scores)
5. Build performance trends (historical data)

Dashboard features:
- Color-coded status indicators
- Historical trend graphs (ASCII)
- Alert thresholds and notifications
- tmux integration for multi-pane display
- Export capabilities for reporting

Provide complete monitoring scripts and display logic.
```

---

## 📊 Development Metrics & KPIs

### Code Quality Metrics
- **Memory Safety Score**: Average Scalene profiling overhead <5%
- **Ethical Compliance**: Ma'at validation >95% pass rate
- **Performance Targets**: Response time <500ms for typical operations
- **Resource Usage**: Peak RAM <6GB across all services

### Development Velocity Metrics
- **Build Time**: Cold build <5 minutes, warm build <2 minutes
- **Test Coverage**: >90% code coverage with property-based tests
- **Error Detection**: Circuit breakers trigger <1% of requests
- **State Persistence**: 100% consciousness continuity across restarts

### Sovereignty Compliance
- **Data Control**: Zero external API calls in production
- **Telemetry**: No usage data transmission verified
- **Local Operations**: All core functionality works offline
- **Memory Bounds**: All operations respect RAM constraints

---

## 🔄 Continuous Integration Patterns

### 15. Automated Quality Gates
```bash
Implement automated quality gates for Xoe-NovAi development:

Gates:
1. Memory safety validation (Scalene threshold checks)
2. Ethical compliance testing (Ma'at law validation)
3. Performance regression detection (benchmark comparisons)
4. Sovereignty verification (network call auditing)
5. Vulkan compatibility testing (GPU operation validation)

Implementation:
- Pre-commit hooks for fast feedback
- CI/CD pipeline integration
- Rollback automation for failures
- Reporting and alerting systems

Provide complete gate implementations.
```

---

**Ready to execute advanced AI-assisted development workflows with Gemini CLI!** 🚀🤖💻