"""
Data models and type definitions for ADO Instructions MCP Server

This module contains all the data classes, enums, and type definitions
used throughout the ADO instruction generation system.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class WorkItemType(Enum):
    """Enumeration of Azure DevOps work item types"""
    EPIC = "Epic"
    TASK = "Task"
    USER_STORY = "User Story"
    BUG = "Bug"


class Priority(Enum):
    """Priority levels for work items"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class WorkItem:
    """Represents a single Azure DevOps work item"""
    id: str
    title: str
    work_item_type: WorkItemType
    description: str
    priority: Priority
    tags: List[str]
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert work item to dictionary format"""
        return {
            "id": self.id,
            "title": self.title,
            "work_item_type": self.work_item_type.value,
            "description": self.description,
            "priority": self.priority.value,
            "tags": self.tags,
            "parent_id": self.parent_id
        }


@dataclass
class ADOInstructions:
    """Complete set of ADO work item instructions"""
    project_name: str
    work_items: List[WorkItem]
    organization_context: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert instructions to dictionary format"""
        return {
            "project_name": self.project_name,
            "work_items": [item.to_dict() for item in self.work_items],
            "organization_context": self.organization_context
        }


# Organization context and constants
ORGANIZATION_CONTEXT = {
    "name": "Omar Solutions",
    "focus_areas": ["Data Engineering", "Visualization", "Analytics"],
    "platform": "Azure Cloud Platform",
    "scale": "Large scale solutions",
    "methodology": "Agile development with Epic/Task hierarchy"
}
