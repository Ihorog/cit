"""
Tests for TZ #001: ci system agent files
Validates that required files exist, scripts have valid syntax,
and bin/ci subcommands produce expected output.
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASS = 0
FAIL = 0


def ok(msg):
    global PASS
    PASS += 1
    print(f"✓ {msg}")


def fail(msg):
    global FAIL
    FAIL += 1
    print(f"✗ {msg}")


def check(condition, msg):
    if condition:
        ok(msg)
    else:
        fail(msg)


def test_required_files_exist():
    """All files from TZ #001 file structure must exist."""
    print("\n--- test_required_files_exist ---")
    required = [
        "install.sh",
        "bin/ci",
        "config/aichat.yaml",
        "config/roles/cimeika.md",
    ]
    for rel in required:
        path = ROOT / rel
        check(path.exists(), f"{rel} exists")


def test_scripts_executable():
    """Shell scripts must have the executable bit set."""
    print("\n--- test_scripts_executable ---")
    for rel in ("install.sh", "bin/ci"):
        path = ROOT / rel
        check(os.access(path, os.X_OK), f"{rel} is executable")


def test_shell_syntax():
    """Shell scripts must pass bash -n (syntax check)."""
    print("\n--- test_shell_syntax ---")
    for rel in ("install.sh", "bin/ci"):
        path = ROOT / rel
        result = subprocess.run(
            ["bash", "-n", str(path)],
            capture_output=True,
            text=True,
        )
        check(result.returncode == 0, f"{rel} syntax valid")


def test_ci_help_output():
    """bin/ci without arguments should print usage info."""
    print("\n--- test_ci_help_output ---")
    result = subprocess.run(
        ["bash", str(ROOT / "bin/ci"), "--help"],
        capture_output=True,
        text=True,
    )
    check(result.returncode == 0, "ci --help exits 0")
    check("chat" in result.stdout, "ci --help mentions chat")
    check("status" in result.stdout, "ci --help mentions status")
    check("sync" in result.stdout, "ci --help mentions sync")


def test_ci_status_output():
    """bin/ci status should print health check header and Ci: Активний."""
    print("\n--- test_ci_status_output ---")
    result = subprocess.run(
        ["bash", str(ROOT / "bin/ci"), "status"],
        capture_output=True,
        text=True,
    )
    check(result.returncode == 0, "ci status exits 0")
    # Strip ANSI codes for text matching
    import re
    clean = re.sub(r'\033\[[0-9;]*m', '', result.stdout)
    check("CIMEIKA HEALTH CHECK" in clean, "ci status shows CIMEIKA HEALTH CHECK")
    check("Ci:" in clean, "ci status shows Ci: status line")


def test_ci_unknown_command():
    """bin/ci with unknown command should exit non-zero."""
    print("\n--- test_ci_unknown_command ---")
    result = subprocess.run(
        ["bash", str(ROOT / "bin/ci"), "nonexistent"],
        capture_output=True,
        text=True,
    )
    check(result.returncode != 0, "ci <unknown> exits non-zero")


def test_cimeika_role_content():
    """config/roles/cimeika.md must contain key role definitions."""
    print("\n--- test_cimeika_role_content ---")
    content = (ROOT / "config/roles/cimeika.md").read_text(encoding="utf-8")
    check("Оркестратор" in content, "cimeika.md mentions Оркестратор")
    check("українською" in content, "cimeika.md enforces Ukrainian language")
    check("Ci" in content, "cimeika.md identifies as Ci")


def test_aichat_config_content():
    """config/aichat.yaml must contain model and clients config."""
    print("\n--- test_aichat_config_content ---")
    content = (ROOT / "config/aichat.yaml").read_text(encoding="utf-8")
    check("model:" in content, "aichat.yaml has model setting")
    check("openai" in content, "aichat.yaml references openai")


if __name__ == "__main__":
    test_required_files_exist()
    test_scripts_executable()
    test_shell_syntax()
    test_ci_help_output()
    test_ci_status_output()
    test_ci_unknown_command()
    test_cimeika_role_content()
    test_aichat_config_content()

    print(f"\n{'='*40}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    if FAIL > 0:
        sys.exit(1)
    print("All tests passed!")
