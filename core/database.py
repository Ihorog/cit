import sqlite3
from pathlib import Path
def get_db_connection():
    db_path = Path(__file__).parent.parent / "storage" / "cit_system.db"
    db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS jobs (job_id TEXT PRIMARY KEY, job_type TEXT, payload TEXT, status TEXT, created_at TEXT, started_at TEXT, completed_at TEXT, result TEXT, error TEXT, logs TEXT)')
    conn.commit()
    conn.close()
