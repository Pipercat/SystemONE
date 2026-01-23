"""
SmartSortierer Pro - Text Chunking Handler
Splits document text into chunks for RAG
"""
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add API path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))

from app.core.database import SessionLocal
from app.models.document import Document, DocumentChunk, DocStatus


class ChunkTextHandler:
    """Split document text into semantic chunks"""
    
    def __init__(self):
        self.chunk_size = 800  # Target characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Simple strategy: Split by paragraphs, then combine into chunks.
        """
        if not text or not text.strip():
            return []
        
        # Split by double newline (paragraphs)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if current_length + para_length > self.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                
                # Start new chunk with overlap (keep last paragraph)
                if len(current_chunk) > 1:
                    current_chunk = [current_chunk[-1], para]
                    current_length = len(current_chunk[-1]) + para_length
                else:
                    current_chunk = [para]
                    current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        # Add remaining chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks
    
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute text chunking job.
        
        Payload:
            - document_id: int
            - depends_on: str (optional job_id dependency)
        
        Returns:
            - chunks_count: int
            - total_chars: int
        """
        document_id = payload["document_id"]
        
        print(f"  Chunking text for document {document_id}")
        
        db = SessionLocal()
        try:
            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            
            if not document:
                raise Exception(f"Document {document_id} not found")
            
            if not document.extracted_text:
                raise Exception(f"Document {document_id} has no extracted text")
            
            # Split into chunks
            text_chunks = self.split_into_chunks(document.extracted_text)
            
            # Delete existing chunks (if any)
            db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
            
            # Create chunk records
            for idx, chunk_text in enumerate(text_chunks):
                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=idx,
                    chunk_text=chunk_text,
                    chunk_tokens=len(chunk_text.split()),  # Rough token count
                )
                db.add(chunk)
            
            # Update document status
            document.status = DocStatus.ANALYZING
            db.commit()
            
            print(f"  ✓ Created {len(text_chunks)} chunks")
            
            return {
                "chunks_count": len(text_chunks),
                "total_chars": sum(len(c) for c in text_chunks),
            }
        
        finally:
            db.close()
