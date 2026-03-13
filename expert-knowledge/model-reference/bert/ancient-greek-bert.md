# Model Card: Ancient-Greek-BERT (uncased)

**Path**: `altsoph/bert-base-ancientgreek-uncased`  
**Format**: Hugging Face Transformers

## Summary
-   **Vector Size**: 768
-   **Primary Use**: High-fidelity embeddings for Ancient Greek texts.
-   **Target Collection**: `xnai_linguistic` in Qdrant.
-   **Key Trait**: Uncased and trained on a wide corpus of classical texts.

## Integration Guidance
-   Download this model to the `embeddings/` directory.
-   Use `sentence-transformers` or a similar library to generate embeddings for ingestion into the `xnai_linguistic` collection.
-   This model is critical for the **Scholarly Language Infrastructure**.

## Next Steps
-   **Download**: `git lfs install && git clone https://huggingface.co/altsoph/bert-base-ancientgreek-uncased` into a temporary directory and move to `embeddings/`.
-   **Validate**: Write a test case to generate an embedding for a sample Greek text and verify the vector dimension is 768.
-   **Integrate**: Update `scripts/ingest_library.py` to use this model when the `language_code` is `grc`.
