# External Research Protocol & Privacy Framework — GPT-4.1 Recommendation #6

**Confidence**: 60% (requires validation + privacy review)  
**Last Updated**: 2026-03-14  
**Status**: DRAFT (pending user review)

---

## Problem Statement

**Current State**: No formal schema for web research requests/responses  
**Risk**: Data leakage, privacy exposure, incomplete research results  
**Solution**: Standardized request/response schema with privacy filters

---

## Request/Response Schema

### Request Format

```yaml
---
id: research-req-001
timestamp: 2026-03-14T04:30:00Z
requester: haiku-4.5
scope: public_sources_only  # public_sources_only | private_with_auth | archived_only
query: "Podman user namespace best practices"
sources_excluded: 
  - internal_docs
  - customer_data
  - credentials
categories:
  - infrastructure
  - devops
  - podman
max_results: 20
confidence_target: 90%
---

**Research context**: Implementing GPT-4.1 recommendations for Omega Stack container security
**Use case**: Verify containerization strategy doesn't expose secrets
**Validation**: Results must not reference API keys, tokens, or proprietary info
```

### Response Format

```yaml
---
id: research-resp-001
request_id: research-req-001
timestamp: 2026-03-14T04:45:00Z
sources_count: 18
results_sanitized: true
privacy_check: passed
findings:
  - title: "User Namespaces in Rootless Podman"
    source_url: "https://docs.podman.io/en/latest/"
    relevance: 95%
    excerpt: "[Sanitized excerpt about namespace mapping]"
    is_primary: true
    
  - title: "Podman Security Best Practices"
    source_url: "https://github.com/containers/podman"
    relevance: 87%
    excerpt: "[Sanitized excerpt]"
    is_primary: false

excluded_sources:
  - "stackoverflow.com/q/..." (reason: potentially outdated)
  - "reddit.com/r/..." (reason: unreliable attribution)

research_gaps:
  - "ACL behavior in rootless containers" (insufficient public documentation)
  
confidence_score: 78%
---

**Summary**: 18 vetted sources confirm user namespace approach is sound. No public sources specifically address ACL-podman interaction; recommend consulting Podman maintainers directly.
```

---

## Privacy Filters

### Automatic Redaction Rules

Apply to ALL responses before using/storing:

```regex
# Detect & redact common patterns
[api_key] = /api[_-]?key|secret|token/gi → [REDACTED]
[email] = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g → [email]
[ip_address] = /\b(\d{1,3}\.){3}\d{1,3}\b/g → [ip.x.x.x]
[phone] = /\b(\+?1)?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b/g → [phone]
[credential] = /password|passwd|pwd|secret|credential/gi → [REDACTED]
[proprietary] = /internal|confidential|nda|proprietary/gi → [MARKED:PROPRIETARY]
[pii] = /ssn|credit_card|tax_id/gi → [REDACTED]
```

### Source Validation Rules

**Accept**:
- ✓ Official documentation (github.com/containers, podman.io, etc.)
- ✓ Published research papers (arxiv.org, ieee.org, etc.)
- ✓ Blog posts from recognized experts
- ✓ Archived versions (archive.org, github historical)
- ✓ Open-source project wikis

**Reject**:
- ✗ Paywalled sources
- ✗ Unverified social media (Twitter, Reddit, Forums)
- ✗ Anonymous sources
- ✗ Outdated versions (>5 years old unless historical context)
- ✗ Sources containing unredacted credentials

---

## Scope Boundaries

### What CAN be researched
- Public containerization best practices
- Open-source framework documentation
- Published security research
- Official vendor documentation
- Community wikis and FAQs

### What CANNOT be researched
- Internal company docs (if requested from external)
- Private GitHub repos or gists
- Paywalled academic papers
- Proprietary frameworks
- Customer data or credentials
- Non-public APIs

### Gray Areas (Require Explicit Approval)
- Pre-release software documentation
- Research papers behind institution paywalls
- Unofficial forks or reimplementations
- Archived versions of deprecated projects
- Security vulnerability disclosures (responsible disclosure rules apply)

---

## Implementation Checklist

### Phase 1: Schema Definition (Complete)
- [x] Request schema designed
- [x] Response schema designed
- [x] Privacy filter rules documented
- [x] Scope boundaries defined

### Phase 2: Tooling (Pending)
- [ ] Create research-request.sh script
- [ ] Create privacy-filter.sh script
- [ ] Create source-validator.sh script
- [ ] Add pre-commit hook: validate research responses

### Phase 3: Automation (Pending)
- [ ] Integrate into web_fetch tool
- [ ] Add research logging to SQL
- [ ] Create RESEARCH_AUDIT_LOG.md for tracking
- [ ] Build dashboard for research history

### Phase 4: Monitoring (Pending)
- [ ] Monthly audit of research requests/responses
- [ ] Quarterly privacy review
- [ ] Annual schema revision

---

## Integration with Copilot

### When to Use External Research
- Validating assumptions about third-party tools/frameworks
- Filling knowledge gaps on technologies <2 years old
- Verifying best practices against authoritative sources
- Finding examples or implementations

### How to Request Research

```markdown
@copilot research: [topic] (scope: [public_sources_only|archived_only])
confidence_target: [60-95%]
```

Example:
```markdown
@copilot research: "Grok API rate limiting best practices" (scope: public_sources_only)
confidence_target: 80%
```

### Response Integration
- Store all responses in memory_bank/research/ with YAML headers
- Add cross-references to related todos
- Log in RESEARCH_AUDIT_LOG.md
- Update confidence matrix with findings

---

## Privacy Compliance

### GDPR Compliance
- [ ] No personal data from research results retained
- [ ] All emails/names/identifiers redacted
- [ ] EU-based sources respect GDPR
- [ ] Right to be forgotten: archive, don't retain indefinitely

### Security Compliance
- [ ] No credentials stored in research logs
- [ ] All URLs verified before including
- [ ] Malware-check enabled (if applicable)
- [ ] TLS verification mandatory for all sources

### Data Retention
- **Research responses**: Keep 1 year (then archive)
- **Research requests**: Keep 3 years (audit trail)
- **Privacy violations**: Report immediately, redact, document incident

---

## Approval Gates

Before deploying External Research Protocol:

1. **User Review**: [  ] User approves schema and privacy rules
2. **Security Review**: [  ] Confirm no credential leakage vectors
3. **Privacy Review**: [  ] Verify GDPR/local compliance
4. **Tool Integration**: [  ] web_fetch tool updated with filters
5. **Monitoring Setup**: [  ] Research audit logging active

**Timeline**: ~2 weeks (pending approvals)

---

## Next Steps

1. User reviews and approves schema
2. Create research tooling scripts
3. Integrate privacy filters into web_fetch
4. Deploy monitoring and logging
5. Run pilot research requests (5-10) for validation
6. Lock schema for 6-month release cycle

**Confidence Uplift Path**: 60% → 80% (after tooling) → 90% (after validation)

