"""Chat Service - Core chat processing logic."""

import logging
from typing import Dict, Any
from app.schemas import ChatRequest, ChatResponse
from app.llm.provider_factory import ProviderFactory, ProviderType
from app.prompts import get_prompt_for_module, BASE_SYSTEM_PROMPT
from app.tools.tool_registry import ToolRegistry
from app.config import settings

logger = logging.getLogger(__name__)


class ChatService:
    """Service for processing chat messages."""
    
    def __init__(self):
        """Initialize chat service."""
        self.provider_factory = ProviderFactory
        ToolRegistry.initialize()
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message.
        
        Args:
            request: ChatRequest with user message and options
            
        Returns:
            ChatResponse with AI reply
        """
        logger.info(f"Processing message for user {request.user_id}")
        
        # Get LLM provider
        provider = self._get_provider()
        
        # Build system prompt
        system_prompt = self._build_system_prompt(request.module)
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ]
        
        # Get tools if enabled
        tools = None
        if request.use_tools:
            tools = ToolRegistry.get_all_schemas()
        
        # Generate response
        try:
            llm_response = await provider.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                functions=tools
            )
            
            # Check for tool calls
            tool_calls = []
            if llm_response.function_call:
                # Execute tool
                tool_result = await self._execute_tool_call(
                    request.user_id,
                    llm_response.function_call
                )
                tool_calls.append(tool_result)
            
            return ChatResponse(
                response=llm_response.content,
                tokens_used=llm_response.tokens_used,
                tool_calls=tool_calls,
                sources=[],
                session_id=request.session_id
            )
        
        except Exception as e:
            logger.error(f"Chat processing error: {e}")
            return ChatResponse(
                response=f"I apologize, but I encountered an error: {str(e)}",
                tokens_used=0,
                tool_calls=[],
                sources=[],
                session_id=request.session_id
            )
    
    def _get_provider(self):
        """Get LLM provider based on settings."""
        provider_type = ProviderType(settings.DEFAULT_LLM_PROVIDER)
        
        if provider_type == ProviderType.OPENAI:
            api_key = settings.OPENAI_API_KEY
        elif provider_type == ProviderType.ANTHROPIC:
            api_key = settings.ANTHROPIC_API_KEY
        elif provider_type == ProviderType.GEMINI:
            api_key = settings.GOOGLE_API_KEY
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")
        
        if not api_key:
            raise ValueError(f"API key not configured for {provider_type}")
        
        return self.provider_factory.create_provider(
            provider_type=provider_type,
            api_key=api_key,
            model=settings.DEFAULT_CHAT_MODEL
        )
    
    def _build_system_prompt(self, module: str = None) -> str:
        """Build system prompt with optional module context."""
        if module:
            return get_prompt_for_module(module)
        return BASE_SYSTEM_PROMPT
    
    async def _execute_tool_call(self, user_id: str, function_call: Dict[str, Any]) -> Dict:
        """Execute a tool call."""
        import json
        
        tool_name = function_call["name"]
        
        # Parse arguments (may be string or dict)
        if isinstance(function_call["arguments"], str):
            arguments = json.loads(function_call["arguments"])
        else:
            arguments = function_call["arguments"]
        
        # Execute tool
        result = await ToolRegistry.execute_tool(
            tool_name=tool_name,
            user_id=user_id,
            parameters=arguments,
            permissions={}  # TODO: Get real permissions
        )
        
        return {
            "tool": tool_name,
            "success": result.success,
            "data": result.data,
            "message": result.message
        }
