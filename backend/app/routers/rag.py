"""RAG Router - Document upload and query endpoints."""

import logging
import uuid
import os
import io
from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
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
        
        # Save original filename metadata
        import json as _json
        meta_path = user_dir / f"{document_id}.meta.json"
        with open(meta_path, 'w') as mf:
            _json.dump({"original_filename": file.filename}, mf)
        
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
        
    except ConnectionError:
        logger.warning("Vector store (Qdrant) not available for RAG query")
        return RAGQueryResponse(
            answer="Document query is currently unavailable. The vector database (Qdrant) is not connected. Your documents are stored and can be summarized directly.",
            sources=[],
            chunks_used=0
        )
    except Exception as e:
        if "connection" in str(e).lower():
            logger.warning(f"Vector store connection error: {e}")
            return RAGQueryResponse(
                answer="Document query is currently unavailable. The vector database (Qdrant) is not connected. Your documents are stored and can be summarized directly.",
                sources=[],
                chunks_used=0
            )
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
        import json as _json
        for file_path in user_dir.iterdir():
            if file_path.is_file() and not file_path.name.endswith('.meta.json'):
                doc_id = file_path.stem
                # Try to read original filename from metadata
                meta_path = user_dir / f"{doc_id}.meta.json"
                original_name = file_path.name
                if meta_path.exists():
                    try:
                        with open(meta_path, 'r') as mf:
                            meta = _json.load(mf)
                            original_name = meta.get('original_filename', file_path.name)
                    except Exception:
                        pass
                documents.append(DocumentInfo(
                    document_id=doc_id,
                    filename=original_name,
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


class SummarizeRequest(BaseModel):
    document_id: Optional[str] = None
    summarize_all: bool = False


class SummaryItem(BaseModel):
    document_id: str
    filename: str
    summary: str
    word_count: Optional[int] = None
    pages: Optional[int] = None


class SummarizeResponse(BaseModel):
    summaries: List[SummaryItem]
    total_documents: int
    downloadable: bool = True


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_documents(
    request: SummarizeRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Summarize uploaded documents using LLM.
    
    - If document_id is provided, summarize that specific document.
    - If summarize_all is True, summarize all documents.
    - Otherwise, summarize the most recently uploaded document.
    """
    try:
        user_dir = DOCUMENTS_DIR / current_user.user_id
        
        if not user_dir.exists():
            raise HTTPException(status_code=404, detail="No documents found. Please upload documents first.")
        
        all_files = [f for f in user_dir.iterdir() if f.is_file()]
        if not all_files:
            raise HTTPException(status_code=404, detail="No documents found.")
        
        # Determine target files
        target_files = []
        if request.document_id:
            for f in all_files:
                if f.stem == request.document_id:
                    target_files.append(f)
                    break
            if not target_files:
                raise HTTPException(status_code=404, detail="Document not found")
        elif request.summarize_all:
            target_files = all_files
        else:
            target_files = sorted(all_files, key=lambda f: f.stat().st_mtime, reverse=True)[:1]
        
        loader = DocumentLoader()
        summaries = []
        
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        for file_path in target_files[:10]:
            try:
                doc_data = await loader.load(str(file_path))
                text = doc_data['text']
                metadata = doc_data['metadata']
                
                # Truncate for LLM context
                max_chars = 8000
                truncated = text[:max_chars] + ("..." if len(text) > max_chars else "")
                
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a document summarizer. Provide a clear, comprehensive summary with key points, important details, and main conclusions. Use bullet points for key findings."},
                        {"role": "user", "content": f"Please summarize this document titled '{metadata.get('filename', 'Unknown')}':\n\n{truncated}"}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                summary_text = response.choices[0].message.content
                
                summaries.append(SummaryItem(
                    document_id=file_path.stem,
                    filename=metadata.get('filename', file_path.name),
                    summary=summary_text,
                    word_count=len(text.split()),
                    pages=metadata.get('pages', None)
                ))
            except Exception as e:
                logger.error(f"Error summarizing {file_path.name}: {e}")
                summaries.append(SummaryItem(
                    document_id=file_path.stem,
                    filename=file_path.name,
                    summary=f"Error summarizing: {str(e)}"
                ))
        
        return SummarizeResponse(
            summaries=summaries,
            total_documents=len(summaries),
            downloadable=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summarize error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download-summary/{document_id}")
async def download_summary(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate and download a summary of a document as a text file.
    """
    try:
        user_dir = DOCUMENTS_DIR / current_user.user_id
        
        if not user_dir.exists():
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Find the document
        target_file = None
        for f in user_dir.iterdir():
            if f.stem == document_id and f.is_file():
                target_file = f
                break
        
        if not target_file:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Load and summarize
        loader = DocumentLoader()
        doc_data = await loader.load(str(target_file))
        text = doc_data['text']
        metadata = doc_data['metadata']
        
        max_chars = 8000
        truncated = text[:max_chars] + ("..." if len(text) > max_chars else "")
        
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional document summarizer. Create a well-structured summary report with:\n1. Document Title\n2. Executive Summary (2-3 sentences)\n3. Key Points (bullet list)\n4. Detailed Summary\n5. Conclusions/Recommendations\n\nFormat it cleanly for download."},
                {"role": "user", "content": f"Create a detailed summary report for this document titled '{metadata.get('filename', 'Unknown')}':\n\n{truncated}"}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        summary_text = response.choices[0].message.content
        
        # Build the downloadable report
        report = f"""{'='*60}
DOCUMENT SUMMARY REPORT
Generated by Salim AI Assistant
{'='*60}

Source Document: {metadata.get('filename', 'Unknown')}
Format: {metadata.get('format', 'unknown').upper()}
Word Count: {len(text.split())}
Pages: {metadata.get('pages', 'N/A')}
Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}

{summary_text}

{'='*60}
End of Summary Report
{'='*60}
"""
        
        # Return as downloadable file
        buffer = io.BytesIO(report.encode('utf-8'))
        filename = f"summary_{metadata.get('filename', document_id).rsplit('.', 1)[0]}.txt"
        
        return StreamingResponse(
            buffer,
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download-all-summaries")
async def download_all_summaries(
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate and download summaries of all uploaded documents as a single file.
    """
    try:
        user_dir = DOCUMENTS_DIR / current_user.user_id
        
        if not user_dir.exists():
            raise HTTPException(status_code=404, detail="No documents found")
        
        all_files = [f for f in user_dir.iterdir() if f.is_file()]
        if not all_files:
            raise HTTPException(status_code=404, detail="No documents found")
        
        loader = DocumentLoader()
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        report_parts = [
            f"{'='*60}",
            "COMPLETE DOCUMENT SUMMARY REPORT",
            "Generated by Salim AI Assistant",
            f"Total Documents: {len(all_files)}",
            f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"{'='*60}\n"
        ]
        
        for i, file_path in enumerate(all_files[:10], 1):
            try:
                doc_data = await loader.load(str(file_path))
                text = doc_data['text']
                metadata = doc_data['metadata']
                
                max_chars = 6000
                truncated = text[:max_chars] + ("..." if len(text) > max_chars else "")
                
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Provide a concise but thorough summary with key points as bullet items."},
                        {"role": "user", "content": f"Summarize this document titled '{metadata.get('filename', 'Unknown')}':\n\n{truncated}"}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )
                summary = response.choices[0].message.content
                
                report_parts.extend([
                    f"\n{'─'*60}",
                    f"Document {i}: {metadata.get('filename', file_path.name)}",
                    f"Format: {metadata.get('format', 'unknown').upper()} | Words: {len(text.split())} | Pages: {metadata.get('pages', 'N/A')}",
                    f"{'─'*60}\n",
                    summary,
                    ""
                ])
            except Exception as e:
                report_parts.extend([
                    f"\nDocument {i}: {file_path.name}",
                    f"Error: {str(e)}\n"
                ])
        
        report_parts.extend([
            f"\n{'='*60}",
            "End of Summary Report",
            f"{'='*60}"
        ])
        
        report = "\n".join(report_parts)
        buffer = io.BytesIO(report.encode('utf-8'))
        
        return StreamingResponse(
            buffer,
            media_type="text/plain",
            headers={
                "Content-Disposition": 'attachment; filename="all_documents_summary.txt"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download all summaries error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

