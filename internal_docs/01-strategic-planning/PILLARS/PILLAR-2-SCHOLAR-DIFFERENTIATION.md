# PILLAR 2: SCHOLAR DIFFERENTIATION

**← [Back to ROADMAP-MASTER-INDEX](../ROADMAP-MASTER-INDEX.md)**

---

## Document Overview

This document contains the complete Phase 6A-6F implementation details for **PILLAR 2: Scholar Differentiation** - establishing Ancient Greek mastery and domain-specific research excellence as competitive differentiators.

**Timeline**: Weeks 11-24 (14 weeks)  
**Priority**: P1 (Critical for Scholar Positioning)  
**Blocking**: Phases 8A (Market Positioning) depend on Scholar features being operational  
**Team**: Grok MCA (Phase lead), Cline-Trinity (implementation), Gemini CLI (execution)

---

## Table of Contents

1. [Executive Context](#executive-context)
2. [Team Roles & Responsibilities](#team-roles--responsibilities)
3. [Phase Overview](#phase-overview)
4. [Phase 6A: Dynamic Embedding System](#phase-6a-dynamic-embedding-system)
5. [Phase 6B: Ancient Greek Scholarly Features](#phase-6b-ancient-greek-scholarly-features)
6. [Phase 6C: Vikunja Memory_Bank Integration](#phase-6c-vikunja-memory_bank-integration)
7. [Phase 6D: Multi-Model Support & Model Registry](#phase-6d-multi-model-support--model-registry)
8. [Phase 6E: Voice Quality Enhancement](#phase-6e-voice-quality-enhancement)
9. [Phase 6F: Fine-Tuning Capability (LoRA/QLoRA)](#phase-6f-fine-tuning-capability-loraqliora)
10. [Success Metrics](#success-metrics)
11. [Related Documents](#related-documents)

---

## Executive Context

### Vision: The Scholar's Forge - Phase 2

While Pillar 1 established production stability, Pillar 2 transforms Xoe-NovAi into a **world-class scholarly research tool** with capabilities that rival multi-million dollar academic platforms.

**Key Differentiators**:
- **Ancient Greek Mastery**: Only tool with Ancient-Greek-BERT + LSJ + Perseus + CLTK integrated
- **AI-Powered Research**: Semantic search across corpora, not keyword matching
- **Sovereign Research**: 100% offline, zero telemetry, air-gapped (protect research IP)
- **Dynamic Intelligence**: Embedding system adapts to domain (philosophy ≠ science)
- **Scholarly Ecosystem**: Multi-model support, fine-tuning, voice interfaces

### Prerequisites

✅ **Pillar 1 Complete**:
- Memory optimization (6A requires dynamic embedding from 5A)
- Observable infrastructure (6A uses metrics)
- Authentication (6B uses auth for LSJ API)
- Library curation (6B requires Ancient Greek texts in library)

### Current State

⚠️ **Starting Point for Pillar 2**:
- Basic RAG infrastructure (Phase 5 complete)
- Library populated with Ancient Greek texts (Phase 5E)
- Single-model embeddings (Sentence-Transformers)
- No scholarly features yet
- Voice interface exists but needs quality improvement

🎯 **Ending State**:
- Multi-embedding system (5+ models)
- Ancient Greek BERT + CLTK + LSJ + Perseus integrated
- Vikunja memory_bank operational
- 5+ model families supported (Qwen, Llama, Mistral, Phi, Krikri-7b)
- Production-quality voice interface
- Fine-tuning pipeline operational

---

## Team Roles & Responsibilities

| Phase | Owner | Duration | Collaborators | Success Metrics |
|-------|-------|----------|---|---|
| **6A: Dynamic Embeddings** | Grok MCA + Cline-Trinity | 3 weeks | Gemini CLI | 5+ models integrated, >95% selection accuracy, 20% quality improvement |
| **6B: Ancient Greek** | Grok MCA + Cline-Trinity | 3 weeks | Cline-Kat (docs) | CLTK >95% lemmatization, LSJ 100% common words, validation by scholars |
| **6C: Vikunja Memory** | Gemini CLI + Cline-Trinity | 2 weeks | Team (data input) | 100+ conversations stored, <500ms retrieval, 90% context preservation |
| **6D: Multi-Model Registry** | Cline-Trinity + Cline-Kat | 3 weeks | Gemini CLI | 5+ model families, <30s swap time, zero-downtime deployment |
| **6E: Voice Quality** | Cline-Kat + Cline-Pro | 2 weeks | Gemini CLI (testing) | WER <5%, TTS quality parity with Azure, 5+ languages |
| **6F: Fine-Tuning** | Cline-Trinity + Gemini CLI | 3 weeks | Team (iteration) | Train <4 hours on 8GB, >50% loss reduction, LoRA <100MB |

---

## Phase Overview

| Phase | Name | Duration | Impact | Owner | Blocking | Key Dependencies |
|-------|------|----------|--------|-------|----------|---|
| 6A | Dynamic Embedding System | 3 weeks | CRITICAL | Grok MCA | 6B, 6C, 6D | Phase 5E (library) |
| 6B | Ancient Greek Scholarly | 3 weeks | CRITICAL | Grok MCA | 6C, 8A | Phase 5E (texts), Phase 6A (embeddings) |
| 6C | Vikunja Memory_Bank | 2 weeks | HIGH | Gemini CLI | 6D (coordination) | Vikunja operational |
| 6D | Multi-Model Registry | 3 weeks | CRITICAL | Cline-Trinity | 6E, 6F, 8A | Phase 6A (embedding models) |
| 6E | Voice Quality | 2 weeks | HIGH | Cline-Kat | None | None (independent) |
| 6F | Fine-Tuning (LoRA) | 3 weeks | HIGH | Cline-Trinity | None (optional) | Phase 6D (models) |

---

## PHASE 6A: DYNAMIC EMBEDDING SYSTEM

**Duration**: 3 weeks | **Complexity**: Very High (5/5) | **Impact**: Critical | **Owner**: Grok MCA + Cline-Trinity

### Scope

- Multi-embedding architecture (Ancient-Greek-BERT, scienceBERT, philosophyBERT, etc.)
- Dynamic embedding selection based on domain/context
- Embedding model registry and versioning
- Hybrid retrieval (multiple embeddings for same query)
- Performance optimization (lazy loading, caching)

### Implementation Manual Sections

#### 1. Embedding Architecture Design

**Core Principle**: Different domains require different semantic understanding. A single multilingual embedding cannot capture the nuances of Ancient Greek philosophy AND modern Python documentation equally well.

**Embedding Registry**:
```python
EMBEDDING_MODELS = {
    "ancient_greek": {
        "model": "pranaydeeps/Ancient-Greek-BERT",
        "dim": 768,
        "languages": ["grc"],
        "domains": ["classics", "philosophy"],
        "max_length": 512
    },
    "krikri": {
        "model": "ilsp/Krikri-7B-Instruct",
        "dim": 4096,
        "languages": ["el", "grc"],
        "domains": ["classics", "philosophy", "literature"],
        "max_length": 4096,
        "type": "llm_embeddings"
    },
    "sciencebert": {
        "model": "allenai/sciencebert_scivocab_uncased",
        "dim": 768,
        "languages": ["en"],
        "domains": ["science", "technical"],
        "max_length": 512
    },
    "philosophybert": {
        "model": "guymorlan/philosophy-bert",
        "dim": 768,
        "languages": ["en", "de", "fr"],
        "domains": ["philosophy"],
        "max_length": 512
    },
    "codebert": {
        "model": "microsoft/codebert-base",
        "dim": 768,
        "languages": ["code"],
        "domains": ["technical"],
        "max_length": 512
    },
    "multilingual": {
        "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "dim": 384,
        "languages": ["multi"],
        "domains": ["general"],
        "max_length": 128
    }
}
```

#### 2. Dynamic Selection Logic

**Selection Algorithm**:
```python
def select_embedding_models(query: str, context: QueryContext) -> List[str]:
    """
    Select best embedding model(s) for query based on:
    - Detected language
    - Inferred domain
    - Query complexity
    - Available models
    """
    models = []
    
    # Detect language
    lang = detect_language(query)
    
    # Infer domain from context
    if context.knowledge_base:
        domain = context.knowledge_base.domain
    else:
        domain = infer_domain_from_query(query)
    
    # Primary model selection
    if lang == "grc":
        # Ancient Greek text - use specialized model
        models.append("ancient_greek")
        # Add Krikri for longer texts or instruction-following
        if len(query) > 200 or context.requires_instruction_following:
            models.append("krikri")
    elif domain == "science":
        models.append("sciencebert")
    elif domain == "philosophy":
        if lang in ["en", "de", "fr"]:
            models.append("philosophybert")
        models.append("multilingual")  # Fallback
    elif domain == "technical":
        if "code" in context.tags:
            models.append("codebert")
        models.append("sciencebert")  # Technical writing
    else:
        models.append("multilingual")  # General fallback
    
    return models
```

**Context-Aware Selection**:
- **Ancient Greek Philosophy**: ancient_greek + philosophybert (hybrid)
- **Scientific Papers**: sciencebert
- **Code Documentation**: codebert + multilingual
- **Esoteric Texts**: multilingual + philosophybert (no specialized model yet)
- **Modern Greek**: krikri (handles both modern and ancient)

#### 3. Multi-Embedding Retrieval

**Hybrid Search Strategy**:
```python
async def hybrid_retrieval(
    query: str,
    context: QueryContext,
    top_k: int = 10
) -> List[Document]:
    """
    Retrieve documents using multiple embeddings, then fuse results.
    """
    # Select embedding models
    models = select_embedding_models(query, context)
    
    # Parallel retrieval with each model
    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(
                retrieve_with_embedding(query, model, top_k)
            )
            for model in models
        ]
    
    # Collect results
    all_results = [task.result() for task in tasks]
    
    # Reciprocal Rank Fusion (RRF)
    fused_results = reciprocal_rank_fusion(all_results, k=60)
    
    return fused_results[:top_k]
```

**Reciprocal Rank Fusion (RRF)**:
- Combines rankings from multiple retrievers
- Robust to differences in score scales
- Formula: `RRF(d) = Σ(1 / (k + rank_i(d)))`
- k = 60 (standard parameter)

#### 4. Embedding Storage & Management

**Storage Strategy**:
```
/embeddings/
├── ancient_greek/
│   ├── classics/
│   │   └── plato_republic.npy
│   └── philosophy/
├── sciencebert/
│   ├── physics/
│   └── cs/
├── philosophybert/
│   └── modern/
├── codebert/
│   └── technical/
└── multilingual/
    └── general/
```

**Lazy Loading**:
- Embeddings loaded on-demand (not all in memory)
- LRU cache (1GB max per model)
- Model quantization for memory efficiency (FP16)

**Versioning**:
- Embedding model version tracked in metadata
- Re-embedding strategy when models update
- Backward compatibility (old embeddings still searchable)

#### 5. Ancient-Greek-BERT Integration

**Model**: `pranaydeeps/Ancient-Greek-BERT`
- Pre-trained on Ancient Greek corpus (Perseus, Thesaurus Linguae Graecae)
- 768-dimensional embeddings
- Handles polytonic Greek, diacritics, breathing marks
- Optimized for classical texts (Homer, Plato, Aristotle, Sophocles)

**Preprocessing Pipeline**:
```python
def preprocess_ancient_greek(text: str) -> str:
    """
    Normalize Ancient Greek text for BERT input.
    """
    # Normalize sigma variants (existing code)
    text = normalize_greek_text(text)
    
    # Handle diacritics
    # (Ancient-Greek-BERT expects polytonic input)
    # Do NOT strip diacritics - they carry semantic meaning
    
    # Tokenization
    # BERT tokenizer handles Greek Unicode properly
    
    return text
```

**Fine-Tuning Considerations** (Optional - Future):
- Domain-specific fine-tuning on philosophical texts
- Contrastive learning for better similarity
- Instruction tuning for Krikri-7B integration

#### 6. Krikri-7B-Instruct Integration

**Model**: `ilsp/Krikri-7B-Instruct`
- 7B parameter model for Modern + Ancient Greek
- Instruction-following capability
- Longer context window (4096 tokens)
- Can be used for:
  - Text generation (summaries, translations)
  - Question answering on Greek texts
  - Embedding generation (alternative to Ancient-Greek-BERT)

**Integration Modes**:
1. **Embedding Generation**: Use Krikri's hidden states as embeddings
2. **Reranking**: Use Krikri to rerank Ancient-Greek-BERT results
3. **Generation**: Generate summaries/translations of retrieved texts
4. **QA**: Answer questions about retrieved Ancient Greek texts

**Memory Optimization** (Critical for 16GB system):
- Quantization: 4-bit GGUF format (reduces 7B to ~4GB RAM)
- Lazy loading: Only load when Ancient Greek query detected
- Offloading: CPU inference (llama.cpp), no GPU required

### Success Criteria
- ✅ 5+ embedding models integrated and operational
- ✅ Dynamic selection accuracy > 95% (correct model for query)
- ✅ Hybrid retrieval improves quality by 20%+ (vs. single model)
- ✅ Ancient-Greek-BERT retrieval quality validated by Greek scholars
- ✅ Krikri-7B summaries indistinguishable from human (blind test)
- ✅ Embedding generation < 500ms per document (Ancient-Greek-BERT)
- ✅ Memory usage < 6GB total (all models lazy-loaded)

### Dependencies
- Phase 5E (Library Curation System with Ancient Greek texts)
- Existing embedding infrastructure in RAG system

---

## PHASE 6B: ANCIENT GREEK SCHOLARLY FEATURES

**Duration**: 3 weeks | **Complexity**: Very High (5/5) | **Impact**: Very High | **Owner**: Grok MCA + Cline-Trinity

### Scope
- Ancient Greek text analysis tools (morphology, syntax, lexicon)
- Integration with Perseus Digital Library
- LSJ (Liddell-Scott-Jones) Lexicon integration
- Parsing and lemmatization (CLTK integration)
- Citation formatting (classical references)
- Parallel text support (Greek + English)

### Implementation Manual Sections

#### 1. Classical Language Toolkit (CLTK) Integration

**CLTK**: Comprehensive library for processing ancient languages (Greek, Latin, etc.)

**Features to Integrate**:
- **Tokenization**: Split Ancient Greek text into words (handle clitics, elision)
- **Lemmatization**: Reduce words to dictionary form (λύω from λύσω, λύσομαι, etc.)
- **POS Tagging**: Part-of-speech tagging (noun, verb, adjective, etc.)
- **Morphological Analysis**: Parse inflected forms (case, number, gender, tense, mood, voice)
- **Named Entity Recognition**: Identify proper names (people, places)

**Installation**:
```python
# Add to requirements.txt
cltk>=1.2.0
cltk_data>=1.0.0

# Download Ancient Greek models
from cltk.data.fetch import FetchCorpus
corpus_downloader = FetchCorpus(language="grc")
corpus_downloader.import_corpus("grc_models_cltk")
```

**Integration Example**:
```python
from cltk.tokenizers.grc import GreekWordTokenizer
from cltk.lemmatize.grc import GreekBackoffLemmatizer
from cltk.tag.pos import POSTag

class AncientGreekAnalyzer:
    def __init__(self):
        self.tokenizer = GreekWordTokenizer()
        self.lemmatizer = GreekBackoffLemmatizer()
        self.pos_tagger = POSTag('grc')
    
    def analyze(self, text: str) -> List[Dict[str, Any]]:
        """
        Full morphological analysis of Ancient Greek text.
        """
        tokens = self.tokenizer.tokenize(text)
        lemmas = self.lemmatizer.lemmatize(tokens)
        pos_tags = self.pos_tagger.tag_ngram_123_backoff(tokens)
        
        return [
            {
                "token": token,
                "lemma": lemma,
                "pos": pos,
                "citation_form": self.get_citation_form(lemma, pos)
            }
            for token, lemma, (_, pos) in zip(tokens, lemmas, pos_tags)
        ]
```

#### 2. LSJ Lexicon Integration

**LSJ**: Liddell-Scott-Jones Greek-English Lexicon (standard for Ancient Greek)

**Data Source**:
- Perseus Digital Library XML export
- Parse TEI XML to extract entries
- Store in local SQLite database

**Lexicon Features**:
- Word lookup (lemma → definition, etymology, usage examples)
- Morphological variants (handle all inflected forms)
- Cross-references (related words, compounds)
- Citation examples (quote from classical texts)

**API**:
```python
class LSJLexicon:
    def lookup(self, lemma: str) -> Dict[str, Any]:
        """
        Look up word in LSJ lexicon.
        
        Returns:
            {
                "lemma": "λύω",
                "transliteration": "luo",
                "short_definition": "to loose, release",
                "full_entry": "...",
                "etymology": "...",
                "compounds": ["ἀπολύω", "ἐκλύω", "κατα Lύω"],
                "citations": [...]
            }
        """
        pass
```

**UI Integration**:
- Chainlit UI: Hoverable tooltips on Greek words
- Click word → show LSJ definition in sidebar
- Pronunciation guide (transliteration)

#### 3. Perseus Digital Library API Integration

**Perseus**: Largest digital library of Ancient Greek & Latin texts

**API Endpoints**:
- `/api/text/{urn}`: Retrieve text by CTS URN
- `/api/translations/{urn}`: Get English translations
- `/api/commentary/{urn}`: Get scholarly commentary
- `/api/lexicon/{word}`: Lexicon lookup

**CTS URN Format**:
- `urn:cts:greekLit:tlg0012.tlg001.perseus-grc2:1.1-1.100`
- `tlg0012` = Homer
- `tlg001` = Iliad
- `perseus-grc2` = Edition
- `1.1-1.100` = Book 1, lines 1-100

**Integration**:
```python
class PerseusAPI:
    def __init__(self):
        self.base_url = "http://www.perseus.tufts.edu/hopper"
    
    async def get_text(self, urn: str) -> Dict[str, Any]:
        """
        Retrieve text from Perseus by CTS URN.
        """
        pass
    
    async def get_parallel_texts(self, urn: str) -> List[Dict[str, Any]]:
        """
        Get Greek text + all available English translations.
        """
        greek_text = await self.get_text(urn)
        translations = await self.get_translations(urn)
        return [greek_text] + translations
```

**Offline Caching**:
- Cache all retrieved texts locally
- Build offline mirror of frequently-accessed works
- Graceful degradation if Perseus API unavailable

#### 4. Citation Formatting (Classical References)

**Standard Format**: Author, Work, Book.Chapter.Section (or Line)

**Examples**:
- Plato, *Republic* 514a = `Pl. R. 514a`
- Homer, *Iliad* 1.1-10 = `Hom. Il. 1.1-10`
- Aristotle, *Nicomachean Ethics* 1094a = `Arist. EN 1094a`

**Auto-Citation Detection**:
```python
def extract_citations(text: str) -> List[Dict[str, Any]]:
    """
    Detect classical citations in text.
    
    Patterns:
    - "Plato's Republic 514a"
    - "Hom. Il. 1.1"
    - "Aristotle, Nicomachean Ethics 1094a"
    """
    # Regex patterns for common citation formats
    patterns = [
        r"(Plato|Aristotle|Homer|Sophocles),?\s+([A-Z][a-z]+)\s+(\d+[a-z]?)",
        r"(Pl\.|Arist\.|Hom\.|Soph\.)\s+([A-Z][a-z]+\.?)\s+(\d+[a-z]?)",
    ]
    
    citations = []
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            citations.append({
                "author": match.group(1),
                "work": match.group(2),
                "reference": match.group(3),
                "cts_urn": resolve_to_cts_urn(match.groups())
            })
    
    return citations
```

**Citation Resolver**:
- Convert author abbreviation → CTS author code (Pl. → tlg0059)
- Convert work abbreviation → CTS work code (R. → tlg030)
- Generate full CTS URN for retrieval

#### 5. Parallel Text Support

**Use Case**: Display Ancient Greek text alongside English translation

**UI Layout**:
```
┌─────────────────────────────────────────────────┐
│  Πλάτων, Πολιτεία 514a                          │
├─────────────────────────────────────────────────┤
│  Greek (Original)         │ English (Jowett)    │
├───────────────────────────┼─────────────────────┤
│  μετὰ ταῦτα δή, εἶπον,  │ After this, I said, │
│  ἀπείκασον τοιούτῳ       │ compare our nature  │
│  πάθει τὴν ἡμετέραν      │ in respect of        │
│  φύσιν...                │ education...         │
└───────────────────────────┴─────────────────────┘
```

**Alignment**:
- Sentence-level alignment (not word-level)
- Synchronized scrolling
- Toggle visibility (show Greek-only, English-only, or both)

**Translation Quality**:
- Multiple translations available (Jowett, Bloom, Reeve)
- User can select preferred translation
- Display translator & publication date

#### 6. Scholarly Features

**Morphological Hover**:
- Hover over Greek word → show lemma, POS, morphology
- Click word → show LSJ definition

**Commentary Integration**:
- Link to scholarly commentary (if available)
- Extract commentary from Perseus
- Display in sidebar or modal

**Text Comparison**:
- Compare different editions of same text
- Highlight textual variants
- Show critical apparatus

**Export**:
- Export as PDF with formatting
- Export as LaTeX for academic papers
- Export citations in BibTeX format

### Success Criteria
- ✅ CLTK integration: 95%+ lemmatization accuracy on Plato corpus
- ✅ LSJ lexicon: 100% coverage of common words (top 10,000 lemmas)
- ✅ Perseus API: < 1s retrieval time for text + translation
- ✅ Citation detection: 90%+ accuracy on scholarly papers
- ✅ Parallel texts: Sentence alignment error < 5%
- ✅ Scholarly validation: Greek professors rate system as "publication-quality"

---

## PHASE 6C: VIKUNJA MEMORY_BANK INTEGRATION

**Duration**: 2 weeks | **Complexity**: High (4/5) | **Impact**: High | **Owner**: Gemini CLI + Cline-Trinity

### Scope
- Vikunja as experimental memory_bank feature
- Task-based memory persistence
- Conversation history in Vikunja tasks
- Context retrieval from past tasks
- Team coordination memory (agent handoffs)
- **Important**: Vikunja is a local installation - no external rate limiting applies

### Implementation Manual Sections

#### 1. Vikunja Architecture (Current State)

**From projectbrief.md**:
- Container deployment: ✅ Operational
- PostgreSQL backend: ✅ Configured
- Service startup: ✅ Operational
- Web UI: ✅ Accessible at http://localhost:3456
- Rate Limiting: N/A (local installation, no external limits)

**Current Vikunja Usage**:
- Project management for team coordination
- Task assignment via labels (agent:cline-trinity, etc.)
- Multi-agent workflow orchestration

#### 2. Memory_Bank Experimental Design

**Concept**: Use Vikunja tasks as persistent memory storage for conversations and context.

**Memory Types**:
1. **Conversation Memory**: Store chat history as Vikunja tasks
2. **Context Memory**: Store important context snippets (decisions, learnings)
3. **Handoff Memory**: Store agent-to-agent handoff context
4. **Reference Memory**: Store links to documents, code, external resources

**Task Structure**:
```
Vikunja Namespace: Memory Bank
├── Project: Conversations
│   └── Tasks: One task per conversation session
├── Project: Context Snippets
│   └── Tasks: Important context (decisions, learnings)
├── Project: Handoffs
│   └── Tasks: Agent-to-agent transition context
└── Project: References
    └── Tasks: Links to docs, code, external resources
```

**Task Metadata**:
- **Labels**: `memory:conversation`, `memory:context`, `memory:handoff`, `memory:reference`
- **Tags**: Domain, agent, date
- **Assignee**: Original agent who created memory
- **Description**: Memory content (full conversation or snippet)
- **Attachments**: Files if needed

#### 3. Conversation Memory Implementation

**Create Conversation Task**:
```python
async def store_conversation_memory(
    conversation_id: str,
    messages: List[Dict[str, str]],
    summary: str,
    metadata: Dict[str, Any]
) -> int:
    """
    Store conversation as Vikunja task.
    
    Returns:
        task_id: Vikunja task ID
    """
    # Create task in "Conversations" project
    task = await vikunja_client.create_task(
        project="conversations",
        title=f"Conversation: {metadata['title']} ({conversation_id})",
        description=format_conversation(messages, summary),
        labels=["memory:conversation", metadata['domain']],
        tags=metadata.get('tags', []),
        assignee=metadata.get('agent', 'user')
    )
    
    return task.id
```

**Retrieve Conversation Memory**:
```python
async def retrieve_conversation_memory(
    conversation_id: str = None,
    domain: str = None,
    agent: str = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Retrieve past conversations from Vikunja.
    
    Filters:
        - conversation_id: Specific conversation
        - domain: Filter by domain (classics, technical, etc.)
        - agent: Filter by agent who created memory
        - limit: Max number of conversations to return
    """
    tasks = await vikunja_client.get_tasks(
        project="conversations",
        labels=["memory:conversation"],
        tags=[domain] if domain else None,
        assignee=agent,
        limit=limit
    )
    
    return [parse_conversation_task(task) for task in tasks]
```

#### 4. Context Snippet Storage

**Purpose**: Store important context that should be retained long-term (decisions, learnings, patterns).

**Example Context Snippets**:
- "Decision: Use Ancient-Greek-BERT for Greek text embeddings"
- "Learning: vm.swappiness=35 optimal for ML workloads"
- "Pattern: Hybrid RRF retrieval improves quality by 20%"

### Success Criteria
- ✅ Vikunja operational (local installation)
- ✅ 100+ conversations stored in memory bank
- ✅ Context retrieval < 500ms (search + display)
- ✅ Handoff memory reduces context loss by 90% (agent transitions)

### Dependencies
- Vikunja deployment (already operational)
- Vikunja API client library
- Chainlit UI modifications

---

## PHASE 6D: MULTI-MODEL SUPPORT & MODEL REGISTRY

**Duration**: 3 weeks | **Complexity**: Very High (5/5) | **Impact**: Critical | **Owner**: Cline-Trinity

### Scope
- Model abstraction layer (support Qwen, Llama, Mistral, Phi, Krikri-7b)
- Local model registry (Ollama-style pull/push)
- Model versioning and hot-swapping
- GGUF file management and validation
- Performance comparison framework

### Implementation Manual Sections

#### 1. Model Abstraction Architecture

- Unified inference API (across GGML, GGUF, AWQ)
- Model capability detection (context window, vocab size)
- Dynamic prompt template selection
- Tokenizer abstraction (SentencePiece, BPE, WordPiece)
- Memory footprint estimation

#### 2. Model Registry Design

**Local Model Store** (`~/.xnai/models/`):
```
~/.xnai/models/
├── ancient-greek-bert/
│   ├── model.safetensors
│   └── manifest.json
├── qwen-7b/
│   ├── model.gguf
│   └── manifest.json
└── krikri-7b/
    ├── model.gguf
    └── manifest.json
```

**Model Manifest Format**:
```json
{
  "name": "qwen-7b",
  "version": "v1.0",
  "model_id": "Qwen/Qwen2-7B-Instruct-GGUF",
  "format": "gguf",
  "size_gb": 4.2,
  "context_window": 8192,
  "vocab_size": 152064,
  "architecture": "transformer",
  "requires": ["tokenizer.model"],
  "checksum": "sha256:abc123...",
  "tags": ["instruction-following", "multilingual"]
}
```

#### 3. Model Management CLI

```bash
# List installed models
$ xnai model list

# Download model
$ xnai model pull qwen-7b

# Remove model
$ xnai model remove llama-7b

# Show model info
$ xnai model info qwen-7b

# Benchmark model
$ xnai model benchmark qwen-7b
```

#### 4. Hot-Swap Implementation

- Model unload/load without service restart
- Graceful request draining (60s timeout)
- Memory reclamation verification
- Health check integration (model readiness)
- Rollback mechanism (automatic on failure)

#### 5. Performance Benchmarking

- Token throughput (tokens/second)
- First-token latency
- Memory usage
- Context window utilization
- Quality metrics (for domain-specific tasks)

### Success Criteria
- ✅ Support 5+ model families
- ✅ Model swap < 30 seconds
- ✅ Zero downtime during model change
- ✅ Automatic model recommendation (based on task)
- ✅ Performance comparison dashboard in Grafana

---

## PHASE 6E: VOICE QUALITY ENHANCEMENT

**Duration**: 2 weeks | **Complexity**: High (4/5) | **Impact**: High | **Owner**: Cline-Kat

### Scope
- STT quality evaluation (Whisper vs. alternatives)
- TTS quality upgrade (Azure/Google quality locally)
- Voice cloning capability (optional)
- Multi-language support (5+ languages)
- Real-time voice processing optimization

### Implementation Manual Sections

#### 1. STT Quality Assessment

- Benchmark datasets (Common Voice, LibriSpeech)
- Accuracy metrics (WER - Word Error Rate)
- Latency profiling (real-time factor)
- Accent/dialect handling
- Technical term recognition (AI/ML jargon)

#### 2. STT Alternative Evaluation

- **Option 1**: Whisper.cpp optimization (CPU-only, fastest)
- **Option 2**: Vosk (offline, 20+ languages)
- **Option 3**: Coqui STT (customizable)
- **Option 4**: Nvidia NeMo (high quality)

#### 3. TTS Quality Upgrade

- **Option 1**: Coqui TTS (neural, voice cloning)
- **Option 2**: Piper TTS (fast, 40+ voices)
- **Option 3**: VITS (high quality)
- Voice sample library (10+ voices, multiple emotions)
- Real-time synthesis optimization

#### 4. Voice Features

- Emotion detection (sentiment analysis integration)
- Speaker diarization (multi-speaker conversations)
- Wake word customization
- Voice activity detection (VAD)
- Noise cancellation (RNNoise)

#### 5. Multi-Language Support

- Language detection (auto-detect)
- Cross-language STT/TTS pairing
- Translation integration
- Locale-aware formatting
- Character encoding

### Success Criteria
- ✅ WER < 5% on clean audio
- ✅ STT latency < 200ms (real-time factor < 0.5)
- ✅ TTS quality parity with Azure/Google
- ✅ Support 5+ languages
- ✅ Voice cloning from 5-minute sample (optional)

---

## PHASE 6F: FINE-TUNING CAPABILITY (LORA/QLORA)

**Duration**: 3 weeks | **Complexity**: Very High (5/5) | **Impact**: Very High | **Owner**: Cline-Trinity

### Scope
- LoRA/QLoRA training pipeline
- Dataset preparation and validation
- Training job orchestration
- Model merging and quantization
- Fine-tuned model versioning

### Implementation Manual Sections

#### 1. Fine-Tuning Architecture

- Training backend (Axolotl, LLaMA Factory, Unsloth)
- LoRA adapter management
- Base model + adapter loading
- Memory-efficient training (4-bit quantization)
- Distributed training prep (future multi-GPU)

#### 2. Dataset Pipeline

- Dataset format validation (Alpaca, ShareGPT)
- Data cleaning and deduplication
- Train/val/test split strategies
- Dataset versioning (DVC integration)
- Privacy-preserving data handling

#### 3. Training Job Management

- Job queue (Celery-based, priority scheduling)
- Resource allocation (CPU cores, memory limits)
- Progress tracking (epoch, loss, perplexity)
- Checkpointing strategy (save every N steps)
- Early stopping (validation loss plateau)

#### 4. Hyperparameter Optimization

- Learning rate scheduling (cosine annealing)
- LoRA rank/alpha tuning (default: r=16, alpha=32)
- Batch size optimization (gradient accumulation)
- Epoch count determination
- Weight decay and warmup

#### 5. Model Deployment

- Adapter merging (LoRA → full model)
- Quantization post-training (GGUF conversion)
- Model registry integration
- A/B testing framework
- Rollback mechanism

### Success Criteria
- ✅ Fine-tune 0.6B model on 8GB RAM in < 4 hours
- ✅ Training loss reduction > 50% after 3 epochs
- ✅ Fine-tuned model accuracy > base + 10% on domain task
- ✅ LoRA adapter size < 100MB
- ✅ Zero data exfiltration (air-gapped training)

### Competitive Advantages
- **vs. LM Studio**: Fine-tuning capability (LM Studio lacks this)
- **vs. Ollama**: Domain-specific customization
- **vs. Cloud APIs**: Data sovereignty
- **vs. GitHub Copilot**: Local fine-tuning

---

## Success Metrics

### Research Quality Metrics (from RESEARCH-P1)

| Metric | Target | Validation |
|--------|--------|------------|
| Ancient-Greek-BERT retrieval quality | Validated by Greek scholars | A/B test with academic baseline |
| Dynamic embedding accuracy | > 95% correct model selection | Test on 100+ diverse queries |
| CLTK lemmatization | > 95% on Plato corpus | Standard CLTK test suite |
| LSJ coverage | 100% of top 10,000 lemmas | Frequency analysis of corpus |
| Voice quality (WER) | < 5% on clean audio | Common Voice test set |
| Fine-tuning training time | < 4 hours on 8GB | Benchmark on reference dataset |

### Implementation Quality Metrics

| Metric | Target | Measurement |
|--------|--------|------------|
| Embedding retrieval latency | < 500ms per query | Load testing with realistic workload |
| Embedding model memory | < 6GB total (all loaded) | Memory profiling with all models active |
| Multi-model swap time | < 30 seconds | Timed testing with health checks |
| Vikunja memory retrieval | < 500ms for search | Database query profiling |
| Voice latency (end-to-end) | < 2 seconds | Real-world testing with Chainlit UI |

### Team Success Metrics

| Phase | Owner | On-Time Target | Quality Target |
|-------|-------|---|---|
| 6A | Grok MCA + Cline-Trinity | Week 13 | 5+ models, >95% selection accuracy |
| 6B | Grok MCA + Cline-Trinity | Week 16 | CLTK >95%, scholarly validation |
| 6C | Gemini CLI + Cline-Trinity | Week 18 | 100+ conversations, <500ms retrieval |
| 6D | Cline-Trinity | Week 21 | 5 models, <30s swap, zero downtime |
| 6E | Cline-Kat | Week 23 | WER <5%, 5+ languages |
| 6F | Cline-Trinity | Week 26 | <4h training, >50% loss reduction |

---

## Documentation & Knowledge Management 📚

### Purpose
This pillar establishes the scholarly research differentiation and is documented for team coordination, implementation tracking, and knowledge transfer. All documentation is centralized in the MkDocs internal knowledge base.

### Documentation Location
- **Strategic Planning Hub**: `internal_docs/01-strategic-planning/PILLARS/PILLAR-2-SCHOLAR-DIFFERENTIATION.md`
- **Navigation Path**: Internal Knowledge Base → Strategic Planning → Execution Pillars → Scholar Differentiation
- **MkDocs Config**: `mkdocs-internal.yml` references this document with anchor links to phases

### Related Research & Analysis
This pillar is informed by and references:
- **Research Critical Path (P0)**: `02-research-lab/RESEARCH-P0-CRITICAL-PATH.md` - Foundational research
- **Ancient Greek Research**: Session 3 in Research-P0 - Embedding strategies
- **Multi-Model Support**: Research threads on model management
- **Comprehensive Report**: `02-research-lab/XOE-NOVAI-RESEARCH-REPORT-2026-02-11.md`

### Documentation Standards
- **Phase documents**: Each phase (6A-6F) has dedicated section with objectives and dependencies
- **Progress tracking**: Status tracked in Vikunja PM and memory_bank/
- **Research foundation**: Each phase references underlying research in RESEARCH documents
- **Cross-pillar coordination**: Links to PILLAR 1 (dependencies) and PILLAR 3 (integration points)

### Knowledge Transfer
- **Team onboarding**: New team members start with Executive Context section
- **Phase handoff**: Each phase includes explicit acceptance criteria and documentation requirements
- **Research traceability**: Every feature links back to supporting research documents
- **CI/CD integration**: Automated documentation validation

---

## MkDocs Integration 🔗

### Internal Documentation System

This document is part of the **unified MkDocs internal knowledge base**, accessible locally at:
```bash
mkdocs serve -f mkdocs-internal.yml  # Serves on http://127.0.0.1:8001
```

### Navigation in MkDocs

**Full path**: Strategic Planning → Execution Pillars → Scholar Differentiation

**Related sections in same MkDocs nav**:
- [Roadmap Master Index](../ROADMAP-MASTER-INDEX.md) - Overview of all pillars
- [PILLAR 1: Operational Stability](PILLAR-1-OPERATIONAL-STABILITY.md) - Prerequisite pillar
- [PILLAR 3: Modular Excellence](PILLAR-3-MODULAR-EXCELLENCE.md) - Downstream pillar

**Research links**:
- [Research Critical Path (P0)](../../02-research-lab/RESEARCH-P0-CRITICAL-PATH.md) - Sessions 1-4 directly support phases 6A-6C
- [Comprehensive Research Report](../../02-research-lab/XOE-NOVAI-RESEARCH-REPORT-2026-02-11.md) - Deep analysis of scholarly features

**Implementation guides**:
- [Code Audit Implementation Manual](../../04-code-quality/IMPLEMENTATION-GUIDES/xnai-code-audit-implementation-manual.md) - Implementation patterns used in 6A-6F

### Search in MkDocs

Users can find this pillar via internal search using keywords:
- "scholar differentiation"
- "ancient greek" (Phase 6B)
- "embedding" (Phase 6A)
- "vikunja integration" (Phase 6C)
- "multi-model support" (Phase 6D)
- "voice quality" (Phase 6E)
- "fine-tuning lora" (Phase 6F)

### Public vs. Internal Documentation

- **This document**: Internal only (strategic planning, team coordination)
- **Public equivalent**: `docs/04-explanation/expert-knowledge-system-overview.md` contains expert knowledge public documentation
- **Research insights**: Some research findings published to public docs for community knowledge

---

## Related Documents

**← [Back to ROADMAP-MASTER-INDEX](../ROADMAP-MASTER-INDEX.md)**

### Cross-References

**Research Foundations** (from [RESEARCH-MASTER-INDEX](../RESEARCH-MASTER-INDEX.md)):
- [Session 1: Memory & Performance](../research-phases/RESEARCH-P0-CRITICAL-PATH.md#session-1) ← Supports 6A (eager loading strategy)
- [Session 3: Ancient Greek BERT & Embeddings](../research-phases/RESEARCH-P0-CRITICAL-PATH.md#session-3) ← Foundation for 6A & 6B
- [Session 4: Vikunja Integration](../research-phases/RESEARCH-P0-CRITICAL-PATH.md#session-4) ← Foundation for 6C
- [Session 2: Library APIs](../research-phases/RESEARCH-P0-CRITICAL-PATH.md#session-2) ← Supports 6B (Perseus, LSJ)
- Session 7: [Cline CLI Automation](../research-phases/RESEARCH-MASTER-INDEX.md) → Can automate embedding model updates (6A/6D)

**Implementation Dependencies**:
- [PILLAR-1-OPERATIONAL-STABILITY](PILLAR-1-OPERATIONAL-STABILITY.md) → Must complete before 6A (needs Phase 5E library)
- [PILLAR-3-MODULAR-EXCELLENCE](PILLAR-3-MODULAR-EXCELLENCE.md) (Phases 7A-7B) → Requires 6D model registry to work

**Reference Materials**:
- Original complete roadmap: [xoe-novai-implementation-roadmap-v2-COMPLETE.md](../xoe-novai-implementation-roadmap-v2-COMPLETE.md#pillar-2-scholar-differentiation)
- Project brief: [_meta/PHASE-4-5-COMPLETION-SUMMARY.md](../../_meta/PHASE-4-5-COMPLETION-SUMMARY.md)
- Team protocols: [memory_bank/teamProtocols.md](../../memory_bank/teamProtocols.md)

---

**Document Status**: ✅ Ready for Team Execution  
**Last Updated**: February 12, 2026  
**Team Distribution**: Grok MCA (strategic), Cline-Trinity (implementation), Gemini CLI (execution)
