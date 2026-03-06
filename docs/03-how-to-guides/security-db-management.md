# Managing Offline Security Databases
**Target**: Air-Gapped / Sovereign Deployments
**Tools**: `scripts/db_manager.py`

## 📡 Why Local Databases?
To maintain absolute sovereignty and support air-gapped environments, Xoe-NovAi does not query external vulnerability APIs during the build process. Instead, we maintain local clones of the **Grype** and **Trivy** vulnerability databases.

## 📁 Storage Location
By default, the databases are stored in:
`~/.xnai/security-db/`

This location is separate from the project directory to ensure that databases are not accidentally committed to version control and can be shared across multiple project instances.

## 🚀 Operations

### 1. Initialize / Update Databases
Run this when you have internet access to fetch the latest CVE definitions:
```bash
make update-security-db
```
This command:
1.  Cleans the local cache.
2.  Invokes Grype and Trivy with `--download-db-only`.
3.  Verifies the integrity of the downloaded files.

### 2. Verify Database Health
Check the age and integrity of your local data:
```bash
make verify-security-db
```
If the database is older than 7 days, the PR Auditor will issue a warning.

### 3. Air-Gapped Migration
To move the security databases to a fully air-gapped machine:
1.  On a connected machine: `make update-security-db`.
2.  Compress the directory: `tar -czf security-db.tar.gz ~/.xnai/security-db`.
3.  On the air-gapped machine: `tar -xzf security-db.tar.gz -C ~/.xnai/`.

## ⚙️ Configuration
The DB Manager is controlled via environment variables (usually set in `Makefile`):
- `XNAI_DB_CACHE_DIR`: Override the default storage path.
- `GRYPE_DB_UPDATE_URL`: Override the update source for enterprise mirrors.

## 🛡️ Best Practices
- **Weekly Updates**: We recommend running `make update-security-db` at least once a week.
- **Rootless Persistence**: The `db_manager.py` script automatically handles directory permissions for rootless Podman execution.
