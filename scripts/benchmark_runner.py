#!/usr/bin/env python3
"""
XNAi Benchmark Runner - Python Implementation
==============================================

Programmatic benchmark execution with metrics collection.
Integrates with app/XNAi_rag_app/core/metrics.py for performance tracking.

Usage:
    python scripts/benchmark_runner.py --env E5 --model opus-4.6
    python scripts/benchmark_runner.py --all --output ./benchmark-results

Features:
- Context pack generation (E1-E5 environments)
- Metrics collection via Prometheus
- Redis stream publishing
- JSON manifest output
- Async execution support
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# Enums & Data Models
# ============================================================================


class Environment(str, Enum):
    """Benchmark environment types."""

    E1_COLD_START = "E1"
    E2_README_ONLY = "E2"
    E3_RAW_CODEBASE = "E3"
    E4_MINIMAL_MEMORY = "E4"
    E5_FULL_PROTOCOL = "E5"


@dataclass
class ContextPack:
    """Generated context pack."""

    environment: str
    path: Path
    lines: int = 0
    bytes: int = 0
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class BenchmarkRun:
    """Benchmark run metadata."""

    benchmark_version: str = "v1.0.0"
    runner_version: str = "v1.0.0"
    tag: str = ""
    git_sha: str = ""
    model: str = ""
    environments: List[str] = field(default_factory=list)
    output_dir: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    hostname: str = ""
    context_packs: List[Dict[str, Any]] = field(default_factory=list)


# ============================================================================
# Context Pack Generators
# ============================================================================


class ContextPackGenerator:
    """Generates context packs for each environment."""

    def __init__(self, repo_path: Path, output_dir: Path):
        self.repo_path = repo_path
        self.output_dir = output_dir

    def generate_all(self) -> List[ContextPack]:
        """Generate all environment context packs."""
        packs = []
        for env in Environment:
            pack = self.generate(env)
            packs.append(pack)
        return packs

    def generate(self, env: Environment) -> ContextPack:
        """Generate context pack for specific environment."""
        generator_map = {
            Environment.E1_COLD_START: self._generate_e1,
            Environment.E2_README_ONLY: self._generate_e2,
            Environment.E3_RAW_CODEBASE: self._generate_e3,
            Environment.E4_MINIMAL_MEMORY: self._generate_e4,
            Environment.E5_FULL_PROTOCOL: self._generate_e5,
        }

        env_dir = self.output_dir / f"{env.value.lower()}-{env.name.split('_')[1].replace('_', '-').lower()}"
        env_dir.mkdir(parents=True, exist_ok=True)

        content = generator_map[env]()
        context_path = env_dir / "context.md"

        with open(context_path, "w") as f:
            f.write(content)

        pack = ContextPack(
            environment=env.value, path=context_path, lines=len(content.splitlines()), bytes=len(content.encode())
        )

        logger.info(f"Generated {env.value}: {context_path} ({pack.lines} lines)")
        return pack

    def _generate_e1(self) -> str:
        """E1: Cold Start - repo path only, no context."""
        return f"""# E1: Cold Start Context

No project documentation provided. The model receives only the repository path.

Repository path: {self.repo_path}

Instructions: Navigate and explore the codebase using available tools.
No files are pre-loaded into context.
"""

    def _generate_e2(self) -> str:
        """E2: README Only - just the README content."""
        readme_path = None
        for candidate in ["README.md", "readme.md", "README.rst", "README"]:
            potential = self.repo_path / candidate
            if potential.exists():
                readme_path = potential
                break

        if not readme_path:
            return "# E2: README Only — NO README FOUND\n\nNo README file found in repository."

        readme_content = readme_path.read_text()
        return f"""# E2: README Only Context

The model receives only the project README. No other files pre-loaded.

---

{readme_content}
"""

    def _generate_e3(self) -> str:
        """E3: Raw Codebase - full repo except memory_bank/."""
        try:
            result = subprocess.run(
                ["tree", "-L", "2", "--charset", "ascii", "-I", "memory_bank|__pycache__|.git|node_modules|.venv"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )
            tree_output = result.stdout if result.returncode == 0 else "(tree generation failed)"
        except FileNotFoundError:
            tree_output = "(tree not installed)"

        return f"""# E3: Raw Codebase Context

The model has full repo access EXCEPT memory_bank/.
Tool-based exploration is allowed.

## Excluded Paths
- memory_bank/ (all files and subdirectories)

## Repository Structure
{tree_output}
"""

    def _generate_e4(self) -> str:
        """E4: Minimal Memory - activeContext.md + progress.md only."""
        files = ["memory_bank/activeContext.md", "memory_bank/progress.md"]

        sections = []
        for file_path in files:
            full_path = self.repo_path / file_path
            if full_path.exists():
                sections.append(f"---\n## File: {file_path}\n\n{full_path.read_text()}\n")
            else:
                sections.append(f"## File: {file_path} — NOT FOUND\n")

        return f"""# E4: Minimal Memory Bank Context

The model receives only activeContext.md and progress.md.

{"".join(sections)}
"""

    def _generate_e5(self) -> str:
        """E5: Full Protocol - 15-file XNAi Onboarding Protocol."""
        files = [
            "memory_bank/INDEX.md",
            "memory_bank/activeContext.md",
            "memory_bank/progress.md",
            "memory_bank/CONTEXT.md",
            "configs/agent-identity.yaml",
            "configs/model-router.yaml",
            "configs/free-providers-catalog.yaml",
            ".opencode/RULES.md",
            "memory_bank/teamProtocols.md",
            "docs/architecture/XNAI-AGENT-TAXONOMY.md",
            "memory_bank/ARCHITECTURE.md",
            "expert-knowledge/esoteric/maat_ideals.md",
            "expert-knowledge/origins/xoe-journey-v1.0.0.md",
            "AGENTS.md",
        ]

        sections = []
        for file_path in files:
            full_path = self.repo_path / file_path
            if full_path.exists():
                sections.append(f"---\n## File: {file_path}\n\n{full_path.read_text()}\n")
            else:
                sections.append(f"---\n## File: {file_path} — NOT FOUND IN SNAPSHOT\n")

        return f"""# E5: Full XNAi Onboarding Protocol Context

15 files from the XNAi Onboarding Protocol v1.0.0.

{"".join(sections)}
"""


# ============================================================================
# Metrics Integration
# ============================================================================


def record_benchmark_metrics(run: BenchmarkRun, packs: List[ContextPack]) -> None:
    """Record benchmark metrics via Prometheus."""
    try:
        from XNAi_rag_app.core.metrics import (
            benchmark_run_status,
            benchmark_comparison_score,
            record_structured_log_event,
        )

        # Record benchmark status (1 = running, 2 = completed)
        for pack in packs:
            benchmark_run_status.labels(benchmark_type="context_engineering", hardware_config=run.model or "unknown").set(
                2
            )  # completed

        logger.info("Recorded benchmark metrics to Prometheus")

    except ImportError:
        logger.warning("Metrics module not available, skipping metrics recording")


# ============================================================================
# Manifest Generation
# ============================================================================


def write_manifest(run: BenchmarkRun) -> Path:
    """Write benchmark run manifest to JSON file."""
    manifest_path = Path(run.output_dir) / "manifest.json"

    manifest_data = asdict(run)
    manifest_data["context_packs"] = [asdict(p) for p in run.context_packs]

    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=2, default=str)

    logger.info(f"Wrote manifest: {manifest_path}")
    return manifest_path


# ============================================================================
# Main Entry Point
# ============================================================================


def main():
    parser = argparse.ArgumentParser(description="XNAi Benchmark Runner - Generate context packs for benchmarking")
    parser.add_argument(
        "-e",
        "--env",
        choices=["E1", "E2", "E3", "E4", "E5", "all"],
        default="all",
        help="Environment to generate (default: all)",
    )
    parser.add_argument("-m", "--model", default="", help="Model identifier for results naming")
    parser.add_argument(
        "-o", "--output", default="/tmp/xnai-benchmark", help="Output directory (default: /tmp/xnai-benchmark)"
    )
    parser.add_argument("--metrics", action="store_true", help="Record metrics to Prometheus")
    parser.add_argument("--repo", default=".", help="Repository path (default: current directory)")

    args = parser.parse_args()

    # Resolve paths
    repo_path = Path(args.repo).resolve()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get git info
    try:
        git_sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=repo_path
        ).stdout.strip()
    except Exception:
        git_sha = "unknown"

    # Create run label
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_label = f"{args.model}-{timestamp}" if args.model else f"run-{timestamp}"
    run_output = output_dir / run_label
    run_output.mkdir(parents=True, exist_ok=True)

    # Determine environments
    if args.env == "all":
        environments = [e.value for e in Environment]
    else:
        environments = [args.env]

    # Generate context packs
    logger.info(f"Generating context packs for: {', '.join(environments)}")
    generator = ContextPackGenerator(repo_path, run_output)

    packs = []
    for env_str in environments:
        env = Environment(env_str)
        pack = generator.generate(env)
        packs.append(pack)

    # Create run metadata
    run = BenchmarkRun(
        tag="HEAD",
        git_sha=git_sha,
        model=args.model,
        environments=environments,
        output_dir=str(run_output),
        hostname=os.uname().nodename,
        context_packs=[{"environment": p.environment, "path": str(p.path), "lines": p.lines, "bytes": p.bytes} for p in packs],
    )

    # Write manifest
    write_manifest(run)

    # Record metrics if requested
    if args.metrics:
        record_benchmark_metrics(run, packs)

    # Print summary
    print("\n" + "=" * 70)
    print("XNAi Benchmark Runner - Summary")
    print("=" * 70)
    print(f"  Output: {run_output}")
    print(f"  Environments: {', '.join(environments)}")
    print(f"  Context Packs: {len(packs)}")
    print("\nContext Pack Files:")
    for pack in packs:
        print(f"  {pack.environment}: {pack.path} ({pack.lines} lines, {pack.bytes} bytes)")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
