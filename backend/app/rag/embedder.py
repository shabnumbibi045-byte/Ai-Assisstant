"""Embedder - Generate embeddings for text chunks."""

import logging
from typing import List, Dict, Any
from app.llm.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class Embedder:
    """Generate embeddings using LLM provider."""
    
    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initialize embedder.
        
        Args:
            llm_provider: LLM provider with embedding capabilities
        """
        self.provider = llm_provider
    
    async def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of chunk dictionaries with 'text' key
            
        Returns:
            Chunks with added 'embedding' key
        """
        texts = [chunk['text'] for chunk in chunks]
        
        # Batch embed
        embedding_responses = await self.provider.batch_embeddings(texts)
        
        # Add embeddings to chunks
        for chunk, emb_response in zip(chunks, embedding_responses):
            chunk['embedding'] = emb_response.embedding
        
        logger.info(f"Generated embeddings for {len(chunks)} chunks")
        return chunks
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query.
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector
        """
        emb_response = await self.provider.generate_embedding(query)
        return emb_response.embedding
