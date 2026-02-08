"""
JSON Utilities for CIT v2.1
Common JSON file operations with consistent encoding and error handling.
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional


def read_json_file(file_path: str, default: Any = None) -> Any:
    """
    Read JSON file with consistent encoding and error handling.
    
    Args:
        file_path: Path to JSON file
        default: Default value to return on error or file not found
    
    Returns:
        Parsed JSON data or default value
    """
    path = Path(file_path)
    if not path.exists():
        return default
    
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return default


def write_json_file(file_path: str, data: Any, indent: int = 2) -> bool:
    """
    Write JSON file with consistent encoding and formatting.
    
    Args:
        file_path: Path to JSON file
        data: Data to serialize
        indent: Indentation level (default: 2)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=indent, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except (IOError, TypeError):
        return False


def append_json_line(file_path: str, data: Dict) -> bool:
    """
    Append JSON object as a single line (JSONL format).
    
    Args:
        file_path: Path to JSONL file
        data: Dictionary to append
    
    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
        return True
    except (IOError, TypeError):
        return False


def ensure_directory(directory: str) -> None:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
