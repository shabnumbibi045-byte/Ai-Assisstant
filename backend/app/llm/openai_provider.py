"""OpenAI LLM Provider Implementation."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from .base_provider import BaseLLMProvider, LLMResponse, EmbeddingResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI implementation of LLM provider."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        embedding_model: str = "text-embedding-3-small",
        timeout: int = 60,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Chat model to use
            embedding_model: Embedding model to use
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__(api_key, model, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)
        self.embedding_model = embedding_model
        self.max_retries = max_retries
        logger.info(f"Initialized OpenAI provider with model: {model}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError)),
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
        """Generate chat completion using OpenAI."""
        try:
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                **kwargs
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            if functions:
                request_params["tools"] = [
                    {"type": "function", "function": func} for func in functions
                ]
                request_params["tool_choice"] = "auto"
            
            response = await self.client.chat.completions.create(**request_params)
            
            # Extract response data
            message = response.choices[0].message
            content = message.content or ""
            
            # Handle function calling
            function_call = None
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_call = message.tool_calls[0]
                function_call = {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            
            # Token tracking
            tokens_used = response.usage.total_tokens
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            self._total_tokens_used += tokens_used
            
            logger.info(f"OpenAI completion: {tokens_used} tokens used")
            
            return LLMResponse(
                content=content,
                model=response.model,
                provider="openai",
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                finish_reason=response.choices[0].finish_reason,
                timestamp=datetime.utcnow(),
                function_call=function_call,
                raw_response=response.model_dump()
            )
            
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI chat completion: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError)),
    )
    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> EmbeddingResponse:
        """Generate embedding using OpenAI."""
        try:
            embed_model = model or self.embedding_model
            
            response = await self.client.embeddings.create(
                model=embed_model,
                input=text,
                **kwargs
            )
            
            embedding = response.data[0].embedding
            tokens_used = response.usage.total_tokens
            self._total_tokens_used += tokens_used
            
            logger.debug(f"Generated embedding: {tokens_used} tokens")
            
            return EmbeddingResponse(
                embedding=embedding,
                model=embed_model,
                provider="openai",
                tokens_used=tokens_used,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def batch_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        batch_size: int = 100,
        **kwargs
    ) -> List[EmbeddingResponse]:
        """Generate embeddings for multiple texts in batches."""
        embed_model = model or self.embedding_model
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = await self.client.embeddings.create(
                    model=embed_model,
                    input=batch,
                    **kwargs
                )
                
                tokens_used = response.usage.total_tokens
                self._total_tokens_used += tokens_used
                
                for data in response.data:
                    all_embeddings.append(
                        EmbeddingResponse(
                            embedding=data.embedding,
                            model=embed_model,
                            provider="openai",
                            tokens_used=tokens_used // len(batch),
                            timestamp=datetime.utcnow()
                        )
                    )
                
                logger.info(f"Batch embedding: {len(batch)} texts, {tokens_used} tokens")
                
            except Exception as e:
                logger.error(f"Error in batch embeddings: {e}")
                raise
        
        return all_embeddings
    
    def validate_function_schema(self, functions: List[Dict[str, Any]]) -> bool:
        """Validate function calling schema for OpenAI."""
        required_keys = {"name", "description", "parameters"}
        
        for func in functions:
            if not all(key in func for key in required_keys):
                raise ValueError(f"Function missing required keys: {required_keys}")
            
            # Validate parameters schema
            params = func["parameters"]
            if "type" not in params or params["type"] != "object":
                raise ValueError("Parameters must be of type 'object'")
            
            if "properties" not in params:
                raise ValueError("Parameters must have 'properties' field")
        
        return True
    
    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False
