"""
FastAPI router — mounts at /api/spark.
Activates the Spark dormant module and reflects state in manifest.json.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pathlib import Path
import json
from datetime import datetime
from .github_ingestor import ingest_all
from .spark_engine import run_pipeline, get_session, OUT_PATH

router = APIRouter(prefix="/api/spark", tags=["spark"])
MANIFEST_PATH = Path("manifest.json")


def _update_manifest(status: str, summary: list, total_files: int = 0):
    """Reflect Spark ability state into manifest.json via Dzerkalo pattern."""
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text())
    else:
        manifest = {}
    existing = manifest.setdefault("abilities_registry", {}).get("spark", {})
    manifest["abilities_registry"]["spark"] = {
        "path": "/abilities/spark",
        "priority": 11,
        "status": status,
        "trigger": "api:spark",
        # Only record last_run when the pipeline has actually executed
        "last_run": datetime.now().isoformat() if status == "indexed" else existing.get("last_run"),
        "total_files": total_files,
        "datasets": summary,
        "repos": [
            "Ihorog/cit",
            "Ihorog/ci_gitapi",
            "Ihorog/cimeika-unified",
            "Ihorog/cimeika-backend",
            "Ihorog/ci-memory",
            "Ihorog/ciwiki",
            "Ihorog/media",
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))


@router.get("/status")
def spark_status():
    """Returns current Spark ability state from manifest.json."""
    if not MANIFEST_PATH.exists():
        return {"status": "dormant", "manifest": "not_found"}
    manifest = json.loads(MANIFEST_PATH.read_text())
    spark_state = manifest.get("abilities_registry", {}).get("spark", {"status": "dormant"})
    return spark_state


@router.post("/ingest")
async def ingest(background_tasks: BackgroundTasks):
    """Pull all 7 Cimeika repo data via GitHub API → dani/spark/raw/raw_corpus.json"""
    data = await ingest_all()
    background_tasks.add_task(_update_manifest, "ingested", [], len(data))
    return {"status": "ingested", "files": len(data)}


@router.post("/run")
def run_spark():
    """Execute Spark pipeline: raw JSON → transformed Parquet, partitioned by role."""
    try:
        result = run_pipeline()
        _update_manifest("indexed", result.get("summary", []), result.get("total_files", 0))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query")
def spark_query(
    sql: str = "SELECT repo, role, COUNT(*) as n FROM corpus GROUP BY repo, role ORDER BY role"
):
    """Run ad-hoc Spark SQL over indexed corpus Parquet."""
    # Basic guard: only allow SELECT statements to prevent destructive operations
    stripped = sql.strip().upper()
    if not stripped.startswith("SELECT"):
        raise HTTPException(status_code=400, detail="Only SELECT statements are allowed")
    spark = get_session("CIT-Query")
    try:
        df = spark.read.parquet(str(OUT_PATH / "corpus"))
        df.createOrReplaceTempView("corpus")
        result = spark.sql(sql).toPandas().to_dict(orient="records")
        return {"sql": sql, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        spark.stop()
