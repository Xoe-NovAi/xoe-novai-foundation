# Thinking Models Strategy: Optimization & Integration

**Status**: 🟡 IN RESEARCH  
**Date**: 2026-02-24T04:54:08Z  
**Priority**: HIGH - Expands model portfolio capability

---

## DISCOVERY: Thinking Model Variants

### What We Found

**Available Thinking Models** (via `opencode models google`):
```
✅ google/antigravity-claude-opus-4-5-thinking
✅ google/antigravity-claude-opus-4-6-thinking  
✅ google/antigravity-claude-sonnet-4-5-thinking
```

**Available Non-Thinking Models**:
```
✅ google/antigravity-claude-sonnet-4-6
✅ google/antigravity-gemini-3-pro
✅ google/antigravity-gemini-3-flash
```

### Implication

We have **TWO distinct model variants**:
1. **Regular models**: Fast, direct responses
2. **Thinking models**: Internal reasoning, better quality

This enables **differentiated routing** based on task type.

---

## THINKING MODEL CHARACTERISTICS

### What "Thinking" Means

Claude models with "thinking" suffix use extended inference:
- **Internal reasoning**: Model thinks through problem before responding
- **Better quality**: Often produces more accurate, nuanced answers
- **Longer latency**: Takes extra time for thinking
- **Higher tokens**: Thinking adds to token consumption

### Performance Tradeoffs

| Aspect | Thinking | Regular |
|--------|----------|---------|
| Response Quality | ⭐⭐⭐⭐⭐ (best) | ⭐⭐⭐⭐ (good) |
| Latency | 🐌 Slower (+20-30%) | ⚡ Faster |
| Token Cost | 📊 Higher (thinking) | 📊 Normal |
| Best For | Complex reasoning | Fast answers |
| Worst For | Simple queries | Anything | N/A |

---

## TASK ROUTING STRATEGY

### When to Use Thinking Models

**HIGH PRIORITY (Always use thinking)**:
- Architecture decisions
- Security analysis
- Complex algorithm design
- System design reviews
- Ambiguous problem solving
- Critical business decisions

**MEDIUM PRIORITY (Consider thinking)**:
- Code reviews
- Performance optimization
- API design
- Error diagnosis
- Documentation

**LOW PRIORITY (Don't use thinking)**:
- Simple queries
- Formatting requests
- Quick answers
- Information retrieval
- Translation

### Recommended Routing Rules

```python
if task_type == "architecture_design":
    use_model("antigravity-claude-opus-4-6-thinking")
    
elif task_type == "security_analysis":
    use_model("antigravity-claude-opus-4-6-thinking")
    
elif task_type == "complex_reasoning":
    use_model("antigravity-claude-opus-4-6-thinking")
    
elif task_type == "code_review":
    use_model("antigravity-claude-sonnet-4-6-thinking")  # Good balance
    
elif task_type == "code_generation":
    use_model("antigravity-claude-sonnet-4-6")  # Non-thinking, faster
    
elif task_type == "quick_answer":
    use_model("antigravity-claude-sonnet-4-6")  # Speed priority
    
else:  # general_task
    use_model("antigravity-claude-sonnet-4-6")  # Default: balance
```

---

## QUOTA IMPACT

### Token Consumption

**Question**: Do thinking models consume extra tokens?

**Likely Answer**: Yes
- Internal thinking uses tokens
- Adds 10-30% to total token count
- Should be factored into quota planning

**Strategic Implication**:
- Thinking = Higher cost, better quality
- Use strategically, not for everything
- Reserve for high-value decisions

---

## INTEGRATION WITH DISPATCHER

### Update to MultiProviderDispatcher

Current specialization scores need update:

```python
SPECIALIZATION_SCORES = {
    # Opus (Thinking) - Best for reasoning
    "antigravity_opus_4_6_thinking": {
        "reasoning": 100,      # Perfect for reasoning
        "code": 85,            # Good for code review
        "architecture": 100,   # Excellent for design
        "speed": 20,           # Slow (not for urgent)
    },
    
    # Sonnet (Thinking) - Balance for code
    "antigravity_sonnet_4_6_thinking": {
        "reasoning": 90,       # Very good reasoning
        "code": 95,            # Excellent code review
        "architecture": 95,    # Good for design
        "speed": 40,           # Still slower but better
    },
    
    # Sonnet (Regular) - Default fast choice
    "antigravity_sonnet_4_6": {
        "reasoning": 70,       # Adequate reasoning
        "code": 100,           # Perfect for generation
        "architecture": 70,    # Okay for design
        "speed": 100,          # Fastest
    },
}
```

---

## QUESTIONS FOR RESEARCH

### Q1: Thinking Budget Configuration
- Can we control thinking budget (8K, 16K, 32K)?
- Is it configurable per-request in OpenCode?
- Default thinking budget value?
- **Impact**: HIGH - affects quality tuning

### Q2: Performance Characteristics
- Actual latency difference (thinking vs non-thinking)?
- Token consumption difference (measured)?
- Quality improvement quantifiable?
- **Impact**: HIGH - affects SLA decisions

### Q3: Streaming Support
- Do thinking models support streaming?
- Does thinking show as "thinking..." then response?
- Or only complete after thinking finishes?
- **Impact**: MEDIUM - affects UX

### Q4: Cost Optimization
- Should we limit thinking model usage (due to token cost)?
- What's optimal ratio (thinking vs regular)?
- How to prevent unnecessary thinking queries?
- **Impact**: HIGH - affects quota management

---

## RECOMMENDATIONS (Preliminary)

### For Phase 3C Update

1. **Add Thinking Models to Provider Hierarchy**
   - Document as specialized variants
   - Add to task routing rules
   - Update specialization matrix

2. **Implement Thinking Model Strategy**
   - Architect dispatcher to choose thinking when needed
   - Add metrics for thinking model usage
   - Monitor token consumption by model type

3. **Update SLA Targets**
   - Increase p95 latency allowance for thinking models
   - Keep p50 at <1000ms (will be violated by thinking)
   - Or: Have separate SLA for reasoning tasks

4. **Quota Planning**
   - Assuming thinking = 20% extra tokens
   - Could reduce 4M capacity to 3.2M effective if heavy thinking use
   - Should plan strategically

---

## NEXT STEPS

1. **Measure actual performance** (latency, tokens, quality)
2. **Test thinking budget configuration** in OpenCode
3. **Implement routing logic** in MultiProviderDispatcher
4. **Update PROVIDER-HIERARCHY-FINAL.md** with thinking strategy
5. **Create monitoring** for thinking model usage
6. **Document best practices** for thinking model usage

---

## REFERENCES

- Available models (verified live): 30+ Google models including 7 Antigravity
- Previous: PROVIDER-HIERARCHY-FINAL.md
- Previous: PHASE-3C-STATUS-SUMMARY.md

---

**Status**: �� THINKING MODELS STRATEGY IN DEVELOPMENT

Multiple thinking model variants discovered. Strategy being developed to optimize routing and quota usage.

