# Unified CIT API Specification

## Overview

This document defines a unified, coherent API for CIT (Ci Interface Terminal) that consolidates functionality from both the local `cit_server.py` and the Hugging Face Space deployment (`cimeika-api`). The goal is to create a single, consistent API surface that works across all deployment environments.

## Design Principles

1. **Minimal and Stable** - Keep the core API small and backward-compatible
2. **Stdlib-first** - Implementation should use Python standard library where possible
3. **Environment-agnostic** - Works on Termux (Android), Docker, Hugging Face Spaces
4. **Secure by default** - No secrets in code, proper error handling
5. **Progressive enhancement** - Optional features don't break core functionality

## API Version: v1

All versioned endpoints use the `/v1/` prefix to enable future evolution.

---

## Core Endpoints

### 1. Health Check

**Endpoint:** `GET /health` or `GET /v1/health`

**Description:** Returns service status, available features, and configuration info.

**Response:**
```json
{
  "ok": true,
  "service": "cit",
  "version": "1.0.0",
  "time": "2026-01-14T16:20:19.340Z",
  "port": 8790,
  "model": "gpt-4o-mini",
  "features": {
    "openai": true,
    "huggingface": false,
    "storage": "local",
    "webdav": false
  },
  "environment": "termux"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 2. Chat Completion

**Endpoint:** `POST /chat` or `POST /v1/chat`

**Description:** Send a message to the AI assistant. Intelligently routes to OpenAI Responses API with fallback to Chat Completions API.

**Request:**
```json
{
  "message": "Hello, how are you?",
  "system": "You are a helpful assistant.",
  "model": "gpt-4o-mini",
  "max_tokens": 4096,
  "temperature": 0.7
}
```

**Required fields:**
- `message` (string) - User's message

**Optional fields:**
- `system` (string) - System prompt
- `model` (string) - Override default model
- `max_tokens` (integer) - Maximum response tokens
- `temperature` (float) - Sampling temperature (0.0-2.0)

**Response (Success):**
```json
{
  "ok": true,
  "cit": "v1",
  "time": "2026-01-14T16:20:19.340Z",
  "model": "gpt-4o-mini",
  "reply": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "api": "responses",
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 18,
    "total_tokens": 30
  }
}
```

**Response (Error):**
```json
{
  "ok": false,
  "error": "billing_not_active",
  "message": "OpenAI API billing не активний для цього акаунта.",
  "time": "2026-01-14T16:20:19.340Z"
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid request format
- `401 Unauthorized` - API key not configured
- `429 Too Many Requests` - Rate limit exceeded
- `502 Bad Gateway` - Upstream API error

---

## Configuration Endpoints

### 3. Get Configuration

**Endpoint:** `GET /config` or `GET /v1/config`

**Description:** Retrieve current configuration (secrets are masked).

**Response:**
```json
{
  "model": "gpt-4o-mini",
  "storage_mode": "local",
  "vault_dir": "/storage/emulated/0/CimeikaVault",
  "webdav_url": "https://example.com/webdav",
  "webdav_user": "user",
  "openai_api_key_masked": "sk-***abc1234",
  "features": {
    "file_upload": true,
    "webdav": true,
    "exec": false
  }
}
```

**Status Codes:**
- `200 OK` - Success

---

### 4. Update Configuration

**Endpoint:** `POST /config` or `POST /v1/config`

**Description:** Update configuration settings.

**Request:**
```json
{
  "model": "gpt-4o-mini",
  "openai_api_key": "your-api-key-here",
  "storage_mode": "webdav",
  "webdav_url": "https://example.com/webdav",
  "webdav_user": "user",
  "webdav_pass": "password"
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Configuration updated successfully"
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid configuration

---

## File Management Endpoints

### 5. List Files

**Endpoint:** `GET /files` or `GET /v1/files`

**Description:** List files in the vault storage.

**Query Parameters:**
- `limit` (integer, default: 100) - Maximum number of files to return
- `offset` (integer, default: 0) - Pagination offset

**Response:**
```json
{
  "ok": true,
  "mode": "local",
  "vault": "/storage/emulated/0/CimeikaVault",
  "items": [
    {
      "name": "document.txt",
      "size": 1024,
      "mtime": "2026-01-14T16:20:19"
    },
    {
      "name": "image.png",
      "size": 51200,
      "mtime": "2026-01-13T10:15:00"
    }
  ],
  "total": 2
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Vault directory not found

---

### 6. Get File

**Endpoint:** `GET /file` or `GET /v1/file`

**Description:** Download a specific file from vault.

**Query Parameters:**
- `name` (string, required) - File name

**Response:**
- Binary file content with appropriate Content-Type header

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - File not found
- `502 Bad Gateway` - WebDAV error (if using remote storage)

---

### 7. Upload File

**Endpoint:** `POST /file` or `POST /v1/file` or `POST /upload`

**Description:** Upload a file to vault.

**Request:**
- Content-Type: `multipart/form-data`
- Form field: `file` (binary file data)

**Response:**
```json
{
  "ok": true,
  "name": "uploaded_file.txt",
  "size": 1024,
  "url": "/file?name=uploaded_file.txt"
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - No file provided
- `413 Payload Too Large` - File too large
- `502 Bad Gateway` - WebDAV error (if using remote storage)

---

### 8. Delete File

**Endpoint:** `DELETE /file` or `DELETE /v1/file`

**Description:** Delete a file from vault.

**Query Parameters:**
- `name` (string, required) - File name

**Response:**
```json
{
  "ok": true,
  "message": "File deleted successfully"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - File not found
- `502 Bad Gateway` - WebDAV error (if using remote storage)

---

## Registry Endpoints

### 9. Get Registry

**Endpoint:** `GET /registry` or `GET /v1/registry`

**Description:** Get CI registry data (components, plugins, modules).

**Response:**
```json
{
  "version": "1.0",
  "components": [
    {
      "id": "ci_home_chat",
      "name": "Home Chat",
      "status": "active",
      "version": "1.0.0"
    }
  ],
  "updated": "2026-01-14T16:20:19.340Z"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Registry file not found

---

### 10. Get Node Packages

**Endpoint:** `GET /node-packages` or `GET /v1/node-packages`

**Description:** Get list of available node packages.

**Response:**
```json
{
  "packages": [
    {
      "name": "express",
      "version": "4.18.2",
      "description": "Fast, unopinionated, minimalist web framework"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Packages file not found

---

## UI Endpoints

### 11. Web UI

**Endpoint:** `GET /` or `GET /ui`

**Description:** Serve the web-based chat interface with PWA support.

**Response:**
- HTML page with embedded chat UI, STT/TTS support

**Status Codes:**
- `200 OK` - Success

---

### 12. PWA Manifest

**Endpoint:** `GET /manifest.webmanifest` or `GET /manifest.json`

**Description:** PWA manifest for installable web app.

**Response:**
```json
{
  "name": "Cimeika",
  "short_name": "Ci",
  "description": "Домашній AI асистент",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0b0b0b",
  "theme_color": "#0b0b0b",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success

---

### 13. UI API - Vault List

**Endpoint:** `GET /ui/api/vault`

**Description:** Get vault file list formatted for UI display.

**Response:**
```json
{
  "files": "document.txt  (1024 bytes)\nimage.png  (51200 bytes)"
}
```

**Status Codes:**
- `200 OK` - Success

---

### 14. UI API - Logs

**Endpoint:** `GET /ui/api/logs`

**Description:** Get recent log entries.

**Query Parameters:**
- `lines` (integer, default: 120) - Number of lines to return

**Response:**
```json
{
  "logs": "[2026-01-14 16:20:19] Server started\n[2026-01-14 16:21:00] Request: POST /chat"
}
```

**Status Codes:**
- `200 OK` - Success

---

## Migration Strategy

### Phase 1: Standardize Existing Endpoints (Current)
1. Ensure both `cit_server.py` and Hugging Face deployment use consistent response formats
2. Add `/v1/` prefix support while maintaining backward compatibility
3. Standardize error response format across all endpoints

### Phase 2: Consolidate Features
1. Merge settings endpoint from `ci.py` into main config API
2. Add missing endpoints (DELETE /file)
3. Implement consistent authentication/authorization layer

### Phase 3: Documentation & Testing
1. Generate OpenAPI/Swagger documentation
2. Add API integration tests
3. Create client libraries/SDKs

### Phase 4: Enhanced Features
1. Add versioning support (v2 endpoints)
2. Implement rate limiting
3. Add webhook/event streaming support
4. Multi-user and session management

---

## Security Considerations

1. **API Keys**: Never expose in responses, always mask
2. **File Access**: Validate and sanitize all file paths
3. **Rate Limiting**: Implement rate limits for expensive operations
4. **CORS**: Configure appropriately for cross-origin requests
5. **Input Validation**: Validate all user inputs
6. **Error Messages**: Don't leak sensitive information in errors

---

## Environment Variables

Required:
- `OPENAI_API_KEY` or `CIT_OPENAI_API_KEY` - OpenAI API key

Optional:
- `CIT_PORT` (default: 8790) - Server port
- `CIT_BIND` (default: 127.0.0.1) - Bind address
- `CIT_MODEL` or `CIT_OPENAI_MODEL` (default: gpt-4o-mini) - Default AI model
- `HUGGINGFACE_API_TOKEN` or `HF_TOKEN` - HuggingFace token
- `CIT_STORAGE_MODE` (default: local) - Storage mode (local/webdav)
- `CIT_VAULT_DIR` - Vault directory path
- `CIT_WEBDAV_URL` - WebDAV server URL
- `CIT_WEBDAV_USER` - WebDAV username
- `CIT_WEBDAV_PASS` - WebDAV password

---

## Backward Compatibility

All existing endpoints without `/v1/` prefix remain functional:
- `/health` → works alongside `/v1/health`
- `/chat` → works alongside `/v1/chat`
- `/config` → works alongside `/v1/config`

This ensures existing integrations continue to work while new integrations can use versioned endpoints.
