# 👁️ OMEGA AISTHESIS STRATEGY: VISION, AUDIO & SENSES (v2.0)
**Status**: DRAFT | **Target**: Future Horizon (Phase 4)
**Role**: Giving the Omega Stack "Eyes and Ears"

---

## 1. Vision Strategy (Beyond Screenshots)
**Goal**: Real-time visual understanding of the user's workflow.

### **A. The "Watcher" (Screenshots)**
*   **Status**: Defined in `docs/specs/BROWSER_MCP_SPEC.md` and `VISION_AND_CONTINUAL_PROCESS_STRATEGY.md`.
*   **Tech**: `watchdog` + `mss` + Gemini 1.5 Flash.

### **B. The "Streamer" (Video/Live Feed)**
*   **Gap**: We lack a strategy for continuous video analysis.
*   **Solution**: **Gstreamer + Gemini 1.5 Flash (Multimodal API)**.
    *   **Pipeline**: `ffmpeg` captures screen -> HLS stream -> Gemini API (Frame sampling @ 1fps).
    *   **Use Case**: "Watch me debug this" (Agent proactively intervenes when it sees an error in the terminal).

---

## 2. Audio Strategy (The Voice of Jem)
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

## 3. Infrastructure Optimization: `mmap` for Embeddings
**Goal**: Load massive vector indexes without consuming RAM.

### **The "Zero-Copy" Protocol**
*   **Problem**: Loading 1GB of embeddings into RAM kills the 12GB limit.
*   **Solution**: **Memory-Mapped Files (`mmap`)**.
    *   **Qdrant**: Already supports `mmap` storage backend. We must *enforce* it in `config.toml`.
    *   **Implementation**: Ensure `storage_type: mmap` is set for all Qdrant collections in `infra/docker/docker-compose.yml` (environment variables).

---

## 4. The Curator & Linguistic Strategy
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
