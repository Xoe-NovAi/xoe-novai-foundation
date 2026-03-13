#!/usr/bin/env python3
"""
XNAi Enhanced Entity Handler
============================

Advanced "Hey Entity" features including:
- Multiple trigger patterns
- Entity-to-entity communication
- Multi-expert panel summoning
- Expert consultation routing
"""

import re
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class EntityTriggerPattern(Enum):
    """Supported trigger patterns for entity summoning."""

    DIRECT = "hey {entity}, {query}"  # "Hey Kurt, tell me about grunge"
    CONSULT = "ask {entity} about {query}"  # "Ask Plato about virtue"
    COMPARE = "compare {entity1} and {entity2}"  # "Compare Kurt and Plato on creativity"
    PANEL = "summon panel: {entities}"  # "Summon panel: Kurt, Plato, Einstein"
    CONSULT_OTHER = "hey {entity1}, ask {entity2} about {query}"  # "Hey Kurt, ask Plato about virtue"


@dataclass
class EntityQuery:
    """Parsed entity query with routing information."""

    pattern: EntityTriggerPattern
    primary_entity: str
    query: str
    secondary_entity: Optional[str] = None
    entities: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.entities is None:
            self.entities = []


class EnhancedEntityHandler:
    """
    Enhanced handler for "Hey Entity" functionality.
    Supports multiple trigger patterns and entity communication.
    """

    # Entity name aliases for flexible matching
    ENTITY_ALIASES = {
        "kurt": "kurt_cobain",
        "kurt cobain": "kurt_cobain",
        "plato": "plato",
        "socrates": "socrates",
        "einstein": "einstein",
        "tesla": "tesla",
        "ada": "ada_lovelace",
        "ada lovelace": "ada_lovelace",
    }

    # Expert domain mappings
    ENTITY_DOMAINS = {
        "kurt_cobain": ["grunge", "nirvana", "music", "guitar", "seattle_scene"],
        "plato": ["philosophy", "ethics", "dialogues", "ancient_greece"],
        "socrates": ["philosophy", "ethics", "dialectic", "ancient_greece", "virtue", "epistemology"],
        "aristotle": ["philosophy", "ethics", "logic", "metaphysics", "ancient_greece"],
        "einstein": ["physics", "relativity", "quantum_mechanics"],
        "tesla": ["electricity", "inventions", "engineering"],
        "ada_lovelace": ["computing", "algorithms", "mathematics"],
    }

    def __init__(self, entity_registry):
        self.registry = entity_registry

    def parse_query(self, user_input: str) -> Optional[EntityQuery]:
        """
        Parse user input and extract entity query.
        Returns None if no entity pattern detected.
        """
        text = user_input.lower().strip()

        # Pattern 1: Direct summon "Hey Entity, query"
        # Example: "Hey Kurt Cobain, tell me about grunge"
        direct_match = re.match(r"^hey\s+(.+?),\s*(.+)$", text)
        if direct_match:
            entity = self._normalize_entity(direct_match.group(1))
            query = direct_match.group(2)

            # Check for cross-entity query: "Hey Kurt, ask Plato about..."
            consult_match = re.match(r"ask\s+(.+?)\s+about\s+(.+)$", query)
            if consult_match:
                secondary = self._normalize_entity(consult_match.group(1))
                actual_query = consult_match.group(2)
                return EntityQuery(
                    pattern=EntityTriggerPattern.CONSULT_OTHER,
                    primary_entity=entity,
                    query=actual_query,
                    secondary_entity=secondary,
                )

            return EntityQuery(pattern=EntityTriggerPattern.DIRECT, primary_entity=entity, query=query)

        # Pattern 2: Consult "Ask Entity about query"
        # Example: "Ask Plato about virtue ethics"
        consult_match = re.match(r"^ask\s+(.+?)\s+about\s+(.+)$", text)
        if consult_match:
            entity = self._normalize_entity(consult_match.group(1))
            query = consult_match.group(2)
            return EntityQuery(pattern=EntityTriggerPattern.CONSULT, primary_entity=entity, query=query)

        # Pattern 3: Compare "Compare Entity1 and Entity2 on topic"
        # Example: "Compare Kurt and Plato on creativity"
        compare_match = re.match(r"^compare\s+(.+?)\s+and\s+(.+?)\s+on\s+(.+)$", text)
        if compare_match:
            entity1 = self._normalize_entity(compare_match.group(1))
            entity2 = self._normalize_entity(compare_match.group(2))
            topic = compare_match.group(3)
            return EntityQuery(
                pattern=EntityTriggerPattern.COMPARE, primary_entity=entity1, query=topic, secondary_entity=entity2
            )

        # Pattern 4: Panel "Summon panel: Entity1, Entity2, ..."
        # Example: "Summon panel: Kurt, Plato, Einstein"
        panel_match = re.match(r"^summon\s+panel:\s*(.+)$", text)
        if panel_match:
            entities = [self._normalize_entity(e.strip()) for e in panel_match.group(1).split(",")]
            return EntityQuery(
                pattern=EntityTriggerPattern.PANEL,
                primary_entity=entities[0] if entities else "",
                query="panel discussion",
                entities=entities,
            )

        return None

    def _normalize_entity(self, entity_name: str) -> str:
        """Normalize entity name using aliases."""
        normalized = entity_name.lower().strip()
        return self.ENTITY_ALIASES.get(normalized, normalized.replace(" ", "_"))

    def get_entity_domains(self, entity_name: str) -> List[str]:
        """Get associated domains for an entity."""
        normalized = self._normalize_entity(entity_name)
        return self.ENTITY_DOMAINS.get(normalized, [])

    async def handle_query(self, query: EntityQuery) -> Dict[str, Any]:
        """
        Handle parsed entity query.
        Returns response dict with entity interactions.
        """
        if query.pattern == EntityTriggerPattern.DIRECT:
            return await self._handle_direct(query)
        elif query.pattern == EntityTriggerPattern.CONSULT:
            return await self._handle_consult(query)
        elif query.pattern == EntityTriggerPattern.COMPARE:
            return await self._handle_compare(query)
        elif query.pattern == EntityTriggerPattern.PANEL:
            return await self._handle_panel(query)
        elif query.pattern == EntityTriggerPattern.CONSULT_OTHER:
            return await self._handle_cross_entity(query)

        return {"error": "Unknown pattern"}

    async def _handle_direct(self, query: EntityQuery) -> Dict[str, Any]:
        """Handle direct entity query."""
        entity = await self.registry.get_entity(query.primary_entity)

        if not entity.is_initialized:
            # Trigger expertise mining
            await self.registry._trigger_expertise_mining(query.primary_entity, "expert")

        context = entity.get_relevant_context(query.query)

        return {
            "type": "direct",
            "entity": query.primary_entity,
            "query": query.query,
            "context": context,
            "domains": self.get_entity_domains(query.primary_entity),
        }

    async def _handle_consult(self, query: EntityQuery) -> Dict[str, Any]:
        """Handle consultation query."""
        return await self._handle_direct(query)

    async def _handle_compare(self, query: EntityQuery) -> Dict[str, Any]:
        """Handle comparison query between two entities."""
        entity1 = await self.registry.get_entity(query.primary_entity)
        entity2 = await self.registry.get_entity(query.secondary_entity)

        context1 = entity1.get_relevant_context(query.query)
        context2 = entity2.get_relevant_context(query.query)

        return {
            "type": "compare",
            "entity1": query.primary_entity,
            "entity2": query.secondary_entity,
            "topic": query.query,
            "context1": context1,
            "context2": context2,
            "domains1": self.get_entity_domains(query.primary_entity),
            "domains2": self.get_entity_domains(query.secondary_entity) if query.secondary_entity else [],
        }

    async def _handle_panel(self, query: EntityQuery) -> Dict[str, Any]:
        """Handle multi-expert panel query."""
        results = []

        for entity_name in query.entities:
            entity = await self.registry.get_entity(entity_name)
            context = entity.get_relevant_context(query.query)
            results.append({"entity": entity_name, "context": context, "domains": self.get_entity_domains(entity_name)})

        return {"type": "panel", "entities": query.entities, "query": query.query, "results": results}

    async def _handle_cross_entity(self, query: EntityQuery) -> Dict[str, Any]:
        """
        Handle entity-to-entity consultation.
        Example: "Hey Kurt, ask Plato about virtue ethics"
        """
        # Primary entity initiates
        primary = await self.registry.get_entity(query.primary_entity)

        # Get secondary entity's expertise
        secondary = await self.registry.get_entity(query.secondary_entity)

        # Get both contexts
        primary_context = primary.get_relevant_context(query.query)
        secondary_context = secondary.get_relevant_context(query.query)

        return {
            "type": "cross_entity",
            "initiator": query.primary_entity,
            "consulted": query.secondary_entity,
            "query": query.query,
            "initiator_context": primary_context,
            "consulted_context": secondary_context,
            "initiator_domains": self.get_entity_domains(query.primary_entity),
            "consulted_domains": self.get_entity_domains(query.secondary_entity) if query.secondary_entity else [],
        }

    def list_available_entities(self) -> List[str]:
        """List all known entities."""
        return list(self.ENTITY_DOMAINS.keys())

    def get_expert_for_domain(self, domain: str) -> Optional[str]:
        """Find best expert for a given domain."""
        domain = domain.lower()
        for entity, domains in self.ENTITY_DOMAINS.items():
            if any(d in domain or domain in d for d in domains):
                return entity
        return None


# Convenience function for Chainlit integration
def create_entity_handler(entity_registry):
    """Create enhanced entity handler."""
    return EnhancedEntityHandler(entity_registry)
