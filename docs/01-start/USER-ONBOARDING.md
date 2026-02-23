# User Onboarding: XNAi Foundation

> **Date**: 2026-02-23
> **Context**: JOB-W2-007 - User Documentation Research
> **Status**: INITIAL DRAFT

---

## 1. Quick Start (The 5-Minute Win)

Welcome to the XNAi Foundation! Follow these steps to get your first AI-powered knowledge session running.

### 1.1 Prerequisites
- **Docker/Podman**: Installed and running.
- **Python 3.11+**: For local script execution.
- **API Keys**: (Optional) OpenAI, Anthropic, or Google API keys for external models.

### 1.2 Step 1: Clone and Build
```bash
git clone https://github.com/arcana-novai/xnai-foundation.git
cd xnai-foundation
make build  # Or 'podman-compose build'
```

### 1.3 Step 2: Configure
Copy the example environment file and add your keys:
```bash
cp .env.example .env
# Edit .env and set your model provider
```

### 1.4 Step 3: Launch
```bash
make up  # Or 'podman-compose up -d'
```

### 1.5 Step 4: Access the UI
Open your browser and navigate to `http://localhost:8000` to access the **Chainlit** knowledge interface.

---

## 2. Core Concepts

### 2.1 The Knowledge Absorption Pipeline
- **Extract**: Scrapes or reads your content.
- **Classify**: Categorizes it (How-to, Reference, etc.).
- **Score**: Evaluates quality and density.
- **Distill**: Summarizes and extracts insights.
- **Store**: Saves to long-term memory (Qdrant).

### 2.2 Memory Bank
This is the core of the project. It stores all research, strategies, and progress in human-readable Markdown.

### 2.3 Agent Bus (Redis)
All specialized agents (Cline, Gemini) coordinate using a shared Redis stream for real-time task management.

---

## 3. Contribution Basics

- **Code Style**: Follow the `ruff` and `mypy` configurations.
- **Documentation**: Use the Diátaxis framework (Tutorials, How-to, Reference, Explanation).
- **Tests**: Always add a unit test for new features in `tests/`.

---

## 4. Next Steps
- Read the [User FAQ](../03-reference/USER-FAQ.md).
- Check the [Troubleshooting Guide](../03-reference/TROUBLESHOOTING-GUIDE.md).
- Join the community (Discord/Slack).
