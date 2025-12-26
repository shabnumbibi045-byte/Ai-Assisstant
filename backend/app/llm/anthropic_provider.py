"""Anthropic Claude LLM Provider Implementation."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from anthropic import AsyncAnthropic, RateLimitError, APIError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from .base_provider import BaseLLMProvider, LLMResponse, EmbeddingResponse

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude implementation of LLM provider."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        timeout: int = 60,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__(api_key, model, **kwargs)
        self.client = AsyncAnthropic(api_key=api_key, timeout=timeout)
        self.max_retries = max_retries
        logger.info(f"Initialized Anthropic provider with model: {model}")
    
    def _convert_messages_format(self, messages: List[Dict[str, str]]) -> tuple:
        """
        Convert OpenAI-style messages to Anthropic format.
        
        Returns:
            (system_prompt, user_messages)
        """
        system_prompt = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt += msg["content"] + "\n"
            else:
                user_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return system_prompt.strip(), user_messages
    
    def _convert_functions_to_tools(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI function schema to Anthropic tools format."""
        tools = []
        for func in functions:
            tool = {
                "name": func["name"],
                "description": func["description"],
                "input_schema": func["parameters"]
            }
            tools.append(tool)
        return tools
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((RateLimitError, APIError)),
        reraise=True
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """Generate chat completion using Anthropic Claude."""
        try:
            system_prompt, user_messages = self._convert_messages_format(messages)
            
            request_params = {
                "model": self.model,
                "messages": user_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
                **kwargs
            }
            
            if system_prompt:
                request_params["system"] = system_prompt
            
            if functions:
                request_params["tools"] = self._convert_functions_to_tools(functions)
            
            response = await self.client.messages.create(**request_params)
            
            # Extract content
            content = ""
            function_call = None
            
            for block in response.content:
                if block.type == "text":
                    content += block.text
                elif block.type == "tool_use":
                    function_call = {
                        "name": block.name,
                        "arguments": block.input
                    }
            
            # Token tracking
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens
            self._total_tokens_used += tokens_used
            
            logger.info(f"Anthropic completion: {tokens_used} tokens used")
            
            return LLMResponse(
                content=content,
                model=response.model,
                provider="anthropic",
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                finish_reason=response.stop_reason,
                timestamp=datetime.utcnow(),
                function_call=function_call,
                raw_response=response.model_dump()
            )
            
        except RateLimitError as e:
            logger.error(f"Anthropic rate limit exceeded: {e}")
            raise
        except APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Anthropic chat completion: {e}")
            raise
    
    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> EmbeddingResponse:
        """
        Note: Anthropic doesn't provide embeddings API.
        This is a placeholder that raises NotImplementedError.
        """
        raise NotImplementedError(
            "Anthropic does not provide an embeddings API. "
            "Use OpenAI or other providers for embeddings."
        )
    
    async def batch_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs
    ) -> List[EmbeddingResponse]:
        """Not implemented for Anthropic."""
        raise NotImplementedError(
            "Anthropic does not provide an embeddings API."
        )
    
    def validate_function_schema(self, functions: List[Dict[str, Any]]) -> bool:
        """Validate function calling schema for Anthropic."""
        required_keys = {"name", "description", "parameters"}
        
        for func in functions:
            if not all(key in func for key in required_keys):
                raise ValueError(f"Function missing required keys: {required_keys}")
            
            params = func["parameters"]
            if "type" not in params:
                raise ValueError("Parameters must have 'type' field")
        
        return True
    
    async def health_check(self) -> bool:
        """Check if Anthropic API is accessible."""
        try:
            response = await self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False
