"""Sample Tests - Demonstrates testing structure."""

import pytest
from app.tools.banking_tools import GetBalanceTool
from app.llm.provider_factory import ProviderType


@pytest.mark.asyncio
async def test_get_balance_tool():
    """Test balance retrieval tool."""
    tool = GetBalanceTool()
    
    result = await tool.execute(
        user_id="test_user",
        parameters={"account_type": "checking"},
        permissions={"banking_read": True}
    )
    
    assert result.success is True
    assert result.data is not None
    assert "balance" in result.data


@pytest.mark.asyncio
async def test_get_balance_no_permission():
    """Test balance retrieval without permission."""
    tool = GetBalanceTool()
    
    result = await tool.execute(
        user_id="test_user",
        parameters={"account_type": "checking"},
        permissions={"banking_read": False}
    )
    
    assert result.success is False
    assert result.error is not None


def test_tool_schema():
    """Test tool schema generation."""
    tool = GetBalanceTool()
    schema = tool.get_schema()
    
    assert schema["name"] == "get_balance"
    assert "parameters" in schema
    assert "properties" in schema["parameters"]


def test_provider_types():
    """Test provider type enum."""
    assert ProviderType.OPENAI == "openai"
    assert ProviderType.ANTHROPIC == "anthropic"
    assert ProviderType.GEMINI == "gemini"
