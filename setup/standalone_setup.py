# Standalone Setup for XNAi Speculative Research
# This script allows you to extract and install the Speculative Research system
# as a standalone package for other projects.

import os
import shutil
from setuptools import setup, find_packages

def create_standalone_pkg():
    pkg_dir = "packages/xnai-speculative-research"
    os.makedirs(f"{pkg_dir}/xnai_research", exist_ok=True)
    
    # Map of internal files to standalone package
    files_to_copy = {
        "app/XNAi_rag_app/core/embeddings/speculative_engine.py": "xnai_research/embeddings.py",
        "app/XNAi_rag_app/services/escalation_researcher.py": "xnai_research/escalation.py",
        "app/XNAi_rag_app/core/redis_streams.py": "xnai_research/streams.py",
    }
    
    for src, dst in files_to_copy.items():
        shutil.copy(src, f"{pkg_dir}/{dst}")
        
    with open(f"{pkg_dir}/xnai_research/__init__.py", "w") as f:
        f.write("from .embeddings import SpeculativeEmbeddingEngine\n")
        f.write("from .escalation import EscalationResearcher\n")

    print(f"✅ Standalone package created at {pkg_dir}")

if __name__ == "__main__":
    create_standalone_pkg()
    
    setup(
        name="xnai-speculative-research",
        version="1.0.0",
        packages=find_packages(where="packages/xnai-speculative-research"),
        package_dir={"": "packages/xnai-speculative-research"},
        install_requires=[
            "numpy",
            "redis",
            "anyio"
        ],
        description="Modular Speculative Generation and Escalation Research System",
        author="Xoe-NovAi Team",
    )
