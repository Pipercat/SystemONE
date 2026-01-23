"""
SmartSortierer Pro - Redis Job Queue Service
"""
import json
import redis
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.config import settings


class JobQueue:
    """
    Redis-based job queue for background processing.
    Workers pull jobs and process them asynchronously.
    """
    
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True,
        )
        self.queue_name = "smartsortierer:jobs"
    
    def enqueue(
        self,
        job_type: str,
        payload: Dict[str, Any],
        priority: int = 100,
        document_id: Optional[int] = None,
    ) -> str:
        """
        Enqueue a job for background processing.
        
        Args:
            job_type: Type of job (e.g., 'extract_text', 'chunk_text', 'embed')
            payload: Job-specific data
            priority: Lower = higher priority (default 100)
            document_id: Optional document ID for tracking
            
        Returns:
            Job ID (UUID)
        """
        import uuid
        
        job_id = str(uuid.uuid4())
        
        job_data = {
            "job_id": job_id,
            "job_type": job_type,
            "payload": payload,
            "priority": priority,
            "document_id": document_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "PENDING",
        }
        
        # Push to Redis list (FIFO queue)
        # We use a sorted set for priority queue
        self.redis.zadd(
            self.queue_name,
            {json.dumps(job_data): priority}
        )
        
        # Also store in hash for lookup
        self.redis.hset(
            f"smartsortierer:job:{job_id}",
            mapping={
                "data": json.dumps(job_data),
                "status": "PENDING",
            }
        )
        
        return job_id
    
    def dequeue(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Dequeue the next job (blocks until available or timeout).
        
        Args:
            timeout: Seconds to wait for a job
            
        Returns:
            Job data dict or None if timeout
        """
        # Pop lowest priority (highest priority jobs first)
        result = self.redis.bzpopmin(self.queue_name, timeout)
        
        if not result:
            return None
        
        queue_name, job_json, priority = result
        job_data = json.loads(job_json)
        
        # Update status in hash
        job_id = job_data["job_id"]
        self.redis.hset(
            f"smartsortierer:job:{job_id}",
            "status",
            "RUNNING"
        )
        
        return job_data
    
    def complete_job(self, job_id: str, result: Optional[Dict[str, Any]] = None):
        """Mark job as completed"""
        self.redis.hset(
            f"smartsortierer:job:{job_id}",
            mapping={
                "status": "COMPLETED",
                "result": json.dumps(result) if result else None,
                "completed_at": datetime.utcnow().isoformat(),
            }
        )
    
    def fail_job(self, job_id: str, error: str):
        """Mark job as failed"""
        self.redis.hset(
            f"smartsortierer:job:{job_id}",
            mapping={
                "status": "FAILED",
                "error": error,
                "failed_at": datetime.utcnow().isoformat(),
            }
        )
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and result"""
        job_hash = self.redis.hgetall(f"smartsortierer:job:{job_id}")
        
        if not job_hash:
            return None
        
        if job_hash.get("data"):
            job_data = json.loads(job_hash["data"])
            job_data["status"] = job_hash.get("status")
            job_data["result"] = json.loads(job_hash["result"]) if job_hash.get("result") else None
            job_data["error"] = job_hash.get("error")
            return job_data
        
        return None
    
    def get_queue_length(self) -> int:
        """Get number of pending jobs"""
        return self.redis.zcard(self.queue_name)
    
    def health_check(self) -> bool:
        """Check if Redis is reachable"""
        try:
            self.redis.ping()
            return True
        except Exception:
            return False
