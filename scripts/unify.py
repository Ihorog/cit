#!/usr/bin/env python3
"""
Міграційний скрипт для об'єднання репозиторіїв у modules/
Копіює файли з дедуплікацією та реєструє модулі
"""
import shutil
import yaml
import json
from pathlib import Path
from typing import Dict


# Мапа репозиторіїв для інтеграції
REPOS = {
    'wiki': '../ciwiki',
    'unified': '../cimeika-unified',
    'media': '../media',
    'vercel': '../cit_versel'
}

# Директорії та файли, які потрібно виключити при копіюванні
EXCLUDE = {'.git', 'node_modules', 'venv', '__pycache__', '.pytest_cache', 
           'dist', 'build', '.next', '.vercel', '.env', '.DS_Store'}


def copy_unique(source: Path, target: Path):
    """Копіювати файли з виключенням непотрібних"""
    if not source.exists():
        print(f"⚠️  Source not found: {source}")
        return 0
    
    copied = 0
    
    for item in source.rglob('*'):
        # Перевірити, чи потрібно виключити
        if any(ex in item.parts for ex in EXCLUDE):
            continue
        
        rel_path = item.relative_to(source)
        dest = target / rel_path
        
        if item.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(item, dest)
                copied += 1
            except Exception as e:
                print(f"⚠️  Error copying {item}: {e}")
    
    return copied


def register_module(manifest: Dict) -> bool:
    """Додати модуль до registry/modules.json"""
    registry_path = Path('registry/modules.json')
    
    # Завантажити існуючий реєстр
    if not registry_path.exists():
        registry = {
            "version": "1.0.0",
            "core": "Ihorog/cit",
            "modules": []
        }
    else:
        try:
            registry = json.loads(registry_path.read_text())
        except Exception as e:
            print(f"❌ Error loading registry: {e}")
            return False
    
    # Перевірити, чи модуль вже зареєстрований
    module_id = manifest['id']
    if any(m['id'] == module_id for m in registry['modules']):
        print(f"  ℹ️  Module already registered: {module_id}")
        return True
    
    # Додати новий модуль
    registry['modules'].append({
        "id": module_id,
        "status": "active",
        "requires": manifest.get('dependencies', [])
    })
    
    # Зберегти реєстр
    try:
        registry_path.write_text(
            json.dumps(registry, indent=2, ensure_ascii=False)
        )
        print(f"  ✓ Registered in registry: {module_id}")
        return True
    except Exception as e:
        print(f"  ❌ Error saving registry: {e}")
        return False


def integrate():
    """Інтегрувати всі репозиторії"""
    print("🧬 Початок унікації репозиторіїв...")
    print("=" * 60)
    
    total_copied = 0
    total_modules = 0
    
    for name, source_path in REPOS.items():
        print(f"\n📦 Processing: {name}")
        
        source = Path(source_path)
        target = Path(f'modules/{name}')
        
        # Перевірити джерело
        if not source.exists():
            print(f"  ⚠️  Source not found: {source_path}")
            print(f"  ℹ️  Skipping (repository may need to be cloned separately)")
            continue
        
        # Створити target директорію
        target.mkdir(parents=True, exist_ok=True)
        
        # Копіювати з дедуплікацією
        print(f"  📁 Copying files...")
        copied = copy_unique(source, target)
        total_copied += copied
        print(f"  ✓ Copied {copied} files")
        
        # Реєстрація в registry/modules.json
        manifest_path = target / "manifest.yaml"
        if manifest_path.exists():
            try:
                manifest = yaml.safe_load(manifest_path.read_text())
                if register_module(manifest):
                    total_modules += 1
            except Exception as e:
                print(f"  ❌ Error loading manifest: {e}")
        else:
            print(f"  ⚠️  Manifest not found: {manifest_path}")
    
    print("\n" + "=" * 60)
    print(f"✅ Унікація завершена!")
    print(f"📊 Summary:")
    print(f"  • Modules processed: {len(REPOS)}")
    print(f"  • Modules registered: {total_modules}")
    print(f"  • Files copied: {total_copied}")


def validate_manifests():
    """Валідувати всі маніфести"""
    print("\n🔍 Validating manifests...")
    
    try:
        # Додати батьківську директорію до sys.path для імпорту
        import sys
        from pathlib import Path
        parent_dir = Path(__file__).parent.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
        
        from core.plugin_loader import PluginRegistry
        
        registry = PluginRegistry()
        
        modules_dir = Path('modules')
        valid = 0
        invalid = 0
        
        for manifest_file in modules_dir.rglob('manifest.yaml'):
            try:
                manifest = yaml.safe_load(manifest_file.read_text())
                if registry.validate_manifest(manifest):
                    print(f"  ✓ {manifest_file.relative_to(modules_dir)}")
                    valid += 1
                else:
                    print(f"  ✗ {manifest_file.relative_to(modules_dir)}")
                    invalid += 1
            except Exception as e:
                print(f"  ❌ {manifest_file.relative_to(modules_dir)}: {e}")
                invalid += 1
        
        print(f"\n📊 Validation: {valid} valid, {invalid} invalid")
        return invalid == 0
        
    except ImportError as e:
        print(f"  ⚠️  Could not import PluginRegistry for validation: {e}")
        return True


if __name__ == "__main__":
    integrate()
    validate_manifests()
