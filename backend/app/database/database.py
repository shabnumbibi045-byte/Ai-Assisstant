"""Database Manager - Database connection and session management."""

import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url: str = None):
        """Initialize database manager."""
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = create_async_engine(
            self.database_url,
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("Database manager initialized")
    
    async def init_db(self):
        """Initialize database tables."""
        from .models import Base
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        async with self.async_session_maker() as session:
            yield session
    
    async def close(self):
        """Close database connections."""
        await self.engine.dispose()
        logger.info("Database connections closed")
