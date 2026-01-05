#!/usr/bin/env python3
"""Database Initialization Script - Create all database tables."""

import asyncio
import sys
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.database.models import Base
# Import all models to ensure they're registered with Base
from app.database import chat_models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def create_database():
    """Create database if it doesn't exist."""
    # Extract database name from URL
    db_url = settings.DATABASE_URL
    db_name = db_url.split('/')[-1]
    base_url = '/'.join(db_url.split('/')[:-1])

    # Connect without specifying database
    engine = create_async_engine(base_url + '/mysql', echo=False)

    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            # Check if database exists
            result = await conn.execute(
                text(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'")
            )
            exists = result.fetchone()

            if not exists:
                logger.info(f"Creating database: {db_name}")
                await conn.execute(text(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                logger.info(f"Database '{db_name}' created successfully")
            else:
                logger.info(f"Database '{db_name}' already exists")
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise
    finally:
        await engine.dispose()


async def init_tables():
    """Initialize all database tables."""
    logger.info(f"Connecting to database: {settings.DATABASE_URL}")

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        pool_pre_ping=True
    )

    try:
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully!")

        # Verify tables were created
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Created tables: {', '.join(tables)}")

    except Exception as e:
        logger.error(f"Error initializing tables: {e}")
        raise
    finally:
        await engine.dispose()


async def main():
    """Main function."""
    try:
        logger.info("=" * 60)
        logger.info("Starting Database Initialization")
        logger.info("=" * 60)

        # Step 1: Create database
        await create_database()

        # Step 2: Create tables
        await init_tables()

        logger.info("=" * 60)
        logger.info("Database initialization completed successfully!")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"Database initialization failed: {e}")
        logger.error("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
