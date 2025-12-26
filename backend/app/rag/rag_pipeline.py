"""RAG Pipeline - End-to-end document processing and retrieval."""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .document_loader import DocumentLoader
from .chunker import TextChunker
from .embedder import Embedder
from .retriever import Retriever
from app.memory.vector_memory import VectorMemory
from app.llm.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Complete RAG pipeline for document ingestion and retrieval.
    
    Steps:
    1. Load document
    2. Chunk text
    3. Generate embeddings
    4. Store in vector database
    5. Retrieve relevant chunks for queries
    """
    
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        vector_memory: VectorMemory,
        chunk_size: int = 400,
        overlap: int = 80
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            llm_provider: LLM provider for embeddings
            vector_memory: Vector memory for storage
            chunk_size: Chunk size in tokens
            overlap: Overlap between chunks
        """
        self.loader = DocumentLoader()
        self.chunker = TextChunker(chunk_size=chunk_size, overlap=overlap)
        self.embedder = Embedder(llm_provider)
        self.retriever = Retriever(vector_memory)
        self.vector_memory = vector_memory
        
        logger.info("RAG Pipeline initialized")
    
    async def ingest_document(
        self,
        user_id: str,
        file_path: str,
        document_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest a document: load, chunk, embed, and store.
        
        Args:
            user_id: User identifier
            file_path: Path to document
            document_metadata: Optional metadata for the document
            
        Returns:
            Ingestion summary
        """
        logger.info(f"Starting document ingestion: {file_path}")
        
        # 1. Load document
        doc_data = await self.loader.load(file_path)
        text = doc_data['text']
        file_metadata = doc_data['metadata']
        
        # Merge metadata
        combined_metadata = {
            **file_metadata,
            **(document_metadata or {}),
            'user_id': user_id
        }
        
        # 2. Chunk text
        chunks = self.chunker.chunk(text, metadata=combined_metadata)
        
        # 3. Generate embeddings
        chunks_with_embeddings = await self.embedder.embed_chunks(chunks)
        
        # 4. Store in vector database
        stored_ids = []
        for chunk in chunks_with_embeddings:
            chunk_id = await self.vector_memory.store(
                user_id=user_id,
                text=chunk['text'],
                embedding=chunk['embedding'],
                metadata={
                    **chunk['metadata'],
                    'chunk_index': chunk['index'],
                    'word_count': chunk['word_count']
                }
            )
            stored_ids.append(chunk_id)
        
        logger.info(f"Successfully ingested {len(chunks)} chunks from {file_metadata['filename']}")
        
        return {
            'document': file_metadata['filename'],
            'chunks_created': len(chunks),
            'chunks_stored': len(stored_ids),
            'total_words': sum(c['word_count'] for c in chunks),
            'metadata': combined_metadata
        }
    
    async def query(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Query documents and retrieve relevant chunks.
        
        Args:
            user_id: User identifier
            query: Query string
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            Query results with context
        """
        logger.info(f"Processing RAG query: {query[:50]}...")
        
        # 1. Generate query embedding
        query_embedding = await self.embedder.embed_query(query)
        
        # 2. Retrieve relevant chunks
        chunks = await self.retriever.retrieve(
            user_id=user_id,
            query_embedding=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold
        )
        
        # 3. Build context
        context = self._build_context(chunks)
        
        return {
            'query': query,
            'chunks_found': len(chunks),
            'chunks': chunks,
            'context': context
        }
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved chunks.
        
        Args:
            chunks: Retrieved chunks
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk['metadata'].get('filename', 'Unknown')
            text = chunk['text']
            score = chunk.get('score', 0)
            
            context_parts.append(
                f"[Source {i}: {source} (relevance: {score:.2f})]\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    async def generate_answer(
        self,
        user_id: str,
        query: str,
        llm_provider: BaseLLMProvider,
        top_k: int = 5,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Query documents and generate answer using LLM.
        
        Args:
            user_id: User identifier
            query: User query
            llm_provider: LLM provider for answer generation
            top_k: Number of chunks to retrieve
            include_sources: Whether to include source citations
            
        Returns:
            Answer with sources
        """
        # Retrieve relevant chunks
        rag_results = await self.query(user_id, query, top_k=top_k)
        
        if not rag_results['chunks']:
            return {
                'answer': "I couldn't find relevant information in your documents to answer this question.",
                'sources': []
            }
        
        # Build prompt with context
        context = rag_results['context']
        prompt = f"""Based on the following context from the user's documents, answer the question.
If the context doesn't contain enough information, say so.

Context:
{context}

Question: {query}

Provide a clear, concise answer based on the context above."""
        
        # Generate answer
        response = await llm_provider.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        answer = response.content
        
        # Extract sources
        sources = []
        if include_sources:
            seen_sources = set()
            for chunk in rag_results['chunks']:
                filename = chunk['metadata'].get('filename', 'Unknown')
                if filename not in seen_sources:
                    sources.append({
                        'filename': filename,
                        'format': chunk['metadata'].get('format', 'unknown'),
                        'relevance': chunk.get('score', 0)
                    })
                    seen_sources.add(filename)
        
        return {
            'answer': answer,
            'sources': sources,
            'chunks_used': len(rag_results['chunks'])
        }
