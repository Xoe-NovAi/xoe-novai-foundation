# Tactical Review Quick Start Guide

**Created**: 2026-02-14 22:05 UTC  
**Purpose**: Quick reference for monitoring CLI automation and reviewing integration tests

---

## 🚀 Quick Commands

```bash
# Watch for new test files (real-time monitoring)
./scripts/monitor-cli-implementations.sh --watch

# Generate status report
./scripts/monitor-cli-implementations.sh --review

# Show summary
./scripts/monitor-cli-implementations.sh --summary

# One-time check (default)
./scripts/monitor-cli-implementations.sh
```

---

## ✅ What to Look For When New Tests Appear

### File Structure
- [ ] Module has clear docstring explaining test purpose
- [ ] Imports are organized (stdlib, then third-party, then local)
- [ ] Uses proper pytest naming conventions (`test_*.py`, `def test_*`)
- [ ] Async tests marked with `@pytest.mark.asyncio`

### Test Quality
- [ ] Each test tests ONE thing (single responsibility)
- [ ] Test names describe what is being tested
- [ ] Setup/teardown handled with fixtures
- [ ] Resources cleaned up (connections, files, etc.)
- [ ] No hardcoded values or test data in code

### Coverage
- [ ] Happy path tested (normal operation)
- [ ] Error paths tested (what happens when things fail)
- [ ] Edge cases tested (boundary conditions)
- [ ] Performance baselines captured (if applicable)

### Integration Readiness
- [ ] All imports can be resolved
- [ ] Uses proper fixtures from conftest.py
- [ ] All dependencies are installed
- [ ] Service mocks work correctly
- [ ] No external API calls (should be mocked)

---

## 📊 Expected Test File Locations

### Service Integration Tests (Phase 4.1)
```
tests/integration/
├── conftest.py                    # Fixtures & setup
├── test_service_discovery.py      # Can we find all services?
├── test_query_flow.py             # Does query flow work end-to-end?
├── test_failure_modes.py          # Do failures get handled correctly?
├── test_health_monitoring.py      # Does health checking work?
├── test_api_integration.py        # Are APIs responding correctly?
└── test_end_to_end.py             # Complete workflow tests
```

---

## 🎯 Review Process

### When You See a New Test File:

1. **Quick Scan** (30 seconds)
   - Check filename and class names
   - Scan for obvious issues (syntax, imports)
   - Look for test organization

2. **Structure Review** (1-2 minutes)
   - Does it follow pytest patterns?
   - Are fixtures used properly?
   - Is it testing one clear thing?

3. **Quality Check** (2-3 minutes)
   - Are there good assertions?
   - Are edge cases tested?
   - Is error handling validated?

4. **Integration Check** (1 minute)
   - Will it run in the test environment?
   - Are all dependencies available?
   - Are mocks properly configured?

5. **Feedback** (Optional)
   - Note any issues found
   - Log to tactical-reviews.log
   - Share suggestions with team

---

## 🔍 Common Issues to Watch For

### Code Quality
- ❌ Test has multiple assertions testing different things
- ❌ Test data hardcoded in test function
- ❌ No error handling for cleanup
- ❌ Test name doesn't describe what's being tested

### Structure
- ❌ Mixing setup with assertions
- ❌ Not using fixtures for common setup
- ❌ Incomplete teardown (resources not released)
- ❌ Sync/async mixing without proper markers

### Integration
- ❌ Tests have external API dependencies
- ❌ Services assumed to be running
- ❌ No mocking of external systems
- ❌ Tests interfering with each other (state pollution)

### Performance
- ❌ Very slow tests (>5 seconds for unit tests)
- ❌ No timeout protection
- ❌ Database or file operations in fast tests
- ❌ Unbounded loops in tests

---

## 📝 Where to Log Findings

```
logs/tactical-reviews.log
```

Entry format:
```
=== Tactical Review: test_service_discovery.py ===
Timestamp: 2026-02-14 22:15:33 UTC
File: tests/integration/test_service_discovery.py
Status: ✅ GOOD / ⚠️  ISSUES / ❌ BLOCKING

Structure: [findings]
Quality: [findings]
Integration: [findings]
Suggestions: [findings]

---
```

---

## 🎓 Reference Materials

### Inside Memory Bank
- `memory_bank/PHASES/phase-4-status.md` - Test planning
- `memory_bank/OPERATIONS.md` - How to use CLI tools
- `internal_docs/01-strategic-planning/PHASE-4.1-RESEARCH-DEEP-DIVE.md` - Test patterns

### Implementation Guides
- `.clinerules/` - Cline coding standards
- `docs/02-tutorials/gemini-mastery/` - Gemini procedures
- `internal_docs/05-client-projects/gemini-cli-integration/` - Integration guide

---

## 💡 Tips for Good Integration Tests

✅ **DO**:
- Test one behavior per test
- Use clear, descriptive names
- Mock external systems
- Clean up resources
- Use fixtures for setup/teardown
- Test both success and failure paths
- Include performance baselines
- Document complex test logic

❌ **DON'T**:
- Mix multiple assertions in one test
- Hardcode test data
- Depend on test order
- Make real API calls
- Leave resources hanging
- Test implementation details
- Skip error scenarios
- Ignore performance

---

## 🔗 Quick Links

- **Monitoring Script**: `./scripts/monitor-cli-implementations.sh`
- **Review Framework**: `internal_docs/01-strategic-planning/CLI-AUTOMATION-REVIEW-FRAMEWORK.md`
- **Test Planning**: `memory_bank/PHASES/phase-4-status.md`
- **Research Details**: `internal_docs/01-strategic-planning/PHASE-4.1-RESEARCH-DEEP-DIVE.md`

---

## 📞 Questions?

Check these memory_bank files:
1. **How do I use the CLI tools?** → `memory_bank/OPERATIONS.md`
2. **What are we testing?** → `memory_bank/PHASES/phase-4-status.md`
3. **What patterns should I use?** → `internal_docs/01-strategic-planning/PHASE-4.1-RESEARCH-DEEP-DIVE.md`
4. **Who should I contact?** → `memory_bank/activeContext.md`

---

**Status**: ✅ Ready for Phase 4.1  
**Last Updated**: 2026-02-14 22:05 UTC
