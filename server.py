"""
ADO Instructions MCP Server - Text and Image Processing with Azure OpenAI

A Model Context Protocol (MCP) server that generates Azure DevOps work item instructions
from text input and images. Features advanced workflow diagram analysis with dependency 
arrow parsing to create proper Epic → Task hierarchies from visual documentation.

🆕 DEPENDENCY ARROW ANALYSIS:
- Identifies arrows and flow direction in workflow diagrams
- Creates ONE Epic from workflow root with Tasks for connected steps
- Preserves dependency relationships shown by visual arrows
- Supports patterns like: [Database] → [Website] → [Frontend]
"""

import argparse
import json
import fastmcp
from pathlib import Path
import base64

# Import modules
from modules.config import setup_environment, get_organization_context, get_azure_openai_config
from modules.text_processor import extract_features_from_text, extract_requirements_from_text, determine_priority_from_text
from modules.image_processor import process_image_with_azure_openai, load_image_as_base64, get_azure_openai_client, format_image_analysis_result
from modules.ado_generator import generate_ado_instructions, format_ado_summary, create_epic_from_feature, create_task_from_requirement
from modules.file_search import search_files_for_processing, format_search_results_for_display, get_search_usage_examples
from modules.error_handling import safe_json_response, safe_operation, handle_import_error, validate_json_structure, safe_file_operation, standardize_error_response, retry_operation, ValidationError
from modules.common_utils import safe_json_dumps, clean_text
from modules.models import WorkItem, WorkItemType, Priority, ADOInstructions, ORGANIZATION_CONTEXT
from modules.display_utils import print_ado_summary, get_quick_stats


def process_text_input(text: str, project_name: str = "Text Analysis Project") -> dict:
    """
    Process text input and generate ADO work items
    
    Args:
        text: Input text content
        project_name: Optional project name
        
    Returns:
        Dictionary containing ADO instructions
    """
    features = extract_features_from_text(text)
    instructions = generate_ado_instructions(
        text_input=text,
        project_name=project_name,
        features=features
    )
    return instructions.to_dict()


# Initialize environment and MCP server
setup_environment()
mcp = fastmcp.FastMCP("ADO Instructions Server")


@mcp.tool()
@safe_json_response
def process_meeting_transcript(transcript: str) -> dict:
    """
    Process a long meeting transcript or notes to generate ADO work item instructions.
    
    Args:
        transcript: Long text from meeting transcripts, notes, or requirements documents
        
    Returns:
        JSON string containing structured ADO work item instructions
        
    Example Output Structure (displayed during processing):
        📋 Meeting Transcript Analysis Results - Sprint Planning Session
        ================================================================================
        📊 Structure: 3 Epic → 8 Tasks (Standard structure)
        
        🎯 Epic 1: "Authentication System"
           Priority: High | Tags: security, core-feature
           Description: Complete authentication and authorization system...
           
           📋 Tasks (3):
           ├── 1. Login Implementation [High Priority]
           ├── 2. Password Reset [Medium Priority]
           └── 3. Two-Factor Authentication [Medium Priority]
    """
    instructions = process_text_input(transcript, "Meeting Transcript Analysis")
    return instructions


@mcp.tool()
@safe_json_response  
def generate_ado_workitems_from_text(
    text_input: str, 
    project_name: str = "", 
    priority_override: str = ""
) -> dict:
    """
    Generate complete ADO work item hierarchy from any text input with optional overrides.
    
    Args:
        text_input: Any text input (meeting notes, requirements, user stories, etc.)
        project_name: Optional override for project name
        priority_override: Optional priority override (Low, Medium, High, Critical)
        
    Returns:
        JSON string with complete ADO work item structure (Epics and Tasks)
        
    Example Output Structure (displayed during processing):
        📋 Text Analysis Results - Customer Portal Development
        ================================================================================
        📊 Structure: 2 Epic → 5 Tasks (Standard structure)
        
        🎯 Epic 1: "User Management System"
           Priority: High | Tags: user-management, core-feature
           Description: Comprehensive user management functionality...
           
           📋 Tasks (3):
           ├── 1. User Registration [Medium Priority]
           ├── 2. Email Verification [Medium Priority]
           └── 3. Profile Management [Low Priority]
    """
    instructions = generate_ado_instructions(
        text_input=text_input,
        project_name=project_name,
        priority_override=priority_override
    )
    
    # Display summary for immediate feedback
    print_ado_summary(instructions, "Text Analysis Results")
    
    return instructions.to_dict()


@mcp.tool()
def validate_ado_structure(instructions_json: str) -> str:
    """
    Validate the structure of ADO instructions JSON.
    
    Args:
        instructions_json: JSON string containing ADO instructions
        
    Returns:
        Validation result with any issues found
        
    Example Output Structure (displayed during processing):
        📋 Validation Results - Project Setup Instructions
        ================================================================================
        📊 Structure: 2 Epic → 6 Tasks (Standard structure)
        ✅ Validation Status: All checks passed
        
        🎯 Epic 1: "Database Setup"
           Priority: High | Tags: database, infrastructure
           Description: Set up database infrastructure and schemas...
           ✅ Valid structure with 3 tasks
           
        🎯 Epic 2: "API Development"
           Priority: Medium | Tags: api, backend
           Description: Develop RESTful API endpoints...
           ✅ Valid structure with 3 tasks
    """
    try:
        data = json.loads(instructions_json)
        issues = []
        
        # Check required fields
        required_fields = ['project_name', 'epics']
        for field in required_fields:
            if field not in data:
                issues.append(f"Missing required field: {field}")
        
        # Check epics structure
        if 'epics' in data:
            for i, epic in enumerate(data['epics']):
                epic_required = ['title', 'description', 'tasks']
                for field in epic_required:
                    if field not in epic:
                        issues.append(f"Epic {i+1} missing field: {field}")
                
                # Check tasks
                if 'tasks' in epic:
                    for j, task in enumerate(epic['tasks']):
                        task_required = ['title', 'description', 'work_item_type']
                        for field in task_required:
                            if field not in task:
                                issues.append(f"Epic {i+1}, Task {j+1} missing field: {field}")
        
        if issues:
            result = {"valid": False, "issues": issues}
        else:
            result = {"valid": True, "message": "ADO structure is valid"}
            # Display summary for valid structures
            print_ado_summary(instructions_json, "Validation Results")
            
        return json.dumps(result, indent=2)
            
    except json.JSONDecodeError as e:
        return json.dumps({"valid": False, "issues": [f"Invalid JSON: {str(e)}"]}, indent=2)
    except Exception as e:
        return json.dumps({"valid": False, "issues": [f"Validation error: {str(e)}"]}, indent=2)


@mcp.tool()
def get_organization_context() -> str:
    """
    Get information about Omar Solutions organization context for work item generation.
    
    Returns:
        JSON string with organization details and focus areas
        
    Example Output Structure:
        {
          "organization": "Omar Solutions",
          "industry": "Software Development & Technology Consulting",
          "focus_areas": ["Web Development", "Cloud Solutions", "API Integration"],
          "common_projects": [
            "Web Application Development",
            "API Development and Integration", 
            "Database Design and Optimization",
            "Mobile Application Development"
          ],
          "typical_epic_categories": [
            "Frontend Development",
            "Backend API Development", 
            "Database Infrastructure",
            "Testing & Quality Assurance"
          ]
        }
    """
    context = {
        'organization': ORGANIZATION_CONTEXT['organization'],
        'industry': ORGANIZATION_CONTEXT['industry'],
        'focus_areas': ORGANIZATION_CONTEXT['focus_areas'],
        'common_projects': [
            'Web Application Development',
            'API Development and Integration',
            'Database Design and Optimization',
            'Mobile Application Development',
            'Cloud Infrastructure Setup',
            'DevOps Pipeline Implementation',
            'Security Compliance',
            'Performance Monitoring',
            'User Experience Enhancement',
            'Data Analytics and Reporting',
            'Automated Testing Framework',
            'Documentation',
            'Code Review and Optimization'
        ]
    }
    
    return json.dumps(context, indent=2)


@mcp.tool()
def format_ado_instructions_summary(instructions_json: str) -> str:
    """
    Format ADO instructions into a user-friendly summary for review and confirmation.
    
    This tool should be used after generating ADO work items to:
    1. Present a neatly formatted summary of all Epics and Tasks
    2. Show project structure and work item relationships  
    3. Prompt user to confirm if instructions are correct
    4. Ask if any modifications are needed
    
    Args:
        instructions_json: JSON string containing ADO instructions
        
    Returns:
        Formatted summary with confirmation prompts
        
    Example Output Structure (displayed during processing):
        📋 ADO Instructions Summary - E-commerce Platform Development
        ================================================================================
        📊 Structure: 4 Epic → 12 Tasks (Standard structure)
        
        🎯 Epic 1: "Frontend Development"
           Priority: High | Tags: frontend, react, user-interface
           Description: Build responsive user interface with React...
           
           📋 Tasks (4):
           ├── 1. Setup React Project [High Priority]
           ├── 2. Create Header Component [Medium Priority]
           ├── 3. Product Listing Page [High Priority]
           └── 4. Shopping Cart Component [Medium Priority]
           
        🎯 Epic 2: "Backend API Development"
           Priority: High | Tags: backend, api, database
           Description: Implement RESTful API with authentication...
           
           📋 Tasks (3):
           ├── 1. Database Schema Design [High Priority]
           ├── 2. User Authentication API [High Priority]
           └── 3. Product Management API [Medium Priority]
    """
    try:
        # Use display utility to print formatted summary
        print_ado_summary(instructions_json, "ADO Instructions Summary")
        
        # Also return formatted summary
        data = json.loads(instructions_json)
        summary = format_ado_summary(data)
        return summary
        
    except json.JSONDecodeError as e:
        return f"❌ Error parsing JSON: {str(e)}"
    except Exception as e:
        return f"❌ Error formatting summary: {str(e)}"


@mcp.tool()
def search_files_for_processing(
    search_pattern: str = "", 
    file_types: str = "images,text", 
    search_locations: str = "desktop,documents,downloads"
) -> str:
    """
    Search for image or text files on the PC that can be processed by the ADO system.
    
    This tool helps users locate files for processing without knowing exact paths.
    Searches common locations and returns a list of matching files with their full paths.
    
    Args:
        search_pattern: Optional filename pattern to search for (e.g., "wireframe", "meeting", "*.png")
        file_types: File types to search for. Options: "images", "text", "all" (default: "images,text")
        search_locations: Locations to search. Options: "desktop", "documents", "downloads", "pictures", "current", "all" (default: "desktop,documents,downloads")
        
    Returns:
        JSON string with found files categorized by type and location
        
    Example Output Structure:
        {
          "search_summary": "Found 8 files matching pattern 'wireframe' in desktop,documents",
          "found_files": [
            {
              "file_path": "C:\\Users\\user\\Desktop\\wireframe_v1.png",
              "file_type": "image",
              "location": "desktop",
              "file_size": "245KB"
            },
            {
              "file_path": "C:\\Users\\user\\Documents\\meeting_notes.txt",
              "file_type": "text",
              "location": "documents", 
              "file_size": "12KB"
            }
          ]
        }
    """
    try:
        results = search_files_for_processing(search_pattern, file_types, search_locations)
        
        # If results are extensive, provide a summary
        if len(results.get('found_files', [])) > 20:
            return json.dumps({
                'search_summary': results['search_summary'],
                'total_files': len(results['found_files']),
                'first_10_files': results['found_files'][:10],
                'suggestions': [
                    'Use a more specific search pattern to narrow results',
                    'Try searching in specific locations only',
                    'Use "all" for file_types or search_locations to expand search'
                ],
                'search_summary': results['search_summary']
            }, indent=2)
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        return json.dumps({
            'error': f'Error searching files: {str(e)}',
            'search_pattern': search_pattern,
            'file_types': file_types,
            'search_locations': search_locations
        }, indent=2)


@mcp.tool()
@safe_json_response  
def process_feature_image(image_base64: str, description: str = "") -> dict:
    """
    Process an image (wireframe, diagram, sketch) to generate ADO work item instructions using Azure OpenAI.

    Supports analysis of various visual materials with dependency arrow detection:
    - UI/UX wireframes and mockups (PNG, JPG, WebP)
    - System architecture diagrams (any supported format)
    - Hand-drawn sketches or whiteboard photos (JPG, PNG)
    - Screenshots of existing interfaces (PNG, JPG)
    - Technical diagrams and flowcharts (PNG, GIF, BMP)
    - Workflow diagrams with dependency arrows (→, ←, ↓, ↑)

    Args:
        image_base64: Base64 encoded image data (use load_image_from_file to convert files)
        description: Optional description or context about the image to enhance analysis
        
    Returns:
        JSON string containing structured ADO work item instructions with Epics and Tasks
        
    Example Output Structure (displayed during processing):
        📋 Azure OpenAI Image Analysis Results - Website Development Project
        ================================================================================
        📊 Structure: 1 Epic → 3 Tasks (✅ Proper dependency chain detected!)
        
        🎯 Epic 1: "Build a website"
           Priority: High | Tags: workflow, dependency-chain, epic
           Description: Epic to deliver a complete website solution...
           
           📋 Tasks (3):
           ├── 1. Build database [High Priority]
           │   └── Tags: workflow-step, dependency-task, step-1
           ├── 2. Develop Frontend [Medium Priority]
           │   └── Tags: workflow-step, dependency-task, step-2
           └── 3. Develop Backend [High Priority]
               └── Tags: workflow-step, dependency-task, step-3
        
        🔗 Workflow Sequence: Build database → Develop Frontend → Develop Backend
        ✅ SUCCESS: Proper dependency structure (1 Epic with dependent tasks)
    """
    try:
        # Check if Azure OpenAI is available
        client = get_azure_openai_client()
        if not client:
            return {
                "error": "Azure OpenAI not configured. Please check your .env file configuration.",
                "fallback": "Use text-based tools for processing requirements."
            }
            
        # Process image with Azure OpenAI
        ado_instructions = process_image_with_azure_openai(image_base64, description)
        
        return ado_instructions.to_dict()
        
    except ValidationError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Image processing failed: {str(e)}"}


@mcp.tool()
def load_image_from_file(image_path: str) -> str:
    """
    Load an image file and convert it to base64 for analysis.

    Args:
        image_path: Path to the image file (absolute path recommended)
        
    Returns:
        Base64 encoded image data or error message
        
    Example Output Structure:
        {
          "success": true,
          "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...[base64 data]",
          "image_path": "C:\\Users\\user\\Documents\\wireframe.png",
          "file_size": "245KB",
          "image_format": "PNG"
        }
    """
    try:
        if not image_path:
            return json.dumps({"error": "Image path is required"})
            
        # Convert to absolute path
        image_path = str(Path(image_path).resolve())
        
        # Load and convert image
        base64_data = load_image_as_base64(image_path)
        
        return json.dumps({
            "success": True,
            "image_base64": base64_data,
            "image_path": image_path,
            "message": f"Image loaded successfully: {Path(image_path).name}"
        })
        
    except ValidationError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"Failed to load image: {str(e)}"})


if __name__ == "__main__":
    # Run the MCP server with HTTP transport
    parser = argparse.ArgumentParser(description="ADO Instructions MCP Server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="http", 
                       help="Transport protocol (default: http)")
    parser.add_argument("--port", type=int, default=2000, 
                       help="Port for HTTP transport (default: 2000)")
    parser.add_argument("--host", default="localhost", 
                       help="Host for HTTP transport (default: localhost)")
    
    args = parser.parse_args()
    
    if args.transport == "http":
        print(f"🚀 Starting ADO Instructions MCP Server on http://{args.host}:{args.port}")
        print("�️ Text and Image Processing with Azure OpenAI")
        print("\nAvailable tools:")
        print("   - process_meeting_transcript") 
        print("   - process_feature_image (🆕 Azure OpenAI)")
        print("   - generate_ado_workitems_from_text")
        print("   - validate_ado_structure")
        print("   - format_ado_instructions_summary")
        print("   - search_files_for_processing")
        print("   - get_organization_context")
        print("   - load_image_from_file (🆕)")
        
        # Check Azure OpenAI configuration
        config = get_azure_openai_config()
        if config.get('endpoint') and config.get('api_key'):
            print("✅ Azure OpenAI configured - Image processing available")
        else:
            print("⚠️ Azure OpenAI not configured - Text processing only")
        
        import uvicorn
        app = mcp.http_app()
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        print("📝 Starting ADO Instructions MCP Server with stdio transport")
        mcp.run()
