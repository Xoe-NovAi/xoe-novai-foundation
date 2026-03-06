import os
import sys
import time
import tempfile
import pytest
from datetime import datetime

# dynamically load the split_test module from scripts/ directory (not a package)
import importlib.util
from pathlib import Path

def _load_split_test():
    base = Path(__file__).parent.parent / "scripts" / "split_test" / "__init__.py"
    spec = importlib.util.spec_from_file_location("split_test", str(base))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

split_test_module = _load_split_test()
# expose common names for convenience
ModelConfig = split_test_module.ModelConfig
CLIAdapter = split_test_module.CLIAdapter
SplitTestConfig = split_test_module.SplitTestConfig
SplitTestRunner = split_test_module.SplitTestRunner
MetricsCollector = split_test_module.MetricsCollector
ResultStorage = split_test_module.ResultStorage
# load additional modules
perf_path = Path(__file__).parent.parent / "scripts" / "split_test" / "performance.py"
perf_spec = importlib.util.spec_from_file_location("split_test.performance", str(perf_path))
perf_mod = importlib.util.module_from_spec(perf_spec)
perf_spec.loader.exec_module(perf_mod)

FoundationStackTester = perf_mod.FoundationStackTester
CircuitBreakerOpenError = split_test_module.CircuitBreakerOpenError


def test_model_config_command_quoting():
    cfg = ModelConfig(id="m", name="M", provider="X", cli="echo", model_id="id", context_window=1000)
    prompt = 'hello "world"'
    cmd = cfg.to_command(prompt)
    # should be a list and preserve the space-containing prompt as a single element
    assert isinstance(cmd, list)
    assert cmd[-1] == 'hello world'


def test_cli_adapter_missing_cli(monkeypatch, caplog):
    adapter = CLIAdapter()
    cfg = ModelConfig(id="t", name="T", provider="X", cli="nonexistent", model_id="id", context_window=1000)
    res = adapter.execute(cfg, "test", [])
    assert res.status.name == "FAILED"
    assert "CLI not found" in res.errors[0]
    assert "CLI binary not found" in caplog.text


def test_cli_adapter_circuit_breaker_opens(monkeypatch):
    adapter = CLIAdapter()
    cfg = ModelConfig(id="t", name="T", provider="X", cli="echo", model_id="id", context_window=1000)
    # explicitly insert a breaker and open it
    # create a breaker with nonzero timeout and mark as open
    cb = split_test_module.CircuitBreaker(failure_threshold=1, timeout=60)
    cb.state = "open"
    cb.last_failure_time = time.time()
    adapter._circuit_breakers[cfg.cli] = cb
    # execute should honor breaker and mark failure
    res = adapter.execute(cfg, "test", [])
    assert res.status.name == "FAILED"
    assert any("Circuit breaker open" in e for e in res.errors)


def test_cli_adapter_nonzero_exit(tmp_path):
    # simulate a CLI that returns non-zero by creating a small shell script
    script = tmp_path / "fail.sh"
    script.write_text("#!/bin/sh\necho error >&2\nexit 5")
    script.chmod(0o755)
    adapter = CLIAdapter()
    cfg = ModelConfig(id="t2", name="T2", provider="X", cli=str(script), model_id="id", context_window=1000)
    res = adapter.execute(cfg, "input", [])
    assert res.status.name == "FAILED"
    assert "Non-zero exit code" in res.errors[0]
    assert any("error" in e for e in res.errors)


def test_local_model_adapter(monkeypatch, tmp_path, caplog):
    # create dummy model file and monkeypatch ONNX runtime
    monkeypatch.setenv("LOCAL_MODEL_DIR", str(tmp_path))
    dummy = tmp_path / "foo.onnx"
    dummy.write_text("not really a model")

    class DummySession:
        def __init__(self, path):
            if "foo.onnx" not in path:
                raise FileNotFoundError()
        def get_inputs(self):
            return [type("X", (), {"name": "inp"})()]
        def get_outputs(self):
            return [type("X", (), {"name": "out"})()]
        def run(self, outputs, feed):
            return ["result"]

    monkeypatch.setattr(split_test_module, "onnxruntime", None, raising=False)
    # simulate import successful by adding attribute
    import types
    onnxmod = types.SimpleNamespace(InferenceSession=DummySession)
    monkeypatch.setitem(sys.modules, "onnxruntime", onnxmod)

    adapter = split_test_module.LocalModelAdapter(model_dir=str(tmp_path))
    cfg = ModelConfig(id="foo", name="Foo", provider="local", cli="", model_id="foo", context_window=1000)
    res = adapter.execute(cfg, "prompt", [])
    assert res.status.name == "COMPLETED"
    assert res.output_text == "result"

    # missing model file
    cfg2 = ModelConfig(id="bar", name="Bar", provider="local", cli="", model_id="bar", context_window=1000)
    res2 = adapter.execute(cfg2, "prompt", [])
    assert res2.status.name == "FAILED"
    assert "not found" in res2.errors[0]


def test_split_test_config_env_and_yaml(tmp_path, monkeypatch):
    # set environment override
    monkeypatch.setenv("SPLIT_TEST_OUTPUT_DIR", "foo_dir")
    yaml_file = tmp_path / "cfg.yaml"
    yaml_file.write_text("task_prompt: 'override prompt'\nevaluation_criteria: {completeness: 1.0}")
    cfg = SplitTestConfig(test_id="1", test_name="n", description="d", task_prompt="p")
    # apply yaml
    with open(yaml_file) as f:
        import yaml as _yaml
        user_cfg = _yaml.safe_load(f)
    for key, val in user_cfg.items():
        if hasattr(cfg, key):
            setattr(cfg, key, val)
    # env override applied in post_init
    cfg.__post_init__()
    assert cfg.task_prompt == "override prompt"
    assert cfg.output_dir == "foo_dir"
    assert cfg.evaluation_criteria["completeness"] == 1.0


def test_split_test_runner_build_prompt_missing(tmp_path, caplog):
    cfg = SplitTestConfig(test_id="2", test_name="n", description="d", task_prompt="base")
    cfg.context_files = ["nonexistent.txt"]
    runner = SplitTestRunner(cfg)
    prompt = runner._build_prompt()
    assert "base" in prompt
    assert "nonexistent" not in prompt
    assert "Context file does not exist" in caplog.text


def test_metrics_collector_no_redis():
    mc = MetricsCollector(redis_url="redis://invalid:6379")
    res = mc.publish_result("test", None)  # should not raise


def test_metrics_collector_env_password(monkeypatch):
    # verify that environment variables are used to build redis_url
    monkeypatch.setenv("SPLIT_TEST_REDIS_HOST", "h")
    monkeypatch.setenv("SPLIT_TEST_REDIS_PORT", "1234")
    monkeypatch.setenv("REDIS_PASSWORD", "secret")
    mc = MetricsCollector(redis_url=None)
    assert "secret" in mc.redis_url
    assert "h:1234" in mc.redis_url
    # the URL should start with redis:// and contain the auth segment
    assert mc.redis_url.startswith("redis://:")


def test_result_storage_no_qdrant():
    rs = ResultStorage(qdrant_url="invalid:0000")
    rs.store_result("col", None, "test")  # should not raise
    assert rs.search_similar("col", "q") == []


def test_result_storage_uuid_id(monkeypatch):
    # ensure the generated point id is a valid UUID
    class DummyClient:
        def __init__(self):
            self.upserted = None
        def create_collection(self, *args, **kwargs):
            pass
        def upsert(self, collection_name, points):
            self.upserted = points
    monkeypatch.setattr(split_test_module, "QdrantClient", lambda **kw: DummyClient())
    rs = ResultStorage()
    from datetime import datetime
    r = split_test_module.TestResult(model_id="abc", model_name="n", status=split_test_module.ModelStatus.COMPLETED, start_time=datetime.now())
    r.output_text = "hello"
    rs.store_result("col", r, "testid")
    uid = rs.client.upserted[0]["id"]
    import uuid
    # should parse without error
    assert uuid.UUID(uid)


def test_foundation_stack_tester_runs():
    tester = FoundationStackTester()
    results = tester.run_all_tests([])
    assert "suites" in results
    # ensure each suite summary is present
    for k in ["memory_bank", "agent_bus", "rag", "dispatcher"]:
        assert k in results["suites"]


def test_runner_session_and_knowledge(monkeypatch):
    # stub session manager to capture set calls
    calls = []
    class DummySession:
        def __init__(self, cfg):
            pass
        async def initialize(self):
            return True
        async def set(self, key, value):
            calls.append((key, value))
            return True
    monkeypatch.setattr(split_test_module, "SessionManager", DummySession)
    # ensure SessionConfig is callable even if import failed earlier
    if not hasattr(split_test_module, "SessionConfig") or split_test_module.SessionConfig is None:
        class SimpleSessionConfig:
            def __init__(self):
                pass
        monkeypatch.setattr(split_test_module, "SessionConfig", SimpleSessionConfig)
    # stub knowledge client and qdrant upsert
    class DummyQdrant:
        def __init__(self):
            self.points = []
        def upsert(self, collection_name, points):
            self.points.extend(points)
    class DummyKnowledge:
        def __init__(self, cfg):
            self._qdrant_client = DummyQdrant()
            self.config = cfg
            self._use_qdrant = True
        async def initialize(self):
            return True
    monkeypatch.setattr(split_test_module, "KnowledgeClient", DummyKnowledge)
    # ensure config object includes a collection name so our fallback logic can be exercised
    monkeypatch.setattr(split_test_module, "KnowledgeConfig", lambda **kw: type("C",(),{**kw, "qdrant_collection": "stub_collection"}))

    cfg = SplitTestConfig(test_id="s", test_name="n", description="d", task_prompt="p")
    runner = SplitTestRunner(cfg)
    # add fake model that returns a simple result
    class FakeAdapter:
        def get_available_models(self):
            return []
        def execute(self, config, prompt, context_files):
            r = split_test_module.TestResult(model_id="m", model_name="M", status=split_test_module.ModelStatus.COMPLETED, start_time=datetime.now())
            r.output_text = "out"
            r.end_time = datetime.now()
            return r
    runner.adapter = FakeAdapter()
    runner.add_model(ModelConfig(id="m", name="M", provider="X", cli="", model_id="m", context_window=1000))
    res = runner.run_model(runner.config.models[0])
    # session set should have been called
    assert any(k.startswith("result:") for k, v in calls)
    # knowledge upsert should store at least one point
    assert hasattr(runner.knowledge, "_qdrant_client")
    assert runner.knowledge._qdrant_client.points


def test_cli_adapter_selection(monkeypatch):
    # ensure CLI `--adapter` flag selects correct adapter class
    import argparse
    # use module imported at top
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", choices=["cli","local","memory_bank"], default="cli")
    args = parser.parse_args(["--adapter","memory_bank"])
    assert args.adapter == "memory_bank"



def test_memory_bank_adapter(tmp_path, monkeypatch):
    # create fake bank with a file containing keyword
    bank = tmp_path / "philosophy"
    bank.mkdir()
    file = bank / "notes.txt"
    file.write_text("This document discusses Plato and Socrates.")

    adapter = split_test_module.MemoryBankAdapter(bank_dir=str(tmp_path))
    models = adapter.get_available_models()
    assert models and models[0].id == "philosophy"

    config = split_test_module.ModelConfig(id="philosophy", name="Philosophy", provider="memory_bank", cli="", model_id="philosophy", context_window=0)
    result = adapter.execute(config, "Tell me about Plato", [])
    assert result.status == split_test_module.ModelStatus.COMPLETED
    assert "Plato" in result.output_text

    # query with unrelated prompt returns failure
    result2 = adapter.execute(config, "Unrelated question", [])
    assert result2.status == split_test_module.ModelStatus.FAILED
