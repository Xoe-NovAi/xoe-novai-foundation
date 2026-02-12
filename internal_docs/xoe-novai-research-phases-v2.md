# XOE-NOVAI RESEARCH PHASES v2.0: EXPANSION PRIORITIES
## Scholar-Focused Research Requests for Future Sessions
**Prepared By**: Claude Sonnet 4.5 (Implementation Architect)  
**Date**: February 12, 2026  
**Purpose**: Break down scholarly research tool development into manageable, prioritized phases

---

## RESEARCH PHASE CATEGORIZATION (UPDATED)

This document organizes comprehensive research for transforming Xoe-NovAi into a world-class scholarly research tool. Research is structured based on:
- **Criticality** (P0-P3)
- **Scholar Value** (Ancient Greek specialization priority)
- **Dependencies** (what blocks what)
- **Impact** (academic credibility vs. technical vs. operational)
- **Complexity** (research depth required)

---

# CRITICAL PATH RESEARCH (P0) - Sessions 1-6

## SESSION 1: MEMORY & PERFORMANCE OPTIMIZATION
**Duration**: 2-3 hours | **Priority**: P0 | **Blocking**: Phase 5A execution

[Same as original v1.0 - no changes needed]

---

## SESSION 2: LIBRARY CURATION SYSTEM ARCHITECTURE (NEW - HIGH PRIORITY)
**Duration**: 4-5 hours | **Priority**: P0 | **Blocking**: Phase 5E execution

### Research Areas

#### 1. Multi-Library API Integration Strategy
**Context**: Need to integrate multiple library APIs for comprehensive metadata enrichment.

**Research Needed**:
1. **OpenLibrary API**:
   - Rate limits and authentication requirements
   - Coverage (how complete is their catalog?)
   - API response time and reliability
   - Offline caching strategy

2. **WorldCat API**:
   - OCLC API access (authentication, pricing)
   - Coverage for Ancient Greek texts
   - Bibliographic data quality
   - OCLC number resolution

3. **Perseus Digital Library API**:
   - CTS URN resolution system
   - TEI XML parsing (Greek text markup)
   - API stability and availability
   - Offline mirroring strategy (legal considerations)

4. **arXiv API**:
   - Category system for paper classification
   - Rate limits (100 requests/5 minutes)
   - Metadata completeness
   - PDF download integration

5. **CrossRef API**:
   - DOI resolution
   - Citation metadata
   - Journal impact factors
   - Rate limits and authentication

**Deliverable Requested**:
- API comparison matrix (coverage, rate limits, data quality, cost)
- Integration architecture (parallel vs. sequential API calls)
- Caching strategy (when to refresh, TTL recommendations)
- Error handling (fallback when APIs unavailable)
- Legal considerations (terms of service, data usage)

---

#### 2. Domain Classification System
**Context**: Need to automatically classify documents into domains (classics, philosophy, esoteric, technical, science).

**Research Needed**:
1. **Classification Approaches**:
   - Rule-based (keyword lists, regex patterns)
   - ML-based (supervised classifier, zero-shot)
   - Hybrid (rules + ML)
   - Accuracy tradeoffs

2. **Training Data**:
   - Where to get labeled examples?
   - How many examples needed per domain?
   - Active learning (improve over time)

3. **Sub-Domain Classification**:
   - Classics: Greek, Latin, Hebrew, Coptic
   - Philosophy: Pre-Socratic, Classical, Hellenistic, Medieval, Modern
   - Esoteric: Hermeticism, Gnosticism, Kabbalah, Alchemy, Tarot
   - Technical: Languages, frameworks, tools, patterns
   - Science: Physics, Chemistry, Biology, Math, CS

4. **Multi-Label Classification**:
   - Document can belong to multiple domains (Plato = Classics + Philosophy)
   - How to handle overlaps?
   - Confidence scores

**Deliverable Requested**:
- Classification algorithm recommendation (rule-based, ML, hybrid)
- Domain taxonomy (hierarchical structure)
- Training data acquisition strategy
- Accuracy targets (> 95% for primary domain)
- Implementation guide (libraries, code examples)

---

#### 3. Dewey Decimal Automation
**Context**: Need to map documents to Dewey Decimal Classification (DDC) for academic compatibility.

**Research Needed**:
1. **DDC System**:
   - Structure (100s, 10s, 1s divisions)
   - Classics coverage (180-189 for Ancient philosophy)
   - Technical documentation categories (000-099 for CS, 500-599 for science)

2. **Automated Mapping**:
   - Use OpenLibrary DDC mappings
   - Rule-based DDC assignment (domain → DDC range)
   - ML-based DDC prediction
   - Confidence thresholds

3. **DDC Database**:
   - Where to get full DDC database? (OCLC licensing?)
   - Open alternatives (Universal Decimal Classification?)
   - Build own simplified DDC-lite?

**Deliverable Requested**:
- DDC mapping strategy (API, database, rules)
- Coverage analysis (what % of documents can be mapped?)
- Implementation guide (code examples)
- Licensing considerations

---

#### 4. Authority Scoring System
**Context**: Need to assess source quality (peer-reviewed, canonical texts, technical specs vs. blog posts).

**Research Needed**:
1. **Authority Signals**:
   - Domain indicators (`.edu`, `.gov`, `.org` vs. `.com`)
   - Publication type (peer-reviewed journal, book, conference, blog)
   - Author credentials (h-index, affiliations)
   - Citation count (Google Scholar, CrossRef)
   - Source reputation (Perseus, arXiv, JSTOR vs. random blog)

2. **Scoring Formula**:
   - Weighted combination of signals
   - Domain-specific weights (classics: canonical editions weighted higher)
   - Threshold for inclusion (> 0.7 for most domains)
   - Adjustable per use case

3. **Canonical Text Lists**:
   - Classics: Perseus Digital Library, Loeb Classical Library
   - Philosophy: Stanford Encyclopedia of Philosophy (SEP)
   - Science: arXiv, peer-reviewed journals
   - Technical: Official documentation, RFCs

**Deliverable Requested**:
- Authority scoring formula (pseudocode)
- Signal weight recommendations per domain
- Canonical source lists (top 100 per domain)
- Implementation guide (web scraping, API queries)

---

#### 5. Technical Manual Library Structure
**Context**: Need to curate high-quality technical documentation for AI coding assistants (Cline, Gemini CLI).

**Research Needed**:
1. **Content Sources**:
   - Official docs (Python, Rust, Docker, Kubernetes, FastAPI, etc.)
   - Framework guides (React, Vue, Flask, Django)
   - Tool manuals (Git, Podman, make, pytest)
   - Best practices (12-factor app, SOLID principles, design patterns)
   - Code examples (verified, tested snippets)

2. **Storage Structure**:
   - Directory hierarchy (languages/, frameworks/, tools/, patterns/)
   - Metadata schema (language version, framework version, last updated)
   - Versioning strategy (track documentation versions)

3. **AI Assistant Integration**:
   - Context injection (when Cline implements, inject relevant docs)
   - Real-time lookup API (`get_technical_reference("fastapi", "dependency injection")`)
   - Example retrieval (`find_code_examples("pytest", "fixtures")`)
   - Best practice checks (`validate_against_best_practices(code, "python")`)

4. **Auto-Update Strategy**:
   - Monitor official doc sites for updates
   - Crawl GitHub READMEs for new tools
   - Version compatibility checks

**Deliverable Requested**:
- Technical manual taxonomy (20+ frameworks/tools covered)
- Storage structure (directory hierarchy, metadata schema)
- AI assistant integration API design
- Auto-update architecture (crawlers, monitoring)
- Priority list (which tools/frameworks first?)

---

#### 6. Automated Curation Workflow
**Context**: Need end-to-end automation from source discovery → classification → storage.

**Research Needed**:
1. **Trigger Mechanisms**:
   - Scheduled (cron job daily for new content)
   - Manual (user-initiated for specific URLs)
   - API-driven (external tools trigger curation)
   - Watch (file system watcher for new documents)

2. **Quality Gates**:
   - Language confidence > 90%
   - Authority score > 0.7 (adjustable)
   - Completeness (min 500 words for articles, 50 pages for books)
   - Duplication check (SHA256 hash)
   - Format validation (valid UTF-8, parseable)

3. **Error Handling**:
   - API failures (retry logic, fallback to cache)
   - Classification uncertainty (flag for manual review)
   - Low authority score (discard or flag)
   - Duplicate detection (merge metadata, keep best version)

4. **Performance**:
   - Parallel processing (10 documents concurrently)
   - Caching (API responses, embeddings)
   - Rate limiting (respect API limits)
   - Progress tracking (how many processed, how many queued)

**Deliverable Requested**:
- Workflow diagram (Mermaid)
- Trigger mechanism implementations (code examples)
- Quality gate logic (pseudocode)
- Error handling strategies
- Performance benchmarks (documents/hour)

---

### Deliverables Expected (Session 2)
- Multi-library API integration architecture
- Domain classification system design
- Dewey Decimal mapping strategy
- Authority scoring formula
- Technical manual library structure
- Automated curation workflow diagram
- Implementation guide (30-50 pages)

---

## SESSION 3: ANCIENT GREEK BERT & EMBEDDINGS RESEARCH (NEW - HIGH PRIORITY)
**Duration**: 4-5 hours | **Priority**: P0 | **Blocking**: Phase 6A execution

### Research Areas

#### 1. Ancient-Greek-BERT Evaluation
**Context**: Need to validate Ancient-Greek-BERT quality for scholarly use.

**Research Needed**:
1. **Model Details**:
   - Model: `pranaydeeps/Ancient-Greek-BERT`
   - Training corpus (Perseus, TLG, other?)
   - Training methodology (masked language modeling, etc.)
   - Model size (parameters, memory footprint)
   - Inference speed (CPU, GPU)

2. **Quality Assessment**:
   - Lemmatization accuracy (test on Plato's Republic)
   - Semantic similarity (test on philosophical concepts)
   - Comparison with multilingual BERT
   - Scholar validation (publications citing this model?)

3. **Preprocessing Requirements**:
   - Polytonic Greek handling (diacritics, breathing marks)
   - Sigma variants (σ/ς) normalization
   - Unicode normalization (NFC vs. NFD)
   - Tokenization (word vs. subword)

4. **Fine-Tuning Potential**:
   - Domain-specific fine-tuning (philosophical texts)
   - Contrastive learning (improve similarity)
   - Few-shot learning (adapt to rare words)
   - Cost-benefit of fine-tuning

**Deliverable Requested**:
- Ancient-Greek-BERT quality benchmarks (accuracy, speed)
- Preprocessing pipeline design
- Comparison with alternatives (multilingual BERT, XLM-R)
- Fine-tuning recommendations (optional)
- Implementation guide (code examples)

---

#### 2. Krikri-7B-Instruct Integration
**Context**: 7B parameter model for Modern + Ancient Greek, instruction-following capability.

**Research Needed**:
1. **Model Details**:
   - Model: `ilsp/Krikri-7B-Instruct`
   - Training corpus (Modern Greek + Ancient Greek corpus?)
   - Context window (4096 tokens?)
   - Quantization options (4-bit GGUF for memory efficiency)

2. **Use Cases**:
   - Embedding generation (alternative to Ancient-Greek-BERT)
   - Reranking (rerank Ancient-Greek-BERT results)
   - Text generation (summaries, translations)
   - Question answering (answer questions about Greek texts)

3. **Memory Optimization** (Critical for 16GB system):
   - Quantization: 4-bit GGUF reduces 7B to ~4GB RAM
   - Lazy loading: Only load when Ancient Greek query detected
   - CPU inference (llama.cpp, no GPU required)
   - Offloading strategy (swap to disk when not in use)

4. **Integration with Ancient-Greek-BERT**:
   - Hybrid approach (BERT for embeddings, Krikri for generation)
   - When to use each model?
   - Performance tradeoffs

**Deliverable Requested**:
- Krikri-7B quality benchmarks (generation quality, QA accuracy)
- Memory optimization strategy (quantization, lazy loading)
- Hybrid integration architecture (BERT + Krikri)
- Use case recommendations (when to use Krikri vs. BERT)
- Implementation guide (llama.cpp integration, GGUF conversion)

---

#### 3. Domain-Specific Embeddings Research
**Context**: Need embeddings for science (scienceBERT), philosophy (philosophyBERT), code (codeBERT), etc.

**Research Needed**:
1. **scienceBERT**:
   - Model: `allenai/sciencebert_scivocab_uncased`
   - Training corpus (scientific papers)
   - Performance on science vs. general BERT
   - Use cases (physics, chemistry, biology papers)

2. **philosophyBERT**:
   - Model: `guymorlan/philosophy-bert`
   - Training corpus (philosophical texts)
   - Performance on philosophy vs. general BERT
   - Use cases (philosophy papers, arguments)

3. **codeBERT**:
   - Model: `microsoft/codebert-base`
   - Training corpus (code + natural language)
   - Performance on code understanding
   - Use cases (API documentation, code examples)

4. **Other Domain Embeddings**:
   - Legal: `nlpaueb/legal-bert-base-uncased`
   - Biomedical: `dmis-lab/biobert-base-cased-v1.1`
   - Finance: `ProsusAI/finbert`

**Deliverable Requested**:
- Domain embedding comparison matrix (performance, use cases)
- Recommended embeddings per domain (top 3 choices)
- Integration strategy (how to select embedding dynamically)
- Performance benchmarks (retrieval quality, speed)

---

#### 4. Dynamic Embedding Selection Logic
**Context**: Need to automatically select best embedding(s) for query based on language/domain/context.

**Research Needed**:
1. **Language Detection**:
   - Library: `langdetect`, `fasttext`
   - Accuracy for Ancient Greek (grc) vs. Modern Greek (el)
   - Handling multilingual queries

2. **Domain Inference**:
   - From knowledge base context
   - From query keywords
   - From user profile/history
   - Confidence thresholds

3. **Selection Algorithm**:
   - Rule-based (if lang=grc → ancient_greek_bert)
   - ML-based (classifier predicts best embedding)
   - Hybrid (rules + ML fallback)

4. **Multi-Embedding Retrieval**:
   - When to use multiple embeddings?
   - Reciprocal Rank Fusion (RRF) for combining results
   - Performance impact (latency, quality)

**Deliverable Requested**:
- Dynamic selection algorithm (pseudocode, flowchart)
- Language detection strategy
- Domain inference logic
- Multi-embedding retrieval architecture (RRF)
- Implementation guide (code examples)

---

#### 5. Embedding Storage & Management
**Context**: Need efficient storage for multiple embeddings per document.

**Research Needed**:
1. **Storage Format**:
   - NumPy arrays (`.npy` files)
   - HDF5 (hierarchical, compressed)
   - Database (PostgreSQL with pgvector, Qdrant)
   - File system organization

2. **Lazy Loading**:
   - LRU cache (1GB max per model)
   - On-demand loading (not all embeddings in memory)
   - Preloading strategy (common models always loaded)

3. **Versioning**:
   - Track embedding model version in metadata
   - Re-embedding strategy when models update
   - Backward compatibility (old embeddings still searchable)

4. **Memory Optimization**:
   - FP16 quantization (reduce memory by 50%)
   - Embedding compression (PQ, OPQ)
   - Disk offloading (swap to disk when not used)

**Deliverable Requested**:
- Storage architecture (file system vs. database)
- Lazy loading strategy (LRU cache, preloading)
- Versioning system design
- Memory optimization recommendations

---

### Deliverables Expected (Session 3)
- Ancient-Greek-BERT quality benchmarks and implementation guide
- Krikri-7B memory optimization and hybrid integration strategy
- Domain-specific embedding comparison and recommendations
- Dynamic embedding selection algorithm
- Embedding storage and management architecture
- Complete implementation guide (40-60 pages)

---

## SESSION 4: VIKUNJA MEMORY_BANK INTEGRATION RESEARCH (NEW - HIGH PRIORITY)
**Duration**: 3-4 hours | **Priority**: P0 | **Blocking**: Phase 6C execution

### Research Areas

#### 1. Vikunja API Capabilities
**Context**: Need to use Vikunja as experimental memory_bank for conversations, context, handoffs.

**Research Needed**:
1. **Vikunja REST API**:
   - Authentication (API token, JWT)
   - Task CRUD operations
   - Project/namespace management
   - Label and tag system
   - Comment system (for agent communication)
   - Attachment support

2. **API Client Libraries**:
   - Official Python client?
   - Community libraries?
   - Need to implement our own?

3. **Rate Limits**:
   - API rate limits (if any)
   - Bulk operations (create 100 tasks at once?)

4. **Search Capabilities**:
   - Full-text search
   - Keyword search
   - Filter by labels, tags, assignee
   - Search performance

**Deliverable Requested**:
- Vikunja API documentation summary
- Python client library recommendation (or implementation guide)
- API usage examples (create task, search tasks, etc.)
- Rate limit considerations

---

#### 2. Memory Types & Task Structure
**Context**: Need to design how different memory types map to Vikunja tasks.

**Research Needed**:
1. **Conversation Memory**:
   - Store chat history as tasks
   - One task per conversation or per message?
   - How to format conversation in task description?
   - How to retrieve past conversations?

2. **Context Snippets**:
   - Store important decisions, learnings, patterns
   - Categorization (decision, learning, pattern)
   - Search and retrieval

3. **Handoff Memory**:
   - Agent-to-agent transition context
   - Format (from, to, context, files modified, blockers)
   - Retrieval (get last handoff to agent X)

4. **Reference Memory**:
   - Store links to docs, code, external resources
   - Categorization (docs, code, research, data)
   - Automatic link validation?

**Deliverable Requested**:
- Memory type taxonomy (4 types defined)
- Task structure design (title, description, labels, tags)
- Metadata schema (JSON in description or custom fields?)
- Retrieval patterns (how to search each memory type)

---

#### 3. Chainlit UI Integration
**Context**: Need to integrate memory_bank with Chainlit UI for user interaction.

**Research Needed**:
1. **Save Conversation Button**:
   - Add button to Chainlit sidebar
   - Prompt user for conversation title/summary
   - Store to Vikunja automatically

2. **Context Recall Interface**:
   - Add "Recall Context" button
   - Search interface (keyword search)
   - Display results in sidebar
   - Click result → load context into current conversation

3. **Visual Indicators**:
   - Show icon when context from Vikunja is active
   - "Using context from: [Task #1234]"
   - Highlight recalled context in chat

4. **Auto-Save Option**:
   - Auto-save every N messages
   - User can disable
   - Background save (non-blocking)

**Deliverable Requested**:
- Chainlit UI mockups (wireframes)
- Integration architecture (Chainlit → Vikunja API)
- User interaction flow (save, recall, display)
- Implementation guide (Chainlit customization)

---

#### 4. Performance & Scalability
**Context**: Need to ensure memory_bank performs well with 1000s of conversations/contexts.

**Research Needed**:
1. **Search Performance**:
   - Vikunja search speed with 10K+ tasks
   - Indexing strategy (does Vikunja have full-text index?)
   - Caching (cache recent searches)

2. **Storage Limits**:
   - Vikunja database size limits (SQLite vs. PostgreSQL)
   - Task description size limits
   - Attachment size limits

3. **Retrieval Latency**:
   - Target: < 500ms for context recall
   - API call latency
   - Network overhead (localhost = fast)

4. **Backup & Export**:
   - Export all memory_bank data (JSON, CSV)
   - Backup strategy (automated daily)
   - Import to new Vikunja instance

**Deliverable Requested**:
- Performance benchmarks (search speed, storage limits)
- Scalability recommendations (when to upgrade database)
- Backup and export strategy
- Monitoring setup (track usage, performance)

---

#### 5. Experimental Features & Future Vision
**Context**: Vikunja memory_bank is experimental, need to explore future potential.

**Research Needed**:
1. **Advanced Memory Features**:
   - Semantic search (use embeddings for similarity)
   - Automatic summarization (summarize long conversations)
   - Memory clustering (group related contexts)
   - Temporal search (find conversations from last week)

2. **Multi-User Coordination**:
   - Shared memory_bank (team knowledge base)
   - Permissions (who can read/write which memories?)
   - Conflict resolution (concurrent edits)

3. **Integration with RAG**:
   - Use memory_bank as additional context source for RAG
   - Retrieve past conversations relevant to current query
   - Hybrid retrieval (documents + memory_bank)

4. **AI-Powered Memory Management**:
   - Auto-tagging (AI suggests tags for conversations)
   - Auto-summarization (AI generates summaries)
   - Auto-archival (AI archives old, irrelevant memories)

**Deliverable Requested**:
- Future feature roadmap (prioritized)
- Advanced memory architecture (semantic search, RAG integration)
- Multi-user coordination design (permissions, conflicts)
- AI-powered memory management strategy

---

### Deliverables Expected (Session 4)
- Vikunja API client library and usage guide
- Memory type taxonomy and task structure design
- Chainlit UI integration mockups and implementation guide
- Performance benchmarks and scalability recommendations
- Future feature roadmap for memory_bank
- Complete implementation guide (30-40 pages)

---

## SESSION 5: OBSERVABLE ARCHITECTURE & IMPLEMENTATION
**Duration**: 3-4 hours | **Priority**: P0 | **Blocking**: Phase 5B execution

[Same as original v1.0, but add library operation metrics]

**Additional Library Metrics**:
- Document ingestion rate (docs/hour)
- Domain classification accuracy (%)
- Language detection metrics (grc, la, heb)
- Library API call rate and success rate
- Knowledge base quality metrics (authority scores)
- Ancient Greek BERT inference time (ms per text)

---

## SESSION 6: AUTHENTICATION & AUTHORIZATION DESIGN
**Duration**: 3-4 hours | **Priority**: P0 | **Blocking**: Phase 5C execution

[Same as original v1.0 - no changes needed]

---

# SCHOLAR DIFFERENTIATION RESEARCH (P1) - Sessions 7-10

## SESSION 7: ANCIENT GREEK SCHOLARLY FEATURES RESEARCH (NEW - HIGH PRIORITY)
**Duration**: 5-6 hours | **Priority**: P1 | **Blocking**: Phase 6B execution

### Research Areas

#### 1. Classical Language Toolkit (CLTK) Integration
**Context**: CLTK is comprehensive library for Ancient Greek/Latin processing.

**Research Needed**:
1. **CLTK Capabilities**:
   - Tokenization (word splitting, clitic handling)
   - Lemmatization (dictionary form reduction)
   - POS tagging (part of speech)
   - Morphological analysis (case, number, gender, tense, mood, voice)
   - NER (named entity recognition for proper names)

2. **Model Quality**:
   - Accuracy on canonical texts (Plato, Homer, Aristotle)
   - Performance on different dialects (Attic, Ionic, Doric)
   - Speed (characters/second)
   - Memory footprint

3. **Installation & Setup**:
   - CLTK package installation
   - Model downloads (Ancient Greek models)
   - Offline operation (models stored locally)

4. **API Design**:
   - Input: Ancient Greek text
   - Output: Tokenized, lemmatized, POS-tagged, morphologically analyzed
   - Integration with embeddings (use lemmas for embedding lookup)

**Deliverable Requested**:
- CLTK quality benchmarks (accuracy, speed, memory)
- API design (input/output format)
- Integration strategy (CLTK → embeddings, CLTK → UI)
- Implementation guide (installation, model setup, code examples)

---

#### 2. LSJ Lexicon Integration
**Context**: Liddell-Scott-Jones (LSJ) is the standard Ancient Greek-English lexicon.

**Research Needed**:
1. **Data Source**:
   - Perseus Digital Library XML export
   - TEI XML structure (how to parse?)
   - License considerations (public domain?)
   - Size (how many entries?)

2. **Lexicon Features**:
   - Word lookup (lemma → definition)
   - Etymology
   - Usage examples (citations from classical texts)
   - Morphological variants (handle all inflected forms)
   - Cross-references (related words, compounds)

3. **Database Design**:
   - SQLite (simple, offline)
   - Full-text search (FTS5)
   - Lemma → definition mapping
   - Compound word handling (ἀπολύω → ἀπό + λύω)

4. **UI Integration**:
   - Chainlit hoverable tooltips on Greek words
   - Click word → show LSJ definition in sidebar
   - Pronunciation guide (transliteration)
   - Export definition (copy to clipboard)

**Deliverable Requested**:
- LSJ XML parsing strategy (TEI → SQLite)
- Database schema design
- Lookup API design (lemma → definition)
- UI integration mockups (tooltips, sidebar)
- Implementation guide (XML parsing, database creation, UI code)

---

#### 3. Perseus Digital Library API Integration
**Context**: Perseus is the largest digital library of Ancient Greek/Latin texts.

**Research Needed**:
1. **Perseus API**:
   - API endpoints (text retrieval, lexicon lookup, commentary)
   - CTS URN system (how does it work?)
   - Rate limits
   - Authentication requirements

2. **CTS URN Resolution**:
   - Format: `urn:cts:greekLit:tlg0012.tlg001.perseus-grc2:1.1-1.100`
   - How to map author abbreviations to CTS codes? (Pl. → tlg0059)
   - How to map work abbreviations to CTS codes? (R. → tlg030)
   - How to resolve reference (514a → line numbers)?

3. **Offline Caching**:
   - Cache all retrieved texts locally
   - Build offline mirror of frequently-accessed works
   - Graceful degradation if Perseus API unavailable
   - Update strategy (refresh cache weekly?)

4. **Parallel Text Support**:
   - Retrieve Greek text + English translations
   - Display side-by-side
   - Sentence alignment (how to align Greek/English?)
   - Multiple translations (Jowett, Bloom, Reeve)

**Deliverable Requested**:
- Perseus API documentation summary
- CTS URN resolution logic (author/work/reference → URN)
- Offline caching architecture
- Parallel text display design (mockups)
- Implementation guide (API calls, caching, UI)

---

#### 4. Citation Formatting (Classical References)
**Context**: Need to automatically detect and format classical citations.

**Research Needed**:
1. **Citation Formats**:
   - Standard: Author, Work, Book.Chapter.Section (or Line)
   - Examples: Pl. R. 514a, Hom. Il. 1.1-10, Arist. EN 1094a
   - Variations (different abbreviation systems)

2. **Auto-Detection**:
   - Regex patterns for common formats
   - Handling ambiguity (R. = Republic or Rhetoric?)
   - Context-based disambiguation

3. **Citation Resolver**:
   - Map abbreviations to full CTS URN
   - Link to Perseus Digital Library
   - Retrieve text snippet (show preview)

4. **Export**:
   - BibTeX format for academic papers
   - Chicago/MLA style
   - Custom formats

**Deliverable Requested**:
- Citation detection regex patterns
- Citation resolver logic (abbreviation → CTS URN)
- Export format templates (BibTeX, Chicago, MLA)
- Implementation guide (regex, resolver, export)

---

#### 5. Scholarly UI Features
**Context**: Need UI features for scholars (morphological hover, commentary, text comparison).

**Research Needed**:
1. **Morphological Hover**:
   - Hover over Greek word → show lemma, POS, morphology
   - Implementation (JavaScript, Chainlit customization)
   - Performance (process entire text upfront or on-demand?)

2. **Commentary Integration**:
   - Link to scholarly commentary (if available)
   - Extract from Perseus
   - Display in sidebar or modal

3. **Text Comparison**:
   - Compare different editions (Oxford, Teubner, OCT)
   - Highlight textual variants
   - Show critical apparatus

4. **Export Options**:
   - Export as PDF with formatting
   - Export as LaTeX for academic papers
   - Export citations in BibTeX

**Deliverable Requested**:
- UI mockups (morphological hover, commentary, text comparison)
- Implementation strategy (JavaScript, Chainlit customization)
- Performance considerations (caching, lazy loading)
- Export format templates

---

### Deliverables Expected (Session 7)
- CLTK integration guide (installation, API, accuracy benchmarks)
- LSJ lexicon database design and implementation guide
- Perseus API integration strategy and CTS URN resolver
- Citation detection and formatting system
- Scholarly UI feature mockups and implementation guide
- Complete implementation guide (60-80 pages)

---

## SESSION 8: MODULAR SERVICE ARCHITECTURE RESEARCH (NEW - HIGH PRIORITY)
**Duration**: 4-5 hours | **Priority**: P1 | **Blocking**: Phase 7A execution

### Research Areas

#### 1. Service Plugin System Design
**Context**: Need plugin system for enable/disable services via config.

**Research Needed**:
1. **Plugin Architectures**:
   - Python entry points (setuptools)
   - Import hooks (sys.meta_path)
   - Dynamic module loading (importlib)
   - Microkernel architecture (core + plugins)

2. **Service Manifest Format**:
   - YAML vs. TOML vs. JSON
   - Required fields (name, version, dependencies, resources)
   - Optional fields (config, hooks, APIs)

3. **Dependency Resolution**:
   - Graph-based (NetworkX, topological sort)
   - Circular dependency detection
   - Optional dependencies (feature flags)

4. **Hot-Plugging**:
   - Add/remove services without restart (challenging)
   - FastAPI sub-app hot-loading (non-trivial)
   - State migration (if service stores state)

**Deliverable Requested**:
- Plugin system architecture (diagram)
- Service manifest format (YAML schema)
- Dependency resolution algorithm
- Hot-plugging feasibility analysis (phased approach)
- Implementation guide (entry points, dynamic loading)

---

#### 2. Service Templates
**Context**: Provide templates for creating new services easily.

**Research Needed**:
1. **Template Types**:
   - Library service (Python module, no ports)
   - API service (FastAPI sub-app, HTTP endpoints)
   - Worker service (background task processing)
   - UI service (Chainlit, MkDocs, etc.)

2. **Template Structure**:
   - Minimal files needed
   - Boilerplate code (service.py, api.py, tests)
   - Docker files (if containerized)

3. **Code Generation**:
   - CLI tool (`xnai service create <name> --template=library`)
   - Jinja2 templating (fill in placeholders)
   - Interactive prompts (ask user for details)

4. **Example Services**:
   - Ancient Greek processor (library)
   - Technical manual API (API service)
   - Voice interface (UI service)

**Deliverable Requested**:
- Service template designs (4 types)
- Template file structure
- Code generation CLI tool design
- Example service implementations

---

#### 3. Portability Strategy
**Context**: Services should be usable outside Xoe-NovAi (standalone Docker images).

**Research Needed**:
1. **Standalone Docker Images**:
   - Minimal dependencies (don't require full stack)
   - Clear API documentation
   - Example integration code

2. **Dependency Minimization**:
   - Identify core dependencies
   - Optional dependencies (feature flags)
   - Graceful degradation (if dependency missing)

3. **API Standardization**:
   - REST API design (OpenAPI spec)
   - gRPC option (for performance)
   - Clear input/output contracts

4. **Documentation**:
   - Standalone README (how to use outside Xoe-NovAi)
   - API documentation (generated from OpenAPI)
   - Integration examples (Python, curl, JavaScript)

**Deliverable Requested**:
- Standalone Docker image design (Dockerfile template)
- Dependency minimization strategy
- API standardization guidelines (OpenAPI)
- Portability documentation template

---

### Deliverables Expected (Session 8)
- Plugin system architecture and implementation guide
- Service template designs and code generation tool
- Portability strategy and standalone Docker image design
- Complete implementation guide (40-50 pages)

---

## SESSION 9: DISTRIBUTED TRACING STRATEGY
**Duration**: 2-3 hours | **Priority**: P1 | **Blocking**: Phase 5D execution

[Same as original v1.0, but add library operation spans]

**Additional Spans for Library Operations**:
- Document ingestion (crawl → classify → enrich → store)
- Domain classification (text → domain)
- Language detection (text → language)
- API calls (OpenLibrary, Perseus, arXiv)
- Embedding generation (text → embedding)

---

## SESSION 10: VOICE QUALITY EVALUATION
**Duration**: 3-4 hours | **Priority**: P1 | **Blocking**: Phase 6E execution

[Same as original v1.0 - lower priority for scholar tool, but still valuable]

---

# OPERATIONAL EXCELLENCE RESEARCH (P2) - Sessions 11-13

## SESSION 11: BUILD SYSTEM MODERNIZATION RESEARCH
**Duration**: 3-4 hours | **Priority**: P2 | **Blocking**: Phase 7B execution

[Same as original v1.0 - Taskfile vs. Nix vs. Keep-Make]

---

## SESSION 12: SECURITY HARDENING RESEARCH
**Duration**: 3-4 hours | **Priority**: P2 | **Blocking**: Phase 7C execution

[Same as original v1.0 - Syft, Grype, Cosign]

---

## SESSION 13: RESILIENCE PATTERNS RESEARCH
**Duration**: 2-3 hours | **Priority**: P2 | **Blocking**: Phase 7D execution

[Same as original v1.0 - circuit breakers, chaos engineering]

---

# ACADEMIC POSITIONING RESEARCH (P3) - Sessions 14-16

## SESSION 14: SCHOLAR COMPETITIVE ANALYSIS (NEW - HIGH PRIORITY)
**Duration**: 4-5 hours | **Priority**: P3 | **Blocking**: Phase 8A execution

### Research Areas

#### 1. Perseus Digital Library Deep Dive
**Research Needed**:
- Feature set (what does Perseus offer?)
- UI/UX (strengths, weaknesses)
- Corpus coverage (how complete?)
- API capabilities
- Pricing/licensing
- Scholar adoption (how widely used?)
- Weaknesses (what are the pain points?)

**Deliverable**: Feature comparison matrix, gap analysis

---

#### 2. Thesaurus Linguae Graecae (TLG) Deep Dive
**Research Needed**:
- Corpus coverage (10M+ words?)
- Pricing ($400/year individual, $5K+ institutional?)
- API capabilities (if any)
- Scholar adoption (gold standard?)
- Weaknesses (expensive, online-only, no AI)

**Deliverable**: Feature comparison, pricing analysis, gap analysis

---

#### 3. Loeb Classical Library Deep Dive
**Research Needed**:
- Content (parallel Greek/English texts)
- Translation quality (reputation?)
- Pricing ($300/year?)
- Digital platform capabilities
- Weaknesses (expensive, proprietary, no search)

**Deliverable**: Feature comparison, gap analysis

---

#### 4. Zotero Integration Strategy
**Research Needed**:
- Zotero plugin architecture
- Ancient Greek support (none currently?)
- API capabilities
- Integration opportunities (Xoe-NovAi as Zotero plugin?)

**Deliverable**: Integration strategy, plugin feasibility

---

#### 5. Unique Value Proposition Refinement
**Research Needed**:
- Scholar pain points (interviews, surveys)
- Pricing sensitivity (what would scholars pay?)
- Feature priorities (what do scholars need most?)
- Adoption barriers (what would prevent adoption?)

**Deliverable**: UVP statement, positioning strategy, pricing model

---

### Deliverables Expected (Session 14)
- Scholar competitive matrix (Perseus, TLG, Loeb, Zotero)
- Feature gap analysis
- Pricing comparison and recommendations
- UVP refinement (Ancient Greek mastery, sovereign, affordable, AI-powered)
- Go-to-market strategy (target segments, messaging, channels)
- Complete report (30-40 pages)

---

## SESSION 15: ACADEMIC LAUNCH STRATEGY
**Duration**: 3-4 hours | **Priority**: P3 | **Blocking**: Phase 8B execution

### Research Areas

#### 1. Academic Mailing Lists & Conferences
**Research Needed**:
- Classics-L (subscriber count, engagement)
- APA/SCS (membership, reach)
- Digital Humanities conferences (DH2027, etc.)
- Call for papers (submission deadlines)

**Deliverable**: Launch channel strategy

---

#### 2. Early Access Program Design
**Research Needed**:
- Recruitment strategies (where to find PhD students?)
- Incentives (free Scholar Pro, swag, recognition)
- Onboarding process (tutorial, 1-on-1 calls)
- Feedback collection (surveys, interviews)

**Deliverable**: Early access program design (50 PhD students, 10 professors)

---

#### 3. Demo Video Production
**Research Needed**:
- Script writing (problem, solution, demo, CTA)
- Screen recording tools (OBS, SimpleScreenRecorder)
- Voiceover (professional vs. AI TTS)
- Editing (Kdenlive, DaVinci Resolve)
- Hosting (YouTube, PeerTube)

**Deliverable**: Demo video script and production guide

---

#### 4. Landing Page Design
**Research Needed**:
- Scholar-targeted messaging
- Feature highlights (Ancient-Greek-BERT, LSJ, Perseus)
- Testimonials (beta tester quotes)
- Pricing (free for students, $99/year Scholar Pro)
- CTA (start free trial, join waitlist)

**Deliverable**: Landing page mockup and copy

---

### Deliverables Expected (Session 15)
- Academic launch channel strategy (mailing lists, conferences, social media)
- Early access program design (recruitment, onboarding, feedback)
- Demo video script and production guide
- Landing page mockup and copy
- Complete launch plan (20-30 pages)

---

## SESSION 16: ACADEMIC RECOGNITION STRATEGY
**Duration**: 3-4 hours | **Priority**: P3 | **Blocking**: Phase 8C execution

### Research Areas

#### 1. Academic Paper Publication
**Research Needed**:
- Target venues (Digital Humanities journals/conferences)
- Paper structure (abstract, methods, results, discussion)
- Evaluation methodology (accuracy benchmarks, scholar validation)
- Timeline (submission deadlines, review process)

**Deliverable**: Academic paper outline and publication strategy

---

#### 2. Conference Presentation Strategy
**Research Needed**:
- Target conferences (SCS, APA, DH2027)
- Presentation types (lightning talk, full paper, workshop)
- Abstract writing
- Slide design

**Deliverable**: Conference presentation strategy and abstract templates

---

#### 3. Community Building
**Research Needed**:
- Discord server setup (channels, roles, moderation)
- Office hours format (monthly Q&A, webinars)
- Scholar spotlight (feature beta tester research)
- Forum setup (Discourse instance)

**Deliverable**: Community building strategy

---

### Deliverables Expected (Session 16)
- Academic paper outline and publication strategy
- Conference presentation strategy
- Community building plan (Discord, forum, webinars)
- Complete academic recognition strategy (20-30 pages)

---

# RESEARCH SESSION EXECUTION GUIDE

## Updated Research Order (Scholar-Focused)

### Fast Track (10 months to Scholar MVP)
Execute P0 sessions (Sessions 1-6):
1. Session 1: Memory Optimization → Execute Phase 5A
2. **Session 2: Library Curation System → Execute Phase 5E** (NEW)
3. **Session 3: Ancient Greek BERT & Embeddings → Execute Phase 6A** (NEW)
4. **Session 4: Vikunja Memory_Bank → Execute Phase 6C** (NEW)
5. Session 5: Observable → Execute Phase 5B
6. Session 6: Authentication → Execute Phase 5C

**Result**: Scholar-ready system in 10 months

---

### Standard Track (24 months to Academic Credibility)
Execute P0 + P1 sessions (Sessions 1-10):
1-6: (Same as Fast Track)
7. **Session 7: Ancient Greek Scholarly Features → Execute Phase 6B** (NEW)
8. **Session 8: Modular Service Architecture → Execute Phase 7A** (NEW)
9. Session 9: Distributed Tracing → Execute Phase 5D
10. Session 10: Voice Quality → Execute Phase 6E (optional)

**Result**: Ancient Greek mastery + academic credibility in 24 months

---

### Full Track (36 months to Scholar Leadership)
Execute all sessions (Sessions 1-16):
1-10: (Same as Standard Track)
11. Session 11: Build System → Execute Phase 7B
12. Session 12: Security → Execute Phase 7C
13. Session 13: Resilience → Execute Phase 7D
14. **Session 14: Scholar Competitive Analysis → Execute Phase 8A** (NEW)
15. **Session 15: Academic Launch → Execute Phase 8B** (NEW)
16. **Session 16: Academic Recognition → Execute Phase 8C** (NEW)

**Result**: Scholar community leadership in 36 months

---

## Research Session Duration Estimates (Updated)

| Priority | Sessions | Total Hours | Weeks (Part-Time) |
|----------|----------|-------------|-------------------|
| P0 (Critical + Library + Ancient Greek) | 1-6 | 18-24 hours | 4-6 weeks |
| P1 (Scholar Differentiation + Modular) | 7-10 | 14-19 hours | 3-5 weeks |
| P2 (Operational) | 11-13 | 8-11 hours | 2-3 weeks |
| P3 (Academic) | 14-16 | 11-14 hours | 3-4 weeks |
| **Total** | **16 sessions** | **51-68 hours** | **12-18 weeks** |

**Note**: Part-time = 4-6 hours/week of research time

---

## Next Action

**Recommended**: Start with **Session 2 (Library Curation System Research)** or **Session 3 (Ancient Greek BERT Research)** to support immediate scholar features.

**Alternative**: If memory is immediate concern, start with **Session 1 (Memory Optimization)**, then Sessions 2-3 in parallel.

---

**Prepared By**: Claude Sonnet 4.5 (Implementation Architect)  
**Status**: Ready for research session selection  
**Team Coordination**: Via Vikunja (http://localhost:3456)  
**Document Version**: 2.0 (Updated with Scholar + Library + Ancient Greek focus)  
**Last Updated**: February 12, 2026
