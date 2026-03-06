"""
model_intelligence_ingestion.py
================================
Routinely ingests AI model landscape data into the XNAi RAG system.

Supports two ingestion modes:
1. From OpenRouter snapshot JSON (output of scripts/update-model-intelligence.sh)
2. Live fetch from OpenRouter API (for immediate use)

Each model is stored as a RAG document with:
- Model ID, name, provider, pricing, context window
- Capability tags (free, multimodal, coding, reasoning, etc.)
- Verification status (confirmed_real, version_uncertain, internal_only)

Usage:
    # Ingest from snapshot
    python3 -m app.XNAi_rag_app.model_intelligence_ingestion \
        --ingest expert-knowledge/model-snapshots/openrouter-models-latest.json

    # Live fetch and ingest
    python3 -m app.XNAi_rag_app.model_intelligence_ingestion --live

    # Dry run (show what would be ingested)
    python3 -m app.XNAi_rag_app.model_intelligence_ingestion --live --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.request import urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)

# ─── Constants ───────────────────────────────────────────────────────────────

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/models"
CONFIRMED_REAL_MODELS: dict[str, dict[str, Any]] = {
    "moonshotai/kimi-k2.5": {
        "name": "Kimi K2.5",
        "provider": "Moonshot AI",
        "context_length": 262144,
        "architecture": "1T MoE, 32B active params",
        "multimodal": True,
        "swe_bench": 76.8,
        "pricing_prompt": 0.00000023,
        "pricing_completion": 0.000003,
        "notes": "Native video+image multimodal, Agent Swarm paradigm, confirmed on HuggingFace",
    },
    "minimax/minimax-m2.5": {
        "name": "MiniMax M2.5",
        "provider": "MiniMax",
        "context_length": 204800,
        "swe_bench": 80.2,
        "pricing_prompt": 0.0000003,
        "pricing_completion": 0.0000011,
        "notes": "80.2% SWE-Bench, Chinese AI company, confirmed on OpenRouter",
    },
    "z-ai/glm-5": {
        "name": "GLM-5",
        "provider": "Z.ai (Zhipu AI)",
        "context_length": 204800,
        "pricing_prompt": 0.0000003,
        "pricing_completion": 0.00000255,
        "notes": "938B tokens served on OpenRouter, strong multilingual capabilities",
    },
    "google/gemini-3-pro-preview": {
        "name": "Gemini 3 Pro Preview",
        "provider": "Google",
        "context_length": 1050000,
        "multimodal": True,
        "pricing_prompt": 0.000002,
        "pricing_completion": 0.000012,
        "notes": "1.05M context, confirmed PUBLIC on OpenRouter as of Feb 2026",
    },
    "google/gemini-3-flash-preview": {
        "name": "Gemini 3 Flash Preview",
        "provider": "Google",
        "context_length": 1050000,
        "multimodal": True,
        "pricing_prompt": 0.0000005,
        "pricing_completion": 0.000003,
        "notes": "1.05M context, fast, confirmed PUBLIC on OpenRouter as of Feb 2026",
    },
    "anthropic/claude-sonnet-4-6": {
        "name": "Claude Sonnet 4.6",
        "provider": "Anthropic",
        "context_length": 200000,
        "pricing_prompt": 0.000003,
        "pricing_completion": 0.000015,
        "notes": "Jan 2026 training cutoff, 64K output, current Cline model",
    },
    "anthropic/claude-opus-4-6": {
        "name": "Claude Opus 4.6",
        "provider": "Anthropic",
        "context_length": 200000,
        "pricing_prompt": 0.000005,
        "pricing_completion": 0.000025,
        "notes": "128K output (largest Anthropic output), Aug 2025 cutoff",
    },
}

INTERNAL_ONLY_MODELS: set[str] = {
    "opencode/big-pickle",
    "opencode/kimi-k2.5-free",
    "opencode/gpt-5-nano",
    "opencode/minimax-m2.5-free",
    "opencode/glm-5-free",
    "google/antigravity-gemini-3-pro",
    "google/antigravity-gemini-3-flash",
    "google/antigravity-claude-sonnet-4-6",
    "google/antigravity-claude-opus-4-6-thinking",
    "google/antigravity-claude-opus-4-5-thinking",
    "google/antigravity-claude-sonnet-4-5",
}


# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class ModelDocument:
    """A RAG document representing a single AI model."""

    model_id: str
    name: str
    provider: str
    context_length: int
    pricing_prompt: float  # per token (NOT per million)
    pricing_completion: float  # per token
    is_free: bool
    is_multimodal: bool
    is_confirmed_real: bool
    is_internal_only: bool
    swe_bench_score: float | None
    capabilities: list[str]
    notes: str
    source: str  # "openrouter_api" | "confirmed_real_hardcoded" | "internal_only"
    ingested_at: str  # ISO 8601

    def to_rag_text(self) -> str:
        """Generate the text that will be embedded and stored in RAG."""
        price_str = "FREE" if self.is_free else f"${self.pricing_prompt * 1_000_000:.2f}/${self.pricing_completion * 1_000_000:.2f} per MTok in/out"
        ctx_str = f"{self.context_length // 1000}K" if self.context_length else "unknown"

        capabilities_str = ", ".join(self.capabilities) if self.capabilities else "general"

        status = "CONFIRMED REAL"
        if self.is_internal_only:
            status = "INTERNAL/PROPRIETARY (not on public API)"
        elif not self.is_confirmed_real:
            status = "UNVERIFIED"

        bench_str = f" | SWE-Bench: {self.swe_bench_score}%" if self.swe_bench_score else ""

        return (
            f"AI Model: {self.name} | ID: {self.model_id}\n"
            f"Provider: {self.provider} | Status: {status}\n"
            f"Context: {ctx_str} | Pricing: {price_str}{bench_str}\n"
            f"Multimodal: {'Yes' if self.is_multimodal else 'No'} | "
            f"Capabilities: {capabilities_str}\n"
            f"Notes: {self.notes}\n"
            f"Source: {self.source} | Ingested: {self.ingested_at}"
        )

    def to_rag_metadata(self) -> dict[str, Any]:
        """Metadata dict for RAG retrieval filtering."""
        return {
            "model_id": self.model_id,
            "provider": self.provider,
            "context_length": self.context_length,
            "is_free": self.is_free,
            "is_multimodal": self.is_multimodal,
            "is_confirmed_real": self.is_confirmed_real,
            "is_internal_only": self.is_internal_only,
            "swe_bench_score": self.swe_bench_score,
            "capabilities": self.capabilities,
            "ingested_at": self.ingested_at,
            "document_type": "model_intelligence",
        }


# ─── Core functions ───────────────────────────────────────────────────────────

def _infer_capabilities(model: dict[str, Any]) -> list[str]:
    """Infer capability tags from model metadata."""
    caps: list[str] = []
    model_id = model.get("id", "").lower()
    name = model.get("name", "").lower()
    ctx = model.get("context_length", 0) or 0

    # Context tiers
    if ctx >= 900_000:
        caps.append("1M_context")
    elif ctx >= 200_000:
        caps.append("200K_context")
    elif ctx >= 100_000:
        caps.append("100K_context")

    # Modality
    arch = model.get("architecture", {})
    if arch.get("modality", "") in ("image+text", "multimodal"):
        caps.append("multimodal")
    if "vision" in name or "vision" in model_id:
        caps.append("vision")

    # Pricing
    pricing = model.get("pricing", {})
    try:
        if float(pricing.get("prompt", "1") or "1") == 0.0:
            caps.append("free")
    except (ValueError, TypeError):
        pass

    # Coding signals
    if any(kw in model_id for kw in ("coder", "code", "deepseek-coder", "codex")):
        caps.append("coding")

    # Reasoning/thinking
    if any(kw in model_id for kw in ("thinking", "reason", "r1", "o1", "o3", "o4")):
        caps.append("extended_thinking")

    # Provider signals
    if "anthropic" in model_id or "claude" in model_id:
        caps.append("anthropic")
    if "google" in model_id or "gemini" in model_id:
        caps.append("google")
    if "openai" in model_id or "gpt" in model_id:
        caps.append("openai")
    if "moonshot" in model_id or "kimi" in model_id:
        caps.append("moonshot_ai")
    if "minimax" in model_id:
        caps.append("minimax")
    if "glm" in model_id or "z-ai" in model_id or "zhipu" in model_id:
        caps.append("zhipu_ai")

    return caps


def openrouter_model_to_document(model: dict[str, Any], ingested_at: str) -> ModelDocument:
    """Convert an OpenRouter API model dict to a ModelDocument."""
    model_id = model.get("id", "")
    pricing = model.get("pricing", {})

    try:
        price_prompt = float(pricing.get("prompt", "0") or "0")
    except (ValueError, TypeError):
        price_prompt = 0.0

    try:
        price_completion = float(pricing.get("completion", "0") or "0")
    except (ValueError, TypeError):
        price_completion = 0.0

    is_free = price_prompt == 0.0
    is_confirmed = model_id in CONFIRMED_REAL_MODELS
    is_internal = model_id in INTERNAL_ONLY_MODELS

    # Merge with hardcoded confirmed data if available
    confirmed_data = CONFIRMED_REAL_MODELS.get(model_id, {})
    is_multimodal = confirmed_data.get("multimodal", False)
    swe_bench = confirmed_data.get("swe_bench")

    # Check multimodal from architecture
    arch = model.get("architecture", {})
    if arch.get("modality", "") not in ("text", ""):
        is_multimodal = True

    capabilities = _infer_capabilities(model)

    return ModelDocument(
        model_id=model_id,
        name=model.get("name", model_id),
        provider=model.get("top_provider", {}).get("context_length", None)
               and model_id.split("/")[0] or model_id.split("/")[0],
        context_length=model.get("context_length", 0) or 0,
        pricing_prompt=price_prompt,
        pricing_completion=price_completion,
        is_free=is_free,
        is_multimodal=is_multimodal,
        is_confirmed_real=is_confirmed,
        is_internal_only=is_internal,
        swe_bench_score=swe_bench,
        capabilities=capabilities,
        notes=confirmed_data.get("notes", ""),
        source="openrouter_api",
        ingested_at=ingested_at,
    )


def hardcoded_model_to_document(model_id: str, data: dict[str, Any], ingested_at: str) -> ModelDocument:
    """Build a ModelDocument from the hardcoded CONFIRMED_REAL_MODELS dict."""
    capabilities = _infer_capabilities({"id": model_id, "name": data.get("name", model_id)})
    if data.get("multimodal"):
        if "multimodal" not in capabilities:
            capabilities.append("multimodal")
    if data.get("context_length", 0) >= 900_000:
        if "1M_context" not in capabilities:
            capabilities.append("1M_context")

    return ModelDocument(
        model_id=model_id,
        name=data.get("name", model_id),
        provider=data.get("provider", model_id.split("/")[0]),
        context_length=data.get("context_length", 0),
        pricing_prompt=data.get("pricing_prompt", 0.0),
        pricing_completion=data.get("pricing_completion", 0.0),
        is_free=data.get("pricing_prompt", 1.0) == 0.0,
        is_multimodal=data.get("multimodal", False),
        is_confirmed_real=True,
        is_internal_only=False,
        swe_bench_score=data.get("swe_bench"),
        capabilities=capabilities,
        notes=data.get("notes", ""),
        source="confirmed_real_hardcoded",
        ingested_at=ingested_at,
    )


def fetch_from_openrouter() -> list[dict[str, Any]]:
    """Fetch live model list from OpenRouter API. Returns list of model dicts."""
    logger.info("Fetching model list from OpenRouter API...")
    try:
        with urlopen(OPENROUTER_API_URL, timeout=30) as response:
            data = json.loads(response.read().decode())
        models = data.get("data", [])
        logger.info("Fetched %d models from OpenRouter", len(models))
        return models
    except URLError as e:
        logger.error("Failed to fetch from OpenRouter: %s", e)
        raise


def load_from_snapshot(snapshot_path: Path) -> list[dict[str, Any]]:
    """Load model list from a JSON snapshot file."""
    logger.info("Loading models from snapshot: %s", snapshot_path)
    with snapshot_path.open() as f:
        data = json.load(f)
    models = data.get("models", [])
    logger.info("Loaded %d models from snapshot", len(models))
    return models


def build_documents(
    models: list[dict[str, Any]],
    ingested_at: str,
    include_confirmed_hardcoded: bool = True,
) -> list[ModelDocument]:
    """
    Convert raw model dicts to ModelDocument list.
    Also appends hardcoded CONFIRMED_REAL_MODELS that may not be on OpenRouter.
    """
    docs: list[ModelDocument] = []
    seen_ids: set[str] = set()

    for model in models:
        try:
            doc = openrouter_model_to_document(model, ingested_at)
            docs.append(doc)
            seen_ids.add(doc.model_id)
        except Exception as e:
            logger.warning("Failed to convert model %s: %s", model.get("id", "?"), e)

    # Add hardcoded confirmed models not present in OpenRouter snapshot
    if include_confirmed_hardcoded:
        for model_id, data in CONFIRMED_REAL_MODELS.items():
            if model_id not in seen_ids:
                doc = hardcoded_model_to_document(model_id, data, ingested_at)
                docs.append(doc)
                logger.debug("Added hardcoded confirmed model: %s", model_id)

    logger.info("Built %d model documents total", len(docs))
    return docs


def ingest_to_rag(documents: list[ModelDocument], dry_run: bool = False) -> int:
    """
    Ingest model documents into the XNAi RAG system.

    NOTE: This is a stub that shows the integration pattern.
    Full implementation requires the RAG ingestion pipeline to be running.

    In production, this would call:
        from app.XNAi_rag_app.ingest_library import ingest_document
        ingest_document(text=doc.to_rag_text(), metadata=doc.to_rag_metadata())

    Returns the count of documents ingested (or would-be ingested in dry-run).
    """
    if dry_run:
        logger.info("[DRY RUN] Would ingest %d model documents into RAG", len(documents))
        for doc in documents[:5]:  # Show first 5 as preview
            print("\n" + "─" * 60)
            print(doc.to_rag_text())
        if len(documents) > 5:
            print(f"\n... and {len(documents) - 5} more documents")
        return len(documents)

    # Real ingestion would happen here
    # Try to import the RAG ingestion module
    ingested = 0
    try:
        from app.XNAi_rag_app.ingest_library import ingest_text_document  # type: ignore[import]
        for doc in documents:
            try:
                ingest_text_document(
                    text=doc.to_rag_text(),
                    metadata=doc.to_rag_metadata(),
                    doc_id=f"model_intelligence:{doc.model_id}",
                )
                ingested += 1
            except Exception as e:
                logger.warning("Failed to ingest %s: %s", doc.model_id, e)
    except ImportError:
        # RAG pipeline not available in current environment — write to JSONL fallback
        logger.warning(
            "RAG ingest_library not available. Writing to JSONL fallback."
        )
        fallback_path = Path("expert-knowledge/model-snapshots/rag-ready-models.jsonl")
        fallback_path.parent.mkdir(parents=True, exist_ok=True)
        with fallback_path.open("w") as f:
            for doc in documents:
                json.dump(
                    {"text": doc.to_rag_text(), "metadata": doc.to_rag_metadata()},
                    f,
                )
                f.write("\n")
                ingested += 1
        logger.info("Wrote %d documents to JSONL fallback: %s", ingested, fallback_path)

    return ingested


def generate_summary_report(documents: list[ModelDocument]) -> str:
    """Generate a human-readable summary of ingested model data."""
    total = len(documents)
    free_models = [d for d in documents if d.is_free]
    confirmed = [d for d in documents if d.is_confirmed_real]
    with_1m_ctx = [d for d in documents if d.context_length >= 900_000]
    multimodal = [d for d in documents if d.is_multimodal]

    lines = [
        "# Model Intelligence Ingestion Report",
        f"**Generated**: {datetime.now(UTC).isoformat()}",
        f"**Total models**: {total}",
        f"**Free models**: {len(free_models)}",
        f"**Confirmed real**: {len(confirmed)}",
        f"**1M+ context**: {len(with_1m_ctx)}",
        f"**Multimodal**: {len(multimodal)}",
        "",
        "## Free Models (Top 20)",
        "| Model ID | Context | Provider |",
        "|----------|---------|----------|",
    ]
    for doc in sorted(free_models, key=lambda d: d.model_id)[:20]:
        ctx_str = f"{doc.context_length // 1000}K" if doc.context_length else "N/A"
        lines.append(f"| `{doc.model_id}` | {ctx_str} | {doc.provider} |")

    lines += [
        "",
        "## Confirmed Real Key Models",
        "| Model ID | SWE-Bench | Context | Price (in/out per MTok) |",
        "|----------|-----------|---------|------------------------|",
    ]
    for doc in sorted(confirmed, key=lambda d: d.model_id):
        ctx_str = f"{doc.context_length // 1000}K" if doc.context_length else "N/A"
        bench = f"{doc.swe_bench_score}%" if doc.swe_bench_score else "—"
        price = (
            f"${doc.pricing_prompt * 1_000_000:.2f}/${doc.pricing_completion * 1_000_000:.2f}"
            if not doc.is_free
            else "FREE"
        )
        lines.append(f"| `{doc.model_id}` | {bench} | {ctx_str} | {price} |")

    return "\n".join(lines)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="XNAi Model Intelligence RAG Ingestion Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--ingest",
        metavar="SNAPSHOT_JSON",
        help="Ingest from a JSON snapshot file (output of update-model-intelligence.sh)",
    )
    source_group.add_argument(
        "--live",
        action="store_true",
        help="Fetch live model list from OpenRouter API and ingest",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be ingested without actually writing to RAG",
    )
    parser.add_argument(
        "--report",
        metavar="OUTPUT_MD",
        help="Write a markdown summary report to this path",
    )
    parser.add_argument(
        "--no-hardcoded",
        action="store_true",
        help="Skip adding hardcoded confirmed models not in the snapshot",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    ingested_at = datetime.now(UTC).isoformat()

    # Load models
    if args.live:
        raw_models = fetch_from_openrouter()
    else:
        snapshot_path = Path(args.ingest)
        if not snapshot_path.exists():
            logger.error("Snapshot file not found: %s", snapshot_path)
            return 1
        raw_models = load_from_snapshot(snapshot_path)

    # Build documents
    documents = build_documents(
        raw_models,
        ingested_at=ingested_at,
        include_confirmed_hardcoded=not args.no_hardcoded,
    )

    # Ingest
    count = ingest_to_rag(documents, dry_run=args.dry_run)
    logger.info(
        "%s %d model documents into RAG",
        "Would ingest" if args.dry_run else "Ingested",
        count,
    )

    # Optional report
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = generate_summary_report(documents)
        report_path.write_text(report)
        logger.info("Report written to: %s", report_path)
        if args.verbose or args.dry_run:
            print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
