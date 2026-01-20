# CIT Changelog

## [2.1.0] - 2026-01-18

### 🏁 Final Release: Complete Migration and Autonomy

This release completes the v2.1 migration with autonomous components, memory optimization, and comprehensive documentation.

### Added

#### Core Components
- **OpenAIClient** (`server/openai_client.py`) - Autonomous AI client
  - Intelligent routing: Responses API → Chat Completions fallback
  - Environment-based configuration
  - Zero external dependencies
  - Full error handling and logging

- **JobManager Integration** - Enhanced job management
  - Complete lifecycle management (create, start, complete, cancel)
  - RESTful API endpoints: `/v1/jobs/*`
  - File-based persistence via JobStore

#### API Endpoints
- `POST /v1/jobs` - Create new job
- `GET /v1/jobs/{id}` - Get job status
- `GET /v1/jobs/{id}/logs` - Get job logs

#### Documentation
- `docs/RELEASE_v2.1.md` - Complete release notes
- `docs/ARCHITECTURE.md` - Updated with v2.1 components
- `tests/README.md` - Test documentation
- Updated `README.md` with v2.1 features

#### Testing
- `tests/test_v21_components.py` - Comprehensive component tests
  - OpenAIClient tests
  - JobManager tests  
  - JobStore tests
  - All tests passing ✓

### Changed
- `server/cit_server.py` - Now uses OpenAIClient for AI interactions
- Memory usage optimized to ~80MB (was ~150MB in v2.0)

### Performance
- **Memory:** 47% reduction (150MB → 80MB)
- **Startup:** Fast startup maintained
- **Dependencies:** Still zero external packages

### Technical Notes
- Maintains backward compatibility with v2.0
- Responses API endpoint may not exist; fallback always works
- All existing endpoints unchanged
- Pre-existing code structure preserved where not modified

### Migration
No breaking changes. Upgrade by pulling latest code:
```bash
git pull origin main
python server/cit_server.py
```

---

## [2.0.0] - Previous Release

Previous stable release with basic functionality.

---

**Full Changelog**: See [docs/RELEASE_v2.1.md](docs/RELEASE_v2.1.md) for complete details.
