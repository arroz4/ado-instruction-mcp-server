"""
Utility functions for displaying ADO work item summaries
"""

import json
from typing import List, Union
from .models import WorkItem, ADOInstructions


def display_ado_summary(result: ADOInstructions, title: str = "ADO Work Items Summary") -> str:
    """
    Display a formatted summary of ADO work items showing Epic and Task hierarchy.
    
    Args:
        result: ADOInstructions object containing work items
        title: Title for the summary display
        
    Returns:
        Formatted string summary
        
    Example Output:
        📋 ADO Work Items Summary - Website Development Workflow
        ================================================================================
        📊 Structure: 1 Epic → 3 Tasks (Proper dependency chain detected!)
        
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
    """
    if not hasattr(result, 'work_items') or not result.work_items:
        return f"❌ No work items found in {title}"
    
    work_items = result.work_items
    epics = [item for item in work_items if item.work_item_type.value == 'Epic']
    tasks = [item for item in work_items if item.work_item_type.value == 'Task']
    
    # Header
    summary = f"\n📋 {title} - {result.project_name}\n"
    summary += "=" * 80 + "\n"
    
    # Quick stats
    structure_status = "✅ Proper dependency chain detected!" if len(epics) == 1 and len(tasks) > 0 else "⚠️ Non-standard structure"
    summary += f"📊 Structure: {len(epics)} Epic → {len(tasks)} Tasks ({structure_status})\n\n"
    
    # Epic details
    for i, epic in enumerate(epics, 1):
        summary += f"🎯 Epic {i}: \"{epic.title}\"\n"
        summary += f"   Priority: {epic.priority.value} | Tags: {', '.join(epic.tags)}\n"
        
        # Truncate description for readability
        desc = epic.description[:100] + "..." if len(epic.description) > 100 else epic.description
        summary += f"   Description: {desc}\n\n"
        
        # Tasks under this epic
        epic_tasks = [t for t in tasks if hasattr(t, 'parent_id') and t.parent_id == epic.id]
        
        if epic_tasks:
            summary += f"   📋 Tasks ({len(epic_tasks)}):\n"
            
            for j, task in enumerate(epic_tasks, 1):
                is_last = j == len(epic_tasks)
                connector = "└──" if is_last else "├──"
                
                summary += f"   {connector} {j}. {task.title} [{task.priority.value} Priority]\n"
                if task.tags:
                    indent = "       " if is_last else "   │   "
                    summary += f"{indent}└── Tags: {', '.join(task.tags)}\n"
    
    # Workflow sequence
    if tasks:
        summary += f"\n🔗 Workflow Sequence: {' → '.join([task.title for task in tasks])}\n"
        
        if len(epics) == 1 and len(tasks) > 1:
            summary += "✅ SUCCESS: Proper dependency structure (1 Epic with dependent tasks)\n"
        elif len(epics) > 1:
            summary += f"⚠️ WARNING: Multiple Epics ({len(epics)}) - should be 1 Epic for workflow diagrams\n"
        else:
            summary += "📋 INFO: Standard structure\n"
    
    return summary


def print_ado_summary(result: Union[ADOInstructions, str, dict], title: str = "ADO Work Items Summary"):
    """
    Print a formatted summary of ADO work items to console.
    
    Args:
        result: ADOInstructions object, JSON string, or dict containing work items
        title: Title for the summary display
    """
    # Handle different input types
    if isinstance(result, str):
        # JSON string
        try:
            data = json.loads(result)
            result = ADOInstructions.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ Error parsing JSON for summary: {e}")
            return
    elif isinstance(result, dict):
        # Dictionary
        try:
            result = ADOInstructions.from_dict(result)
        except KeyError as e:
            print(f"❌ Error creating ADOInstructions from dict: {e}")
            return
    elif not isinstance(result, ADOInstructions):
        print(f"❌ Invalid input type for summary: {type(result)}")
        return
    
    print(display_ado_summary(result, title))


def get_quick_stats(result: ADOInstructions) -> dict:
    """
    Get quick statistics about ADO work items structure.
    
    Args:
        result: ADOInstructions object containing work items
        
    Returns:
        Dictionary with structure statistics
    """
    if not hasattr(result, 'work_items') or not result.work_items:
        return {"epics": 0, "tasks": 0, "is_proper_structure": False, "status": "No work items"}
    
    work_items = result.work_items
    epics = [item for item in work_items if item.work_item_type.value == 'Epic']
    tasks = [item for item in work_items if item.work_item_type.value == 'Task']
    
    is_proper_structure = len(epics) == 1 and len(tasks) > 0
    
    if is_proper_structure:
        status = "Proper dependency structure"
    elif len(epics) > 1:
        status = f"Multiple Epics ({len(epics)}) detected"
    else:
        status = "Standard structure"
    
    return {
        "epics": len(epics),
        "tasks": len(tasks),
        "total_items": len(work_items),
        "is_proper_structure": is_proper_structure,
        "status": status,
        "project_name": result.project_name
    }
