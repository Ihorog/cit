"""
Path Configuration for CIT v2.1
Centralized path constants for storage and configuration.
"""
from pathlib import Path


# Base directories
BASE_DIR = Path(__file__).parent.parent
STORAGE_DIR = BASE_DIR / "storage"
CONFIG_DIR = BASE_DIR / "config"

# Storage paths
REGISTRY_DIR = STORAGE_DIR / "registry"
JOBS_DIR = STORAGE_DIR / "jobs"
AUDIT_LOG_DIR = STORAGE_DIR / "audit"

# Registry files
CIT_CORE_REGISTRY = REGISTRY_DIR / "cit_core.json"
MATRIX_REGISTRY = BASE_DIR / "docs" / "wiki" / "registry" / "matrix.json"

# Configuration files
CIMEIKA_MATRIX_CONFIG = BASE_DIR / "cimeika_matrix.yaml"
ENV_EXAMPLE = BASE_DIR / ".env.example"


def get_registry_path(registry_name: str = "cit_core") -> Path:
    """
    Get path to a registry file.
    
    Args:
        registry_name: Name of the registry (without extension)
    
    Returns:
        Path to registry file
    """
    return REGISTRY_DIR / f"{registry_name}.json"


def get_job_file_path(job_id: str) -> Path:
    """
    Get path to a job file.
    
    Args:
        job_id: Job ID
    
    Returns:
        Path to job file
    """
    return JOBS_DIR / f"{job_id}.json"


def ensure_storage_dirs() -> None:
    """Create all standard storage directories if they don't exist."""
    for directory in [STORAGE_DIR, REGISTRY_DIR, JOBS_DIR, AUDIT_LOG_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
