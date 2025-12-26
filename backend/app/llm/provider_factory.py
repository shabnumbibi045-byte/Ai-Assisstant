"""LLM Provider Factory - Creates provider instances based on configuration."""

import logging
from typing import Optional, Dict, Any
from enum import Enum

from .base_provider import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """Supported LLM provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    LOCAL = "local"  # Future support


class ProviderFactory:
    """Factory for creating LLM provider instances."""
    
    _providers: Dict[str, BaseLLMProvider] = {}
    
    @classmethod
    def create_provider(
        cls,
        provider_type: ProviderType,
        api_key: str,
        model: Optional[str] = None,
        **kwargs
    ) -> BaseLLMProvider:
        """
        Create and return an LLM provider instance.
        
        Args:
            provider_type: Type of provider to create
            api_key: API key for the provider
            model: Model identifier (uses default if None)
            **kwargs: Additional provider-specific configuration
            
        Returns:
            Initialized provider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        provider_key = f"{provider_type}:{model or 'default'}"
        
        # Return cached provider if exists
        if provider_key in cls._providers:
            logger.debug(f"Returning cached provider: {provider_key}")
            return cls._providers[provider_key]
        
        # Create new provider
        if provider_type == ProviderType.OPENAI:
            provider = cls._create_openai(api_key, model, **kwargs)
        elif provider_type == ProviderType.ANTHROPIC:
            provider = cls._create_anthropic(api_key, model, **kwargs)
        elif provider_type == ProviderType.GEMINI:
            provider = cls._create_gemini(api_key, model, **kwargs)
        elif provider_type == ProviderType.LOCAL:
            raise NotImplementedError("Local model support coming soon")
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        
        # Cache and return
        cls._providers[provider_key] = provider
        logger.info(f"Created new provider: {provider_key}")
        return provider
    
    @staticmethod
    def _create_openai(
        api_key: str,
        model: Optional[str] = None,
        **kwargs
    ) -> OpenAIProvider:
        """Create OpenAI provider instance."""
        default_model = model or "gpt-4-turbo-preview"
        return OpenAIProvider(
            api_key=api_key,
            model=default_model,
            **kwargs
        )
    
    @staticmethod
    def _create_anthropic(
        api_key: str,
        model: Optional[str] = None,
        **kwargs
    ) -> AnthropicProvider:
        """Create Anthropic provider instance."""
        default_model = model or "claude-3-5-sonnet-20241022"
        return AnthropicProvider(
            api_key=api_key,
            model=default_model,
            **kwargs
        )
    
    @staticmethod
    def _create_gemini(
        api_key: str,
        model: Optional[str] = None,
        **kwargs
    ) -> GeminiProvider:
        """Create Gemini provider instance."""
        default_model = model or "gemini-1.5-pro"
        return GeminiProvider(
            api_key=api_key,
            model=default_model,
            **kwargs
        )
    
    @classmethod
    def get_provider(cls, provider_key: str) -> Optional[BaseLLMProvider]:
        """Get cached provider by key."""
        return cls._providers.get(provider_key)
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached providers."""
        cls._providers.clear()
        logger.info("Provider cache cleared")
    
    @classmethod
    async def health_check_all(cls) -> Dict[str, bool]:
        """
        Run health checks on all cached providers.
        
        Returns:
            Dict mapping provider keys to health status
        """
        results = {}
        for key, provider in cls._providers.items():
            try:
                is_healthy = await provider.health_check()
                results[key] = is_healthy
            except Exception as e:
                logger.error(f"Health check failed for {key}: {e}")
                results[key] = False
        return results
