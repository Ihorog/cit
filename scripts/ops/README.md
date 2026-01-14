# Operational Scripts

This directory contains operational scripts for managing CIT services.

## Scripts

### Service Management
- **`CIT_BOOT_USE_CITCTL.sh`** - Configure CIT to auto-start on Termux boot using citctl
- **`CIT_KILL_ALL_CIT.sh`** - Stop all running CIT server processes
- **`START_ALL.sh`** - Start both API and UI services (Termux-specific paths)

### Utilities
- **`logs.sh`** - View and tail CIT server logs
- **`verify-build.sh`** - Verify build success and readiness for deployment

## Usage

Most of these scripts are designed for Termux on Android. For regular usage, prefer using `citctl.sh` from the repository root.

Example:
```bash
# Start CIT service
cd /path/to/cit
./citctl.sh start

# View logs
./scripts/ops/logs.sh

# Stop all CIT processes
./scripts/ops/CIT_KILL_ALL_CIT.sh
```
