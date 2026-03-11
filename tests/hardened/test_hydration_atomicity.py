import os
import pytest
from pathlib import Path

# Path to the root of the project
PROJECT_ROOT = Path(__file__).parent.parent.parent

def test_hydration_consistency():
    """Verify that a hydration beat correctly synchronizes the core Memory Bank files."""
    mb_dir = PROJECT_ROOT / "memory_bank"
    
    index_path = mb_dir / "INDEX.md"
    active_path = mb_dir / "activeContext.md"
    progress_path = mb_dir / "progress.md"
    
    assert index_path.exists(), "INDEX.md is missing"
    assert active_path.exists(), "activeContext.md is missing"
    assert progress_path.exists(), "progress.md is missing"
    
    # Read files
    index_content = index_path.read_text()
    active_content = active_path.read_text()
    progress_content = progress_path.read_text()
    
    # Find the most recent coordination key (METROPOLIS-XXX-YYYYMMDD)
    import re
    key_pattern = r"METROPOLIS-[A-Z]+-\d{8}"
    
    active_keys = re.findall(key_pattern, active_content)
    assert active_keys, "No coordination key found in activeContext.md"
    
    latest_key = active_keys[0]
    
    # Verify consistency across all three
    assert latest_key in index_content, f"Key {latest_key} missing from INDEX.md"
    assert latest_key in progress_content, f"Key {latest_key} missing from progress.md"
    
    print(f"✅ Hydration Consistency Verified. Latest Key: {latest_key}")

if __name__ == "__main__":
    test_hydration_consistency()
