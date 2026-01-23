"""
SmartSortierer Pro - Text Extraction Handler
Extracts text from documents (PDF, TXT, etc.)
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Add API path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))

from app.services.storage import StorageService
from app.core.database import SessionLocal
from app.models.document import Document, DocStatus


class ExtractTextHandler:
    """Extract text from document files"""
    
    def __init__(self):
        self.storage = StorageService()
    
    def extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF using pypdf"""
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(file_path)
            text_parts = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            full_text = "\n\n".join(text_parts)
            page_count = len(reader.pages)
            
            return full_text, page_count
        
        except Exception as e:
            raise Exception(f"PDF extraction failed: {e}")
    
    def extract_from_text(self, file_path: Path) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), 1  # 1 "page"
        except UnicodeDecodeError:
            # Try latin-1 as fallback
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read(), 1
    
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute text extraction job.
        
        Payload:
            - document_id: int
            - file_path: str (relative to storage root)
            - mime_type: str
        
        Returns:
            - extracted_text: str
            - page_count: int
            - char_count: int
        """
        document_id = payload["document_id"]
        file_relpath = payload["file_path"]
        mime_type = payload.get("mime_type", "")
        
        print(f"  Extracting text from: {file_relpath}")
        
        # Get absolute file path
        file_path = self.storage.safe_join(file_relpath)
        
        # Extract based on mime type
        if "pdf" in mime_type.lower() or file_path.suffix.lower() == ".pdf":
            extracted_text, page_count = self.extract_from_pdf(file_path)
        elif "text" in mime_type.lower() or file_path.suffix in [".txt", ".md", ".log"]:
            extracted_text, page_count = self.extract_from_text(file_path)
        else:
            # Unsupported format, try text extraction as fallback
            try:
                extracted_text, page_count = self.extract_from_text(file_path)
            except:
                raise Exception(f"Unsupported file format: {mime_type or file_path.suffix}")
        
        # Update document in database
        db = SessionLocal()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            
            if document:
                document.extracted_text = extracted_text
                document.page_count = page_count
                document.status = DocStatus.ANALYZING
                db.commit()
                
                print(f"  ✓ Extracted {len(extracted_text)} chars from {page_count} page(s)")
            else:
                raise Exception(f"Document {document_id} not found in database")
        
        finally:
            db.close()
        
        return {
            "extracted_text_length": len(extracted_text),
            "page_count": page_count,
            "char_count": len(extracted_text),
        }
