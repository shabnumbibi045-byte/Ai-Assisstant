"""Text Chunker - Split documents into manageable chunks."""

import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class TextChunker:
    """
    Split text into chunks for embedding and retrieval.
    
    Uses sliding window with overlap to maintain context.
    """
    
    def __init__(
        self,
        chunk_size: int = 400,
        overlap: int = 80,
        min_chunk_size: int = 50
    ):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target chunk size in tokens (approx words)
            overlap: Overlap between chunks in tokens
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries
        """
        # Clean text
        text = self._clean_text(text)
        
        # Split into sentences for better boundaries
        sentences = self._split_sentences(text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence.split())
            
            # If adding this sentence exceeds chunk size
            if current_size + sentence_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(self._create_chunk(chunk_text, len(chunks), metadata))
                
                # Start new chunk with overlap
                overlap_size = 0
                overlap_chunk = []
                
                for sent in reversed(current_chunk):
                    sent_size = len(sent.split())
                    if overlap_size + sent_size <= self.overlap:
                        overlap_chunk.insert(0, sent)
                        overlap_size += sent_size
                    else:
                        break
                
                current_chunk = overlap_chunk
                current_size = overlap_size
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text.split()) >= self.min_chunk_size:
                chunks.append(self._create_chunk(chunk_text, len(chunks), metadata))
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-"]', '', text)
        return text.strip()
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _create_chunk(
        self,
        text: str,
        index: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create chunk dictionary."""
        chunk = {
            'text': text,
            'index': index,
            'char_count': len(text),
            'word_count': len(text.split()),
            'metadata': metadata or {}
        }
        return chunk
