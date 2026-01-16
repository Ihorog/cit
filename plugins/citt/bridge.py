"""
Bridge to execute GitHub toolbox commands from CIT.
Executes CITT (private toolbox) commands as subprocess and captures output.
"""

import subprocess
import json
from typing import Dict, Optional
import os
from pathlib import Path


class CITTBridge:
    """Bridge to execute private GitHub toolbox commands."""
    
    def __init__(self, citt_path: Optional[str] = None):
        """
        Initialize CITT bridge.
        
        Args:
            citt_path: Path to CITT toolbox. If None, uses CITT_PATH env var.
        """
        self.citt_path = citt_path or os.getenv("CITT_PATH")
        if not self.citt_path:
            raise ValueError("CITT_PATH not set. Set CITT_PATH environment variable to citt repository path.")
    
    def execute_tool(self, tool_name: str, payload: dict) -> dict:
        """
        Execute a CITT tool with given payload.
        
        Args:
            tool_name: Name of the tool (e.g., 'gh_auth_check', 'issue_create')
            payload: JSON payload to pass to the tool
        
        Returns:
            Dictionary with stdout, stderr, returncode
        """
        tool_path = Path(self.citt_path) / "tools" / f"{tool_name}.py"
        
        if not tool_path.exists():
            return {
                "ok": False,
                "error": f"Tool not found: {tool_name}",
                "tool_path": str(tool_path)
            }
        
        try:
            # Execute tool with JSON payload via stdin
            result = subprocess.run(
                ["python3", str(tool_path)],
                input=json.dumps(payload).encode('utf-8'),
                capture_output=True,
                timeout=60
            )
            
            return {
                "ok": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout.decode('utf-8', errors='replace'),
                "stderr": result.stderr.decode('utf-8', errors='replace')
            }
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "error": "Tool execution timed out",
                "timeout": 60
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "type": e.__class__.__name__
            }
    
    def gh_auth_check(self) -> dict:
        """Check GitHub authentication."""
        return self.execute_tool("gh_auth_check", {})
    
    def create_issue(self, title: str, body: str, labels: list = None) -> dict:
        """Create a GitHub issue."""
        payload = {
            "title": title,
            "body": body,
            "labels": labels or []
        }
        return self.execute_tool("issue_create", payload)
    
    def create_branch(self, branch_name: str, base: str = "main") -> dict:
        """Create a GitHub branch."""
        payload = {
            "branch_name": branch_name,
            "base": base
        }
        return self.execute_tool("branch_create", payload)
    
    def open_pr(self, title: str, body: str, head: str, base: str = "main") -> dict:
        """Open a pull request."""
        payload = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        return self.execute_tool("pr_open", payload)
