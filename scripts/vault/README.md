# Vault Scripts

This directory contains scripts for syncing and managing the CIT vault (data backup/sync).

## Scripts

- **`cit_vault_ls.sh`** - List contents of the CIT vault
- **`cit_vault_pull.sh`** - Pull/sync data from the vault to local
- **`cit_vault_push.sh`** - Push/sync local data to the vault
- **`ci_sync.sh`** - Sync CI-related data

## Usage

These scripts are used to synchronize data between local CIT installation and a backup/vault location.

Example:
```bash
# List vault contents
./scripts/vault/cit_vault_ls.sh

# Pull from vault
./scripts/vault/cit_vault_pull.sh

# Push to vault
./scripts/vault/cit_vault_push.sh
```
