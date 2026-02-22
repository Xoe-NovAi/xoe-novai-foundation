# E2: README Only
# ===============
# The model receives the project path AND the README.md content pre-loaded.
# This simulates what most open-source projects provide.

## Setup Instructions

1. Start a fresh agent session
2. Pre-load the following file into the context:
   - `README.md` (190 lines, ~2,500 tokens)
3. Provide this prompt:

```
You have access to the XNAi Foundation project at:
/home/arcana-novai/Documents/xnai-foundation

Here is the project README:

[INSERT CONTENTS OF README.md HERE]

Analyze this project. I will ask you specific questions about it.
```

4. Allow additional exploration if the model requests it
5. Run all 6 tests from test-battery.md

## What This Measures

The value of a conventional README as context. Most projects rely on README.md
as the primary (often only) onboarding document. This environment tests whether
that is sufficient for deep comprehension.

## Files Provided

```
README.md    (~2,500 tokens)
```

**Total context budget**: ~2,500 tokens pre-loaded

## Expected Outcomes

- The README provides the origin story, component list, and architectural overview
- Models should achieve L2 (Structural Awareness) from README alone
- L3+ requires the model to explore beyond the README on its own
- The README does NOT contain: current sprint status, agent taxonomy, rate limit waterfall, Ma'at details, fork plan, or constraint tensions
