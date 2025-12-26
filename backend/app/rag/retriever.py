"""Retriever - Retrieve relevant chunks from vector store."""

import logging
from typing import List, Dict, Any
from app.memory.vector_memory import VectorMemory

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieve relevant document chunks based on semantic similarity."""
    
    def __init__(self, vector_memory: VectorMemory):
        """
        Initialize retriever.
        
        Args:
            vector_memory: Vector memory instance
        """
        self.vector_memory = vector_memory
    
    async def retrieve(
        self,
        user_id: str,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most relevant chunks.
        
        Args:
            user_id: User identifier
            query_embedding: Query embedding vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of chunk dictionaries with scores
        """
        results = await self.vector_memory.search(
            user_id=user_id,
            query_embedding=query_embedding,
            limit=top_k,
            score_threshold=score_threshold
        )
        
        chunks = [
            {
                'text': result.text,
                'score': result.score,
                'metadata': result.metadata
            }
            for result in results
        ]
        
        logger.info(f"Retrieved {len(chunks)} relevant chunks")
        return chunks
