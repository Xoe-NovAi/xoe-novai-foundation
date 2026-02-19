# E1: Cold Start
# ==============
# The model receives ONLY the project path. No files are pre-loaded.
# The model must discover everything through its own exploration.

## Setup Instructions

1. Start a fresh agent session with no prior context
2. Provide only this prompt:

```
You have access to the XNAi Foundation project at:
/home/arcana-novai/Documents/xnai-foundation

Analyze this project. I will ask you specific questions about it.
```

3. Allow the model to explore freely using whatever tools it has
4. After the model's initial exploration, run all 6 tests from test-battery.md
5. Record tokens consumed during exploration AND during each test

## What This Measures

Raw model capability without any context engineering assistance.
The model must decide what to read, in what order, and how deep to go.

## Expected Outcomes

- Strong models (Opus, Gemini Pro): Should reach L2-L3 with enough exploration tokens
- Mid-tier models (Sonnet, GPT-5 Mini): L1-L2
- Free-tier models (big-pickle, GLM-5): L1, possibly L2
- Local models (Qwen 7B): L1 only (32K context severely limiting)

## Key Metric

The E1 score establishes the **Baseline Capability Score (BCS)** for each model.
