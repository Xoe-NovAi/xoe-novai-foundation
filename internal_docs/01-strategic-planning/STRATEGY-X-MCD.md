# Xoe-NovAi Model Card Database (X-MCD) Strategy
**Version**: 1.0.0 | **Status**: ACTIVE DEVELOPMENT | **Priority**: HIGH

## 🔱 Vision
To create a comprehensive, machine-readable repository of all AI models utilized or evaluated by the Xoe-NovAi Foundation. This database serves as the "Genealogy of Intelligence" for the stack, ensuring transparency, reproducibility, and optimal hardware steering.

---

## 🏗️ Architecture

### 1. File Structure
- **Location**: `expert-knowledge/model-reference/`
- **Taxonomy**: Categorized by function (LLMs, Embeddings, STT-TTS, Vision).
- **Format**: Markdown with a YAML front-matter header (Hugging Face compliant + XNAi extensions).

### 2. The Metadata Standard
Every model card must include the `xnai_integration` block, tracking:
- **Hardware Target**: Ryzen CPU, iGPU, or Vulkan.
- **Footprint**: Real-world RAM/VRAM usage.
- **Latency**: Actual response times in the sovereign environment.

### 3. Integration with CNS
- **Gemini CLI**: Acts as the primary auditor and curator of the X-MCD.
- **RAG API**: Can ingest X-MCD to provide "Model-Aware" responses to users.
- **The Butler**: Can eventually use X-MCD to dynamically switch models based on hardware health.

---

## 🛠️ Implementation Roadmap

### Phase 1: Foundation (Today)
- [x] Create directory structure.
- [x] Establish the `MODEL-CARD-TEMPLATE.md`.
- [ ] Populate the first 3 "Legacy" model cards (Qwen, Whisper, Nomic).

### Phase 2: Automation (Short-term)
- [ ] Develop a script to auto-generate basic metadata from Hugging Face URLs.
- [ ] Integrate X-MCD into the internal MkDocs.

### Phase 3: Dynamic Steering (Mid-term)
- [ ] Use X-MCD data to inform `config.toml` auto-tuning.

---

**Next Step**: Populating the first model cards.
