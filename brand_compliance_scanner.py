#!/usr/bin/env python3
"""
CIMEIKA Brand Compliance Scanner
Автоматичне виявлення порушень брендбуку
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class BrandViolation:
    """Порушення брендбуку"""
    file_path: str
    line_number: int
    violation_type: str
    found: str
    expected: str
    severity: str  # critical, high, medium, low


class BrandComplianceScanner:
    """Сканер відповідності брендбуку"""

    # Правила брендбуку
    BRAND_RULES = {
        # Код (folders, imports, variables)
        'code': {
            'podija': {'correct': 'podiya', 'display': 'ПоДія'},
            'nastrij': {'correct': 'nastriy', 'display': 'Настрій'},
            'gallery': {'correct': 'galereya', 'display': 'Галерея'},
            'calendar': {'correct': 'kalendar', 'display': 'Календар'},
        },

        # Database enums
        'database': [
            'podiya', 'nastriy', 'kazkar', 'malya', 'galereya', 'kalendar'
        ],

        # UI display names (must be Ukrainian)
        'ui_display': {
            'Podiya': 'ПоДія',
            'Podija': 'ПоДія',
            'Nastrij': 'Настрій',
            'Nastriy': 'Настрій',
            'Gallery': 'Галерея',
            'Calendar': 'Календар',
        },

        # API routes
        'api_routes': {
            '/podija/': '/podiya/',
            '/nastrij/': '/nastriy/',
            '/gallery/': '/galereya/',
            '/calendar/': '/kalendar/',
        }
    }

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.violations: List[BrandViolation] = []

    def scan_repository(self) -> List[BrandViolation]:
        """Сканування всього репозиторію"""
        print("🔍 Scanning for brand violations...\n")

        self._scan_python_files()
        self._scan_javascript_files()
        self._scan_sql_files()
        self._scan_config_files()

        return self.violations

    def _scan_python_files(self):
        """Сканування Python файлів"""
        print("📄 Scanning Python files...")

        python_files = list(self.repo_path.rglob("*.py"))

        for file_path in python_files:
            if self._should_skip(file_path):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    # Check imports
                    if 'from' in line or 'import' in line:
                        for wrong, correct_data in self.BRAND_RULES['code'].items():
                            if f"/{wrong}/" in line or f".{wrong}." in line:
                                self.violations.append(BrandViolation(
                                    file_path=str(file_path.relative_to(self.repo_path)),
                                    line_number=line_num,
                                    violation_type='import',
                                    found=wrong,
                                    expected=correct_data['correct'],
                                    severity='critical'
                                ))

                    # Check folder references
                    if 'modules/podija' in line:
                        self.violations.append(BrandViolation(
                            file_path=str(file_path.relative_to(self.repo_path)),
                            line_number=line_num,
                            violation_type='folder_path',
                            found='podija',
                            expected='podiya',
                            severity='critical'
                        ))

                    # Check API routes
                    for wrong_route, correct_route in self.BRAND_RULES['api_routes'].items():
                        if wrong_route in line:
                            self.violations.append(BrandViolation(
                                file_path=str(file_path.relative_to(self.repo_path)),
                                line_number=line_num,
                                violation_type='api_route',
                                found=wrong_route,
                                expected=correct_route,
                                severity='high'
                            ))

            except Exception as e:
                print(f"⚠️ Error scanning {file_path}: {e}")

    def _scan_javascript_files(self):
        """Сканування JS/JSX файлів"""
        print("📄 Scanning JavaScript/React files...")

        js_files = (
            list(self.repo_path.rglob("*.js"))
            + list(self.repo_path.rglob("*.jsx"))
            + list(self.repo_path.rglob("*.tsx"))
        )

        for file_path in js_files:
            if self._should_skip(file_path):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    # Check UI display names
                    for wrong_display, correct_display in self.BRAND_RULES['ui_display'].items():
                        if f">{wrong_display}<" in line or f'"{wrong_display}"' in line:
                            self.violations.append(BrandViolation(
                                file_path=str(file_path.relative_to(self.repo_path)),
                                line_number=line_num,
                                violation_type='ui_display',
                                found=wrong_display,
                                expected=correct_display,
                                severity='high'
                            ))

                    # Check imports
                    if 'from' in line and '@/modules/' in line:
                        for wrong in ['podija', 'gallery', 'calendar']:
                            if f'/{wrong}' in line:
                                correct = self.BRAND_RULES['code'][wrong]['correct']
                                self.violations.append(BrandViolation(
                                    file_path=str(file_path.relative_to(self.repo_path)),
                                    line_number=line_num,
                                    violation_type='import',
                                    found=wrong,
                                    expected=correct,
                                    severity='critical'
                                ))

            except Exception as e:
                print(f"⚠️ Error scanning {file_path}: {e}")

    def _scan_sql_files(self):
        """Сканування SQL файлів"""
        print("📄 Scanning SQL files...")

        sql_files = list(self.repo_path.rglob("*.sql"))

        for file_path in sql_files:
            if self._should_skip(file_path):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if 'CREATE TYPE persona_type' in content or 'ENUM' in content:
                    wrong_values = ['podija', 'nastrij', 'gallery', 'calendar']
                    for wrong in wrong_values:
                        if f"'{wrong}'" in content:
                            correct = self.BRAND_RULES['code'].get(
                                wrong, {}
                            ).get('correct', wrong)
                            self.violations.append(BrandViolation(
                                file_path=str(file_path.relative_to(self.repo_path)),
                                line_number=0,
                                violation_type='database_enum',
                                found=wrong,
                                expected=correct,
                                severity='critical'
                            ))

            except Exception as e:
                print(f"⚠️ Error scanning {file_path}: {e}")

    def _scan_config_files(self):
        """Сканування конфігураційних файлів"""
        print("📄 Scanning config files...")

        config_patterns = ['*.json', '*.yml', '*.yaml', '*.toml', '.env*']
        config_files = []

        for pattern in config_patterns:
            config_files.extend(self.repo_path.rglob(pattern))

        for file_path in config_files:
            if self._should_skip(file_path):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                for wrong, correct_data in self.BRAND_RULES['code'].items():
                    if wrong in content:
                        self.violations.append(BrandViolation(
                            file_path=str(file_path.relative_to(self.repo_path)),
                            line_number=0,
                            violation_type='config',
                            found=wrong,
                            expected=correct_data['correct'],
                            severity='medium'
                        ))

            except Exception:
                pass  # Skip binary files

    def _should_skip(self, file_path: Path) -> bool:
        """Перевірка чи файл потрібно пропустити"""
        skip_dirs = {'venv', '.venv', 'node_modules', '__pycache__', '.git'}
        return any(part in skip_dirs for part in file_path.parts)

    def generate_report(self) -> str:
        """Генерація звіту"""
        report = ["# 🔍 CIMEIKA BRAND COMPLIANCE REPORT\n\n"]
        report.append(
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )
        report.append(f"**Total Violations**: {len(self.violations)}\n\n")

        # Group by severity
        by_severity: Dict[str, List[BrandViolation]] = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }

        for violation in self.violations:
            by_severity[violation.severity].append(violation)

        # Critical violations
        if by_severity['critical']:
            count = len(by_severity['critical'])
            report.append(f"## 🔴 CRITICAL VIOLATIONS ({count})\n\n")
            for v in by_severity['critical']:
                report.append(f"**{v.file_path}:{v.line_number}**\n")
                report.append(f"- Type: `{v.violation_type}`\n")
                report.append(
                    f"- Found: `{v.found}` → Expected: `{v.expected}`\n\n"
                )

        # High priority
        if by_severity['high']:
            count = len(by_severity['high'])
            report.append(f"## 🟠 HIGH PRIORITY ({count})\n\n")
            for v in by_severity['high']:
                report.append(f"**{v.file_path}:{v.line_number}**\n")
                report.append(f"- Type: `{v.violation_type}`\n")
                report.append(
                    f"- Found: `{v.found}` → Expected: `{v.expected}`\n\n"
                )

        # Medium
        if by_severity['medium']:
            count = len(by_severity['medium'])
            report.append(f"## 🟡 MEDIUM PRIORITY ({count})\n\n")
            for v in by_severity['medium']:
                report.append(f"**{v.file_path}:{v.line_number}**\n")
                report.append(f"- Type: `{v.violation_type}`\n")
                report.append(
                    f"- Found: `{v.found}` → Expected: `{v.expected}`\n\n"
                )

        if not self.violations:
            report.append("## ✅ No violations found!\n")

        return "".join(report)

    def generate_migration_script(self) -> str:
        """Генерація migration скрипту"""
        script = ["#!/bin/bash\n"]
        script.append("# CIMEIKA Brand Compliance Migration Script\n")
        script.append("# Auto-generated - Review before executing!\n\n")
        script.append("set -e\n\n")

        # Folder renames
        script.append("echo '📁 Renaming folders...'\n")
        renames = [
            ('podija', 'podiya'),
            ('nastrij', 'nastriy'),
        ]
        for old, new in renames:
            script.append(
                f"find . -type d -name '{old}' "
                f"-exec bash -c 'mv \"$0\" \"${{0%{old}}}{new}\"' {{}} \\;\n"
            )
        # Module-scoped renames
        module_renames = [
            ('gallery', 'galereya'),
            ('calendar', 'kalendar'),
        ]
        for old, new in module_renames:
            script.append(
                f"find . -type d -name '{old}' -path '*/modules/*' "
                f"-exec bash -c 'mv \"$0\" \"${{0%{old}}}{new}\"' {{}} \\;\n"
            )

        script.append("\n")

        # File content replacements
        script.append("echo '📝 Updating file contents...'\n")

        replacements = [
            ("modules/podija", "modules/podiya"),
            ("modules/nastrij", "modules/nastriy"),
            ("modules/gallery", "modules/galereya"),
            ("modules/calendar", "modules/kalendar"),
            ("/podija/", "/podiya/"),
            ("/nastrij/", "/nastriy/"),
            ("/gallery/", "/galereya/"),
            ("/calendar/", "/kalendar/"),
            ("'podija'", "'podiya'"),
            ("'nastrij'", "'nastriy'"),
            ("'gallery'", "'galereya'"),
            ("'calendar'", "'kalendar'"),
        ]

        for old, new in replacements:
            script.append(
                "find . -type f \\( -name '*.py' -o -name '*.js' "
                "-o -name '*.jsx' -o -name '*.sql' \\) \\\n"
            )
            script.append(f"  -exec sed -i 's|{old}|{new}|g' {{}} +\n")

        script.append("\necho '✅ Migration complete!'\n")
        script.append(
            "echo '⚠️ Please review changes and run tests before committing'\n"
        )

        return "".join(script)


def main():
    """Main execution"""
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    scanner = BrandComplianceScanner(repo_path)

    print("=" * 60)
    print("🔍 CIMEIKA BRAND COMPLIANCE SCANNER")
    print("=" * 60 + "\n")

    violations = scanner.scan_repository()

    print(f"\n{'=' * 60}")
    print("📊 SCAN COMPLETE")
    print(f"{'=' * 60}")
    print(f"Total violations found: {len(violations)}")

    # Generate reports
    report = scanner.generate_report()
    migration_script = scanner.generate_migration_script()

    # Save files
    with open('BRAND_COMPLIANCE_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print("✅ Report saved: BRAND_COMPLIANCE_REPORT.md")

    with open('migrate_brand_compliance.sh', 'w', encoding='utf-8') as f:
        f.write(migration_script)
    os.chmod('migrate_brand_compliance.sh', 0o755)
    print("✅ Migration script saved: migrate_brand_compliance.sh")

    print("\n🎯 Next steps:")
    print("1. Review BRAND_COMPLIANCE_REPORT.md")
    print("2. Run: ./migrate_brand_compliance.sh")
    print("3. Test all modules")
    print("4. Commit changes")


if __name__ == "__main__":
    main()
