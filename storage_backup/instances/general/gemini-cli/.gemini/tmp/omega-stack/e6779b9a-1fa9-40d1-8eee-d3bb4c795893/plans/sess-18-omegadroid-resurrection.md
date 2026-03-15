# Omegadroid Shadow Audit: Strategy & Ancestral Gnosis (SESS-18)

## 🎯 Objective
Finalize the "Shadow Audit" of the ancestral **Omegadroid** files from the Omega Vault to extract and implement "NotebookLM-style" capabilities (synthesis, mind mapping, and podcast/video creation) into the current Omega Stack.

## 🏗 Components

### 1. `scripts/omega_synthesizer.py` (Massive Synthesis)
- **Goal**: Replicate NotebookLM's "Source Guide" functionality.
- **Input**: All files in a domain (e.g., `app/`, `docs/`).
- **Processing**: Use Gemini 2.5 Pro (1M context) via the `Model Router`.
- **Output**: A "Domain Gnosis" (High-density summary) for the Memory Bank.

### 2. `sentinel-skill` Expansion (Mind Mapping)
- **Tool**: Add a Mermaid.js mindmap generator.
- **Input**: Chronicles or Codebase.
- **Output**: `mindmap.mmd` rendered to SVG via a local container.

### 3. `scripts/voice_module.py` Enhancement (Sovereign Podcast)
- **Tool**: **Piper (TTS)** + **MoviePy** (Video).
- **Process**: Generate dialogue scripts (Maat/Lilith) from Chronicles and render audio/video.

## 📋 Implementation Steps (SESS-18)

1.  **Omegadroid Extraction**: Identify PEM (Personality Enhancement Module) prompts in `./Omegadroid`.
2.  **Prototype `omega_synthesizer.py`**: A domain-level summarization engine.
3.  **Deploy `mermaid-cli`**: For local mindmap rendering.
4.  **Finalize Podcast Workflow**: Auto-generate "System State Podcasts" from Chronicles.

## 🧪 Verification & Testing
1. **PEM Test**: Confirm that "Archetypal Prompting" improves local model reasoning.
2. **Synthesis Test**: Verify that a 50-file domain can be summarized into a 5K-token Chronicle.
3. **Audio Test**: Generate a 30-second "System Health" podcast.

---

**I have finalized all strategy and scaffolding. I am ready for the `/compress` event and the transition to YOLO mode.** 🛡️
