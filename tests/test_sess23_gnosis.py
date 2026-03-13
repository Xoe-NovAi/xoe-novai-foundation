#!/usr/bin/env python3
"""
🔱 SESS-23: Gnosis System Integration Test
Tests ZLV, Resonance Auditor, TGG Anchoring, and SLM Logic.
"""

import sys
import json
import ast
import hashlib
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Mock MCP imports by adding path
sys.path.append(str(PROJECT_ROOT / "mcp-servers/xnai-gnosis"))

from app.XNAi_rag_app.core.linguistics import ZippedLogosDecoder, normalize_ancient_greek
# Import ResonanceAuditor from the server file directly
from server import ResonanceAuditor

def test_zlv_rigidity():
    print("🧪 Testing ZLV Crystal Hashing Rigidity...")
    decoder = ZippedLogosDecoder()
    
    code_v1 = "def test():\n    # This is a comment\n    print('hello world')\n"
    code_v2 = "def test():\n    print('hello world') # Same function, different format\n"
    
    hash_v1 = decoder.generate_crystal_hash(code_v1)
    hash_v2 = decoder.generate_crystal_hash(code_v2)
    
    print(f"  - Hash V1: {hash_v1}")
    print(f"  - Hash V2: {hash_v2}")
    
    assert hash_v1 == hash_v2, f"❌ Hash mismatch: {hash_v1} != {hash_v2}"
    print(f"✅ ZLV Rigidity Verified.")

def test_greek_normalization():
    print("🧪 Testing Ancient Greek Normalization...")
    text = "μῆνιν ἄειδε θεὰ Πηληϊάδεω Ἀχιλῆος"
    expected = "μηνιν αειδε θεα πηληιαδεω αχιληος"
    normalized = normalize_ancient_greek(text)
    print(f"  - Input: {text}")
    print(f"  - Output: {normalized}")
    assert normalized == expected, f"❌ Normalization mismatch: {normalized} != {expected}"
    print(f"✅ Greek Normalization Verified.")

def test_resonance_auditor():
    print("🧪 Testing Resonance Auditor (Cosine Similarity)...")
    auditor = ResonanceAuditor()
    
    # High resonance: Athena context vs Athena seed words
    context = "Implement logical structures and AST functional integrity."
    seed = "logic functional AST structure"
    
    score = auditor.cosine_similarity(
        auditor.vectorize(context),
        auditor.vectorize(seed)
    )
    print(f"  📈 Athena Resonance Score: {score:.4f}")
    assert score > 0.2, f"❌ Low resonance for aligned context: {score}"
    
    # Low resonance: Random words vs Athena seed
    noise = "The quick brown fox jumps over the lazy dog."
    score_noise = auditor.cosine_similarity(
        auditor.vectorize(noise),
        auditor.vectorize(seed)
    )
    print(f"  📉 Noise Resonance Score: {score_noise:.4f}")
    assert score_noise < 0.1, f"❌ High resonance for noise: {score_noise}"
    print("✅ Resonance Auditor Logic Verified.")

def test_tgg_anchoring_logic():
    print("🧪 Testing TGG Anchoring Data Structure...")
    decoder = ZippedLogosDecoder()
    path = "app/core/test.py"
    c_hash = "abc123hash"
    
    anchor = decoder.anchor_to_gnosis(path, c_hash)
    print(f"  📦 Anchor Result nodes: {list(anchor.keys())}")
    
    assert anchor["path"] == path
    assert anchor["hash"] == c_hash
    assert "graph" in anchor
    print("✅ TGG Anchoring Logic Verified.")

def test_slm_check():
    print("🧪 Testing SLM Check (Security Logic Matrix)...")
    decoder = ZippedLogosDecoder()
    
    safe_path = ["API", "Gnosis", "UI"]
    unsafe_path = ["API", "secrets", "UI"] # Missing Phylax
    hardened_path = ["API", "secrets", "Phylax", "UI"]
    
    print(f"  - Safe Path: {decoder.SLM_check(safe_path)}")
    print(f"  - Unsafe Path: {decoder.SLM_check(unsafe_path)}")
    print(f"  - Hardened Path: {decoder.SLM_check(hardened_path)}")
    
    assert decoder.SLM_check(safe_path) == True
    assert decoder.SLM_check(unsafe_path) == False, "❌ SLM failed to block unsafe path"
    assert decoder.SLM_check(hardened_path) == True
    print("✅ SLM Security Logic Verified.")

if __name__ == "__main__":
    print("🔱 INITIATING GNOSIS SYSTEM VERIFICATION\n")
    try:
        test_zlv_rigidity()
        test_greek_normalization()
        test_resonance_auditor()
        test_tgg_anchoring_logic()
        test_slm_check()
        print("\n🏆 ALL SESS-23 INTEGRATION TESTS PASSED.")
    except Exception as e:
        print(f"\n💥 TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
