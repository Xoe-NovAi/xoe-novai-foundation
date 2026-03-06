# Contributing to the Expert Knowledge Base (EKB)
**Status**: Community Standard
**Version**: v1.0

## 🎯 The Purpose of the EKB
The EKB is a shared "Long-Term Memory" for the Xoe-NovAi Foundation Stack. To ensure your research, hardware fine-tuning, and strategies are "plug-n-play" for other users and AI agents, we maintain a standardized format for every "Knowledge Gem."

## 📏 Basic Standards
1. **Atomic Content**: One "gem" should focus on one specific problem, pattern, or strategy.
2. **Sovereign-First**: All knowledge must align with zero-telemetry and local-only principles.
3. **Hardware Library**: We specifically welcome "Hardware Mastery" gems—fine-tuned optimizations for specific CPUs, GPUs, and Operating Systems.
3. **AI-Parsable**: Use clear Markdown headers and YAML frontmatter so RAG engines can easily index your contribution.
4. **Actionable**: Every gem should conclude with a "Mastery" or "Prevention" step.

---

## 💎 The Knowledge Gem Template
Copy and paste this into a new `.md` file in the appropriate `expert-knowledge/` subfolder.

```markdown
---
title: "Brief Descriptive Title"
category: "coder | architect | security | environment"
author: "Your Name/Alias"
date: "YYYY-MM-DD"
tags: ["tag1", "tag2"]
---

# 💎 [Title of Knowledge Gem]

## 📋 Context & Discovery
*Briefly describe the scenario where this knowledge was discovered. What were you trying to achieve? What hardware/software was involved?*

## 🔍 The Challenge / Root Cause
*What was the core problem or bottleneck? If it was a bug, what was the root cause? Use code snippets if applicable.*

## 🛠️ The Implementation / Strategy
*How did you solve it? Provide the specific steps, code, or configuration changes.*

```bash
# Example of a command or configuration
make example-target
```

## 🏆 Mastery & Prevention
*What is the "Golden Rule" learned here? How can others implement this pattern to improve their stack?*

## 🔗 Related Gems
- [[link_to_another_gem]]
```

---

## 🚀 How to Submit
- **For Personal Use**: Simply add your files to `expert-knowledge/` in your local clone. Your AI agents (Gemini CLI, Cline) will automatically find and use them.
- **For the Community**: We welcome PRs that add high-value strategies to the core EKB! 
    1. Follow the template above.
    2. Ensure your gem passes documentation linting: `make pr-check`.
    3. Submit your PR and share your mastery with the world.

*Let's build the most powerful local AI knowledge base together.* 🚀
