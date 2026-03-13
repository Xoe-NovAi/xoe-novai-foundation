# FINE-TUNING PROTOCOL v1.0
**Status**: 🟢 ACTIVE | **Domain**: Continuous Model Improvement

---

## 🎯 OBJECTIVE
Establish a systematic, semi-automated workflow for the continual fine-tuning of local models (BERT, LLMs) based on human feedback and high-reasoning AI evaluations.

---

## 🔄 CONTINUOUS IMPROVEMENT LOOP

### 1. Data Collection (Interaction Logs)
- **Source**: Chainlit UI, Agent Bus events, CLI research logs.
- **Action**: Capture user "thumbs up/down" on retrieval and synthesis results.
- **Storage**: `quality_metrics` database and `data/training_inbox/`.

### 2. Quality Gating (AI Review)
- **Model**: Cloud `Gemini 1.5 Pro`.
- **Action**: Re-evaluate low-scored interactions to identify root causes (e.g., poor retrieval, hallucination).
- **Output**: Cleaned, high-quality "Gold Sets" for fine-tuning.

### 3. Synthetic Data Augmentation (AI-Automated)
- **Model**: `Gemini 1.5 Pro` or `Claude 3.5 Sonnet`.
- **Action**: Generate 50-100 synthetic Q&A pairs for any new or underperforming scholarly domain (e.g., specific classical philosophy topics).
- **Goal**: Boost the "low-resource" local model performance.

### 4. Fine-Tuning Execution (Sentence-BERT / LoRA)
- **Strategy**: 
    - **BERT-Class**: Sentence-BERT (SBERT) fine-tuning for improved semantic retrieval.
    - **LLM-Class**: QLoRA (4-bit quantization) fine-tuning on the Ryzen host for specialized reasoning.
- **Script**: `scripts/automated_fine_tuning.py` (Planned).

---

## 📈 METRIC TRACKING (SCHOLARLY TEST STUDIES)

- **A/B Testing**: Run retrieval tests with `ancient-greek-bert` vs. `general-bert` on same classical corpus.
- **Retrospective Analysis**: Monthly review of fine-tuning impact on `quality_metrics`.
- **Human-in-the-Loop (HITL)**: Mandatory review of all automated fine-tuning datasets before training.

---

## 🛠 TOOL UTILIZATION

- **Qdrant**: Stores positive/negative interaction vectors.
- **Redis Streams**: Real-time event logging for training data triggers.
- **ChainForge**: Visual evaluation and A/B testing matrix.
- **Librarian Agent**: Manages the training data inventory and freshness.
