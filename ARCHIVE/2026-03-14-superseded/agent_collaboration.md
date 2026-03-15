# Agent Collaboration Protocols

Agents interact over the Redis-based Agent Bus and share job information via
PostgreSQL and Vikunja.

## Job Claiming
- Unclaimed jobs have `status='open'` in `research_jobs`.
- An agent claims a job with `omega agent claim <job_id>`; sets `claimed_by`.
- Claiming agent broadcasts:
  ```json
  {"type":"job_claimed","job_id":"...","agent_id":"..."}
  ```

## Inviting Collaborators
- Owner sends a collaboration request:
  ```json
  {"type":"collab_request","job_id":"...","from":"agent_id"}
  ```
- Receiving agents may reply with `collab_accept` or `collab_decline`.
- Accepting adds entries to `research_collaborators` and notifies the owner.

## Preferences & Affinity
- Agents maintain `agent_preferences` table mapping domains to affinity
  scores. Completing tasks in a domain increases the score, while failures
  decrease.
- The bus consults these scores when routing new jobs: higher affinity
  increases the likelihood an agent will claim a relevant job.

## Visibility
All agents can query the jobs roster and see the claimed status. They may
send `omega agent message <agent_id> "Can I assist?"` which posts a Vikunja
task to the owner.
