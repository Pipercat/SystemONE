"""
SmartSortierer Pro - Storage Service with Path Sandboxing
"""
import os
import hashlib
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO
from datetime import datetime
import mimetypes

from app.core.config import settings


class StorageError(Exception):
    """Base exception for storage operations"""
    pass


class PathTraversalError(StorageError):
    """Raised when path traversal attack is detected"""
    pass


class StorageService:
    """
    Secure file system operations with mandatory path sandboxing.
    All paths must be within SS_STORAGE_ROOT.
    """
    
    def __init__(self, storage_root: Optional[str] = None):
        self.storage_root = Path(storage_root or settings.STORAGE_ROOT).resolve()
        
        if not self.storage_root.exists():
            raise StorageError(f"Storage root does not exist: {self.storage_root}")
        
        if not self.storage_root.is_dir():
            raise StorageError(f"Storage root is not a directory: {self.storage_root}")
    
    def safe_join(self, relpath: str) -> Path:
        """
        Safely join relative path to storage root.
        Prevents path traversal attacks (../).
        
        Args:
            relpath: Relative path within storage root
            
        Returns:
            Resolved absolute Path object
            
        Raises:
            PathTraversalError: If path tries to escape storage root
        """
        # Normalize path (remove .., ., etc.)
        full_path = (self.storage_root / relpath).resolve()
        
        # Verify it's still within storage root
        try:
            full_path.relative_to(self.storage_root)
        except ValueError:
            raise PathTraversalError(
                f"Path traversal attempt detected: {relpath}"
            )
        
        return full_path
    
    def list_directory(self, relpath: str = "") -> List[Dict[str, Any]]:
        """
        List contents of a directory.
        
        Args:
            relpath: Relative path to list (empty = root)
            
        Returns:
            List of file/directory metadata dicts
            
        Raises:
            PathTraversalError: If path invalid
            StorageError: If path doesn't exist or not a directory
        """
        abs_path = self.safe_join(relpath)
        
        if not abs_path.exists():
            raise StorageError(f"Path does not exist: {relpath}")
        
        if not abs_path.is_dir():
            raise StorageError(f"Path is not a directory: {relpath}")
        
        items = []
        try:
            for entry in sorted(abs_path.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
                stat = entry.stat()
                
                item = {
                    "name": entry.name,
                    "path": str(entry.relative_to(self.storage_root)),
                    "type": "directory" if entry.is_dir() else "file",
                    "size": stat.st_size if entry.is_file() else None,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                }
                
                if entry.is_file():
                    item["mime_type"] = mimetypes.guess_type(entry.name)[0]
                
                items.append(item)
        
        except PermissionError:
            raise StorageError(f"Permission denied: {relpath}")
        
        return items
    
    def stat(self, relpath: str) -> Dict[str, Any]:
        """
        Get file/directory metadata.
        
        Args:
            relpath: Relative path
            
        Returns:
            Metadata dictionary
        """
        abs_path = self.safe_join(relpath)
        
        if not abs_path.exists():
            raise StorageError(f"Path does not exist: {relpath}")
        
        stat = abs_path.stat()
        
        metadata = {
            "name": abs_path.name,
            "path": relpath,
            "type": "directory" if abs_path.is_dir() else "file",
            "size": stat.st_size if abs_path.is_file() else None,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "exists": True,
        }
        
        if abs_path.is_file():
            metadata["mime_type"] = mimetypes.guess_type(abs_path.name)[0]
        
        return metadata
    
    def read_file(self, relpath: str) -> BinaryIO:
        """
        Open file for reading (as binary stream).
        Caller is responsible for closing the file.
        
        Args:
            relpath: Relative path to file
            
        Returns:
            File handle (binary mode)
        """
        abs_path = self.safe_join(relpath)
        
        if not abs_path.exists():
            raise StorageError(f"File does not exist: {relpath}")
        
        if not abs_path.is_file():
            raise StorageError(f"Path is not a file: {relpath}")
        
        try:
            return open(abs_path, "rb")
        except PermissionError:
            raise StorageError(f"Permission denied: {relpath}")
    
    def write_file(self, relpath: str, content: BinaryIO, overwrite: bool = False) -> Dict[str, Any]:
        """
        Write file to storage.
        
        Args:
            relpath: Relative path (must be in writable area like 00_inbox)
            content: Binary file content
            overwrite: Allow overwriting existing file
            
        Returns:
            File metadata dict
        """
        abs_path = self.safe_join(relpath)
        
        # Check if file exists
        if abs_path.exists() and not overwrite:
            raise StorageError(f"File already exists: {relpath}")
        
        # Ensure parent directory exists
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(abs_path, "wb") as f:
                shutil.copyfileobj(content, f)
        except PermissionError:
            raise StorageError(f"Permission denied: {relpath}")
        
        return self.stat(relpath)
    
    def move_file(self, src_relpath: str, dest_relpath: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Move/rename file.
        
        Args:
            src_relpath: Source relative path
            dest_relpath: Destination relative path
            overwrite: Allow overwriting destination
            
        Returns:
            New file metadata
        """
        src_abs = self.safe_join(src_relpath)
        dest_abs = self.safe_join(dest_relpath)
        
        if not src_abs.exists():
            raise StorageError(f"Source does not exist: {src_relpath}")
        
        if dest_abs.exists() and not overwrite:
            raise StorageError(f"Destination already exists: {dest_relpath}")
        
        # Ensure destination directory exists
        dest_abs.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.move(str(src_abs), str(dest_abs))
        except PermissionError:
            raise StorageError(f"Permission denied")
        
        return self.stat(dest_relpath)
    
    def copy_file(self, src_relpath: str, dest_relpath: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Copy file (immutable operation for ingestion).
        
        Args:
            src_relpath: Source relative path
            dest_relpath: Destination relative path
            overwrite: Allow overwriting destination
            
        Returns:
            New file metadata
        """
        src_abs = self.safe_join(src_relpath)
        dest_abs = self.safe_join(dest_relpath)
        
        if not src_abs.exists():
            raise StorageError(f"Source does not exist: {src_relpath}")
        
        if not src_abs.is_file():
            raise StorageError(f"Source is not a file: {src_relpath}")
        
        if dest_abs.exists() and not overwrite:
            raise StorageError(f"Destination already exists: {dest_relpath}")
        
        # Ensure destination directory exists
        dest_abs.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(str(src_abs), str(dest_abs))
        except PermissionError:
            raise StorageError(f"Permission denied")
        
        return self.stat(dest_relpath)
    
    def delete_file(self, relpath: str) -> bool:
        """
        Delete file (use with caution).
        
        Args:
            relpath: Relative path
            
        Returns:
            True if deleted
        """
        abs_path = self.safe_join(relpath)
        
        if not abs_path.exists():
            raise StorageError(f"Path does not exist: {relpath}")
        
        try:
            if abs_path.is_file():
                abs_path.unlink()
            elif abs_path.is_dir():
                shutil.rmtree(abs_path)
            return True
        except PermissionError:
            raise StorageError(f"Permission denied: {relpath}")
    
    def compute_sha256(self, relpath: str) -> str:
        """
        Compute SHA256 hash of file.
        
        Args:
            relpath: Relative path to file
            
        Returns:
            Hex string of SHA256 hash
        """
        abs_path = self.safe_join(relpath)
        
        if not abs_path.exists() or not abs_path.is_file():
            raise StorageError(f"File does not exist: {relpath}")
        
        sha256 = hashlib.sha256()
        
        try:
            with open(abs_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
        except PermissionError:
            raise StorageError(f"Permission denied: {relpath}")
        
        return sha256.hexdigest()
    
    def ensure_directory(self, relpath: str) -> Path:
        """
        Ensure directory exists (create if not).
        
        Args:
            relpath: Relative path
            
        Returns:
            Absolute Path object
        """
        abs_path = self.safe_join(relpath)
        abs_path.mkdir(parents=True, exist_ok=True)
        return abs_path
