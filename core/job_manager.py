import uuid
import json
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from core.database import get_db_connection
from core.logger import get_logger

logger = get_logger("job_manager")

class JobManager:
    def __init__(self):
        self.lock = threading.Lock()

    def create_job(self, job_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        with self.lock:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO jobs (job_id, job_type, payload, status, created_at, logs) VALUES (?, ?, ?, ?, ?, ?)",
                (job_id, job_type, json.dumps(payload), "pending", created_at, json.dumps([]))
            )
            conn.commit()
            conn.close()
        return {"ok": True, "job_id": job_id, "status": "pending"}

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        conn.close()
        if not row: return None
        res = dict(row)
        res["payload"] = json.loads(res["payload"])
        res["result"] = json.loads(res["result"]) if res["result"] else None
        return res

    def list_jobs(self, limit: int = 50):
        conn = get_db_connection()
        rows = conn.execute("SELECT job_id, job_type, status, created_at FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

_manager = None
def get_job_manager():
    global _manager
    if _manager is None: _manager = JobManager()
    return _manager
