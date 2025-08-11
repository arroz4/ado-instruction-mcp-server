"""
Text processing and feature extraction for ADO Instructions

This module handles text analysis, feature extraction, and requirement parsing
from various text inputs like meeting transcripts and user requirements.
"""

from typing import List, Dict, Any
from .common_utils import clean_text, extract_action_from_text


def extract_features_from_text(text: str) -> List[str]:
    """Extract main features from text input"""
    
    # Use common utility to clean text
    text = clean_text(text)
    if not text:
        return []
    
    features = []
    text_lower = text.lower()
    
    # Common project/feature keywords
    project_keywords = {
        'chatbot': 'Chatbot Development',
        'bot': 'Bot Development', 
        'chat': 'Chat System',
        'dashboard': 'Dashboard',
        'report': 'Reporting',
        'analytics': 'Analytics',
        'data pipeline': 'Data Pipeline',
        'visualization': 'Data Visualization',
        'api': 'API Development',
        'integration': 'System Integration',
        'authentication': 'Authentication',
        'database': 'Database',
        'etl': 'ETL Pipeline',
        'website': 'Website Development',
        'web app': 'Web Application',
        'mobile app': 'Mobile Application',
        'ai': 'AI/ML System',
        'machine learning': 'Machine Learning',
        'llm': 'LLM Integration'
    }
    
    # Check for project keywords
    for keyword, feature_name in project_keywords.items():
        if keyword in text_lower:
            features.append(feature_name)
    
    # Extract action-based features from sentences
    sentences = text.replace('.', '|').replace('!', '|').replace('?', '|').split('|')
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Use common utility to extract actions
        action = extract_action_from_text(sentence)
        if action:
            # Extract what comes after the action
            sentence_lower = sentence.lower()
            for pattern in ['build', 'create', 'develop', 'implement', 'need']:
                if pattern in sentence_lower:
                    remaining = sentence_lower.split(pattern, 1)
                    if len(remaining) > 1:
                        target = remaining[1].strip()
                        if target:
                            features.append(f"{action.title()} {target.title()}")
                            break
        
        # If sentence contains project-relevant terms, include it as a feature
        if any(word in sentence.lower() for word in ['database', 'llm', 'website', 'api', 'server', 'frontend', 'backend']):
            features.append(sentence.strip())
    
    # Remove duplicates while preserving order
    unique_features = []
    for feature in features:
        if feature not in unique_features:
            unique_features.append(feature)
    
    return unique_features


def extract_requirements_from_text(text: str) -> List[str]:
    """Extract specific requirements from text input"""
    text = clean_text(text)
    requirements = []
    sentences = text.split('.')
    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(keyword in sentence.lower() for keyword in ['must', 'should', 'require', 'need to', 'shall']):
            requirements.append(sentence)
    
    return requirements


def determine_priority_from_text(feature: str) -> int:
    """Determine priority based on feature type and business context"""
    feature = clean_text(feature)
    feature_lower = feature.lower()
    
    # High priority features
    if any(keyword in feature_lower for keyword in ['security', 'authentication', 'data', 'database']):
        return 3
    
    # Medium priority (default for most features)
    return 2


def detect_dependency_chain(text: str) -> Dict[str, Any]:
    """
    Detect if text describes a dependency chain workflow (A → B → C pattern)
    
    Based on ChatGPT methodology for analyzing workflow diagrams:
    1. Extract concepts/nodes from the text
    2. Identify relationships/arrows between concepts
    3. Determine if it forms a sequential workflow
    
    Returns:
        Dict containing:
        - is_chain: bool indicating if this is a dependency chain
        - root_concept: str for the Epic title
        - steps: List[str] of dependent tasks in order
    """
    import re
    
    text_clean = clean_text(text).lower()
    
    # Common dependency chain indicators - more flexible patterns
    chain_patterns = [
        r'([a-zA-Z][a-zA-Z\s]+?)\s*→\s*([a-zA-Z][a-zA-Z\s]+?)\s*→\s*([a-zA-Z][a-zA-Z\s]+)',  # A → B → C
        r'([a-zA-Z][a-zA-Z\s]+?)\s*->\s*([a-zA-Z][a-zA-Z\s]+?)\s*->\s*([a-zA-Z][a-zA-Z\s]+)',  # A -> B -> C
        r'([a-zA-Z][a-zA-Z\s]+?)\s+to\s+([a-zA-Z][a-zA-Z\s]+?)\s+to\s+([a-zA-Z][a-zA-Z\s]+)',  # A to B to C
        r'([a-zA-Z][a-zA-Z\s]+?)\s+then\s+([a-zA-Z][a-zA-Z\s]+?)\s+then\s+([a-zA-Z][a-zA-Z\s]+)',  # A then B then C
        r'([a-zA-Z][a-zA-Z\s]+?)\s+leads\s+to\s+([a-zA-Z][a-zA-Z\s]+?)\s+leads\s+to\s+([a-zA-Z][a-zA-Z\s]+)'  # A leads to B leads to C
    ]
    
    # Check for sequential workflow patterns
    for pattern in chain_patterns:
        match = re.search(pattern, text_clean)
        if match:
            steps = [step.strip().title() for step in match.groups()]
            return {
                'is_chain': True,
                'root_concept': f"{steps[0]} to {steps[-1]} Workflow",
                'steps': steps
            }
    
    # Check for common workflow keywords that indicate dependencies
    workflow_terms = ['database', 'website', 'frontend', 'backend', 'api', 'server']
    found_terms = [term for term in workflow_terms if term in text_clean]
    
    if len(found_terms) >= 2:
        # If we have multiple workflow components, treat as dependency chain
        # Order them logically: Database → Backend/API → Frontend → Website
        ordered_terms = []
        for term in ['database', 'api', 'server', 'backend', 'frontend', 'website']:
            if term in found_terms:
                ordered_terms.append(term.title())
        
        if len(ordered_terms) >= 2:
            return {
                'is_chain': True,
                'root_concept': f"{ordered_terms[0]} to {ordered_terms[-1]} System",
                'steps': ordered_terms
            }
    
    return {
        'is_chain': False,
        'root_concept': '',
        'steps': []
    }
