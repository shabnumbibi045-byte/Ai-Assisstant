"""Base Tool - Abstract base class for all tools."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ToolCategory(str, Enum):
    """Tool categories."""
    BANKING = "banking"
    TRAVEL = "travel"
    RESEARCH = "research"
    COMMUNICATION = "communication"
    STOCKS = "stocks"
    GENERAL = "general"


@dataclass
class ToolResult:
    """Standardized tool execution result."""
    success: bool
    data: Any
    message: str
    error: Optional[str] = None
    requires_confirmation: bool = False
    metadata: Optional[Dict[str, Any]] = None


class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    def __init__(self, name: str, description: str, category: ToolCategory):
        """
        Initialize tool.
        
        Args:
            name: Tool name
            description: Tool description
            category: Tool category
        """
        self.name = name
        self.description = description
        self.category = category
    
    @abstractmethod
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        """
        Execute tool with parameters.
        
        Args:
            user_id: User identifier
            parameters: Tool parameters
            permissions: User permissions
            
        Returns:
            ToolResult
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for function calling.
        
        Returns:
            OpenAI-compatible function schema
        """
        pass
    
    def check_permission(
        self,
        required_permission: str,
        permissions: Optional[Dict[str, bool]] = None
    ) -> bool:
        """
        Check if user has required permission.
        
        Args:
            required_permission: Permission key
            permissions: User permissions dict
            
        Returns:
            True if permitted
        """
        if permissions is None:
            return False
        return permissions.get(required_permission, False)
    
    def validate_parameters(
        self,
        parameters: Dict[str, Any],
        required_keys: List[str]
    ) -> Optional[str]:
        """
        Validate required parameters are present.
        
        Args:
            parameters: Parameters to validate
            required_keys: Required parameter keys
            
        Returns:
            Error message if invalid, None if valid
        """
        missing = [key for key in required_keys if key not in parameters]
        if missing:
            return f"Missing required parameters: {', '.join(missing)}"
        return None
