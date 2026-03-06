Model card: philosophy-BERT (candidate: bowphs/PhilBerta)
Path: https://huggingface.co/bowphs/PhilBerta (fill-mask / philosophical corpora)

Summary
- Candidate lightweight encoder for philosophy domain (classification, topic extraction, semantic search).
- Use-case: index and classify philosophy-focused docs and notes to enrich RAG context.

Knowledge gaps
- Confirm training corpus & license (HF listing suggests a small fill-mask model).
- Assess whether a domain-specific RoBERTa or distilled variant offers better performance/size tradeoff.

Next steps
- Run HF metadata & license check, evaluate on sample philosophy docs.
- If lacking, plan distillation from larger domain-features (future work).
