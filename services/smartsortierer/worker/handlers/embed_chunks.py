"""
SmartSortierer Pro - Embeddings Handler
Generates embeddings and stores in Qdrant
"""
import sys
import uuid
from pathlib import Path
from typing import Dict, Any, List

# Add API path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.document import Document, DocumentChunk, DocStatus


class EmbedChunksHandler:
    """Generate embeddings and upsert to Qdrant"""
    
    def __init__(self):
        self.ollama_available = False
        self.qdrant_available = False
        
        # Try to import optional dependencies
        try:
            import httpx
            self.httpx = httpx
            self.ollama_available = True
        except ImportError:
            print("  ⚠ httpx not available, embeddings will be skipped")
        
        try:
            from qdrant_client import QdrantClient
            self.QdrantClient = QdrantClient
            self.qdrant_available = True
        except ImportError:
            print("  ⚠ qdrant_client not available, vector storage will be skipped")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Ollama"""
        if not self.ollama_available:
            return []
        
        try:
            # Call Ollama embeddings API
            url = f"{settings.ollama_base_url}/api/embeddings"
            
            response = self.httpx.post(
                url,
                json={
                    "model": settings.OLLAMA_MODEL_EMBED,
                    "prompt": text,
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("embedding", [])
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
        
        except Exception as e:
            raise Exception(f"Embedding generation failed: {e}")
    
    def upsert_to_qdrant(self, document_id: int, chunk_id: int, chunk_index: int, text: str, embedding: List[float]):
        """Upsert embedding to Qdrant"""
        if not self.qdrant_available or not embedding:
            return None
        
        try:
            client = self.QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
            )
            
            # Ensure collection exists
            try:
                client.get_collection(settings.QDRANT_COLLECTION)
            except:
                # Create collection if it doesn't exist
                from qdrant_client.models import Distance, VectorParams
                
                client.create_collection(
                    collection_name=settings.QDRANT_COLLECTION,
                    vectors_config=VectorParams(
                        size=len(embedding),
                        distance=Distance.COSINE,
                    ),
                )
            
            # Generate point ID
            point_id = str(uuid.uuid4())
            
            # Upsert point
            from qdrant_client.models import PointStruct
            
            client.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "document_id": document_id,
                            "chunk_id": chunk_id,
                            "chunk_index": chunk_index,
                            "text_preview": text[:200],  # First 200 chars
                        },
                    )
                ],
            )
            
            return point_id
        
        except Exception as e:
            raise Exception(f"Qdrant upsert failed: {e}")
    
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute embeddings job.
        
        Payload:
            - document_id: int
            - depends_on: str (optional job_id dependency)
        
        Returns:
            - embedded_count: int
            - skipped: bool (if no Ollama/Qdrant)
        """
        document_id = payload["document_id"]
        
        print(f"  Embedding chunks for document {document_id}")
        
        if not self.ollama_available or not self.qdrant_available:
            print(f"  ⚠ Skipping embeddings (Ollama or Qdrant not available)")
            
            # Mark document as ANALYZED (even without embeddings)
            db = SessionLocal()
            try:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.status = DocStatus.ANALYZED
                    db.commit()
            finally:
                db.close()
            
            return {
                "embedded_count": 0,
                "skipped": True,
                "reason": "Ollama or Qdrant not available",
            }
        
        db = SessionLocal()
        try:
            # Get all chunks for document
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).order_by(DocumentChunk.chunk_index).all()
            
            if not chunks:
                raise Exception(f"No chunks found for document {document_id}")
            
            embedded_count = 0
            
            for chunk in chunks:
                # Generate embedding
                embedding = self.generate_embedding(chunk.chunk_text)
                
                if embedding:
                    # Upsert to Qdrant
                    point_id = self.upsert_to_qdrant(
                        document_id=document_id,
                        chunk_id=chunk.id,
                        chunk_index=chunk.chunk_index,
                        text=chunk.chunk_text,
                        embedding=embedding,
                    )
                    
                    # Update chunk with Qdrant point ID
                    if point_id:
                        chunk.qdrant_point_id = point_id
                        embedded_count += 1
            
            # Update document status to ANALYZED
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = DocStatus.ANALYZED
            
            db.commit()
            
            print(f"  ✓ Embedded {embedded_count} chunks")
            
            return {
                "embedded_count": embedded_count,
                "skipped": False,
            }
        
        finally:
            db.close()
