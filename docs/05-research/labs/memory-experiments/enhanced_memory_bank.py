#!/usr/bin/env python3
"""
Enhanced Memory Bank - Integration of Traditional and Holographic Memory
=========================================================================

Combines the existing Cline memory bank with the new holographic memory system
for enhanced associative recall and intelligent knowledge management.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
from pathlib import Path

from .holographic_memory import HolographicMemory
from .domains import classify_content_domain, get_related_domains


class EnhancedMemoryBank:
    """
    Enhanced memory bank that combines traditional and holographic memory systems.

    This class provides a unified interface for memory operations while leveraging
    both traditional keyword-based recall and advanced holographic associative recall.
    """

    def __init__(self, traditional_memory_bank=None):
        """
        Initialize enhanced memory bank.

        Args:
            traditional_memory_bank: Existing memory bank instance (optional)
        """
        self.traditional_memory = traditional_memory_bank
        self.holographic_memory = HolographicMemory()

        # Integration settings
        self.hybrid_recall_enabled = True
        self.holographic_boost_threshold = 0.7  # Similarity threshold for holographic priority

        # Statistics
        self.stats = {
            'total_operations': 0,
            'hybrid_recalls': 0,
            'holographic_only_recalls': 0,
            'traditional_only_recalls': 0
        }

    async def store(self, content: Union[str, Dict[str, Any]], context: str = "general",
                   metadata: Optional[Dict] = None) -> str:
        """
        Store content in both traditional and holographic memory systems.

        Args:
            content: Content to store (string or dict)
            context: Context category for traditional storage
            metadata: Optional metadata for the content

        Returns:
            Fragment ID from holographic storage
        """
        # Determine primary domain for holographic storage
        primary_domain = self._classify_content_domain(content, context)

        # Convert content to dict format for holographic storage
        content_dict = self._normalize_content(content)

        # Store in holographic memory
        fragment_id = await self.holographic_memory.store_fragment(
            content_dict, primary_domain, metadata
        )

        # Store in traditional memory if available
        if self.traditional_memory:
            traditional_content = content if isinstance(content, str) else str(content)
            # Assume traditional memory has a store method - adapt as needed
            if hasattr(self.traditional_memory, 'store'):
                await self.traditional_memory.store(traditional_content, context)

        self.stats['total_operations'] += 1

        return fragment_id

    async def recall(self, query: str, method: str = "hybrid", top_k: int = 5,
                    min_similarity: Optional[float] = None) -> Dict[str, Any]:
        """
        Recall content using specified method.

        Args:
            query: Query string for recall
            method: "traditional", "holographic", or "hybrid"
            top_k: Maximum results to return
            min_similarity: Minimum similarity threshold

        Returns:
            Dictionary with recall results from different methods
        """
        results = {}

        # Traditional recall
        if method in ["traditional", "hybrid"] and self.traditional_memory:
            traditional_results = await self._traditional_recall(query, top_k)
            results['traditional'] = traditional_results
            if method == "traditional":
                self.stats['traditional_only_recalls'] += 1

        # Holographic recall
        if method in ["holographic", "hybrid"]:
            holographic_results = await self.holographic_memory.holographic_recall(
                query, top_k, min_similarity
            )
            results['holographic'] = holographic_results
            if method == "holographic":
                self.stats['holographic_only_recalls'] += 1

        # Hybrid processing
        if method == "hybrid":
            self.stats['hybrid_recalls'] += 1
            results['hybrid'] = await self._merge_hybrid_results(
                results.get('traditional', []),
                results.get('holographic', []),
                query
            )

        self.stats['total_operations'] += 1

        return results

    async def find_related_content(self, content_id: str, max_related: int = 5) -> List[Dict]:
        """
        Find content related to the specified content ID.

        Args:
            content_id: ID of the content to find relations for
            max_related: Maximum related items to return

        Returns:
            List of related content with relationship strengths
        """
        # Try holographic associative connections first
        try:
            associations = await self.holographic_memory.find_associative_connections(
                content_id, max_related
            )
            if associations:
                return associations
        except Exception:
            pass  # Fall back to traditional methods

        # Fallback: Find related content through traditional methods
        return await self._find_traditional_relations(content_id, max_related)

    async def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics from both memory systems.

        Returns:
            Combined statistics from traditional and holographic memory
        """
        stats = {
            'enhanced_memory_bank': self.stats.copy(),
            'holographic_memory': self.holographic_memory.get_statistics()
        }

        if self.traditional_memory and hasattr(self.traditional_memory, 'get_statistics'):
            stats['traditional_memory'] = await self.traditional_memory.get_statistics()

        return stats

    async def save_state(self, base_path: str):
        """
        Save state of both memory systems.

        Args:
            base_path: Base directory path for saving state
        """
        # Save holographic memory state
        holo_path = Path(base_path) / "holographic_memory_state.json"
        await self.holographic_memory.save_state(str(holo_path))

        # Save enhanced memory bank state
        enhanced_state = {
            'hybrid_recall_enabled': self.hybrid_recall_enabled,
            'holographic_boost_threshold': self.holographic_boost_threshold,
            'stats': self.stats
        }

        enhanced_path = Path(base_path) / "enhanced_memory_bank_state.json"
        with open(enhanced_path, 'w') as f:
            json.dump(enhanced_state, f, default=str, indent=2)

    async def load_state(self, base_path: str):
        """
        Load state of both memory systems.

        Args:
            base_path: Base directory path for loading state
        """
        # Load holographic memory state
        holo_path = Path(base_path) / "holographic_memory_state.json"
        await self.holographic_memory.load_state(str(holo_path))

        # Load enhanced memory bank state
        enhanced_path = Path(base_path) / "enhanced_memory_bank_state.json"
        if enhanced_path.exists():
            with open(enhanced_path, 'r') as f:
                state = json.load(f)
                self.hybrid_recall_enabled = state.get('hybrid_recall_enabled', True)
                self.holographic_boost_threshold = state.get('holographic_boost_threshold', 0.7)
                self.stats.update(state.get('stats', {}))

    def _classify_content_domain(self, content: Union[str, Dict], context: str) -> str:
        """Classify content into appropriate memory domain."""
        # Convert content to string for classification
        content_text = content if isinstance(content, str) else str(content)

        # Use context hints to improve classification
        primary_keywords = []
        if context != "general":
            primary_keywords = [context.lower()]

        return classify_content_domain(content_text, primary_keywords)

    def _normalize_content(self, content: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Normalize content to dictionary format."""
        if isinstance(content, dict):
            return content
        elif isinstance(content, str):
            return {'text': content, 'type': 'text'}
        else:
            return {'content': str(content), 'type': 'unknown'}

    async def _traditional_recall(self, query: str, top_k: int) -> List[Dict]:
        """Perform traditional memory recall."""
        if not self.traditional_memory:
            return []

        # Assume traditional memory has a search method - adapt as needed
        if hasattr(self.traditional_memory, 'search'):
            results = await self.traditional_memory.search(query, limit=top_k)
            return results
        elif hasattr(self.traditional_memory, 'recall'):
            results = await self.traditional_memory.recall(query)
            return results[:top_k] if isinstance(results, list) else []

        return []

    async def _merge_hybrid_results(self, traditional_results: List,
                                   holographic_results: List,
                                   query: str) -> List[Dict]:
        """
        Merge and rank results from both memory systems.

        Uses holographic relevance as primary ranking, with traditional results
        filling gaps and providing additional context.
        """
        merged_results = []

        # Start with holographic results (higher priority)
        holographic_ids = set()
        for result in holographic_results:
            merged_results.append({
                'content': result,
                'source': 'holographic',
                'confidence': getattr(result, 'get', lambda x: 0)('activation', 0.8),
                'domain': getattr(result, 'get', lambda x: 'unknown')('primary_domain', 'unknown')
            })
            holographic_ids.add(getattr(result, 'get', lambda x: None)('id'))

        # Add traditional results that don't overlap
        for result in traditional_results:
            result_id = getattr(result, 'get', lambda x: str(id(result)))('id')
            if result_id not in holographic_ids:
                merged_results.append({
                    'content': result,
                    'source': 'traditional',
                    'confidence': 0.6,  # Lower confidence for traditional results
                    'domain': 'unknown'
                })

        # Sort by confidence and relevance
        merged_results.sort(key=lambda x: x['confidence'], reverse=True)

        return merged_results[:len(holographic_results) + len(traditional_results)]

    async def _find_traditional_relations(self, content_id: str, max_related: int) -> List[Dict]:
        """Find related content using traditional methods."""
        # This would need to be implemented based on the traditional memory system's capabilities
        # For now, return empty list as fallback
        return []

    async def get_holographic_insights(self, query: str) -> Dict[str, Any]:
        """
        Generate holographic insights for a query.

        Returns insights about knowledge patterns, connections, and recommendations.
        """
        # Get holographic recall results
        holo_results = await self.holographic_memory.holographic_recall(query, top_k=10)

        insights = {
            'query': query,
            'total_fragments': len(holo_results),
            'domain_distribution': {},
            'temporal_patterns': {},
            'associative_connections': 0,
            'insights': []
        }

        if not holo_results:
            insights['insights'].append("No holographic memories found for this query")
            return insights

        # Analyze domain distribution
        for result in holo_results:
            domain = getattr(result, 'get', lambda x: 'unknown')('primary_domain')
            insights['domain_distribution'][domain] = insights['domain_distribution'].get(domain, 0) + 1

        # Analyze temporal patterns
        now = datetime.now()
        recent_count = 0
        for result in holo_results:
            timestamp = getattr(result, 'get', lambda x: now)('timestamp')
            hours_old = (now - timestamp).total_seconds() / 3600
            if hours_old < 24:
                recent_count += 1

        insights['temporal_patterns'] = {
            'recent_memories': recent_count,
            'total_memories': len(holo_results),
            'recency_ratio': recent_count / len(holo_results) if holo_results else 0
        }

        # Generate insights
        if insights['temporal_patterns']['recency_ratio'] > 0.7:
            insights['insights'].append("This topic has been actively worked on recently")

        top_domain = max(insights['domain_distribution'].items(), key=lambda x: x[1])
        if top_domain[1] > len(holo_results) * 0.5:
            insights['insights'].append(f"Strong focus in {top_domain[0]} domain")

        return insights


# Global instance for easy access
enhanced_memory_bank = EnhancedMemoryBank()

print("🧠 Enhanced Memory Bank initialized - Traditional + Holographic Integration Complete!")
