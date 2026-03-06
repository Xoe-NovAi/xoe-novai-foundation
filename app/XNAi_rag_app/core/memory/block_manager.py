"""
Block Manager
=============

Manages memory block reading, validation, and size checking.
Implements the block manifest from BLOCKS.yaml.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import re


class BlockManager:
    """Manages memory bank blocks with size validation."""

    def __init__(self, memory_bank_path: Optional[str] = None):
        if memory_bank_path is None:
            memory_bank_path = os.environ.get(
                "MEMORY_BANK_PATH",
                str(
                    Path(__file__).parent.parent.parent.parent.parent.parent
                    / "memory_bank"
                ),
            )
        self.memory_bank_path = Path(memory_bank_path)
        self.blocks_yaml_path = self.memory_bank_path / "BLOCKS.yaml"
        self._config: Optional[Dict[str, Any]] = None

    def load_config(self) -> Dict[str, Any]:
        """Load BLOCKS.yaml configuration."""
        if self._config is None:
            with open(self.blocks_yaml_path, "r") as f:
                self._config = yaml.safe_load(f)
        return self._config

    def get_block_config(self, label: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific block by label."""
        config = self.load_config()

        for section in ["core_blocks", "operational_blocks", "progress_blocks"]:
            if section in config:
                for block_name, block_config in config[section].items():
                    if block_config.get("label") == label:
                        return block_config

        return None

    def get_block_path(self, label: str) -> Optional[Path]:
        """Get the file path for a block by label."""
        block_config = self.get_block_config(label)
        if block_config and "file" in block_config:
            return self.memory_bank_path / block_config["file"]
        return None

    async def read_block(self, label: str) -> str:
        """Read block content by label."""
        path = self.get_block_path(label)
        if path is None:
            raise ValueError(f"Block not found: {label}")

        if not path.exists():
            raise FileNotFoundError(f"Block file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    async def write_block(self, label: str, content: str) -> bool:
        """Write content to a block, respecting size limits."""
        block_config = self.get_block_config(label)
        if block_config is None:
            raise ValueError(f"Block not found: {label}")

        limit = block_config.get("limit_chars", 10000)

        if len(content) > limit:
            raise ValueError(f"Content exceeds limit: {len(content)} > {limit} chars")

        path = self.get_block_path(label)
        if path is None:
            raise ValueError(f"Block path not found: {label}")

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return True

    async def validate_block(self, label: str) -> Dict[str, Any]:
        """Validate a block against its limits."""
        block_config = self.get_block_config(label)
        if block_config is None:
            return {"valid": False, "error": f"Block not found: {label}"}

        path = self.get_block_path(label)
        if path is None or not path.exists():
            return {"valid": False, "error": f"Block file not found: {label}"}

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        chars = len(content)
        limit = block_config.get("limit_chars", 10000)
        utilization = chars / limit if limit > 0 else 0.0

        return {
            "label": label,
            "file": str(path.relative_to(self.memory_bank_path)),
            "chars": chars,
            "limit": limit,
            "utilization": utilization,
            "valid": chars <= limit,
            "warning": utilization > 0.8,
        }

    async def get_all_block_status(self) -> Dict[str, Any]:
        """Get status for all defined blocks."""
        config = self.load_config()
        blocks = []
        warnings = []

        for section in ["core_blocks", "operational_blocks", "progress_blocks"]:
            if section not in config:
                continue

            for block_name, block_config in config[section].items():
                label = block_config.get("label", block_name)
                status = await self.validate_block(label)
                blocks.append(status)

                if status.get("warning"):
                    warnings.append(f"{label}: {status['utilization']:.1%} utilized")

        total_utilization = (
            sum(b["utilization"] for b in blocks) / len(blocks) if blocks else 0
        )

        return {
            "blocks": blocks,
            "total_utilization": total_utilization,
            "warnings": warnings,
        }

    def extract_frontmatter(self, content: str) -> tuple[str, str]:
        """Extract YAML frontmatter and body from content."""
        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(pattern, content, re.DOTALL)

        if match:
            return match.group(1), match.group(2)

        return "", content

    def reconstruct_with_frontmatter(self, frontmatter: str, body: str) -> str:
        """Reconstruct content with frontmatter preserved."""
        if frontmatter:
            return f"---\n{frontmatter}\n---\n{body}"
        return body
