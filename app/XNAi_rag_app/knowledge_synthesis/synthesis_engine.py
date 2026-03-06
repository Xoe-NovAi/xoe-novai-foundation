"""
XNAi Cortex - Knowledge Synthesis Engine

This module provides the core knowledge synthesis capabilities for the XNAi Knowledge Synthesis Engine,
handling pattern detection, knowledge graph building, and advanced analysis.
"""

import asyncio
import json
import logging
import networkx as nx
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from uuid import UUID, uuid4
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import spacy

from ..core.llm_router import LLMRouter
from ..core.memory_bank import MemoryBank
from ..core.qdrant_manager import QdrantManager
from ..core.redis_streams import RedisStreamManager
from ..core.security.knowledge_access import KnowledgeAccessControl
from .curation_pipeline import CuratedContent

logger = logging.getLogger(__name__)


class KnowledgeEntity(BaseModel):
    """Represents an entity in the knowledge graph."""
    
    id: UUID
    entity_type: str  # "person", "organization", "location", "concept", "technology"
    entity_value: str
    confidence: float
    aliases: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeRelationship(BaseModel):
    """Represents a relationship between entities in the knowledge graph."""
    
    id: UUID
    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: str
    confidence: float
    evidence: List[str] = Field(default_factory=list)
    strength: float = 1.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PatternDetectionResult(BaseModel):
    """Represents a detected pattern in the knowledge graph."""
    
    id: UUID
    pattern_type: str  # "topic_evolution", "entity_correlation", "anomaly", "trend"
    description: str
    confidence: float
    entities_involved: List[UUID] = Field(default_factory=list)
    time_span: Optional[Dict[str, datetime]] = None
    evidence: List[str] = Field(default_factory=list)
    significance: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraph:
    """Knowledge graph implementation using NetworkX."""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.entities: Dict[UUID, KnowledgeEntity] = {}
        self.relationships: Dict[UUID, KnowledgeRelationship] = {}
        
    def add_entity(self, entity: KnowledgeEntity):
        """Add an entity to the knowledge graph."""
        self.entities[entity.id] = entity
        self.graph.add_node(
            entity.id,
            type=entity.entity_type,
            value=entity.entity_value,
            confidence=entity.confidence,
            aliases=entity.aliases,
            description=entity.description,
            metadata=entity.metadata
        )
    
    def add_relationship(self, relationship: KnowledgeRelationship):
        """Add a relationship to the knowledge graph."""
        self.relationships[relationship.id] = relationship
        self.graph.add_edge(
            relationship.source_entity_id,
            relationship.target_entity_id,
            type=relationship.relationship_type,
            confidence=relationship.confidence,
            strength=relationship.strength,
            evidence=relationship.evidence,
            metadata=relationship.metadata
        )
    
    def get_entity(self, entity_id: UUID) -> Optional[KnowledgeEntity]:
        """Get an entity by ID."""
        return self.entities.get(entity_id)
    
    def get_relationship(self, relationship_id: UUID) -> Optional[KnowledgeRelationship]:
        """Get a relationship by ID."""
        return self.relationships.get(relationship_id)
    
    def find_related_entities(self, entity_id: UUID, max_depth: int = 2) -> List[UUID]:
        """Find entities related to a given entity."""
        if entity_id not in self.graph:
            return []
        
        related = []
        for depth in range(1, max_depth + 1):
            neighbors = nx.single_source_shortest_path_length(
                self.graph, entity_id, cutoff=depth
            )
            related.extend([node for node, dist in neighbors.items() if dist == depth])
        
        return list(set(related))
    
    def get_entity_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "entity_types": Counter([entity.entity_type for entity in self.entities.values()]),
            "graph_density": nx.density(self.graph),
            "connected_components": nx.number_connected_components(self.graph),
            "average_clustering": nx.average_clustering(self.graph)
        }


class ContentAnalyzer:
    """Advanced content analysis for knowledge extraction."""
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self.nlp = None  # Will be loaded on demand
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    async def load_nlp_model(self):
        """Load the spaCy NLP model."""
        if self.nlp is None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, using basic analysis")
                self.nlp = None
    
    async def extract_advanced_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities using both LLM and spaCy."""
        entities = []
        
        # LLM-based entity extraction
        llm_entities = await self._extract_llm_entities(content)
        entities.extend(llm_entities)
        
        # spaCy-based entity extraction (if available)
        if self.nlp:
            spacy_entities = await self._extract_spacy_entities(content)
            entities.extend(spacy_entities)
        
        # Deduplicate and merge entities
        return self._merge_entities(entities)
    
    async def _extract_llm_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities using LLM."""
        try:
            prompt = f"""
            Extract all entities from the following content. Return in JSON format:
            {{
                "entities": [
                    {{
                        "type": "person|organization|location|concept|technology",
                        "value": "entity name",
                        "confidence": 0.0-1.0,
                        "aliases": ["alias1", "alias2"],
                        "description": "brief description"
                    }}
                ]
            }}
            
            Content:
            {content[:2000]}
            """
            
            response = await self.llm_router.route_request(
                prompt=prompt,
                context={"operation": "advanced_entity_extraction"},
                model_preference="entity-extraction-model"
            )
            
            result = json.loads(response)
            return result.get("entities", [])
            
        except Exception as e:
            logger.error(f"Error extracting LLM entities: {e}")
            return []
    
    async def _extract_spacy_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities using spaCy."""
        try:
            doc = self.nlp(content[:2000])
            entities = []
            
            for ent in doc.ents:
                entity_type = self._map_spacy_type(ent.label_)
                if entity_type:
                    entities.append({
                        "type": entity_type,
                        "value": ent.text,
                        "confidence": 0.8,  # Default confidence for spaCy
                        "aliases": [],
                        "description": f"spaCy detected {entity_type}"
                    })
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting spaCy entities: {e}")
            return []
    
    def _map_spacy_type(self, spacy_type: str) -> Optional[str]:
        """Map spaCy entity types to our types."""
        mapping = {
            'PERSON': 'person',
            'ORG': 'organization',
            'GPE': 'location',
            'LOC': 'location',
            'PRODUCT': 'technology',
            'EVENT': 'concept',
            'WORK_OF_ART': 'concept',
            'LAW': 'concept',
            'LANGUAGE': 'concept'
        }
        return mapping.get(spacy_type)
    
    def _merge_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge duplicate entities."""
        merged = {}
        
        for entity in entities:
            key = (entity['type'], entity['value'].lower())
            if key in merged:
                # Update confidence (take maximum)
                merged[key]['confidence'] = max(merged[key]['confidence'], entity['confidence'])
                # Merge aliases
                merged[key]['aliases'].extend(entity.get('aliases', []))
                merged[key]['aliases'] = list(set(merged[key]['aliases']))
            else:
                merged[key] = entity
        
        return list(merged.values())
    
    async def extract_topics(self, content: str) -> List[Dict[str, Any]]:
        """Extract topics from content using LLM."""
        try:
            prompt = f"""
            Identify the main topics and themes in the following content.
            Return in JSON format:
            {{
                "topics": [
                    {{
                        "topic": "topic name",
                        "relevance": 0.0-1.0,
                        "keywords": ["keyword1", "keyword2"],
                        "description": "topic description"
                    }}
                ]
            }}
            
            Content:
            {content[:1500]}
            """
            
            response = await self.llm_router.route_request(
                prompt=prompt,
                context={"operation": "topic_extraction"},
                model_preference="topic-extraction-model"
            )
            
            result = json.loads(response)
            return result.get("topics", [])
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    async def analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of content."""
        try:
            prompt = f"""
            Analyze the sentiment of the following content.
            Return in JSON format:
            {{
                "sentiment": "positive|negative|neutral",
                "confidence": 0.0-1.0,
                "sentiment_score": -1.0 to 1.0,
                "key_phrases": ["phrase1", "phrase2"]
            }}
            
            Content:
            {content[:1000]}
            """
            
            response = await self.llm_router.route_request(
                prompt=prompt,
                context={"operation": "sentiment_analysis"},
                model_preference="sentiment-analysis-model"
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"sentiment": "neutral", "confidence": 0.5, "sentiment_score": 0.0}


class PatternDetector:
    """Advanced pattern detection in knowledge graphs."""
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self.knowledge_graph = KnowledgeGraph()
    
    async def detect_topic_evolution(self, time_range: Dict[str, datetime], topics: List[str]) -> List[PatternDetectionResult]:
        """Detect how topics evolve over time."""
        patterns = []
        
        try:
            # Get content within time range
            content_items = await self._get_content_in_time_range(time_range)
            
            # Analyze topic trends
            topic_trends = await self._analyze_topic_trends(content_items, topics)
            
            # Detect evolution patterns
            for topic, trend_data in topic_trends.items():
                if len(trend_data['timestamps']) > 2:  # Need at least 3 data points
                    pattern = await self._detect_topic_evolution_pattern(topic, trend_data)
                    if pattern:
                        patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"Error detecting topic evolution: {e}")
        
        return patterns
    
    async def detect_entity_correlations(self, entities: List[str], time_range: Optional[Dict[str, datetime]] = None) -> List[PatternDetectionResult]:
        """Detect correlations between entities."""
        patterns = []
        
        try:
            # Get entity relationships
            relationships = await self._get_entity_relationships(entities, time_range)
            
            # Analyze correlation patterns
            correlations = await self._analyze_entity_correlations(relationships)
            
            for correlation in correlations:
                pattern = await self._create_correlation_pattern(correlation)
                if pattern:
                    patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"Error detecting entity correlations: {e}")
        
        return patterns
    
    async def detect_anomalies(self, content_items: List[CuratedContent]) -> List[PatternDetectionResult]:
        """Detect anomalous content or patterns."""
        patterns = []
        
        try:
            # Content-based anomaly detection
            content_anomalies = await self._detect_content_anomalies(content_items)
            patterns.extend(content_anomalies)
            
            # Entity-based anomaly detection
            entity_anomalies = await self._detect_entity_anomalies(content_items)
            patterns.extend(entity_anomalies)
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
        
        return patterns
    
    async def _get_content_in_time_range(self, time_range: Dict[str, datetime]) -> List[CuratedContent]:
        """Get content items within a time range."""
        # This would query the database for content in the time range
        # For now, return empty list
        return []
    
    async def _analyze_topic_trends(self, content_items: List[CuratedContent], topics: List[str]) -> Dict[str, Dict]:
        """Analyze topic trends over time."""
        topic_trends = {topic: {'timestamps': [], 'scores': []} for topic in topics}
        
        for content in content_items:
            if content.metadata and 'topics' in content.metadata:
                for topic_data in content.metadata['topics']:
                    topic = topic_data.get('topic')
                    if topic in topics:
                        topic_trends[topic]['timestamps'].append(content.created_at)
                        topic_trends[topic]['scores'].append(topic_data.get('relevance', 0.0))
        
        return topic_trends
    
    async def _detect_topic_evolution_pattern(self, topic: str, trend_data: Dict) -> Optional[PatternDetectionResult]:
        """Detect evolution pattern for a specific topic."""
        try:
            timestamps = trend_data['timestamps']
            scores = trend_data['scores']
            
            if len(scores) < 3:
                return None
            
            # Calculate trend direction
            x = np.arange(len(scores))
            slope = np.polyfit(x, scores, 1)[0]
            
            # Determine pattern type
            if slope > 0.1:
                pattern_type = "growing_interest"
                description = f"Topic '{topic}' shows growing interest over time"
            elif slope < -0.1:
                pattern_type = "declining_interest"
                description = f"Topic '{topic}' shows declining interest over time"
            else:
                pattern_type = "stable_interest"
                description = f"Topic '{topic}' shows stable interest over time"
            
            confidence = abs(slope)
            
            return PatternDetectionResult(
                id=uuid4(),
                pattern_type=pattern_type,
                description=description,
                confidence=confidence,
                time_span={
                    "start": min(timestamps),
                    "end": max(timestamps)
                },
                metadata={
                    "topic": topic,
                    "slope": slope,
                    "data_points": len(scores)
                }
            )
            
        except Exception as e:
            logger.error(f"Error detecting topic evolution pattern: {e}")
            return None
    
    async def _get_entity_relationships(self, entities: List[str], time_range: Optional[Dict[str, datetime]]) -> List[Dict]:
        """Get relationships between entities."""
        # This would query the knowledge graph for relationships
        # For now, return empty list
        return []
    
    async def _analyze_entity_correlations(self, relationships: List[Dict]) -> List[Dict]:
        """Analyze correlations between entities."""
        correlations = []
        
        # Group relationships by entity pairs
        entity_pairs = defaultdict(list)
        for rel in relationships:
            pair = tuple(sorted([rel['source'], rel['target']]))
            entity_pairs[pair].append(rel)
        
        # Calculate correlation strength
        for pair, rels in entity_pairs.items():
            if len(rels) > 1:  # Need multiple relationships for correlation
                avg_strength = sum(rel.get('strength', 1.0) for rel in rels) / len(rels)
                if avg_strength > 0.5:
                    correlations.append({
                        'entities': pair,
                        'correlation_strength': avg_strength,
                        'relationship_count': len(rels)
                    })
        
        return correlations
    
    async def _create_correlation_pattern(self, correlation: Dict) -> Optional[PatternDetectionResult]:
        """Create a correlation pattern."""
        try:
            entities = correlation['entities']
            strength = correlation['correlation_strength']
            
            return PatternDetectionResult(
                id=uuid4(),
                pattern_type="entity_correlation",
                description=f"Strong correlation detected between {entities[0]} and {entities[1]}",
                confidence=strength,
                entities_involved=[],
                metadata={
                    "correlated_entities": list(entities),
                    "correlation_strength": strength,
                    "relationship_count": correlation['relationship_count']
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating correlation pattern: {e}")
            return None
    
    async def _detect_content_anomalies(self, content_items: List[CuratedContent]) -> List[PatternDetectionResult]:
        """Detect anomalous content items."""
        anomalies = []
        
        try:
            # Use quality scores to detect anomalies
            quality_scores = [item.quality_score for item in content_items]
            
            if len(quality_scores) > 5:
                mean_score = np.mean(quality_scores)
                std_score = np.std(quality_scores)
                
                for content in content_items:
                    z_score = abs((content.quality_score - mean_score) / std_score)
                    if z_score > 2.0:  # Outlier threshold
                        anomalies.append(PatternDetectionResult(
                            id=uuid4(),
                            pattern_type="content_anomaly",
                            description=f"Content '{content.title}' has anomalous quality score",
                            confidence=z_score / 3.0,
                            metadata={
                                "content_id": str(content.id),
                                "quality_score": content.quality_score,
                                "z_score": z_score
                            }
                        ))
            
        except Exception as e:
            logger.error(f"Error detecting content anomalies: {e}")
        
        return anomalies
    
    async def _detect_entity_anomalies(self, content_items: List[CuratedContent]) -> List[PatternDetectionResult]:
        """Detect anomalous entity patterns."""
        anomalies = []
        
        try:
            # Count entity occurrences
            entity_counts = Counter()
            for content in content_items:
                if content.entities:
                    for entity in content.entities:
                        entity_counts[entity['value']] += 1
            
            # Detect unusual entity frequencies
            if entity_counts:
                mean_freq = np.mean(list(entity_counts.values()))
                std_freq = np.std(list(entity_counts.values()))
                
                for entity, count in entity_counts.items():
                    z_score = abs((count - mean_freq) / std_freq)
                    if z_score > 2.5:  # High anomaly threshold
                        anomalies.append(PatternDetectionResult(
                            id=uuid4(),
                            pattern_type="entity_anomaly",
                            description=f"Entity '{entity}' appears with anomalous frequency",
                            confidence=z_score / 3.5,
                            metadata={
                                "entity": entity,
                                "frequency": count,
                                "z_score": z_score
                            }
                        ))
            
        except Exception as e:
            logger.error(f"Error detecting entity anomalies: {e}")
        
        return anomalies


class KnowledgeSynthesisEngine:
    """Main knowledge synthesis engine."""
    
    def __init__(
        self,
        llm_router: LLMRouter,
        memory_bank: MemoryBank,
        qdrant_manager: QdrantManager,
        redis_manager: RedisStreamManager,
        access_control: KnowledgeAccessControl
    ):
        self.llm_router = llm_router
        self.memory_bank = memory_bank
        self.qdrant_manager = qdrant_manager
        self.redis_manager = redis_manager
        self.access_control = access_control
        
        self.content_analyzer = ContentAnalyzer(llm_router)
        self.pattern_detector = PatternDetector(llm_router)
        self.knowledge_graph = self.pattern_detector.knowledge_graph
        
        # Processing state
        self.is_running = False
        self.synthesis_tasks: List[asyncio.Task] = []
    
    async def start(self):
        """Start the knowledge synthesis engine."""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting XNAi Cortex synthesis engine")
        
        # Start background tasks
        self.synthesis_tasks = [
            asyncio.create_task(self._knowledge_graph_builder()),
            asyncio.create_task(self._pattern_detection_task()),
            asyncio.create_task(self._knowledge_integrator())
        ]
    
    async def stop(self):
        """Stop the knowledge synthesis engine."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel tasks
        for task in self.synthesis_tasks:
            task.cancel()
        
        await asyncio.gather(*self.synthesis_tasks, return_exceptions=True)
        logger.info("Stopped XNAi Cortex synthesis engine")
    
    async def process_content(self, content: CuratedContent) -> Dict[str, Any]:
        """Process content and extract knowledge."""
        try:
            # Extract entities
            entities = await self.content_analyzer.extract_advanced_entities(content.content)
            
            # Extract topics
            topics = await self.content_analyzer.extract_topics(content.content)
            
            # Analyze sentiment
            sentiment = await self.content_analyzer.analyze_sentiment(content.content)
            
            # Build knowledge graph
            await self._build_knowledge_from_content(content, entities, topics)
            
            # Store analysis results
            analysis_result = {
                "content_id": str(content.id),
                "entities": entities,
                "topics": topics,
                "sentiment": sentiment,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            await self.memory_bank.save_to_archival(
                f"content_analysis_{content.id}",
                analysis_result
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error processing content {content.id}: {e}")
            return {"error": str(e)}
    
    async def _build_knowledge_from_content(self, content: CuratedContent, entities: List[Dict], topics: List[Dict]):
        """Build knowledge graph from content analysis."""
        try:
            # Add entities to knowledge graph
            for entity_data in entities:
                entity = KnowledgeEntity(
                    id=uuid4(),
                    entity_type=entity_data['type'],
                    entity_value=entity_data['value'],
                    confidence=entity_data['confidence'],
                    aliases=entity_data.get('aliases', []),
                    description=entity_data.get('description', ''),
                    metadata={
                        "source_content": str(content.id),
                        "extraction_method": "advanced"
                    }
                )
                self.knowledge_graph.add_entity(entity)
            
            # Add relationships based on co-occurrence
            if len(entities) > 1:
                for i, entity1 in enumerate(entities):
                    for j, entity2 in enumerate(entities[i+1:], i+1):
                        relationship = KnowledgeRelationship(
                            id=uuid4(),
                            source_entity_id=UUID(str(uuid4())),  # Would need actual entity IDs
                            target_entity_id=UUID(str(uuid4())),
                            relationship_type="co_occurrence",
                            confidence=0.8,
                            evidence=[content.title],
                            strength=1.0,
                            metadata={
                                "source_content": str(content.id),
                                "topic_relevance": topics[0].get('relevance', 0.5) if topics else 0.5
                            }
                        )
                        self.knowledge_graph.add_relationship(relationship)
            
        except Exception as e:
            logger.error(f"Error building knowledge from content: {e}")
    
    async def _knowledge_graph_builder(self):
        """Background task to build and maintain knowledge graph."""
        while self.is_running:
            try:
                # This would periodically process new content and update the graph
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in knowledge graph builder: {e}")
                await asyncio.sleep(60)
    
    async def _pattern_detection_task(self):
        """Background task for pattern detection."""
        while self.is_running:
            try:
                # Detect patterns periodically
                patterns = await self.detect_patterns()
                
                # Store detected patterns
                for pattern in patterns:
                    await self.memory_bank.save_to_archival(
                        f"pattern_{pattern.id}",
                        pattern.dict()
                    )
                
                await asyncio.sleep(600)  # Run every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in pattern detection task: {e}")
                await asyncio.sleep(60)
    
    async def _knowledge_integrator(self):
        """Background task to integrate knowledge across sources."""
        while self.is_running:
            try:
                # Integrate knowledge from different sources
                await self._integrate_knowledge()
                await asyncio.sleep(1800)  # Run every 30 minutes
                
            except Exception as e:
                logger.error(f"Error in knowledge integrator: {e}")
                await asyncio.sleep(60)
    
    async def detect_patterns(self) -> List[PatternDetectionResult]:
        """Detect patterns in the knowledge graph."""
        patterns = []
        
        try:
            # Get recent content for pattern detection
            recent_content = await self._get_recent_content(hours=24)
            
            if recent_content:
                # Detect anomalies
                anomalies = await self.pattern_detector.detect_anomalies(recent_content)
                patterns.extend(anomalies)
                
                # Detect topic evolution (if we have historical data)
                # This would require more sophisticated time-series analysis
                
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
        
        return patterns
    
    async def _get_recent_content(self, hours: int = 24) -> List[CuratedContent]:
        """Get content from the last N hours."""
        # This would query the database for recent content
        # For now, return empty list
        return []
    
    async def _integrate_knowledge(self):
        """Integrate knowledge from different sources."""
        try:
            # This would merge knowledge from different content sources
            # and resolve conflicts or redundancies
            
            # Update entity statistics
            stats = self.knowledge_graph.get_entity_statistics()
            
            # Store integration results
            await self.memory_bank.save_to_archival(
                "knowledge_integration_stats",
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "stats": stats
                }
            )
            
        except Exception as e:
            logger.error(f"Error integrating knowledge: {e}")
    
    def get_knowledge_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        return self.knowledge_graph.get_entity_statistics()