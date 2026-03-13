
# LIBRARIAN AGENT PROTOCOL v1.0
**Version**: 1.0.0 | **Status**: ACTIVE | **Priority**: HIGH  
**Created**: 2026-02-17 | **Role Type**: Documentation Maintenance Agent

---

## Overview

The Librarian Agent is the primary documentation maintenance and quality assurance agent in the Xoe-NovAi Documentation Excellence System. This agent operates autonomously to ensure documentation freshness, compliance, and organization.

---

## Role Definition

### Primary Responsibilities

| Responsibility | Description | Frequency |
|----------------|-------------|-----------|
| **Freshness Monitoring** | Detect stale documentation (>90 days) | Every 6 hours |
| **Frontmatter Validation** | Ensure all docs have required metadata | On creation/update |
| **Archival Coordination** | Move deprecated content to archives | As needed |
| **Genealogy Tracking** | Update documentation lineage | On any change |
| **Vikunja Integration** | Create/resolve documentation tasks | Continuous |
| **Reporting** | Generate freshness and compliance reports | Daily |

### Secondary Responsibilities

- Coordinate with QA Agent for quality assessments
- Interface with Search Agent for indexing updates
- Support Integration Agent for standardization
- Maintain memory bank documentation entries

---

## Configuration

### Agent Identity

```yaml
agent:
  name: Librarian Agent
  id: librarian-001
  type: documentation_maintenance
  version: 1.0.0
  
capabilities:
  - frontmatter_validation
  - freshness_monitoring
  - archival_management
  - genealogy_tracking
  - vikunja_task_management
  - reporting_generation
```

### Trigger Configuration

```yaml
triggers:
  scheduled:
    - cron: "0 */6 * * *"
      action: freshness_scan
    - cron: "0 0 * * *"
      action: daily_report
      
  events:
    - channel: doc:events
      pattern: document.created
      action: validate_and_track
    - channel: doc:events
      pattern: document.updated
      action: validate_and_update
    - channel: doc:events
      pattern: document.deprecated
      action: archive_document
      
  manual:
    - command: make docs-check
      action: full_validation
    - command: make docs-janitor
      action: janitor_scan
```

### Output Channels

```yaml
output:
  redis_streams:
    - doc:events      # Document lifecycle events
    - doc:quality     # Quality assessment requests
    - doc:reports     # Generated reports
    
  vikunja:
    project: documentation-health
    task_types:
      - freshness_review
      - frontmatter_fix
      - archival_review
      
  memory_bank:
    - activeContext.md
    - progress.md
    - documentation-status.json
```

---

## Operational Procedures

### 1. Freshness Scan Procedure

```python
async def freshness_scan():
    """
    Scan all documentation for stale content.
    Runs every 6 hours via scheduled trigger.
    """
    docs = scan_documentation_directories([
        "docs/",
        "internal_docs/",
        "expert-knowledge/",
        "memory_bank/"
    ])
    
    stale_docs = []
    for doc in docs:
        metadata = extract_frontmatter(doc)
        days_since_update = calculate_days_since(metadata.last_updated)
        
        if days_since_update > 90:
            stale_docs.append({
                "path": doc,
                "days_stale": days_since_update,
                "status": metadata.status
            })
            
    # Create Vikunja tasks for stale docs
    for stale in stale_docs:
        create_vikunja_task(
            project="documentation-health",
            template="freshness_review",
            data=stale
        )
        
    # Update memory bank
    update_memory_bank("stale_documents", stale_docs)
    
    # Publish event
    publish_event("doc:events", {
        "type": "freshness_scan_complete",
        "stale_count": len(stale_docs),
        "timestamp": now()
    })
```

### 2. Frontmatter Validation Procedure

```python
def validate_frontmatter(document_path: str) -> ValidationResult:
    """
    Validate frontmatter compliance for a single document.
    """
    required_fields = {
        "last_updated": is_valid_date,
        "status": lambda x: x in ["draft", "active", "deprecated", "archived"],
        "category": lambda x: x in ["Reference", "Tutorial", "How-to", "Explanation", "Strategic"]
    }
    
    optional_fields = {
        "hardware_context": is_valid_hardware_context,
        "depends_on": is_valid_path_list,
        "supersedes": is_valid_path_list,
        "tags": is_valid_tag_list
    }
    
    frontmatter = parse_frontmatter(document_path)
    
    errors = []
    warnings = []
    
    # Check required fields
    for field, validator in required_fields.items():
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")
        elif not validator(frontmatter[field]):
            errors.append(f"Invalid value for {field}")
            
    # Check optional fields
    for field, validator in optional_fields.items():
        if field in frontmatter and not validator(frontmatter[field]):
            warnings.append(f"Invalid value for optional field: {field}")
            
    # Performance docs require hardware_context
    if "performance" in document_path.lower():
        if "hardware_context" not in frontmatter:
            errors.append("Performance documents require hardware_context")
            
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        path=document_path
    )
```

### 3. Archival Procedure

```python
async def archive_document(document_path: str, reason: str):
    """
    Archive a deprecated document with metadata preservation.
    """
    # 1. Read original document
    content = read_document(document_path)
    frontmatter = extract_frontmatter(document_path)
    
    # 2. Determine archive location
    archive_path = determine_archive_path(document_path)
    
    # 3. Update frontmatter for archive
    archived_frontmatter = {
        **frontmatter,
        "status": "archived",
        "archived_date": now(),
        "archive_reason": reason,
        "original_path": document_path
    }
    
    # 4. Write to archive
    write_document(archive_path, {
        "frontmatter": archived_frontmatter,
        "content": content
    })
    
    # 5. Update genealogy tracker
    update_genealogy(document_path, {
        "status": "archived",
        "archive_path": archive_path
    })
    
    # 6. Create archive notice at original location
    write_archive_notice(document_path, archive_path)
    
    # 7. Publish event
    publish_event("doc:events", {
        "type": "document.archived",
        "original_path": document_path,
        "archive_path": archive_path,
        "reason": reason
    })
```

### 4. Genealogy Tracking Procedure

```python
def update_genealogy(document_path: str, changes: dict):
    """
    Update the genealogy tracker for a document.
    """
    genealogy_path = "internal_docs/00-system/GENEALOGY-TRACKER.yaml"
    
    genealogy = read_yaml(genealogy_path)
    
    if document_path not in genealogy["documents"]:
        genealogy["documents"][document_path] = {
            "created": now(),
            "lineage": []
        }
        
    # Add change to lineage
    genealogy["documents"][document_path]["lineage"].append({
        "timestamp": now(),
        "changes": changes,
        "version": len(genealogy["documents"][document_path]["lineage"]) + 1
    })
    
    # Update last modified
    genealogy["documents"][document_path]["last_modified"] = now()
    
    write_yaml(genealogy_path, genealogy)
```

---

## Integration Points

### Vikunja Integration

```yaml
vikunja:
  api_url: ${VIKUNJA_API_URL}
  project_id: documentation-health
  
  task_templates:
    freshness_review:
      title: "Review: {document_title}"
      description: |
        Document stale for {days_stale} days.
        
        Review checklist:
        - [ ] Content accuracy verified
        - [ ] Links validated
        - [ ] Hardware context current
        - [ ] Frontmatter complete
      labels: [freshness, review]
      priority: MEDIUM
      due_date: +7d
      
    frontmatter_fix:
      title: "Fix Frontmatter: {document_title}"
      description: |
        Missing/invalid fields: {missing_fields}
        
        Required: {required_fields}
      labels: [frontmatter, fix]
      priority: HIGH
      due_date: +3d
```

### Redis Stream Integration

```yaml
redis_streams:
  input:
    - channel: doc:events
      handlers:
        document.created: handle_new_document
        document.updated: handle_document_update
        document.deprecated: handle_deprecation
        
  output:
    - channel: doc:events
      events:
        - freshness_scan_complete
        - frontmatter_validation_complete
        - document.archived
        
    - channel: doc:quality
      events:
        - quality_assessment_request
```

### Memory Bank Integration

```yaml
memory_bank:
  updates:
    - file: activeContext.md
      section: Documentation System Status
      
    - file: progress.md
      section: Documentation Excellence Initiative
      
    - file: documentation-status.json
      content: full_status_report
```

---

## Decision Trees

### Freshness Decision Tree

```
Document Age Check
├── < 30 days → OK (No action)
├── 30-90 days → WARN (Add to monitoring)
└── > 90 days → STALE
    ├── Status: Active → Create review task
    ├── Status: Draft → Notify author
    └── Status: Deprecated → Consider archival
```

### Archival Decision Tree

```
Archival Assessment
├── Has Superseding Document?
│   └── Yes → Archive with reference
│   └── No →
│       ├── Historical Value?
│       │   └── Yes → Archive for reference
│       │   └── No →
│       │       ├── Duplicate Content?
│       │       │   └── Yes → Remove
│       │       │   └── No → Archive with notice
```

---

## Error Handling

### Common Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `FRONTMATTER_PARSE_ERROR` | Invalid YAML syntax | Log error, create fix task |
| `FILE_NOT_FOUND` | Path changed/removed | Update genealogy, log warning |
| `VIKUNJA_API_ERROR` | Connection/auth issue | Retry with backoff, alert on failure |
| `REDIS_STREAM_ERROR` | Connection issue | Queue locally, retry on reconnect |

### Error Recovery

```python
async def handle_error(error: Exception, context: dict):
    """
    Handle errors with appropriate recovery actions.
    """
    if isinstance(error, FrontmatterParseError):
        # Create fix task in Vikunja
        create_vikunja_task(
            template="frontmatter_fix",
            data={
                "document_path": context["path"],
                "error": str(error)
            }
        )
        
    elif isinstance(error, VikunjaAPIError):
        # Queue for retry
        queue_for_retry(context["operation"], max_retries=3)
        
        # Alert if critical
        if error.is_critical():
            alert_team("Vikunja integration failure")
            
    elif isinstance(error, RedisStreamError):
        # Use local queue
        enable_local_queue()
        schedule_reconnect()
```

---

## Performance Considerations

### Memory Efficiency

- Process documents in batches of 50
- Use streaming for large file reads
- Cache frontmatter for frequently accessed docs
- Clean up temp files after processing

### Hardware-Aware Operation

```yaml
hardware_optimization:
  zram_aware: true
  max_memory_mb: 512
  batch_size: 50
  concurrent_workers: 2
  
  # Ryzen 5700U optimizations
  openblas_coretype: ZEN
  thread_count: 6
```

---

## Monitoring & Metrics

### Key Metrics

```yaml
metrics:
  - name: documents_scanned
    type: counter
    description: Total documents scanned for freshness
    
  - name: stale_documents_detected
    type: gauge
    description: Current count of stale documents
    
  - name: frontmatter_violations
    type: counter
    description: Frontmatter validation failures
    
  - name: documents_archived
    type: counter
    description: Documents moved to archive
    
  - name: vikunja_tasks_created
    type: counter
    description: Vikunja tasks generated
    
  - name: scan_duration_seconds
    type: histogram
    description: Time taken for freshness scans
```

### Health Checks

```yaml
health_checks:
  - name: redis_connection
    interval: 60s
    action: ping_redis
    
  - name: vikunja_connection
    interval: 300s
    action: vikunja_health_check
    
  - name: file_access
    interval: 60s
    action: check_doc_directories
```

---

## Quick Reference

### Commands

```bash
# Manual freshness scan
make docs-janitor

# Validate all frontmatter
make docs-validate-frontmatter

# Archive stale documents
make docs-janitor-archive

# Show documentation status
make docs-excellence-status
```

### Redis Stream Events

```bash
# Subscribe to document events
redis-cli -a "$REDIS_PASSWORD" XREAD STREAMS doc:events 0

# Publish manual scan event
redis-cli -a "$REDIS_PASSWORD" XADD doc:events '*' type manual_scan requested_by human
```

---

**Protocol Status**: ACTIVE  
**Last Updated**: 2026-02-17  
**Maintained By**: Xoe-NovAi Documentation Excellence Team