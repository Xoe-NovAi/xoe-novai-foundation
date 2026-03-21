# 👁️ OMEGA AISTHESIS STRATEGY: VISION, AUDIO & SENSES (v2.0)
**Status**: DRAFT | **Target**: Future Horizon (Phase 4)
**Role**: Giving the Omega Stack "Eyes and Ears"

---

## 1. Local Model Strategy (16GB Sovereignty)
**Goal**: High-fidelity local reasoning with zero external latency.

### **A. Tiered Local Models**
*   **Small (0.5b - 1.5b)**: Qwen 2.5 1.5b (for sub-second routing/summarization).
*   **Medium (3b - 8b)**: **Gemma 4b** (Excellent logic/follow-through), **RocRaccoon** (Creative/Unfiltered), **Krikri-8b-Instruct** (Advanced Instruction Following).
*   **Optimization**: Use `mmap` for all 8b models to ensure zero-copy loading and preserve RAM for the AnyIO mesh.

### **B. The "Sovereign Fallback"**
*   **Design**: If Claude/Gemini APIs are unavailable or high-latency (>2s), the Archon automatically routes to the local **Krikri-8b-Instruct**.
*   **Context**: Use the `session_library` (Zettelkasten) to provide highly filtered, dense context to the local model to maximize its performance within its smaller context window.

---

## 2. Vision Strategy (Beyond Screenshots)
**Goal**: Real-time visual understanding of the user's workflow.

### **A. The "Watcher" (Screenshots)**
*   **Status**: Defined in `docs/specs/BROWSER_MCP_SPEC.md` and `VISION_AND_CONTINUAL_PROCESS_STRATEGY.md`.
*   **Tech**: `watchdog` + `mss` + Gemini 3.1 Flash.

### **B. The "Streamer" (Video/Live Feed)**
*   **Gap**: We lack a strategy for continuous video analysis.
*   **Solution**: **Gstreamer + Gemini 3.1 Flash (Multimodal API)**.
    *   **Pipeline**: `ffmpeg` captures screen -> HLS stream -> Gemini API (Frame sampling @ 1fps).
    *   **Use Case**: "Watch me debug this" (Agent proactively intervenes when it sees an error in the terminal).

---

## 3. Audio Strategy (The Voice of Jem)
**Goal**: Low-latency, full-duplex voice interaction.

### **A. Accessibility Mandate (Hands-Free)**
*   **Priority**: CRITICAL. The system must be fully operable by voice for blind/low-vision users.
*   **Latency Target**: < 500ms (Human conversation pace).
*   **Protocol**: "Wake Word" (Porcupine) -> "Stream" (LiveKit) -> "Think" (Gemini/Groq) -> "Speak" (ElevenLabs/Deepgram).

### **B. The "Nova Legacy" (Mac Portability)**
*   **Heritage**: Original `nova/` module was Mac-native.
*   **Challenge**: CoreAudio (Mac) vs PulseAudio (Linux).
*   **Strategy**: Use `sounddevice` or `pyaudio` python abstractions to wrap OS-specific drivers.
*   **Audit**: Review `projects/nova/` for original Mac bindings.

---

## 4. Infrastructure Optimization: `mmap` for Embeddings & Weights
**Goal**: Load massive vector indexes and model weights without consuming RAM.

### **The "Zero-Copy" Protocol**
*   **Problem**: Loading 1GB of embeddings or 5GB of model weights into RAM kills the 16GB limit.
*   **Solution**: **Memory-Mapped Files (`mmap`)**.
    *   **Qdrant**: Already supports `mmap` storage backend. We must *enforce* it in `config.toml`.
    *   **Llama.cpp**: Ensure `--mmap` is enabled for all local model loading.
    *   **Implementation**: Ensure `storage_type: mmap` is set for all Qdrant collections in `infra/docker/docker-compose.yml` (environment variables).

---

## 5. The Curator & Linguistic Strategy
**Goal**: Semantic consistency and knowledge ingestion.

### **A. The Curator (Ingestion)**
*   **Strategy**: The "Spec-Kit Queue".
*   **Task**: A persistent queue in Redis (`xnai:curation_queue`) where URLs (manuals, docs) are pushed.
*   **Worker**: The `xnai_library_curator` (already in compose) processes this queue, extracting "Gnosis," and updating the Vector Store.

### **B. The Linguistic Strategy**
*   **Strategy**: "The Naming of Things" (Nomenclature).
*   **Action**: Scheduled "Symposium" (Chat Session) to define the controlled vocabulary.
*   **Artifact**: `library/lexicon/OMEGA_DICTIONARY.json`.

---
**Prepared by**: Jem (The Archon)
