"""
Knowledge Distillation Nodes - Distill Node
===========================================

Content distillation node for LangGraph.

v2.0: LLM-powered summarization and insight extraction via get_llm_complete.
      Regex methods retained as fallback when LLM is unavailable.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..state import KnowledgeState

logger = logging.getLogger(__name__)

# ============================================================================
# LLM-POWERED DISTILLATION (Primary)
# ============================================================================

_LLM_AVAILABLE: Optional[bool] = None


async def _check_llm_available() -> bool:
    """Check if the LLM backend is available (cached after first check)."""
    global _LLM_AVAILABLE
    if _LLM_AVAILABLE is not None:
        return _LLM_AVAILABLE

    try:
        from XNAi_rag_app.core.dependencies import get_llm_complete
        # Quick smoke test — if get_llm_complete is importable, we mark available.
        # The actual model-load error will be caught per-call with graceful fallback.
        _LLM_AVAILABLE = True
    except ImportError:
        logger.warning("Distillation: LLM backend not available, using regex fallback")
        _LLM_AVAILABLE = False

    return _LLM_AVAILABLE


async def _generate_summary_llm(content: str, temperature: float = 0.3) -> str:
    """Generate summary using local LLM (Qwen/LLaMA)."""
    from XNAi_rag_app.core.dependencies import get_llm_complete

    # Truncate to fit context window while preserving meaningful content
    truncated = content[:3000]

    prompt = (
        "You are a precise knowledge summarizer. "
        "Summarize the following content in 2-3 clear sentences. "
        "Focus on the key technical insights, discoveries, and actionable information. "
        "Do NOT include filler phrases. Be direct.\n\n"
        f"--- CONTENT ---\n{truncated}\n--- END ---\n\n"
        "SUMMARY:"
    )

    result = await get_llm_complete(prompt, max_tokens=200, temperature=temperature)
    return result.strip()


async def _extract_insights_llm(content: str, temperature: float = 0.3) -> List[str]:
    """Extract key insights using local LLM."""
    from XNAi_rag_app.core.dependencies import get_llm_complete

    truncated = content[:3000]

    prompt = (
        "Extract up to 5 key insights from this content. "
        "Each insight should be a single concise sentence capturing a non-obvious finding. "
        "Return each insight on its own line, prefixed with a dash (-).\n\n"
        f"--- CONTENT ---\n{truncated}\n--- END ---\n\n"
        "KEY INSIGHTS:\n"
    )

    result = await get_llm_complete(prompt, max_tokens=400, temperature=temperature)

    insights = []
    for line in result.strip().split("\n"):
        line = line.strip().lstrip("- •*").strip()
        if len(line) > 10:
            insights.append(line)
        if len(insights) >= 5:
            break

    return insights


async def _extract_action_items_llm(content: str, temperature: float = 0.3) -> List[str]:
    """Extract action items using local LLM."""
    from XNAi_rag_app.core.dependencies import get_llm_complete

    truncated = content[:3000]

    prompt = (
        "Extract actionable tasks or next steps from this content. "
        "Return up to 5 action items, each on its own line prefixed with a dash (-). "
        "If there are no clear action items, return 'None identified.'\n\n"
        f"--- CONTENT ---\n{truncated}\n--- END ---\n\n"
        "ACTION ITEMS:\n"
    )

    result = await get_llm_complete(prompt, max_tokens=300, temperature=temperature)

    actions = []
    for line in result.strip().split("\n"):
        line = line.strip().lstrip("- •*").strip()
        if len(line) > 5 and "none identified" not in line.lower():
            actions.append(line)
        if len(actions) >= 5:
            break

    return actions


# ============================================================================
# REGEX FALLBACK (Used when LLM is unavailable)
# ============================================================================


def _generate_summary_regex(content: str) -> str:
    """Generate brief summary from content using regex (fallback)."""
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    if paragraphs:
        first = paragraphs[0]
        if len(first) > 200:
            return first[:197] + "..."
        return first

    return "No summary available."


def _extract_insights_regex(content: str) -> List[str]:
    """Extract key insights from content using regex (fallback)."""
    insights = []

    patterns = [
        r"Key insight[s]?:?\s*(.+?)(?:\n|$)",
        r"Important:?\s*(.+?)(?:\n|$)",
        r"Note:?\s*(.+?)(?:\n|$)",
        r"Finding[s]?:?\s*(.+?)(?:\n|$)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            insight = match.strip()
            if len(insight) > 10 and insight not in insights:
                insights.append(insight)

    bullets = re.findall(r"[-*]\s*(.+?)(?:\n|$)", content)
    for bullet in bullets[:5]:
        if len(bullet) > 20 and bullet not in insights:
            insights.append(bullet.strip())

    return insights[:10]


def _extract_action_items_regex(content: str) -> List[str]:
    """Extract action items from content using regex (fallback)."""
    actions = []

    patterns = [
        r"TODO:?\s*(.+?)(?:\n|$)",
        r"Action:?\s*(.+?)(?:\n|$)",
        r"Next step[s]?:?\s*(.+?)(?:\n|$)",
        r"Must:?\s*(.+?)(?:\n|$)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            action = match.strip()
            if len(action) > 5 and action not in actions:
                actions.append(action)

    return actions[:10]


# ============================================================================
# MAIN DISTILLATION NODE
# ============================================================================


async def distill_content_node(state: KnowledgeState) -> Dict[str, Any]:
    """
    Distill and refine content using LLM with regex fallback.

    Tasks:
    - Create summary (LLM or regex)
    - Extract key insights (LLM or regex)
    - Identify action items (LLM or regex)
    - Optimize for storage

    Args:
        state: Current knowledge state

    Returns:
        Dict with distilled_content, summary, key_insights, action_items
    """
    content = state.get("extracted_content", "")
    classification = state.get("classification", {})
    use_llm = await _check_llm_available()
    engine = "llm" if use_llm else "regex"
    
    # Extract temperature from state, default to 0.3
    temperature = state.get("temperature", 0.3)

    # Generate summary
    try:
        if use_llm:
            summary = await _generate_summary_llm(content, temperature=temperature)
        else:
            summary = _generate_summary_regex(content)
    except Exception as e:
        logger.warning(f"LLM summary failed, falling back to regex: {e}")
        summary = _generate_summary_regex(content)
        engine = "regex (fallback)"

    # Extract key insights
    try:
        if use_llm:
            key_insights = await _extract_insights_llm(content, temperature=temperature)
        else:
            key_insights = _extract_insights_regex(content)
    except Exception as e:
        logger.warning(f"LLM insights failed, falling back to regex: {e}")
        key_insights = _extract_insights_regex(content)

    # Extract action items
    try:
        if use_llm:
            action_items = await _extract_action_items_llm(content, temperature=temperature)
        else:
            action_items = _extract_action_items_regex(content)
    except Exception as e:
        logger.warning(f"LLM action items failed, falling back to regex: {e}")
        action_items = _extract_action_items_regex(content)

    # Create distilled version
    distilled = _create_distilled(content, summary, key_insights, action_items)

    logger.info(
        f"Distilled ({engine}): {len(distilled)} chars, "
        f"{len(key_insights)} insights, {len(action_items)} actions"
    )

    return {
        "distilled_content": distilled,
        "summary": summary,
        "key_insights": key_insights,
        "action_items": action_items,
    }


def _create_distilled(
    content: str,
    summary: str,
    insights: List[str],
    actions: List[str],
) -> str:
    """Create distilled content document."""
    parts = [f"# Summary\n\n{summary}"]

    if insights:
        parts.append("\n## Key Insights\n")
        for i, insight in enumerate(insights, 1):
            parts.append(f"{i}. {insight}")

    if actions:
        parts.append("\n## Action Items\n")
        for i, action in enumerate(actions, 1):
            parts.append(f"- [ ] {action}")

    # Add condensed content
    parts.append("\n## Content\n")

    # Keep sections with headings
    sections = re.split(r"\n(?=## )", content)
    for section in sections[:5]:  # Limit sections
        if len("\n".join(parts)) + len(section) < 4000:
            parts.append(section)

    return "\n".join(parts)
