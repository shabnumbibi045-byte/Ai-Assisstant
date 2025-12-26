"""Tools Router - Tool invocation endpoints with authentication."""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.schemas import ToolInvokeRequest, ToolInvokeResponse
from app.tools.tool_registry import ToolRegistry
from app.auth.dependencies import get_current_user, get_current_verified_user
from app.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tools", tags=["tools"])


# ============================================
# ADDITIONAL SCHEMAS
# ============================================

class ToolSchema(BaseModel):
    """Tool schema information."""
    name: str
    description: str
    category: str
    parameters: Dict[str, Any]
    required_permissions: List[str]


class ToolListResponse(BaseModel):
    """Response containing list of tools."""
    tools: List[Dict[str, Any]]
    total: int
    categories: List[str]


class ToolDetailResponse(BaseModel):
    """Detailed tool information."""
    name: str
    description: str
    category: str
    parameters: Dict[str, Any]
    examples: List[Dict[str, Any]]
    required_permissions: List[str]


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_user_permissions(user: User) -> Dict[str, bool]:
    """Extract user permissions from preferences."""
    preferences = user.preferences or {}
    module_perms = preferences.get("module_permissions", {})
    
    # Flatten permissions into a single dict
    permissions = {}
    for module, perms in module_perms.items():
        for perm_name, value in perms.items():
            permissions[f"{module}.{perm_name}"] = value
    
    return permissions


def get_user_enabled_modules(user: User) -> List[str]:
    """Get list of enabled modules for user."""
    preferences = user.preferences or {}
    return preferences.get("modules_enabled", ["chat", "memory"])


def check_module_access(user: User, tool_category: str) -> bool:
    """Check if user has access to tool's module."""
    enabled_modules = get_user_enabled_modules(user)
    
    # Map tool categories to modules
    category_module_map = {
        "banking": "banking",
        "stocks": "stocks",
        "travel": "travel",
        "research": "research",
        "communication": "chat",
        "general": "chat"
    }
    
    required_module = category_module_map.get(tool_category, "chat")
    return required_module in enabled_modules


# ============================================
# ENDPOINTS
# ============================================

@router.post("/invoke", response_model=ToolInvokeResponse)
async def invoke_tool(
    request: ToolInvokeRequest,
    current_user: User = Depends(get_current_verified_user)
):
    """
    Invoke a tool by name.
    
    Requires authentication and appropriate module permissions.
    """
    try:
        ToolRegistry.initialize()
        
        # Get tool info to check category
        tool_schemas = ToolRegistry.get_all_schemas()
        tool_info = next(
            (t for t in tool_schemas if t.get("name") == request.tool_name),
            None
        )
        
        if not tool_info:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{request.tool_name}' not found"
            )
        
        # Check module access
        tool_category = tool_info.get("category", "general")
        if not check_module_access(current_user, tool_category):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: Module for '{request.tool_name}' is not enabled"
            )
        
        # Get user permissions
        permissions = get_user_permissions(current_user)
        
        # Execute tool with user's ID from token
        result = await ToolRegistry.execute_tool(
            tool_name=request.tool_name,
            user_id=str(current_user.id),
            parameters=request.parameters,
            permissions=permissions
        )
        
        logger.info(f"Tool '{request.tool_name}' executed for user {current_user.id}")
        
        return ToolInvokeResponse(
            success=result.success,
            data=result.data,
            message=result.message,
            error=result.error,
            requires_confirmation=getattr(result, 'requires_confirmation', False)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool invocation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=ToolListResponse)
async def list_tools(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    List all available tools.
    
    Optionally filter by category.
    """
    try:
        ToolRegistry.initialize()
        schemas = ToolRegistry.get_all_schemas()
        
        # Get enabled modules for user
        enabled_modules = get_user_enabled_modules(current_user)
        
        # Filter by category if specified
        if category:
            schemas = [s for s in schemas if s.get("category") == category]
        
        # Mark tools based on user's module access
        for schema in schemas:
            tool_category = schema.get("category", "general")
            schema["accessible"] = check_module_access(current_user, tool_category)
        
        # Get unique categories
        categories = list(set(s.get("category", "general") for s in schemas))
        
        return ToolListResponse(
            tools=schemas,
            total=len(schemas),
            categories=categories
        )
    except Exception as e:
        logger.error(f"List tools error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tool_name}")
async def get_tool_details(
    tool_name: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific tool."""
    try:
        ToolRegistry.initialize()
        schemas = ToolRegistry.get_all_schemas()
        
        tool_info = next(
            (t for t in schemas if t.get("name") == tool_name),
            None
        )
        
        if not tool_info:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_name}' not found"
            )
        
        # Check if user has access
        tool_category = tool_info.get("category", "general")
        tool_info["accessible"] = check_module_access(current_user, tool_category)
        
        # Add example usages based on tool type
        examples = get_tool_examples(tool_name)
        tool_info["examples"] = examples
        
        return tool_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tool details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/list")
async def list_categories(
    current_user: User = Depends(get_current_user)
):
    """List all tool categories with tool counts."""
    try:
        ToolRegistry.initialize()
        schemas = ToolRegistry.get_all_schemas()
        
        # Count tools per category
        category_counts = {}
        for schema in schemas:
            category = schema.get("category", "general")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        enabled_modules = get_user_enabled_modules(current_user)
        
        categories = []
        for category, count in category_counts.items():
            categories.append({
                "name": category,
                "tool_count": count,
                "accessible": check_module_access(current_user, category)
            })
        
        return {"categories": categories}
    except Exception as e:
        logger.error(f"List categories error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_tool_examples(tool_name: str) -> List[Dict[str, Any]]:
    """Get example usages for a tool."""
    examples = {
        "get_balance": [
            {
                "description": "Get all balances",
                "parameters": {}
            },
            {
                "description": "Get Canadian accounts",
                "parameters": {"country": "CA"}
            }
        ],
        "get_transactions": [
            {
                "description": "Get last 7 days",
                "parameters": {"days": 7}
            },
            {
                "description": "Get groceries category",
                "parameters": {"category": "groceries", "days": 30}
            }
        ],
        "search_flights": [
            {
                "description": "Search one-way flight",
                "parameters": {
                    "origin": "YYZ",
                    "destination": "LAX",
                    "departure_date": "2024-03-15"
                }
            }
        ],
        "get_portfolio": [
            {
                "description": "Get full portfolio",
                "parameters": {}
            }
        ],
        "search_legal": [
            {
                "description": "Search Canadian case law",
                "parameters": {
                    "query": "contract breach damages",
                    "jurisdiction": "federal",
                    "country": "canada"
                }
            }
        ]
    }
    
    return examples.get(tool_name, [])
