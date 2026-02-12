#!/usr/bin/env python3
"""
Memory Domains - Classification system for holographic memory
=============================================================

Defines the semantic domains used by the holographic memory system
for content classification and associative recall.
"""

from typing import List, Dict, Any

# Core memory domains for holographic classification
MEMORY_DOMAINS: List[str] = [
    'technical_architecture',      # API design, system architecture, infrastructure
    'user_requirements',          # User needs, feature requests, use cases
    'implementation_patterns',    # Code patterns, algorithms, solutions
    'error_solutions',           # Bug fixes, debugging, error handling
    'performance_optimizations',  # Speed, efficiency, optimization techniques
    'security_practices',         # Authentication, encryption, security measures
    'testing_strategies',         # Testing approaches, validation methods
    'deployment_processes',       # Deployment, CI/CD, production management
    'documentation_patterns',     # Documentation, guides, tutorials
    'collaboration_history'       # Team interactions, meetings, discussions
]

# Domain-specific keywords for classification
DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    'technical_architecture': [
        'api', 'database', 'server', 'architecture', 'system', 'infrastructure',
        'backend', 'frontend', 'microservice', 'scalability', 'design'
    ],
    'user_requirements': [
        'user', 'requirement', 'need', 'feature', 'functionality', 'use case',
        'stakeholder', 'customer', 'client', 'experience', 'interface'
    ],
    'implementation_patterns': [
        'pattern', 'implementation', 'code', 'algorithm', 'solution',
        'design pattern', 'architecture pattern', 'best practice'
    ],
    'error_solutions': [
        'error', 'bug', 'fix', 'solution', 'debug', 'issue', 'problem',
        'exception', 'crash', 'failure', 'troubleshoot'
    ],
    'performance_optimizations': [
        'performance', 'optimization', 'speed', 'efficiency', 'optimization',
        'bottleneck', 'latency', 'throughput', 'memory', 'cpu'
    ],
    'security_practices': [
        'security', 'auth', 'authentication', 'encryption', 'vulnerability',
        'protection', 'access', 'authorization', 'threat', 'risk'
    ],
    'testing_strategies': [
        'test', 'testing', 'validation', 'quality', 'coverage',
        'unit test', 'integration', 'qa', 'verification'
    ],
    'deployment_processes': [
        'deploy', 'deployment', 'production', 'release', 'ci/cd',
        'pipeline', 'staging', 'environment', 'rollout'
    ],
    'documentation_patterns': [
        'docs', 'documentation', 'readme', 'guide', 'tutorial',
        'manual', 'reference', 'api docs', 'user guide'
    ],
    'collaboration_history': [
        'meeting', 'discussion', 'collaboration', 'team', 'communication',
        'sync', 'review', 'feedback', 'stakeholder', 'alignment'
    ]
}

# Domain relationships for associative connections
DOMAIN_RELATIONSHIPS: Dict[str, List[str]] = {
    'technical_architecture': ['implementation_patterns', 'deployment_processes', 'performance_optimizations'],
    'user_requirements': ['implementation_patterns', 'testing_strategies', 'documentation_patterns'],
    'implementation_patterns': ['technical_architecture', 'error_solutions', 'performance_optimizations'],
    'error_solutions': ['implementation_patterns', 'testing_strategies', 'performance_optimizations'],
    'performance_optimizations': ['technical_architecture', 'implementation_patterns', 'deployment_processes'],
    'security_practices': ['technical_architecture', 'deployment_processes', 'testing_strategies'],
    'testing_strategies': ['implementation_patterns', 'error_solutions', 'deployment_processes'],
    'deployment_processes': ['technical_architecture', 'testing_strategies', 'performance_optimizations'],
    'documentation_patterns': ['user_requirements', 'implementation_patterns', 'collaboration_history'],
    'collaboration_history': ['user_requirements', 'documentation_patterns', 'deployment_processes']
}

def classify_content_domain(content: str, primary_keywords: List[str] = None) -> str:
    """
    Classify content into the most appropriate memory domain.
    
    Args:
        content: Text content to classify
        primary_keywords: Optional list of important keywords to boost
        
    Returns:
        Best matching domain name
    """
    content_lower = content.lower()
    scores = {}
    
    for domain, keywords in DOMAIN_KEYWORDS.items():
        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword in content_lower)
        
        # Boost for primary keywords if provided
        if primary_keywords:
            primary_matches = sum(1 for keyword in primary_keywords 
                                if keyword.lower() in content_lower)
            matches += primary_matches * 2  # Double weight for primary keywords
        
        # Normalize by keyword count
        scores[domain] = matches / len(keywords) if keywords else 0
    
    # Return domain with highest score
    return max(scores.items(), key=lambda x: x[1])[0] if scores else 'implementation_patterns'

def get_related_domains(domain: str) -> List[str]:
    """
    Get domains related to the specified domain.
    
    Args:
        domain: Domain name to find relations for
        
    Returns:
        List of related domain names
    """
    return DOMAIN_RELATIONSHIPS.get(domain, [])

def get_domain_keywords(domain: str) -> List[str]:
    """
    Get keywords associated with a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        List of keywords for the domain
    """
    return DOMAIN_KEYWORDS.get(domain, [])

# Domain metadata for enhanced classification
DOMAIN_METADATA: Dict[str, Dict[str, Any]] = {
    'technical_architecture': {
        'description': 'System design, API structures, and infrastructure decisions',
        'importance': 'high',
        'frequency': 'medium'
    },
    'user_requirements': {
        'description': 'User needs, feature requests, and stakeholder requirements',
        'importance': 'high',
        'frequency': 'high'
    },
    'implementation_patterns': {
        'description': 'Code patterns, algorithms, and implementation approaches',
        'importance': 'medium',
        'frequency': 'high'
    },
    'error_solutions': {
        'description': 'Bug fixes, debugging approaches, and error handling',
        'importance': 'medium',
        'frequency': 'high'
    },
    'performance_optimizations': {
        'description': 'Performance improvements and optimization techniques',
        'importance': 'medium',
        'frequency': 'medium'
    },
    'security_practices': {
        'description': 'Security measures, authentication, and threat mitigation',
        'importance': 'high',
        'frequency': 'medium'
    },
    'testing_strategies': {
        'description': 'Testing approaches, quality assurance, and validation',
        'importance': 'medium',
        'frequency': 'medium'
    },
    'deployment_processes': {
        'description': 'Deployment procedures, CI/CD, and production management',
        'importance': 'medium',
        'frequency': 'low'
    },
    'documentation_patterns': {
        'description': 'Documentation creation, guides, and knowledge sharing',
        'importance': 'low',
        'frequency': 'medium'
    },
    'collaboration_history': {
        'description': 'Team discussions, meetings, and collaborative decisions',
        'importance': 'low',
        'frequency': 'high'
    }
}

print("🧠 Memory domains initialized for holographic classification!")
