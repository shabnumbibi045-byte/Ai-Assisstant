"""Tool Registry - Central registry for all tools."""

import logging
from typing import Dict, List, Optional
from .base_tool import BaseTool, ToolResult, ToolCategory
from .banking_tools import BankingTools
from .travel_tools import TravelTools
from .research_tools import ResearchTools
from .communication_tools import CommunicationTools
from .stock_tools import StockTools

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry for all available tools."""
    
    _tools: Dict[str, BaseTool] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize and register all tools."""
        if cls._initialized:
            return
        
        all_tool_classes = [
            BankingTools,
            TravelTools,
            ResearchTools,
            CommunicationTools,
            StockTools
        ]
        
        for tool_class in all_tool_classes:
            for tool in tool_class.get_all_tools():
                cls._tools[tool.name] = tool
        
        cls._initialized = True
        logger.info(f"Tool registry initialized with {len(cls._tools)} tools")
    
    @classmethod
    def get_tool(cls, name: str) -> Optional[BaseTool]:
        """Get tool by name."""
        if not cls._initialized:
            cls.initialize()
        return cls._tools.get(name)
    
    @classmethod
    def get_all_tools(cls) -> List[BaseTool]:
        """Get all registered tools."""
        if not cls._initialized:
            cls.initialize()
        return list(cls._tools.values())
    
    @classmethod
    def get_tools_by_category(cls, category: ToolCategory) -> List[BaseTool]:
        """Get tools by category."""
        if not cls._initialized:
            cls.initialize()
        return [tool for tool in cls._tools.values() if tool.category == category]
    
    @classmethod
    def get_all_schemas(cls) -> List[Dict]:
        """Get all tool schemas for LLM function calling."""
        if not cls._initialized:
            cls.initialize()
        return [tool.get_schema() for tool in cls._tools.values()]
    
    @classmethod
    async def execute_tool(
        cls,
        tool_name: str,
        user_id: str,
        parameters: Dict,
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Name of tool to execute
            user_id: User identifier
            parameters: Tool parameters
            permissions: User permissions
            
        Returns:
            ToolResult
        """
        if not cls._initialized:
            cls.initialize()
        
        tool = cls.get_tool(tool_name)
        
        if not tool:
            return ToolResult(
                success=False,
                data=None,
                message=f"Tool '{tool_name}' not found",
                error="Invalid tool name"
            )
        
        try:
            result = await tool.execute(user_id, parameters, permissions)
            logger.info(f"Tool {tool_name} executed for {user_id}: {result.success}")
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return ToolResult(
                success=False,
                data=None,
                message="Tool execution failed",
                error=str(e)
            )
