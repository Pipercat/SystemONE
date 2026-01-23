"""
SmartSortierer Pro - Document ORM Models
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, BigInteger, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


# Enums matching database schema
class DocStatus(str, enum.Enum):
    INGESTED = "INGESTED"
    ANALYZING = "ANALYZING"
    ANALYZED = "ANALYZED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    APPROVED = "APPROVED"
    COMMITTED = "COMMITTED"
    ERROR = "ERROR"
    DUPLICATE = "DUPLICATE"


class Document(Base):
    """Document entity - main table for file management"""
    
    __tablename__ = "documents"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    
    # File identification
    file_sha256 = Column(String(64), unique=True, nullable=False, index=True)
    original_filename = Column(String(512), nullable=False)
    mime_type = Column(String(128))
    file_size_bytes = Column(BigInteger)
    
    # Storage paths (relative to SS_STORAGE_ROOT)
    inbox_relpath = Column(String(1024))
    ingested_relpath = Column(String(1024))
    staged_relpath = Column(String(1024))
    final_relpath = Column(String(1024))
    
    # Status & workflow
    status = Column(SQLEnum(DocStatus), nullable=False, default=DocStatus.INGESTED, index=True)
    duplicate_of_doc = Column(BigInteger, ForeignKey("documents.id"), nullable=True)
    
    # Extracted metadata
    extracted_text = Column(Text)
    page_count = Column(Integer)
    ocr_needed = Column(Boolean, default=False)
    
    # Classification (from LLM or rules)
    category = Column(String(256), index=True)
    suggested_filename = Column(String(512))
    suggested_target_path = Column(String(1024))
    classification_confidence = Column(Float)
    llm_trace = Column(JSONB)
    
    # User override
    user_approved_category = Column(String(256))
    user_approved_filename = Column(String(512))
    user_approved_target_path = Column(String(1024))
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyzed_at = Column(DateTime)
    approved_at = Column(DateTime)
    committed_at = Column(DateTime)
    
    # Relationships
    duplicate_of = relationship("Document", remote_side=[id], foreign_keys=[duplicate_of_doc])
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    revisions = relationship("DocumentRevision", back_populates="document", cascade="all, delete-orphan")
    tags = relationship("DocumentTag", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.original_filename}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "file_sha256": self.file_sha256,
            "original_filename": self.original_filename,
            "mime_type": self.mime_type,
            "file_size_bytes": self.file_size_bytes,
            "status": self.status.value if self.status else None,
            "category": self.category,
            "suggested_filename": self.suggested_filename,
            "classification_confidence": self.classification_confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "committed_at": self.committed_at.isoformat() if self.committed_at else None,
            "duplicate_of_doc": self.duplicate_of_doc,
        }


class DocumentRevision(Base):
    """Document revision history"""
    
    __tablename__ = "document_revisions"
    
    id = Column(BigInteger, primary_key=True, index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id"), nullable=False, index=True)
    
    action = Column(String(64), nullable=False)
    old_path = Column(String(1024))
    new_path = Column(String(1024))
    metadata_snapshot = Column(JSONB)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_by = Column(String(256))
    
    # Relationships
    document = relationship("Document", back_populates="revisions")
    
    def __repr__(self):
        return f"<DocumentRevision(id={self.id}, doc_id={self.document_id}, action='{self.action}')>"


class DocumentChunk(Base):
    """Document text chunks for RAG"""
    
    __tablename__ = "document_chunks"
    
    id = Column(BigInteger, primary_key=True, index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id"), nullable=False, index=True)
    
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_tokens = Column(Integer)
    
    # Reference to Qdrant vector point
    qdrant_point_id = Column(String(36), index=True)  # UUID as string
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index})>"


class Tag(Base):
    """Tags for document categorization"""
    
    __tablename__ = "tags"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=False)
    color = Column(String(32))
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("DocumentTag", back_populates="tag")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class DocumentTag(Base):
    """Many-to-many relationship between documents and tags"""
    
    __tablename__ = "document_tags"
    
    document_id = Column(BigInteger, ForeignKey("documents.id"), primary_key=True)
    tag_id = Column(BigInteger, ForeignKey("tags.id"), primary_key=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="tags")
    tag = relationship("Tag", back_populates="documents")
    
    def __repr__(self):
        return f"<DocumentTag(doc_id={self.document_id}, tag_id={self.tag_id})>"
