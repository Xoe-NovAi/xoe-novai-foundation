# Mapping: Memory Bank Frontmatter to Vikunja Fields

Overview
- This document maps memory_bank frontmatter keys to Vikunja task fields to enable reliable bulk import.

Frontmatter Key -> Vikunja Field Mappings
- title -> title
- content (description) -> description
- status -> status
- agents -> labels (or assignees if supported)
- priority -> priority (numeric, if Vikunja uses numeric priority)
- author -> Owner (custom field in Vikunja or equivalent)
- date -> Date (custom field)
- ekb_links -> EKB-Link (custom field)
- version -> Version (custom field)
- account -> Owner/Account (depending on mapping)
- knowledge -> labels
- domains -> labels
- ma_at_ideals -> ma_at_<ideal> labels

Usage Notes
- If a field is missing in frontmatter, rely on sensible defaults in Vikunja (e.g., backlog for status).
- If Vikunja schema changes, update this mapping accordingly.

Examples
- frontmatter:
  title: 'Active Context'
  status: 'in_progress'
  agents: ['Grok MC', 'Gemini CLI']
- mapped to Vikunja labels: ['Grok MC', 'Gemini CLI', 'status-in_progress']
