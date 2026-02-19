# ---
# tool: opencode
# model: claude-opus-4-6-thinking
# account: arcana-novai
# session_id: sprint7-opus-2026-02-19
# version: v1.0.0
# created: 2026-02-19
# ---

# XNAi Context Engineering Benchmark — Test Battery

## Instructions

For each test:
1. Set up the environment condition (E1-E5) as specified in `context-packs/`
2. Present the exact prompt below to the model
3. Allow the model to use any tools available in its environment
4. Record the response
5. Score 0-10 using `scoring-rubric.yaml`
6. Record tokens consumed and wall-clock time

## Target Models

| # | Model | Access Method | Context Window |
|---|-------|--------------|---------------|
| M1 | Claude Opus 4.6 Thinking | Antigravity (free) | 200K |
| M2 | Claude Sonnet 4.6 | Cline / Antigravity | 200K |
| M3 | Gemini 3 Pro | Antigravity / Gemini CLI | 1M |
| M4 | Gemini 3 Flash | Antigravity / Gemini CLI | 1M |
| M5 | GPT-5 Mini | Copilot CLI / OpenRouter | 128K |
| M6 | Kimi K2.5 | OpenCode built-in (free) | 262K |
| M7 | DeepSeek-R1 671B | SambaNova (free) | 128K |
| M8 | GLM-5 | OpenCode built-in (free) | 205K |
| M9 | big-pickle | OpenCode built-in (free) | 200K |
| M10 | Qwen 2.5 7B Q4 (local) | llama-cpp-python | 32K |

---

## Test 1: Stack Identification

**Target Level**: L1-L2 (Surface Recognition → Structural Awareness)
**Time Limit**: 2 minutes

### Prompt

```
Analyze the XNAi Foundation project. Identify:
1. The primary programming language and web framework
2. Every service in the production stack (name, technology, port, purpose)
3. The core architectural constraints that govern all technical decisions

Be specific. Include version numbers where you can determine them.
```

### What to look for in scoring
- Does the model find all 10 services?
- Does it correctly identify ports?
- Does it name the torch-free, memory, telemetry, and async constraints?
- Does it identify the container runtime (Podman, not Docker)?

---

## Test 2: Service Topology

**Target Level**: L3 (Functional Mapping)
**Time Limit**: 5 minutes

### Prompt

```
Map the complete service dependency graph for the XNAi Foundation.
For each service, identify:
1. What it depends on (upstream dependencies)
2. What depends on it (downstream consumers)
3. What happens when it fails (failure cascade)
4. Any resilience patterns protecting it (circuit breakers, fallbacks, degradation tiers)

Include the specific degradation tier thresholds and what changes at each tier.
```

### What to look for in scoring
- Does the model trace the Redis → Vikunja → Caddy cascade?
- Does it find the 4-tier DegradationTierManager with RAM thresholds (85/92/97%)?
- Does it name all 5 circuit breakers?
- Does it identify the Redis in-memory fallback pattern?

---

## Test 3: Constraint Reasoning

**Target Level**: L3-L4 (Functional Mapping → Strategic Comprehension)
**Time Limit**: 5 minutes

### Prompt

```
The XNAi Foundation operates under several hard architectural constraints.
For each constraint you identify:
1. State the constraint precisely
2. Explain WHY it exists (the motivation)
3. Describe HOW it's enforced (code, config, process)
4. Identify any TENSIONS — places where the constraint conflicts with planned features

I'm specifically interested in contradictions between current rules and future roadmap items.
```

### What to look for in scoring
- Does the model find the torch-free vs. LoRA/QLoRA tension?
- Does it identify the 94% memory vs. <6GB target tension?
- Does it trace enforcement to specific files (RULES.md rule 4, .clinerules/03)?
- Does it explain the sovereignty motivation (Ma'at, not just "privacy")?

---

## Test 4: Strategic Assessment

**Target Level**: L4 (Strategic Comprehension)
**Time Limit**: 10 minutes

### Prompt

```
Provide a strategic assessment of the XNAi Foundation project:
1. What is the development roadmap? Describe its structure and timeline.
2. What strategic decisions have been locked in and cannot be changed?
3. What decisions are still open and need resolution?
4. What is the rate-limit waterfall strategy and why does it matter?
5. Are there any organizational or process issues that could impede progress?

I need you to demonstrate understanding of not just WHAT is planned, but WHY specific choices were made over alternatives.
```

### What to look for in scoring
- Does the model describe the 3-pillar, 38-week roadmap?
- Does it explain the OpenCode vs. Crush decision with rationale?
- Does it identify the 7-step rate limit waterfall?
- Does it notice the triple phase numbering confusion?
- Does it understand the fork strategy (fork OpenCode, not Crush)?

---

## Test 5: Cross-Domain Synthesis

**Target Level**: L4-L5 (Strategic Comprehension → Architectural Intuition)
**Time Limit**: 10 minutes

### Prompt

```
This project has layers that span multiple domains — philosophy, configuration,
application code, project management, and security.

Trace every connection you can find between the project's philosophical/ethical
framework and its concrete technical implementations. I want specific file
paths, code references, and configuration values — not abstract observations.

Also identify any architectural patterns where a concept from one domain
(e.g., strategy) manifests in a completely different domain (e.g., code or labels).
```

### What to look for in scoring
- Does the model find maat_guardrails.py?
- Does it connect Ma'at ideals to Vikunja labels (maat:7-truth)?
- Does it connect Ma'at to phase completion criteria?
- Does it trace the Pantheon Model to model-router.yaml?
- Does it map Ten Pillars to specific architecture layers (Voice→Aether, Flesh→Earth)?
- Does it find the Dual Flame and connect Lilith to the fork plan?

---

## Test 6: Gap Identification

**Target Level**: L5 (Architectural Intuition)
**Time Limit**: 10 minutes

### Prompt

```
Review the XNAi Foundation project as a coherent system. Identify every gap,
contradiction, missing piece, or architectural tension you can find.

Organize your findings by severity:
- Critical: Blocks progress or represents a fundamental conflict
- Significant: Creates confusion or technical debt
- Minor: Incomplete or inconsistent but not blocking

For each gap, cite the specific files or locations that create the contradiction.
I want evidence, not speculation.
```

### What to look for in scoring
- Does the model find GAP-01 (torch-free vs. LoRA) with file citations?
- Does the model find GAP-02 (Redis UID cascade) with root cause?
- Does the model find GAP-04 (triple phase numbering)?
- Does it discover 10+ total gaps?
- Are gaps organized by severity with evidence?
- Does it find cross-domain gaps (not just single-file issues)?

---

## Recording Template

For each test run, record:

```yaml
test_run:
  date: "YYYY-MM-DD"
  model: "model-name"
  environment: "E1|E2|E3|E4|E5"
  test: "T1|T2|T3|T4|T5|T6"
  score: 0-10
  tokens_consumed: NNNNN
  wall_clock_seconds: NNN
  comprehension_level_achieved: "L1|L2|L3|L4|L5"
  notes: "Free-form observations"
  scorer: "human|agent"
```
