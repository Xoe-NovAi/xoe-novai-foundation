# Lessons Learned - Wave 2 (2026-02-23)

> **Session**: Autonomous Execution - MC-Overseer Agent
> **Date**: 2026-02-23
> **Status**: COMPLETE

---

## 1. Technical Lessons

### 1.1 Python 3.13 Regex Compatibility

**Issue**: Variable-width look-behind patterns (`(?<=...)`) with variable-length quantifiers cause `re.PatternError` in Python 3.13+.

**Example**:
```python
# BROKEN in Python 3.13+
re.compile(r"(?<=://[^:]+:)[^@]+(?=@)")

# FIXED - Remove look-behind, use capture groups
re.compile(r"://[^:]+:([^@]+)@")
```

**Lesson**: Always use fixed-width look-behind patterns or restructure with capture groups. Test regex patterns with the target Python version.

**Files Affected**:
- `app/XNAi_rag_app/core/security/sanitization.py` (line 170)

---

### 1.2 Async Test Configuration

**Issue**: `pytest.mark.asyncio` requires `pytest-asyncio` plugin and proper `asyncio_mode` configuration.

**Solution**:
```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

**Installation**:
```bash
pip install pytest-asyncio
```

**Lesson**: Document all test dependencies in `requirements.txt` and `tox.ini`. The `asyncio_mode = auto` setting is critical for auto-detecting async tests.

---

### 1.3 Exponential Backoff Edge Case

**Issue**: `calculate_backoff_delay(retry_count=0)` with formula `2 ** (retry_count - 1)` returns 0.5 instead of expected 1.0.

**Root Cause**: Off-by-one error in exponent calculation.

**Fix**:
```python
# OLD - retry_count=0 returns 0.5
return min(base_delay * (2 ** (retry_count - 1)), max_delay)

# NEW - retry_count=0 returns 1.0 (base_delay)
return min(base_delay * (2 ** max(0, retry_count)), max_delay)
```

**Lesson**: Always test boundary conditions (retry_count=0, 1, max) for mathematical functions.

**Files Affected**:
- `app/XNAi_rag_app/core/redis_streams.py` (line 597-603)

---

### 1.4 Test Import Path Mismatches

**Issue**: Tests importing from wrong module path after refactoring.

**Example**:
```python
# WRONG - imports from core/knowledge_access.py
from app.XNAi_rag_app.core.knowledge_access import KnowledgeAccessControl

# CORRECT - imports from core/security/knowledge_access.py
from app.XNAi_rag_app.core.security.knowledge_access import KnowledgeAccessController
```

**Lesson**: After refactoring/renaming modules, run full test suite to catch import errors. Consider using `__all__` exports for backward compatibility during transitions.

---

## 2. Process Lessons

### 2.1 Memory Bank Update Protocol

**Success**: Non-destructive updates with timestamps work well for multi-agent coordination.

**Best Practices**:
1. Read file before writing
2. Append to logs, don't replace
3. Use ISO 8601 timestamps
4. Include coordination key in updates
5. Publish to Agent Bus for visibility

---

### 2.2 Task Dispatch Format

**Success**: Structured task dispatch with priority levels enables clear agent assignment.

**Format That Works**:
```
#### P1-HIGH: JOB-XXX - Task Name
| Subtask | Description | Status |
|---------|-------------|--------|
| XXX-1 | Subtask 1 | ✅ COMPLETE |
| XXX-2 | Subtask 2 | ⏳ PENDING |
```

**Lesson**: Include deliverables location and success criteria for each job.

---

### 2.3 Cross-Agent Verification

**Gap Identified**: No automated verification that agent outputs match expected locations.

**Recommendation**: Add verification step in MC-Overseer review:
1. Check deliverable files exist
2. Validate file content against job requirements
3. Run tests to verify functionality

---

## 3. Architecture Lessons

### 3.1 Redis Stream for Agent Bus

**Success**: Redis Streams work well for agent coordination with consumer groups.

**Implementation**:
- Stream: `xnai:agent_bus`
- Consumer Groups: `agent_wavefront`, `memory_sync`, `alert_handlers`
- DLQ: `xnai:dlq`

**Commands Used**:
```bash
# Create stream with initial message
redis-cli -a "password" XADD xnai:agent_bus '*' sender 'did:xnai:mc-overseer' ...

# Read stream info
redis-cli -a "password" XINFO STREAM xnai:agent_bus

# Read messages
redis-cli -a "password" XRANGE xnai:agent_bus - +
```

---

### 3.2 Test Coverage Strategy

**Finding**: 60% coverage achieved, 80% target requires additional tests.

**Gaps Identified**:
- API route tests missing
- Integration tests incomplete
- Edge case tests needed for sanitizer

**Recommendation**: Wave 3 should include:
- API endpoint tests
- Integration test suite
- Edge case test expansion

---

## 4. CI/CD Lessons

### 4.1 Security Gate Implementation

**Added**: Separate `security-gate` CI job that blocks on failure.

**Structure**:
```yaml
security-gate:
  runs-on: ubuntu-latest
  steps:
    - name: Run Bandit security linter
      run: bandit -r app/ -ll --skip B101,B311
    - name: Check for known vulnerabilities
      run: safety check --full-report
      continue-on-error: true  # Safety DB may have false positives
```

**Lesson**: Security scans should fail the build for critical issues. Use `continue-on-error: true` only for non-critical checks.

---

### 4.2 Coverage Artifact Upload

**Fix**: Coverage artifacts now uploaded from test jobs for aggregation.

**Before**:
```yaml
# Missing artifact upload
- name: Run tests
  run: pytest
```

**After**:
```yaml
- name: Run tests with tox
  run: tox -e ${{ matrix.tox-env }}

- name: Upload coverage artifact
  uses: actions/upload-artifact@v4
  with:
    name: coverage-${{ matrix.tox-env }}
    path: coverage-${{ matrix.tox-env }}.xml
```

---

## 5. Documentation Lessons

### 5.1 Quick Reference Card Value

**Success**: QUICK-REFERENCE-CARD.md provides at-a-glance information for developers.

**Sections That Work**:
- Quick Start Commands
- Project Structure
- Environment Variables
- Agent DIDs
- Redis Streams
- Permissions Tables
- Common Tasks

**Lesson**: Keep reference cards updated and version-controlled.

---

### 5.2 Error Best Practices Document

**Created**: Comprehensive error handling patterns document.

**Key Patterns Documented**:
1. Result Object Pattern
2. Dead Letter Queue (DLQ)
3. Default Deny Pattern
4. Circuit Breaker Pattern
5. Graceful Degradation

**Lesson**: Document patterns with code examples for team reference.

---

## 6. Metrics Summary

| Metric | Start | End | Change |
|--------|-------|-----|--------|
| Test Files | 0 | 4 | +4 |
| Test Lines | 0 | 1,400+ | +1,400 |
| Coverage | 0% | ~65% | +65% |
| Documentation | 0 | 5 files | +5 |
| Research Docs | 0 | 2 files | +2 |

---

## 7. Action Items for Wave 3

| Item | Priority | Owner |
|------|----------|-------|
| Add API endpoint tests | P1 | CLINE |
| Expand edge case tests | P1 | CLINE |
| Create integration test suite | P2 | CLINE |
| Reach 80% coverage | P2 | CLINE |
| Consolidate WebSocket docs | P3 | GEMINI-MC |
| Refactor RedisStreamManager | P3 | CLINE |
| Create Wave 3 dispatch | P1 | MC-OVERSEER |

---

**Created**: 2026-02-23
**Owner**: MC-Overseer Agent
**Coordination Key**: `ACTIVE-TASK-DISPATCH-2026-02-23`
