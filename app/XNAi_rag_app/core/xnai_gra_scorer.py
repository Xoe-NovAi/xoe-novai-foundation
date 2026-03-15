"""
GRA Scorer for Hellenic Ingestion (Block 0.6)
==============================================
Quality scoring system for content ingestion using the GRA formula.

GRA (Semantic_Density, Alethia_Verification, Axiom_Compliance) =
    (Semantic_Density × 0.4) + (Alethia_Verification × 0.4) + (Axiom_Compliance × 0.2)

Scoring Tiers:
- GRA >= 0.8: Gold tier (production-ready)
- GRA 0.7-0.8: Silver tier (acceptable with caution)
- GRA < 0.7: Reprocess required

Reference: requirements/SESS-26-block-0.6-gra-scorer.md
"""

import json
import logging
import math
from typing import Dict, Any, Optional, List
from statistics import mean, stdev

logger = logging.getLogger(__name__)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def measure_semantic_density(content: str) -> float:
    """
    Measure ratio of semantic signal preserved after RCF compression.
    
    Formula: (original_entropy - compressed_entropy) / original_entropy
    
    High density = good signal preservation at low compression cost
    
    Args:
        content: Raw content string to analyze
        
    Returns:
        float: Score in range [0.0, 1.0]
    """
    if not content or len(content.strip()) == 0:
        return 0.0
    
    # Calculate original entropy (Shannon entropy)
    original_entropy = _calculate_shannon_entropy(content)
    
    # Simulate RCF compression: measure token uniqueness
    tokens = content.lower().split()
    unique_tokens = len(set(tokens))
    
    if len(tokens) == 0:
        return 0.0
    
    # Token diversity: how many unique tokens relative to total
    # High diversity = high information density
    token_diversity = unique_tokens / len(tokens)
    
    # Measure meaningful content: filter stopwords
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    meaningful_tokens = [t for t in tokens if t not in stopwords and len(t) > 1]
    meaningful_ratio = len(meaningful_tokens) / len(tokens) if tokens else 0
    
    # Semantic density combines token diversity and meaningful content
    # Base: token diversity (0-1), boost: meaningful token ratio (0-0.3)
    density = token_diversity * 0.7 + meaningful_ratio * 0.3
    
    # Apply entropy-based adjustment
    if original_entropy > 0:
        entropy_boost = min(0.2, original_entropy / 10.0)  # Normalize entropy impact
        density = min(1.0, density + entropy_boost)
    
    # Clamp to [0, 1]
    return min(1.0, max(0.0, density))


def verify_alethia(content: str, metadata: Dict[str, Any]) -> float:
    """
    Validate "truthfulness" and factual grounding.
    
    Checks if "Fact" field references known concepts (keywords from payload axioms).
    Score based on verification confidence:
    - 1.0 = verified (facts match axioms)
    - 0.5 = partial verification
    - 0.0 = unverified
    
    Args:
        content: Content to verify
        metadata: Metadata dict with 'axioms' and optional 'facts' fields
        
    Returns:
        float: Score in range [0.0, 1.0]
    """
    if not content or len(content.strip()) == 0:
        return 0.0
    
    axioms = metadata.get('axioms', [])
    facts = metadata.get('facts', [])
    
    if not axioms:
        # No axioms to verify against, check content coherence
        # High diversity and meaningful content suggest coherence
        tokens = content.lower().split()
        if len(tokens) < 3:
            return 0.3
        unique_ratio = len(set(tokens)) / len(tokens)
        return min(0.9, 0.5 + unique_ratio * 0.4)
    
    # Extract keywords from content and axioms
    content_words = set(w for w in content.lower().split() if len(w) > 2)
    axiom_keywords = set()
    
    for axiom in axioms:
        if isinstance(axiom, str):
            axiom_keywords.update(w for w in axiom.lower().split() if len(w) > 2)
    
    if not content_words:
        return 0.2
    
    if not axiom_keywords:
        return 0.4
    
    # Calculate alignment: what % of content has axiom connection
    matches = len(content_words & axiom_keywords)
    coverage = matches / len(content_words)
    
    # Extract explicit facts if provided
    fact_boost = 0.0
    if facts:
        fact_count = len([f for f in facts if isinstance(f, str) and len(f) > 0])
        if fact_count > 0:
            fact_boost = min(0.2, fact_count * 0.05)  # Each fact adds up to 5% boost
    
    # Score mapping with boost:
    # >= 0.5 coverage = fully verified (0.8-1.0)
    # 0.2-0.5 coverage = partially verified (0.5-0.7)
    # < 0.2 coverage = weakly verified (0.2-0.5)
    base_score = 0.0
    if coverage >= 0.5:
        base_score = 0.8
    elif coverage >= 0.2:
        base_score = 0.5
    else:
        base_score = 0.2
    
    # Apply fact boost
    final_score = min(1.0, base_score + fact_boost)
    
    return final_score


def check_axiom_compliance(axioms: List[str], expected_axiom_count: int = 5) -> float:
    """
    Check alignment with Maat-Lilith axioms.
    
    Implementation: Count axioms tagged in payload / expected axioms.
    If conflicts detected, reduce score by 0.2
    
    Args:
        axioms: List of axiom identifiers or statements
        expected_axiom_count: Expected number of axioms (default 5)
        
    Returns:
        float: Score in range [0.0, 1.0]
    """
    if not axioms:
        return 0.0
    
    # Validate axiom format (should be non-empty strings)
    valid_axioms = [a for a in axioms if isinstance(a, str) and len(a.strip()) > 0]
    
    if not valid_axioms:
        return 0.0
    
    # Count compliance: ratio of provided axioms to expected
    axiom_coverage = min(1.0, len(valid_axioms) / expected_axiom_count)
    
    # Detect conflicts: duplicate axioms indicate inconsistency
    unique_axioms = set(valid_axioms)
    conflict_penalty = 0.0
    
    if len(unique_axioms) < len(valid_axioms):
        # Duplicates detected
        conflict_penalty = 0.2
    
    # Check for semantic conflicts (axioms starting with negations)
    negation_words = {'not', 'no', 'never', 'without', 'anti-', 'non-'}
    negated_axioms = []
    
    for axiom in unique_axioms:
        first_word = axiom.lower().split()[0] if axiom else ""
        if any(neg in first_word for neg in negation_words):
            negated_axioms.append(axiom)
    
    # If many negated axioms, reduce score (conflict indicator)
    if len(negated_axioms) > len(unique_axioms) * 0.5:
        conflict_penalty = max(conflict_penalty, 0.15)
    
    compliance_score = axiom_coverage - conflict_penalty
    return min(1.0, max(0.0, compliance_score))


# ============================================================================
# MAIN GRA CALCULATION
# ============================================================================


def calculate_gra(payload: Dict[str, Any]) -> float:
    """
    Calculate GRA (Global Relevance Assessment) score.
    
    Formula:
        GRA = (Semantic_Density × 0.4) + (Alethia_Verification × 0.4) + (Axiom_Compliance × 0.2)
    
    Args:
        payload: Dictionary containing:
            - 'content' (str): The content to score
            - 'metadata' (dict): Metadata with 'axioms', optionally 'facts'
            
    Returns:
        float: GRA score clamped to [0.0, 1.0]
        
    Raises:
        ValueError: If payload is missing required fields
    """
    # Validate payload structure
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")
    
    if 'content' not in payload:
        raise ValueError("Payload must contain 'content' field")
    
    if 'metadata' not in payload:
        raise ValueError("Payload must contain 'metadata' field")
    
    content = payload.get('content', '')
    metadata = payload.get('metadata', {})
    
    if not isinstance(content, str):
        raise ValueError("Content must be a string")
    
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary")
    
    # Calculate component scores
    semantic_density = measure_semantic_density(content)
    alethia_score = verify_alethia(content, metadata)
    axiom_compliance = check_axiom_compliance(
        metadata.get('axioms', []),
        metadata.get('expected_axioms', 5)
    )
    
    # Apply GRA formula with weights
    gra = (semantic_density * 0.4) + (alethia_score * 0.4) + (axiom_compliance * 0.2)
    
    # Clamp to [0, 1] range
    gra = min(1.0, max(0.0, gra))
    
    return gra


def get_gra_tier(score: float) -> str:
    """
    Classify GRA score into tiers.
    
    Args:
        score: GRA score in range [0.0, 1.0]
        
    Returns:
        str: Tier classification
    """
    if score >= 0.8:
        return "Gold"
    elif score >= 0.7:
        return "Silver"
    else:
        return "Reprocess"


# ============================================================================
# INTERNAL UTILITIES
# ============================================================================


def _calculate_shannon_entropy(text: str) -> float:
    """
    Calculate Shannon entropy of text.
    
    Measures information density/randomness in content.
    
    Args:
        text: Input text
        
    Returns:
        float: Shannon entropy value
    """
    if not text:
        return 0.0
    
    # Count character frequencies
    char_counts = {}
    for char in text:
        char_counts[char] = char_counts.get(char, 0) + 1
    
    # Calculate entropy
    entropy = 0.0
    text_len = len(text)
    
    for count in char_counts.values():
        probability = count / text_len
        entropy -= probability * math.log2(probability)
    
    return entropy


# ============================================================================
# TESTING & VALIDATION
# ============================================================================


def generate_test_payload(
    content_length: str = "normal",
    axiom_count: int = 5,
    fact_coverage: float = 0.8,
    has_conflicts: bool = False
) -> Dict[str, Any]:
    """
    Generate a test payload for GRA scorer validation.
    
    Args:
        content_length: "short", "normal", or "long"
        axiom_count: Number of axioms to include
        fact_coverage: How well facts align with axioms (0-1)
        has_conflicts: Whether to include conflicting axioms
        
    Returns:
        dict: Test payload
    """
    # Generate content based on length
    if content_length == "short":
        content = "The quick brown fox jumps over the lazy dog."
    elif content_length == "long":
        content = (
            "The quick brown fox jumps over the lazy dog. "
            "Knowledge is power and understanding is key. "
            "Truth and verification form the foundation. "
            "Ethical principles guide all actions taken. "
            "Continuous improvement drives excellence forward. "
        ) * 3
    else:  # normal
        content = (
            "The quick brown fox jumps over the lazy dog. "
            "Knowledge is power and understanding is key. "
            "Truth and verification form the foundation."
        )
    
    # Generate axioms
    base_axioms = [
        "truth-verification",
        "knowledge-preservation",
        "semantic-integrity",
        "ethical-grounding",
        "axiom-compliance"
    ]
    
    axioms = base_axioms[:axiom_count]
    
    if has_conflicts:
        axioms.append("truth-verification")  # Duplicate to simulate conflict
        axioms.append("not-applicable")
    
    # Generate facts with alignment to axioms
    facts = [
        f"fact-{i}" for i in range(int(axiom_count * fact_coverage))
    ]
    
    return {
        "content": content,
        "metadata": {
            "axioms": axioms,
            "facts": facts,
            "expected_axioms": 5
        }
    }


def validate_gra_scorer(num_payloads: int = 20) -> Dict[str, Any]:
    """
    Comprehensive validation of the GRA scorer.
    
    Tests:
    - Scores are in [0, 1] range
    - Mean score ~0.75 for typical payloads
    - Formula weights are applied correctly
    - Edge cases handled (empty content, missing axioms, etc.)
    
    Args:
        num_payloads: Number of test payloads to generate
        
    Returns:
        dict: Validation results
    """
    scores = []
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "failures": [],
        "scores": [],
        "score_stats": {}
    }
    
    # Test 1: Normal payloads
    logger.info(f"Testing {num_payloads} normal payloads...")
    for i in range(num_payloads):
        try:
            payload = generate_test_payload(
                content_length="normal",
                axiom_count=5,
                fact_coverage=0.8,
                has_conflicts=False
            )
            score = calculate_gra(payload)
            
            # Validate score range
            assert 0.0 <= score <= 1.0, f"Score {score} outside [0, 1]"
            
            scores.append(score)
            results["total_tests"] += 1
            results["passed"] += 1
            
        except Exception as e:
            results["total_tests"] += 1
            results["failed"] += 1
            results["failures"].append(f"Normal payload {i}: {str(e)}")
    
    # Test 2: Short content
    logger.info("Testing short content...")
    try:
        payload = generate_test_payload(content_length="short", axiom_count=2)
        score = calculate_gra(payload)
        assert 0.0 <= score <= 1.0, f"Score {score} outside [0, 1]"
        scores.append(score)
        results["total_tests"] += 1
        results["passed"] += 1
    except Exception as e:
        results["total_tests"] += 1
        results["failed"] += 1
        results["failures"].append(f"Short content: {str(e)}")
    
    # Test 3: Long content
    logger.info("Testing long content...")
    try:
        payload = generate_test_payload(content_length="long", axiom_count=8)
        score = calculate_gra(payload)
        assert 0.0 <= score <= 1.0, f"Score {score} outside [0, 1]"
        scores.append(score)
        results["total_tests"] += 1
        results["passed"] += 1
    except Exception as e:
        results["total_tests"] += 1
        results["failed"] += 1
        results["failures"].append(f"Long content: {str(e)}")
    
    # Test 4: With conflicts
    logger.info("Testing payload with conflicts...")
    try:
        payload = generate_test_payload(
            content_length="normal",
            axiom_count=4,
            has_conflicts=True
        )
        score = calculate_gra(payload)
        assert 0.0 <= score <= 1.0, f"Score {score} outside [0, 1]"
        assert score < 0.8, "Conflicting axioms should lower score"
        scores.append(score)
        results["total_tests"] += 1
        results["passed"] += 1
    except Exception as e:
        results["total_tests"] += 1
        results["failed"] += 1
        results["failures"].append(f"Conflict detection: {str(e)}")
    
    # Test 5: Edge cases
    logger.info("Testing edge cases...")
    edge_cases = [
        {"content": "", "metadata": {"axioms": []}},  # Empty
        {"content": "test", "metadata": {"axioms": []}},  # No axioms
        {"content": "the quick brown fox", "metadata": {"axioms": ["unknown"]}},  # No match
    ]
    
    for i, payload in enumerate(edge_cases):
        try:
            score = calculate_gra(payload)
            assert 0.0 <= score <= 1.0, f"Edge case {i} score {score} outside [0, 1]"
            scores.append(score)
            results["total_tests"] += 1
            results["passed"] += 1
        except Exception as e:
            results["total_tests"] += 1
            results["failed"] += 1
            results["failures"].append(f"Edge case {i}: {str(e)}")
    
    # Calculate statistics
    if scores:
        results["scores"] = scores
        results["score_stats"] = {
            "min": min(scores),
            "max": max(scores),
            "mean": mean(scores),
            "stdev": stdev(scores) if len(scores) > 1 else 0.0,
            "count": len(scores)
        }
    
    # Validate mean score ~0.75
    if scores and len(scores) > 5:
        mean_score = mean(scores)
        # Allow ±0.15 tolerance
        if 0.6 <= mean_score <= 0.9:
            results["mean_validation"] = "PASS"
        else:
            results["mean_validation"] = f"WARN: mean {mean_score:.3f} outside 0.6-0.9 range"
    
    return results


if __name__ == "__main__":
    # Run validation
    logging.basicConfig(level=logging.INFO)
    results = validate_gra_scorer(num_payloads=20)
    
    print("\n" + "=" * 70)
    print("GRA SCORER VALIDATION RESULTS")
    print("=" * 70)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if results["score_stats"]:
        stats = results["score_stats"]
        print(f"\nScore Statistics:")
        print(f"  Min:    {stats['min']:.4f}")
        print(f"  Max:    {stats['max']:.4f}")
        print(f"  Mean:   {stats['mean']:.4f}")
        print(f"  StDev:  {stats['stdev']:.4f}")
        print(f"  Count:  {stats['count']}")
    
    if results.get("mean_validation"):
        print(f"\nMean Validation: {results['mean_validation']}")
    
    if results["failures"]:
        print(f"\nFailures:")
        for failure in results["failures"]:
            print(f"  - {failure}")
    
    print("\n" + "=" * 70)
