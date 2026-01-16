"""
Job execution logic for CIT v1 Job System.
Handles job lifecycle and execution.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from server.job_store import JobStore


class JobManager:
    """Manages job execution and lifecycle."""
    
    def __init__(self, job_store: JobStore = None):
        """
        Initialize job manager.
        
        Args:
            job_store: JobStore instance. If None, creates a new one.
        """
        self.store = job_store or JobStore()
    
    def create_job(self, job_type: str = "generic", payload: dict = None) -> dict:
        """
        Create a new job and return job info.
        
        Args:
            job_type: Type of job to create
            payload: Job payload/parameters
        
        Returns:
            Dictionary with job_id and request_id
        """
        request_id = str(uuid.uuid4())
        job = self.store.create_job(request_id, job_type, payload)
        
        return {
            "ok": True,
            "job_id": job["job_id"],
            "request_id": job["request_id"],
            "state": job["state"],
            "created_at": job["created_at"]
        }
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """
        Get job status by ID.
        
        Args:
            job_id: Job ID
        
        Returns:
            Job status dictionary or None if not found
        """
        job = self.store.get_job(job_id)
        if job is None:
            return None
        
        return {
            "ok": True,
            "job_id": job["job_id"],
            "request_id": job["request_id"],
            "job_type": job["job_type"],
            "state": job["state"],
            "created_at": job["created_at"],
            "updated_at": job["updated_at"],
            "started_at": job.get("started_at"),
            "completed_at": job.get("completed_at")
        }
    
    def get_job_logs(self, job_id: str) -> Optional[dict]:
        """
        Get job logs by ID.
        
        Args:
            job_id: Job ID
        
        Returns:
            Dictionary with logs or None if not found
        """
        logs = self.store.get_logs(job_id)
        if logs is None:
            return None
        
        return {
            "ok": True,
            "job_id": job_id,
            "logs": logs
        }
    
    def start_job(self, job_id: str) -> bool:
        """
        Mark job as running.
        
        Args:
            job_id: Job ID
        
        Returns:
            True if successful
        """
        now = datetime.now(timezone.utc).isoformat()
        success = self.store.update_job(job_id, {
            "state": "running",
            "started_at": now
        })
        
        if success:
            self.store.add_log(job_id, "Job started", "info")
        
        return success
    
    def complete_job(self, job_id: str, success: bool = True, result: dict = None) -> bool:
        """
        Mark job as completed (succeeded or failed).
        
        Args:
            job_id: Job ID
            success: Whether job succeeded
            result: Job result data
        
        Returns:
            True if successful
        """
        now = datetime.now(timezone.utc).isoformat()
        state = "succeeded" if success else "failed"
        
        updates = {
            "state": state,
            "completed_at": now
        }
        
        if result is not None:
            updates["result"] = result
        
        success = self.store.update_job(job_id, updates)
        
        if success:
            self.store.add_log(job_id, f"Job {state}", "info")
        
        return success
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.
        
        Args:
            job_id: Job ID
        
        Returns:
            True if successful
        """
        success = self.store.update_job(job_id, {
            "state": "canceled",
            "completed_at": datetime.now(timezone.utc).isoformat()
        })
        
        if success:
            self.store.add_log(job_id, "Job canceled", "info")
        
        return success
