#!/usr/bin/env python3
"""
XNAi Metropolis CLI
===================
Universal CLI interface for the Persistent Expert Metropolis.
Allows users and agents to summon, compare, and manage experts.

Usage:
  python3 scripts/metropolis.py summon "Kurt Cobain" "What is grunge?"
  python3 scripts/metropolis.py list
  python3 scripts/metropolis.py compare "Plato" "Socrates" "virtue"
"""

import sys
import os
import asyncio
import argparse
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "app"))

try:
    from XNAi_rag_app.core.entities.tools import summon_expert, get_available_experts, compare_experts
except ImportError as e:
    print(f"Error: Could not import metropolis tools: {e}")
    sys.exit(1)

async def main():
    parser = argparse.ArgumentParser(description="XNAi Metropolis CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Summon
    summon_parser = subparsers.add_parser("summon", help="Summon an expert")
    summon_parser.add_argument("name", help="Name of the expert")
    summon_parser.add_argument("query", help="The query/task")

    # List
    subparsers.add_parser("list", help="List available experts")

    # Compare
    compare_parser = subparsers.add_parser("compare", help="Compare two experts")
    compare_parser.add_argument("e1", help="First expert")
    compare_parser.add_argument("e2", help="Second expert")
    compare_parser.add_argument("topic", help="Topic to compare on")

    args = parser.parse_args()

    if args.command == "summon":
        result = await summon_expert(args.name, args.query)
        print(json.dumps(result, indent=2))
    elif args.command == "list":
        experts = await get_available_experts()
        print(json.dumps(experts, indent=2))
    elif args.command == "compare":
        result = await compare_experts(args.e1, args.e2, args.topic)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
