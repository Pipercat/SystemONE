"""
SmartSortierer Pro - Worker Runner
Processes jobs from Redis queue
"""
import os
import sys
import time
import signal
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from app.services.queue import JobQueue
from app.core.config import settings
from handlers.extract_text import ExtractTextHandler
from handlers.chunk_text import ChunkTextHandler
from handlers.embed_chunks import EmbedChunksHandler
from handlers.classify_document import ClassifyDocumentHandler


# Job handlers mapping
HANDLERS = {
    "extract_text": ExtractTextHandler(),
    "chunk_text": ChunkTextHandler(),
    "embed_chunks": EmbedChunksHandler(),
    "classify_document": ClassifyDocumentHandler(),
}


class Worker:
    """Background job processor"""
    
    def __init__(self):
        self.queue = JobQueue()
        self.running = True
        self.worker_id = f"worker-{os.getpid()}"
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def shutdown(self, signum, frame):
        """Graceful shutdown on SIGINT/SIGTERM"""
        print(f"\n[{self.worker_id}] Shutdown signal received. Finishing current job...")
        self.running = False
    
    def process_job(self, job_data: dict):
        """Process a single job"""
        job_id = job_data["job_id"]
        job_type = job_data["job_type"]
        payload = job_data["payload"]
        
        print(f"[{self.worker_id}] Processing job {job_id} (type: {job_type})")
        
        handler = HANDLERS.get(job_type)
        
        if not handler:
            error = f"Unknown job type: {job_type}"
            print(f"[{self.worker_id}] ERROR: {error}")
            self.queue.fail_job(job_id, error)
            return
        
        try:
            # Execute handler
            result = handler.execute(payload)
            
            # Mark job as completed
            self.queue.complete_job(job_id, result)
            print(f"[{self.worker_id}] ✓ Job {job_id} completed successfully")
        
        except Exception as e:
            error = f"{type(e).__name__}: {str(e)}"
            print(f"[{self.worker_id}] ✗ Job {job_id} failed: {error}")
            self.queue.fail_job(job_id, error)
    
    def run(self):
        """Main worker loop"""
        print(f"[{self.worker_id}] Worker started")
        print(f"[{self.worker_id}] Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        print(f"[{self.worker_id}] Storage: {settings.STORAGE_ROOT}")
        
        # Health check
        if not self.queue.health_check():
            print(f"[{self.worker_id}] ERROR: Cannot connect to Redis. Exiting.")
            return
        
        print(f"[{self.worker_id}] ✓ Redis connection OK")
        print(f"[{self.worker_id}] Waiting for jobs...\n")
        
        while self.running:
            try:
                # Dequeue next job (blocks for 5 seconds)
                job_data = self.queue.dequeue(timeout=5)
                
                if job_data:
                    self.process_job(job_data)
                else:
                    # No job available, just continue
                    pass
            
            except KeyboardInterrupt:
                print(f"\n[{self.worker_id}] Interrupted by user")
                break
            
            except Exception as e:
                print(f"[{self.worker_id}] ERROR: {e}")
                time.sleep(5)  # Wait before retry
        
        print(f"[{self.worker_id}] Worker stopped")


def main():
    worker = Worker()
    worker.run()


if __name__ == "__main__":
    main()
