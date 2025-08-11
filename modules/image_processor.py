"""
Image Processing Module using Azure OpenAI

This module provides image analysis capabilities using Azure OpenAI's vision models
to extract project requirements and generate ADO work items from visual content.
"""

import base64
import os
import json
from typing import Dict, List, Optional, Tuple
from openai import AzureOpenAI
from pathlib import Path

from .models import WorkItem, WorkItemType, Priority, ADOInstructions, ORGANIZATION_CONTEXT
from .error_handling import safe_operation, ValidationError, standardize_error_response
from .common_utils import clean_text, safe_json_dumps
from .text_processor import determine_priority_from_text
from .display_utils import print_ado_summary, get_quick_stats


def get_azure_openai_client() -> Optional[AzureOpenAI]:
    """
    Initialize Azure OpenAI client with environment configuration
    
    Returns:
        AzureOpenAI client instance or None if configuration is missing
    """
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        if not endpoint or not api_key:
            print("⚠️ Azure OpenAI configuration missing. Image processing will be unavailable.")
            return None
            
        client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=api_key,
        )
        
        print("✅ Azure OpenAI client initialized successfully")
        return client
        
    except Exception as e:
        print(f"❌ Failed to initialize Azure OpenAI client: {e}")
        return None


def load_image_as_base64(image_path: str) -> str:
    """
    Load an image file and convert it to base64 format
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded image data
        
    Raises:
        ValidationError: If image file cannot be loaded
    """
    try:
        if not os.path.exists(image_path):
            raise ValidationError(f"Image file not found: {image_path}")
            
        # Check file extension
        supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        file_ext = Path(image_path).suffix.lower()
        
        if file_ext not in supported_extensions:
            raise ValidationError(f"Unsupported image format: {file_ext}. Supported: {supported_extensions}")
            
        # Check file size (limit to 10MB)
        file_size = os.path.getsize(image_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise ValidationError(f"Image file too large: {file_size / (1024*1024):.1f}MB. Maximum: 10MB")
            
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
        print(f"✅ Image loaded successfully: {Path(image_path).name} ({file_size / 1024:.1f}KB)")
        return base64_image
        
    except Exception as e:
        raise ValidationError(f"Failed to load image: {str(e)}")


def analyze_image_with_azure_openai(image_base64: str, description: str = "") -> Dict:
    """
    Analyze an image using Azure OpenAI vision capabilities
    
    Args:
        image_base64: Base64 encoded image data
        description: Optional description or context about the image
        
    Returns:
        Dictionary containing analysis results and extracted features
        
    Raises:
        ValidationError: If analysis fails or Azure OpenAI is unavailable
    """
    client = get_azure_openai_client()
    if not client:
        raise ValidationError("Azure OpenAI client not available. Check configuration.")
        
    try:
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "o4-mini-imagebot")
        
        # Create system prompt for ADO work item extraction with dependency analysis
        system_prompt = """You are an expert at analyzing workflow diagrams and visual project documentation to extract software requirements and generate Azure DevOps work items with proper dependency relationships.

**CRITICAL: Workflow Arrow Analysis Instructions**
1. **Identify arrows and connectors** in the image (→, ←, ↓, ↑, lines with direction)
2. **Follow dependency flow** - arrows indicate parent → child relationships in work item hierarchy
3. **Create single Epic structure** - the workflow starting point becomes the main Epic
4. **Map sequential tasks** - each step connected by arrows becomes a Task under the Epic
5. **Preserve workflow order** - maintain the sequence shown by arrows

**Example Analysis:**
- Visual: [Database] → [Website] → [Frontend]
- Result: Epic "Database Implementation" with Tasks: "Build Website", "Develop Frontend"

Your task is to:
1. Analyze the image for workflow arrows and dependency chains
2. Identify the main workflow starting point (becomes Epic)
3. Extract sequential steps connected by arrows (become Tasks)
4. Preserve hierarchical relationships shown visually
5. Generate ONE Epic with connected Tasks, not multiple separate Epics

Return your analysis as a JSON object with this structure:
{
  "project_name": "Project name based on main workflow",
  "workflow_analysis": {
    "arrows_detected": true/false,
    "main_workflow_start": "Starting element of the workflow",
    "dependency_sequence": ["step1", "step2", "step3"],
    "flow_direction": "left-to-right|top-to-bottom|other"
  },
  "features": [
    {
      "name": "Main Epic based on workflow root",
      "description": "Epic description covering the entire workflow",
      "priority": "High|Medium|Low",
      "is_main_epic": true,
      "requirements": [
        {
          "title": "Task title",
          "description": "Task description",
          "priority": "High|Medium|Low"
        }
      ]
    }
  ],
  "analysis_notes": "Additional observations about the image"
}

Focus on extracting actionable software development tasks, UI components, features, and technical requirements."""

        # Create user prompt with description context emphasizing dependency analysis
        user_prompt = f"""Analyze this workflow diagram/image with SPECIAL FOCUS on arrows and dependency relationships.

{f'Additional context: {description}' if description else 'No additional context provided.'}

**PRIORITY ANALYSIS TASKS:**
1. **Look for arrows/connectors** - identify direction and flow (→, ←, ↓, ↑, lines)
2. **Map dependency chain** - follow arrows to understand sequence
3. **Identify workflow root** - the starting point becomes the main Epic
4. **Extract sequential steps** - each connected element becomes a Task

**What to identify:**
- Arrows and flow direction in the diagram
- Starting element of the workflow (Epic candidate)
- Sequential steps connected by arrows (Task candidates)  
- Dependency relationships shown visually
- Workflow sequence and hierarchy

**IMPORTANT:** Create ONE Epic from the workflow root and Tasks for connected steps. Do NOT create multiple separate Epics unless there are clearly parallel workflows.

Return the analysis as structured JSON focusing on the workflow hierarchy."""

        # Make the API call
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_completion_tokens=40000,
            model=deployment
            # Note: o4-mini-imagebot only supports default temperature (1.0)
        )
        
        # Extract and parse the response
        content = response.choices[0].message.content
        
        # Try to extract JSON from the response
        try:
            # Look for JSON in the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis_result = json.loads(json_match.group())
            else:
                # Fallback: create structured response from text
                analysis_result = {
                    "project_name": "Analyzed Project",
                    "features": [
                        {
                            "name": "Image Analysis Result",
                            "description": clean_text(content),
                            "priority": "Medium",
                            "requirements": [
                                {
                                    "title": "Implement analyzed features",
                                    "description": "Based on image analysis findings",
                                    "priority": "Medium"
                                }
                            ]
                        }
                    ],
                    "analysis_notes": "Azure OpenAI analysis completed"
                }
                
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            analysis_result = {
                "project_name": "Image Analysis Project",
                "features": [
                    {
                        "name": "Visual Requirements",
                        "description": clean_text(content[:500]) + "..." if len(content) > 500 else clean_text(content),
                        "priority": "Medium",
                        "requirements": [
                            {
                                "title": "Implement visual requirements",
                                "description": "Based on image analysis",
                                "priority": "Medium"
                            }
                        ]
                    }
                ],
                "analysis_notes": f"Analysis completed. Response length: {len(content)} characters"
            }
        
        print(f"✅ Azure OpenAI image analysis completed")
        print(f"📊 Identified {len(analysis_result.get('features', []))} features")
        
        return analysis_result
        
    except Exception as e:
        raise ValidationError(f"Azure OpenAI image analysis failed: {str(e)}")


def extract_features_from_image(image_base64: str, description: str = "") -> List[Dict]:
    """
    Extract project features from image using Azure OpenAI
    
    Args:
        image_base64: Base64 encoded image data
        description: Optional description context
        
    Returns:
        List of features extracted from the image
    """
    try:
        analysis = analyze_image_with_azure_openai(image_base64, description)
        features = analysis.get('features', [])
        
        # Enhance features with better priority detection
        for feature in features:
            if 'requirements' in feature:
                for req in feature['requirements']:
                    if req.get('priority') == 'Medium':  # Default, try to improve
                        improved_priority = determine_priority_from_text(req.get('description', ''))
                        if improved_priority != Priority.MEDIUM:
                            req['priority'] = improved_priority.value
                            
        return features
        
    except Exception as e:
        print(f"⚠️ Feature extraction failed: {e}")
        return []


def process_image_with_azure_openai(image_base64: str, description: str = "") -> ADOInstructions:
    """
    Process an image using Azure OpenAI vision capabilities and generate ADO work items with dependency analysis.
    
    This function analyzes workflow diagrams, wireframes, and project visuals to:
    1. Detect dependency arrows and workflow sequences
    2. Create proper Epic → Task hierarchies 
    3. Generate structured ADO work items
    4. Display comprehensive summaries
    
    Args:
        image_base64: Base64 encoded image data
        description: Optional description or context about the image
        
    Returns:
        ADOInstructions object containing structured work items
        
    Example Output Structure:
        📋 ADO Work Items Summary - Website Development Workflow
        ================================================================================
        📊 Structure: 1 Epic → 3 Tasks (✅ Proper dependency chain detected!)
        
        🎯 Epic 1: "Build a website"
           Priority: High | Tags: workflow, dependency-chain, epic
           Description: Epic to deliver a complete website solution...
           
           📋 Tasks (3):
           ├── 1. Build database [High Priority]
           │   └── Tags: workflow-step, dependency-task, step-1
           ├── 2. Develop Front end [Medium Priority] 
           │   └── Tags: workflow-step, dependency-task, step-2
           └── 3. Develop Backend [High Priority]
               └── Tags: workflow-step, dependency-task, step-3
        
        🔗 Workflow Sequence: Build database → Develop Front end → Develop Backend
        ✅ SUCCESS: Proper dependency structure (1 Epic with dependent tasks)
        
    Raises:
        ValidationError: If image processing fails or Azure OpenAI is unavailable
    """
    try:
        # Get analysis from Azure OpenAI with dependency parsing
        analysis = analyze_image_with_azure_openai(image_base64, description)
        
        project_name = analysis.get('project_name', 'Workflow Analysis Project')
        features = analysis.get('features', [])
        workflow_analysis = analysis.get('workflow_analysis', {})
        
        if not features:
            raise ValidationError("No features could be extracted from the image")
            
        # Create work items with proper hierarchy based on workflow analysis
        work_items = []
        main_epic = None
        
        # Look for the main epic (workflow root)
        for feature_data in features:
            is_main_epic = feature_data.get('is_main_epic', False)
            
            if is_main_epic or main_epic is None:  # Create main epic
                epic_id = f"epic_{len(work_items) + 1}"
                main_epic = WorkItem(
                    id=epic_id,
                    title=clean_text(feature_data.get('name', 'Workflow Implementation')),
                    description=clean_text(feature_data.get('description', 
                        f"Main workflow implementation based on dependency analysis. "
                        f"Flow detected: {workflow_analysis.get('flow_direction', 'sequential')}. "
                        f"Acceptance Criteria: Complete workflow implementation following visual dependency chain, "
                        f"all workflow steps properly integrated, dependencies correctly implemented in sequence.")),
                    work_item_type=WorkItemType.EPIC,
                    priority=Priority(feature_data.get('priority', 'High').title()),
                    tags=["workflow", "dependency-chain", "epic"]
                )
                work_items.append(main_epic)
                
                # Create Tasks for workflow steps (requirements)
                requirements = feature_data.get('requirements', [])
                for i, req in enumerate(requirements):
                    # Add dependency context to task description
                    task_description = clean_text(req.get('description', ''))
                    depends_on = req.get('depends_on', '')
                    if depends_on:
                        task_description += f"\n\nDependency: This task depends on completion of '{depends_on}'"
                    
                    # Include sequence information
                    sequence_info = ""
                    if workflow_analysis.get('dependency_sequence'):
                        seq = workflow_analysis['dependency_sequence']
                        if i < len(seq):
                            sequence_info = f"\nWorkflow Step {i+1} of {len(seq)}: {seq[i]}"
                    
                    task_id = f"task_{len(work_items) + 1}"
                    task = WorkItem(
                        id=task_id,
                        title=clean_text(req.get('title', f'Workflow Step {i+1}')),
                        description=task_description + sequence_info + 
                                   f"\nAcceptance Criteria: Implementation follows workflow dependencies, "
                                   f"integration with previous workflow steps is verified, "
                                   f"code is properly tested, documentation includes dependency information.",
                        work_item_type=WorkItemType.TASK,
                        priority=Priority(req.get('priority', 'Medium').title()),
                        parent_id=main_epic.id,
                        tags=["workflow-step", "dependency-task", f"step-{i+1}"]
                    )
                    work_items.append(task)
                
                # Only create one main epic from workflow analysis
                break
        
        # Create ADO instructions with workflow context
        ado_instructions = ADOInstructions(
            project_name=project_name,
            organization_context=ORGANIZATION_CONTEXT["name"],
            work_items=work_items
        )
        
        print(f"✅ Generated {len(work_items)} work items from image analysis")
        
        # Display comprehensive summary
        print_ado_summary(ado_instructions, "Azure OpenAI Image Analysis Results")
        
        return ado_instructions
        
    except Exception as e:
        raise ValidationError(f"Image processing failed: {str(e)}")


@safe_operation
def analyze_workflow_diagram(image_base64: str, description: str = "") -> Dict:
    """
    Specialized function for analyzing workflow diagrams
    
    Args:
        image_base64: Base64 encoded image data
        description: Optional description context
        
    Returns:
        Dictionary containing workflow analysis results
    """
    try:
        # Use enhanced prompt for workflow analysis
        workflow_description = f"Workflow diagram analysis: {description}" if description else "Workflow diagram showing project structure and dependencies"
        
        analysis = analyze_image_with_azure_openai(image_base64, workflow_description)
        
        # Add workflow-specific processing
        workflow_info = {
            "workflow_steps": [],
            "dependencies": [],
            "decision_points": [],
            "components": []
        }
        
        # Parse features for workflow elements
        for feature in analysis.get('features', []):
            workflow_info["components"].append({
                "name": feature.get('name'),
                "description": feature.get('description'),
                "priority": feature.get('priority', 'Medium')
            })
            
            for req in feature.get('requirements', []):
                workflow_info["workflow_steps"].append({
                    "step": req.get('title'),
                    "description": req.get('description'),
                    "priority": req.get('priority', 'Medium')
                })
        
        return {
            "analysis": analysis,
            "workflow_info": workflow_info
        }
        
    except Exception as e:
        return standardize_error_response(f"Workflow analysis failed: {str(e)}")


def format_image_analysis_result(analysis_result: Dict) -> str:
    """
    Format image analysis results for display
    
    Args:
        analysis_result: Analysis results from Azure OpenAI
        
    Returns:
        Formatted string representation
    """
    try:
        output = []
        output.append("🖼️ **Azure OpenAI Image Analysis Results**")
        output.append("=" * 50)
        
        project_name = analysis_result.get('project_name', 'Unknown Project')
        output.append(f"📋 **Project**: {project_name}")
        
        features = analysis_result.get('features', [])
        output.append(f"🔍 **Features Identified**: {len(features)}")
        output.append("")
        
        for i, feature in enumerate(features, 1):
            output.append(f"## {i}. {feature.get('name', 'Unnamed Feature')}")
            output.append(f"**Priority**: {feature.get('priority', 'Medium')}")
            output.append(f"**Description**: {feature.get('description', 'No description')}")
            
            requirements = feature.get('requirements', [])
            if requirements:
                output.append("**Requirements**:")
                for j, req in enumerate(requirements, 1):
                    output.append(f"  {j}. {req.get('title', 'Unnamed Task')} ({req.get('priority', 'Medium')})")
                    if req.get('description'):
                        output.append(f"     {req.get('description')}")
            output.append("")
        
        if analysis_result.get('analysis_notes'):
            output.append("📝 **Analysis Notes**:")
            output.append(analysis_result['analysis_notes'])
        
        return "\n".join(output)
        
    except Exception as e:
        return f"Error formatting analysis results: {str(e)}"


# Utility functions for image processing
def validate_image_format(image_path: str) -> bool:
    """Check if image format is supported"""
    supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    return Path(image_path).suffix.lower() in supported_extensions


def get_image_info(image_path: str) -> Dict:
    """Get basic information about an image file"""
    try:
        if not os.path.exists(image_path):
            return {"error": "File not found"}
            
        stat = os.stat(image_path)
        return {
            "path": image_path,
            "name": Path(image_path).name,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "extension": Path(image_path).suffix.lower(),
            "supported": validate_image_format(image_path)
        }
    except Exception as e:
        return {"error": str(e)}
