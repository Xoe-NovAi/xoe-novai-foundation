# Troubleshooting Guide: XNAi Foundation

> **Date**: 2026-02-23
> **Context**: JOB-W2-007 - User Documentation Research
> **Status**: INITIAL DRAFT

---

## 1. System Failures (Infrastructure)

### 1.1 Qdrant Database Connectivity
- **Symptoms**: `KnowledgeClient` cannot connect to `http://localhost:6333`.
- **Diagnosis**: 
  - Check if the container is running: `podman ps | grep qdrant`.
  - Check logs: `podman logs qdrant`.
- **Resolution**: 
  - Restart the service: `make qdrant-restart`.
  - Verify `QDRANT_HOST` in `.env`.

### 1.2 Redis Stream Errors
- **Symptoms**: Agents are not picking up tasks from the `xnai:agent_bus`.
- **Diagnosis**:
  - Run `redis-cli XINFO STREAM xnai:agent_bus`.
  - Check for messages in the Dead Letter Queue (DLQ).
- **Resolution**:
  - Re-create the consumer group if it has become corrupted.
  - Clear the stream: `redis-cli DEL xnai:agent_bus`.

### 1.3 Container Startup Issues (Podman/Docker)
- **Symptoms**: `docker-compose up` fails with "Permission Denied".
- **Diagnosis**: 
  - Host-level UID/GID mapping issues on Linux.
- **Resolution**:
  - Run `podman unshare chown -R 1000:1000 data/`.
  - Use the `z` or `Z` flags for volume mounts (SELinux).

---

## 2. Application Errors (Logic)

### 2.1 Knowledge Distillation Pipeline Failures
- **Symptoms**: `KnowledgeDistillationPipeline` crashes with `AttributeError`.
- **Diagnosis**: 
  - Missing field in the `KnowledgeState` (e.g., `classification`).
  - LLM returned malformed JSON during the "Distill" step.
- **Resolution**:
  - Ensure all nodes (Extract, Classify, Score) are correctly implemented.
  - Enable `verbose` logging to see the raw LLM response.

### 2.2 Sanitization Rejections (False Positives)
- **Symptoms**: Important technical data is being redacted as `[REDACTED_SECRET]`.
- **Diagnosis**: 
  - Overly aggressive regex patterns in `sanitizer.py`.
- **Resolution**:
  - Adjust the `SanitizationConfig` to exclude certain types.
  - Add an exclusion list to the `ContentSanitizer`.

### 2.3 Access Denied (ABAC Policy)
- **Symptoms**: Valid agent cannot access a resource.
- **Diagnosis**:
  - `KnowledgeAccessControl` returned `AccessDecision.NOT_AUTHORIZED`.
  - Metadata in `iam_db` is missing required `permissions`.
- **Resolution**:
  - Update the agent's permissions in the `IAMDatabase`.
  - Check the `_evaluate_abac` logic in `knowledge_access.py`.

---

## 3. Reporting New Issues

When reporting a bug, please include:
1. **System Info**: OS, Python version, Docker/Podman version.
2. **Logs**: Relevant snippets from `logs/xnai.log`.
3. **Reproduction Steps**: A minimal set of commands to trigger the error.
4. **Agent State**: Output of `gemini status` or `cline status`.
