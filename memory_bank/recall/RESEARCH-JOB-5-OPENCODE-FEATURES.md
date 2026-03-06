# Job 5: OpenCode CLI Advanced Features Research

**Status**: 🟡 READY TO START  
**Date Queued**: 2026-02-24T02:12:00Z  
**Priority**: MEDIUM - Enhances Antigravity integration  
**Estimated Duration**: 1-2 hours research

---

## Research Objective

Document advanced OpenCode CLI features for better Antigravity integration. Focus on streaming, retry logic, configuration, and performance flags.

---

## Questions to Answer

1. Does OpenCode support streaming mode?
2. What retry logic is built-in?
3. Can we pre-configure default model?
4. Does --json flag work with Antigravity?
5. Are there performance optimization flags?

---

## Testing Commands

### Feature 1: Streaming Mode
```bash
# Does output stream or buffer?
time opencode chat --model google/antigravity-claude-sonnet \
  --stream "Write a long story" | head -20
```

### Feature 2: JSON Output
```bash
# Can we get structured output?
opencode chat --model google/antigravity-claude-sonnet \
  --json "Write hello world in Python" | python3 -m json.tool
```

### Feature 3: Retry Configuration
```bash
# Built-in retry behavior?
opencode chat --model google/antigravity-claude-sonnet \
  --retry 3 "test" 2>&1 | grep -i retry
```

### Feature 4: Configuration
```bash
# Can we set defaults?
opencode config set default-model google/antigravity-claude-sonnet
opencode config show | grep antigravity
```

### Feature 5: Performance Flags
```bash
# Any parallelization or caching?
opencode chat --help | grep -i "parallel\|cache\|optimize"
```

---

## Expected Findings

| Feature | Status | Impact |
|---------|--------|--------|
| Streaming | ⏳ TBD | Better UX for long responses |
| JSON | ⏳ TBD | Structured parsing for integration |
| Retry | ⏳ TBD | Better reliability |
| Configuration | ⏳ TBD | Reduced CLI args |
| Performance | ⏳ TBD | Faster subprocess execution |

---

## Integration Impact

Based on findings, will document:
- Best practices for subprocess.Popen integration
- Streaming response handling
- Error recovery patterns
- Performance optimization techniques

---

**Status**: 🟡 READY TO START

Can execute immediately - Independent research, no blockers.

