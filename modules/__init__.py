"""
Modular components for the ADO Instructions MCP Server

This package contains focused modules for different aspects of the system:
- models: Data structures and enums
- config: Environment and configuration management
- text_processor: Text analysis and feature extraction
- image_processor: Azure OpenAI image analysis
- ado_generator: Work item generation and formatting
- file_search: File discovery and search functionality
- error_handling: Common error handling patterns and decorators
- common_utils: Shared utility functions
- display_utils: Summary display utilities
"""

from .models import WorkItem, WorkItemType, Priority, ADOInstructions, ORGANIZATION_CONTEXT
from .config import setup_environment, get_organization_context, get_azure_openai_config
from .text_processor import extract_features_from_text, extract_requirements_from_text, determine_priority_from_text
from .image_processor import process_image_with_azure_openai, load_image_as_base64, get_azure_openai_client, format_image_analysis_result
from .ado_generator import generate_ado_instructions, format_ado_summary, create_epic_from_feature, create_task_from_requirement
from .file_search import search_files_for_processing, format_search_results_for_display, get_search_usage_examples
from .error_handling import (
    safe_json_response, safe_operation, handle_import_error, validate_json_structure,
    safe_file_operation, standardize_error_response, retry_operation, ValidationError
)
from .common_utils import clean_text, extract_action_from_text, safe_json_dumps
from .display_utils import print_ado_summary, get_quick_stats

__all__ = [
    # Models
    'WorkItem', 'WorkItemType', 'Priority', 'ADOInstructions', 'ORGANIZATION_CONTEXT',
    # Configuration
    'setup_environment', 'get_organization_context', 'get_azure_openai_config',
    # Text processing
    'extract_features_from_text', 'extract_requirements_from_text', 'determine_priority_from_text',
    # Image processing
    'process_image_with_azure_openai', 'load_image_as_base64', 'get_azure_openai_client', 'format_image_analysis_result',
    # ADO generation
    'generate_ado_instructions', 'format_ado_summary', 'create_epic_from_feature', 'create_task_from_requirement',
    # File search
    'search_files_for_processing', 'format_search_results_for_display', 'get_search_usage_examples',
    # Error handling
    'safe_json_response', 'safe_operation', 'handle_import_error', 'validate_json_structure',
    'safe_file_operation', 'standardize_error_response', 'retry_operation', 'ValidationError',
    # Common utilities
    'clean_text', 'extract_action_from_text', 'safe_json_dumps',
    # Display utilities
    'print_ado_summary', 'get_quick_stats'
]
