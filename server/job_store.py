"""
Job storage for CIT v1 Job System.
Stores jobs locally using JSON files (no external dependencies).
"""

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for utils imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.json_handler import read_json_file, write_json_file
from utils.time_utils import now_utc_iso
from config.paths import JOBS_DIR


class JobStore:
    """Simple file-based job storage using JSON."""
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize job store.
        
        Args:
            storage_dir: Directory to store job data. Defaults to storage/jobs/
        """
        if storage_dir is None:
            self.storage_dir = JOBS_DIR
        else:
            self.storage_dir = Path(storage_dir)
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def create_job(self, request_id: str, job_type: str = "generic", payload: dict = None) -> dict:
        """
        Create a new job.
        
        Args:
            request_id: Request ID associated with this job
            job_type: Type of job (e.g., "generic", "github_task", "toolbox")
            payload: Job payload/parameters
        
        Returns:
            Job object with job_id and initial state
        """
        job_id = str(uuid.uuid4())
        now = now_utc_iso()
        
        job = {
            "job_id": job_id,
            "request_id": request_id,
            "job_type": job_type,
            "state": "queued",
            "payload": payload or {},
            "created_at": now,
            "updated_at": now,
            "started_at": None,
            "completed_at": None,
            "logs": []
        }
        
        self._save_job(job)
        return job
    
    def get_job(self, job_id: str) -> Optional[dict]:
        """
        Get job by ID.
        
        Args:
            job_id: Job ID
        
        Returns:
            Job object or None if not found
        """
        job_file = self.storage_dir / f"{job_id}.json"
        return read_json_file(str(job_file))
    
    def update_job(self, job_id: str, updates: dict) -> bool:
        """
        Update job fields.
        
        Args:
            job_id: Job ID
            updates: Dictionary of fields to update
        
        Returns:
            True if successful, False if job not found
        """
        job = self.get_job(job_id)
        if job is None:
            return False
        
        job.update(updates)
        job["updated_at"] = now_utc_iso()
        
        self._save_job(job)
        return True
    
    def add_log(self, job_id: str, message: str, level: str = "info") -> bool:
        """
        Add a log entry to the job.
        
        Args:
            job_id: Job ID
            message: Log message
            level: Log level (info, warning, error)
        
        Returns:
            True if successful, False if job not found
        """
        job = self.get_job(job_id)
        if job is None:
            return False
        
        log_entry = {
            "timestamp": now_utc_iso(),
            "level": level,
            "message": message
        }
        
        job["logs"].append(log_entry)
        job["updated_at"] = now_utc_iso()
        
        self._save_job(job)
        return True
    
    def get_logs(self, job_id: str) -> Optional[List[dict]]:
        """
        Get all logs for a job.
        
        Args:
            job_id: Job ID
        
        Returns:
            List of log entries or None if job not found
        """
        job = self.get_job(job_id)
        if job is None:
            return None
        
        return job.get("logs", [])
    
    def list_jobs(self, limit: int = 100) -> List[dict]:
        """
        List recent jobs.
        
        Args:
            limit: Maximum number of jobs to return
        
        Returns:
            List of job objects, sorted by creation time (newest first)
        """
        jobs = []
        
        for job_file in sorted(self.storage_dir.glob("*.json"), reverse=True):
            if len(jobs) >= limit:
                break
            
            try:
                job = read_json_file(str(job_file))
                if job:
                    jobs.append(job)
            except Exception:
                continue
        
        return jobs
    
    def _save_job(self, job: dict):
        """Save job to disk."""
        job_file = self.storage_dir / f"{job['job_id']}.json"
        write_json_file(str(job_file), job, indent=2)
