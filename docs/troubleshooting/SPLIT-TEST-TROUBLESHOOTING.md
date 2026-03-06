# Split Test Troubleshooting Guide

This document helps developers diagnose and resolve common issues when using the split test framework.

## Common Errors

### CLI Not Found
```
CLI not found: <cli>
```
- **Cause**: `cli` binary is not in `PATH` or configured location.
- **Solution**: Install the CLI or update `configs/model-router.yaml` with correct `cli` path. Use `which <cli>` to verify.

### Timeout Errors
```
Timeout for model <id>
```
- **Cause**: Model execution exceeded configured timeout (default 600s).
- **Solution**: Increase `timeout_seconds` in `configs/split-test-defaults.yaml` or per-model settings. Check network issues or infinite loops in prompts.

### Circuit Breaker Open
```
Circuit breaker open for CLI <cli>
```
- **Cause**: Multiple consecutive failures triggered a circuit breaker to prevent cascading errors.
- **Solution**: Investigate underlying cause (missing binary, permission error, crash) and allow timeout to expire or reset breaker manually by restarting the process.

### Vikunja API Failures
- **Symptoms**: warnings in logs about Vikunja status codes, network errors.
- **Solution**: Ensure `VIKUNJA_URL`/`VIKUNJA_API_KEY` environment variables are set. Confirm network connectivity and API availability.

### Redis/Qdrant Not Available
- **Symptoms**: infrastructure tests simulate latency; metrics not published.
- **Solution**: Start Redis (`redis-server`) and Qdrant services or adjust `configs/split-test-defaults.yaml` URLs to point to working hosts. Use `redis-cli ping` and `curl http://localhost:6333` to verify.

> **Redis auth**: if your Redis instance requires a password, set the full
> connection string using `SPLIT_TEST_REDIS_URL` (e.g.
> `redis://:changeme@localhost:6379/0`) or export `REDIS_PASSWORD` along with
> `SPLIT_TEST_REDIS_HOST`/`PORT` – the runner will automatically build a
> suitable URL from those variables.

## Debug Commands

```bash
# Validate YAML configurations
python3 -c "import yaml; yaml.safe_load(open('configs/split-test-defaults.yaml')); yaml.safe_load(open('configs/model-router.yaml'))"

# Run performance suite with debug output
python3 scripts/split_test/performance.py --suite all

# Run a single model invocation with error handling test
python3 -c "from scripts.split_test import CLIAdapter, ModelConfig; adapter=CLIAdapter(); config=ModelConfig(id='test', name='Test', provider='X', cli='nonexistent', model_id='test', context_window=1000); print(adapter.execute(config, 'test', []))"
```

## Logging

- Logs are written to `split_test.log` and stderr/stdout.
- Set `SPLIT_TEST_LOG_LEVEL` to `DEBUG`/`INFO` to adjust verbosity.
- Use `--adapter local` to run models from `LOCAL_MODEL_DIR`; missing files or
  invalid binaries will appear as errors in the results.
- Use `--adapter memory_bank` to exercise a specialized memory bank; if the
  bank contains no documents matching the prompt the adapter will return a
  failure with error "No relevant content found".  Ensure Qdrant is running
  or populate the bank with keyword-rich text.
- Non‑zero exit codes from CLI programs are now treated as failures and the
  stderr text is appended to the result; check the `errors` field in JSON
  output.

## Further Assistance

If you cannot resolve an issue:
- Re-run the failing command with `PYTHONBREAKPOINT=1` to drop into debugger.
- Check the `docs/protocols/SPLIT-TEST-PROTOCOL.md` for procedural guidance.
- Reach out on the coordination channel or file an issue in the repository.
