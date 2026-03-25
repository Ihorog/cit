"""
Spark Engine v2 — partitioned by repo role.
CF Workers (cimeika-backend) → TypeScript data handled as raw text corpus.
ci-memory MIND.md → special semantic partition.
Termux-safe: local[*], 512m driver memory.
"""
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType
from pathlib import Path
import json

RAW_PATH  = Path("dani/spark/raw/raw_corpus.json")
ROLE_INDEX_PATH  = Path("dani/spark/raw/role_index.json")
OUT_PATH  = Path("dani/spark/indexed")

SCHEMA = StructType([
    StructField("repo",    StringType(), True),
    StructField("path",    StringType(), True),
    StructField("role",    StringType(), True),
    StructField("content", StringType(), True),
    StructField("sha",     StringType(), True),
])

def get_session(app_name: str = "CIT-Spark-v2") -> SparkSession:
    """
    Termux: local[*], 512m RAM.
    Vercel Edge / Cloudflare Workers: incompatible — use lightweight fallback.
    Cloud future: extend with .remote('sc://host') for Spark Connect.
    """
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", "512m")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

def transform(df: DataFrame) -> DataFrame:
    return (
        df
        .withColumn("module",       F.regexp_extract("path", r"(?:agents|modules|routers)/([^/]+)/", 1))
        .withColumn("file_ext",     F.regexp_extract("path", r"\.([a-zA-Z]+)$", 1))
        .withColumn("content_len",  F.length("content"))
        .withColumn("is_agent",     F.col("path").rlike(r"agents/"))
        .withColumn("is_memory",    F.col("role") == F.lit("shared_memory"))
        .withColumn("lang",
            F.when(F.col("file_ext").isin("ts", "tsx"), "typescript")
             .when(F.col("file_ext").isin("py"),        "python")
             .when(F.col("file_ext").isin("md"),        "markdown")
             .when(F.col("file_ext").isin("yaml", "yml"), "yaml")
             .when(F.col("file_ext").isin("json"),      "json")
             .otherwise("other")
        )
    )

def run_pipeline() -> dict:
    OUT_PATH.mkdir(parents=True, exist_ok=True)
    spark = get_session()
    try:
        raw  = json.loads(RAW_PATH.read_text())
        df   = spark.createDataFrame(raw, schema=SCHEMA)
        df_t = transform(df)

        # Write partitioned by role
        df_t.write.mode("overwrite").partitionBy("role").parquet(str(OUT_PATH / "corpus"))

        # Summary per repo + role + lang
        summary = (
            df_t.groupBy("repo", "role", "lang")
                .agg(
                    F.count("*").alias("files"),
                    F.sum("content_len").alias("total_chars")
                )
                .orderBy("role", "repo")
                .toPandas()
                .to_dict(orient="records")
        )

        total = df_t.count()

        return {
            "status": "ok",
            "total_files": total,
            "parquet_path": str(OUT_PATH / "corpus"),
            "summary": summary
        }
    finally:
        spark.stop()
