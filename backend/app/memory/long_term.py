"""Long-term Memory - Persistent storage of user facts, preferences, and structured data."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, select, update, delete

logger = logging.getLogger(__name__)

Base = declarative_base()


class UserFact(Base):
    """Stores learned facts about users."""
    __tablename__ = "user_facts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    category = Column(String(100), index=True)  # 'preference', 'personal', 'work', etc.
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    confidence = Column(Integer, default=100)  # 0-100 confidence score
    source = Column(String(50))  # 'explicit', 'inferred', 'corrected'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON)


class ConversationSummary(Base):
    """Stores summarized past conversations."""
    __tablename__ = "conversation_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    session_id = Column(String(255), index=True, nullable=False)
    summary = Column(Text, nullable=False)
    key_topics = Column(JSON)  # List of main topics
    action_items = Column(JSON)  # List of action items extracted
    sentiment = Column(String(50))  # 'positive', 'neutral', 'negative'
    message_count = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


@dataclass
class MemoryEntry:
    """Represents a memory entry."""
    key: str
    value: str
    category: str
    confidence: int = 100
    source: str = "explicit"
    metadata: Optional[Dict[str, Any]] = None


class LongTermMemory:
    """
    Manages persistent storage of structured user information.
    
    Stores:
    - User preferences and facts
    - Conversation summaries
    - Learned patterns
    - Historical data
    """
    
    def __init__(self, database_url: str):
        """
        Initialize long-term memory with database connection.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("LongTermMemory initialized")
    
    async def init_db(self):
        """Create database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    
    async def store_fact(
        self,
        user_id: str,
        key: str,
        value: str,
        category: str = "general",
        confidence: int = 100,
        source: str = "explicit",
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Store a user fact.
        
        Args:
            user_id: User identifier
            key: Fact key/name
            value: Fact value
            category: Category (preference, personal, work, etc.)
            confidence: Confidence score (0-100)
            source: How fact was learned
            metadata: Additional metadata
            
        Returns:
            Fact ID
        """
        async with self.async_session() as session:
            # Check if fact exists
            stmt = select(UserFact).where(
                UserFact.user_id == user_id,
                UserFact.key == key,
                UserFact.category == category,
                UserFact.is_active == True
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing fact
                existing.value = value
                existing.confidence = confidence
                existing.source = source
                existing.metadata = metadata
                existing.updated_at = datetime.utcnow()
                fact_id = existing.id
                logger.debug(f"Updated fact {key} for user {user_id}")
            else:
                # Create new fact
                fact = UserFact(
                    user_id=user_id,
                    key=key,
                    value=value,
                    category=category,
                    confidence=confidence,
                    source=source,
                    metadata=metadata
                )
                session.add(fact)
                await session.flush()
                fact_id = fact.id
                logger.debug(f"Stored new fact {key} for user {user_id}")
            
            await session.commit()
            return fact_id
    
    async def get_fact(
        self,
        user_id: str,
        key: str,
        category: Optional[str] = None
    ) -> Optional[MemoryEntry]:
        """
        Retrieve a specific fact.
        
        Args:
            user_id: User identifier
            key: Fact key
            category: Optional category filter
            
        Returns:
            MemoryEntry or None
        """
        async with self.async_session() as session:
            stmt = select(UserFact).where(
                UserFact.user_id == user_id,
                UserFact.key == key,
                UserFact.is_active == True
            )
            
            if category:
                stmt = stmt.where(UserFact.category == category)
            
            result = await session.execute(stmt)
            fact = result.scalar_one_or_none()
            
            if fact:
                return MemoryEntry(
                    key=fact.key,
                    value=fact.value,
                    category=fact.category,
                    confidence=fact.confidence,
                    source=fact.source,
                    metadata=fact.metadata
                )
            
            return None
    
    async def get_facts_by_category(
        self,
        user_id: str,
        category: str
    ) -> List[MemoryEntry]:
        """Get all facts in a category."""
        async with self.async_session() as session:
            stmt = select(UserFact).where(
                UserFact.user_id == user_id,
                UserFact.category == category,
                UserFact.is_active == True
            ).order_by(UserFact.updated_at.desc())
            
            result = await session.execute(stmt)
            facts = result.scalars().all()
            
            return [
                MemoryEntry(
                    key=f.key,
                    value=f.value,
                    category=f.category,
                    confidence=f.confidence,
                    source=f.source,
                    metadata=f.metadata
                )
                for f in facts
            ]
    
    async def get_all_facts(self, user_id: str) -> List[MemoryEntry]:
        """Get all active facts for a user."""
        async with self.async_session() as session:
            stmt = select(UserFact).where(
                UserFact.user_id == user_id,
                UserFact.is_active == True
            ).order_by(UserFact.category, UserFact.updated_at.desc())
            
            result = await session.execute(stmt)
            facts = result.scalars().all()
            
            return [
                MemoryEntry(
                    key=f.key,
                    value=f.value,
                    category=f.category,
                    confidence=f.confidence,
                    source=f.source,
                    metadata=f.metadata
                )
                for f in facts
            ]
    
    async def search_facts(
        self,
        user_id: str,
        query: str,
        category: Optional[str] = None
    ) -> List[MemoryEntry]:
        """
        Search facts by keyword.
        
        Args:
            user_id: User identifier
            query: Search query
            category: Optional category filter
            
        Returns:
            List of matching MemoryEntry objects
        """
        async with self.async_session() as session:
            stmt = select(UserFact).where(
                UserFact.user_id == user_id,
                UserFact.is_active == True,
                (UserFact.key.ilike(f"%{query}%") | UserFact.value.ilike(f"%{query}%"))
            )
            
            if category:
                stmt = stmt.where(UserFact.category == category)
            
            stmt = stmt.order_by(UserFact.confidence.desc(), UserFact.updated_at.desc())
            
            result = await session.execute(stmt)
            facts = result.scalars().all()
            
            return [
                MemoryEntry(
                    key=f.key,
                    value=f.value,
                    category=f.category,
                    confidence=f.confidence,
                    source=f.source,
                    metadata=f.metadata
                )
                for f in facts
            ]
    
    async def delete_fact(
        self,
        user_id: str,
        key: str,
        category: Optional[str] = None
    ) -> bool:
        """
        Soft delete a fact (marks as inactive).
        
        Returns:
            True if fact was deleted
        """
        async with self.async_session() as session:
            stmt = update(UserFact).where(
                UserFact.user_id == user_id,
                UserFact.key == key,
                UserFact.is_active == True
            ).values(is_active=False)
            
            if category:
                stmt = stmt.where(UserFact.category == category)
            
            result = await session.execute(stmt)
            await session.commit()
            
            return result.rowcount > 0
    
    async def store_conversation_summary(
        self,
        user_id: str,
        session_id: str,
        summary: str,
        key_topics: List[str],
        action_items: List[str],
        sentiment: str,
        message_count: int,
        start_time: datetime,
        end_time: datetime
    ) -> int:
        """Store a conversation summary."""
        async with self.async_session() as session:
            conv_summary = ConversationSummary(
                user_id=user_id,
                session_id=session_id,
                summary=summary,
                key_topics=key_topics,
                action_items=action_items,
                sentiment=sentiment,
                message_count=message_count,
                start_time=start_time,
                end_time=end_time
            )
            session.add(conv_summary)
            await session.flush()
            summary_id = conv_summary.id
            await session.commit()
            
            logger.info(f"Stored conversation summary for {user_id}/{session_id}")
            return summary_id
    
    async def get_recent_summaries(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent conversation summaries."""
        async with self.async_session() as session:
            stmt = select(ConversationSummary).where(
                ConversationSummary.user_id == user_id
            ).order_by(ConversationSummary.end_time.desc()).limit(limit)
            
            result = await session.execute(stmt)
            summaries = result.scalars().all()
            
            return [
                {
                    "session_id": s.session_id,
                    "summary": s.summary,
                    "key_topics": s.key_topics,
                    "action_items": s.action_items,
                    "sentiment": s.sentiment,
                    "start_time": s.start_time.isoformat(),
                    "end_time": s.end_time.isoformat()
                }
                for s in summaries
            ]
    
    async def get_conversation_summaries(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get conversation summaries (alias for get_recent_summaries).
        
        Args:
            user_id: User identifier
            limit: Maximum summaries to return
            
        Returns:
            List of summary dictionaries
        """
        return await self.get_recent_summaries(user_id, limit)
    
    async def close(self):
        """Close database connection."""
        await self.engine.dispose()
        logger.info("Database connection closed")
