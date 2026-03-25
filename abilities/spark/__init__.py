"""
Spark Ability — dormant analytics node for CIT organism.
Activate via: POST /api/spark/ingest + POST /api/spark/run
"""
from .spark_routes import router as spark_router

__all__ = ["spark_router"]
