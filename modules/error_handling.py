"""
Common error handling utilities and decorators

This module provides standardized error handling patterns to reduce
code duplication across the application.
"""

import json
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union
import logging

# Configure logging for error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_json_response(func: Callable) -> Callable:
    """
    Decorator to safely handle JSON responses for MCP tools
    
    Automatically handles exceptions and returns properly formatted JSON responses
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> str:
        try:
            result = func(*args, **kwargs)
            if isinstance(result, str):
                return result
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, indent=2)
    return wrapper


def safe_operation(operation_name: str = "operation"):
    """
    Decorator for safe operation handling with custom operation names
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"Error during {operation_name}: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg) from e
        return wrapper
    return decorator


def handle_import_error(module_name: str, fallback_value: Any = None):
    """
    Standard import error handler
    
    Args:
        module_name: Name of the module being imported
        fallback_value: Value to return if import fails
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ImportError as e:
                logger.warning(f"⚠️ {module_name} not available: {e}")
                if fallback_value is not None:
                    return fallback_value
                raise
        return wrapper
    return decorator


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_json_structure(data: Dict[str, Any], required_fields: list) -> list:
    """
    Validate JSON structure and return list of issues
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    for field in required_fields:
        if field not in data:
            issues.append(f"Missing required field: {field}")
        elif data[field] is None:
            issues.append(f"Null value for required field: {field}")
        elif isinstance(data[field], str) and not data[field].strip():
            issues.append(f"Empty string for required field: {field}")
        elif isinstance(data[field], list) and len(data[field]) == 0:
            # Allow empty lists for some fields like work_items
            continue
    
    return issues


def safe_file_operation(operation: str):
    """
    Decorator for safe file operations
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                error_msg = f"File not found during {operation}: {str(e)}"
                logger.error(error_msg)
                return {"error": error_msg}
            except PermissionError as e:
                error_msg = f"Permission denied during {operation}: {str(e)}"
                logger.error(error_msg)
                return {"error": error_msg}
            except Exception as e:
                error_msg = f"Unexpected error during {operation}: {str(e)}"
                logger.error(error_msg)
                return {"error": error_msg}
        return wrapper
    return decorator


def standardize_error_response(error: Exception, context: str = "") -> Dict[str, str]:
    """
    Create standardized error response dictionary
    
    Args:
        error: Exception that occurred
        context: Additional context about where the error occurred
        
    Returns:
        Standardized error response dictionary
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    response = {
        "error": True,
        "error_type": error_type,
        "message": error_msg
    }
    
    if context:
        response["context"] = context
        
    logger.error(f"{context}: {error_type} - {error_msg}")
    return response


def retry_operation(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry operations with exponential backoff
    """
    import time
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed")
            
            raise last_exception
        return wrapper
    return decorator
