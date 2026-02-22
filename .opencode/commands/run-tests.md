# Run Tests Command

## Purpose
Execute test suite and report results.

## Usage
```
/run-tests [options]
```

## Options
- `--phase N` - Run tests for specific phase
- `--coverage` - Include coverage report
- `--verbose` - Detailed output

## Workflow
1. Identify test directory based on phase
2. Run pytest with specified options
3. Parse results
4. Report pass/fail status
5. Highlight failures

## Test Structure
```
tests/
├── phase_1/
├── phase_2/
├── phase_3/
├── phase_4/
├── integration/
└── conftest.py
```

## Output
```
## Test Results

### Summary
- Passed: 45
- Failed: 2
- Skipped: 3
- Coverage: 78%

### Failures
1. tests/phase_4/test_agent_bus.py:45
   - AssertionError: Expected connection timeout

2. tests/integration/test_rag.py:120
   - ImportError: Missing dependency

### Recommendations
1. Fix agent_bus timeout handling
2. Install missing dependency X
```

## Commands Executed
```bash
pytest tests/ -v --tb=short
pytest tests/ --cov=app --cov-report=term
```
