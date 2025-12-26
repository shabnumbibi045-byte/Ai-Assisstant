"""Chat Router - Main conversation endpoint with authentication and memory."""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.auth.dependencies import get_current_user, get_current_verified_user
from app.database.models import User
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
    current_user: User = Depends(get_current_user)
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
        user_id = str(current_user.id)
        
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
