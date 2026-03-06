# Split Test Protocol — Adding New Models
# ========================================

## Overview

This document defines the protocol for adding new AI models to the XNAi Foundation split test system.

---

## 1. Model Discovery Process

### 1.1 Research New Models

When a new model is discovered:

1. **Verify the model exists** - Check official sources (provider docs, API)
2. **Confirm pricing** - Is it free or paid?
3. **Check context window** - What are the limits?
4. **Test availability** - Can it be accessed via CLI?

### 1.2 Research Template

```yaml
# For each new model, document:
model_discovery:
  name: "Model Name"
  provider: "Provider"
  source_url: "Official documentation URL"
  
  # Technical specs
  specs:
    context_window: 200000  # tokens
    max_output: 64000      # tokens
    modalities: ["text", "vision"]
  
  # Access
  access:
    cli: "cli-name"
    auth_required: true/false
    free: true/false
  
  # Testing status
  status: "discovered/tested/ready"
  tested_by: "agent-name"
  date: "YYYY-MM-DD"
```

---

## 2. Adding a Model to Config

### 2.1 Update model-router.yaml

Add to the appropriate provider tier:

```yaml
- id: provider_id
  name: "Provider Name"
  tier: 1  # Update tier number
  models:
    - id: "model-id"
      name: "Human Readable Name"
      context_length: 200000
      max_output: 64000
      cost_per_mtok_in: 0  # or actual cost
      capabilities: [coding, reasoning]
      best_for: [task_types]
```

### 2.2 Update confirmed_real_models

Add to the registry:

```yaml
- id: "provider/model-id"
  provider: "Provider Name"
  confirmed_date: "YYYY-MM-DD"
  source: "Source of confirmation"
  context_k: 200
  cost: "free/paid"
  status: "available/alpha/beta"
```

---

## 3. Running Split Tests

### 3.1 Quick Start

```bash
# List available models
python3 scripts/split_test/__init__.py --list-models

# Run default 4-model test
python3 scripts/split_test/__init__.py --test-id wave5-2026-02-26

# Run specific models
python3 scripts/split_test/__init__.py --models raptor-mini haiku-4-5 minimax-m2.5-free kat-coder-pro
```

### 3.2 Custom Test

Create a test config:

```bash
# Run with custom prompt
python3 -c "
from split_test import SplitTestRunner, SplitTestConfig, ModelConfig

config = SplitTestConfig(
    test_id='custom-test',
    test_name='My Custom Test',
    task_prompt='Your task here...',
    models=[
        ModelConfig(id='model1', name='Model 1', provider='X', cli='cli', model_id='id1', context_window=200000),
        ModelConfig(id='model2', name='Model 2', provider='Y', cli='cli', model_id='id2', context_window=200000),
    ]
)

runner = SplitTestRunner(config)
runner.run()
results = runner.compare()
print(results)
"
```

---

## 4. Metrics & Storage

### 4.1 Redis Metrics

Metrics are published to Redis streams:

```bash
# Subscribe to test results
redis-cli XREAD STREAM test-results 0

# Get all results
redis-cli XRANGE test-results - +

# Get metrics
redis-cli HGETALL test-id:metrics
```

### 4.2 Qdrant Storage

Results are stored in Qdrant for semantic search:

```python
from split_test import ResultStorage

storage = ResultStorage()
results = storage.search_similar(
    "split_test_results", 
    "How well did each model document Phase 5A?",
    limit=5
)
```

---

## 5. Evaluation

### 5.1 Scoring Criteria

| Criterion | Weight | Measurement |
|-----------|--------|-------------|
| Completeness | 25% | Phases covered / 5 |
| Accuracy | 25% | File path validity, technical correctness |
| Actionability | 20% | Executable steps, code blocks |
| Efficiency | 15% | Output length / time |
| Structure | 15% | TOC, navigation, tables |

### 5.2 Manual Evaluation

After automated scoring, manually review:

1. **File paths** - Do they exist?
2. **Technical accuracy** - Are details correct?
3. **Hallucinations** - Any fabricated content?
4. **Completeness** - All 5 phases covered?

---

## 6. Adding to the Framework

### 6.1 New CLI Adapter

To add support for a new CLI:

```python
from split_test import ModelAdapter, ModelConfig

class NewCLIAdapter(ModelAdapter):
    def execute(self, config: ModelConfig, prompt: str, context_files: List[str]):
        # Implement CLI execution
        pass
    
    def get_available_models(self):
        # Return models from config
        pass
```

### 6.2 Local Model Support

(This section remains unchanged)

The framework now includes a `LocalModelAdapter` that can exercise models
stored on disk using the Foundation stack (ONNX/GGUF). Set the environment
variable `LOCAL_MODEL_DIR` to point at the directory containing `*.onnx`
(or `*.gguf`) files, or pass the directory when constructing the adapter.

```python
from split_test import LocalModelAdapter, SplitTestRunner, SplitTestConfig

adapter = LocalModelAdapter(model_dir="/path/to/models")
runner = SplitTestRunner(config, adapter=adapter)
```

When running the CLI, select the adapter using `--adapter local` (default is
`cli`). Error conditions such as missing model files or inference failures are
captured in the resulting `TestResult` and will mark the run as **FAILED**.
Example:

```bash
python3 scripts/split_test/__init__.py --adapter local --models raptor-mini

### 6.3 Memory Bank Adapter

A new adapter type, `memory_bank`, treats each directory under
`memory_bank/multi_expert/` as a pseudo‑model. It performs a lightweight
semantic or keyword search against the bank and returns the most relevant
passage. This allows running split tests on knowledge banks themselves (e.g.
compare a "foundation stack" bank to a "philosophy" bank).

```bash
python3 scripts/split_test/__init__.py --adapter memory_bank --models philosophy
```

The same metrics, error handling, and session/knowledge recording apply when
using this adapter. Memory banks must contain plain text files; if Qdrant is
installed the adapter will try semantic search, otherwise it falls back to a
case-insensitive keyword scan.

### 6.4 Metrics and Error Handling Enhancements
```

Errors and exit codes from any adapter are logged and stored in metrics so
post‑mortem analysis can locate problematic models.

### 6.3 Metrics and Error Handling Enhancements

The `MetricsCollector` now tracks error counts per model in Redis under a
`<test_id>:errors` hash.  The `CLIAdapter` treats non‑zero exit codes as
failures and records stderr.  A circuit breaker and retry/backoff logic
prevent cascading failures; when the breaker opens, subsequent calls are
short‑circuited and labeled accordingly.

These mechanisms ensure that model executions are robust and that failures
are transparent for downstream evaluation.

### 6.2 New Metrics

To add new metrics:

```python
class CustomMetricsCollector(MetricsCollector):
    def collect(self, result: TestResult):
        # Custom metric collection
        result.metrics["custom_metric"] = calculate_custom(result)
```

---

## 7. Troubleshooting

### 7.1 Common Issues

| Issue | Solution |
|-------|----------|
| CLI not found | Check PATH, install CLI |
| Auth failure | Run `cli auth` manually first |
| Timeout | Increase timeout in config |
| Output empty | Check stderr for errors |

### 7.2 Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 8. Reliability & Hardening

The framework now includes built-in error handling utilities and resilience features:

- **Logging**: All components use the `logging` module and emit to `split_test.log` plus console. Adjust `SPLIT_TEST_LOG_LEVEL` as needed.
- **Timeouts**: Each model run respects a `timeout` value (default 600s). Override via `timeout_seconds` in `split-test-defaults.yaml` or per-test config.
- **Retry Logic**: CLI calls are wrapped with `retry_with_backoff` (exponential backoff). Defaults (`retry_attempts`, `retry_delay_seconds`) are configured in defaults or on `SplitTestConfig`.
- **Circuit Breaker**: Each CLI has a simple circuit breaker preventing repeated failures. When open, calls fail fast until the timeout expires or process restarts.
- **Input Validation**: CLI binaries are checked with `shutil.which` before invocation; missing executables produce a clear failure and are logged.
- **Exception Handling**: All subprocess calls catch `TimeoutExpired`, `FileNotFoundError`, and general exceptions, logging details and marking results `FAILED`.

Refer to the troubleshooting guide (`docs/troubleshooting/SPLIT-TEST-TROUBLESHOOTING.md`) for practical tips on dealing with these faults.

---

**Last Updated**: 2026-02-26  
**Protocol Version**: 1.0.0
