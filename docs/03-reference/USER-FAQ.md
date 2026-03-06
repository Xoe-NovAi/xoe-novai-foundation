# User FAQ: XNAi Foundation

> **Date**: 2026-02-23
> **Context**: JOB-W2-007 - User Documentation Research
> **Status**: INITIAL DRAFT

---

## 1. General Questions

### 1.1 What is the XNAi Foundation?
It's an open-source, AI-powered knowledge management and multi-agent coordination system designed for high-throughput research, distillation, and long-term memory storage.

### 1.2 Who is it for?
Researchers, developers, and organizations looking to automate the process of absorbing large volumes of technical documentation, code, and session data into a searchable, structured knowledge base.

### 1.3 What models are supported?
Currently, XNAi supports **OpenAI (GPT-4o)**, **Anthropic (Claude 3.5/Sonnet)**, and **Google (Gemini 1.5 Pro/Flash)** via their respective APIs. Support for local models (e.g., Llama 3 via Ollama) is planned.

---

## 2. Technical Questions

### 2.1 Where is my data stored?
- **Raw/Staging Data**: In `library/_staging/` and `data/scraping_results/`.
- **Long-term Memory**: In a **Qdrant** vector database and the **Memory Bank** (Markdown files).
- **Session State**: In a **Redis** instance.

### 2.2 How do I update the knowledge base?
Use the **Chainlit** UI to upload documents or trigger a scrape. The `KnowledgeDistillationPipeline` will automatically process, score, and store the information.

### 2.3 Can I use it air-gapped?
Not yet. Current versions rely on external LLM APIs for the "Distill" and "Score" steps. Support for local inference (vLLM/Ollama) is in the roadmap for Phase 5.

---

## 3. Troubleshooting Quick Fixes

### 3.1 Qdrant is failing to start.
- **Cause**: Port 6333 or 6334 is already in use.
- **Solution**: Check running processes with `lsof -i :6333` or change the port in `docker-compose.yml`.

### 3.2 "Access Denied" when running tasks.
- **Cause**: Your agent DID is not verified or lacks the required ABAC permission.
- **Solution**: Run the `register_knowledge_agent` script to generate and verify your identity.

### 3.3 Slow performance during distillation.
- **Cause**: High latency from the LLM provider or large document chunking.
- **Solution**: Switch to a faster model (e.g., Gemini Flash) or reduce the `chunk_size` in `config.toml`.

---

## 4. Still Have Questions?
- **GitHub Issues**: Search for existing solutions or open a new one.
- **Discord**: Join our developer chat for real-time support.
