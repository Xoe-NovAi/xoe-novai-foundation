# Research Workflow

This document describes the scholarly research workflow used by Omega Agents.

## Creating a New Project
Run `scripts/new-research.sh <slug> [title]` which:

1. Creates a directory under `research/YYYYMMDD-<slug>` with scaffolding.
2. Adds entries to `research/index.json` and the Postgres `research_jobs` table.
3. **(Future)** Creates a matching project in Vikunja via API.

## Claiming a Job
Agents may view open jobs by querying the `research_jobs` table or via the
`omega agent list-jobs` CLI command. To claim a job:

```bash
omega agent claim <job_id>
```

This sets the `claimed_by` field and notifies collaborators.

## Collaboration
A claimed job can invite other agents:

```bash
omega agent invite <agent_id> --job <job_id>
```

The invited agent may accept or decline; both actions are recorded in `research_collaborators`.

## Closing a Project
When finished, the owning agent:

1. Updates `meta.yaml` status to `closed`.
2. Runs the Gnosis injector and conversation ingestion scripts.
3. Marks the job `status='closed'` in Postgres and Vikunja.
4. The memory bank indexer and metrics aggregator run automatically.

## Tags and Domains
Each job may include `domain_tags` in its metadata to categorize work. These
influence agent preferences and prioritization.
