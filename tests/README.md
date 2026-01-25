# CIT Tests

This directory contains tests for CIT components.

## Running Tests

### All Tests
```bash
python3 tests/test_v21_components.py
python3 tests/test_modular_engine.py
```

## Test Coverage

### v2.1 Components
- `test_v21_components.py` - Tests for OpenAIClient, JobManager, and JobStore
  - OpenAIClient initialization and configuration
  - Job creation, lifecycle management
  - Job persistence and logging

### Modular Engine (Unified Architecture)
- `test_modular_engine.py` - Tests for modular engine and plugin system
  - PluginRegistry initialization and module loading
  - Manifest validation against JSON Schema
  - Dependency resolution
  - Registry structure validation

## Test Requirements

Tests use only Python standard library modules plus:
- `unittest` or simple assertions
- `tempfile` for temporary storage
- `pyyaml` for YAML parsing
- `jsonschema` for manifest validation

## Adding New Tests

When adding new features, create corresponding test files:
1. Name test files `test_*.py`
2. Use descriptive function names starting with `test_`
3. Include docstrings explaining what is being tested
4. Use temporary directories for file-based tests
5. Clean up resources after tests complete

## CI/CD Integration

Tests can be integrated into GitHub Actions workflows:
```yaml
- name: Run tests
  run: |
    python3 tests/test_v21_components.py
    python3 tests/test_modular_engine.py
```
