#!/usr/bin/env python3
"""
Holographic Memory System - Resurrected from 2025 Mind Model
============================================================

Inspired by the user's 2025 NotebookLM implementation, this system provides:
- Content-addressable memory recall
- Associative weight matrices
- Temporal decay and reinforcement
- Fractal memory organization

Integration with Cline memory bank for enhanced associative recall.
"""

import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import asyncio
from pathlib import Path
import json

# Import memory domains
try:
    from .domains import MEMORY_DOMAINS
except ImportError:
    # Fallback if domains.py not yet created
    MEMORY_DOMAINS = [
        'technical_architecture',
        'user_requirements', 
        'implementation_patterns',
        'error_solutions',
        'performance_optimizations',
        'security_practices',
        'testing_strategies',
        'deployment_processes',
        'documentation_patterns',
        'collaboration_history'
    ]


class HolographicMemory:
    """
    Holographic memory system with associative recall.

    Based on the user's 2025 Omnidroid Ω implementation, adapted for Cline memory bank.
    Provides content-addressable storage and retrieval with associative connections.
    """

    def __init__(self, decay_rate: float = 0.95, similarity_threshold: float = 0.7):
        """
        Initialize holographic memory system.

        Args:
            decay_rate: Temporal decay factor (0.95 = 5% decay per hour)
            similarity_threshold: Minimum similarity for recall (0-1)
        """
        self.memory_fragments = []
        self.associative_matrix = np.eye(len(MEMORY_DOMAINS))
        self.decay_rate = decay_rate
        self.similarity_threshold = similarity_threshold
        self._last_decay = datetime.now()

        # Performance tracking
        self.stats = {
            'fragments_stored': 0,
            'recall_operations': 0,
            'average_similarity': 0.0,
            'temporal_decay_applied': 0
        }

    async def store_fragment(self, content: Dict[str, Any], primary_domain: str, metadata: Optional[Dict] = None) -> str:
        """
        Store experience as holographic memory fragment.

        Args:
            content: The content to store
            primary_domain: Primary memory domain for this fragment
            metadata: Optional metadata (tags, importance, etc.)

        Returns:
            Fragment ID for tracking
        """
        fragment_id = str(uuid.uuid4())

        fragment = {
            'id': fragment_id,
            'timestamp': datetime.now(),
            'content': content,
            'associations': self._extract_associations(content, primary_domain),
            'activation': 1.0,
            'metadata': metadata or {},
            'access_count': 0,
            'last_accessed': datetime.now(),
            'primary_domain': primary_domain
        }

        self.memory_fragments.append(fragment)
        await self._update_associative_weights(fragment)

        self.stats['fragments_stored'] += 1

        return fragment_id

    async def holographic_recall(self, query: str, top_k: int = 5, min_similarity: Optional[float] = None) -> List[Dict]:
        """
        Content-addressable recall using holographic principles.

        Args:
            query: Query string for recall
            top_k: Maximum number of results to return
            min_similarity: Override similarity threshold

        Returns:
            List of relevant memory fragments with similarity scores
        """
        threshold = min_similarity if min_similarity is not None else self.similarity_threshold

        # Apply temporal decay if needed
        await self._apply_temporal_decay()

        query_vector = self._vectorize_query(query)

        scored_fragments = []
        for fragment in self.memory_fragments:
            similarity = self._cosine_similarity(query_vector, fragment['associations'])

            if similarity >= threshold:
                # Calculate holographic relevance (combines similarity + activation + recency)
                holographic_score = self._calculate_holographic_score(fragment, similarity)

                scored_fragments.append({
                    'fragment': fragment,
                    'similarity': similarity,
                    'holographic_score': holographic_score,
                    'domain': fragment['primary_domain']
                })

        # Sort by holographic score (most relevant first)
        scored_fragments.sort(key=lambda x: x['holographic_score'], reverse=True)

        # Update access patterns for reinforcement
        retrieved_fragments = scored_fragments[:top_k]
        await self._reinforce_accessed_fragments(retrieved_fragments)

        self.stats['recall_operations'] += 1

        return [item['fragment'] for item in retrieved_fragments]

    def get_statistics(self) -> Dict[str, Any]:
        """Get holographic memory statistics."""
        total_fragments = len(self.memory_fragments)

        if total_fragments == 0:
            return self.stats

        # Calculate additional metrics
        avg_activation = np.mean([f['activation'] for f in self.memory_fragments])
        avg_access_count = np.mean([f['access_count'] for f in self.memory_fragments])

        domain_distribution = {}
        for fragment in self.memory_fragments:
            domain = fragment['primary_domain']
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1

        return {
            **self.stats,
            'total_fragments': total_fragments,
            'average_activation': avg_activation,
            'average_access_count': avg_access_count,
            'domain_distribution': domain_distribution,
            'associative_matrix_density': np.mean(self.associative_matrix)
        }

    def _extract_associations(self, content: Dict[str, Any], primary_domain: str) -> np.array:
        """
        Extract associative vector from content.

        Based on the user's 2025 implementation, creates a numerical representation
        of the content for similarity calculations.
        """
        associations = np.zeros(len(MEMORY_DOMAINS))

        # Convert content to searchable text
        content_text = self._content_to_text(content)

        # Calculate relevance for each domain
        for i, domain in enumerate(MEMORY_DOMAINS):
            relevance = self._calculate_domain_relevance(content_text, domain, primary_domain)
            associations[i] = relevance

        # Normalize associations
        if np.max(associations) > 0:
            associations = associations / np.max(associations)

        return associations

    def _content_to_text(self, content: Dict[str, Any]) -> str:
        """Convert content dict to searchable text."""
        if isinstance(content, str):
            return content

        text_parts = []
        for key, value in content.items():
            if isinstance(value, str):
                text_parts.append(f"{key}: {value}")
            elif isinstance(value, (list, tuple)):
                text_parts.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                text_parts.append(f"{key}: {str(value)}")

        return ' '.join(text_parts)

    def _calculate_domain_relevance(self, content_text: str, domain: str, primary_domain: str) -> float:
        """
        Calculate how relevant content is to a specific domain.

        Uses keyword matching and primary domain boost.
        """
        # Domain-specific keywords
        domain_keywords = {
            'technical_architecture': ['api', 'database', 'server', 'architecture', 'system', 'infrastructure'],
            'user_requirements': ['user', 'requirement', 'need', 'feature', 'functionality', 'use case'],
            'implementation_patterns': ['pattern', 'implementation', 'code', 'algorithm', 'solution'],
            'error_solutions': ['error', 'bug', 'fix', 'solution', 'debug', 'issue', 'problem'],
            'performance_optimizations': ['performance', 'optimization', 'speed', 'efficiency', 'optimization'],
            'security_practices': ['security', 'auth', 'encryption', 'vulnerability', 'protection'],
            'testing_strategies': ['test', 'testing', 'validation', 'quality', 'coverage'],
            'deployment_processes': ['deploy', 'deployment', 'production', 'release', 'ci/cd'],
            'documentation_patterns': ['docs', 'documentation', 'readme', 'guide', 'tutorial'],
            'collaboration_history': ['meeting', 'discussion', 'collaboration', 'team', 'communication']
        }

        keywords = domain_keywords.get(domain, [])
        if not keywords:
            return 0.0

        # Count keyword matches
        text_lower = content_text.lower()
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        relevance = matches / len(keywords)

        # Boost if this is the primary domain
        if domain == primary_domain:
            relevance *= 2.0

        return min(1.0, relevance)

    def _vectorize_query(self, query: str) -> np.array:
        """
        Convert query string to vector representation.

        Similar to content vectorization but focused on query terms.
        """
        query_vector = np.zeros(len(MEMORY_DOMAINS))

        query_lower = query.lower()

        for i, domain in enumerate(MEMORY_DOMAINS):
            # Simple term matching - could be enhanced with embeddings
            domain_keywords = self._get_domain_keywords(domain)
            matches = sum(1 for keyword in domain_keywords if keyword in query_lower)
            query_vector[i] = matches / max(1, len(domain_keywords))

        return query_vector

    def _get_domain_keywords(self, domain: str) -> List[str]:
        """Get keywords associated with a domain."""
        # Simplified - could be expanded
        keyword_map = {
            'technical_architecture': ['architecture', 'system', 'api', 'database'],
            'user_requirements': ['user', 'requirement', 'feature', 'need'],
            'implementation_patterns': ['pattern', 'implementation', 'code'],
            'error_solutions': ['error', 'fix', 'solution', 'bug'],
            'performance_optimizations': ['performance', 'speed', 'optimization'],
            'security_practices': ['security', 'auth', 'encryption'],
            'testing_strategies': ['test', 'testing', 'validation'],
            'deployment_processes': ['deploy', 'deployment', 'production'],
            'documentation_patterns': ['docs', 'documentation', 'guide'],
            'collaboration_history': ['meeting', 'team', 'discussion']
        }
        return keyword_map.get(domain, [])

    def _cosine_similarity(self, a: np.array, b: np.array) -> float:
        """
        Calculate cosine similarity between two vectors.

        From the user's 2025 implementation.
        """
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

    def _calculate_holographic_score(self, fragment: Dict, similarity: float) -> float:
        """
        Calculate holographic relevance score.

        Combines similarity, activation, and recency for comprehensive scoring.
        """
        # Base similarity score
        score = similarity

        # Activation boost (how "alive" this memory is)
        score *= fragment['activation']

        # Recency boost (newer memories are more relevant)
        hours_old = (datetime.now() - fragment['timestamp']).total_seconds() / 3600
        recency_boost = max(0.5, 1.0 - (hours_old / 24))  # Full boost for < 24h, minimum after
        score *= recency_boost

        # Access pattern boost (frequently accessed memories)
        access_boost = 1.0 + (fragment['access_count'] * 0.1)
        score *= min(2.0, access_boost)  # Cap at 2x boost

        return score

    async def _update_associative_weights(self, fragment: Dict):
        """
        Update the associative weight matrix.

        From the user's 2025 holographic memory implementation.
        """
        if fragment['primary_domain'] not in MEMORY_DOMAINS:
            return

        domain_idx = MEMORY_DOMAINS.index(fragment['primary_domain'])

        # Strengthen connections to this domain
        self.associative_matrix[domain_idx] += 0.01
        self.associative_matrix[:, domain_idx] += 0.005  # Bidirectional strengthening

        # Keep matrix normalized
        self.associative_matrix = np.clip(self.associative_matrix, 0, 1)

    async def _apply_temporal_decay(self):
        """
        Apply temporal decay to memory activations.

        From the user's 2025 implementation.
        """
        current_time = datetime.now()
        hours_elapsed = (current_time - self._last_decay).total_seconds() / 3600

        if hours_elapsed < 1:  # Only decay once per hour
            return

        decay_factor = self.decay_rate ** hours_elapsed

        for fragment in self.memory_fragments:
            # Apply decay
            fragment['activation'] *= decay_factor

            # Ensure minimum activation
            fragment['activation'] = max(0.1, fragment['activation'])

        self._last_decay = current_time
        self.stats['temporal_decay_applied'] += 1

    async def _reinforce_accessed_fragments(self, accessed_fragments: List[Dict]):
        """
        Reinforce activation of accessed memory fragments.

        From the user's 2025 temporal reinforcement concept.
        """
        for item in accessed_fragments:
            fragment = item['fragment']
            fragment['activation'] = min(1.0, fragment['activation'] + 0.1)
            fragment['access_count'] += 1
            fragment['last_accessed'] = datetime.now()

    def _find_shared_domains(self, frag1: Dict, frag2: Dict) -> List[str]:
        """Find domains that both fragments belong to or are related to."""
        domains1 = set([frag1['primary_domain']])
        domains2 = set([frag2['primary_domain']])

        # Could be expanded to include related domains based on associative matrix
        return list(domains1 & domains2)

    async def find_associative_connections(self, fragment_id: str, max_connections: int = 5) -> List[Dict]:
        """
        Find associative connections to a given fragment.

        Args:
            fragment_id: ID of the source fragment
            max_connections: Maximum connections to return

        Returns:
            List of associated fragments with connection strengths
        """
        source_fragment = None
        for fragment in self.memory_fragments:
            if fragment['id'] == fragment_id:
                source_fragment = fragment
                break

        if not source_fragment:
            return []

        connections = []
        source_vector = source_fragment['associations']

        for fragment in self.memory_fragments:
            if fragment['id'] == fragment_id:
                continue

            similarity = self._cosine_similarity(source_vector, fragment['associations'])
            if similarity > 0.5:  # Threshold for associative connections
                connections.append({
                    'fragment': fragment,
                    'connection_strength': similarity,
                    'shared_domains': self._find_shared_domains(source_fragment, fragment)
                })

        # Sort by connection strength
        connections.sort(key=lambda x: x['connection_strength'], reverse=True)

        return connections[:max_connections]

    async def save_state(self, filepath: str):
        """Save holographic memory state to disk."""
        state = {
            'memory_fragments': self.memory_fragments,
            'associative_matrix': self.associative_matrix.tolist(),
            'decay_rate': self.decay_rate,
            'similarity_threshold': self.similarity_threshold,
            'stats': self.stats,
            'last_decay': self._last_decay.isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, default=str, indent=2)

    async def load_state(self, filepath: str):
        """Load holographic memory state from disk."""
        if not Path(filepath).exists():
            return

        with open(filepath, 'r') as f:
            state = json.load(f)

        self.memory_fragments = state['memory_fragments']
        self.associative_matrix = np.array(state['associative_matrix'])
        self.decay_rate = state['decay_rate']
        self.similarity_threshold = state['similarity_threshold']
        self.stats = state['stats']
        self._last_decay = datetime.fromisoformat(state['last_decay'])

        # Convert timestamp strings back to datetime
        for fragment in self.memory_fragments:
            fragment['timestamp'] = datetime.fromisoformat(fragment['timestamp'])
            fragment['last_accessed'] = datetime.fromisoformat(fragment['last_accessed'])