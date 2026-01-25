#!/usr/bin/env python3
"""
CIT Engine — Модульний рантайм для CIT
Трансформований з ci.py у модульну систему
"""
import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Optional
import subprocess

# Імпортувати PluginRegistry
try:
    from core.plugin_loader import PluginRegistry
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.plugin_loader import PluginRegistry


class CiEngine:
    """Ядро CIT — модульний рантайм з підтримкою плагінів"""
    
    def __init__(self):
        self.registry = PluginRegistry()
        self.config = self.load_config()
        self.modules = {}
    
    def load_config(self) -> dict:
        """Завантажити конфігурацію з cimeika_matrix.yaml та .env"""
        config = {}
        
        # Завантажити cimeika_matrix.yaml
        matrix_path = Path("cimeika_matrix.yaml")
        if matrix_path.exists():
            try:
                config['matrix'] = yaml.safe_load(matrix_path.read_text())
            except Exception as e:
                print(f"⚠️  Error loading cimeika_matrix.yaml: {e}")
        
        # Завантажити змінні середовища
        config['env'] = {
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', ''),
            'OPENAI_MODEL': os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
            'HOST': os.environ.get('HOST', '0.0.0.0'),
            'PORT': int(os.environ.get('PORT', '8790')),
        }
        
        return config
    
    def build(self):
        """Збірка всіх модулів"""
        print("🔨 Building CIT...")
        
        # 1. Виконати scripts/unify.py
        unify_script = Path("scripts/unify.py")
        if unify_script.exists():
            print("\n📦 Running migration script...")
            try:
                subprocess.run([sys.executable, str(unify_script)], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Migration script failed: {e}")
                return False
        
        # 2. Завантажити та валідувати всі модулі
        print("\n🔍 Loading modules...")
        self.modules = self.registry.load_modules()
        
        if not self.modules:
            print("⚠️  No modules loaded")
            return False
        
        # 3. Валідувати залежності
        print("\n🔗 Validating dependencies...")
        for module_id in self.modules:
            deps = self.registry.resolve_dependencies(module_id)
            if deps:
                print(f"  {module_id} → {deps}")
        
        print("\n✅ Build completed successfully!")
        return True
    
    def run(self):
        """Запустити HTTP сервер"""
        print("🚀 Starting CIT Engine...")
        
        # Завантажити модулі
        if not self.modules:
            print("📦 Loading modules...")
            self.modules = self.registry.load_modules()
        
        # Запустити оригінальний ci.py сервер
        ci_script = Path("ci.py")
        if not ci_script.exists():
            print("❌ ci.py not found")
            return False
        
        print(f"🌐 Starting server on {self.config['env']['HOST']}:{self.config['env']['PORT']}")
        print(f"📦 Loaded {len(self.modules)} modules")
        
        # Запустити ci.py
        try:
            subprocess.run([sys.executable, str(ci_script)], check=True)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
        except subprocess.CalledProcessError as e:
            print(f"❌ Server failed: {e}")
            return False
        
        return True
    
    def module(self, module_id: str):
        """Запустити окремий модуль"""
        print(f"🔌 Running module: {module_id}")
        
        # Завантажити модулі
        if not self.modules:
            self.modules = self.registry.load_modules()
        
        module = self.registry.get_module(module_id)
        if not module:
            print(f"❌ Module not found: {module_id}")
            return False
        
        print(f"📦 Module: {module['id']}")
        print(f"   Type: {module['type']}")
        print(f"   Mount: {module['mount']}")
        print(f"   Description: {module.get('description', 'N/A')}")
        
        # Перевірити, чи модуль має entry point
        if 'entry' in module:
            entry_path = Path(f"modules/{module_id}") / module['entry']
            if entry_path.exists():
                print(f"\n🏃 Executing: {entry_path}")
                try:
                    subprocess.run([sys.executable, str(entry_path)], check=True)
                except KeyboardInterrupt:
                    print("\n🛑 Module stopped")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Module failed: {e}")
                    return False
            else:
                print(f"⚠️  Entry point not found: {entry_path}")
        else:
            print(f"⚠️  No entry point defined for module: {module_id}")
        
        return True
    
    def status(self):
        """Показати статус системи"""
        print("📊 CIT Engine Status")
        print("=" * 50)
        
        # Конфігурація
        print("\n🔧 Configuration:")
        print(f"  Host: {self.config['env']['HOST']}")
        print(f"  Port: {self.config['env']['PORT']}")
        print(f"  Model: {self.config['env']['OPENAI_MODEL']}")
        print(f"  API Key: {'✓' if self.config['env']['OPENAI_API_KEY'] else '✗'}")
        
        # Модулі
        print("\n📦 Modules:")
        if not self.modules:
            self.modules = self.registry.load_modules()
        
        for module_id, module in self.modules.items():
            status_icon = "✓" if module.get('status') == 'active' else "◌"
            print(f"  {status_icon} {module_id} ({module['type']})")
            if module.get('dependencies'):
                print(f"    ↳ requires: {', '.join(module['dependencies'])}")


def print_usage():
    """Показати довідку"""
    print("""
CIT Engine — Модульний рантайм для CIT

Usage:
  python core/engine.py <command> [options]

Commands:
  build              Збірка всіх модулів та валідація
  run                Запуск HTTP сервера
  module <id>        Запуск окремого модуля
  status             Показати статус системи
  help               Показати цю довідку

Examples:
  python core/engine.py build
  python core/engine.py run
  python core/engine.py module ciwiki
  python core/engine.py status
""")


def main():
    """Точка входу CLI"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    engine = CiEngine()
    
    if command == "build":
        success = engine.build()
        sys.exit(0 if success else 1)
    
    elif command == "run":
        success = engine.run()
        sys.exit(0 if success else 1)
    
    elif command == "module":
        if len(sys.argv) < 3:
            print("❌ Error: module ID required")
            print("Usage: python core/engine.py module <id>")
            sys.exit(1)
        module_id = sys.argv[2]
        success = engine.module(module_id)
        sys.exit(0 if success else 1)
    
    elif command == "status":
        engine.status()
        sys.exit(0)
    
    elif command in ["help", "-h", "--help"]:
        print_usage()
        sys.exit(0)
    
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
