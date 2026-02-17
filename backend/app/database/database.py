"""Database Manager - Database connection and session management."""

import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

logger = logging.getLogger(__name__)


def _build_engine_kwargs(database_url: str) -> dict:
    """Build engine kwargs based on database type."""
    kwargs = {
        "echo": settings.DATABASE_ECHO,
    }
    # SQLite doesn't support pool_size/max_overflow/pool_pre_ping
    if "sqlite" not in database_url:
        kwargs["pool_pre_ping"] = True
        kwargs["pool_size"] = 10
        kwargs["max_overflow"] = 20
    return kwargs


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url: str = None):
        """Initialize database manager."""
        self.database_url = database_url or settings.DATABASE_URL
        engine_kwargs = _build_engine_kwargs(self.database_url)
        self.engine = create_async_engine(
            self.database_url,
            **engine_kwargs
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


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncSession:
    """Dependency for getting database session."""
    async with db_manager.async_session_maker() as session:
        yield session
