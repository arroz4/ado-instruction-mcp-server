"""
Common utility functions used across multiple modules

This module contains shared utility functions to reduce code duplication
and provide consistent functionality across the application.
"""

import json
import re
from typing import Any, Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize text input
    
    Args:
        text: Raw text input
        
    Returns:
        Cleaned and normalized text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line endings
    text = re.sub(r'\s+', ' ', text.strip())
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text


def extract_action_from_text(text: str) -> Optional[str]:
    """
    Extract action words from text using common patterns
    
    Args:
        text: Text to analyze
        
    Returns:
        Extracted action or None if not found
    """
    action_patterns = [
        r'\b(build|create|develop|implement|setup|configure)\b',
        r'\b(want to|need to|should|must)\s+(\w+)',
        r'\b(design|analyze|test|deploy|monitor)\b'
    ]
    
    for pattern in action_patterns:
        match = re.search(pattern, text.lower())
        if match:
            if len(match.groups()) > 1:
                return match.group(2)  # Return the action word after "want to", etc.
            else:
                return match.group(1)  # Return the direct action word
    
    return None


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    Safely serialize data to JSON string with fallback
    
    Args:
        data: Data to serialize
        default: Default string if serialization fails
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        return default
