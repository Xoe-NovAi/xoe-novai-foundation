# Memory Bank → Vikunja Mapping (v1.0.0)

Overview
- Guidelines for translating memory_bank frontmatter to Vikunja task fields for bulk migration.

Frontmatter Key | Vikunja Field | Transformation Notes
- title | title | Direct
- content | description | Direct
- status | status (or done flag) | Map known statuses to Vikunja statuses; default to backlog
- priority | priority | Map: high=5, medium=3, low=1
- agents | labels | Prefix with agent: or map to labels per project policy
- ma_at_ideals | labels | Prefix ma_at_ with each ideal
- knowledge | labels | Expand to knowledge-domain labels
- domains | labels | Domain labels
- ekb_links | EKB-Link (custom field) | Join into a comma-separated string or array
- author | Owner | Map to owner field (custom or assigned owner)
- date | Date | Convert to string date
- version | Version | Custom field
- account | Account | Custom field or owner

Notes
- If Vikunja doesn’t expose a direct owner field in your setup, map Owner to a custom field.
- For multi-valued frontmatter fields, push as multiple labels where supported.
- The importer should ensure project/namespace creation before task creation.

Sample mapping example
- Frontmatter: { title: 'Active Context', status: 'in_progress', agents: ['Grok MC', 'Gemini CLI'], knowledge: ['Security', 'Platform'] }
- Vikunja: title='Active Context', description='(rendered', labels=['Grok MC','Gemini CLI','Security','Platform'], priority=3)
