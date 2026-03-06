# Metrics & Promotion

Agents are evaluated continuously and promoted within domains based on
measurable performance.

## Emitted Metrics
All services emit Prometheus metrics with an `agent_id` label. Important
metrics include:

- `agent_task_success_total{agent_id,domain}`
- `agent_latency_seconds{agent_id,task_type}`
- `agent_model_accuracy{agent_id,model}`
- `agent_research_outcomes{agent_id,job_id}`

Custom metrics may be defined in `config/*.yaml` and are scraped by the
Prometheus server on `/metrics`.

## Aggregation & Ranking
A nightly `agent_ranker` job reads recent metrics from Prometheus and
calculates a composite score per `(agent_id,domain)`. Scores are written to
the `agents.priority` field and recorded in the `agent_metrics` table.

Agents with high priority are preferred by the Agent Bus when assigning
workflows. Promotions and demotions generate Vikunja alerts for human review.

## Historical Storage
The `agent_metrics` table stores time‑series snapshots for long‑term analysis.
This supports quarterly reviews and audits of agent performance.
