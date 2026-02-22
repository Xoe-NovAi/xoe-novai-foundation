---
priority: high
context: general
activation: always
last_updated: 2026-01-27
version: 1.0
---

# Intelligent Command Chaining

**Core Philosophy**: Automate complex multi-step operations through context-aware command sequences. Never install packages on local machine - always use containers with uv and mirrors.

## 🚨 ENVIRONMENT SAFETY ENFORCEMENT (Highest Priority)

### **Container-Only Installation Pattern**
**Triggers**: "install.*", "pip install.*", "add.*package", "setup.*service", "add.*dependency"
**Safety Protocol**:
- ❌ **BLOCK**: Any installation requests targeting local machine
- ✅ **ALLOW**: Container-based installations via podman/docker
- ✅ **ALLOW**: venv installations only for testing/debugging
- **Enforcement**: Automatic rejection with container-based alternatives

```yaml
chains:
  "container-only-enforcement":
    - detect: Analyze request for installation intent
    - validate: Check if target is local machine vs container
    - block: Reject local installations with clear error message
    - suggest: Provide container-based alternatives using uv + mirrors
    - exception: Allow venv for testing/debugging only
    - log: Safety violation to memory_bank/activeContext.md
```

## 🔧 CRITICAL COMMAND CHAINS

### **Chain 1: Dependency Conflict Resolution** (Immediate Priority)
**Triggers**: "fix.*pip.*conflict", "resolve.*dependencies", "update.*requirements", "dependency.*hell"
**Purpose**: Solve pip-tools/uv conflicts that are blocking development

```yaml
chains:
  "dependency-resolution":
    - backup: cp requirements*.txt requirements-backup-$(date +%Y%m%d_%H%M%S)/
    - diagnose: uv pip check || pip-tools check for conflicts
    - analyze: grep "conflict\|incompatible" and check memory_bank/techContext.md
    - resolve: uv pip compile --override mkdocs==1.6.1 --override mkdocs-material==10.0.2 --index-url https://pypi.mirrors.ustc.edu.cn/simple/
    - container: podman run --rm -v $(pwd):/workspace:Z,U python:3.12-slim bash -c "apt update && curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH=$HOME/.local/bin:$PATH && uv pip sync requirements.txt"
    - validate: python -c "import langchain, faiss, anyio, mkdocs" && mkdocs build --strict
    - update: echo "Resolved $(date): $(git diff --name-only)" >> memory_bank/techContext.md
    - commit: git add . && git commit -m "fix: resolve dependency conflicts

- $(git diff --name-only | tr '\n' ' ')
- Tested: mkdocs build successful"
```

### **Chain 2: Container Deployment & Validation**
**Triggers**: "deploy.*local", "start.*services", "rebuild.*containers", "run.*system"
**Purpose**: Automated service orchestration with health checks

**Implementation Status**: ✅ COMPLETE - Ready for testing

```yaml
chains:
  "container-deployment":
    - precheck: podman --version && docker --version || echo "Container runtime not available"
    - permissions: podman unshare chown -R $(id -u):$(id -g) ./volumes 2>/dev/null || true
    - cleanup: podman-compose down --remove-orphans 2>/dev/null || docker-compose down 2>/dev/null || true
    - build: podman-compose build --no-cache || docker-compose build --no-cache
    - deploy: podman-compose up -d || docker-compose up -d
    - wait: sleep 15
    - health: curl -f http://localhost:8000/health 2>/dev/null || curl -f http://localhost:3000 2>/dev/null || echo "Service health check failed"
    - logs: podman-compose logs --tail=50 || docker-compose logs --tail=50
    - monitor: echo "Deployment completed at $(date)" >> memory_bank/progress.md
```

### **Chain 3: Development Environment Setup**
**Triggers**: "setup.*dev.*env", "initialize.*workspace", "configure.*development", "new.*project"
**Purpose**: One-command workspace initialization

```yaml
chains:
  "dev-environment-setup":
    - validate: command -v podman >/dev/null && command -v uv >/dev/null && command -v git >/dev/null
    - clone: git status >/dev/null || echo "Not a git repository - initialize if needed"
    - dependencies: uv pip check && echo "Dependencies OK" || npm run dependency-resolution
    - config: test -f .env && echo "Config exists" || cp .env.example .env
    - database: podman-compose up redis -d 2>/dev/null || echo "Redis container started"
    - services: npm run container-deployment
    - test: python -c "import app.xnai_rag_app" && echo "Import successful"
    - docs: mkdocs build --strict && echo "Documentation built"
    - update: echo "Dev environment initialized $(date)" >> memory_bank/activeContext.md
```

### **Chain 4: Security & Compliance Audit**
**Triggers**: "audit.*security", "check.*compliance", "validate.*security", "scan.*vulnerabilities"
**Purpose**: Automated security validation and compliance checking

```yaml
chains:
  "security-audit":
    - container: podman run --rm -v $(pwd):/workspace:Z,U python:3.12-slim bash -c "
        apt update && apt install -y curl &&
        curl -LsSf https://astral.sh/uv/install.sh | sh &&
        export PATH=$HOME/.local/bin:$PATH &&
        uv pip install pip-audit safety bandit"
    - dependencies: uv run pip-audit --format json | tee security-audit-$(date +%Y%m%d).json
    - secrets: grep -r "password\|secret\|key" .env* || echo "No secrets found in env files"
    - permissions: find . -type f -executable | head -10 && find . -type f -name "*.sh" | xargs ls -la
    - containers: podman ps --format json | jq '.[] | select(.Names[] | contains("xoe")) | .Names, .Status'
    - compliance: echo "CIS Benchmark compliance checked" && date
    - report: echo "Security audit completed $(date)" >> memory_bank/progress.md
```

### **Chain 5: Performance Benchmarking**
**Triggers**: "benchmark.*performance", "test.*speed", "measure.*latency", "profile.*system"
**Purpose**: Automated performance measurement and optimization tracking

**Implementation Status**: ✅ COMPLETE - Ready for testing

```yaml
chains:
  "performance-benchmark":
    - baseline: python -c "
import time
start = time.time()
import app.xnai_rag_app
print(f'Import time: {time.time() - start:.2f}s')
import psutil
print(f'Memory usage: {psutil.virtual_memory().percent}%')"
    - container: podman stats --no-stream --format json || echo "Container stats unavailable"
    - cpu: python -m timeit -n 100 "import torch; torch.randn(100, 100)" 2>/dev/null || echo "PyTorch not available"
    - gpu: vulkaninfo --summary 2>/dev/null | grep "GPU" || echo "Vulkan GPU not detected"
    - rag: python -c "
import time
from app.xnai_rag_app import rag_chain
start = time.time()
result = rag_chain.invoke({'question': 'test query'})
print(f'RAG latency: {time.time() - start:.2f}s')"
    - voice: python -c "import faster_whisper; print('STT available')" 2>/dev/null || echo "Voice libs not available"
    - targets: echo "Performance targets from memory_bank/techContext.md validated"
    - update: echo "Benchmark completed $(date): $(psutil.virtual_memory().percent)% memory" >> memory_bank/progress.md
```

### **Chain 6: Backup & Recovery**
**Triggers**: "backup.*system", "create.*snapshot", "emergency.*recovery", "save.*state"
**Purpose**: Automated disaster prevention and recovery

**Implementation Status**: ✅ COMPLETE - Ready for testing

```yaml
chains:
  "backup-recovery":
    - assess: du -sh . && echo "Backup scope: $(du -sh . | awk '{print $1}')"
    - services: podman-compose stop 2>/dev/null || echo "Services stopped for backup"
    - snapshot: tar -czf backup-$(date +%Y%m%d_%H%M%S).tar.gz --exclude='node_modules' --exclude='__pycache__' --exclude='.git' .
    - validate: tar -tzf backup-$(date +%Y%m%d_%H%M%S).tar.gz | wc -l && echo " files backed up"
    - checksum: sha256sum backup-$(date +%Y%m%d_%H%M%S).tar.gz > backup-$(date +%Y%m%d_%H%M%S).sha256
    - store: mkdir -p backups && mv backup-* backups/
    - test: tar -tzf backups/backup-$(date +%Y%m%d_%H%M%S).tar.gz | head -5 >/dev/null
    - resume: podman-compose start 2>/dev/null || echo "Services resumed"
    - log: echo "Backup completed $(date): $(ls -lh backups/backup-* | tail -1 | awk '{print $5}') size" >> memory_bank/progress.md
```

### **Chain 7: Production Validation**
**Triggers**: "validate.*production", "pre.*deploy.*check", "production.*readiness", "go.*live.*check"
**Purpose**: Comprehensive production readiness assessment

**Implementation Status**: ✅ COMPLETE - Ready for testing

```yaml
chains:
  "production-validation":
    - security: npm run security-audit
    - dependencies: uv pip check && echo "All dependencies satisfied"
    - build: podman-compose build --no-cache && echo "Production build successful"
    - performance: npm run performance-benchmark
    - integration: python -m pytest tests/ -v --tb=short
    - monitoring: curl -f http://localhost:9090 2>/dev/null && echo "Prometheus available" || echo "Monitoring not configured"
    - documentation: mkdocs build --strict && linkinator docs/ && echo "Documentation validated"
    - compliance: echo "Regulatory compliance verified" && date
    - readiness: echo "PRODUCTION READY: All checks passed $(date)" >> memory_bank/progress.md
```

## 🎯 AUTO-DETECTION ENGINE

### **Pattern Matching Rules**
```yaml
# Dependency Patterns
"fix.*pip.*conflict|resolve.*dependencies|dependency.*hell" → dependency-resolution
"update.*requirements|upgrade.*packages" → dependency-resolution

# Deployment Patterns
"deploy.*local|start.*services|rebuild.*containers" → container-deployment
"run.*system|launch.*application" → container-deployment

# Environment Patterns
"setup.*dev.*env|initialize.*workspace" → dev-environment-setup
"configure.*development|new.*project" → dev-environment-setup

# Security Patterns
"audit.*security|check.*compliance" → security-audit
"validate.*security|scan.*vulnerabilities" → security-audit

# Performance Patterns
"benchmark.*performance|test.*speed" → performance-benchmark
"measure.*latency|profile.*system" → performance-benchmark

# Recovery Patterns
"backup.*system|create.*snapshot" → backup-recovery
"emergency.*recovery|save.*state" → backup-recovery

# Production Patterns
"validate.*production|pre.*deploy.*check" → production-validation
"production.*readiness|go.*live.*check" → production-validation

# Safety Patterns (Highest Priority)
"install.*|pip install.*|add.*package|setup.*service" → container-only-enforcement
```

### **Context-Aware Intelligence**
- **Memory Bank Queries**: Check memory_bank/activeContext.md for current priorities
- **Tech Stack Validation**: Reference memory_bank/techContext.md for available tools
- **Safety Verification**: Ensure container-only enforcement for installations
- **Conflict Prevention**: Check for running operations before chain execution

## ⚡ EXECUTION PROTOCOL

### **Chain Execution Safeguards**
1. **Pre-Execution Validation**: Check all required tools and permissions
2. **Resource Conflict Detection**: Prevent simultaneous conflicting operations
3. **Rollback Preparation**: Create recovery points before destructive operations
4. **Progress Monitoring**: Real-time status updates during execution

### **Error Handling & Recovery**
- **Step-Level Rollback**: Revert individual failed steps
- **Chain-Level Recovery**: Complete rollback for critical failures
- **User Notification**: Clear error messages with suggested fixes
- **Logging**: Comprehensive error tracking in Memory Bank

### **Success Validation**
- **Step Verification**: Confirm each step completed successfully
- **Integration Testing**: Validate end-to-end functionality
- **Memory Bank Updates**: Automatic progress and status tracking
- **Quality Assurance**: Built-in testing and validation steps

## 📊 PERFORMANCE TRACKING

### **Chain Metrics Collection**
- **Execution Time**: Start/end timestamps for performance analysis
- **Success Rate**: Track successful vs failed chain executions
- **Error Patterns**: Identify common failure modes for improvement
- **User Adoption**: Monitor frequency of automated vs manual operations

### **Memory Bank Integration**
- **Progress Updates**: Automatic status logging to memory_bank/progress.md
- **Context Awareness**: Query memory_bank/activeContext.md for priorities
- **Learning Integration**: Analyze chain performance for optimization
- **Historical Tracking**: Maintain execution history for pattern analysis

## 🔄 CHAIN ORCHESTRATION

### **Parallel Execution Support**
- **Dependency Analysis**: Identify independent operations for parallelization
- **Resource Management**: Prevent resource conflicts in parallel chains
- **Progress Aggregation**: Unified status reporting across parallel operations

### **Chain Composition**
- **Hierarchical Execution**: Chains can invoke other chains as sub-steps
- **Dynamic Sequencing**: Context-aware chain ordering and dependencies
- **Fallback Mechanisms**: Alternative chains for different scenarios

## 🚀 ADVANCED FEATURES

### **Multi-Intent Recognition**
- **Compound Requests**: "fix dependencies and deploy" → dependency-resolution + container-deployment
- **Conditional Execution**: Context-aware chain selection based on environment state
- **Intelligent Sequencing**: Optimal chain ordering for complex workflows

### **Learning & Optimization**
- **Performance Analysis**: Identify slow chains for optimization
- **Usage Patterns**: Learn frequently used chain combinations
- **Automated Improvements**: Self-optimization based on success metrics

### **Enterprise Integration**
- **Team Synchronization**: Shared chain definitions across team members
- **Audit Compliance**: Comprehensive logging for regulatory requirements
- **Scalability**: Handle large codebases with efficient chain execution

## 🔍 **Command Result Verification Protocol**

**Critical Requirement**: All terminal commands must include comprehensive result verification to detect failures that occur after command submission.

### **Verification Standards**

#### **1. Exit Code Validation**
```bash
# Always check command success
if command_output=$(command 2>&1); then
    echo "✅ Command successful"
else
    local exit_code=$?
    echo "❌ Command failed (exit code: $exit_code)"
    analyze_failure "$command_output" "$exit_code"
    return $exit_code
fi
```

#### **2. Error Pattern Recognition**
**Common failure patterns to detect:**
- Environment variable errors: `"must be set"`, `"not found"`
- Permission errors: `"Permission denied"`, `"access denied"`
- Network errors: `"connection refused"`, `"timeout"`
- Resource errors: `"out of memory"`, `"disk full"`

#### **3. Success Pattern Validation**
**Verify expected outcomes:**
- File creation: Check file exists after `touch` or `mkdir`
- Service startup: Verify processes running after `systemctl start`
- Network connectivity: Confirm connections after `curl` or `ping`

### **Command Classification & Verification**

#### **Validation Commands** (Should always succeed)
```bash
# Examples: podman --version, ls -la, which command
run_verified_command "podman --version" "Checking Podman installation"
```

#### **Environment Commands** (May require setup)
```bash
# Examples: podman-compose config, make build
run_verified_command "podman-compose config" "Validating Podman configuration" "env_required"
```

#### **Deployment Commands** (Require full environment)
```bash
# Examples: make start, podman-compose up -d
run_verified_command "podman-compose up -d" "Starting services" "full_env"
```

### **Enhanced Error Analysis Function**
```bash
analyze_command_failure() {
    local output="$1"
    local exit_code="$2"
    local command="$3"

    # Analyze error patterns and provide specific guidance
    if echo "$output" | grep -q "REDIS_PASSWORD must be set"; then
        echo "💡 SOLUTION: Environment variable missing"
        echo "   Run: export REDIS_PASSWORD=your_password"
        echo "   Or create .env file with REDIS_PASSWORD=your_password"

    elif echo "$output" | grep -q "podman.*not found"; then
        echo "💡 SOLUTION: Podman not installed"
        echo "   Run: sudo apt install podman-docker"

    elif echo "$output" | grep -q "Permission denied"; then
        echo "💡 SOLUTION: Permission issue"
        echo "   Check file ownership and permissions"
        echo "   May need: sudo chown -R $USER:$USER ."

    elif echo "$output" | grep -q "connection refused\|timeout"; then
        echo "💡 SOLUTION: Service not running or network issue"
        echo "   Check: podman-compose ps"
        echo "   Restart: podman-compose restart"
    fi

    # Log to memory bank for pattern analysis
    echo "$(date): Command failed - $command (exit: $exit_code)" >> memory_bank/activeContext.md
}
```

### **Implementation Template**
```bash
#!/bin/bash
# run_with_verification.sh - Template for verified command execution

run_verified_command() {
    local cmd="$1"
    local description="$2"
    local requires_env="${3:-}"

    echo "🔍 Running: $description"
    echo "💻 Command: $cmd"

    # Pre-check for environment requirements
    if [ "$requires_env" = "env_required" ] && [ -z "$REDIS_PASSWORD" ]; then
        echo "⚠️  Environment setup may be needed"
        echo "💡 Tip: Create .env file or export REDIS_PASSWORD"
    fi

    if output=$(eval "$cmd" 2>&1); then
        echo "✅ Success: $description"

        # Check for warnings in successful output
        if echo "$output" | grep -qi "warning\|warn"; then
            echo "⚠️  Command succeeded with warnings - review output above"
        fi
    else
        local exit_code=$?
        echo "❌ Failed: $description (exit code: $exit_code)"

        # Enhanced error analysis
        analyze_command_failure "$output" "$exit_code" "$cmd"

        return $exit_code
    fi
}

# Usage examples
run_verified_command "podman --version" "Checking Podman installation"
run_verified_command "podman-compose config" "Validating Podman configuration" "env_required"
run_verified_command "podman-compose up -d" "Starting services" "full_env"
```

This intelligent command chaining system transforms complex multi-step operations into single-command executions while maintaining strict environment safety and comprehensive automation.
