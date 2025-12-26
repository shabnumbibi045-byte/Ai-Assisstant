"""Base LLM Provider Interface - Abstract base class for all LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LLMResponse:
    """Standardized response from LLM provider."""
    content: str
    model: str
    provider: str
    tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str
    timestamp: datetime
    function_call: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class EmbeddingResponse:
    """Standardized embedding response."""
    embedding: List[float]
    model: str
    provider: str
    tokens_used: int
    timestamp: datetime


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Initialize provider with API key and model.
        
        Args:
            api_key: Provider API key
            model: Model identifier
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self._total_tokens_used = 0
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            functions: Function schemas for function calling
            stream: Whether to stream response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse object with standardized fields
        """
        pass
    
    @abstractmethod
    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> EmbeddingResponse:
        """
        Generate text embedding.
        
        Args:
            text: Input text to embed
            model: Embedding model (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            EmbeddingResponse with embedding vector
        """
        pass
    
    @abstractmethod
    async def batch_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs
    ) -> List[EmbeddingResponse]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            model: Embedding model
            **kwargs: Additional parameters
            
        Returns:
            List of EmbeddingResponse objects
        """
        pass
    
    def get_total_tokens_used(self) -> int:
        """Get total tokens used by this provider instance."""
        return self._total_tokens_used
    
    def reset_token_counter(self):
        """Reset token usage counter."""
        self._total_tokens_used = 0
    
    @abstractmethod
    def validate_function_schema(self, functions: List[Dict[str, Any]]) -> bool:
        """
        Validate function calling schema.
        
        Args:
            functions: List of function schemas
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if provider is healthy and accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        pass
