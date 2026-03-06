# Memory Bank Archive Index
**Archive Date**: 2026-02-11  
**Reason**: Deprecation - Outdated agent-specific and superseded files  
**Archived By**: Cline (Code Expert Persona)

---

## Archived Files

### Agent-Specific Operational Guidelines (Deprecated)
These files contained operational guidelines for specific AI agents but are now outdated (Jan 27-29, 2026). Current agent coordination is managed through `teamProtocols.md` and `.clinerules/`.

| File | Original Date | Size | Reason for Archive |
|------|---------------|------|-------------------|
| `claude.md` | Jan 27, 2026 | 6.8KB | Agent-specific, outdated operational guidelines |
| `cline.md` | Jan 27, 2026 | 5.3KB | Agent-specific, outdated operational guidelines |
| `gemini.md` | Jan 27, 2026 | 13.3KB | Agent-specific, outdated operational guidelines |
| `grok.md` | Jan 27, 2026 | 5.7KB | Agent-specific, outdated operational guidelines |
| `agent_capabilities_summary.md` | Jan 29, 2026 | 6.9KB | Outdated multi-grok team structure |

### Superseded Protocol Files
| File | Original Date | Size | Reason for Archive |
|------|---------------|------|-------------------|
| `contextProtocols.md` | Feb 10, 2026 | 22.3KB | Integrated into `teamProtocols.md` |
| `mcpConfiguration.md` | Jan 27, 2026 | 5.1KB | Better suited for `expert-knowledge/` |
| `onboardingChecklist.md` | Jan 27, 2026 | 15.7KB | Now in `docs/02-tutorials/onboarding.md` |
| `handoff_to_cline.md` | Feb 7, 2026 | 2.9KB | Specific handoff completed |

### Large Context Packs (Deprecated)
| File | Original Date | Size | Reason for Archive |
|------|---------------|------|-------------------|
| `GROK_CONTEXT_PACK_v1.5.0.md` | Feb 6, 2026 | 92.5KB | Outdated Grok-specific context pack |

---

## Active Memory Bank Files (Post-Archive)

The following files remain active in `memory_bank/`:

### Core Context (Essential)
- `activeContext.md` - Current priorities and status
- `projectbrief.md` - Mission and Maat ideals
- `techContext.md` - Technical stack and constraints
- `systemPatterns.md` - Architectural decisions
- `progress.md` - Work tracking and milestones

### Team & Coordination
- `teamProtocols.md` - AI team coordination (consolidated)
- `productContext.md` - UX and market context
- `environmentContext.md` - Dev environment setup

---

## Migration Notes

### For Agent Guidelines
Current agent operational guidelines are now managed through:
1. `.clinerules/` directory (Cline-specific)
2. `teamProtocols.md` (All-agent coordination)
3. `expert-knowledge/` (Technical mastery)

### For Context Protocols
Context loading protocols have been integrated into `teamProtocols.md` Section 3: "Context Loading & Memory Bank Protocol".

### For MCP Configuration
MCP server configurations should be moved to `expert-knowledge/tools/mcp-configuration.md` if still relevant.

### For Onboarding
Onboarding content has been migrated to `docs/02-tutorials/onboarding.md` following Diátaxis framework.

---

## Restoration

If any archived file needs to be restored:
1. Copy from `memory_bank/_archive/2026-02-11_deprecated/`
2. Update content to current standards
3. Add frontmatter with `update_type: restored-from-archive`
4. Verify against current `activeContext.md` for consistency

---

**Archive Status**: ✅ Complete  
**Total Files Archived**: 10  
**Space Freed**: ~170KB from active memory_bank
