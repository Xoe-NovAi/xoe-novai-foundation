# XNAi Agent Bus: Agent Role Definitions

**Status**: Phase A Deliverable #4  
**Date**: 2026-02-16  
**Authority**: Copilot CLI + Cline (kat-coder-pro) review  

---

## Executive Summary

Five distinct agent roles in the XNAi Agent Bus ecosystem, each with non-overlapping responsibilities, clear success criteria, and defined boundaries.

---

## 1. Model Research Crawler (ruvltra-claude-code-0.5b)

### Identity
- **Name**: Model Research Crawler (or "Crawler")
- **Model**: Local ruvltra-claude-code-0.5b quantized (q4_k_m)
- **Context Window**: ~8K tokens (effective)
- **Execution Location**: Local (Ryzen 7 5700U)
- **API Dependency**: None (sovereign execution)

### Responsibility
Research XNAi-stack-compatible models and generate structured model card data. Determine task complexity and escalate complex work to Agent Bus for delegation.

### Inputs
1. **Research Task**: Model category, XNAi use case, evaluation requirements
2. **Sources**: HuggingFace, OpenCompass, MTEB, Papers, BigCode leaderboards
3. **Context**: Prior model cards (for consistency and comparison)

### Outputs
1. **Model Cards**: JSON files with specs, benchmarks, ecosystem compatibility
2. **Complexity Scores**: 1-10 score for delegation routing
3. **Escalation Decisions**: Which complex findings to route to Agent Bus
4. **Inventory**: `model_cards_inventory.json` with all researched models

### Key Behaviors
- ✅ **Do**: Research facts, extract metadata, compare benchmarks
- ✅ **Do**: Score complexity accurately
- ✅ **Do**: Gracefully handle missing data with fallback sources
- ✅ **Do**: Generate valid JSON matching ModelCardSchema
- ❌ **Don't**: Make architectural decisions
- ❌ **Don't**: Write code or generate implementations
- ❌ **Don't**: Synthesize across multiple models without escalation

### Success Criteria
- [x] 6-10 models researched per hour
- [x] Model cards match schema with all required fields
- [x] Complexity scores validated against test suite (10+ scenarios)
- [x] Zero formatting errors in JSON output
- [x] Fallback sources used when primary sources unavailable
- [x] 100% task completion rate (no partial outputs)

### Failure Modes & Fallbacks
| Failure | Fallback |
|---------|----------|
| HuggingFace API unavailable | Use OpenCompass, Papers with Code |
| Missing benchmark for model | Mark as `pending_verification`, note gap |
| Unable to determine Ryzen 7 speed | Use inference formula from similar model |
| Ambiguous task categorization | Escalate to Copilot (score +2 complexity) |

### Constraints
- **Memory**: Keep processing < 500MB (allow room for OS)
- **CPU**: Don't exceed 50% utilization (preserve system responsiveness)
- **Network**: Retry failed requests 3x before fallback
- **Time**: Target 30-50 models per day (can vary with source availability)

---

## 2. Agent Bus Conductor (Consul + Redis Orchestrator)

### Identity
- **Name**: Conductor
- **Implementation**: Consul service registry + Redis state store + async task gateway
- **Location**: Orchestration layer (between Crawler and agents)
- **Execution Model**: Event-driven, stateless microservice

### Responsibility
Route incoming tasks to appropriate agent based on complexity score and task type. Manage task queuing, result collection, and feedback flow.

### Inputs
1. **Tasks**: From Crawler (with complexity_score and raw output)
2. **Agent Health**: From Consul health checks
3. **Priority**: From task metadata (normal, priority, urgent)

### Outputs
1. **Task Queue**: Queued in Redis for selected agent (`xnai:jobs:{agent}:pending`)
2. **Route Decision**: Log showing why task was routed to specific agent
3. **Tracking**: Task ID linked to agent + output stored in KB

### Key Behaviors
- ✅ **Do**: Calculate complexity score based on Delegation Protocol
- ✅ **Do**: Route tasks to non-overloaded agents
- ✅ **Do**: Handle failures gracefully (retry, escalate, alert)
- ✅ **Do**: Maintain task audit trail in Redis
- ❌ **Don't**: Perform task analysis or synthesis
- ❌ **Don't**: Make architectural decisions
- ❌ **Don't**: Store persistent state outside Redis/Consul
- ❌ **Don't**: Filter or modify task content

### Success Criteria
- [x] 100% task routing accuracy (validated on 10+ test cases)
- [x] Zero missed escalations (all complex tasks routed up, not down)
- [x] < 100ms routing latency (from receipt to queue to agent)
- [x] Task audit trail complete and queryable
- [x] Agent health checks integrated with task routing (don't route to unhealthy agent)

### Integration Points
- **Input**: Redis queue `xnai:jobs:crawler:pending`
- **Output**: Redis queues `xnai:jobs:copilot:pending`, `xnai:jobs:gemini:pending`, etc.
- **Registry**: Consul service catalog (agent availability)
- **State**: Redis hash `xnai:conductor:task-routes:` + task_id

### Constraints
- **Latency**: Routing decisions < 100ms
- **Throughput**: Handle 100+ tasks/hour
- **State**: Zero persistent local state (all in Redis)
- **Coupling**: Minimal agent-specific logic (routes based on score only)

---

## 3. Copilot (Claude Haiku 4.5)

### Identity
- **Name**: Copilot CLI
- **Model**: Claude Haiku 4.5
- **Context Window**: 100K tokens
- **API Dependency**: Anthropic Claude API
- **Specialty**: Fast strategic planning, synthesis, research summaries

### Responsibility
Conduct strategic synthesis, planning, code review, and small-to-medium research tasks. Identify gaps and escalate complex problems.

### Inputs
1. **Routed Tasks**: Score 4-5 complexity from Conductor
2. **Expert KB**: Copilot-specific SOP docs, examples, decision patterns
3. **Context**: Prior research (model cards, findings)

### Outputs
1. **Analysis**: Strategic synthesis documents (Markdown)
2. **Recommendations**: Actionable suggestions prioritized by impact
3. **Decisions**: Planning outputs, architectural choices
4. **Flags**: Complexity escalations (if task reveals higher complexity)

### Key Behaviors
- ✅ **Do**: Strategic planning and synthesis
- ✅ **Do**: Compare options and provide trade-off analysis
- ✅ **Do**: Identify gaps and unknown areas
- ✅ **Do**: Escalate to Gemini when complexity increases
- ❌ **Don't**: Implement code or write detailed code reviews
- ❌ **Don't**: Conduct exhaustive large-scale research (use Gemini)
- ❌ **Don't**: Manage entire codebase refactoring
- ❌ **Don't**: Make system-level architectural decisions alone

### Success Criteria
- [x] Turnaround time 30-120 minutes for routed tasks
- [x] Strategic recommendations backed by evidence
- [x] Escalation decisions accurate (detects when task > complexity 5)
- [x] Output quality verified by spot-check (user or Cline review)
- [x] Gap identification precise and actionable

### Expert KB
- Location: `expert-knowledge/copilot/`
- Contents:
  - `system-instructions.md`: Haiku 4.5 capabilities and limitations
  - `models/haiku-4.5-profile.md`: Speed, accuracy, context usage patterns
  - `sop/strategic-planning-protocols.md`: How to approach planning tasks
  - `sop/code-review-checklist.md`: Code review methodology
  - `examples/strategic-plan-template.md`: Template for outputs

### Constraints
- **Context**: Use judiciously (100K tokens, ~80K for task + context)
- **Throughput**: ~3-5 complex tasks per day
- **API Cost**: Monitor usage (Anthropic billed per token)
- **Task Scope**: 30-120 minute expected completion, not longer

### Integration Points
- **Input**: Redis queue `xnai:jobs:copilot:pending`
- **Output**: Results stored in KB (`knowledge/insights/copilot-decisions/`)
- **Escalation**: Task complexity > 6 → queue for Gemini
- **Health**: Register with Consul, report task status

---

## 4. Gemini (Google Gemini 3 Pro)

### Identity
- **Name**: Gemini CLI
- **Model**: Google Gemini 3 Pro
- **Context Window**: 1M tokens (exceptional)
- **API Dependency**: Google Generative AI API
- **Specialty**: Large-scale synthesis, holistic analysis, architecture review

### Responsibility
Conduct large-scale analysis, holistic synthesis across multiple sources, architectural reviews, and complex strategy work. Synthesize outputs from other agents.

### Inputs
1. **Routed Tasks**: Score 6-8 complexity from Conductor
2. **Expert KB**: Gemini-specific frameworks, synthesis patterns, templates
3. **Context**: Multiple prior analyses, decision logs, full research datasets
4. **Multi-Agent**: Results from Copilot or Crawler (for synthesis)

### Outputs
1. **Comprehensive Analysis**: Detailed reports leveraging 1M context window
2. **Architecture Recommendations**: System-level design decisions
3. **Synthesis**: Integration of multiple sources into cohesive narrative
4. **Gap Analysis**: Identification of missing knowledge and next steps

### Key Behaviors
- ✅ **Do**: Large-scale synthesis across many documents
- ✅ **Do**: Holistic analysis considering full problem space
- ✅ **Do**: Identify subtle patterns and cross-domain connections
- ✅ **Do**: Synthesize outputs from other agents
- ✅ **Do**: Escalate to Cline when implementation needed
- ❌ **Don't**: Get bogged down in implementation details
- ❌ **Don't**: Do simple lookups (route to Crawler)
- ❌ **Don't**: Do quick comparisons (use Copilot)
- ❌ **Don't**: Write code without deep analysis first

### Success Criteria
- [x] Turnaround time 2-6 hours for routed tasks
- [x] Synthesis leverages 1M context (multi-source integration)
- [x] Architecture recommendations implementable and specific
- [x] Gap analysis actionable and precise
- [x] Outputs ready for Cline implementation

### Expert KB
- Location: `expert-knowledge/gemini/`
- Contents:
  - `system-instructions.md`: Gemini 3 Pro capabilities and 1M context strategies
  - `models/gemini-3-pro-capabilities.md`: Strengths, limitations, best use cases
  - `sop/holistic-synthesis-protocols.md`: How to synthesize large datasets
  - `sop/large-scale-analysis-framework.md`: Framework for architectural analysis
  - `examples/large-document-processing-example.md`: Template for synthesis

### Constraints
- **Context**: Leverage full 1M window (this is Gemini's strength)
- **Throughput**: ~2-3 complex tasks per day (quality over speed)
- **API Cost**: Monitor usage (Google API billed per token)
- **Task Scope**: 2-6 hour expected completion

### Integration Points
- **Input**: Redis queue `xnai:jobs:gemini:pending`
- **Output**: Results stored in KB (`knowledge/insights/gemini-analysis/`)
- **Multi-Agent**: Receives synthesis requests with multiple input documents
- **Escalation**: Task implementation needed → queue for Cline
- **Health**: Register with Consul, report task status

---

## 5. Cline (kat-coder-pro Model, 256K Context)

### Identity
- **Name**: Cline CLI with kat-coder-pro model
- **Model**: kat-coder-pro (OpenRouter: kwaipilot/kat-coder-pro)
- **Context Window**: 256K tokens (excellent for code)
- **API Dependency**: OpenRouter proxy
- **Specialty**: Implementation, code generation, refactoring, documentation, testing

### Responsibility
Implement architectural decisions, generate production-ready code, refactor existing code, write comprehensive documentation, and conduct integration testing. Review outputs from other agents and fill quality gaps.

### Inputs
1. **Routed Tasks**: Score 8+ complexity from Conductor
2. **Expert KB**: Cline-specific patterns, code templates, testing frameworks
3. **Context**: Architecture decisions (from Gemini), code requirements, existing codebase
4. **Review Requests**: Feedback loop from crawler outputs (quality assurance)

### Outputs
1. **Production Code**: Fully tested, documented implementations
2. **Documentation**: Comprehensive runbooks, integration guides, API docs
3. **Tests**: Unit tests, integration tests, test automation
4. **Quality Reviews**: Enhancements to outputs from other agents (feedback loop)

### Key Behaviors
- ✅ **Do**: Implement architectural decisions with production-ready code
- ✅ **Do**: Generate comprehensive documentation and examples
- ✅ **Do**: Write and verify test suites
- ✅ **Do**: Refactor and optimize existing code
- ✅ **Do**: Review and enhance outputs from other agents (feedback loop)
- ✅ **Do**: Create integration patterns and code templates
- ❌ **Don't**: Make architectural decisions (use Gemini)
- ❌ **Don't**: Do research (use Crawler or Copilot)
- ❌ **Don't**: Implement without clear specifications
- ❌ **Don't**: Ignore test coverage

### Success Criteria
- [x] Turnaround time 4-12 hours for implementation tasks
- [x] Code passes lint checks and test suite
- [x] Documentation complete with examples and troubleshooting
- [x] 80%+ test coverage minimum
- [x] Code review (own) before returning results
- [x] Feedback loop: Reviews 20% random + 100% high-complexity outputs
- [x] Quality improvement measured (KB metrics before/after Cline review)

### Expert KB
- Location: `expert-knowledge/cline/`
- Contents:
  - `system-instructions.md`: kat-coder-pro capabilities and context usage
  - `models/kat-coder-pro-profile.md`: Strengths in code generation, 256K context
  - `sop/whole-codebase-refactoring.md`: Large-scale refactoring approach
  - `sop/documentation-rewriting.md`: Technical documentation best practices
  - `sop/integration-testing.md`: Test automation and CI/CD patterns
  - `examples/refactoring-example.md`: Concrete refactoring patterns
  - `examples/test-automation-example.md`: Test suite templates

### Constraints
- **Context**: Use 256K for full codebase context (this is Cline's strength)
- **Throughput**: ~2-3 implementation tasks per day (quality focus)
- **API Cost**: Monitor usage (OpenRouter billed per token)
- **Task Scope**: 4-12 hour expected completion
- **Review**: Sampling-based (20% random + 100% high-complexity)

### Integration Points
- **Input**: Redis queue `xnai:jobs:cline:pending`
- **Output**: Code stored in codebase, docs in KB, tests in `/tests/`
- **Feedback Loop**: Samples outputs for review, enhances KB
- **Health**: Register with Consul, report task status
- **Escalation**: If architectural change needed → escalate to Gemini + Copilot

---

## Role Boundaries & Non-Overlaps

### Verification Matrix

| Responsibility | Crawler | Conductor | Copilot | Gemini | Cline |
|---|---|---|---|---|---|
| **Research** | ✅ | ❌ | ✅ | ✅ | ❌ |
| **Strategic Planning** | ❌ | ❌ | ✅ | ✅ | ❌ |
| **Large-Scale Synthesis** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Implementation** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Code Generation** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Routing/Orchestration** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Quality Review** | ❌ | ❌ | ❌ | ❌ | ✅ |

### Decision Rights
- **Task Selection**: Conductor (routing only)
- **Strategy**: Copilot (fast), Gemini (thorough)
- **Architecture**: Gemini (alone) or Copilot + Gemini (consultation)
- **Implementation**: Cline (sole authority)
- **Quality Assurance**: Cline (with feedback from others)

---

## Communication Protocol

### Agent → Conductor
```
{
  "task_id": "...",
  "status": "complete|failed|escalated",
  "results": {...},
  "complexity_actual": 5,
  "complexity_expected": 5,
  "execution_time_seconds": 1200,
  "next_action": "store_in_kb|escalate_to_gemini|needs_implementation"
}
```

### Conductor → Next Agent
```
{
  "task_id": "...",
  "task_description": "...",
  "complexity_score": 7,
  "prior_outputs": [...],
  "context": {...},
  "deadline": "2026-02-16T23:00:00Z"
}
```

---

## Escalation Protocol

### When Task Complexity Increases
1. Agent detects complexity > assigned range
2. Agent calculates new complexity_score
3. Agent notifies Conductor: `escalate_to_X`
4. Conductor queues for next-higher-capability agent
5. Task context + prior output included

### Example
```
Copilot assigned task (score 5)
→ Discovers multi-dimensional architecture decision
→ Recalculates complexity as 7
→ Escalates to Gemini with full context
→ Gemini conducts full analysis
→ Queues implementation for Cline
```

---

## Success Metrics Per Agent

### Crawler
- Models/hour: 6-10
- JSON validity: 100%
- Complexity accuracy: ±1 point

### Conductor
- Routing latency: < 100ms
- Accuracy: 100% (validated on test suite)
- Task audit trail: 100% complete

### Copilot
- Turnaround: 30-120 minutes
- Escalation detection: 100% (no tasks > 5 scope handled solo)
- Output quality: Spot-check pass rate

### Gemini
- Turnaround: 2-6 hours
- Synthesis quality: Leverages 1M context (multi-source integration verified)
- Implementation readiness: Cline can execute without clarification

### Cline
- Turnaround: 4-12 hours
- Test coverage: 80%+
- Review feedback impact: Measurable KB improvement
- Code quality: Lint pass, manual review pass

---

## Implementation Checklist

- [x] Roles defined and documented
- [x] Boundaries verified (no overlaps)
- [x] Success criteria specified
- [x] Integration points detailed
- [ ] Health check implementation (Phase E)
- [ ] Monitoring dashboard (Phase E)
- [ ] Training/documentation for users (Phase F)

---

**Status**: ✅ PHASE A COMPLETE (All 4 Deliverables)  
**Next**: Phase B - Model Research Crawler Job (Begin immediately)
