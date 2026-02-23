"""
Knowledge Distillation Nodes - Distill Node
===========================================

Content distillation node for LangGraph.
"""

import logging
import re
from typing import Dict, Any, List
from datetime import datetime

from ..state import KnowledgeState

logger = logging.getLogger(__name__)


async def distill_content_node(state: KnowledgeState) -> Dict[str, Any]:
    """
    Distill and refine content.

    Tasks:
    - Create summary
    - Extract key insights
    - Identify action items
    - Optimize for storage

    Args:
        state: Current knowledge state

    Returns:
        Dict with distilled_content, summary, key_insights, action_items
    """
    content = state.get("extracted_content", "")
    classification = state.get("classification", {})

    # Generate summary
    summary = _generate_summary(content)

    # Extract key insights
    key_insights = _extract_insights(content)

    # Extract action items
    action_items = _extract_action_items(content)

    # Create distilled version
    distilled = _create_distilled(content, summary, key_insights, action_items)

    logger.info(
        f"Distilled: {len(distilled)} chars, {len(key_insights)} insights, {len(action_items)} actions"
    )

    return {
        "distilled_content": distilled,
        "summary": summary,
        "key_insights": key_insights,
        "action_items": action_items,
    }


def _generate_summary(content: str) -> str:
    """Generate brief summary from content."""
    # Extract first significant paragraph
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    if paragraphs:
        first = paragraphs[0]
        # Truncate to ~200 chars
        if len(first) > 200:
            return first[:197] + "..."
        return first

    return "No summary available."


def _extract_insights(content: str) -> List[str]:
    """Extract key insights from content."""
    insights = []

    # Look for insight patterns
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

    # Extract from bullet points
    bullets = re.findall(r"[-*]\s*(.+?)(?:\n|$)", content)
    for bullet in bullets[:5]:
        if len(bullet) > 20 and bullet not in insights:
            insights.append(bullet.strip())

    return insights[:10]


def _extract_action_items(content: str) -> List[str]:
    """Extract action items from content."""
    actions = []

    # Look for action patterns
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


def _create_distilled(
    content: str,
    summary: str,
    insights: List[str],
    actions: List[str],
) -> str:
    """Create distilled content."""
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
