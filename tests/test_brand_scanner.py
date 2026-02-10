"""
Tests for CIMEIKA Brand Compliance Scanner
Validates scanner detection, report generation, and migration script output
"""

import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brand_compliance_scanner import BrandComplianceScanner, BrandViolation


def test_scanner_init():
    """Test scanner initialization"""
    print("Testing scanner initialization...")

    scanner = BrandComplianceScanner(".")
    assert scanner is not None
    assert scanner.repo_path == Path(".")
    assert scanner.violations == []
    assert 'code' in scanner.BRAND_RULES
    assert 'api_routes' in scanner.BRAND_RULES
    assert 'ui_display' in scanner.BRAND_RULES
    print("✓ Scanner initializes correctly")


def test_violation_dataclass():
    """Test BrandViolation dataclass"""
    print("\nTesting BrandViolation dataclass...")

    v = BrandViolation(
        file_path="test.py",
        line_number=10,
        violation_type="import",
        found="podija",
        expected="podiya",
        severity="critical"
    )
    assert v.file_path == "test.py"
    assert v.line_number == 10
    assert v.violation_type == "import"
    assert v.found == "podija"
    assert v.expected == "podiya"
    assert v.severity == "critical"
    print("✓ BrandViolation stores data correctly")


def test_python_violation_detection():
    """Test detection of violations in Python files"""
    print("\nTesting Python violation detection...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test Python file with violations
        test_file = Path(tmpdir) / "test_module.py"
        test_file.write_text(
            "from modules.podija import handler\n"
            "route = '/podija/api'\n"
            "path = 'modules/podija/main.py'\n",
            encoding='utf-8'
        )

        scanner = BrandComplianceScanner(tmpdir)
        scanner._scan_python_files()

        assert len(scanner.violations) > 0
        found_types = {v.violation_type for v in scanner.violations}
        assert 'import' in found_types or 'folder_path' in found_types
        print(f"✓ Detected {len(scanner.violations)} Python violations")


def test_javascript_violation_detection():
    """Test detection of violations in JavaScript files"""
    print("\nTesting JavaScript violation detection...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test JS file with violations
        test_file = Path(tmpdir) / "test_component.jsx"
        test_file.write_text(
            'import Module from "@/modules/podija/index"\n'
            'const title = "Podiya"\n'
            '<h1>Calendar</h1>\n',
            encoding='utf-8'
        )

        scanner = BrandComplianceScanner(tmpdir)
        scanner._scan_javascript_files()

        assert len(scanner.violations) > 0
        print(f"✓ Detected {len(scanner.violations)} JavaScript violations")


def test_sql_violation_detection():
    """Test detection of violations in SQL files"""
    print("\nTesting SQL violation detection...")

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "schema.sql"
        test_file.write_text(
            "CREATE TYPE persona_type AS ENUM (\n"
            "    'podija',\n"
            "    'nastrij',\n"
            "    'gallery',\n"
            "    'calendar'\n"
            ");\n",
            encoding='utf-8'
        )

        scanner = BrandComplianceScanner(tmpdir)
        scanner._scan_sql_files()

        assert len(scanner.violations) == 4
        for v in scanner.violations:
            assert v.violation_type == 'database_enum'
            assert v.severity == 'critical'
        print(f"✓ Detected {len(scanner.violations)} SQL violations")


def test_config_violation_detection():
    """Test detection of violations in config files"""
    print("\nTesting config violation detection...")

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "config.yml"
        test_file.write_text(
            "modules:\n"
            "  - podija\n"
            "  - nastrij\n",
            encoding='utf-8'
        )

        scanner = BrandComplianceScanner(tmpdir)
        scanner._scan_config_files()

        assert len(scanner.violations) >= 2
        for v in scanner.violations:
            assert v.violation_type == 'config'
            assert v.severity == 'medium'
        print(f"✓ Detected {len(scanner.violations)} config violations")


def test_no_violations_clean_repo():
    """Test scanner reports no violations for clean files"""
    print("\nTesting clean repository (no violations)...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a clean Python file
        test_file = Path(tmpdir) / "clean_module.py"
        test_file.write_text(
            "from modules.podiya import handler\n"
            "route = '/podiya/api'\n",
            encoding='utf-8'
        )

        scanner = BrandComplianceScanner(tmpdir)
        scanner._scan_python_files()

        assert len(scanner.violations) == 0
        print("✓ No false positives on clean files")


def test_report_generation():
    """Test report generation"""
    print("\nTesting report generation...")

    scanner = BrandComplianceScanner(".")
    scanner.violations = [
        BrandViolation("test.py", 1, "import", "podija", "podiya", "critical"),
        BrandViolation("app.js", 5, "ui_display", "Podiya", "ПоДія", "high"),
        BrandViolation("config.yml", 0, "config", "nastrij", "nastriy", "medium"),
    ]

    report = scanner.generate_report()

    assert "CIMEIKA BRAND COMPLIANCE REPORT" in report
    assert "Total Violations**: 3" in report
    assert "CRITICAL" in report
    assert "HIGH PRIORITY" in report
    assert "MEDIUM PRIORITY" in report
    assert "podija" in report
    assert "podiya" in report
    print("✓ Report generated with correct sections")


def test_empty_report():
    """Test report with no violations"""
    print("\nTesting empty report...")

    scanner = BrandComplianceScanner(".")
    report = scanner.generate_report()

    assert "Total Violations**: 0" in report
    assert "No violations found" in report
    print("✓ Empty report generated correctly")


def test_migration_script_generation():
    """Test migration script generation"""
    print("\nTesting migration script generation...")

    scanner = BrandComplianceScanner(".")
    script = scanner.generate_migration_script()

    assert "#!/bin/bash" in script
    assert "set -e" in script
    assert "podija" in script and "podiya" in script
    assert "nastrij" in script and "nastriy" in script
    assert "gallery" in script and "galereya" in script
    assert "calendar" in script and "kalendar" in script
    assert "Migration complete" in script
    print("✓ Migration script generated correctly")


def test_skip_directories():
    """Test that venv/node_modules are skipped"""
    print("\nTesting directory skip logic...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create file in venv (should be skipped)
        venv_dir = Path(tmpdir) / "venv" / "lib"
        venv_dir.mkdir(parents=True)
        venv_file = venv_dir / "module.py"
        venv_file.write_text(
            "from modules.podija import x\n",
            encoding='utf-8'
        )

        # Create file in node_modules (should be skipped)
        nm_dir = Path(tmpdir) / "node_modules" / "pkg"
        nm_dir.mkdir(parents=True)
        nm_file = nm_dir / "index.js"
        nm_file.write_text(
            'import x from "@/modules/podija"\n',
            encoding='utf-8'
        )

        scanner = BrandComplianceScanner(tmpdir)
        violations = scanner.scan_repository()

        assert len(violations) == 0
        print("✓ Skipped venv and node_modules correctly")


def test_brand_rules_completeness():
    """Test that brand rules cover all required mappings"""
    print("\nTesting brand rules completeness...")

    rules = BrandComplianceScanner.BRAND_RULES

    # Code rules
    assert 'podija' in rules['code']
    assert 'nastrij' in rules['code']
    assert 'gallery' in rules['code']
    assert 'calendar' in rules['code']

    # API routes
    assert '/podija/' in rules['api_routes']
    assert '/nastrij/' in rules['api_routes']
    assert '/gallery/' in rules['api_routes']
    assert '/calendar/' in rules['api_routes']

    # UI display
    assert 'Podiya' in rules['ui_display']
    assert 'Podija' in rules['ui_display']
    assert 'Nastriy' in rules['ui_display']

    print("✓ Brand rules are complete")


def main():
    """Run all tests"""
    print("=" * 60)
    print("CIMEIKA Brand Compliance Scanner Tests")
    print("=" * 60)

    try:
        test_scanner_init()
        test_violation_dataclass()
        test_python_violation_detection()
        test_javascript_violation_detection()
        test_sql_violation_detection()
        test_config_violation_detection()
        test_no_violations_clean_repo()
        test_report_generation()
        test_empty_report()
        test_migration_script_generation()
        test_skip_directories()
        test_brand_rules_completeness()

        print("\n" + "=" * 60)
        print("✓ All 12 tests passed!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
