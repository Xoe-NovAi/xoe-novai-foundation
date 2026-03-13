# ChainForge LLM Evaluation & Testing (XNAi Foundation)

**Status**: 🟢 CURRENT  
**Last Updated**: 2026-02-28  
**Owner**: MC-Overseer  
**Domain**: Infrastructure

---

## Overview

In the XNAi Foundation stack, **ChainForge** is used as the primary visual environment for prompt engineering, evaluation, and LLM-as-a-Judge testing. It allows for systematic comparison of model responses (Gemini, Copilot, OpenCode) across various prompt templates and scoring rubrics.

---

## 🚀 Evaluation Scorer Types (2026)

ChainForge utilizes a "Scorer-First" philosophy to evaluate LLM outputs:

| Scorer Type | Best Use Case | Precision | Setup Effort |
| :--- | :--- | :--- | :--- |
| **Simple Evaluator** | Boolean checks (e.g., "Contains 'JSON'?") | High (Deterministic) | Low |
| **Code Evaluator (JS/Python)** | Structured data, regex, or BLEU/ROUGE scores | Absolute | Medium |
| **LLM Scorer** | Subjective quality, tone, and reasoning | Variable | Low |

### 2026 Best Practice: Multi-Stage Gating
1. **Gate 1**: Simple Evaluator (Catch formatting/syntax errors).
2. **Gate 2**: Python Evaluator (Semantic similarity vs. ground truth).
3. **Gate 3**: LLM Scorer (Qualitative analysis using GPT-5 or Claude 4.5).

---

## 🛠 LLM-as-a-Judge (Scorer Models)

When using the **LLM Scorer Node**, model selection is critical for reliability:

| Model (as Scorer) | Reasoning Depth | Recommended Use |
| :--- | :--- | :--- |
| **GPT-5 (Codex/Pro)** | Ultra-High | Gold standard for logic and code correctness |
| **Claude 4.5 Opus** | High | Best for human-like tone and safety alignment |
| **Gemini 2.5 Pro** | High | Ideal for long-context evaluation (100k+ tokens) |
| **Llama 3.3 (70B+)** | Medium | High-volume, low-cost local scoring (Ollama) |

---

## 📈 Operational Workflows

### 1. The "Hashtag" Context Pattern
Use implicit template variables (e.g., `{#writing_style}`) in the LLM Scorer to provide the judge with the intended style, preventing "blind" scoring.

### 2. Temperature Zero Mandate
Always set the scorer model's temperature to `0` to ensure test matrices are reproducible and deterministic.

### 3. Visualizing Jitter
Use **Box Plots** and **Histograms** in ChainForge to identify which prompt variables cause the most variance ("jitter") in scores, rather than relying solely on the mean.

### 4. Meta-Scoring (Rubric Test)
Before running large batches, validate the scoring prompt against 5 "Good" and 5 "Bad" known responses to refine the rubric.

---

## ⚠️ Known Issues & Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| Inter-Rater Disagreement | Judges disagree on a score | Chain multiple scorers (e.g., GPT-5 + Claude) and use the Response Inspector. |
| Hallucinated Scores | Vague rubrics | Refine the scoring prompt with specific examples (Few-shot scoring). |
| High Evaluation Cost | Using Opus for every check | Use the Multi-Stage Gating pattern (Simple → Python → LLM). |

---

## 📚 References
- [ChainForge Documentation](https://chainforge.ai/docs/)
- [XNAi Model Research Compendium](expert-knowledge/model-reference/MODEL-RESEARCH-COMPENDIUM.md)
- [XNAi Split Test Protocol](docs/protocols/SPLIT-TEST-PROTOCOL.md)
