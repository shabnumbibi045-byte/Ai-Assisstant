"""Memory Router - Memory management endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.schemas import AddMemoryRequest, GetMemoryRequest
from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory, MemoryEntry
from app.memory.vector_memory import VectorMemory
from app.memory.memory_orchestrator import MemoryOrchestrator
from app.config import settings
from app.auth.dependencies import get_current_active_user
from app.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memory", tags=["memory"])


# Memory instances (initialized lazily)
_memory_orchestrator: Optional[MemoryOrchestrator] = None


async def get_memory_orchestrator() -> MemoryOrchestrator:
    """Get or create memory orchestrator instance."""
    global _memory_orchestrator
    
    if _memory_orchestrator is None:
        short_term = ShortTermMemory(
            redis_url=settings.REDIS_URL if settings.REDIS_ENABLED else None,
            max_messages=settings.SHORT_TERM_MAX_MESSAGES,
            ttl_hours=settings.SHORT_TERM_TTL_HOURS
        )
        
        long_term = LongTermMemory(database_url=settings.DATABASE_URL)
        await long_term.init_db()
        
        vector_memory = VectorMemory(
            qdrant_url=settings.QDRANT_URL if settings.QDRANT_ENABLED else None,
            collection_name=settings.QDRANT_COLLECTION,
            vector_size=settings.QDRANT_VECTOR_SIZE
        )
        await vector_memory.init_collection()
        
        _memory_orchestrator = MemoryOrchestrator(
            short_term=short_term,
            long_term=long_term,
            vector_memory=vector_memory
        )
    
    return _memory_orchestrator


class MemoryFactResponse(BaseModel):
    key: str
    value: str
    category: str
    confidence: int
    source: str


class ConversationHistoryResponse(BaseModel):
    messages: List[dict]
    count: int


@router.post("/add")
async def add_memory(
    request: AddMemoryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Store a user fact in long-term memory.
    
    - **key**: Fact identifier (e.g., "favorite_color")
    - **value**: Fact value (e.g., "blue")
    - **category**: Category (preference, personal, work, etc.)
    - **confidence**: Confidence score 0-100
    """
    try:
        orchestrator = await get_memory_orchestrator()
        
        await orchestrator.store_user_fact(
            user_id=current_user.user_id,
            key=request.key,
            value=request.value,
            category=request.category,
            confidence=request.confidence,
            source="explicit"
        )
        
        return {
            "status": "success",
            "message": f"Memory stored: {request.key}"
        }
    except Exception as e:
        logger.error(f"Add memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get", response_model=List[MemoryFactResponse])
async def get_memory(
    request: GetMemoryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve user memories.
    
    - **category**: Optional category filter
    """
    try:
        orchestrator = await get_memory_orchestrator()
        
        facts = await orchestrator.get_user_facts(
            user_id=current_user.user_id,
            category=request.category
        )
        
        return [
            MemoryFactResponse(
                key=f.key,
                value=f.value,
                category=f.category,
                confidence=f.confidence,
                source=f.source
            )
            for f in facts
        ]
    except Exception as e:
        logger.error(f"Get memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{session_id}")
async def get_conversation_history(
    session_id: str,
    limit: Optional[int] = 50,
    current_user: User = Depends(get_current_active_user)
):
    """Get conversation history for a session."""
    try:
        orchestrator = await get_memory_orchestrator()
        
        messages = await orchestrator.short_term.get_history(
            user_id=current_user.user_id,
            session_id=session_id,
            limit=limit
        )
        
        return {
            "messages": [m.to_dict() for m in messages],
            "count": len(messages)
        }
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/{session_id}")
async def clear_conversation(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Clear conversation history for a session."""
    try:
        orchestrator = await get_memory_orchestrator()
        
        await orchestrator.clear_session(
            user_id=current_user.user_id,
            session_id=session_id
        )
        
        return {"status": "success", "message": "Conversation cleared"}
    except Exception as e:
        logger.error(f"Clear conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/fact/{key}")
async def delete_memory_fact(
    key: str,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a memory fact."""
    try:
        orchestrator = await get_memory_orchestrator()
        
        deleted = await orchestrator.long_term.delete_fact(
            user_id=current_user.user_id,
            key=key,
            category=category
        )
        
        if deleted:
            return {"status": "success", "message": f"Fact deleted: {key}"}
        else:
            raise HTTPException(status_code=404, detail="Fact not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete fact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summaries")
async def get_conversation_summaries(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """Get recent conversation summaries."""
    try:
        orchestrator = await get_memory_orchestrator()
        
        summaries = await orchestrator.long_term.get_recent_summaries(
            user_id=current_user.user_id,
            limit=limit
        )
        
        return {"summaries": summaries}
    except Exception as e:
        logger.error(f"Get summaries error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

