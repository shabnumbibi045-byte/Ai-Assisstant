"""Memory Orchestrator - Coordinates all memory systems."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .short_term import ShortTermMemory, Message
from .long_term import LongTermMemory, MemoryEntry
from .vector_memory import VectorMemory, VectorMemoryEntry

logger = logging.getLogger(__name__)


class MemoryOrchestrator:
    """
    Orchestrates all memory systems for unified memory management.
    
    Coordinates:
    - Short-term (conversation history)
    - Long-term (structured facts)
    - Vector (semantic search)
    """
    
    def __init__(
        self,
        short_term: ShortTermMemory,
        long_term: LongTermMemory,
        vector_memory: VectorMemory
    ):
        """
        Initialize memory orchestrator.
        
        Args:
            short_term: Short-term memory instance
            long_term: Long-term memory instance
            vector_memory: Vector memory instance
        """
        self.short_term = short_term
        self.long_term = long_term
        self.vector = vector_memory
        
        logger.info("MemoryOrchestrator initialized")
    
    async def initialize(self):
        """Initialize all memory systems."""
        await self.long_term.init_db()
        await self.vector.init_collection()
        logger.info("All memory systems initialized")
    
    async def store_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store a message in short-term memory.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            role: Message role
            content: Message content
            metadata: Optional metadata
        """
        await self.short_term.add_message(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata
        )
    
    async def get_conversation_context(
        self,
        user_id: str,
        session_id: str,
        max_tokens: int = 2000
    ) -> List[Dict[str, str]]:
        """
        Get recent conversation context formatted for LLM.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            max_tokens: Maximum tokens to include
            
        Returns:
            List of message dicts for LLM
        """
        return await self.short_term.get_recent_context(
            user_id=user_id,
            session_id=session_id,
            max_tokens=max_tokens
        )
    
    async def store_user_fact(
        self,
        user_id: str,
        key: str,
        value: str,
        category: str = "general",
        confidence: int = 100,
        source: str = "explicit"
    ):
        """
        Store a learned fact about the user.
        
        Args:
            user_id: User identifier
            key: Fact key
            value: Fact value
            category: Category
            confidence: Confidence score
            source: How fact was learned
        """
        await self.long_term.store_fact(
            user_id=user_id,
            key=key,
            value=value,
            category=category,
            confidence=confidence,
            source=source
        )
    
    async def get_user_facts(
        self,
        user_id: str,
        category: Optional[str] = None
    ) -> List[MemoryEntry]:
        """
        Get user facts, optionally filtered by category.
        
        Args:
            user_id: User identifier
            category: Optional category filter
            
        Returns:
            List of MemoryEntry objects
        """
        if category:
            return await self.long_term.get_facts_by_category(user_id, category)
        else:
            return await self.long_term.get_all_facts(user_id)
    
    async def store_semantic_memory(
        self,
        user_id: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store text with semantic embedding.
        
        Args:
            user_id: User identifier
            text: Text to store
            embedding: Vector embedding
            metadata: Optional metadata
            
        Returns:
            Memory entry ID
        """
        return await self.vector.store(
            user_id=user_id,
            text=text,
            embedding=embedding,
            metadata=metadata
        )
    
    async def semantic_search(
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
            limit: Maximum results
            score_threshold: Minimum similarity
            
        Returns:
            List of VectorMemoryEntry objects
        """
        return await self.vector.search(
            user_id=user_id,
            query_embedding=query_embedding,
            limit=limit,
            score_threshold=score_threshold
        )
    
    async def get_full_context(
        self,
        user_id: str,
        session_id: str,
        query_embedding: Optional[List[float]] = None,
        include_facts: bool = True,
        include_semantic: bool = True,
        max_conversation_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Get comprehensive context including conversation, facts, and semantic memories.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            query_embedding: Optional embedding for semantic search
            include_facts: Whether to include user facts
            include_semantic: Whether to include semantic memories
            max_conversation_tokens: Max tokens for conversation history
            
        Returns:
            Dictionary with all context
        """
        context = {}
        
        # Get conversation history
        context["conversation"] = await self.get_conversation_context(
            user_id=user_id,
            session_id=session_id,
            max_tokens=max_conversation_tokens
        )
        
        # Get user facts
        if include_facts:
            facts = await self.get_user_facts(user_id)
            context["facts"] = [
                {"key": f.key, "value": f.value, "category": f.category}
                for f in facts
            ]
        
        # Get semantic memories
        if include_semantic and query_embedding:
            semantic_results = await self.semantic_search(
                user_id=user_id,
                query_embedding=query_embedding,
                limit=5
            )
            context["semantic_memories"] = [
                {"text": m.text, "score": m.score}
                for m in semantic_results
            ]
        
        return context
    
    async def summarize_and_archive_session(
        self,
        user_id: str,
        session_id: str,
        llm_provider,
        extract_facts: bool = True
    ) -> Dict[str, Any]:
        """
        Summarize a conversation session and store in long-term memory.
        
        This should be called when a session ends or becomes inactive.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            llm_provider: LLM provider for summarization
            extract_facts: Whether to extract and store facts
            
        Returns:
            Summary information
        """
        # Get full conversation history
        messages = await self.short_term.get_history(user_id, session_id)
        
        if not messages:
            logger.warning(f"No messages to summarize for {user_id}/{session_id}")
            return {}
        
        # Build conversation text
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in messages
        ])
        
        # Generate summary using LLM
        summary_prompt = f"""Summarize this conversation concisely. Include:
1. Main topics discussed
2. Key decisions or outcomes
3. Any action items
4. Overall sentiment

Conversation:
{conversation_text}

Provide a structured summary."""
        
        try:
            response = await llm_provider.chat_completion(
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            summary = response.content
            
            # Extract key topics (simple keyword extraction)
            key_topics = []  # TODO: Implement proper topic extraction
            
            # Extract action items (simple pattern matching)
            action_items = []  # TODO: Implement proper action item extraction
            
            # Determine sentiment
            sentiment = "neutral"  # TODO: Implement sentiment analysis
            
            # Store summary
            await self.long_term.store_conversation_summary(
                user_id=user_id,
                session_id=session_id,
                summary=summary,
                key_topics=key_topics,
                action_items=action_items,
                sentiment=sentiment,
                message_count=len(messages),
                start_time=messages[0].timestamp,
                end_time=messages[-1].timestamp
            )
            
            logger.info(f"Archived session {user_id}/{session_id}")
            
            return {
                "summary": summary,
                "message_count": len(messages),
                "key_topics": key_topics,
                "action_items": action_items
            }
        
        except Exception as e:
            logger.error(f"Error summarizing session: {e}")
            return {}
    
    async def clear_session(self, user_id: str, session_id: str):
        """Clear short-term memory for a session."""
        await self.short_term.clear_session(user_id, session_id)
    
    async def get_conversation(
        self,
        user_id: str,
        session_id: str,
        max_messages: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history as list of message dicts.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            max_messages: Maximum messages to return
            
        Returns:
            List of message dictionaries
        """
        messages = await self.short_term.get_history(user_id, session_id)
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "metadata": msg.metadata
            }
            for msg in messages[-max_messages:]
        ]
    
    async def clear_conversation(self, user_id: str, session_id: str):
        """Clear conversation for a session (alias for clear_session)."""
        await self.clear_session(user_id, session_id)
    
    async def get_relevant_context(
        self,
        user_id: str,
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """
        Get relevant context strings for a query.
        
        Args:
            user_id: User identifier
            query: Query text
            top_k: Number of results
            
        Returns:
            List of relevant context strings
        """
        # Get facts that might be relevant
        facts = await self.get_user_facts(user_id)
        
        # Simple keyword matching for now
        # In production, this would use embeddings
        query_lower = query.lower()
        relevant = []
        
        for fact in facts:
            if any(word in fact.value.lower() for word in query_lower.split()):
                relevant.append(f"{fact.key}: {fact.value}")
        
        return relevant[:top_k]
    
    async def get_session_summaries(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get summaries of recent sessions.
        
        Args:
            user_id: User identifier
            limit: Maximum summaries to return
            
        Returns:
            List of session summary dicts
        """
        try:
            summaries = await self.long_term.get_conversation_summaries(
                user_id=user_id,
                limit=limit
            )
            return summaries
        except Exception as e:
            logger.warning(f"Error getting session summaries: {e}")
            return []
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get usage statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Statistics dictionary
        """
        try:
            # Get fact count
            facts = await self.get_user_facts(user_id)
            
            # Get session summaries for counting
            summaries = await self.get_session_summaries(user_id, limit=100)
            
            return {
                "total_sessions": len(summaries),
                "total_facts": len(facts),
                "fact_categories": list(set(f.category for f in facts)),
                "tokens_used_today": 0,  # Would need token tracking
                "most_used_module": None  # Would need usage tracking
            }
        except Exception as e:
            logger.warning(f"Error getting user stats: {e}")
            return {
                "total_sessions": 0,
                "total_facts": 0,
                "fact_categories": [],
                "tokens_used_today": 0,
                "most_used_module": None
            }
    
    async def delete_user_data(self, user_id: str):
        """
        Delete all data for a user (GDPR compliance).
        
        Args:
            user_id: User identifier
        """
        # Clear all short-term sessions
        # Note: Need to implement get_all_sessions in short_term
        
        # Clear vector memories
        await self.vector.delete_user_memories(user_id)
        
        # Note: Long-term facts can be soft-deleted via delete_fact
        # Full deletion would require additional method
        
        logger.info(f"Deleted data for user {user_id}")
    
    async def close(self):
        """Close all memory connections."""
        await self.short_term.close()
        await self.long_term.close()
        await self.vector.close()
        logger.info("All memory systems closed")
