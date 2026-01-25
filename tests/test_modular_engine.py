#!/usr/bin/env python3
"""
Tests for CIT modular engine components
"""
import sys
import json
import yaml
from pathlib import Path

# Add project root to path only if module not importable
try:
    from core.plugin_loader import PluginRegistry
except ImportError:
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from core.plugin_loader import PluginRegistry


def test_plugin_registry():
    """Test PluginRegistry initialization and basic functionality"""
    print("Testing PluginRegistry...")
    
    registry = PluginRegistry()
    assert registry is not None, "Registry should initialize"
    
    # Test schema loading
    schema = registry.load_schema()
    assert schema is not None, "Schema should load"
    assert "$schema" in schema, "Schema should have $schema field"
    
    print("✓ PluginRegistry initializes correctly")


def test_module_loading():
    """Test loading modules from registry"""
    print("Testing module loading...")
    
    registry = PluginRegistry()
    modules = registry.load_modules()
    
    assert len(modules) > 0, "Should load at least one module"
    assert "media" in modules, "Should load media module"
    
    print(f"✓ Loaded {len(modules)} modules")


def test_manifest_validation():
    """Test manifest validation against schema"""
    print("Testing manifest validation...")
    
    registry = PluginRegistry()
    
    # Valid manifest
    valid_manifest = {
        "id": "test-module",
        "type": "documentation",
        "source": "test/repo",
        "mount": "/test"
    }
    
    assert registry.validate_manifest(valid_manifest), "Valid manifest should pass"
    
    # Invalid manifest (missing required field)
    invalid_manifest = {
        "id": "test-module",
        "type": "documentation"
        # Missing 'source' and 'mount'
    }
    
    assert not registry.validate_manifest(invalid_manifest), "Invalid manifest should fail"
    
    print("✓ Manifest validation works correctly")


def test_dependency_resolution():
    """Test dependency resolution"""
    print("Testing dependency resolution...")
    
    registry = PluginRegistry()
    modules = registry.load_modules()
    
    if "cimeika-unified" in modules:
        deps = registry.resolve_dependencies("cimeika-unified")
        assert "media" in deps, "Should resolve media dependency"
        print(f"✓ Dependencies resolved: {deps}")
    else:
        print("⚠️  cimeika-unified module not loaded, skipping dependency test")


def test_module_manifests():
    """Test that all module manifests are valid"""
    print("Testing all module manifests...")
    
    registry = PluginRegistry()
    modules_dir = Path("modules")
    
    if not modules_dir.exists():
        print("⚠️  Modules directory not found, skipping test")
        return
    
    valid_count = 0
    invalid_count = 0
    
    for manifest_file in modules_dir.rglob("manifest.yaml"):
        try:
            manifest = yaml.safe_load(manifest_file.read_text())
            if registry.validate_manifest(manifest):
                valid_count += 1
            else:
                invalid_count += 1
                print(f"  ✗ Invalid: {manifest_file}")
        except Exception as e:
            invalid_count += 1
            print(f"  ✗ Error in {manifest_file}: {e}")
    
    assert invalid_count == 0, f"All manifests should be valid, but {invalid_count} failed"
    print(f"✓ All {valid_count} manifests are valid")


def test_registry_json():
    """Test registry.json structure"""
    print("Testing registry.json...")
    
    registry_path = Path("registry/modules.json")
    
    if not registry_path.exists():
        print("⚠️  Registry not found, skipping test")
        return
    
    registry = json.loads(registry_path.read_text())
    
    assert "version" in registry, "Registry should have version"
    assert "core" in registry, "Registry should have core"
    assert "modules" in registry, "Registry should have modules list"
    
    # Check module structure
    for module in registry["modules"]:
        assert "id" in module, "Module should have id"
        assert "status" in module, "Module should have status"
        assert "requires" in module, "Module should have requires"
    
    print(f"✓ Registry is valid with {len(registry['modules'])} modules")


def main():
    """Run all tests"""
    print("=" * 60)
    print("CIT Modular Engine Tests")
    print("=" * 60)
    
    tests = [
        test_plugin_registry,
        test_module_loading,
        test_manifest_validation,
        test_dependency_resolution,
        test_module_manifests,
        test_registry_json,
    ]
    
    failed = []
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed.append(test.__name__)
    
    print("\n" + "=" * 60)
    
    if failed:
        print(f"✗ {len(failed)} test(s) failed:")
        for name in failed:
            print(f"  - {name}")
        sys.exit(1)
    else:
        print("✓ All tests passed!")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
