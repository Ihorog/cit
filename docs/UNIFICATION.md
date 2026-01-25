# 🧬 CIT Unification Architecture

## Overview

This document describes the unified modular architecture that consolidates 5 repositories (`cit`, `ciwiki`, `cimeika-unified`, `media`, `cit_versel`) into a single digital organism following the **111 density principle**:

- **1 Core** → `core/engine.py`
- **1 Registry** → `registry/modules.json`
- **1 Entry Point** → `python core/engine.py`

## Architecture

### Directory Structure

```
cit/
├── core/                          # Core engine
│   ├── engine.py                  # Modular runtime with CLI
│   ├── plugin_loader.py           # Dynamic module registration
│   └── manifest.schema.json       # JSON Schema for validation
├── modules/                       # All modules as plugins
│   ├── wiki/
│   │   └── manifest.yaml
│   ├── unified/
│   │   └── manifest.yaml
│   ├── media/
│   │   └── manifest.yaml
│   └── vercel/
│       └── manifest.yaml
├── scripts/
│   └── unify.py                   # Migration script
├── registry/
│   └── modules.json               # Module dependency graph
└── cimeika_matrix.yaml            # Centralized configuration
```

### Module Manifest Format

Each module has a `manifest.yaml` file that declares its properties:

```yaml
id: module-name
type: documentation|platform|assets|deployment
source: Ihorog/repo-name
mount: /path
entry: main.py                     # Optional entry point
frontend: frontend/                # Optional frontend directory
dependencies:                      # Optional dependencies
  - other-module
static: true                       # Optional static assets flag
serverless: true                   # Optional serverless flag
description: "Human-readable description"
```

### Registry Format

The `registry/modules.json` maintains the module graph:

```json
{
  "version": "1.0.0",
  "core": "Ihorog/cit",
  "modules": [
    {
      "id": "module-name",
      "status": "active|static|cloud",
      "requires": ["dependency-1", "dependency-2"]
    }
  ]
}
```

## CLI Commands

### Build

Validates all modules and prepares the system:

```bash
python core/engine.py build
```

This command:
1. Runs the migration script (`scripts/unify.py`)
2. Loads all module manifests
3. Validates manifests against JSON Schema
4. Resolves and validates dependencies

### Run

Starts the HTTP server with all modules loaded:

```bash
python core/engine.py run
```

### Module

Runs a specific module independently:

```bash
python core/engine.py module <module-id>
```

### Status

Shows system status and loaded modules:

```bash
python core/engine.py status
```

## Module Types

### Documentation (ciwiki)
- **Type**: `documentation`
- **Mount**: `/docs`
- **Purpose**: Central documentation and ecosystem rules
- **Entry**: `mkdocs.yml`

### Platform (cimeika-unified)
- **Type**: `platform`
- **Mount**: `/api`
- **Purpose**: Unified platform with 7 modules (Ci, Kazkar, Podija, Nastrij, Malya, Gallery, Calendar)
- **Entry**: `backend/main.py`
- **Dependencies**: `media`

### Assets (media)
- **Type**: `assets`
- **Mount**: `/public/media`
- **Purpose**: Media resources (icons, images, visual memory)
- **Static**: `true`

### Deployment (vercel)
- **Type**: `deployment`
- **Mount**: N/A (extends core)
- **Purpose**: Cloud configuration for Vercel deployment
- **Serverless**: `true`

## Dependency Graph

```
cimeika-unified
    └── media

ciwiki
    (no dependencies)

media
    (no dependencies)

vercel
    (no dependencies, extends core)
```

## Migration Process

The `scripts/unify.py` script handles repository integration:

1. **Copy files** from external repositories to `modules/` with deduplication
2. **Exclude** unnecessary files (`.git`, `node_modules`, `venv`, etc.)
3. **Register** modules in `registry/modules.json`
4. **Validate** all manifests against JSON Schema

### Running Migration

```bash
python scripts/unify.py
```

**Note**: External repositories must be cloned in parent directory:
```
parent/
├── cit/              # This repository
├── ciwiki/           # Clone of Ihorog/ciwiki
├── cimeika-unified/  # Clone of Ihorog/cimeika-unified
├── media/            # Clone of Ihorog/media
└── cit_versel/       # Clone of Ihorog/cit_versel
```

## Configuration

### Environment Variables

The engine reads configuration from environment variables:

- `OPENAI_API_KEY` — OpenAI API key (required)
- `OPENAI_MODEL` — Model to use (default: `gpt-4o-mini`)
- `HOST` — Server host (default: `0.0.0.0`)
- `PORT` — Server port (default: `8790`)

### Matrix Configuration

The `cimeika_matrix.yaml` defines:
- **States**: System states (fatigue, strength, search, etc.)
- **Intents**: Action intents (understand, fix, create, etc.)
- **Modules**: Module-specific configuration with priorities

## CI/CD Integration

The `.github/workflows/cit-unified.yml` workflow:

1. Validates all module manifests
2. Loads modules using `PluginRegistry`
3. Runs build command
4. Executes tests

## Plugin System

### PluginRegistry

The `PluginRegistry` class manages module lifecycle:

- **Load modules** from registry
- **Validate manifests** against JSON Schema
- **Register new modules** dynamically
- **Resolve dependencies** into execution graph

### Example Usage

```python
from core.plugin_loader import PluginRegistry

registry = PluginRegistry()
modules = registry.load_modules()

# Get module info
module = registry.get_module('ciwiki')

# Resolve dependencies
deps = registry.resolve_dependencies('cimeika-unified')
```

## Design Principles

### 1. Single Responsibility
Each module has a clear, single purpose defined by its `type`.

### 2. Declarative Configuration
Modules declare their requirements, dependencies, and capabilities in manifests.

### 3. Dependency Resolution
The registry automatically resolves and validates dependency graphs.

### 4. Validation First
All manifests must pass JSON Schema validation before loading.

### 5. Minimal Core
The core engine is lightweight and delegates functionality to modules.

## Future Extensions

### Adding New Modules

1. Create module directory in `modules/<module-id>/`
2. Add `manifest.yaml` with module definition
3. Register module in `registry/modules.json`
4. Run `python core/engine.py build` to validate

### Custom Module Types

Add new types to `core/manifest.schema.json`:

```json
{
  "type": {
    "enum": ["documentation", "platform", "assets", "deployment", "custom-type"]
  }
}
```

## References

- [CIT README](../README.md) — Technical implementation details
- [Legend Ci](../LEGEND_CI.md) — Conceptual framework
- [ciwiki](https://github.com/Ihorog/ciwiki) — Ecosystem documentation
