"""
SmartSortierer Pro - File Management Endpoints
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_actor_info
from app.core.audit import AuditLogger
from app.services.storage import StorageService, StorageError, PathTraversalError
from app.core.config import settings


router = APIRouter(prefix="/api/files", tags=["files"])


def get_storage() -> StorageService:
    """Dependency to get storage service instance"""
    return StorageService()


@router.get("/list")
async def list_files(
    path: str = Query("", description="Relative path to list (empty = root)"),
    storage: StorageService = Depends(get_storage),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    List files and directories at the given path.
    
    **Security**: Path must be within storage root. No traversal allowed.
    
    **Returns**: Array of file/directory objects with metadata.
    """
    try:
        items = storage.list_directory(path)
        
        # Audit log
        actor_info = get_actor_info(request)
        AuditLogger.log_file_operation(
            db=db,
            operation="LISTED",
            path=path or "/",
            actor_info=actor_info,
            success=True,
        )
        
        return {
            "path": path or "/",
            "items": items,
            "count": len(items),
        }
    
    except PathTraversalError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/stat")
async def get_file_stat(
    path: str = Query(..., description="Relative path to file/directory"),
    storage: StorageService = Depends(get_storage),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Get metadata for a specific file or directory.
    
    **Security**: Path must be within storage root.
    
    **Returns**: File/directory metadata object.
    """
    try:
        metadata = storage.stat(path)
        
        # Audit log
        actor_info = get_actor_info(request)
        AuditLogger.log_file_operation(
            db=db,
            operation="STAT",
            path=path,
            actor_info=actor_info,
            success=True,
        )
        
        return metadata
    
    except PathTraversalError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/download")
async def download_file(
    path: str = Query(..., description="Relative path to file"),
    storage: StorageService = Depends(get_storage),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Download a file as a stream.
    
    **Security**: Path must be within storage root. Only files, not directories.
    
    **Returns**: File content as streaming response.
    """
    try:
        # Get file metadata first
        metadata = storage.stat(path)
        
        if metadata["type"] != "file":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot download a directory",
            )
        
        # Open file for streaming
        file_handle = storage.read_file(path)
        
        # Audit log
        actor_info = get_actor_info(request)
        AuditLogger.log_file_operation(
            db=db,
            operation="DOWNLOADED",
            path=path,
            actor_info=actor_info,
            success=True,
            additional_data={"size": metadata["size"]},
        )
        
        # Stream response
        return StreamingResponse(
            file_handle,
            media_type=metadata.get("mime_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f'attachment; filename="{metadata["name"]}"',
                "Content-Length": str(metadata["size"]),
            },
        )
    
    except PathTraversalError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# Pydantic models for request bodies
class MoveFileRequest(BaseModel):
    source: str
    destination: str
    overwrite: bool = False


class RenameFileRequest(BaseModel):
    path: str
    new_name: str


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: str = Query("00_inbox", description="Target directory (default: 00_inbox)"),
    storage: StorageService = Depends(get_storage),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Upload a file to storage.
    
    **Default target**: 00_inbox (inbox folder)
    
    **Security**: 
    - Path must be within storage root
    - File size limited by MAX_UPLOAD_SIZE_MB
    - Only uploads to writable areas (00_inbox recommended)
    
    **Returns**: File metadata after upload.
    """
    try:
        # Build target path
        target_relpath = f"{path}/{file.filename}" if path else file.filename
        
        # Write file
        metadata = storage.write_file(target_relpath, file.file, overwrite=False)
        
        # Audit log
        actor_info = get_actor_info(request)
        AuditLogger.log_file_operation(
            db=db,
            operation="UPLOADED",
            path=target_relpath,
            actor_info=actor_info,
            success=True,
            additional_data={
                "filename": file.filename,
                "size": metadata["size"],
                "mime_type": metadata.get("mime_type"),
            },
        )
        
        return {
            "message": "File uploaded successfully",
            "file": metadata,
        }
    
    except PathTraversalError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/move")
async def move_file(
    request_data: MoveFileRequest,
    storage: StorageService = Depends(get_storage),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Move or rename a file/directory.
    
    **Security**: Both source and destination must be within storage root.
    
    **Returns**: New file metadata.
    """
    try:
        metadata = storage.move_file(
            request_data.source,
            request_data.destination,
            overwrite=request_data.overwrite,
        )
        
        # Audit log
        actor_info = get_actor_info(request)
        AuditLogger.log_file_operation(
            db=db,
            operation="MOVED",
            path=request_data.source,
            actor_info=actor_info,
            success=True,
            additional_data={
                "destination": request_data.destination,
                "overwrite": request_data.overwrite,
            },
        )
        
        return {
            "message": "File moved successfully",
            "file": metadata,
        }
    
    except PathTraversalError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/rename")
async def rename_file(
    request_data: RenameFileRequest,
    storage: StorageService = Depends(get_storage),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Rename a file (convenience wrapper for move operation).
    
    **Security**: Path must be within storage root.
    
    **Returns**: New file metadata.
    """
    try:
        # Get current file metadata to determine parent directory
        current_metadata = storage.stat(request_data.path)
        
        # Build new path (same directory, new name)
        from pathlib import Path
        current_path = Path(request_data.path)
        new_path = str(current_path.parent / request_data.new_name)
        
        # Move file
        metadata = storage.move_file(request_data.path, new_path, overwrite=False)
        
        # Audit log
        actor_info = get_actor_info(request)
        AuditLogger.log_file_operation(
            db=db,
            operation="RENAMED",
            path=request_data.path,
            actor_info=actor_info,
            success=True,
            additional_data={
                "new_name": request_data.new_name,
                "new_path": new_path,
            },
        )
        
        return {
            "message": "File renamed successfully",
            "file": metadata,
        }
    
    except PathTraversalError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
