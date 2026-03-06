#!/usr/bin/env python3
"""
OpenAPI Schema Export Script

Generates OpenAPI JSON schemas from FastAPI applications for documentation.
Run from project root: python scripts/generate_openapi.py
"""

import json
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


def export_openapi_schemas():
    """Export OpenAPI schemas from FastAPI applications."""

    output_dir = Path(__file__).parent.parent / "docs" / "api" / "schemas"
    output_dir.mkdir(parents=True, exist_ok=True)

    schemas_exported = []

    # Try to import and export from entrypoint.py (main API)
    try:
        from XNAi_rag_app.api.entrypoint import app as main_app

        openapi_main = main_app.openapi()

        # Remove server URLs for cleaner output
        if "servers" in openapi_main:
            del openapi_main["servers"]

        output_file = output_dir / "main_api.json"
        with open(output_file, "w") as f:
            json.dump(openapi_main, f, indent=2)

        schemas_exported.append(
            {
                "name": "Main API (entrypoint.py)",
                "file": "main_api.json",
                "endpoints": len(openapi_main.get("paths", {})),
            }
        )
        print(f"✓ Exported Main API: {len(openapi_main.get('paths', {}))} endpoints")

    except ImportError as e:
        print(f"⚠ Could not import main app: {e}")
    except Exception as e:
        print(f"⚠ Error exporting main app: {e}")

    # Try to import and export from semantic_search.py
    try:
        from XNAi_rag_app.api.semantic_search import app as semantic_app

        openapi_semantic = semantic_app.openapi()

        if "servers" in openapi_semantic:
            del openapi_semantic["servers"]

        output_file = output_dir / "semantic_search.json"
        with open(output_file, "w") as f:
            json.dump(openapi_semantic, f, indent=2)

        schemas_exported.append(
            {
                "name": "Semantic Search API",
                "file": "semantic_search.json",
                "endpoints": len(openapi_semantic.get("paths", {})),
            }
        )
        print(
            f"✓ Exported Semantic Search API: {len(openapi_semantic.get('paths', {}))} endpoints"
        )

    except ImportError as e:
        print(f"⚠ Could not import semantic search app: {e}")
    except Exception as e:
        print(f"⚠ Error exporting semantic search app: {e}")

    # Generate summary
    print("\n" + "=" * 50)
    print("OpenAPI Schema Export Summary")
    print("=" * 50)

    if schemas_exported:
        for schema in schemas_exported:
            print(
                f"  • {schema['name']}: {schema['endpoints']} endpoints -> {schema['file']}"
            )
        print(f"\n  Total: {len(schemas_exported)} APIs exported")
        print(f"  Output directory: {output_dir}")
    else:
        print("  ⚠ No schemas exported. Check import errors above.")

    return schemas_exported


if __name__ == "__main__":
    export_openapi_schemas()
