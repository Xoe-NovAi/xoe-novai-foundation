# 🧠 The Xoe-NovAi Expert Knowledge System (EKB)

> **💎 STATUS: DUAL-PURPOSE CORE FEATURE**
> The EKB is a foundational piece of the Xoe-NovAi Foundation stack, serving as the "Long-Term Memory" for all internal agents and models. However, it is architected as a **Portable Knowledge Vault** that can be utilized by external AI assistants (Gemini, Claude, Cline) even outside the Xoe-NovAi environment.

---

## 🏗️ 1. Architecture: The Graph-Markdown Hybrid
The EKB is more than a folder of text; it is a **Knowledge Runtime**.
- **Storage**: Plain Markdown (`.md`) files.
- **Metadata**: YAML frontmatter for RAG-optimal filtering.
- **Relationships**: Bidirectional `[[wikilinks]]` allow AI agents to navigate the knowledge graph and understand concept dependencies.

## 🛠️ 2. Recommended Management Tools
While the EKB is accessible via any text editor, we recommend the following for the best experience:
1.  **Obsidian / Logseq**: Use these to visualize the knowledge graph and manage relationships.
2.  **MkDocs**: The Xoe-NovAi Foundation stack automatically renders the EKB into a searchable documentation portal.
3.  **MCP Servers**: Configure a filesystem MCP server to give your agents direct read/write access to this vault.

## 📥 3. The "Living Brain" Protocol
The EKB is self-populating. All Xoe-NovAi agents follow these mandates:
- **Research Synthesis**: Every deep research turn concludes with a draft EKB entry.
- **Post-Mortem Hook**: Every critical bug fix is documented as a "Mastery Pattern" to prevent regression.
- **Standardization**: Use the `expert-knowledge/_meta/standard_protocol.md` for all new entries.

## 🚀 4. How to Use Externally
To point your own AI assistants at the Xoe-NovAi EKB:
1.  **Context Loading**: Tell your agent to "Read the files in `expert-knowledge/` to understand the project's technical standards."
2.  **Metadata Awareness**: Instruct your agent to prioritize results with `impact_level: high` in the YAML frontmatter.
3.  **Relationship Navigation**: Tell your agent that `[[link]]` syntax denotes a related technical concept.

---
**Vision**: By providing a pre-populated Expert Knowledge Base, Xoe-NovAi allows new developers and agents to reach "Expert Level" understanding of the stack within minutes of cloning the repository.
