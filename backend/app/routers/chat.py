"""Chat Router - Main conversation endpoint with authentication and memory."""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.auth.dependencies import get_current_user, get_current_verified_user
from app.database.models import User
from app.database.chat_models import ChatSession, ChatMessage
from app.database.database import get_db_session
from app.memory.memory_orchestrator import MemoryOrchestrator
from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory
from app.memory.vector_memory import VectorMemory
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


# ============================================
# ADDITIONAL SCHEMAS
# ============================================

class AuthenticatedChatRequest(BaseModel):
    """Chat request with session management."""
    message: str
    session_id: Optional[str] = None
    module: Optional[str] = None
    use_rag: bool = False
    use_tools: bool = True
    use_memory: bool = True
    include_context: bool = True


class ConversationMessage(BaseModel):
    """Individual message in conversation."""
    role: str
    content: str
    timestamp: datetime
    tool_calls: Optional[List[Dict]] = None


class ConversationHistory(BaseModel):
    """Conversation history response."""
    session_id: str
    user_id: str
    messages: List[ConversationMessage]
    message_count: int
    started_at: datetime
    last_message_at: datetime


class ChatSummary(BaseModel):
    """Summary of recent chat activity."""
    total_sessions: int
    total_messages: int
    recent_sessions: List[Dict[str, Any]]


# ============================================
# MEMORY ORCHESTRATOR SETUP
# ============================================

_memory_orchestrator: Optional[MemoryOrchestrator] = None


async def get_or_create_chat_session(
    db: AsyncSession,
    session_id: str,
    user_id: int,
    first_message: str = None
) -> ChatSession:
    """Get existing chat session or create a new one."""
    result = await db.execute(
        select(ChatSession).where(ChatSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        # Generate title from first message (first 50 chars)
        title = None
        if first_message:
            title = first_message[:50] + "..." if len(first_message) > 50 else first_message

        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            title=title,
            message_count=0
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    return session


async def save_chat_message(
    db: AsyncSession,
    session: ChatSession,
    role: str,
    content: str,
    tokens_used: int = 0
) -> ChatMessage:
    """Save a chat message to the database."""
    message = ChatMessage(
        session_id=session.id,
        role=role,
        content=content,
        tokens_used=tokens_used
    )
    db.add(message)

    # Update session
    session.message_count += 1
    session.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(message)

    return message


async def get_memory_orchestrator() -> MemoryOrchestrator:
    """Get or create memory orchestrator instance."""
    global _memory_orchestrator
    
    if _memory_orchestrator is None:
        try:
            short_term = ShortTermMemory(
                redis_url=settings.REDIS_URL,
                ttl_seconds=3600
            )
            long_term = LongTermMemory(
                database_url=settings.DATABASE_URL
            )
            vector = VectorMemory(
                qdrant_url=settings.QDRANT_URL
            )
            
            _memory_orchestrator = MemoryOrchestrator(
                short_term=short_term,
                long_term=long_term,
                vector_memory=vector
            )
            
            logger.info("Memory orchestrator initialized for chat")
        except Exception as e:
            logger.warning(f"Memory orchestrator initialization failed: {e}")
            _memory_orchestrator = None
    
    return _memory_orchestrator


# ============================================
# CHAT ENDPOINTS
# ============================================

@router.post("/", response_model=ChatResponse)
async def chat(
    request: AuthenticatedChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Main chat endpoint with authentication.

    Handles:
    - Conversation with LLM
    - Memory retrieval and storage
    - RAG if enabled
    - Tool execution if enabled
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        # Use user_id (UUID) instead of id (integer) for consistency with PlaidAccount
        user_id = current_user.user_id

        # Get or create chat session in database
        chat_session = await get_or_create_chat_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            first_message=request.message
        )
        
        # Get memory orchestrator
        memory = await get_memory_orchestrator()
        
        # Build context from memory
        context = ""
        if request.use_memory and memory:
            try:
                # Get conversation history
                history = await memory.get_conversation(
                    user_id=user_id,
                    session_id=session_id,
                    max_messages=10
                )
                
                if history:
                    context = "\n".join([
                        f"{msg['role']}: {msg['content']}" 
                        for msg in history
                    ])
                
                # Get relevant facts
                facts = await memory.get_relevant_context(
                    user_id=user_id,
                    query=request.message,
                    top_k=5
                )
                
                if facts:
                    context += "\n\nRelevant context:\n" + "\n".join(facts)
                    
            except Exception as e:
                logger.warning(f"Memory retrieval error: {e}")
        
        # Create chat request for service
        chat_request = ChatRequest(
            user_id=user_id,
            session_id=session_id,
            message=request.message,
            module=request.module,
            use_rag=request.use_rag,
            use_tools=request.use_tools
        )
        
        # Process with chat service
        chat_service = ChatService()
        
        # Inject context if available
        if context and request.include_context:
            chat_request.message = f"Context:\n{context}\n\nUser message: {request.message}"
        
        response = await chat_service.process_message(chat_request)

        # Save messages to database
        try:
            # Save user message
            await save_chat_message(
                db=db,
                session=chat_session,
                role="user",
                content=request.message,
                tokens_used=0
            )

            # Save assistant response
            await save_chat_message(
                db=db,
                session=chat_session,
                role="assistant",
                content=response.response,
                tokens_used=response.tokens_used if hasattr(response, 'tokens_used') else 0
            )

            logger.info(f"Messages saved to database for session {session_id}")
        except Exception as e:
            logger.warning(f"Database storage error: {e}")

        # Store in memory
        if request.use_memory and memory:
            try:
                # Store user message
                await memory.store_message(
                    user_id=user_id,
                    session_id=session_id,
                    role="user",
                    content=request.message
                )

                # Store assistant response
                await memory.store_message(
                    user_id=user_id,
                    session_id=session_id,
                    role="assistant",
                    content=response.response
                )
            except Exception as e:
                logger.warning(f"Memory storage error: {e}")

        logger.info(f"Chat processed for user {user_id}, session {session_id}")

        return response
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_conversation_history(
    session_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get conversation history for a session."""
    try:
        user_id = str(current_user.id)
        memory = await get_memory_orchestrator()
        
        if not memory:
            raise HTTPException(
                status_code=503,
                detail="Memory service unavailable"
            )
        
        history = await memory.get_conversation(
            user_id=user_id,
            session_id=session_id,
            max_messages=limit
        )
        
        if not history:
            return ConversationHistory(
                session_id=session_id,
                user_id=user_id,
                messages=[],
                message_count=0,
                started_at=datetime.utcnow(),
                last_message_at=datetime.utcnow()
            )
        
        messages = [
            ConversationMessage(
                role=msg.get("role", "unknown"),
                content=msg.get("content", ""),
                timestamp=msg.get("timestamp", datetime.utcnow()),
                tool_calls=msg.get("tool_calls")
            )
            for msg in history
        ]
        
        return ConversationHistory(
            session_id=session_id,
            user_id=user_id,
            messages=messages,
            message_count=len(messages),
            started_at=messages[0].timestamp if messages else datetime.utcnow(),
            last_message_at=messages[-1].timestamp if messages else datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_sessions(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """List recent chat sessions for the user."""
    try:
        user_id = str(current_user.id)
        memory = await get_memory_orchestrator()
        
        if not memory:
            return {"sessions": [], "total": 0}
        
        # Get session summaries from memory
        sessions = await memory.get_session_summaries(
            user_id=user_id,
            limit=limit
        )
        
        return {
            "sessions": sessions,
            "total": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"List sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a chat session and its history."""
    try:
        user_id = str(current_user.id)
        memory = await get_memory_orchestrator()
        
        if not memory:
            raise HTTPException(
                status_code=503,
                detail="Memory service unavailable"
            )
        
        await memory.clear_conversation(
            user_id=user_id,
            session_id=session_id
        )
        
        return {
            "status": "success",
            "message": f"Session {session_id} deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(
    session_id: str,
    message_index: int,
    rating: int,
    comment: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Submit feedback for a chat response."""
    try:
        if rating < 1 or rating > 5:
            raise HTTPException(
                status_code=400,
                detail="Rating must be between 1 and 5"
            )
        
        # TODO: Store feedback in database
        logger.info(
            f"Feedback received: user={current_user.id}, "
            f"session={session_id}, rating={rating}"
        )
        
        return {
            "status": "success",
            "message": "Feedback submitted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_chat_stats(
    current_user: User = Depends(get_current_user)
):
    """Get chat statistics for the user."""
    try:
        user_id = str(current_user.id)
        memory = await get_memory_orchestrator()

        if not memory:
            return {
                "total_sessions": 0,
                "total_messages": 0,
                "tokens_used_today": 0,
                "most_used_module": None
            }

        # Get stats from memory
        stats = await memory.get_user_stats(user_id=user_id)

        return stats

    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# DATABASE CHAT HISTORY ENDPOINTS
# ============================================

@router.get("/db/sessions")
async def get_database_sessions(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get chat sessions from database."""
    try:
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == current_user.id)
            .order_by(ChatSession.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        sessions = result.scalars().all()

        count_result = await db.execute(
            select(ChatSession).where(ChatSession.user_id == current_user.id)
        )
        total = len(count_result.scalars().all())

        return {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "title": s.title,
                    "message_count": s.message_count,
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat()
                }
                for s in sessions
            ],
            "total": total
        }

    except Exception as e:
        logger.error(f"Get database sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/db/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get messages for a specific chat session from database."""
    try:
        # Verify session belongs to user
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.session_id == session_id,
                ChatSession.user_id == current_user.id
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        messages_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        messages = messages_result.scalars().all()

        return {
            "session_id": session_id,
            "title": session.title,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                    "tokens_used": m.tokens_used
                }
                for m in messages
            ],
            "total_messages": session.message_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session messages error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/db/sessions/{session_id}")
async def delete_database_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a chat session from database."""
    try:
        # Verify session belongs to user
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.session_id == session_id,
                ChatSession.user_id == current_user.id
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Delete session (cascade will delete messages)
        db.delete(session)
        await db.commit()

        logger.info(f"Deleted session {session_id} for user {current_user.id}")

        return {
            "status": "success",
            "message": f"Session {session_id} deleted"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete database session error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
