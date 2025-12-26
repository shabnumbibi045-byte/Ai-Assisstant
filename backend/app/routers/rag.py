"""RAG Router - Document upload and query endpoints."""

import logging
import uuid
import os
from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, BackgroundTasks
from pydantic import BaseModel

from app.schemas import RAGQueryRequest, RAGQueryResponse
from app.rag.rag_pipeline import RAGPipeline
from app.rag.document_loader import DocumentLoader
from app.memory.vector_memory import VectorMemory
from app.llm.provider_factory import ProviderFactory, ProviderType
from app.config import settings
from app.auth.dependencies import get_current_active_user
from app.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])

# Ensure documents directory exists
DOCUMENTS_DIR = Path(settings.DOCUMENTS_DIR)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    status: str
    chunks_count: Optional[int] = None


class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
    total: int


async def get_rag_pipeline() -> RAGPipeline:
    """Get RAG pipeline instance."""
    # Get LLM provider for embeddings
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured for embeddings"
        )
    
    llm_provider = ProviderFactory.create_provider(
        provider_type=ProviderType.OPENAI,
        api_key=api_key,
        model=settings.DEFAULT_EMBEDDING_MODEL
    )
    
    vector_memory = VectorMemory(
        qdrant_url=settings.QDRANT_URL if settings.QDRANT_ENABLED else None,
        collection_name=settings.QDRANT_COLLECTION,
        vector_size=settings.QDRANT_VECTOR_SIZE
    )
    await vector_memory.init_collection()
    
    return RAGPipeline(
        llm_provider=llm_provider,
        vector_memory=vector_memory,
        chunk_size=settings.RAG_CHUNK_SIZE,
        overlap=settings.RAG_CHUNK_OVERLAP
    )


async def process_document_background(
    user_id: str,
    document_id: str,
    file_path: str,
    filename: str
):
    """Background task to process uploaded document."""
    try:
        pipeline = await get_rag_pipeline()
        
        result = await pipeline.ingest_document(
            user_id=user_id,
            file_path=file_path,
            document_metadata={
                "document_id": document_id,
                "filename": filename
            }
        )
        
        logger.info(f"Document processed: {filename}, {result.get('chunks_count', 0)} chunks")
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
    finally:
        # Optionally clean up the file after processing
        pass


@router.post("/upload", response_model=DocumentInfo)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload and process a document for RAG.
    
    Supported formats: PDF, DOCX, TXT, MD
    """
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.txt', '.md'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Check file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    
    if file_size_mb > settings.MAX_DOCUMENT_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_DOCUMENT_SIZE_MB}MB"
        )
    
    try:
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Save file
        user_dir = DOCUMENTS_DIR / current_user.user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = user_dir / f"{document_id}{file_ext}"
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Process document in background
        background_tasks.add_task(
            process_document_background,
            current_user.user_id,
            document_id,
            str(file_path),
            file.filename
        )
        
        return DocumentInfo(
            document_id=document_id,
            filename=file.filename,
            status="processing"
        )
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=RAGQueryResponse)
async def query_documents(
    request: RAGQueryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Query uploaded documents using semantic search.
    
    - **query**: Natural language question
    - **top_k**: Number of relevant chunks to retrieve
    """
    try:
        pipeline = await get_rag_pipeline()
        
        # Generate query embedding and search
        result = await pipeline.query(
            user_id=current_user.user_id,
            query=request.query,
            top_k=request.top_k
        )
        
        return RAGQueryResponse(
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
            chunks_used=result.get("chunks_used", 0)
        )
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    current_user: User = Depends(get_current_active_user)
):
    """List all uploaded documents for the current user."""
    try:
        user_dir = DOCUMENTS_DIR / current_user.user_id
        
        if not user_dir.exists():
            return DocumentListResponse(documents=[], total=0)
        
        documents = []
        for file_path in user_dir.iterdir():
            if file_path.is_file():
                doc_id = file_path.stem
                documents.append(DocumentInfo(
                    document_id=doc_id,
                    filename=file_path.name,
                    status="indexed"
                ))
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
        
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete an uploaded document."""
    try:
        user_dir = DOCUMENTS_DIR / current_user.user_id
        
        # Find and delete the file
        deleted = False
        for file_path in user_dir.iterdir():
            if file_path.stem == document_id:
                file_path.unlink()
                deleted = True
                break
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # TODO: Also delete chunks from vector store
        
        return {"status": "success", "message": "Document deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

