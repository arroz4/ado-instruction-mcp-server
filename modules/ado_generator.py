"""
ADO Work Item generation logic and business rules

This module contains the core business logic for generating Azure DevOps
work items from extracted features and requirements.
"""

from typing import List, Dict, Any
import uuid

from .models import WorkItem, ADOInstructions, WorkItemType, Priority, ORGANIZATION_CONTEXT
from .text_processor import determine_priority_from_text


def create_epic_from_feature(feature: str, project_name: str = "") -> WorkItem:
    """Create an Epic work item from a feature description"""
    
    # Generate descriptive title
    if not project_name:
        project_name = "Project"
    
    # Clean up feature name for title
    feature_clean = feature.replace("Build ", "").replace("Create ", "").replace("Develop ", "")
    title = f"Epic: {feature_clean}"
    
    # Generate description based on feature type
    description = f"""
## Epic Overview
{feature}

## Business Value
This epic delivers core functionality that aligns with our organization's focus on innovative technology solutions and digital transformation.

## Acceptance Criteria
- [ ] All related features are implemented and tested
- [ ] Solution meets performance and security requirements
- [ ] Documentation is complete and up-to-date
- [ ] User acceptance testing is completed successfully

## Dependencies
- Project infrastructure setup
- Development environment configuration
- Required third-party integrations
    """.strip()
    
    # Determine priority
    priority_level = determine_priority_from_text(feature)
    priority = Priority.HIGH if priority_level >= 3 else Priority.MEDIUM
    
    return WorkItem(
        id=str(uuid.uuid4()),
        title=title,
        work_item_type=WorkItemType.EPIC,
        description=description,
        priority=priority,
        tags=["epic", "feature", project_name.lower().replace(" ", "-")],
        parent_id=None
    )


def create_task_from_requirement(requirement: str, epic_id: str, project_name: str = "") -> WorkItem:
    """Create a Task work item from a requirement"""
    
    # Clean up requirement for title
    requirement_clean = requirement.replace("Need a ", "").replace("Need ", "").replace("Connect to ", "Connect to ")
    title = f"Task: {requirement_clean}"
    
    # Generate detailed description based on requirement type
    req_lower = requirement.lower()
    
    if "database" in req_lower:
        description = f"""
## Task Description
{requirement}

## Technical Requirements
- Choose appropriate database technology (SQL Server, PostgreSQL, MongoDB, etc.)
- Design database schema and relationships
- Implement connection pooling and configuration
- Set up database migrations and versioning
- Configure backup and recovery procedures

## Acceptance Criteria
- [ ] Database is provisioned and accessible
- [ ] Schema is implemented with proper relationships
- [ ] Connection strings are configured securely
- [ ] Basic CRUD operations are tested
- [ ] Performance benchmarks are established

## Definition of Done
- Code is reviewed and merged
- Unit tests are written and passing
- Documentation is updated
- Security review is completed
        """.strip()
        
    elif "llm" in req_lower or "ai" in req_lower:
        description = f"""
## Task Description
{requirement}

## Technical Requirements
- Select appropriate LLM provider (OpenAI, Azure OpenAI, Anthropic, etc.)
- Implement API integration and authentication
- Design prompt templates and conversation flow
- Set up rate limiting and error handling
- Implement response parsing and validation

## Acceptance Criteria
- [ ] LLM integration is functional and tested
- [ ] API keys are securely managed
- [ ] Conversation flow is implemented
- [ ] Error handling covers edge cases
- [ ] Response times meet performance requirements

## Definition of Done
- Integration tests are passing
- API documentation is complete
- Security scan shows no vulnerabilities
- Performance metrics are within acceptable range
        """.strip()
        
    elif "website" in req_lower or "frontend" in req_lower:
        description = f"""
## Task Description
{requirement}

## Technical Requirements
- Choose frontend framework (React, Angular, Vue.js, etc.)
- Design responsive UI components
- Implement routing and navigation
- Set up state management
- Configure build and deployment pipeline

## Acceptance Criteria
- [ ] Website is responsive across devices
- [ ] All core pages are implemented
- [ ] Navigation is intuitive and functional
- [ ] Performance scores meet standards
- [ ] Accessibility guidelines are followed

## Definition of Done
- UI/UX review is approved
- Cross-browser testing is completed
- Performance audit passes
- Accessibility audit passes
        """.strip()
        
    else:
        description = f"""
## Task Description
{requirement}

## Technical Requirements
- Analyze and define specific technical approach
- Identify required technologies and dependencies
- Design implementation strategy
- Consider integration points and dependencies

## Acceptance Criteria
- [ ] Requirements are clearly defined
- [ ] Technical approach is documented
- [ ] Implementation is complete and tested
- [ ] Integration points are verified

## Definition of Done
- Code review is completed
- Tests are written and passing
- Documentation is updated
        """.strip()
    
    # Determine priority
    priority_level = determine_priority_from_text(requirement)
    if priority_level >= 3:
        priority = Priority.HIGH
    elif priority_level >= 2:
        priority = Priority.MEDIUM
    else:
        priority = Priority.LOW
    
    # Generate tags based on requirement content
    tags = ["task"]
    if project_name:
        tags.append(project_name.lower().replace(" ", "-"))
    
    if "database" in req_lower:
        tags.extend(["database", "backend", "data"])
    elif "llm" in req_lower or "ai" in req_lower:
        tags.extend(["ai", "llm", "integration"])
    elif "website" in req_lower or "frontend" in req_lower:
        tags.extend(["frontend", "ui", "web"])
    elif "api" in req_lower:
        tags.extend(["api", "backend", "integration"])
    
    return WorkItem(
        id=str(uuid.uuid4()),
        title=title,
        work_item_type=WorkItemType.TASK,
        description=description,
        priority=priority,
        tags=tags,
        parent_id=epic_id
    )


def generate_work_items_from_features(features: List[str], project_name: str = "", text_input: str = "") -> List[WorkItem]:
    """Generate a complete set of work items from extracted features"""
    work_items = []
    
    if not features:
        return work_items
    
    # Check if this is a dependency chain workflow using the text input
    if text_input:
        from .text_processor import detect_dependency_chain
        chain_info = detect_dependency_chain(text_input)
        
        if chain_info['is_chain']:
            # Create ONE Epic for the workflow root
            epic = create_epic_from_feature(chain_info['root_concept'], project_name)
            work_items.append(epic)
            
            # Create Tasks for each step in the dependency chain
            for step in chain_info['steps']:
                task = create_task_from_requirement(f"Implement {step} Component", epic.id, project_name)
                work_items.append(task)
            
            return work_items
    
    # Fallback to original logic if not a dependency chain
    # If we have multiple features, create epics for major ones and tasks for smaller ones
    major_features = []
    minor_features = []
    
    for feature in features:
        feature_lower = feature.lower()
        # Major features that deserve their own epic
        if any(keyword in feature_lower for keyword in [
            'build', 'create', 'develop', 'chatbot', 'website', 'application', 'system', 'platform'
        ]):
            major_features.append(feature)
        else:
            minor_features.append(feature)
    
    # Create epics for major features
    epic_ids = []
    for feature in major_features:
        epic = create_epic_from_feature(feature, project_name)
        work_items.append(epic)
        epic_ids.append(epic.id)
    
    # If no major features, create a general epic
    if not major_features and minor_features:
        general_epic = create_epic_from_feature(f"{project_name} Development" if project_name else "Project Development")
        work_items.append(general_epic)
        epic_ids.append(general_epic.id)
    
    # Create tasks for minor features under the first epic
    parent_epic_id = epic_ids[0] if epic_ids else None
    for feature in minor_features:
        if parent_epic_id:
            task = create_task_from_requirement(feature, parent_epic_id, project_name)
            work_items.append(task)
    
    return work_items


def format_ado_summary(instructions: ADOInstructions) -> str:
    """
    Format ADO instructions into a user-friendly summary for review
    
    Creates a neatly formatted summary showing:
    - Project overview
    - Epic and Task breakdown
    - Priority distribution
    - Work item relationships
    
    Args:
        instructions: The ADOInstructions object to format
        
    Returns:
        str: Formatted summary ready for user review
    """
    summary = []
    summary.append("=" * 60)
    summary.append(f"📋 ADO WORK ITEMS SUMMARY")
    summary.append("=" * 60)
    summary.append(f"🎯 Project: {instructions.project_name}")
    summary.append(f"🏢 Organization: {instructions.organization_context['name']}")
    summary.append("")
    
    # Group work items by type
    epics = [wi for wi in instructions.work_items if wi.work_item_type.value == "Epic"]
    tasks = [wi for wi in instructions.work_items if wi.work_item_type.value == "Task"]
    
    summary.append(f"📊 OVERVIEW:")
    summary.append(f"   • {len(epics)} Epic(s)")
    summary.append(f"   • {len(tasks)} Task(s)")
    summary.append(f"   • Total Work Items: {len(instructions.work_items)}")
    summary.append("")
    
    # Show Epics
    if epics:
        summary.append("🎯 EPICS:")
        for i, epic in enumerate(epics, 1):
            summary.append(f"   {i}. {epic.title}")
            summary.append(f"      Priority: {epic.priority.value}")
            summary.append(f"      Description: {epic.description[:80]}...")
            summary.append("")
    
    # Show Tasks grouped by Epic (if applicable)
    if tasks:
        summary.append("✅ TASKS:")
        for i, task in enumerate(tasks, 1):
            summary.append(f"   {i}. {task.title}")
            summary.append(f"      Priority: {task.priority.value}")
            summary.append(f"      Description: {task.description[:80]}...")
            summary.append("")
    
    summary.append("=" * 60)
    summary.append("❓ Please review the above work items.")
    summary.append("   • Are these instructions correct?")
    summary.append("   • Do any work items need modifications?")
    summary.append("   • Should priorities be adjusted?")
    summary.append("=" * 60)
    
    return "\n".join(summary)


def generate_ado_instructions(
    text_input: str = "",
    project_name: str = "",
    priority_override: str = "",
    features: List[str] = None
) -> ADOInstructions:
    """
    Generate complete ADO instructions from input parameters
    
    After generating the work items, the system should:
    1. Present a neatly formatted summary of all Epics and Tasks created
    2. Show the project structure and work item relationships
    3. Ask the user if the generated instructions are correct
    4. Offer to make modifications if the user requests changes
    
    Returns:
        ADOInstructions: Complete work item structure ready for ADO import
    """
    
    # Use provided features or extract from text
    if features is None:
        from .text_processor import extract_features_from_text
        features = extract_features_from_text(text_input)
    
    # Generate work items (now passing text_input for dependency chain detection)
    work_items = generate_work_items_from_features(features, project_name, text_input)
    
    # Apply priority override if specified
    if priority_override:
        try:
            override_priority = Priority(priority_override.upper())
            for work_item in work_items:
                work_item.priority = override_priority
        except ValueError:
            pass  # Invalid priority override, ignore
    
    return ADOInstructions(
        project_name=project_name or "Generated Project",
        work_items=work_items,
        organization_context=ORGANIZATION_CONTEXT
    )
