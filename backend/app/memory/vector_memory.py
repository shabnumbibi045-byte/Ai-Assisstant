"""Vector Memory - Semantic search over embeddings using Qdrant."""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("qdrant-client not installed, vector memory unavailable")

logger = logging.getLogger(__name__)


@dataclass
class VectorMemoryEntry:
    """Represents a vector memory entry."""
    id: str
    text: str
    embedding: List[float]
    user_id: str
    metadata: Dict[str, Any]
    timestamp: datetime
    score: Optional[float] = None


class VectorMemory:
    """
    Manages semantic memory using vector embeddings.
    
    Stores and retrieves information based on semantic similarity
    rather than exact keyword matching.
    """
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "user_memories",
        vector_size: int = 1536,  # OpenAI text-embedding-3-small
        use_qdrant: bool = True
    ):
        """
        Initialize vector memory.
        
        Args:
            qdrant_url: Qdrant server URL
            collection_name: Collection name for memories
            vector_size: Dimension of embedding vectors
            use_qdrant: Whether to use Qdrant (False for in-memory fallback)
        """
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.use_qdrant = use_qdrant and QDRANT_AVAILABLE
        
        # Qdrant client
        self.client: Optional[AsyncQdrantClient] = None
        if self.use_qdrant:
            try:
                self.client = AsyncQdrantClient(url=qdrant_url)
                logger.info(f"Qdrant client initialized: {qdrant_url}")
            except Exception as e:
                logger.error(f"Failed to initialize Qdrant: {e}, using in-memory fallback")
                self.use_qdrant = False
        else:
            self.use_qdrant = False
        
        # In-memory fallback (simple list storage)
        self._memory_store: List[VectorMemoryEntry] = []
        
        logger.info(f"VectorMemory initialized (Qdrant: {self.use_qdrant})")
    
    async def init_collection(self):
        """Initialize Qdrant collection."""
        if not self.use_qdrant or not self.client:
            return
        
        try:
            # Check if collection exists
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Using existing collection: {self.collection_name}")
        
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {e}")
            raise
    
    async def store(
        self,
        user_id: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store text with its embedding.
        
        Args:
            user_id: User identifier
            text: Original text
            embedding: Vector embedding
            metadata: Additional metadata
            
        Returns:
            Unique ID for the stored entry
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        full_metadata = {
            "user_id": user_id,
            "text": text,
            "timestamp": timestamp.isoformat(),
            **(metadata or {})
        }
        
        if self.use_qdrant and self.client:
            await self._store_qdrant(entry_id, embedding, full_metadata)
        else:
            await self._store_memory(entry_id, user_id, text, embedding, full_metadata, timestamp)
        
        logger.debug(f"Stored vector memory for user {user_id}")
        return entry_id
    
    async def _store_qdrant(
        self,
        entry_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """Store in Qdrant."""
        point = PointStruct(
            id=entry_id,
            vector=embedding,
            payload=metadata
        )
        
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
    
    async def _store_memory(
        self,
        entry_id: str,
        user_id: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        timestamp: datetime
    ):
        """Store in memory."""
        entry = VectorMemoryEntry(
            id=entry_id,
            text=text,
            embedding=embedding,
            user_id=user_id,
            metadata=metadata,
            timestamp=timestamp
        )
        self._memory_store.append(entry)
    
    async def search(
        self,
        user_id: str,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[VectorMemoryEntry]:
        """
        Search for semantically similar memories.
        
        Args:
            user_id: User identifier
            query_embedding: Query vector
            limit: Maximum results to return
            score_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of VectorMemoryEntry objects
        """
        if self.use_qdrant and self.client:
            results = await self._search_qdrant(user_id, query_embedding, limit, score_threshold)
        else:
            results = await self._search_memory(user_id, query_embedding, limit, score_threshold)
        
        logger.debug(f"Found {len(results)} similar memories for user {user_id}")
        return results
    
    async def _search_qdrant(
        self,
        user_id: str,
        query_embedding: List[float],
        limit: int,
        score_threshold: float
    ) -> List[VectorMemoryEntry]:
        """Search using Qdrant."""
        search_result = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=limit,
            score_threshold=score_threshold
        )
        
        results = []
        for hit in search_result:
            payload = hit.payload
            results.append(
                VectorMemoryEntry(
                    id=str(hit.id),
                    text=payload.get("text", ""),
                    embedding=[],  # Don't return full embedding
                    user_id=payload.get("user_id", ""),
                    metadata=payload,
                    timestamp=datetime.fromisoformat(payload.get("timestamp")),
                    score=hit.score
                )
            )
        
        return results
    
    async def _search_memory(
        self,
        user_id: str,
        query_embedding: List[float],
        limit: int,
        score_threshold: float
    ) -> List[VectorMemoryEntry]:
        """Search using in-memory store with cosine similarity."""
        import numpy as np
        
        # Filter by user
        user_memories = [m for m in self._memory_store if m.user_id == user_id]
        
        if not user_memories:
            return []
        
        # Calculate cosine similarities
        query_vec = np.array(query_embedding)
        
        scored_memories = []
        for memory in user_memories:
            mem_vec = np.array(memory.embedding)
            
            # Cosine similarity
            similarity = np.dot(query_vec, mem_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(mem_vec)
            )
            
            if similarity >= score_threshold:
                memory.score = float(similarity)
                scored_memories.append(memory)
        
        # Sort by score and limit
        scored_memories.sort(key=lambda x: x.score, reverse=True)
        return scored_memories[:limit]
    
    async def delete(self, user_id: str, entry_id: str) -> bool:
        """
        Delete a memory entry.
        
        Returns:
            True if deleted
        """
        if self.use_qdrant and self.client:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=[entry_id]
            )
            return True
        else:
            initial_len = len(self._memory_store)
            self._memory_store = [
                m for m in self._memory_store 
                if not (m.id == entry_id and m.user_id == user_id)
            ]
            return len(self._memory_store) < initial_len
    
    async def delete_user_memories(self, user_id: str) -> int:
        """
        Delete all memories for a user.
        
        Returns:
            Number of memories deleted
        """
        if self.use_qdrant and self.client:
            # Qdrant batch delete by filter
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                )
            )
            return 0  # Can't get exact count easily
        else:
            initial_len = len(self._memory_store)
            self._memory_store = [
                m for m in self._memory_store if m.user_id != user_id
            ]
            return initial_len - len(self._memory_store)
    
    async def close(self):
        """Close Qdrant connection."""
        if self.client:
            await self.client.close()
            logger.info("Qdrant connection closed")
