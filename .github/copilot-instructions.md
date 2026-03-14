# Omega Stack Repository Instructions

**For**: All Copilot models (Haiku, GPT-4.1, Sonnet, etc.)
**Updated**: 2026-03-14
**Owner**: @arcana-novai

## 1. File Naming Convention (MANDATORY)

Pattern: `{document_type}_{primary_purpose}_{date}_v{version}_{status}`

Types: chronicle, config, report, guide, spec, checkpoint, archive

## 2. Frontmatter (REQUIRED)

All strategic markdown requires YAML with:
- document_type, title, created_by, created_date, version, status

## 3. Code Standards
- Run tests before proposing
- Use squash+rebase merges
- Never commit secrets
- GPG sign main/develop commits

## Questions?
See CUSTOM_INSTRUCTIONS_v1_OPERATIONAL.md for details.
