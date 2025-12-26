"""Short-term Memory - Redis-based conversation history and session state."""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import asyncio

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("redis not installed, using in-memory fallback")

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a single message in conversation history."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create Message from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


class ShortTermMemory:
    """
    Manages short-term conversation history and session state.
    
    Uses Redis for distributed caching with in-memory fallback.
    Stores recent messages (last N messages or time window).
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        max_messages: int = 50,
        ttl_hours: int = 24,
        use_redis: bool = True
    ):
        """
        Initialize short-term memory.
        
        Args:
            redis_url: Redis connection URL
            max_messages: Maximum messages to keep per session
            ttl_hours: Time-to-live for session data
            use_redis: Whether to use Redis (falls back to memory if False or unavailable)
        """
        self.max_messages = max_messages
        self.ttl_seconds = ttl_hours * 3600
        self.use_redis = use_redis and REDIS_AVAILABLE
        
        # Redis client
        self.redis_client: Optional[aioredis.Redis] = None
        if self.use_redis and redis_url:
            try:
                self.redis_client = aioredis.from_url(
                    redis_url,
                    decode_responses=True,
                    encoding="utf-8"
                )
                logger.info("Redis client initialized for short-term memory")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}, using in-memory fallback")
                self.use_redis = False
        else:
            self.use_redis = False
        
        # In-memory fallback
        self._memory_store: Dict[str, List[Message]] = {}
        
        logger.info(f"ShortTermMemory initialized (Redis: {self.use_redis})")
    
    def _get_key(self, user_id: str, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"stm:{user_id}:{session_id}"
    
    async def add_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a message to conversation history.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional metadata
        """
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        
        if self.use_redis and self.redis_client:
            await self._add_message_redis(user_id, session_id, message)
        else:
            await self._add_message_memory(user_id, session_id, message)
        
        logger.debug(f"Added message for {user_id}/{session_id}: {role}")
    
    async def _add_message_redis(
        self,
        user_id: str,
        session_id: str,
        message: Message
    ) -> None:
        """Add message using Redis."""
        key = self._get_key(user_id, session_id)
        message_json = json.dumps(message.to_dict())
        
        # Add to list
        await self.redis_client.rpush(key, message_json)
        
        # Trim to max size
        await self.redis_client.ltrim(key, -self.max_messages, -1)
        
        # Set expiration
        await self.redis_client.expire(key, self.ttl_seconds)
    
    async def _add_message_memory(
        self,
        user_id: str,
        session_id: str,
        message: Message
    ) -> None:
        """Add message using in-memory store."""
        key = f"{user_id}:{session_id}"
        
        if key not in self._memory_store:
            self._memory_store[key] = []
        
        self._memory_store[key].append(message)
        
        # Trim to max size
        if len(self._memory_store[key]) > self.max_messages:
            self._memory_store[key] = self._memory_store[key][-self.max_messages:]
    
    async def get_history(
        self,
        user_id: str,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Retrieve conversation history.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            limit: Maximum messages to return (None = all)
            
        Returns:
            List of Message objects
        """
        if self.use_redis and self.redis_client:
            messages = await self._get_history_redis(user_id, session_id)
        else:
            messages = await self._get_history_memory(user_id, session_id)
        
        if limit:
            messages = messages[-limit:]
        
        logger.debug(f"Retrieved {len(messages)} messages for {user_id}/{session_id}")
        return messages
    
    async def _get_history_redis(
        self,
        user_id: str,
        session_id: str
    ) -> List[Message]:
        """Get history from Redis."""
        key = self._get_key(user_id, session_id)
        messages_json = await self.redis_client.lrange(key, 0, -1)
        
        messages = []
        for msg_json in messages_json:
            msg_dict = json.loads(msg_json)
            messages.append(Message.from_dict(msg_dict))
        
        return messages
    
    async def _get_history_memory(
        self,
        user_id: str,
        session_id: str
    ) -> List[Message]:
        """Get history from memory."""
        key = f"{user_id}:{session_id}"
        return self._memory_store.get(key, [])
    
    async def get_recent_context(
        self,
        user_id: str,
        session_id: str,
        max_tokens: int = 2000
    ) -> List[Dict[str, str]]:
        """
        Get recent messages formatted for LLM context.
        
        Retrieves most recent messages up to token limit.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            max_tokens: Approximate max tokens (rough estimate: 1 token ≈ 4 chars)
            
        Returns:
            List of message dicts for LLM
        """
        messages = await self.get_history(user_id, session_id)
        
        # Convert to LLM format
        context = []
        total_chars = 0
        max_chars = max_tokens * 4  # Rough approximation
        
        # Start from most recent
        for message in reversed(messages):
            msg_dict = {"role": message.role, "content": message.content}
            msg_chars = len(message.content)
            
            if total_chars + msg_chars > max_chars and context:
                break
            
            context.insert(0, msg_dict)
            total_chars += msg_chars
        
        return context
    
    async def clear_session(self, user_id: str, session_id: str) -> None:
        """Clear all messages for a session."""
        if self.use_redis and self.redis_client:
            key = self._get_key(user_id, session_id)
            await self.redis_client.delete(key)
        else:
            key = f"{user_id}:{session_id}"
            if key in self._memory_store:
                del self._memory_store[key]
        
        logger.info(f"Cleared session {user_id}/{session_id}")
    
    async def get_session_count(self, user_id: str) -> int:
        """Get number of active sessions for user."""
        if self.use_redis and self.redis_client:
            pattern = f"stm:{user_id}:*"
            keys = await self.redis_client.keys(pattern)
            return len(keys)
        else:
            pattern = f"{user_id}:"
            return sum(1 for key in self._memory_store.keys() if key.startswith(pattern))
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
