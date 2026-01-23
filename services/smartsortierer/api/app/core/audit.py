"""
SmartSortierer Pro - Audit Logging
"""
import logging
from typing import Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam
from sqlalchemy.types import String, Integer, Text

from app.core.config import settings

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Centralized audit logging for all critical operations.
    Logs to database table: audit_events
    """
    
    @staticmethod
    def log(
        db: Session,
        event_type: str,
        actor_type: str = "SYSTEM",
        actor_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        event_data: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[int]:
        """
        Log an audit event to the database.
        
        Args:
            db: Database session
            event_type: Type of event (must match audit_event_type ENUM)
            actor_type: Who performed the action (USER, SYSTEM, WORKER, API)
            actor_id: Identifier of the actor
            resource_type: Type of resource affected (e.g., 'document', 'file')
            resource_id: ID of the resource
            event_data: Additional event-specific data (stored as JSONB)
            ip_address: IP address of the actor
            user_agent: User agent string
            
        Returns:
            Audit event ID if successful, None on error
        """
        try:
            # Convert event_data dict to JSON string for PostgreSQL
            import json
            event_data_json = json.dumps(event_data) if event_data else None
            
            # Insert audit event - use simple parameterized query
            query = text("""
                INSERT INTO audit_events (
                    event_type, actor_type, actor_id, resource_type, resource_id,
                    event_data, ip_address, user_agent, created_at
                )
                VALUES (
                    :event_type, :actor_type, :actor_id, :resource_type, :resource_id,
                    :event_data, :ip_address, :user_agent, NOW()
                )
                RETURNING id
            """)
            
            result = db.execute(
                query,
                {
                    "event_type": event_type,
                    "actor_type": actor_type,
                    "actor_id": actor_id,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "event_data": event_data_json,
                    "ip_address": str(ip_address) if ip_address else None,
                    "user_agent": user_agent,
                }
            )
            db.commit()
            
            audit_id = result.scalar_one()
            
            # Also log to stdout for Docker logs
            if settings.LOG_LEVEL == "DEBUG":
                logger.debug(f"Audit: {event_type} by {actor_type}:{actor_id} on {resource_type}:{resource_id}")
            
            return audit_id
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def log_file_operation(
        db: Session,
        operation: str,
        path: str,
        actor_info: dict,
        success: bool = True,
        error: Optional[str] = None,
        additional_data: Optional[dict] = None,
    ) -> Optional[int]:
        """
        Specialized helper for file operations.
        
        Args:
            db: Database session
            operation: Operation type (UPLOADED, MOVED, RENAMED, DELETED, DOWNLOADED)
            path: File path involved
            actor_info: Actor information from get_actor_info()
            success: Whether operation succeeded
            error: Error message if failed
            additional_data: Extra data (e.g., destination path for move)
            
        Returns:
            Audit event ID
        """
        event_data = {
            "operation": operation,
            "path": path,
            "success": success,
            **(additional_data or {}),
        }
        
        if error:
            event_data["error"] = error
        
        event_type = f"FILE_{operation}"
        
        return AuditLogger.log(
            db=db,
            event_type=event_type,
            actor_type=actor_info.get("actor_type", "API"),
            actor_id=actor_info.get("actor_id"),
            resource_type="file",
            resource_id=None,  # Files don't have DB IDs yet
            event_data=event_data,
            ip_address=actor_info.get("ip_address"),
            user_agent=actor_info.get("user_agent"),
        )
    
    @staticmethod
    def log_document_event(
        db: Session,
        event_type: str,
        document_id: int,
        actor_info: dict,
        event_data: Optional[dict] = None,
    ) -> Optional[int]:
        """
        Specialized helper for document events.
        
        Args:
            db: Database session
            event_type: Event type (DOC_INGESTED, DOC_ANALYZED, etc.)
            document_id: Document ID
            actor_info: Actor information
            event_data: Additional event data
            
        Returns:
            Audit event ID
        """
        return AuditLogger.log(
            db=db,
            event_type=event_type,
            actor_type=actor_info.get("actor_type", "SYSTEM"),
            actor_id=actor_info.get("actor_id"),
            resource_type="document",
            resource_id=document_id,
            event_data=event_data,
            ip_address=actor_info.get("ip_address"),
            user_agent=actor_info.get("user_agent"),
        )
