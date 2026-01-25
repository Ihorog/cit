#!/usr/bin/env python3
"""
Plugin Loader для CIT
Динамічна реєстрація та завантаження модулів
"""
import json
import yaml
import jsonschema
from pathlib import Path
from typing import Dict, List, Optional


class PluginRegistry:
    """Реєстр модулів CIT з підтримкою динамічного завантаження"""
    
    def __init__(self, registry_path: str = "registry/modules.json"):
        self.registry_path = Path(registry_path)
        self.modules: Dict[str, dict] = {}
        self.schema_path = Path("core/manifest.schema.json")
    
    def load_schema(self) -> dict:
        """Завантажити JSON Schema для валідації маніфестів"""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {self.schema_path}")
        return json.loads(self.schema_path.read_text())
    
    def validate_manifest(self, manifest: dict) -> bool:
        """Валідувати маніфест через JSON Schema"""
        try:
            schema = self.load_schema()
            jsonschema.validate(manifest, schema)
            return True
        except jsonschema.ValidationError as e:
            print(f"❌ Validation error: {e.message}")
            return False
        except Exception as e:
            print(f"❌ Error loading schema: {e}")
            return False
    
    def load_modules(self) -> Dict[str, dict]:
        """Завантажити модулі з registry/modules.json"""
        if not self.registry_path.exists():
            print(f"⚠️  Registry not found: {self.registry_path}")
            return {}
        
        try:
            data = json.loads(self.registry_path.read_text())
            
            # Спочатку сканувати всі маніфести в modules/
            modules_dir = Path("modules")
            manifests = {}
            
            if modules_dir.exists():
                for manifest_file in modules_dir.rglob("manifest.yaml"):
                    try:
                        manifest = yaml.safe_load(manifest_file.read_text())
                        module_id = manifest.get('id')
                        if module_id:
                            manifests[module_id] = manifest
                    except Exception as e:
                        print(f"⚠️  Error reading {manifest_file}: {e}")
            
            # Завантажити модулі з registry
            for module in data.get("modules", []):
                module_id = module['id']
                
                if module_id in manifests:
                    manifest = manifests[module_id]
                    
                    # Валідувати маніфест
                    if self.validate_manifest(manifest):
                        self.modules[module_id] = {
                            **manifest,
                            "status": module.get("status", "active")
                        }
                        print(f"✓ Loaded module: {module_id}")
                    else:
                        print(f"⚠️  Invalid manifest: {module_id}")
                else:
                    print(f"⚠️  Manifest not found for module: {module_id}")
            
            return self.modules
        except Exception as e:
            print(f"❌ Error loading modules: {e}")
            return {}
    
    def register_module(self, manifest: dict) -> bool:
        """Додати новий модуль до registry"""
        if not self.validate_manifest(manifest):
            return False
        
        module_id = manifest['id']
        
        # Завантажити існуючий реєстр
        if self.registry_path.exists():
            registry = json.loads(self.registry_path.read_text())
        else:
            registry = {
                "version": "1.0.0",
                "core": "Ihorog/cit",
                "modules": []
            }
        
        # Перевірити, чи модуль вже зареєстрований
        existing = next((m for m in registry['modules'] if m['id'] == module_id), None)
        
        if existing:
            print(f"⚠️  Module already registered: {module_id}")
            return False
        
        # Додати новий модуль
        registry['modules'].append({
            "id": module_id,
            "status": "active",
            "requires": manifest.get('dependencies', [])
        })
        
        # Зберегти реєстр
        self.registry_path.write_text(
            json.dumps(registry, indent=2, ensure_ascii=False)
        )
        
        print(f"✓ Registered module: {module_id}")
        return True
    
    def get_module(self, module_id: str) -> Optional[dict]:
        """Отримати інформацію про модуль"""
        return self.modules.get(module_id)
    
    def list_modules(self) -> List[str]:
        """Отримати список всіх модулів"""
        return list(self.modules.keys())
    
    def resolve_dependencies(self, module_id: str) -> List[str]:
        """Визначити граф залежностей для модуля"""
        if module_id not in self.modules:
            return []
        
        dependencies = []
        visited = set()
        
        def _resolve(mid: str):
            if mid in visited:
                return
            visited.add(mid)
            
            module = self.modules.get(mid)
            if not module:
                return
            
            for dep in module.get('dependencies', []):
                _resolve(dep)
                if dep not in dependencies:
                    dependencies.append(dep)
            
            if mid != module_id and mid not in dependencies:
                dependencies.append(mid)
        
        _resolve(module_id)
        return dependencies


if __name__ == "__main__":
    # Тестовий запуск
    registry = PluginRegistry()
    print("🔍 Loading modules...")
    modules = registry.load_modules()
    print(f"\n📦 Loaded {len(modules)} modules:")
    for mod_id in modules:
        print(f"  • {mod_id}")
