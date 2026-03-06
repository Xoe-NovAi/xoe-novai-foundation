# UI STRATEGY: Dual-Interface Protocol v1.0
**Status**: 🟢 ACTIVE | **Domain**: User Experience & Developer Operations

---

## 🎯 OBJECTIVE
Provide a high-quality, consumer-grade experience for library management and research while maintaining deep, low-level observability for agent development.

---

## 🖥️ THE TWO INTERFACES

### 1. Open WebUI (The "Librarian")
**Role**: Primary interface for research, chatting with documents, and library exploration.
- **URL**: `http://localhost:3001`
- **Target Audience**: Human Operator (Research mode), Scholarly users.
- **Key Features**:
    - **Document Q&A**: Native RAG indexing of the `library/sorted` folder.
    - **Model Switching**: Easy selection between local (Ollama) and cloud models.
    - **History**: Polished chat history and user management.
- **Integration**: Uses "Functions" to send commands to the XNAi Agent Bus.

### 2. Chainlit (The "Dev Console")
**Role**: Debugging, agentic trace observation, and voice interface development.
- **URL**: `http://localhost:8001`
- **Target Audience**: Developer / MC-Overseer.
- **Key Features**:
    - **Step-by-Step Traces**: Shows the raw logic of the `Gnosis Engine`.
    - **Voice Integration**: Primary testbed for low-latency voice-to-voice patterns.
    - **Tool Monitoring**: Direct visibility into tool calls and Agent Bus events.

---

## 🔄 WORKFLOW SYNERGY

1.  **Exploration**: User discovers a topic in **BookLore** (Library UI).
2.  **Inquiry**: User asks questions in **Open WebUI** using the curated books as context.
3.  **Refinement**: If the agent struggles, the Developer opens **Chainlit** to observe the "Chain of Thought" and identifies the logic gap.
4.  **Correction**: The Developer updates the `memory_bank` or fine-tunes the BERT model, observing the immediate impact in the Chainlit trace.

---

## 🛠️ MAINTENANCE & SCALING

- **Shared Volume**: Both UIs share access to the `library/` and `data/` volumes.
- **Single Backend**: Both UIs communicate with the same `xnai_rag_api` and `xnai_qdrant` instances.
- **Modular Portability**: New UIs (e.g., a mobile app) can be added by connecting to the standard Agent Bus and API endpoints.
