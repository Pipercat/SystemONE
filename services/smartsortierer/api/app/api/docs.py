"""
SmartSortierer Pro - Document Management Endpoints
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_actor_info
from app.core.audit import AuditLogger
from app.services.storage import StorageService, StorageError
from app.services.queue import JobQueue
from app.services.rules_engine import RulesEngine
from app.services.llm_classifier import LLMClassifier
from app.models.document import Document, DocStatus
from datetime import datetime

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/docs", tags=["documents"])


def get_storage() -> StorageService:
    """Dependency to get storage service instance"""
    return StorageService()


class IngestRequest(BaseModel):
    """Request body for document ingest"""
    inbox_path: str
    skip_duplicate_check: bool = False


class IngestResponse(BaseModel):
    """Response for document ingest"""
    document_id: Optional[int] = None
    status: str
    message: str
    is_duplicate: bool = False
    duplicate_of: Optional[int] = None
    sha256: str


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    request_body: IngestRequest,
    storage: StorageService = Depends(get_storage),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Ingest a document from inbox.
    
    **Process:**
    1. Compute SHA256 hash
    2. Check for duplicates (unless skip_duplicate_check=True)
    3. Create immutable copy in 01_ingested
    4. Create database record with status=INGESTED
    5. Enqueue processing jobs (Phase 5)
    
    **Security:** Path must be in 00_inbox
    
    **Returns:** Document metadata with ingest status
    """
    try:
        inbox_path = request_body.inbox_path
        
        # Security: Ensure path is in inbox
        if not inbox_path.startswith("00_inbox/"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Documents can only be ingested from 00_inbox",
            )
        
        # 1. Compute SHA256
        sha256 = storage.compute_sha256(inbox_path)
        
        # 2. Check for duplicates
        existing_doc = db.query(Document).filter(
            Document.file_sha256 == sha256
        ).first()
        
        if existing_doc and not request_body.skip_duplicate_check:
            # Return info about existing document (don't create duplicate record)
            # The unique constraint prevents duplicate SHA256 anyway
                
            return IngestResponse(
                document_id=existing_doc.id,
                status="DUPLICATE",
                message=f"Document already exists with ID #{existing_doc.id}",
                is_duplicate=True,
                duplicate_of=existing_doc.id,
                sha256=sha256,
            )
        
        # 3. Get file metadata
        file_stat = storage.stat(inbox_path)
        original_filename = file_stat["name"]
        
        # 4. Create immutable copy in 01_ingested
        # Filename format: <sha256>_<original_filename>
        ingested_filename = f"{sha256}_{original_filename}"
        ingested_path = f"01_ingested/{ingested_filename}"
        
        storage.copy_file(inbox_path, ingested_path, overwrite=False)
        
        # 5. Create database record
        document = Document(
            file_sha256=sha256,
            original_filename=original_filename,
            mime_type=file_stat.get("mime_type"),
            file_size_bytes=file_stat["size"],
            inbox_relpath=inbox_path,
            ingested_relpath=ingested_path,
            status=DocStatus.INGESTED,
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # 6. Audit log
        actor_info = get_actor_info(request)
        AuditLogger.log_document_event(
            db=db,
            event_type="DOC_INGESTED",
            document_id=document.id,
            actor_info=actor_info,
            event_data={
                "sha256": sha256,
                "filename": original_filename,
                "size": file_stat["size"],
                "inbox_path": inbox_path,
                "ingested_path": ingested_path,
            }
        )
        
        # 7. Enqueue background jobs
        queue = JobQueue()
        
        # Job 1: Extract text from document
        extract_job_id = queue.enqueue(
            job_type="extract_text",
            payload={
                "document_id": document.id,
                "file_path": ingested_path,
                "mime_type": file_stat.get("mime_type"),
            },
            priority=50,  # High priority
            document_id=document.id,
        )
        
        # Job 2: Chunk text (depends on extract_text)
        chunk_job_id = queue.enqueue(
            job_type="chunk_text",
            payload={
                "document_id": document.id,
                "depends_on": extract_job_id,
            },
            priority=100,  # Normal priority
            document_id=document.id,
        )
        
        # Job 3: Generate embeddings (depends on chunk_text)
        embed_job_id = queue.enqueue(
            job_type="embed_chunks",
            payload={
                "document_id": document.id,
                "depends_on": chunk_job_id,
            },
            priority=150,  # Lower priority
            document_id=document.id,
        )
        
        # Job 4: Classify document (depends on embeddings)
        classify_job_id = queue.enqueue(
            job_type="classify_document",
            payload={
                "document_id": document.id,
                "depends_on": embed_job_id,
            },
            priority=200,  # After embeddings
            document_id=document.id,
        )
        
        return IngestResponse(
            document_id=document.id,
            status="INGESTED",
            message=f"Document ingested successfully. ID: {document.id}",
            is_duplicate=False,
            sha256=sha256,
        )
    
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingest failed: {str(e)}",
        )


@router.get("/list")
async def list_documents(
    status_filter: Optional[str] = Query(None, description="Filter by status (e.g., INGESTED, ANALYZED)"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List documents with optional status filter.
    
    **Returns:** Paginated list of documents
    """
    query = db.query(Document)
    
    # Apply status filter
    if status_filter:
        try:
            status_enum = DocStatus[status_filter.upper()]
            query = query.filter(Document.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}. Valid: {[s.value for s in DocStatus]}",
            )
    
    # Order by newest first
    query = query.order_by(desc(Document.created_at))
    
    # Count total
    total = query.count()
    
    # Paginate
    documents = query.offset(offset).limit(limit).all()
    
    return {
        "documents": [doc.to_dict() for doc in documents],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{document_id}")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """
    Get document details by ID.
    
    **Returns:** Full document metadata
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )
    
    # Include additional details
    doc_dict = document.to_dict()
    doc_dict["chunks_count"] = len(document.chunks)
    doc_dict["tags"] = [{"id": dt.tag_id, "name": dt.tag.name} for dt in document.tags]
    
    return doc_dict


class ApproveRequest(BaseModel):
    """Request body for approving a document"""
    final_category: Optional[str] = None
    final_filename: Optional[str] = None
    final_target_path: Optional[str] = None


class UpdateDocumentRequest(BaseModel):
    """Request body for updating document metadata"""
    user_approved_category: Optional[str] = None
    user_approved_filename: Optional[str] = None
    user_approved_target_path: Optional[str] = None


class ClassifyDocumentRequest(BaseModel):
    """Request body for document classification"""
    force_llm: bool = False  # If True, skip rules and go directly to LLM


class ClassificationResult(BaseModel):
    """Response for classification"""
    document_id: int
    category: str
    filename: str
    target_path: str
    confidence: Optional[float] = None
    method: str  # "rules", "llm", or "fallback"
    message: str


@router.post("/{document_id}/classify", response_model=ClassificationResult)
async def classify_document(
    document_id: int,
    request_body: ClassifyDocumentRequest = None,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Classify a document using Rules Engine and/or LLM.
    
    1. If force_llm=False: Try rules first, then LLM as fallback
    2. If force_llm=True: Skip rules, classify directly with LLM
    
    Classification result is stored in document.category, .suggested_filename, 
    .suggested_target_path, and .classification_confidence
    
    **Workflow**: ANALYZED → document classification → user review → APPROVED
    
    **Returns**: Classification results with suggested metadata
    """
    if request_body is None:
        request_body = ClassifyDocumentRequest()
    
    # Load document
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )
    
    # Document must have extracted text to classify
    if not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot classify document without extracted text. Document must be in ANALYZED status.",
        )
    
    try:
        classification_method = "fallback"
        rule_match = None
        llm_result = None
        
        # Step 1: Try Rules Engine (unless force_llm=True)
        if not request_body.force_llm:
            rules_engine = RulesEngine(db)
            rule_match = rules_engine.classify_document(document)
            
            if rule_match:
                classification_method = "rules"
                document.category = rule_match["category"]
                document.suggested_filename = rule_match.get("suggested_filename")
                document.suggested_target_path = rule_match.get("suggested_target_path")
                document.classification_confidence = 1.0  # Rules are deterministic
                
                logger.info(f"Document {document_id} classified by rules: {document.category}")
        
        # Step 2: If no rule matched, try LLM
        if not rule_match:
            llm_classifier = LLMClassifier()
            llm_result = llm_classifier.classify(document)
            
            if llm_result and llm_result.get("category"):
                classification_method = "llm"
                document.category = llm_result["category"]
                document.suggested_filename = llm_result.get("suggested_filename") or document.original_filename
                document.suggested_target_path = llm_result.get("suggested_target_path") or "03_sorted/Uncategorized"
                document.classification_confidence = llm_result.get("confidence", 0.5)
                document.llm_trace = llm_result  # Store full LLM response
                
                logger.info(f"Document {document_id} classified by LLM: {document.category} (confidence: {document.classification_confidence})")
        
        # Step 3: Fallback to sensible defaults if neither worked
        if not rule_match and not llm_result:
            classification_method = "fallback"
            document.category = "Uncategorized"
            document.suggested_filename = document.original_filename
            document.suggested_target_path = "03_sorted/Uncategorized"
            document.classification_confidence = 0.0
            
            logger.warning(f"Document {document_id} could not be classified. Using fallback defaults.")
        
        # Mark document as needing review (classification complete)
        document.status = DocStatus.NEEDS_REVIEW
        db.commit()
        db.refresh(document)
        
        # Audit log
        actor_info = get_actor_info(request)
        AuditLogger.log_document_event(
            db=db,
            event_type="DOC_CLASSIFIED",
            document_id=document.id,
            actor_info=actor_info,
            event_data={
                "category": document.category,
                "confidence": document.classification_confidence,
                "method": classification_method,
                "suggested_filename": document.suggested_filename,
                "suggested_target_path": document.suggested_target_path,
            }
        )
        
        return ClassificationResult(
            document_id=document.id,
            category=document.category,
            filename=document.suggested_filename or document.original_filename,
            target_path=document.suggested_target_path or "03_sorted/Uncategorized",
            confidence=document.classification_confidence,
            method=classification_method,
            message=f"Document classified successfully using {classification_method}",
        )
    
    except Exception as e:
        logger.error(f"Classification failed for document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}",
        )


@router.post("/{document_id}/approve")
async def approve_document(
    document_id: int,
    request_body: ApproveRequest,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Approve a document for commit.
    
    Sets final metadata fields and status to APPROVED.
    Document is then ready for safe commit to 03_sorted.
    
    **Security**: Requires API key
    
    **Returns**: Updated document metadata
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )
    
    # Check if document is in reviewable state
    if document.status not in [DocStatus.ANALYZED, DocStatus.NEEDS_REVIEW]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document cannot be approved. Current status: {document.status}",
        )
    
    # Set final fields (use user overrides if available, else suggested values)
    document.user_approved_category = request_body.final_category or document.user_approved_category or document.category
    document.user_approved_filename = request_body.final_filename or document.user_approved_filename or document.suggested_filename or document.original_filename
    document.user_approved_target_path = request_body.final_target_path or document.user_approved_target_path or document.suggested_target_path or "03_sorted/Uncategorized"
    
    # Update status
    document.status = DocStatus.APPROVED
    document.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(document)
    
    # Audit log
    actor_info = get_actor_info(request)
    AuditLogger.log_document_event(
        db=db,
        event_type="DOC_APPROVED",
        document_id=document.id,
        actor_info=actor_info,
        event_data={
            "category": document.user_approved_category,
            "filename": document.user_approved_filename,
            "target_path": document.user_approved_target_path,
        }
    )
    
    return {
        "message": "Document approved successfully",
        "document": document.to_dict(),
    }


@router.post("/{document_id}/reject")
async def reject_document(
    document_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    storage: StorageService = Depends(get_storage),
):
    """
    Reject a document.
    
    Moves document to 99_errors and sets status to ERROR.
    
    **Security**: Requires API key
    
    **Returns**: Updated document metadata
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )
    
    # Move file to errors folder
    if document.ingested_relpath:
        try:
            error_filename = document.ingested_relpath.split("/")[-1]
            error_path = f"99_errors/{error_filename}"
            
            storage.copy_file(document.ingested_relpath, error_path, overwrite=True)
            document.staged_relpath = error_path
        except StorageError as e:
            logger.warning(f"Could not move file to errors: {e}")
    
    # Update status
    document.status = DocStatus.ERROR
    
    db.commit()
    db.refresh(document)
    
    # Audit log
    actor_info = get_actor_info(request)
    AuditLogger.log_document_event(
        db=db,
        event_type="DOC_REJECTED",
        document_id=document.id,
        actor_info=actor_info,
        event_data={"reason": "User rejected"}
    )
    
    return {
        "message": "Document rejected and moved to errors",
        "document": document.to_dict(),
    }


@router.patch("/{document_id}")
async def update_document(
    document_id: int,
    request_body: UpdateDocumentRequest,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Update document user-approved fields.
    
    Allows user to override LLM/rules classification before approval.
    
    **Security**: Requires API key
    
    **Returns**: Updated document metadata
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )
    
    # Update user override fields
    if request_body.user_approved_category is not None:
        document.user_approved_category = request_body.user_approved_category
    
    if request_body.user_approved_filename is not None:
        document.user_approved_filename = request_body.user_approved_filename
    
    if request_body.user_approved_target_path is not None:
        document.user_approved_target_path = request_body.user_approved_target_path
    
    document.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(document)
    
    return {
        "message": "Document updated successfully",
        "document": document.to_dict(),
    }
