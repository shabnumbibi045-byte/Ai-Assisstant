"""Google Gemini LLM Provider Implementation."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from .base_provider import BaseLLMProvider, LLMResponse, EmbeddingResponse

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini implementation of LLM provider."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-pro",
        embedding_model: str = "models/embedding-001",
        timeout: int = 60,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google AI API key
            model: Gemini model to use
            embedding_model: Embedding model
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__(api_key, model, **kwargs)
        genai.configure(api_key=api_key)
        self.chat_model = genai.GenerativeModel(model)
        self.embedding_model = embedding_model
        self.max_retries = max_retries
        logger.info(f"Initialized Gemini provider with model: {model}")
    
    def _convert_messages_to_gemini(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Convert OpenAI-style messages to Gemini format."""
        gemini_messages = []
        system_instruction = None
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                system_instruction = content
            elif role == "user":
                gemini_messages.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [content]})
        
        return gemini_messages, system_instruction
    
    def _convert_functions_to_declarations(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert function schemas to Gemini function declarations."""
        declarations = []
        for func in functions:
            declaration = {
                "name": func["name"],
                "description": func["description"],
                "parameters": func["parameters"]
            }
            declarations.append(declaration)
        return declarations
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((google_exceptions.ResourceExhausted,)),
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
        """Generate chat completion using Google Gemini."""
        try:
            gemini_messages, system_instruction = self._convert_messages_to_gemini(messages)
            
            # Configure generation
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens or 8192,
            }
            
            # Handle function calling
            tools = None
            if functions:
                tools = [{"function_declarations": self._convert_functions_to_declarations(functions)}]
            
            # Create chat session
            chat = self.chat_model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
            
            # Send message
            response = await asyncio.to_thread(
                chat.send_message,
                gemini_messages[-1]["parts"][0] if gemini_messages else "",
                generation_config=generation_config,
                tools=tools
            )
            
            # Extract content
            content = response.text if hasattr(response, 'text') else ""
            
            # Handle function calls
            function_call = None
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call'):
                        function_call = {
                            "name": part.function_call.name,
                            "arguments": dict(part.function_call.args)
                        }
            
            # Token tracking (Gemini provides token counts)
            prompt_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
            completion_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
            tokens_used = prompt_tokens + completion_tokens
            self._total_tokens_used += tokens_used
            
            logger.info(f"Gemini completion: {tokens_used} tokens used")
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider="gemini",
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                finish_reason=str(response.candidates[0].finish_reason),
                timestamp=datetime.utcnow(),
                function_call=function_call,
                raw_response=None  # Gemini responses are not easily serializable
            )
            
        except google_exceptions.ResourceExhausted as e:
            logger.error(f"Gemini rate limit exceeded: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Gemini chat completion: {e}")
            raise
    
    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> EmbeddingResponse:
        """Generate embedding using Google Gemini."""
        try:
            embed_model = model or self.embedding_model
            
            result = await asyncio.to_thread(
                genai.embed_content,
                model=embed_model,
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = result['embedding']
            
            # Gemini doesn't provide token counts for embeddings
            # Estimate based on text length
            tokens_used = len(text.split()) * 2
            self._total_tokens_used += tokens_used
            
            logger.debug(f"Generated Gemini embedding: ~{tokens_used} tokens")
            
            return EmbeddingResponse(
                embedding=embedding,
                model=embed_model,
                provider="gemini",
                tokens_used=tokens_used,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating Gemini embedding: {e}")
            raise
    
    async def batch_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs
    ) -> List[EmbeddingResponse]:
        """Generate embeddings for multiple texts."""
        embed_model = model or self.embedding_model
        all_embeddings = []
        
        try:
            result = await asyncio.to_thread(
                genai.embed_content,
                model=embed_model,
                content=texts,
                task_type="retrieval_document"
            )
            
            for i, embedding in enumerate(result['embedding']):
                tokens_used = len(texts[i].split()) * 2
                self._total_tokens_used += tokens_used
                
                all_embeddings.append(
                    EmbeddingResponse(
                        embedding=embedding,
                        model=embed_model,
                        provider="gemini",
                        tokens_used=tokens_used,
                        timestamp=datetime.utcnow()
                    )
                )
            
            logger.info(f"Batch embedding: {len(texts)} texts")
            
        except Exception as e:
            logger.error(f"Error in Gemini batch embeddings: {e}")
            raise
        
        return all_embeddings
    
    def validate_function_schema(self, functions: List[Dict[str, Any]]) -> bool:
        """Validate function calling schema for Gemini."""
        required_keys = {"name", "description", "parameters"}
        
        for func in functions:
            if not all(key in func for key in required_keys):
                raise ValueError(f"Function missing required keys: {required_keys}")
        
        return True
    
    async def health_check(self) -> bool:
        """Check if Gemini API is accessible."""
        try:
            response = await asyncio.to_thread(
                self.chat_model.generate_content,
                "test",
                generation_config={"max_output_tokens": 5}
            )
            return True
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False
