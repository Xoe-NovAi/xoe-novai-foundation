---
title: Copilot ask_question — research & test plan
tags: [copilot, agents, billing, test-plan]
---

## Key finding (short)

No public vendor document explicitly enumerates per-API "ask_question" increments or a named "ask_question" billing unit. Copilot docs expose plan-level quotas for chat/agent requests; therefore treat `ask_question` as part of chat/agent request accounting and validate via empirical testing.

## Evidence & citations

- GitHub Copilot plans & quotas (shows agent/chat request quotas per plan): https://github.com/features/copilot (see plan descriptions)
- GitHub Copilot docs (billing, enterprise controls): https://docs.github.com/en/copilot

> No explicit "ask_question" billing page was found in public docs (as of 2026-02-13).

## Recommended empirical test plan (step-by-step)

Objective: determine whether each `ask_question` increments the Copilot chat/agent usage counter and how it maps to plan quotas.

Test steps:
1. Use a disposable GitHub org or an account with Copilot Pro/Free tiers and access to Copilot usage dashboard.
2. Instrument a small script that issues repeated `ask_question` calls via the Copilot CLI (or agent SDK) with a unique idempotency token for each call.
   - If CLI only supports interactive requests, use recorded session counts or the Copilot SDK where available.
3. Record timestamps and request payloads for 500 sequential `ask_question` calls (batched in groups of 1, 5, 50).
4. After each batch, check the Copilot usage dashboard / billing UI and note increments and delays.
5. Repeat across two plans (Free and Pro/Pro+) and with varying payload sizes and multimodal attachments.

Expected metrics to observe:
- Usage count change in Copilot dashboard after N calls (ideally immediate or within minutes).
- Whether grouped/batched calls are collapsed (unlikely) or counted individually.
- Any error codes or rate-limit headers returned by the CLI/API.

Success criteria:
- Clear mapping of N ask_question calls → M usage increment in dashboard.
- Identification of per-plan rate-limits and throttling behavior.

## Guardrails / best practices

- Treat `ask_question` as a billable chat/agent request until vendor confirms otherwise.
- Cache results for repeated identical prompts, batch low-priority research queries, and use shorter prompts for high-frequency automation.
- Add telemetry around ask_question usage (who/what/why) in `memory_bank/agent_usage.log`.

## Action items for operators

- Run the empirical test plan with a staging Copilot account and commit the observed mapping to this file.
- If evidence shows `ask_question` is billed per-call, add per-agent daily quotas in agent orchestration.

