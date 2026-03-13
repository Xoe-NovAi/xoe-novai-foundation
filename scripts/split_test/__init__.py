#!/usr/bin/env python3
"""
XNAi Foundation — Modular Split Test Framework
==============================================
A flexible, modular system for comparing AI models across multiple dimensions.

Features:
- Pluggable model adapters
- Redis-backed real-time metrics
- Qdrant/FAISS result storage and similarity search
- Vikunja task integration
- Extensible evaluation framework

Usage:
    from split_test.core import SplitTestRunner
    runner = SplitTestRunner(config_path="configs/split-test.yaml")
    runner.add_model("raptor", model_config)
    runner.run()
    results = runner.compare()

Author: XNAi Foundation
Date: 2026-02-26
"""

import argparse
import json
import os
import subprocess
import time
import logging
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

# foundation services
try:
    from XNAi_rag_app.core.infrastructure import KnowledgeClient, KnowledgeConfig, SessionManager
    from XNAi_rag_app.core.infrastructure.session_manager import SessionConfig
except ImportError:
    KnowledgeClient = None
    KnowledgeConfig = None
    SessionManager = None
    SessionConfig = None

# setup logging early so other modules can use it
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('split_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import stack components
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from qdrant_client import QdrantClient

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# ============================================================================
# UTILITIES & HARDENING HELPERS
# ============================================================================

class CircuitBreakerOpenError(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func: Callable, *args, **kwargs):
        if self.state == "open":
            if time.time() - (self.last_failure_time or 0) > self.timeout:
                self.state = "half-open"
            else:
                raise CircuitBreakerOpenError()

        try:
            result = func(*args, **kwargs)
            self.state = "closed"
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise


def retry_with_backoff(func: Callable, max_attempts: int = 3, base_delay: float = 1.0, *args, **kwargs):
    for attempt in range(max_attempts):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt+1} failed: {e}. Retrying in {delay}s")
            time.sleep(delay)

# ============================================================================
# DATA CLASSES
# ============================================================================


class ModelStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ModelConfig:
    """Configuration for a test model."""

    id: str
    name: str
    provider: str
    cli: str
    model_id: str
    context_window: int
    max_output: int = 64000
    capabilities: List[str] = field(default_factory=list)
    cost: str = "free"
    cli_template: str = '{cli} --model {model_id} "{prompt}"'
    env_vars: Dict[str, str] = field(default_factory=dict)

    def to_command(self, prompt: str) -> List[str]:
        """Generate CLI command for this model.

        Uses ``shlex.split`` so that quoted arguments (especially the prompt) are
        handled safely and avoid shell injection.
        """
        import shlex

        rendered = self.cli_template.format(cli=self.cli, model_id=self.model_id, prompt=prompt)
        try:
            cmd = shlex.split(rendered)
        except Exception:
            # fallback to simple split if something goes wrong
            cmd = rendered.split()
        return cmd


@dataclass
class TestResult:
    """Result from a single model test run."""

    model_id: str
    model_name: str
    status: ModelStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    output_path: Optional[str] = None
    output_text: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "output_path": self.output_path,
            "output_length": len(self.output_text),
            "metrics": self.metrics,
            "errors": self.errors,
        }


@dataclass
class SplitTestConfig:
    """Configuration for a split test."""

    test_id: str
    test_name: str
    description: str
    task_prompt: str
    context_files: List[str] = field(default_factory=list)
    output_dir: str = "memory_bank/handovers/split-test/outputs"
    models: List[ModelConfig] = field(default_factory=list)
    evaluation_criteria: Dict[str, float] = field(default_factory=dict)
    redis_stream: str = "xnai:split_test"
    qdrant_collection: str = "split_test_results"
    # helpers
    timeout: Optional[int] = None
    retry_attempts: int = 1
    retry_delay_seconds: float = 1.0

    def __post_init__(self):
        # load defaults from YAML file if available
        if YAML_AVAILABLE:
            config_path = Path(os.getenv("SPLIT_TEST_CONFIG", "configs/split-test-defaults.yaml"))
            if config_path.exists():
                with open(config_path) as f:
                    defaults = yaml.safe_load(f)
                    if not self.evaluation_criteria:
                        self.evaluation_criteria = defaults.get("evaluation_criteria", {})
                    # propagate some common defaults into config
                    timeout = defaults.get("defaults", {}).get("timeout_seconds")
                    if timeout:
                        self.timeout = timeout
                    retry = defaults.get("defaults", {}).get("retry_attempts")
                    if retry:
                        self.retry_attempts = retry
                    delay = defaults.get("defaults", {}).get("retry_delay_seconds")
                    if delay:
                        self.retry_delay_seconds = delay
                    # override paths if provided
                    self.output_dir = defaults.get("output", {}).get("directory", self.output_dir)
                    self.redis_stream = defaults.get("redis", {}).get("stream_prefix", self.redis_stream)
                    self.qdrant_collection = defaults.get("qdrant", {}).get("collection_prefix", self.qdrant_collection)
        # environment variable overrides
        self.output_dir = os.getenv("SPLIT_TEST_OUTPUT_DIR", self.output_dir)
        self.redis_stream = os.getenv("SPLIT_TEST_REDIS_STREAM", self.redis_stream)
        self.qdrant_collection = os.getenv("SPLIT_TEST_QDRANT_COLLECTION", self.qdrant_collection)
        # context files may be relative to memory_bank root; ensure they exist or warn
        valid_contexts = []
        for ctx in self.context_files:
            path = Path(ctx)
            if not path.exists():
                logger.warning(f"Context file not found during config init: {ctx}")
            valid_contexts.append(ctx)
        self.context_files = valid_contexts


# ============================================================================
# MODEL ADAPTERS (Pluggable)
# ============================================================================


class ModelAdapter(ABC):
    """Abstract base class for model adapters."""

    @abstractmethod
    def execute(self, config: ModelConfig, prompt: str, context_files: List[str]) -> TestResult:
        """Execute a test run with this model."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[ModelConfig]:
        """Return list of available models for this adapter."""
        pass


class CLIAdapter(ModelAdapter):
    """Adapter for CLI-based models (Copilot, OpenCode, Cline)."""

    def __init__(self):
        self.cli_paths = {"copilot": "~/.local/bin/copilot", "opencode": "opencode", "cline": "cline", "gemini": "gemini"}
        # circuit breakers per CLI to avoid cascading failures
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}

    def _validate_cli(self, cli: str) -> bool:
        """Check that the CLI binary exists on PATH or known location."""
        path = shutil.which(cli) or shutil.which(os.path.expanduser(cli))
        if path is None:
            logger.error(f"CLI binary not found: {cli}")
            return False
        return True

    def execute(self, config: ModelConfig, prompt: str, context_files: List[str]) -> TestResult:
        """Execute test via CLI with retry/circuit-breaker and logging."""
        result = TestResult(model_id=config.id, model_name=config.name, status=ModelStatus.RUNNING, start_time=datetime.now())

        # ensure CLI exists
        if not self._validate_cli(config.cli):
            result.status = ModelStatus.FAILED
            result.errors.append(f"CLI not found: {config.cli}")
            result.end_time = datetime.now()
            return result

        # get or create circuit breaker for this cli
        breaker = self._circuit_breakers.setdefault(config.cli, CircuitBreaker())

        def _run():
            # Build command safely (list form to avoid shell injection)
            cmd = config.to_command(prompt)

            logger.debug(f"Executing command: {cmd}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd(),
                env={**os.environ, **config.env_vars},
            )

            try:
                stdout, stderr = process.communicate(timeout=config.max_output or 600)
            except subprocess.TimeoutExpired:
                process.kill()
                raise

            return stdout, stderr, process.returncode

        try:
            stdout, stderr, return_code = retry_with_backoff(lambda: breaker.call(_run),
                                                             max_attempts=getattr(config, 'retry_attempts', 1),
                                                             base_delay=getattr(config, 'retry_delay_seconds', 1))

            result.output_text = stdout
            result.end_time = datetime.now()
            # treat non-zero exit codes as failures as well
            if return_code != 0:
                result.status = ModelStatus.FAILED
                result.errors.append(f"Non-zero exit code: {return_code}")
            else:
                result.status = ModelStatus.COMPLETED

            if stderr:
                result.errors.append(stderr)

            # Extract metrics
            result.metrics = {
                "exit_code": return_code,
                "output_length": len(stdout),
                "duration_seconds": result.duration_seconds,
                "tokens_per_second": len(stdout) / max(result.duration_seconds, 1),
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout for model {config.id}")
            result.errors.append("Timeout")
            result.status = ModelStatus.FAILED
            result.end_time = datetime.now()
        except CircuitBreakerOpenError:
            logger.error(f"Circuit breaker open for CLI {config.cli}")
            result.errors.append("Circuit breaker open")
            result.status = ModelStatus.FAILED
            result.end_time = datetime.now()
        except Exception as e:
            logger.exception(f"Unexpected error for {config.id}")
            result.errors.append(str(e))
            result.status = ModelStatus.FAILED
            result.end_time = datetime.now()

        return result

    def get_available_models(self) -> List[ModelConfig]:
        """Return available models from config."""
        models = []

        # Load from model-router.yaml if available
        if YAML_AVAILABLE:
            config_path = Path("configs/model-router.yaml")
            if config_path.exists():
                with open(config_path) as f:
                    router_config = yaml.safe_load(f)
                    for provider in router_config.get("providers", []):
                        for model in provider.get("models", []):
                            cli = provider.get("cli", "")
                            if cli in self.cli_paths:
                                models.append(
                                    ModelConfig(
                                        id=model.get("id", ""),
                                        name=model.get("name", ""),
                                        provider=provider.get("name", ""),
                                        cli=cli,
                                        model_id=model.get("id", ""),
                                        context_window=model.get("context_length", 200000),
                                        max_output=model.get("max_output", 64000),
                                        capabilities=model.get("capabilities", []),
                                        cost=provider.get("cost", "unknown"),
                                    )
                                )
        # if no models discovered (e.g. YAML missing or CLIs unavailable) fall
        # back to a small hardcoded set useful for Wave 5 tests
        if not models:
            logger.warning("No CLI models found in router; using defaults")
            for mid, name in [
                ("raptor-mini-preview", "Raptor Mini"),
                ("claude-haiku-4-5", "Claude Haiku 4.5"),
                ("minimax-m2.5-free", "MiniMax M2.5 Free"),
                ("kat-coder-pro", "kat-coder-pro"),
            ]:
                # determine provider by prefix heuristic
                provider = "GitHub Copilot" if "copilot" in mid or "haiku" in mid else "OpenCode/Cline"
                cli = "copilot" if provider.startswith("GitHub") else ("opencode" if "minimax" in mid else "cline")
                models.append(
                    ModelConfig(
                        id=mid,
                        name=name,
                        provider=provider,
                        cli=cli,
                        model_id=mid,
                        context_window=200000,
                        max_output=64000,
                    )
                )

        return models


# ============================================================================
# LOCAL MODEL SUPPORT
# ============================================================================

class LocalModelAdapter(ModelAdapter):
    """Adapter for running local Foundation stack models via ONNX/GGUF.

    Models are expected to live in a directory specified by ``LOCAL_MODEL_DIR``
    env var or passed to the constructor.  The adapter scans for ``.onnx`` and
    ``.gguf`` files and exposes them through ``get_available_models``.  Execution
    uses ``onnxruntime`` when available; errors are caught and turned into
    ``TestResult`` failures so the runner can continue.
    """

    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or os.getenv("LOCAL_MODEL_DIR", "models")
        try:
            import onnxruntime  # type: ignore
            self._onnx = onnxruntime
            self.onnx_available = True
        except ImportError:
            self._onnx = None
            self.onnx_available = False

    def execute(self, config: ModelConfig, prompt: str, context_files: List[str]) -> TestResult:
        result = TestResult(model_id=config.id, model_name=config.name, status=ModelStatus.RUNNING, start_time=datetime.now())

        if not self.onnx_available:
            err = "ONNX Runtime not available"
            logger.error(err)
            result.errors.append(err)
            result.status = ModelStatus.FAILED
            result.end_time = datetime.now()
            return result

        model_path = Path(self.model_dir) / f"{config.model_id}.onnx"
        if not model_path.exists():
            err = f"Local model file not found: {model_path}"
            logger.error(err)
            result.errors.append(err)
            result.status = ModelStatus.FAILED
            result.end_time = datetime.now()
            return result

        try:
            sess = self._onnx.InferenceSession(str(model_path))
            input_name = sess.get_inputs()[0].name
            output_name = sess.get_outputs()[0].name

            # the interface here is intentionally naive; real models will
            # require proper tokenization and batching.
            output = sess.run([output_name], {input_name: prompt})
            result.output_text = str(output[0])
            result.status = ModelStatus.COMPLETED
        except Exception as e:
            logger.exception(f"Local model inference failed for {config.model_id}: {e}")
            result.errors.append(str(e))
            result.status = ModelStatus.FAILED
        finally:
            result.end_time = datetime.now()

        # basic metrics
        result.metrics = {
            "output_length": len(result.output_text),
            "duration_seconds": result.duration_seconds,
        }
        return result

    def get_available_models(self) -> List[ModelConfig]:
        models: List[ModelConfig] = []
        root = Path(self.model_dir)
        if root.exists() and root.is_dir():
            for file in root.iterdir():
                if file.suffix in [".onnx", ".gguf"]:
                    mid = file.stem
                    models.append(
                        ModelConfig(
                            id=mid,
                            name=mid,
                            provider="local",
                            cli="",
                            model_id=mid,
                            context_window=200000,
                        )
                    )
        return models


# ============================================================================
# MEMORY BANK ADAPTER (for specialized knowledge retrieval)
# ============================================================================

class MemoryBankAdapter(ModelAdapter):
    """Adapter that treats a memory bank as a model.

    Each "model" corresponds to a named memory bank directory under
    ``memory_bank/multi_expert/``.  Execution simply queries the bank for
    relevant passages using a simple semantic search (Qdrant/FAISS or naive
    keyword matching) and returns the top hit as the output text.

    This enables the split test runner to evaluate the effectiveness of
    domain-specific memory banks in answering questions or generating
    content.
    """

    def __init__(self, bank_dir: Optional[str] = None):
        # default to first level of multi_expert if not provided
        self.base_dir = Path(bank_dir or "memory_bank/multi_expert")
        # simple in-memory cache of banks
        self.banks = {}
        # initialize search client if available
        try:
            from qdrant_client import QdrantClient
            self._qdrant = QdrantClient(host="localhost", port=6333)
        except Exception:
            self._qdrant = None

    def get_available_models(self) -> List[ModelConfig]:
        models = []
        if self.base_dir.exists():
            for sub in self.base_dir.iterdir():
                if sub.is_dir():
                    models.append(ModelConfig(
                        id=sub.name,
                        name=sub.name.replace("_", " ").title(),
                        provider="memory_bank",
                        cli="",
                        model_id=sub.name,
                        context_window=0,
                    ))
        return models

    def execute(self, config: ModelConfig, prompt: str, context_files: List[str]) -> TestResult:
        result = TestResult(model_id=config.id, model_name=config.name, status=ModelStatus.RUNNING, start_time=datetime.now())
        # naive implementation: attempt Qdrant semantic search, but always
        # fall back to keyword scanning if it fails or is unavailable.
        output = ""
        try:
            bank_path = self.base_dir / config.model_id
            if self._qdrant:
                # perform semantic query on bank collection
                coll = config.model_id
                try:
                    resp = self._qdrant.search(collection_name=coll, query_vector=self._simple_embedding(prompt), limit=1)
                    if resp:
                        output = resp[0].payload.get("text", "")
                except Exception:
                    logger.warning("Qdrant search failed, falling back to keyword scan")
                    output = ""
            # if no output from Qdrant or qdrant unavailable, try simple file search
            if not output:
                tokens = [w.lower() for w in prompt.split()[:5]]
                for file in bank_path.glob("**/*"):
                    if file.is_file():
                        text = file.read_text(errors="ignore")
                        lower_text = text.lower()
                        if any(tok in lower_text for tok in tokens):
                            output = text[:1000]
                            break
        except Exception as e:
            logger.warning(f"MemoryBankAdapter error: {e}")

        if output:
            result.output_text = output
            result.status = ModelStatus.COMPLETED
        else:
            result.errors.append("No relevant content found")
            result.status = ModelStatus.FAILED
        result.end_time = datetime.now()
        result.metrics = {"length": len(result.output_text)}
        return result


# ============================================================================
# METRICS COLLECTION (Redis Integration)
# ============================================================================


class MetricsCollector:
    """Collects and stores metrics in Redis.

    The constructor accepts a full Redis URL (``redis://``) or, when none is
    provided, will synthesize one from environment variables.  This allows
    callers to simply set ``REDIS_PASSWORD`` / ``SPLIT_TEST_REDIS_HOST`` etc
    without needing to build the URL themselves.
    """

    def __init__(self, redis_url: Optional[str] = None):
        # if the caller did not supply a URL, build one from environment
        if not redis_url:
            # first look for an explicit override
            redis_url = os.getenv("SPLIT_TEST_REDIS_URL")
        if not redis_url:
            host = os.getenv("SPLIT_TEST_REDIS_HOST", "localhost")
            port = os.getenv("SPLIT_TEST_REDIS_PORT", "6379")
            db = os.getenv("SPLIT_TEST_REDIS_DB", "0")
            password = os.getenv("REDIS_PASSWORD", "")
            creds = f":{password}@" if password else ""
            redis_url = f"redis://{creds}{host}:{port}/{db}"
        self.redis_url = redis_url
        self.client = None
        if REDIS_AVAILABLE:
            try:
                self.client = redis.from_url(self.redis_url)
                self.client.ping()
            except Exception as e:
                logger.warning(f"Redis not available: {e}")

    def publish_result(self, test_id: str, result: TestResult):
        """Publish a test result to Redis stream."""
        if not self.client:
            logger.debug("Skipping publish_result: Redis client not available")
            return

        stream_key = f"{test_id}:results"
        try:
            self.client.xadd(
                stream_key,
                {
                    "model_id": result.model_id,
                    "model_name": result.model_name,
                    "status": result.status.value,
                    "duration": str(result.duration_seconds),
                    "output_length": str(len(result.output_text)),
                    "timestamp": datetime.now().isoformat(),
                },
            )
            # also publish simple count of errors
            if result.errors:
                self.client.hincrby(f"{test_id}:errors", result.model_id, 1)
        except Exception as e:
            logger.warning(f"Failed to publish result to Redis: {e}")

    def get_stream_results(self, test_id: str, count: int = 100) -> List[Dict]:
        """Retrieve results from Redis stream."""
        if not self.client:
            logger.debug("get_stream_results called but Redis client not available")
            return []

        stream_key = f"{test_id}:results"
        try:
            results = self.client.xrange(stream_key, count=count)
            return [{"id": r[0], **json.loads(r[1]["data"])} for r in results]
        except Exception as e:
            logger.warning(f"Error reading from Redis stream {stream_key}: {e}")
            return []

    def publish_metric(self, test_id: str, metric_name: str, value: float):
        """Publish a single metric."""
        if not self.client:
            return

        self.client.hincrbyfloat(f"{test_id}:metrics", metric_name, value)


# ============================================================================
# RESULT STORAGE (Qdrant + FAISS)
# ============================================================================


class ResultStorage:
    """Stores test results in Qdrant for semantic search."""

    def __init__(self, qdrant_url: str = "localhost:6333"):
        self.client = None
        if QDRANT_AVAILABLE:
            try:
                self.client = QdrantClient(host="localhost", port=6333)
            except Exception as e:
                logger.warning(f"Qdrant not available: {e}")

    def store_result(self, collection: str, result: TestResult, test_id: str):
        """Store a test result in Qdrant."""
        if not self.client:
            logger.debug("Skipping store_result: Qdrant client not available")
            return

        # Create collection if not exists.  We explicitly declare a
        # vector field named "vector" so that later upserts with that key
        # will succeed regardless of Qdrant's default behavior.  The size is
        # determined from a dummy embedding; mismatched sizes are tolerated by
        # Qdrant as it auto-resizes when necessary.
        try:
            vec_size = len(self._simple_embedding(result.output_text))
            # use anonymous vector params (not a dict) so collection has an
            # unnamed default vector.  upserts later can then use the
            # top-level "vector" key rather than the newer "vectors" map.
            from qdrant_client.models import VectorParams

            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=vec_size, distance="Cosine"),
            )
        except Exception:
            # collection may already exist or parameters conflict, ignore
            pass

        # Store result
        try:
            # Qdrant requires point IDs to be either unsigned ints or UUIDs.  We
            # generate a deterministic UUID from the test/model pair so that
            # repeated runs will upsert the same point rather than throwing an
            # error.
            import uuid

            uid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{test_id}_{result.model_id}"))

            self.client.upsert(
                collection_name=collection,
                points=[
                    {
                        "id": uid,
                        "vector": self._simple_embedding(result.output_text),
                        "payload": result.to_dict(),
                    }
                ],
            )
        except Exception as e:
            msg = str(e)
            # if the collection exists but the vector schema doesn't match,
            # attempt to rebuild it and retry once
            if "Not existing vector name" in msg:
                logger.warning("Detected missing vector name in Qdrant collection, rebuilding")
                try:
                    self.client.delete_collection(collection_name=collection)
                except Exception:
                    pass
                try:
                    vec_size = len(self._simple_embedding(result.output_text))
                    from qdrant_client.models import VectorParams
                    self.client.create_collection(
                        collection_name=collection,
                        vectors_config=VectorParams(size=vec_size, distance="Cosine"),
                    )
                    # retry upsert
                    self.client.upsert(
                        collection_name=collection,
                        points=[
                            {
                                "id": uid,
                                "vector": self._simple_embedding(result.output_text),
                                "payload": result.to_dict(),
                            }
                        ],
                    )
                    return
                except Exception as e2:
                    logger.warning(f"Retry upsert after rebuild failed: {e2}")
            logger.warning(f"Failed to upsert result into Qdrant: {e}")

    def search_similar(self, collection: str, query: str, limit: int = 5) -> List[Dict]:
        """Find similar results by semantic search."""
        if not self.client:
            logger.debug("search_similar called but Qdrant client not available")
            return []

        try:
            results = self.client.search(collection_name=collection, query_vector=self._simple_embedding(query), limit=limit)
            return [r.payload for r in results]
        except Exception as e:
            logger.warning(f"Qdrant search error: {e}")
            return []

    def _simple_embedding(self, text: str) -> List[float]:
        """Simple hash-based embedding for comparison."""
        import hashlib

        h = hashlib.sha256(text.encode()).digest()
        return [float(b) / 255.0 for b in h[:64]] + [0.0] * (64 - 64)


# ============================================================================
# EVALUATION FRAMEWORK
# ============================================================================


class Evaluator:
    """Evaluates test results against criteria."""

    def __init__(self, criteria: Dict[str, float]):
        self.criteria = criteria

    def evaluate(self, result: TestResult, reference_output: Optional[str] = None) -> Dict[str, float]:
        """Evaluate a single result."""
        scores = {}

        # Completeness (based on output length vs expected)
        expected_min_length = 5000  # Minimum for Wave 5 manual
        completeness = min(len(result.output_text) / expected_min_length, 1.0) * 100
        scores["completeness"] = completeness

        # Accuracy (simplified - would need LLM-based evaluation)
        accuracy = 80.0  # Placeholder
        scores["accuracy"] = accuracy

        # Actionability (based on structure markers)
        actionability = 75.0
        if "# " in result.output_text and "## " in result.output_text:
            actionability += 10
        if "```" in result.output_text:
            actionability += 5
        scores["actionability"] = min(actionability, 100)

        # Token efficiency
        if result.duration_seconds > 0:
            efficiency = len(result.output_text) / result.duration_seconds
            scores["efficiency"] = min(efficiency / 100, 1.0) * 100
        else:
            scores["efficiency"] = 0

        # Structure
        structure = 70.0
        if "- [ ]" in result.output_text or "- [x]" in result.output_text:
            structure += 10
        if "| " in result.output_text:  # Tables
            structure += 10
        scores["structure"] = min(structure, 100)

        return scores

    def compare(self, results: List[TestResult]) -> Dict[str, Any]:
        """Compare all results and determine winner."""
        evaluations = []

        for result in results:
            if result.status == ModelStatus.COMPLETED:
                scores = self.evaluate(result)
                total = sum(scores.get(criterion, 0) * weight for criterion, weight in self.criteria.items())
                evaluations.append({"model_id": result.model_id, "scores": scores, "total_score": total})

        # Sort by total score
        evaluations.sort(key=lambda x: x["total_score"], reverse=True)

        return {"rankings": evaluations, "winner": evaluations[0] if evaluations else None, "criteria": self.criteria}


# ============================================================================
# MAIN SPLIT TEST RUNNER
# ============================================================================


class SplitTestRunner:
    """Main orchestrator for split tests."""

    def __init__(self, config: SplitTestConfig, adapter: Optional[ModelAdapter] = None):
        self.config = config
        self.results: List[TestResult] = []
        # allow custom adapter injection for local models, etc.
        self.adapter = adapter if adapter is not None else CLIAdapter()

        # compute redis URL once and hand off to metrics collector
        redis_url = os.getenv("SPLIT_TEST_REDIS_URL")
        if not redis_url:
            host = os.getenv("SPLIT_TEST_REDIS_HOST", "localhost")
            port = os.getenv("SPLIT_TEST_REDIS_PORT", "6379")
            db = os.getenv("SPLIT_TEST_REDIS_DB", "0")
            password = os.getenv("REDIS_PASSWORD", "")
            creds = f":{password}@" if password else ""
            redis_url = f"redis://{creds}{host}:{port}/{db}"
        self.metrics = MetricsCollector(redis_url=redis_url)

        self.storage = ResultStorage()
        self.evaluator = Evaluator(config.evaluation_criteria)

        # infrastructure helpers
        self.session: Optional[SessionManager] = None
        if SessionManager:
            try:
                sess_cfg = SessionConfig()
                self.session = SessionManager(sess_cfg)
                import anyio

                anyio.run(self.session.initialize)
            except Exception as e:
                logger.warning(f"SessionManager init failed: {e}")
                self.session = None

        self.knowledge: Optional[KnowledgeClient] = None
        if KnowledgeClient:
            try:
                config_k = KnowledgeConfig(qdrant_url=os.getenv("SPLIT_TEST_QDRANT_URL", None))
                self.knowledge = KnowledgeClient(config_k)
                import anyio
                anyio.run(self.knowledge.initialize)
            except Exception as e:
                logger.warning(f"KnowledgeClient init failed: {e}")
                self.knowledge = None

    def add_model(self, model_config: ModelConfig):
        """Add a model to the test."""
        self.config.models.append(model_config)

    def add_model_from_id(self, model_id: str):
        """Add a model by ID from available models.

        Falls back to a small built-in list if the adapter doesn't know the
        requested model. This prevents empty test runs when YAML or CLI
        detection fails.
        """
        available = self.adapter.get_available_models()
        for model in available:
            if model.id == model_id or model.model_id == model_id:
                self.add_model(model)
                return

        # fallback definitions for the four primary Wave 5 models
        defaults = {
            "raptor-mini-preview": ModelConfig(
                id="raptor-mini-preview",
                name="Raptor Mini",
                provider="GitHub Copilot",
                cli="copilot",
                model_id="raptor-mini-preview",
                context_window=264000,
                max_output=64000,
            ),
            "claude-haiku-4-5": ModelConfig(
                id="claude-haiku-4-5",
                name="Claude Haiku 4.5",
                provider="GitHub Copilot",
                cli="copilot",
                model_id="claude-haiku-4-5",
                context_window=200000,
                max_output=64000,
            ),
            "minimax-m2.5-free": ModelConfig(
                id="minimax-m2.5-free",
                name="MiniMax M2.5 Free",
                provider="OpenCode",
                cli="opencode",
                model_id="minimax-m2.5-free",
                context_window=204800,
                max_output=131072,
            ),
            "kat-coder-pro": ModelConfig(
                id="kat-coder-pro",
                name="kat-coder-pro",
                provider="Cline CLI",
                cli="cline",
                model_id="kat-coder-pro",
                context_window=262144,
                max_output=32768,
            ),
        }
        if model_id in defaults:
            print(f"Adding fallback default model {model_id}")
            self.add_model(defaults[model_id])
            return

        print(f"Model {model_id} not found")

    def run_model(self, model_config: ModelConfig) -> TestResult:
        """Run a single model test."""
        print(f"\n{'=' * 60}")
        print(f"Running: {model_config.name}")
        print(f"Adapter: {self.adapter.__class__.__name__}")
        if isinstance(self.adapter, CLIAdapter):
            print(f"CLI: {model_config.cli} --model {model_config.model_id}")
        print(f"{'=' * 60}")

        # Build prompt with context files (may log missing files)
        prompt = self._build_prompt()

        # Execute
        result = self.adapter.execute(model_config, prompt, self.config.context_files)

        # Save output
        if result.status == ModelStatus.COMPLETED:
            self._save_output(model_config, result)

        # Publish metrics
        self.metrics.publish_result(self.config.test_id, result)

        # Store in Qdrant
        self.storage.store_result(self.config.qdrant_collection, result, self.config.test_id)

        self.results.append(result)

        # record session entry
        if self.session:
            try:
                import anyio
                key = f"result:{result.model_id}"
                anyio.run(self.session.set, key, result.to_dict())
            except Exception as e:
                logger.warning(f"Failed to record session data: {e}")

        # index into knowledge base
        if self.knowledge and getattr(self.knowledge, "_use_qdrant", False):
            try:
                import anyio
                # determine collection name with fallback if config lacks it
                collection_name = getattr(self.knowledge.config, "qdrant_collection", None)
                if not collection_name:
                    collection_name = self.config.qdrant_collection
                # build vector via embedding and upsert document
                def _upsert():
                    client = self.knowledge._qdrant_client
                    txt = result.output_text or ""
                    client.upsert(
                        collection_name=collection_name,
                        points=[
                            {
                                "id": f"{self.config.test_id}_{result.model_id}",
                                "vector": self.storage._simple_embedding(txt),
                                "payload": result.to_dict(),
                            }
                        ],
                    )
                anyio.run(_upsert)
            except Exception as e:
                logger.warning(f"Knowledge index failed: {e}")

        return result

    def run(self, parallel: bool = False):
        """Run all models."""
        print(f"\n{'#' * 60}")
        print(f"# SPLIT TEST: {self.config.test_name}")
        print(f"# Test ID: {self.config.test_id}")
        print(f"# Models: {len(self.config.models)}")
        print(f"{'#' * 60}")

        if parallel:
            # Run in parallel (would need async implementation)
            print("Parallel execution not yet implemented")
        else:
            for model in self.config.models:
                self.run_model(model)

    def compare(self) -> Dict[str, Any]:
        """Compare results and determine winner."""
        return self.evaluator.compare(self.results)

    def export_results(self, output_path: str):
        """Export results to JSON."""
        data = {
            "test_id": self.config.test_id,
            "test_name": self.config.test_name,
            "results": [r.to_dict() for r in self.results],
            "comparison": self.compare(),
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Results exported to: {output_path}")

    def _build_prompt(self) -> str:
        """Build prompt with context files, handling missing or unreadable files."""
        prompt = self.config.task_prompt

        # Add context files if specified
        for ctx_file in self.config.context_files:
            path = Path(ctx_file)
            try:
                if path.exists():
                    with open(path) as f:
                        content = f.read()
                        prompt += f"\n\n# Context from {ctx_file}:\n{content}"
                else:
                    logger.warning(f"Context file does not exist: {ctx_file}")
            except Exception as e:
                logger.exception(f"Failed to read context file {ctx_file}: {e}")
        return prompt

    def _save_output(self, model_config: ModelConfig, result: TestResult):
        """Save model output to file."""
        output_dir = Path(self.config.output_dir) / f"{model_config.id}-wave5-manual"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "WAVE-5-MANUAL.md"
        with open(output_file, "w") as f:
            f.write(result.output_text)

        # Save metrics
        metrics_file = output_dir / "METRICS.json"
        with open(metrics_file, "w") as f:
            json.dump(result.metrics, f, indent=2)

        result.output_path = str(output_file)
        print(f"Output saved to: {output_file}")


# ============================================================================
# CLI ENTRY POINT
# ============================================================================


def main():
    parser = argparse.ArgumentParser(description="XNAi Split Test Runner")
    parser.add_argument("--config", "-c", help="Config file path")
    parser.add_argument("--test-id", "-t", help="Test ID")
    parser.add_argument("--models", "-m", nargs="+", help="Model IDs to test")
    parser.add_argument("--output", "-o", help="Output JSON path")
    parser.add_argument("--list-models", "-l", action="store_true", help="List available models")
    parser.add_argument("--adapter", choices=["cli","local","memory_bank"], default="cli", help="Which adapter to use for model execution")

    args = parser.parse_args()

    # choose adapter
    adapter_choice = args.adapter
    if adapter_choice == "local":
        adapter = LocalModelAdapter()
    elif adapter_choice == "memory_bank":
        adapter = MemoryBankAdapter()
    else:
        adapter = CLIAdapter()

    # runner = SplitTestRunner(cfg, adapter=adapter)  # removed; cfg not defined yet

    if args.list_models:
        adapter = CLIAdapter()
        models = adapter.get_available_models()
        print("\nAvailable Models:")
        print("-" * 60)
        for m in models:
            print(f"{m.id:40} | {m.provider:20} | {m.context_window}K")
        return

    # Create config (with optional YAML file)

    # choose adapter implementation
    adapter_impl = None
    if args.adapter == "local":
        adapter_impl = LocalModelAdapter()

    test_id = args.test_id or f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # start with base config
    config = SplitTestConfig(
        test_id=test_id,
        test_name="Wave 5 Manual Split Test",
        description="Compare AI models for Wave 5 manual creation",
        task_prompt="Create a comprehensive Wave 5 Implementation Manual...",
    )

    # if user specified a config path, merge values
    if args.config:
        try:
            with open(args.config) as f:
                user_cfg = yaml.safe_load(f)
            # map keys
            for key, val in user_cfg.items():
                if hasattr(config, key):
                    setattr(config, key, val)
            logger.debug(f"Loaded test config from {args.config}")
        except Exception as e:
            logger.warning(f"Failed to load config file {args.config}: {e}")

    # Add models
    runner = SplitTestRunner(config, adapter=adapter_impl)

    if args.models:
        for model_id in args.models:
            runner.add_model_from_id(model_id)
    else:
        # Default models for Wave 5 test
        runner.add_model_from_id("raptor-mini-preview")
        runner.add_model_from_id("claude-haiku-4-5")
        runner.add_model_from_id("minimax-m2.5-free")
        runner.add_model_from_id("kat-coder-pro")

    # Run tests
    runner.run()

    # Compare and export
    comparison = runner.compare()
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)

    for i, result in enumerate(comparison["rankings"], 1):
        print(f"\n{i}. {result['model_id']}: {result['total_score']:.1f}/100")
        for criterion, score in result["scores"].items():
            print(f"   {criterion}: {score:.1f}")

    if args.output:
        runner.export_results(args.output)


if __name__ == "__main__":
    main()
