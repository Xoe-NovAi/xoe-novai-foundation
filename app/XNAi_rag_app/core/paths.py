"""
Central Path Resolution Module for Omega Stack

This module serves as the single source of truth for all file paths in the system.
It dynamically resolves the OMEGA_ROOT based on its own location, ensuring
portability across different environments (local, container, cloud).
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Determine the project root relative to this file
# This file is in app/XNAi_rag_app/core/paths.py
# Root is ../../../
_CURRENT_DIR = Path(__file__).resolve().parent
OMEGA_ROOT = _CURRENT_DIR.parent.parent.parent

def get_omega_root() -> Path:
    """Return the absolute path to the project root."""
    return OMEGA_ROOT

def resolve_path(path_str: str) -> Path:
    """
    Resolve a path string to an absolute Path object.
    
    - If path is absolute, return it as is (but try to re-root if it points to a known old root).
    - If path is relative, resolve it against OMEGA_ROOT.
    - Expands user (~) and environment variables.
    """
    if not path_str:
        return OMEGA_ROOT

    # Expand ~ and vars
    expanded = os.path.expanduser(os.path.expandvars(path_str))
    p = Path(expanded)

    # Handle absolute paths that might be hardcoded from other environments
    # e.g., /home/arcana-novai/... -> $OMEGA_ROOT/...
    if p.is_absolute():
        # Heuristic: If it contains 'omega-stack' or 'xnai-foundation', try to re-base it
        parts = p.parts
        if 'omega-stack' in parts:
            idx = parts.index('omega-stack')
            rel_parts = parts[idx+1:]
            return OMEGA_ROOT.joinpath(*rel_parts)
        elif 'xnai-foundation' in parts:
            idx = parts.index('xnai-foundation')
            rel_parts = parts[idx+1:]
            return OMEGA_ROOT.joinpath(*rel_parts)
        return p

    return OMEGA_ROOT / p

def get_config_path(filename: str) -> Path:
    """Get path for a config file."""
    return resolve_path(f"config/{filename}")

def get_script_path(script_name: str) -> Path:
    """Get path for a script."""
    return resolve_path(f"scripts/{script_name}")

def get_expert_config_path(domain: str) -> Path:
    """Get path for an expert configuration."""
    return resolve_path(f"expert-knowledge/{domain}-expert.yaml")

# Common directories
CONFIG_DIR = resolve_path("config")
SCRIPTS_DIR = resolve_path("scripts")
LOGS_DIR = resolve_path("logs")
DATA_DIR = resolve_path("data")
MEMORY_BANK_DIR = resolve_path("memory_bank")
MCP_SERVERS_DIR = resolve_path("mcp-servers")
ENTITIES_DIR = resolve_path("entities")

# Ensure critical directories exist
for d in [LOGS_DIR, DATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)
