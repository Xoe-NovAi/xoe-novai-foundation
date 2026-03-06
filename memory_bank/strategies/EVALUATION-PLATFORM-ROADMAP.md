# Evaluation Platform Roadmap

**Date**: February 26, 2026
**Purpose**: High-level strategy and phased roadmap for expanding the split-test framework into a full evaluation service for both models and memory banks.

## Vision
Transform the existing split-test system into a comprehensive evaluation platform that:

- Compares models and knowledge banks side-by-side
- Supports multi-expert memory bank evaluation
- Offers parallel execution, caching, and dashboarding
- Can be exposed as a CLI or service
- Integrates seamlessly with the Foundation Stack and research workflows

## Phases

### Phase A: Research & Foundation (Weeks 1-4)
- Complete critical research jobs (vector cache, parallel execution, automated bank ingestion, evaluation metrics)
- Audit and update memory bank entries
- Create Research Expert Memory Bank and templates
- Write architecture and integration documentation

### Phase B: Prototyping & Expansion (Weeks 5-8)
- Implement vector cache and parallel runner prototype
- Extend MetricsCollector and ResultStorage for bank evaluations
- Add hybrid adapter support and CLI features for bank listing
- Build example banks (philosophy, classical works, foundation stack)
- Develop ingestion scripts for automated bank construction

### Phase C: Testing & Validation (Weeks 9-12)
- Expand pytest suite with cross-bank comparisons and ground truth sets
- Benchmarks for latency and resource usage
- Collect early metrics and adjust evaluation criteria
- Perform integration tests with SessionManager/KnowledgeClient

### Phase D: Documentation & Training (Weeks 13-16)
- Publish user guides and tutorials for bank creation and evaluation
- Update onboarding materials for engineers
- Run internal demos and workshops

### Phase E: Deployment & Monitoring (Weeks 17-20)
- Deploy platform as a service with dashboards
- Schedule periodic research jobs and automated replays
- Set up Grafana alerts and monitoring for bank health
- Open-source CLI and evaluation code

## Success Metrics
- **Coverage**: % of models and banks usable in the platform
- **Performance**: evaluation run time per bank/model
- **Accuracy**: alignment of metrics with manual assessment
- **Adoption**: number of engineers/researchers using the tool
- **Research Output**: completion rate of queued research jobs

## Dependencies & Risks
- Reliance on Redis/Qdrant availability
- Memory bank ingestion tooling maturity
- Scalability of parallel runner on local hardware
- Clear definition of evaluation metrics to avoid biases

---
*This document is referenced by `/memories/session/plan.md` and will be updated as work progresses.*